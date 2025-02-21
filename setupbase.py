# -*- coding: utf-8 -*-
import os
import re
import io
import sys
import json
import hashlib
import zipfile

try:
    from fontTools import ttLib
except ImportError:
    ttLib = None

from urllib.request import urlopen

import setuptools

LOG_INFO = 20

HERE = os.path.abspath(os.path.dirname(__file__))
INIT_PY_PATH = os.path.join(HERE, "qtawesome", "__init__.py")


def rename_font(font_path, font_name):
    """
    Font renaming code originally from:
    https://github.com/chrissimpkins/fontname.py/blob/master/fontname.py
    """
    tt = ttLib.TTFont(font_path, recalcBBoxes=False, recalcTimestamp=False)
    namerecord_list = tt["name"].names
    variant = ""

    # determine font variant for this file path from name record nameID 2
    for record in namerecord_list:
        if record.nameID == 2:
            variant = str(record)
            break

    # test that a variant name was found in the OpenType tables of the font
    if len(variant) == 0:
        raise ValueError(
            "Unable to detect the font variant from the OpenType name table in: %s"
            % font_path
        )

    # Here are some sample name records to give you an idea of the name tables:
    # ID 0: 'Copyright (c) Font Awesome'
    # ID 1: 'Font Awesome 5 Free Regular'
    # ID 2: 'Regular'
    # ID 3: 'Font Awesome 5 Free Regular-5.14.0'
    # ID 4: 'Font Awesome 5 Free Regular'
    # ID 5: '331.264 (Font Awesome version: 5.14.0)'
    # ID 6: 'FontAwesome5Free-Regular'
    # ID 10: "The web's most popular icon set and toolkit."
    # ID 11: 'https://fontawesome.com'
    # ID 16: 'Font Awesome 5 Free'
    # ID 17: 'Regular'
    # ID 18: 'Font Awesome 5 Free Regular'
    # ID 21: 'Font Awesome 5 Free'
    # ID 22: 'Regular'

    # modify the opentype table data in memory with updated values
    for record in namerecord_list:
        if record.nameID in (1, 4, 16, 21):
            print(
                f"Renaming font name record at ID {record.nameID}: {record.string} --> {font_name}"
            )
            record.string = font_name

    # write changes to the font file
    try:
        tt.save(font_path, reorderTables=False)
    except Exception:
        raise RuntimeError(
            f"ERROR: unable to write new name to OpenType tables for: {font_path}"
        )


class UpdateFA6Command(setuptools.Command):
    """A custom command to make updating FontAwesome 6.x easy!"""

    description = "Try to update the FontAwesome 6.x data in the project."
    user_options = [
        ("fa-version=", None, "FA version."),
        ("zip-path=", None, "Read from local zip file path."),
    ]

    # Update these below if the FontAwesome changes their structure:
    FA_STYLES = ("regular", "solid", "brands")
    CHARMAP_PATH_TEMPLATE = os.path.join(
        HERE,
        "qtawesome",
        "fonts",
        "fontawesome6-{style}-webfont-charmap-{version}.json",
    )
    TTF_PATH_TEMPLATE = os.path.join(
        HERE, "qtawesome", "fonts", "fontawesome6-{style}-webfont-{version}.ttf"
    )
    URL_TEMPLATE = (
        "https://github.com/FortAwesome/Font-Awesome/"
        "releases/download/{version}/fontawesome-free-{version}-web.zip"
    )

    def initialize_options(self):
        """Set default values for the command options."""
        self.fa_version = ""
        self.zip_path = ""

    def finalize_options(self):
        """Validate the command options."""
        assert bool(self.fa_version), "FA version is mandatory for this command."
        if self.zip_path:
            assert os.path.exists(self.zip_path), (
                "Local zipfile does not exist: %s" % self.zip_path
            )

    def __print(self, msg):
        """Shortcut for printing with the setuptools logger."""
        self.announce(msg, level=LOG_INFO)

    def __get_charmap_path(self, style):
        """Get the project FA charmap path for a given style."""
        return self.CHARMAP_PATH_TEMPLATE.format(style=style, version=self.fa_version)

    def __get_ttf_path(self, style):
        """Get the project FA font path for a given style."""
        return self.TTF_PATH_TEMPLATE.format(style=style, version=self.fa_version)

    @property
    def __release_url(self):
        """Get the release URL."""
        return self.URL_TEMPLATE.format(version=self.fa_version)

    @property
    def __zip_file(self):
        """Get a file object of the FA zip file."""
        if self.zip_path:
            # If using a local file, just open it:
            self.__print("Opening local zipfile: %s" % self.zip_path)
            return open(self.zip_path, "rb")

        # Otherwise, download it and make a file object in-memory:
        url = self.__release_url
        self.__print("Downloading from URL: %s" % url)
        response = urlopen(url)
        return io.BytesIO(response.read())

    @property
    def __zipped_files_data(self):
        """Get a dict of all files of interest from the FA release zipfile."""
        files = {}
        with zipfile.ZipFile(self.__zip_file) as thezip:
            for zipinfo in thezip.infolist():
                if zipinfo.filename.endswith("metadata/icons.json"):
                    with thezip.open(zipinfo) as compressed_file:
                        files["icons.json"] = compressed_file.read()
                elif zipinfo.filename.endswith(".ttf"):
                    # For the record, the paths usually look like this:
                    # webfonts/fa-brands-400.ttf
                    # webfonts/fa-regular-400.ttf
                    # webfonts/fa-solid-900.ttf
                    name = os.path.basename(zipinfo.filename)
                    tokens = name.split("-")
                    style = tokens[1]
                    if style in self.FA_STYLES:
                        with thezip.open(zipinfo) as compressed_file:
                            files[style] = compressed_file.read()

        # Safety checks:
        assert all(style in files for style in self.FA_STYLES), (
            "Not all FA styles found! Update code is broken."
        )
        assert "icons.json" in files, "icons.json not found! Update code is broken."

        return files

    def run(self):
        """Run command."""
        files = self.__zipped_files_data
        hashes = {}
        icons = {}

        # Read icons.json (from the webfont zip download)
        data = json.loads(files["icons.json"])

        # Group icons by style, since not all icons exist for all styles:
        for icon, info in data.items():
            for style in info["styles"]:
                icons.setdefault(str(style), {})
                icons[str(style)][icon] = str(info["unicode"])

        # For every FA "style":
        for style, details in icons.items():
            # Dump a .json charmap file:
            charmapPath = self.__get_charmap_path(style)
            self.__print('Dumping updated "%s" charmap: %s' % (style, charmapPath))
            with open(charmapPath, "w+") as f:
                json.dump(details, f, indent=4, sort_keys=True)

            # Dump a .ttf font file:
            font_path = self.__get_ttf_path(style)
            data = files[style]
            self.__print('Dumping updated "%s" font: %s' % (style, font_path))
            with open(font_path, "wb+") as f:
                f.write(data)

            # Fix to prevent repeated font names:
            if style in ("regular", "solid"):
                new_name = str("Font Awesome 6 Free %s") % style.title()
                self.__print('Renaming font to "%s" in: %s' % (new_name, font_path))
                if ttLib is not None:
                    rename_font(font_path, new_name)
                else:
                    sys.exit(
                        "This special command requires the module 'fonttools': "
                        "https://github.com/fonttools/fonttools/"
                    )

                # Reread the data since we just edited the font file:
                with open(font_path, "rb") as f:
                    data = f.read()
                    files[style] = data
            # Store hashes for later:
            hashes[style] = hashlib.md5(data).hexdigest()

        # Now it's time to patch "__init__.py":
        init_path = INIT_PY_PATH
        self.__print("Patching new MD5 hashes in: %s" % init_path)
        with open(init_path, "r") as init_file:
            contents = init_file.read()
        # We read it in full, then use regex substitution:
        for style, md5 in hashes.items():
            self.__print('New "%s" hash is: %s' % (style, md5))
            regex = r'("fontawesome6-%s-webfont-%s.ttf":\s+)"(\w+)"' % (
                style,
                self.fa_version,
            )
            subst = r'\g<1>"' + md5 + '"'
            contents = re.sub(regex, subst, contents, 1)
        # and finally overwrite with the modified file:
        self.__print("Dumping updated file: %s" % init_path)
        with open(init_path, "w") as init_file:
            init_file.write(contents)

        self.__print(
            "\nFinished!\n"
            "Please check the git diff to make sure everything went okay.\n"
            "You should also edit README.md and "
            "qtawesome/docs/source/usage.rst to reflect the changes."
        )


class UpdateCodiconCommand(setuptools.Command):
    """A custom command to make updating Microsoft's Codicons easy!"""

    description = "Try to update the Codicon font data in the project."
    user_options = [("msc-version=", None, "Codicon version.")]

    CHARMAP_PATH = os.path.join(
        HERE, "qtawesome", "fonts", "codicon-charmap-{version}.json"
    )
    TTF_PATH = os.path.join(HERE, "qtawesome", "fonts", "codicon-{version}.ttf")
    DOWNLOAD_URL_TTF = "https://github.com/microsoft/vscode-codicons/releases/download/{version}/codicon.ttf"
    DOWNLOAD_URL_MAPPING = "https://raw.githubusercontent.com/microsoft/vscode-codicons/refs/tags/{version}/src/template/mapping.json"
    DOWNLOAD_URL_JSON = "https://raw.githubusercontent.com/microsoft/vscode-codicons/{version}/package.json"

    def initialize_options(self):
        """Set default values for the command options."""
        self.msc_version = ""

    def finalize_options(self):
        """Validate the command options."""
        assert bool(self.msc_version), "Codicons version is mandatory for this command."

    def __print(self, msg):
        """Shortcut for printing with the setuptools logger."""
        self.announce(msg, level=LOG_INFO)

    def run(self):
        """Run command."""

        # Download .json to a temporary path:
        download_url_json = self.DOWNLOAD_URL_JSON.format(version=self.msc_version)
        package_json = urlopen(download_url_json)
        package_info = json.load(package_json)
        package_version = package_info["version"]
        assert self.msc_version == package_version, (
            "Codicons version does not match with `package.json` info. %s and %s"
            % (
                self.msc_version,
                package_version,
            )
        )
        self.__print("Will download codicons version: %s" % package_version)

        # Download mapping.json:
        donwload_url_mapping = self.DOWNLOAD_URL_MAPPING.format(
            version=self.msc_version
        )
        req = urlopen(donwload_url_mapping)
        if req.status != 200:
            raise Exception("Failed to download JSON mapping")

        data = json.loads(req.read().decode())
        req.close()

        # Interpret the mapping.json file:
        charmap = {}
        for name, key in data.items():
            key = hex(key)
            name = name.lower()
            charmap[name] = key
        self.__print("Identified %s icons in the JSON." % len(charmap))

        # Dump a .json charmap file the way we like it:
        charmap_path = self.CHARMAP_PATH.format(version=package_version)
        self.__print("Dumping updated charmap: %s" % charmap_path)
        with open(charmap_path, "w+") as f:
            json.dump(charmap, f, indent=4, sort_keys=True)

        # Dump a .ttf font file:
        download_url_ttf = self.DOWNLOAD_URL_TTF.format(version=self.msc_version)
        ttf_path = self.TTF_PATH.format(version=package_version)
        with open(ttf_path, "wb+") as ttfFile:
            self.__print("Downloading %s --> %s" % (download_url_ttf, ttf_path))
            response = urlopen(download_url_ttf)
            data = response.read()
            ttfFile.write(data)
            md5 = hashlib.md5(data).hexdigest()
            self.__print("New hash is: %s" % md5)

        # Now it's time to patch "__init__.py":
        self.__print("Patching new MD5 hashes in: %s" % INIT_PY_PATH)
        with open(INIT_PY_PATH, "r") as init_file:
            contents = init_file.read()
        regex = r'("codicon-%s.ttf":\s+)"(\w+)"' % self.msc_version
        subst = r'\g<1>"' + md5 + '"'
        contents = re.sub(regex, subst, contents, 1)
        self.__print("Dumping updated file: %s" % INIT_PY_PATH)
        with open(INIT_PY_PATH, "w") as init_file:
            init_file.write(contents)

        self.__print(
            "\nFinished!\n"
            "Please check the git diff to make sure everything went okay.\n"
            "You should also edit README.md and "
            "qtawesome/docs/source/usage.rst to reflect the changes."
        )

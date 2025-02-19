import abc
import argparse
import hashlib
import html.parser
import json
import os
import re
import sys
import urllib.request

FONTS_DIR = os.path.join("qtawesome", "fonts")
ICONIC_FONT_PY_PATH = os.path.join("qtawesome", "iconic_font.py")

FONT_CONF = {
    "fa": {
        "version": "v4.7.0",  # last 4.x version
        "baseurl": "https://github.com/FortAwesome/Font-Awesome",

        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/fonts/fontawesome-webfont.ttf",
        "cmap_url": "{baseurl}/raw/{version}/css/font-awesome.css",
        "font_loc": os.path.join(FONTS_DIR, "fontawesome4.7-webfont.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "fontawesome4.7-webfont-charmap.json"),
    },
    "fa5": {
        "version": "master",
        "baseurl": "https://github.com/FortAwesome/Font-Awesome",

        "updater": "FA5FontUpdater",
        "style": "regular", "weight": "400",
        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/webfonts/fa-{style}-{weight}.ttf",
        "cmap_url": "{baseurl}/raw/{version}/metadata/icons.json",
        "font_loc": os.path.join(FONTS_DIR, "fontawesome5-{style}-webfont.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "fontawesome5-{style}-webfont-charmap.json"),
    },
    "fa5s": {
        "version": "master",
        "baseurl": "https://github.com/FortAwesome/Font-Awesome",

        "updater": "FA5FontUpdater",
        "style": "solid", "weight": "900",
        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/webfonts/fa-{style}-{weight}.ttf",
        "cmap_url": "{baseurl}/raw/{version}/metadata/icons.json",
        "font_loc": os.path.join(FONTS_DIR, "fontawesome5-{style}-webfont.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "fontawesome5-{style}-webfont-charmap.json"),
    },
    "fa5b": {
        "version": "master",
        "baseurl": "https://github.com/FortAwesome/Font-Awesome",

        "updater": "FA5FontUpdater",
        "style": "brands", "weight": "400",
        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/webfonts/fa-{style}-{weight}.ttf",
        "cmap_url": "{baseurl}/raw/{version}/metadata/icons.json",
        "font_loc": os.path.join(FONTS_DIR, "fontawesome5-{style}-webfont.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "fontawesome5-{style}-webfont-charmap.json"),
    },
    "ei": {
        "version": "master",
        "baseurl": "https://github.com/dovy/elusive-icons",

        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/fonts/elusiveicons-webfont.ttf",
        "cmap_url": "{baseurl}/raw/{version}/css/elusive-icons.css",
        "font_loc": os.path.join(FONTS_DIR, "elusiveicons-webfont.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "elusiveicons-webfont-charmap.json"),
    },
    "mdi": {
        "version": "v5.9.55",  # last 5.x version
        "baseurl": "https://github.com/Templarian/MaterialDesign-Webfont",

        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/fonts/materialdesignicons-webfont.ttf",
        "cmap_url": "{baseurl}/raw/{version}/css/materialdesignicons.css",
        "font_loc": os.path.join(FONTS_DIR, "materialdesignicons5-webfont.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "materialdesignicons5-webfont-charmap.json"),
    },
    "mdi6": {
        "version": "master",
        "baseurl": "https://github.com/Templarian/MaterialDesign-Webfont",

        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/fonts/materialdesignicons-webfont.ttf",
        "cmap_url": "{baseurl}/raw/{version}/css/materialdesignicons.css",
        "font_loc": os.path.join(FONTS_DIR, "materialdesignicons6-webfont.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "materialdesignicons6-webfont-charmap.json"),
    },
    "ph": {
        "version": "master",
        "baseurl": "https://github.com/phosphor-icons/phosphor-icons",

        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/src/font/phosphor.ttf",
        "cmap_url": "{baseurl}/raw/{version}/src/css/phosphor.css",
        "font_loc": os.path.join(FONTS_DIR, "phosphor.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "phosphor-charmap.json"),
    },
    "ri": {
        "version": "master",
        "baseurl": "https://github.com/Remix-Design/RemixIcon",

        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/fonts/remixicon.ttf",
        "cmap_url": "{baseurl}/raw/{version}/fonts/remixicon.css",
        "font_loc": os.path.join(FONTS_DIR, "remixicon.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "remixicon-charmap.json"),
    },
    "msc": {
        "version": "main",
        "baseurl": "https://github.com/microsoft/vscode-codicons",

        "info_url": "{baseurl}/commits/{version}",
        "font_url": "{baseurl}/raw/{version}/dist/codicon.ttf",
        "cmap_url": "{baseurl}/raw/{version}/dist/codicon.css",
        "font_loc": os.path.join(FONTS_DIR, "codicon.ttf"),
        "cmap_loc": os.path.join(FONTS_DIR, "codicon-charmap.json"),
    },
}

FONT_OPTS = argparse.ArgumentParser()
FONT_OPTS.add_argument("--prefix", choices=FONT_CONF.keys(), required=True)
FONT_OPTS.add_argument("--version")
FONT_OPTS.add_argument("--cmaphex", choices=["asis", "no", "0x", "0X"], default="asis")
FONT_OPTS.add_argument("--cmapfmt", choices=["asis", "lower", "upper"], default="asis")
FONT_OPTS.add_argument("--nopatch", action="store_const", const=True)
FONT_OPTS.add_argument("--compat", action="store_const", const=True)


def main(argv):
    opts = FONT_OPTS.parse_args(argv[1:])
    conf = FONT_CONF[opts.prefix]
    args = prep_args(conf, opts)
    globals()[args.get("updater", "FontUpdater")](**args).run()


def prep_args(conf, opts):
    args = dict(**conf)
    for key, val in vars(opts).items():
        if val is not None:
            args[key] = val
    for key, val in args.items():
        if isinstance(val, str):
            args[key] = val.format(**args)
    return args


def urlopen(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.request.URLError as error:
        raise RuntimeError(f"{str(error)}: {url}")


def md5sum(file):
    with open(file, "rb") as fp:
        return hashlib.md5(fp.read()).hexdigest()


class FontUpdater:
    def __init__(self, *args, **kwargs):
        self.info_url = kwargs["info_url"]
        self.font_url = kwargs["font_url"]
        self.cmap_url = kwargs["cmap_url"]
        self.font_loc = kwargs["font_loc"]
        self.cmap_loc = kwargs["cmap_loc"]
        self.nopatch = kwargs.get("nopatch", False)
        self.cmaphex = kwargs.get("cmaphex", "asis")
        self.cmapfmt = kwargs.get("cmapfmt", "asis")

    def run(self):
        print("Update started")
        print("")
        self.print_info()
        self.store_cmap()
        self.store_font()
        self.patch_font()
        self.patch_iconic()
        print("Update finished")
        print("")

    def print_info(self):
        class InfoParser(html.parser.HTMLParser, abc.ABC):
            def __init__(self):
                super().__init__()
                self.value = ""

            def handle_starttag(self, tag, attrs):
                # store first <a href=".../commit/...">
                if self.value or tag != "a":
                    return
                for key, val in attrs:
                    if key != "href" or "/commit/" not in val:
                        continue
                    self.value = val
                    break

        with urlopen(self.info_url) as fp:
            parser = InfoParser()
            parser.feed(fp.read().decode())
            info = parser.value
        print(f"Info URL      : {info}")
        print("")

    def parse_cmap(self, data):
        cmap = {}
        patt = r'^\.[^-]+-([^:]+)::?before\s*{\s*content:\s*"(.+)";?\s*}$'
        for name, key in re.findall(patt, data.decode(), re.MULTILINE):
            cmap[name] = key.replace("\\", "")
        return cmap

    def store_cmap(self):
        with urlopen(self.cmap_url) as fp:
            cmap = self.parse_cmap(fp.read())
        assert len(cmap) > 0
        if self.cmapfmt != "asis":
            for key, val in cmap.items():
                if self.cmapfmt == "upper":
                    cmap[key] = val.upper()
                elif self.cmapfmt == "lower":
                    cmap[key] = val.lower()
        if self.cmaphex != "asis":
            for key, val in cmap.items():
                cmap[key] = re.sub(r"^0x", "", val, re.IGNORECASE)
                if self.cmaphex != "no":
                    cmap[key] = f"{self.cmaphex}{val}"
        with open(self.cmap_loc, "w") as fp:
            json.dump(cmap, fp, indent=4, sort_keys=True)
        print(f"Charmap URL   : {self.cmap_url}")
        print(f"Charmap Path  : {self.cmap_loc}")
        print("")
        print(f"Charmap Count : {len(cmap)}")
        print(f"Charmap Hex   : {self.cmaphex}")
        print(f"Charmap Format: {self.cmapfmt}")
        print("")

    def store_font(self):
        with urlopen(self.font_url) as fp:
            data = fp.read()
        with open(self.font_loc, "wb") as fp:
            fp.write(data)
        print(f"Font URL      : {self.font_url}")
        print(f"Font Path     : {self.font_loc}")
        print("")
        print(f"Font md5sum   : {md5sum(self.font_loc)}")
        print("")

    def alter_name(self, record, oldstring):
        return f"qta+{md5sum(self.font_loc)[:6]}@{oldstring}"

    def patch_font(self):
        if self.nopatch:
            print(f"Patch Font    : nothing")
            print("")
            return
        try:
            import fontTools.ttLib
        except ImportError:
            print(f"Patch Font    : skip (fontTools is unavailable)")
            print("")
            return
        ttfont = fontTools.ttLib.TTFont(
            self.font_loc, recalcBBoxes=False, recalcTimestamp=False)
        if "CFF " in ttfont:
            raise RuntimeError(f"ERROR: cannot process: {self.font_loc}")
        # https://docs.microsoft.com/en-us/typography/opentype/spec/name
        kind = {
            1: "Font Family Name",
            4: "Full Font Name",
            6: "PostScript Name",
            16: "Typographic Family Name",
            21: "WWS Family Name",
        }
        for record in ttfont["name"].names:
            if record.nameID not in kind:
                continue
            if record.platformID == 1:
                code = "utf-8"
            elif record.platformID == 3 and record.platEncID == 1:
                code = "utf-16-be"
            else:
                raise RuntimeError(
                    f"ERROR: Unsupported code: "
                    f"platformID={record.platformID} "
                    f"platEncID={record.platEncID}: "
                    f"{self.font_loc}")
            oldstring = record.string.decode(code)
            newstring = self.alter_name(record, oldstring)
            if newstring is not None:
                record.string = newstring.encode(code)
                print(f"Patch Font    : "
                      f"{code:<10} {kind[record.nameID]:<24} -> {newstring}")
        ttfont.save(self.font_loc, reorderTables=False)
        print("")
        print(f"Font md5sum   : {md5sum(self.font_loc)}")
        print("")

    def patch_iconic(self):
        with open(ICONIC_FONT_PY_PATH, "r") as iconic_file:
            contents = iconic_file.read()
        regex = rf"('{os.path.basename(self.font_loc)}':\s+)'(\w+)'"
        subst = rf"\g<1>'{md5sum(self.font_loc)}'"
        contents = re.sub(regex, subst, contents, 1)
        with open(ICONIC_FONT_PY_PATH, 'w') as iconic_file:
            iconic_file.write(contents)


class FA5FontUpdater(FontUpdater):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = kwargs["style"]
        self.compat = kwargs.get("compat", False)

    def parse_cmap(self, data):
        cmap = {}
        for icon, info in json.loads(data).items():
            if self.style in info["styles"]:
                cmap[icon] = str(info["unicode"])
        return cmap

    def alter_name(self, record, oldstring):
        if self.compat:
            if record.nameID == 6:  # PostScript Name
                return None
            return f"Font Awesome 5 Free {self.style.title()}"
        else:
            return super().alter_name(record, oldstring)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

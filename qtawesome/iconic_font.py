r"""

Iconic Font
===========

A lightweight module handling iconic fonts.

It is designed to provide a simple way for creating QIcons from glyphs.

From a user's viewpoint, the main entry point is the ``IconicFont`` class which
contains methods for loading new iconic fonts with their character map and
methods returning instances of ``QIcon``.

"""

# Standard library imports
import ctypes
import json
import os
import shutil
import warnings

# Third party imports
from qtpy import PYSIDE_VERSION
from qtpy.QtCore import QObject, QPoint, QRect, Qt, QSizeF, QRectF, QPointF, QThread
from qtpy.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QIcon,
    QIconEngine,
    QPainter,
    QPixmap,
    QTransform,
    QPalette,
    QRawFont,
    QImage,
)
from qtpy.QtWidgets import QApplication

try:
    # Needed since `QGlyphRun` is not available for PySide2
    # See spyder-ide/qtawesome#210
    from qtpy.QtGui import QGlyphRun
except ImportError:
    QGlyphRun = None

# Linux packagers, please set this to True if you want to make qtawesome
# use system fonts
SYSTEM_FONTS = False

# Needed imports and constants to install bundled fonts on Windows
# Based on https://stackoverflow.com/a/41841088/15954282
if os.name == "nt":
    from ctypes import wintypes, windll
    import winreg

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

    FONTS_REG_PATH = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    GFRI_DESCRIPTION = 1
    GFRI_ISTRUETYPE = 3

    if not hasattr(wintypes, "LPDWORD"):
        wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

    user32.SendMessageTimeoutW.restype = wintypes.LPVOID
    user32.SendMessageTimeoutW.argtypes = (
        wintypes.HWND,  # hWnd
        wintypes.UINT,  # Msg
        wintypes.LPVOID,  # wParam
        wintypes.LPVOID,  # lParam
        wintypes.UINT,  # fuFlags
        wintypes.UINT,  # uTimeout
        wintypes.LPVOID,
    )  # lpdwResult

    gdi32.AddFontResourceW.argtypes = (wintypes.LPCWSTR,)  # lpszFilename

    # http://www.undocprint.org/winspool/getfontresourceinfo
    gdi32.GetFontResourceInfoW.argtypes = (
        wintypes.LPCWSTR,  # lpszFilename
        wintypes.LPDWORD,  # cbBuffer
        wintypes.LPVOID,  # lpBuffer
        wintypes.DWORD,
    )  # dwQueryType


def text_color():
    try:
        palette = QApplication.instance().palette()
        return palette.color(QPalette.Active, QPalette.Text)
    except AttributeError:
        return QColor(50, 50, 50)


def text_color_disabled():
    try:
        palette = QApplication.instance().palette()
        return palette.color(QPalette.Disabled, QPalette.Text)
    except AttributeError:
        return QColor(150, 150, 150)


_default_options = {
    "color": text_color,
    "color_disabled": text_color_disabled,
    "opacity": 1.0,
    "scale_factor": 1.0,
}


def set_global_defaults(**kwargs):
    """Set global defaults for the options passed to the icon painter."""

    valid_options = [
        "active",
        "selected",
        "disabled",
        "on",
        "off",
        "on_active",
        "on_selected",
        "on_disabled",
        "off_active",
        "off_selected",
        "off_disabled",
        "color",
        "color_on",
        "color_off",
        "color_active",
        "color_selected",
        "color_disabled",
        "color_on_selected",
        "color_on_active",
        "color_on_disabled",
        "color_off_selected",
        "color_off_active",
        "color_off_disabled",
        "animation",
        "offset",
        "scale_factor",
        "rotated",
        "hflip",
        "vflip",
        "draw",
    ]

    for kw in kwargs:
        if kw in valid_options:
            _default_options[kw] = kwargs[kw]
        else:
            error = "Invalid option '{0}'".format(kw)
            raise KeyError(error)


class CharIconPainter:
    """Char icon painter."""

    def paint(self, iconic, painter, rect, mode, state, options):
        """Main paint method."""
        for opt in options:
            self._paint_icon(iconic, painter, rect, mode, state, opt)

    def _paint_icon(self, iconic, painter, rect, mode, state, options):
        """Paint a single icon."""
        painter.save()

        color_options = {
            QIcon.On: {
                QIcon.Normal: (options["color_on"], options["on"]),
                QIcon.Disabled: (options["color_on_disabled"], options["on_disabled"]),
                QIcon.Active: (options["color_on_active"], options["on_active"]),
                QIcon.Selected: (options["color_on_selected"], options["on_selected"]),
            },
            QIcon.Off: {
                QIcon.Normal: (options["color_off"], options["off"]),
                QIcon.Disabled: (
                    options["color_off_disabled"],
                    options["off_disabled"],
                ),
                QIcon.Active: (options["color_off_active"], options["off_active"]),
                QIcon.Selected: (
                    options["color_off_selected"],
                    options["off_selected"],
                ),
            },
        }

        color, char = color_options[state][mode]
        alpha = None

        # If color comes as a tuple, it means we need to set alpha on it.
        if isinstance(color, tuple):
            alpha = color[1]
            color = color[0]

        qcolor = QColor(color)
        if alpha:
            qcolor.setAlpha(alpha)

        painter.setPen(qcolor)

        # A 16 pixel-high icon yields a font size of 14, which is pixel perfect
        # for font-awesome. 16 * 0.875 = 14
        # The reason why the glyph size is smaller than the icon size is to
        # account for font bearing.

        draw_size = round(0.875 * rect.height() * options["scale_factor"])
        prefix = options["prefix"]

        # Animation setup hook
        animation = options.get("animation")
        if animation is not None:
            animation.setup(self, painter, rect)

        if "offset" in options:
            rect = QRect(rect)
            rect.translate(
                round(options["offset"][0] * rect.width()),
                round(options["offset"][1] * rect.height()),
            )

        x_center = rect.width() * 0.5
        y_center = rect.height() * 0.5
        transform = QTransform()
        transform.translate(+x_center, +y_center)
        if "vflip" in options and options["vflip"] is True:
            transform.scale(1, -1)
        if "hflip" in options and options["hflip"] is True:
            transform.scale(-1, 1)
        if "rotated" in options:
            transform.rotate(options["rotated"])
        transform.translate(-x_center, -y_center)
        painter.setTransform(transform, True)

        painter.setOpacity(options.get("opacity", 1.0))

        draw = options.get("draw")
        if draw not in ("text", "path", "glyphrun", "image"):
            # Use QPainterPath when setting an animation
            # to fix tremulous spinning icons.
            # See spyder-ide/qtawesome#39
            draw = "path" if animation is not None else "text"

        def try_draw_rawfont():
            if draw == "glyphrun" and animation is not None:
                # Disable font hinting to mitigate tremulous spinning to some extent
                # See spyder-ide/qtawesome#39
                rawfont = iconic.rawfont(prefix, draw_size, QFont.PreferNoHinting)
            else:
                rawfont = iconic.rawfont(prefix, draw_size)

            # Check glyf table and fallback to draw text if missing
            # because font glyph is necessary to draw path/glyphrun/image.
            if not rawfont.fontTable("glyf"):
                return False

            glyph = rawfont.glyphIndexesForString(char)[0]
            advance = rawfont.advancesForGlyphIndexes((glyph,))[0]
            ascent = rawfont.ascent()
            size = QSizeF(abs(advance.x()), ascent + rawfont.descent())
            painter.translate(QRectF(rect).center())
            painter.translate(-size.width() / 2, -size.height() / 2)

            if draw == "path":
                path = rawfont.pathForGlyph(glyph)
                path.translate(0, ascent)
                path.setFillRule(Qt.WindingFill)
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.fillPath(path, painter.pen().color())

            elif draw == "glyphrun":
                if QGlyphRun:
                    glyphrun = QGlyphRun()
                    glyphrun.setRawFont(rawfont)
                    glyphrun.setGlyphIndexes((glyph,))
                    glyphrun.setPositions((QPointF(0, ascent),))
                    painter.drawGlyphRun(QPointF(0, 0), glyphrun)
                else:
                    warnings.warn(
                        "QGlyphRun is unavailable for the current Qt binding! "
                        "QtAwesome will use the default draw values"
                    )
                    return False
            elif draw == "image":
                image = rawfont.alphaMapForGlyph(
                    glyph, QRawFont.PixelAntialiasing
                ).convertToFormat(QImage.Format_ARGB32_Premultiplied)
                painter2 = QPainter(image)
                painter2.setCompositionMode(QPainter.CompositionMode_SourceIn)
                painter2.fillRect(image.rect(), painter.pen().color())
                painter2.end()
                brect = rawfont.boundingRect(glyph)
                brect.translate(0, ascent)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.drawImage(brect.topLeft(), image)

            else:
                # fallback to draw text if unknown value
                return False

            return True

        if draw == "text" or not try_draw_rawfont():
            font = iconic.font(prefix, draw_size)
            # Disable font hinting to mitigate tremulous spinning to some extent
            # See spyder-ide/qtawesome#39
            if animation is not None:
                font.setHintingPreference(QFont.PreferNoHinting)
            painter.setFont(font)
            painter.drawText(rect, int(Qt.AlignCenter | Qt.AlignVCenter), char)

        painter.restore()


class FontError(Exception):
    """Exception for font errors."""


class CharIconEngine(QIconEngine):
    """Specialization of QIconEngine used to draw font-based icons."""

    def __init__(self, iconic, painter, options):
        super().__init__()
        self.iconic = iconic
        self.painter = painter
        self.options = options

    def paint(self, painter, rect, mode, state):
        self.painter.paint(self.iconic, painter, rect, mode, state, self.options)

    def pixmap(self, size, mode, state):
        pm = QPixmap(size)
        pm.fill(Qt.transparent)
        self.paint(QPainter(pm), QRect(QPoint(0, 0), size), mode, state)
        return pm


class IconicFont(QObject):
    """Main class for managing iconic fonts."""

    def __init__(self, *args):
        """IconicFont Constructor.

        Parameters
        ----------
        ``*args``: tuples
            Each positional argument is a tuple of 3 or 4 values:
            - The prefix string to be used when accessing a given font set,
            - The ttf font filename,
            - The json charmap filename,
            - Optionally, the directory containing these files. When not
              provided, the files will be looked for in the QtAwesome ``fonts``
              directory.
        """
        super().__init__()
        self.painter = CharIconPainter()
        self.painters = {}
        self.fontname = {}
        self.fontdata = {}
        self.fontids = {}
        self.charmap = {}
        self.icon_cache = {}
        self.rawfont_cache = {}
        for fargs in args:
            self.load_font(*fargs)

    def load_font(self, prefix, ttf_filename, charmap_filename, directory=None):
        """Loads a font file and the associated charmap.

        If ``directory`` is None, the files will be looked for in
        the qtawesome ``fonts`` directory.

        Parameters
        ----------
        prefix: str
            Prefix string to be used when accessing a given font set
        ttf_filename: str
            Ttf font filename
        charmap_filename: str
            Charmap filename
        directory: str or None, optional
            Directory path for font and charmap files
        """

        def hook(obj):
            result = {}
            for key in obj:
                try:
                    result[key] = chr(int(obj[key], 16))
                except ValueError:
                    if int(obj[key], 16) > 0xFFFF:
                        # ignoring unsupported code in Python 2.7 32bit Windows
                        # ValueError: chr() arg not in range(0x10000)
                        pass
                    else:
                        raise FontError(
                            "Failed to load character {0}:{1}".format(key, obj[key])
                        )
            return result

        if directory is None:
            directory = self._get_fonts_directory()

        # Load font
        if QApplication.instance() is not None:
            with open(os.path.join(directory, ttf_filename), "rb") as font_data:
                data = font_data.read()
                id_ = (
                    -1
                    if os.environ.get("QTA_FORCE_SYSTEM_FONTS_LOAD") and os.name == "nt"
                    else QFontDatabase.addApplicationFontFromData(data)
                )
            font_data.close()

            if id_ == -1 and os.name == "nt":
                # Try to load font from system Fonts directory
                windows_dir = os.environ.get("WINDIR", r"C:\Windows")
                if os.path.isdir(windows_dir):
                    from_system_ttf = os.path.join(windows_dir, "Fonts", ttf_filename)
                    id_ = QFontDatabase.addApplicationFont(from_system_ttf)

            loadedFontFamilies = QFontDatabase.applicationFontFamilies(id_)

            if loadedFontFamilies:
                self.fontids[prefix] = id_
                self.fontname[prefix] = loadedFontFamilies[0]
                self.fontdata[prefix] = data
            else:
                raise FontError(
                    "Font at '{0}' appears to be empty. "
                    "If you are on Windows 10, please read "
                    "https://support.microsoft.com/"
                    "en-us/kb/3053676 "
                    "to know how to prevent Windows from blocking "
                    "the fonts that come with QtAwesome.".format(
                        os.path.join(directory, ttf_filename)
                    )
                )

            with open(os.path.join(directory, charmap_filename), "r") as codes:
                self.charmap[prefix] = json.load(codes, object_hook=hook)

    def icon(self, *names, **kwargs):
        """Return a QIcon object corresponding to the provided icon name."""
        cache_key = "{}{}".format(names, kwargs)

        if cache_key not in self.icon_cache:
            options_list = kwargs.pop("options", [{}] * len(names))
            general_options = kwargs

            if len(options_list) != len(names):
                error = '"options" must be a list of size {0}'.format(len(names))
                raise Exception(error)

            if QApplication.instance() is not None:
                parsed_options = []
                for i in range(len(options_list)):
                    specific_options = options_list[i]
                    parsed_options.append(
                        self._parse_options(specific_options, general_options, names[i])
                    )

                # Process high level API
                api_options = parsed_options

                self.icon_cache[cache_key] = self._icon_by_painter(
                    self.painter, api_options
                )
            else:
                warnings.warn(
                    "You need to have a running QApplication to use QtAwesome!"
                )
                return QIcon()
        return self.icon_cache[cache_key]

    def _parse_options(self, specific_options, general_options, name):
        live_dict = {k: v() if callable(v) else v for k, v in _default_options.items()}

        options = dict(live_dict, **general_options)
        options.update(specific_options)

        # Handle icons for modes (Active, Disabled, Selected, Normal)
        # and states (On, Off)
        icon_kw = [
            "char",
            "on",
            "off",
            "active",
            "selected",
            "disabled",
            "on_active",
            "on_selected",
            "on_disabled",
            "off_active",
            "off_selected",
            "off_disabled",
        ]
        char = options.get("char", name)
        on = options.get("on", char)
        off = options.get("off", char)
        active = options.get("active", on)
        selected = options.get("selected", active)
        disabled = options.get("disabled", char)
        on_active = options.get("on_active", active)
        on_selected = options.get("on_selected", selected)
        on_disabled = options.get("on_disabled", disabled)
        off_active = options.get("off_active", active)
        off_selected = options.get("off_selected", selected)
        off_disabled = options.get("off_disabled", disabled)

        icon_dict = {
            "char": char,
            "on": on,
            "off": off,
            "active": active,
            "selected": selected,
            "disabled": disabled,
            "on_active": on_active,
            "on_selected": on_selected,
            "on_disabled": on_disabled,
            "off_active": off_active,
            "off_selected": off_selected,
            "off_disabled": off_disabled,
        }
        names = [icon_dict.get(kw, name) for kw in icon_kw]
        prefix, chars = self._get_prefix_chars(names)
        options.update(dict(zip(*(icon_kw, chars))))
        options.update({"prefix": prefix})

        # Handle colors for modes (Active, Disabled, Selected, Normal)
        # and states (On, Off)
        color = options.get("color")
        options.setdefault("color_on", color)
        options.setdefault("color_active", options["color_on"])
        options.setdefault("color_selected", options["color_active"])
        options.setdefault("color_on_active", options["color_active"])
        options.setdefault("color_on_selected", options["color_selected"])
        options.setdefault("color_on_disabled", options["color_disabled"])
        options.setdefault("color_off", color)
        options.setdefault("color_off_active", options["color_active"])
        options.setdefault("color_off_selected", options["color_selected"])
        options.setdefault("color_off_disabled", options["color_disabled"])

        return options

    def _get_prefix_chars(self, names):
        chars = []
        for name in names:
            if "." in name:
                prefix, n = name.split(".")
                if prefix in self.charmap:
                    if n in self.charmap[prefix]:
                        chars.append(self.charmap[prefix][n])
                    else:
                        error = 'Invalid icon name "{0}" in font "{1}"'.format(
                            n, prefix
                        )
                        raise Exception(error)
                else:
                    error = 'Invalid font prefix "{0}"'.format(prefix)
                    raise Exception(error)
            else:
                raise Exception("Invalid icon name")

        return prefix, chars

    def font(self, prefix, size):
        """Return a QFont corresponding to the given prefix and size."""
        font = QFont()
        font.setFamily(self.fontname[prefix])
        font.setPixelSize(round(size))
        if prefix[-1] == "s":  # solid style
            font.setStyleName("Solid")
        return font

    def rawfont(self, prefix, size, hintingPreference=QFont.PreferDefaultHinting):
        """Return a QRawFont corresponding to the given prefix and size."""
        cache = self.rawfont_cache
        # https://doc.qt.io/qt-5/qrawfont.html
        # QRawFont is considered local to the thread in which it is constructed
        # (either using a constructor, or by calling loadFromData() or loadFromFile()).
        # The QRawFont cannot be moved to a different thread,
        # but will have to be recreated in the thread in question.
        if PYSIDE_VERSION:
            # Needed since PySide* bindings don't expose QThread.currentThreadId
            tid = str(QThread.currentThread())
        else:
            tid = int(QThread.currentThreadId())

        if tid not in cache:
            cache[tid] = {}

            def clear_cache():
                cache.pop(tid)

            QThread().currentThread().finished.connect(clear_cache)
        key = prefix, size, hintingPreference
        if key not in cache[tid]:
            cache[tid][key] = QRawFont(self.fontdata[prefix], size, hintingPreference)
        return cache[tid][key]

    def set_custom_icon(self, name, painter):
        """Associate a user-provided CharIconPainter to an icon name.

        The custom icon can later be addressed by calling
        icon('custom.NAME') where NAME is the provided name for that icon.

        Parameters
        ----------
        name: str
            name of the custom icon
        painter: CharIconPainter
            The icon painter, implementing
            ``paint(self, iconic, painter, rect, mode, state, options)``
        """
        self.painters[name] = painter

    def install_fonts_system_wide(self):
        """Install bundled fonts system wide on Windows."""
        if os.name == "nt":
            if windll.shell32.IsUserAnAdmin():
                # Execute logic to install bundled fonts system wide
                fonts_directory = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), "fonts"
                )
                self._install_fonts(fonts_directory, system_wide=True)
            else:
                # Call `qta-install-fonts-all-users` using `runas` to prompt user for admin elevation
                warnings.warn(
                    "Admin privileges are needed to install the bundled fonts. "
                    "A prompt to get them will be shown and after that this "
                    "command will be relaunched..."
                )
                windll.shell32.ShellExecuteW(
                    None, "runas", "qta-install-fonts-all-users", None, None, 0
                )

    def _custom_icon(self, name, **kwargs):
        """Return the custom icon corresponding to the given name."""
        options = dict(_default_options, **kwargs)
        if name in self.painters:
            painter = self.painters[name]
            return self._icon_by_painter(painter, options)
        else:
            return QIcon()

    def _icon_by_painter(self, painter, options):
        """Return the icon corresponding to the given painter."""
        engine = CharIconEngine(self, painter, options)
        return QIcon(engine)

    def _get_fonts_directory(self):
        """
        Get bundled fonts directory.

        On Windows an attempt to install the fonts per user is done
        to prevent errors with fonts loading.

        See spyder-ide/qtawesome#167 and spyder-ide/spyder#18642 for
        context.
        """
        fonts_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "fonts"
        )
        return self._install_fonts(fonts_directory)

    def _install_fonts(self, fonts_directory, system_wide=False):
        """
        Install bundled fonts on Windows.

        By default copy the fonts to the user Fonts folder. Passing the
        `system_wide` kwarg as `True` will instead copy them to the system
        Fonts directory (operation will fail in case the required admin
        privileges are not available).

        Based on https://stackoverflow.com/a/41841088/15954282 and
        https://superuser.com/a/1663482
        """
        if os.name != "nt":
            return fonts_directory

        # Try to get WINDIR and LOCALAPPDATA path
        windows_dir = os.environ.get("WINDIR", None)
        if not windows_dir and system_wide:
            return fonts_directory

        local_appdata_dir = os.environ.get("LOCALAPPDATA", None)
        if not local_appdata_dir and not system_wide:
            return fonts_directory

        # Construct path to fonts from WINDIR or LOCALAPPDATA
        system_fonts_dir = os.path.join(windows_dir, "Fonts")

        user_fonts_dir = os.path.join(
            local_appdata_dir, "Microsoft", "Windows", "Fonts"
        )
        os.makedirs(user_fonts_dir, exist_ok=True)

        install_fonts_dir = system_fonts_dir if system_wide else user_fonts_dir

        # Setup bundled fonts on the WINDIR or LOCALAPPDATA fonts directory
        for root, __, files in os.walk(fonts_directory):
            for filename in files:
                src_path = os.path.join(root, filename)
                dst_filename = filename
                dst_path = os.path.join(install_fonts_dir, dst_filename)

                # Check if font already exists and proceed with copy font
                # process if needed or skip it
                if os.path.isfile(dst_path):
                    continue

                shutil.copy(src_path, dst_path)

                # Further process the font file (`.ttf`)
                if os.path.splitext(filename)[-1] == ".ttf":
                    # Load the font in the current session
                    if not gdi32.AddFontResourceW(dst_path):
                        try:
                            os.remove(dst_path)
                        except OSError:
                            # Possible permission error when trying to remove
                            # a font which potentially is already in use
                            # See spyder-ide/qtawesome#236
                            continue

                    # Store the fontname/filename in the registry
                    fontname = os.path.splitext(filename)[0]

                    # Try to get the font's real name
                    cb = wintypes.DWORD()
                    if gdi32.GetFontResourceInfoW(
                        filename, ctypes.byref(cb), None, GFRI_DESCRIPTION
                    ):
                        buf = (ctypes.c_wchar * cb.value)()
                        if gdi32.GetFontResourceInfoW(
                            filename, ctypes.byref(cb), buf, GFRI_DESCRIPTION
                        ):
                            fontname = buf.value
                    is_truetype = wintypes.BOOL()
                    cb.value = ctypes.sizeof(is_truetype)
                    gdi32.GetFontResourceInfoW(
                        filename,
                        ctypes.byref(cb),
                        ctypes.byref(is_truetype),
                        GFRI_ISTRUETYPE,
                    )
                    if is_truetype:
                        fontname += " (TrueType)"
                    try:
                        with winreg.OpenKey(
                            winreg.HKEY_LOCAL_MACHINE
                            if system_wide
                            else winreg.HKEY_CURRENT_USER,
                            FONTS_REG_PATH,
                            0,
                            winreg.KEY_SET_VALUE,
                        ) as key:
                            winreg.SetValueEx(key, fontname, 0, winreg.REG_SZ, filename)
                    except OSError:
                        # Needed to support older Windows version where
                        # font installation per user is not possible/related registry
                        # entry is not available
                        # See spyder-ide/qtawesome#214
                        return fonts_directory

        return install_fonts_dir

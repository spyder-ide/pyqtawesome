r"""
qtawesome
=========

Font-Awesome and other iconic fonts for PyQt / PySide applications.

.. currentmodule:: qtawesome

.. autosummary::
   :toctree: _generate

   get_fonts_info
   install_bundled_fonts_system_wide
   icon
   load_font
   charmap
   font
   set_defaults
"""

import hashlib
import os

# Third party imports
from qtpy import QtCore, QtWidgets, QtGui

# Local imports
from ._version import __version__ as __version__, version_info as version_info
from .animation import Pulse as Pulse, Spin as Spin
from .iconic_font import IconicFont, set_global_defaults, FontError
from .iconic_font import SYSTEM_FONTS as _SYSTEM_FONTS
from .styles import dark as dark, light as light

# Constants
_resource = {"iconic": None}

_BUNDLED_FONTS = (
    (
        "fa5",
        "fontawesome5-regular-webfont-5.15.4.ttf",
        "fontawesome5-regular-webfont-charmap-5.15.4.json",
    ),
    (
        "fa5s",
        "fontawesome5-solid-webfont-5.15.4.ttf",
        "fontawesome5-solid-webfont-charmap-5.15.4.json",
    ),
    (
        "fa5b",
        "fontawesome5-brands-webfont-5.15.4.ttf",
        "fontawesome5-brands-webfont-charmap-5.15.4.json",
    ),
    (
        "fa6",
        "fontawesome6-regular-webfont-6.7.2.ttf",
        "fontawesome6-regular-webfont-charmap-6.7.2.json",
    ),
    (
        "fa6s",
        "fontawesome6-solid-webfont-6.7.2.ttf",
        "fontawesome6-solid-webfont-charmap-6.7.2.json",
    ),
    (
        "fa6b",
        "fontawesome6-brands-webfont-6.7.2.ttf",
        "fontawesome6-brands-webfont-charmap-6.7.2.json",
    ),
    ("ei", "elusiveicons-webfont-2.0.ttf", "elusiveicons-webfont-charmap-2.0.json"),
    (
        "mdi",
        "materialdesignicons5-webfont-5.9.55.ttf",
        "materialdesignicons5-webfont-charmap-5.9.55.json",
    ),
    (
        "mdi6",
        "materialdesignicons6-webfont-6.9.96.ttf",
        "materialdesignicons6-webfont-charmap-6.9.96.json",
    ),
    ("ph", "phosphor-1.3.0.ttf", "phosphor-charmap-1.3.0.json"),
    ("ri", "remixicon-2.5.0.ttf", "remixicon-charmap-2.5.0.json"),
    ("msc", "codicon-0.0.36.ttf", "codicon-charmap-0.0.36.json"),
)


# MD5 Hashes for font files bundled with qtawesome:
_MD5_HASHES = {
    "fontawesome5-regular-webfont-5.15.4.ttf": "dc47e4089f5bcb25f241bdeb2de0fb58",
    "fontawesome5-solid-webfont-5.15.4.ttf": "5de19800fc9ae73438c2e5c61d041b48",
    "fontawesome5-brands-webfont-5.15.4.ttf": "513aa607d398efaccc559916c3431403",
    "fontawesome6-regular-webfont-6.7.2.ttf": "2b9e6cb53822f6a9b42f15229a36811a",
    "fontawesome6-solid-webfont-6.7.2.ttf": "07312c769a05b2c17133da1a09db4ccf",
    "fontawesome6-brands-webfont-6.7.2.ttf": "15d54d142da2f2d6f2e90ed1d55121af",
    "elusiveicons-webfont-2.0.ttf": "207966b04c032d5b873fd595a211582e",
    "materialdesignicons5-webfont-5.9.55.ttf": "b7d40e7ef80c1d4af6d94902af66e524",
    "materialdesignicons6-webfont-6.9.96.ttf": "ecaabfbb23fdac4ddbaf897b97257a92",
    "phosphor-1.3.0.ttf": "5b8dc57388b2d86243566b996cc3a789",
    "remixicon-2.5.0.ttf": "888e61f04316f10bddfff7bee10c6dd0",
    "codicon-0.0.36.ttf": "5fcbaf4e245dde222bd74022e5c50bc7",
}


def get_fonts_info():
    """
    Return tuple with information about the bundled fonts being used.

    Notes
    -----
    The tuple contains the fonts directory path and a list of font filenames.
    """
    fonts_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")
    return (
        fonts_directory,
        [entry for entry in os.listdir(fonts_directory) if entry.endswith(".ttf")],
    )


def install_bundled_fonts_system_wide():
    _instance().install_fonts_system_wide()


def has_valid_font_ids(inst):
    """Validate instance's font ids are loaded to QFontDatabase.

    It is possible that QFontDatabase was reset or QApplication was recreated
    in both cases it is possible that font is not available.
    """
    # Check stored font ids are still available
    for font_id in inst.fontids.values():
        font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if not font_families:
            return False
    return True


def _instance():
    """
    Return the singleton instance of IconicFont.

    Functions ``icon``, ``load_font``, ``charmap``, ``font`` and
    ``set_defaults`` all rebind to methods of the singleton instance of IconicFont.
    """
    if _resource["iconic"] is not None and not has_valid_font_ids(_resource["iconic"]):
        # Reset cached instance
        _resource["iconic"] = None

    if _resource["iconic"] is None:
        # Verify that vendorized fonts are not corrupt
        if not _SYSTEM_FONTS:
            for fargs in _BUNDLED_FONTS:
                ttf_filename = fargs[1]
                ttf_hash = _MD5_HASHES.get(ttf_filename, None)
                if ttf_hash is None:
                    continue
                ttf_filepath = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), "fonts", ttf_filename
                )
                with open(ttf_filepath, "rb") as f:
                    ttf_calculated_hash_code = hashlib.md5(f.read()).hexdigest()
                if ttf_calculated_hash_code != ttf_hash:
                    raise FontError(f"Font is corrupt at: '{ttf_filepath}'")

        _resource["iconic"] = IconicFont(*_BUNDLED_FONTS)
    return _resource["iconic"]


def reset_cache():
    if _resource["iconic"] is not None:
        _resource["iconic"].icon_cache = {}


def icon(*names, **kwargs):
    """
    Return a QIcon object corresponding to the provided icon name(s).

    This function is the main interface of qtawesome.

    It can be used to create a QIcon instance from a single glyph
    or from a list of glyphs that are displayed on the top of each other.
    Such icon stacks are generally used to combine multiple glyphs to make
    more complex icons.

    Glyph names are specified by strings, of the form ``prefix.name``.
    The ``prefix`` corresponds to the font to be used and ``name`` is the
    name of the icon.

     - The prefix corresponding to Font-Awesome 6.x (regular) is 'fa6'
     - The prefix corresponding to Font-Awesome 6.x (solid) is 'fa6s'
     - The prefix corresponding to Font-Awesome 6.x (brands) is 'fa6b'
     - The prefix corresponding to Font-Awesome 5 (regular) is 'fa5'
     - The prefix corresponding to Font-Awesome 5 (solid) is 'fa5s'
     - The prefix corresponding to Font-Awesome 5 (brands) is 'fa5b'
     - The prefix corresponding to Elusive-Icons is 'ei'
     - The prefix corresponding to Material-Design-Icons 5.x is 'mdi'
     - The prefix corresponding to Material-Design-Icons 6.x is 'mdi6'
     - The prefix corresponding to Phosphor is 'ph'
     - The prefix corresponding to Remix-Icon is 'ri'
     - The prefix corresponding to Microsoft's Codicons is 'msc'

    When requesting a single glyph, options (such as color or positional offsets)
    can be passed as keyword arguments::

        import qtawesome as qta

        music_icon = qta.icon(
            'fa5s.music',
            color='blue',
            color_active='orange')

    When requesting multiple glyphs, the `options` keyword argument contains
    the list of option dictionaries to be used for each glyph::

        camera_ban = qta.icon('fa5s.camera', 'fa5s.ban', options=[{
                'scale_factor': 0.5,
                'active': 'fa5s.balance-scale'
            }, {
                'color': 'red',
                'opacity': 0.7
            }])

    Qt's ``QIcon`` object has four modes

        - ``Normal``: The user is not interacting with the icon, but the
          functionality represented by the icon is available.
        - ``Disabled``: The functionality corresponding to the icon is not
          available.
        - ``Active``: The functionality corresponding to the icon is available.
          The user is interacting with the icon, for example, moving the mouse
          over it or clicking it.
        - ``Selected``: The item represented by the icon is selected.

    The glyph for the Normal mode is the one specified with the main positional
    argument.

     - ``color``: icon color in the ``Normal`` mode.

    The following four options will apply to the icon regardless of the mode.

     - ``offset``: tuple (x, y) corresponding to the horizontal and vertical
       offsets for the glyph, specified as a proportion of the icon size.
     - ``animation``: animation object for the icon.
     - ``scale_factor``: multiplicative scale factor to be used for the glyph.

    The following options apply to the different modes of the icon

     - ``active``: name of the glyph to be used when the icon is ``Active``.
     - ``color_active``: the corresponding icon color.

     - ``disabled``: name of the glyph to be used when the icon is ``Disabled``.
     - ``color_disabled``: the corresponding icon color.

     - ``selected``: name of the glyph to be used when the icon is ``Selected``.
     - ``color_selected``: the corresponding icon color.

    Default values for these options can be specified via the function
    ``set_defaults``. If unspecified, the default defaults are::

        {
            'opacity': 1.0,
            'scale_factor': 1.0
            'color': QColor(50, 50, 50),
            'color_disabled': QColor(150, 150, 150),
        }

    If no default value is provided for ``active``, ``disabled`` or ``selected``
    the glyph specified for the ``Normal`` mode will be used.

    """
    return _instance().icon(*names, **kwargs)


def load_font(prefix, ttf_filename, charmap_filename, directory=None):
    """
    Loads a font file and the associated charmap.

    If ``directory`` is passed, the files will be looked for in the qtawesome
    ``fonts`` directory.

    Parameters
    ----------
    prefix: str
        Prefix string to be used when accessing a given font set
    ttf_filename: str
        Ttf font filename
    charmap_filename: str
        Character map filename
    directory: str or None, optional
        Directory path for font and charmap files

    Example
    -------
    If you want to load a font ``myicon.tff`` with a ``myicon-charmap.json``
    charmap added to the qtawesome ``fonts`` directory (usually located at
    ``</path/to/lib/python>/site-packages/qtawesome/fonts/``) you can use::

        qta.load_font(
            'myicon',
            'myicon.ttf',
            'myicon-charmap.json'
        )

    However, if you want to load a font ``myicon.tff`` with a
    ``myicon-charmap.json`` charmap located in a specific path outside the
    qtawesome ``font`` directory like for example ``/path/to/myproject/fonts``
    you can use::

        qta.load_font(
            'myicon',
            'myicon.ttf',
            'myicon-charmap.json',
            directory='/path/to/myproject/fonts'
        )

    """
    return _instance().load_font(prefix, ttf_filename, charmap_filename, directory)


def charmap(prefixed_name):
    """
    Return the character map used for a given font.

    Returns
    -------
    return_value: dict
        The dictionary mapping the icon names to the corresponding unicode character.

    """
    prefix, name = prefixed_name.split(".")
    return _instance().charmap[prefix][name]


def font(prefix, size):
    """
    Return the font corresponding to the specified prefix.

    This can be used to render text using the iconic font directly::

        import qtawesome as qta
        from qtpy import QtWidgets

        label = QtWidgets.QLabel(unichr(0xf19c) + ' ' + 'Label')
        label.setFont(qta.font('fa', 16))

    Parameters
    ----------
    prefix: str
        prefix string of the loaded font
    size: int
        size for the font

    """
    return _instance().font(prefix, size)


def set_defaults(**kwargs):
    """
    Set default options for icons.

    The valid keyword arguments are:

    'active', 'animation', 'color', 'color_active', 'color_disabled',
    'color_selected', 'disabled', 'offset', 'scale_factor', 'selected'.

    """
    return set_global_defaults(**kwargs)


class IconWidget(QtWidgets.QLabel):
    """
    IconWidget gives the ability to display an icon as a widget

    It supports the same arguments as `icon()`,
    for example,

        music_icon = qta.IconWidget('fa5s.music',
                                    color='blue',
                                    color_active='orange')

    The exceptions are `parent` and `size` keyword-only arguments,
    which allow setting the widget parent and initial size, correspondingly.

    It also has `setIcon()` and `setIconSize()` functions.
    """

    def __init__(self, *names, **kwargs):
        super().__init__(parent=kwargs.get("parent"))
        self._icon = None
        self._size = kwargs.get("size", QtCore.QSize(16, 16))
        self.setIcon(icon(*names, **kwargs))

    def setIcon(self, _icon):
        """
        set a new icon()

        Parameters
        ----------
        _icon: qtawesome.icon
            icon to set
        """
        self._icon = _icon
        self.setPixmap(_icon.pixmap(self._size))

    def setIconSize(self, size):
        """
        set icon size

        Parameters
        ----------
        size: QtCore.QSize
            size of the icon
        """
        self._size = size

    def update(self, *args, **kwargs):
        if self._icon:
            self.setPixmap(self._icon.pixmap(self._size))
        return super().update(*args, **kwargs)

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
from __future__ import print_function
import json
import os
import hashlib
import warnings

# Third party imports
from qtpy.QtCore import QObject, QPoint, QRect, qRound, Qt
from qtpy.QtGui import (QColor, QFont, QFontDatabase, QIcon, QIconEngine,
                        QPainter, QPixmap)
from qtpy.QtWidgets import QApplication
from six import unichr


# Linux packagers, please set this to True if you want to make qtawesome
# use system fonts
SYSTEM_FONTS = False


_default_options = {
    'color': QColor(50, 50, 50),
    'color_disabled': QColor(150, 150, 150),
    'opacity': 1.0,
    'scale_factor': 1.0,
}


def set_global_defaults(**kwargs):
    """Set global defaults for the options passed to the icon painter."""

    valid_options = [
        'active', 'selected', 'disabled', 'on', 'off',
        'on_active', 'on_selected', 'on_disabled',
        'off_active', 'off_selected', 'off_disabled',
        'color', 'color_on', 'color_off',
        'color_active', 'color_selected', 'color_disabled',
        'color_on_selected', 'color_on_active', 'color_on_disabled',
        'color_off_selected', 'color_off_active', 'color_off_disabled',
        'animation', 'offset', 'scale_factor',
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
        color = options['color']
        char = options['char']

        color_options = {
            QIcon.On: {
                QIcon.Normal: (options['color_on'], options['on']),
                QIcon.Disabled: (options['color_on_disabled'],
                                 options['on_disabled']),
                QIcon.Active: (options['color_on_active'],
                               options['on_active']),
                QIcon.Selected: (options['color_on_selected'],
                                 options['on_selected']) 
            },

            QIcon.Off: {
                QIcon.Normal: (options['color_off'], options['off']),
                QIcon.Disabled: (options['color_off_disabled'],
                                 options['off_disabled']),
                QIcon.Active: (options['color_off_active'],
                               options['off_active']),
                QIcon.Selected: (options['color_off_selected'],
                                 options['off_selected']) 
            }
        }

        color, char = color_options[state][mode]

        painter.setPen(QColor(color))

        # A 16 pixel-high icon yields a font size of 14, which is pixel perfect
        # for font-awesome. 16 * 0.875 = 14
        # The reason why the glyph size is smaller than the icon size is to
        # account for font bearing.

        draw_size = 0.875 * qRound(rect.height() * options['scale_factor'])
        prefix = options['prefix']

        # Animation setup hook
        animation = options.get('animation')
        if animation is not None:
            animation.setup(self, painter, rect)

        painter.setFont(iconic.font(prefix, draw_size))
        if 'offset' in options:
            rect = QRect(rect)
            rect.translate(options['offset'][0] * rect.width(),
                           options['offset'][1] * rect.height())

        painter.setOpacity(options.get('opacity', 1.0))

        painter.drawText(rect, Qt.AlignCenter | Qt.AlignVCenter, char)
        painter.restore()


class FontError(Exception):
    """Exception for font errors."""


class CharIconEngine(QIconEngine):

    """Specialization of QIconEngine used to draw font-based icons."""

    def __init__(self, iconic, painter, options):
        super(CharIconEngine, self).__init__()
        self.iconic = iconic
        self.painter = painter
        self.options = options

    def paint(self, painter, rect, mode, state):
        self.painter.paint(
            self.iconic, painter, rect, mode, state, self.options)

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
              provided, the files will be looked for in ``./fonts/``.
        """
        super(IconicFont, self).__init__()
        self.painter = CharIconPainter()
        self.painters = {}
        self.fontname = {}
        self.charmap = {}
        for fargs in args:
            self.load_font(*fargs)

    def load_font(self, prefix, font_filename, charmap_filename, directory=None):
        """Loads a font file and the associated charmap.

        If ``directory`` is None, the files will be looked for in ``./fonts/``.

        Parameters
        ----------
        prefix: str
            Prefix string to be used when accessing a given font set
        font_filename: str
            Ttf font filename
        charmap_filename: str
            Charmap filename
        directory: str or None, optional
            Directory for font and charmap files
        """

        def hook(obj):
            result = {}
            for key in obj:
                result[key] = unichr(int(obj[key], 16))
            return result

        if directory is None:
            directory = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), 'fonts')

        # Load font
        if QApplication.instance() is not None:
            id_ = QFontDatabase.addApplicationFont(os.path.join(directory,
                                                                font_filename))
            loadedFontFamilies = QFontDatabase.applicationFontFamilies(id_)
            if(loadedFontFamilies):
                self.fontname[prefix] = loadedFontFamilies[0]
            else:
                raise FontError(u"Font at '{0}' appears to be empty. "
                                "If you are on Windows 10, please read "
                                "https://support.microsoft.com/"
                                "en-us/kb/3053676 "
                                "to know how to prevent Windows from blocking "
                                "the fonts that come with QtAwesome.".format(
                                        os.path.join(directory, font_filename)))

            with open(os.path.join(directory, charmap_filename), 'r') as codes:
                self.charmap[prefix] = json.load(codes, object_hook=hook)

            # Verify that vendorized fonts are not corrupt
            if not SYSTEM_FONTS:
                md5_hashes = { 'Font Awesome 5 Brands-Regular-400.otf':
                                'fa63e85727b1b8ad35b9390d81617e08',
                                'Font Awesome 5 Free-Regular-400.otf':
                                '57f731fe9728946eea37155e8ca0479a',
                                'Font Awesome 5 Free-Solid-900.otf':
                                '6a001f8bc3ace8d0fff495ebd123413e',
                                'elusiveicons-webfont.ttf':
                                '207966b04c032d5b873fd595a211582e'}
                ttf_hash = md5_hashes.get(font_filename, None)
                if ttf_hash is not None:
                    hasher = hashlib.md5()
                    with open(os.path.join(directory, font_filename),
                              'rb') as f:
                        content = f.read()
                        hasher.update(content)
                    ttf_calculated_hash_code = hasher.hexdigest()
                    if ttf_calculated_hash_code != ttf_hash:
                        raise FontError(u"Font is corrupt at: '{0}'".format(
                                        os.path.join(directory, font_filename)))

    def icon(self, *names, **kwargs):
        """Return a QIcon object corresponding to the provided icon name."""
        options_list = kwargs.pop('options', [{}] * len(names))
        general_options = kwargs

        if len(options_list) != len(names):
            error = '"options" must be a list of size {0}'.format(len(names))
            raise Exception(error)

        if QApplication.instance() is not None:
            parsed_options = []
            for i in range(len(options_list)):
                specific_options = options_list[i]
                parsed_options.append(self._parse_options(specific_options,
                                                          general_options,
                                                          names[i]))

            # Process high level API
            api_options = parsed_options

            return self._icon_by_painter(self.painter, api_options)
        else:
            warnings.warn("You need to have a running "
                          "QApplication to use QtAwesome!")
            return QIcon()

    def _parse_options(self, specific_options, general_options, name):
        options = dict(_default_options, **general_options)
        options.update(specific_options)

        # Handle icons for modes (Active, Disabled, Selected, Normal)
        # and states (On, Off)
        icon_kw = ['char', 'on', 'off', 'active', 'selected', 'disabled',
                   'on_active', 'on_selected', 'on_disabled', 'off_active',
                   'off_selected', 'off_disabled']
        char = options.get('char', name)
        on = options.get('on', char)
        off = options.get('off', char)
        active = options.get('active', on)
        selected = options.get('selected', active)
        disabled = options.get('disabled', char)
        on_active = options.get('on_active', active)
        on_selected = options.get('on_selected', selected)
        on_disabled = options.get('on_disabled', disabled)
        off_active = options.get('off_active', active)
        off_selected = options.get('off_selected', selected)
        off_disabled = options.get('off_disabled', disabled)

        icon_dict = {'char': char,
                     'on': on,
                     'off': off,
                     'active': active,
                     'selected': selected,
                     'disabled': disabled,
                     'on_active': on_active,
                     'on_selected': on_selected,
                     'on_disabled': on_disabled,
                     'off_active': off_active,
                     'off_selected': off_selected,
                     'off_disabled': off_disabled,
                     }
        names = [icon_dict.get(kw, name) for kw in icon_kw]
        prefix, chars = self._get_prefix_chars(names)
        options.update(dict(zip(*(icon_kw, chars))))
        options.update({'prefix': prefix})

        # Handle colors for modes (Active, Disabled, Selected, Normal)
        # and states (On, Off)
        color = options.get('color')
        options.setdefault('color_on', color)
        options.setdefault('color_active', options['color_on'])
        options.setdefault('color_selected', options['color_active'])
        options.setdefault('color_on_active', options['color_active'])
        options.setdefault('color_on_selected', options['color_selected'])
        options.setdefault('color_on_disabled', options['color_disabled'])
        options.setdefault('color_off', color)
        options.setdefault('color_off_active', options['color_active'])
        options.setdefault('color_off_selected', options['color_selected'])
        options.setdefault('color_off_disabled', options['color_disabled'])

        return options

    def _get_prefix_chars(self, names):
        chars = []
        for name in names:
            if '.' in name:
                prefix, n = name.split('.')
                if prefix in self.charmap:
                    if n in self.charmap[prefix]:
                        chars.append(self.charmap[prefix][n])
                    else:
                        error = 'Invalid icon name "{0}" in font "{1}"'.format(
                            n, prefix)
                        raise Exception(error)
                else:
                    error = 'Invalid font prefix "{0}"'.format(prefix)
                    raise Exception(error)
            else:
                raise Exception('Invalid icon name')

        return prefix, chars

    def font(self, prefix, size):
        """Return a QFont corresponding to the given prefix and size."""
        font = QFont(self.fontname[prefix])
        font.setPixelSize(size)
        return font

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

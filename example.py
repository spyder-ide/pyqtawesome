# -*- coding: utf-8 -*-

# Standard library imports
import sys

# Third party imports
from qtpy import QtCore, QtWidgets
from six import unichr

# Local imports
import qtawesome as qta


class AwesomeExample(QtWidgets.QDialog):

    def __init__(self):
        super(AwesomeExample, self).__init__()

        # Get icons by name.
        # In general, in FA5 they are the same but with a new prefix:
        fa_icon = qta.icon('fas.flag')
        fa_button = QtWidgets.QPushButton(fa_icon, 'Font Awesome!')

        asl_icon = qta.icon('ei.asl')
        elusive_button = QtWidgets.QPushButton(asl_icon, 'Elusive Icons!')

        # Styling
        styling_icon = qta.icon('fas.music',
                                # some names need updating
                                # active=update_fa_name('fa.legal'),
                                active='fas.gavel',
                                color='blue',
                                color_active='orange')
        music_button = QtWidgets.QPushButton(styling_icon, 'Styling')

        # Toggle
        toggle_icon = qta.icon('fas.home', selected='fab.gavel',
                               color_off='black',
                               color_off_active='blue',
                               color_on='orange',
                               color_on_active='yellow')
        toggle_button = QtWidgets.QPushButton(toggle_icon, 'Toggle')
        toggle_button.setCheckable(True)

        # Render a label with this font
        label = QtWidgets.QLabel(unichr(0xf19c) + ' ' + 'Label')
        label.setFont(qta.font('fas', 16))

        # Stack icons
        camera_ban = qta.icon('fas.camera', 'fas.ban',
                              options=[{'scale_factor': 0.5,
                                        'active': 'fab.gavel'},
                                       {'color': 'red', 'opacity': 0.7}])
        stack_button = QtWidgets.QPushButton(camera_ban, 'Stack')
        stack_button.setIconSize(QtCore.QSize(32, 32))

        # Spin icons
        spin_button = QtWidgets.QPushButton(' Spinning icon')
        spin_icon = qta.icon('fas.spinner', color='red',
                             animation=qta.Spin(spin_button))
        spin_button.setIcon(spin_icon)

        # Pulse icons
        pulse_button = QtWidgets.QPushButton(' Pulsing icon')
        pulse_icon = qta.icon('fas.spinner', color='green',
                              animation=qta.Pulse(pulse_button))
        pulse_button.setIcon(pulse_icon)

        # Stacked spin icons
        stack_spin_button = QtWidgets.QPushButton('Stack spin')
        options = [{'scale_factor': 0.4,
                    'animation': qta.Spin(stack_spin_button)},
                   {'color': 'blue'}]
        stack_spin_icon = qta.icon('ei.asl', 'far.square',
                                   options=options)
        stack_spin_button.setIcon(stack_spin_icon)
        stack_spin_button.setIconSize(QtCore.QSize(32, 32))

        # Stack and offset icons
        saveall = qta.icon('fas.save', 'fas.save',
                           options=[{'scale_factor': 0.8,
                                     'offset': (0.2, 0.2),
                                     'color': 'gray'},
                                    {'scale_factor': 0.8}])
        saveall_button = QtWidgets.QPushButton(saveall, 'Stack, offset')

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        widgets = [fa_button, elusive_button, music_button, toggle_button,
                   stack_button, saveall_button, spin_button, pulse_button,
                   stack_spin_button, label]

        for w in widgets:
            vbox.addWidget(w)

        self.setLayout(vbox)
        self.setWindowTitle('Awesome')
        self.show()


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Enable High DPI display with PyQt5
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    QtCore.QTimer.singleShot(10000, app.exit)
    _ = AwesomeExample()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

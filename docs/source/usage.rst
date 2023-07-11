Usage
-----

Supported Fonts
~~~~~~~~~~~~~~~

QtAwesome identifies icons by their **prefix** and their **icon name**, separated by a *period* (``.``) character.

The following prefixes are currently available to use:

-  `FontAwesome`_:

   -  FA 5.15.4 features 1,608 free icons in different styles:

      -  ``fa5`` prefix has `151 icons in the "regular" style.`_
      -  ``fa5s`` prefix has `1001 icons in the "solid" style.`_
      -  ``fa5b`` prefix has `456 icons of various brands.`_

   -  ``fa`` is the legacy `FA 4.7 version with its 675 icons`_ but
      **all** of them (*and more!*) are part of FA 5.x so you should
      probably use the newer version above.

-  ``ei`` prefix holds `Elusive Icons 2.0 with its 304 icons`_.

-  `Material Design Icons`_:

   -  ``mdi6`` prefix holds `Material Design Icons 6.3.95 with its 6395 icons.`_

   -  ``mdi`` prefix holds `Material Design Icons 5.9.55 with its 5955 icons.`_

- ``ph`` prefix holds `Phosphor 1.3.0 with its 4470 icons (894 icons * 5 weights: Thin, Light, Regular, Bold and Fill).`_

- ``ri`` prefix holds `Remix Icon 2.5.0 with its 2271 icons.`_

-  ``msc`` prefix holds Microsoft's `Codicons 0.0.33 with its 426 icons.`_

.. _FontAwesome: https://fontawesome.com
.. _151 icons in the "regular" style.: https://fontawesome.com/v5/search?o=r&m=free&s=regular
.. _1001 icons in the "solid" style.: https://fontawesome.com/v5/search?o=r&m=free&s=solid
.. _456 icons of various brands.: https://fontawesome.com/v5/search?o=r&m=free&f=brands
.. _FA 4.7 version with its 675 icons: https://fontawesome.com/v4.7.0/icons/
.. _Elusive Icons 2.0 with its 304 icons: http://elusiveicons.com/icons/
.. _Material Design Icons: https://cdn.materialdesignicons.com/
.. _Material Design Icons 6.3.95 with its 6395 icons.: https://cdn.materialdesignicons.com/6.3.95/
.. _Material Design Icons 5.9.55 with its 5955 icons.: https://cdn.materialdesignicons.com/5.9.55/
.. _Phosphor 1.3.0 with its 4470 icons (894 icons * 5 weights\: Thin, Light, Regular, Bold and Fill).: https://github.com/phosphor-icons/phosphor-icons
.. _Remix Icon 2.5.0 with its 2271 icons.: https://github.com/Remix-Design/RemixIcon
.. _Codicons 0.0.33 with its 426 icons.: https://github.com/microsoft/vscode-codicons

Examples
~~~~~~~~

.. code:: python

   import qtawesome as qta

-  Use Font Awesome, Elusive Icons, Material Design Icons, Phosphor, Remix Icon or Microsoft's Codicons:

.. code:: python

   # Get FontAwesome 5.x icons by name in various styles by name
   fa5_icon = qta.icon('fa5.flag')
   fa5_button = QtWidgets.QPushButton(fa5_icon, 'Font Awesome! (regular)')

   fa5s_icon = qta.icon('fa5s.flag')
   fa5s_button = QtWidgets.QPushButton(fa5s_icon, 'Font Awesome! (solid)')

   fa5b_icon = qta.icon('fa5b.github')
   fa5b_button = QtWidgets.QPushButton(fa5b_icon, 'Font Awesome! (brands)')

   # Get Elusive icons by name
   asl_icon = qta.icon('ei.asl')
   elusive_button = QtWidgets.QPushButton(asl_icon, 'Elusive Icons!')

   # Get Material Design icons 6.x by name
   apn_icon = qta.icon('mdi6.access-point-network')
   mdi6_button = QtWidgets.QPushButton(apn_icon, 'Material Design Icons!')

   # Get Phosphor by name
   mic_icon = qta.icon('ph.microphone-fill')
   ph_button = QtWidgets.QPushButton(mic_icon, 'Phosphor!')

   # Get Remix Icon by name
   truck_icon = qta.icon('ri.truck-fill')
   ri_button = QtWidgets.QPushButton(truck_icon, 'Remix Icon!')

   # Get Microsoft's Codicons by name
   squirrel_icon = qta.icon('msc.squirrel')
   msc_button = QtWidgets.QPushButton(squirrel_icon, 'Codicons!')

-  Apply some transformations:

.. code:: python

   # Rotated
   rot_icon = qta.icon('mdi.access-point-network', rotated=45)
   rot_button = QtWidgets.QPushButton(rot_icon, 'Rotated Icons!')

   # Horizontal flip
   hflip_icon = qta.icon('mdi.account-alert', hflip=True)
   hflip_button = QtWidgets.QPushButton(hflip_icon, 'Horizontally Flipped Icons!')

   # Vertical flip
   vflip_icon = qta.icon('mdi.account-alert', vflip=True)
   vflip_button = QtWidgets.QPushButton(vflip_icon, 'Vertically Flipped Icons!')

-  Apply some styling:

.. code:: python

   # Styling
   styling_icon = qta.icon('fa5s.music',
                           active='fa5s.balance-scale',
                           color='blue',
                           color_active='orange')
   music_button = QtWidgets.QPushButton(styling_icon, 'Styling')

- Set alpha in colors:

.. code:: python

   # Setting an alpha of 120 to the color of this icon. Alpha must be a number
   # between 0 and 255.
   icon_with_alpha = qta.icon('mdi.heart',
                              color=('red', 120))
   heart_button = QtWidgets.QPushButton(icon_with_alpha, 'Setting alpha')

-  Apply toggling state styling:

.. code:: python

   # Toggle
   toggle_icon = qta.icon('fa5s.home', selected='fa5s.balance-scale',
                           color_off='black',
                           color_off_active='blue',
                           color_on='orange',
                           color_on_active='yellow')
   toggle_button = QtWidgets.QPushButton(toggle_icon, 'Toggle')
   toggle_button.setCheckable(True)

- Define the way to draw icons (`text`- default for icons without animation, `path` - default for icons with animations, `glyphrun` and `image`):

.. code:: python

   # Icon drawn with the `image` option
   drawn_image_icon = qta.icon('ri.truck-fill',
                            options=[{'draw': 'image'}])
   drawn_image_button = QtWidgets.QPushButton(drawn_image_icon,
                                              'Icon drawn as an image')

-  Stack multiple icons:

.. code:: python

   # Stack icons
   camera_ban = qta.icon('fa5s.camera', 'fa5s.ban',
                        options=[{'scale_factor': 0.5,
                                    'active': 'fa5s.balance-scale'},
                                 {'color': 'red', 'opacity': 0.7}])
   stack_button = QtWidgets.QPushButton(camera_ban, 'Stack')
   stack_button.setIconSize(QtCore.QSize(32, 32))

   # Stack and offset icons
   saveall = qta.icon('fa5.save', 'fa5.save',
                     options=[{'scale_factor': 0.8,
                                 'offset': (0.2, 0.2),
                                 'color': 'gray'},
                              {'scale_factor': 0.8}])
   saveall_button = QtWidgets.QPushButton(saveall, 'Stack, offset')

-  Animations:

.. code:: python

   # Spin icons
   spin_button = QtWidgets.QPushButton(' Spinning icon')
   spin_icon = qta.icon('fa5s.spinner', color='red',
                        animation=qta.Spin(spin_button))
   spin_button.setIcon(spin_icon)

   # Pulse icons
   pulse_button = QtWidgets.QPushButton(' Pulsing icon')
   pulse_icon = qta.icon('fa5s.spinner', color='green',
                        animation=qta.Pulse(pulse_button))
   pulse_button.setIcon(pulse_icon)

   # Stacked spin icons
   stack_spin_button = QtWidgets.QPushButton('Stack spin')
   options = [{'scale_factor': 0.4,
               'animation': qta.Spin(stack_spin_button)},
               {'color': 'blue'}]
   stack_spin_icon = qta.icon('ei.asl', 'fa5.square',
                              options=options)
   stack_spin_button.setIcon(stack_spin_icon)
   stack_spin_button.setIconSize(QtCore.QSize(32, 32))

-  Apply font label rendering:

.. code:: python

   # Render a label with this font
   label = QtWidgets.QLabel(unichr(0xf19c) + ' ' + 'Label')
   label.setFont(qta.font('fa', 16))

- Display Icon as a widget:

.. code:: python

   # Spinning icon widget
   spin_widget = qta.IconWidget()
   spin_icon = qta.icon('mdi.loading', color='red',
                        animation=qta.Spin(spin_widget))
   spin_widget.setIcon(spin_icon)

   # simple widget
   simple_widget = qta.IconWidget('mdi.web', color='blue',
                                  size=QtCore.QSize(16, 16))

Screenshot
~~~~~~~~~~

.. image:: ../../qtawesome-screenshot.gif

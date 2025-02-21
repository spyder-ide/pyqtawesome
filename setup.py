# -*- coding: utf-8 -*-
import os
import io

from setuptools import setup

# Code to add custom build commands comes from here:
import setupbase

HERE = os.path.abspath(os.path.dirname(__file__))

VERSION_NS = {}
with open(os.path.join(HERE, "qtawesome", "_version.py")) as f:
    exec(f.read(), {}, VERSION_NS)

with io.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


setup(
    name="QtAwesome",
    version=VERSION_NS["__version__"],
    description="FontAwesome icons in PyQt and PySide applications",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Sylvain Corlay and the Spyder Development Team",
    author_email="spyder.python@gmail.com",
    maintainer="Spyder Development Team and QtAwesome Contributors",
    maintainer_email="spyder.python@gmail.com",
    license="MIT",
    url="https://github.com/spyder-ide/qtawesome",
    keywords=["PyQt", "PySide", "Icons", "Font Awesome", "Fonts"],
    packages=["qtawesome"],
    install_requires=["qtpy"],
    include_package_data=True,
    python_requires=">=3.7",
    platforms=["OS-independent"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    cmdclass={
        "update_fa6": setupbase.UpdateFA6Command,
        "update_msc": setupbase.UpdateCodiconCommand,
    },
    entry_points={
        "console_scripts": [
            "qta-browser=qtawesome.icon_browser:run",
            "qta-install-fonts-all-users=qtawesome:install_bundled_fonts_system_wide",
        ],
    },
)

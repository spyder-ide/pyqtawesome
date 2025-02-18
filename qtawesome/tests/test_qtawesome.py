r"""
Tests for QtAwesome.
"""

# Standard library imports
import collections
import os
import subprocess
import sys

# Test Library imports
import pytest

# Local imports
from qtawesome.iconic_font import IconicFont
import qtawesome as qta


def test_segfault_import():
    output_number = subprocess.call(
        sys.executable + ' -c "import qtawesome ' '; qtawesome.icon()"', shell=True
    )
    assert output_number == 0


def test_unique_font_family_name(qtbot):
    """
    Test that each font used by qtawesome has a unique name. If this test
    fails, this probably means that you need to rename the family name of
    some fonts. Please see PR #98 for more details on why it is necessary and
    on how to do this.

    Regression test for Issue #107
    """
    resource = qta._instance()
    assert isinstance(resource, IconicFont)

    # Check that the fonts were loaded successfully.
    fontnames = resource.fontname.values()
    assert fontnames

    # Check that qtawesome does not load fonts with duplicate family names.
    duplicates = [
        fontname
        for fontname, count in collections.Counter(fontnames).items()
        if count > 1
    ]
    assert not duplicates


@pytest.mark.skipif(os.name != "nt", reason="Only meant for Windows")
def test_bundled_font_user_installation():
    """
    Test that the bundled fonts are being installed on Windows for current user.

    See spyder-ide/qtawesome#167 and spyder-ide/spyder#18642
    """
    qta._instance()
    fonts_expected = [
        font_filename
        for _prefix, font_filename, _charmap_filename in qta._BUNDLED_FONTS
    ]
    fonts_command = [
        "powershell.exe",
        r'Get-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"',
    ]
    fonts_result = subprocess.run(
        fonts_command, capture_output=True, check=True, text=True
    ).stdout
    for font_filename in fonts_expected:
        assert font_filename in fonts_result


@pytest.mark.skipif(os.name != "nt", reason="Only meant for Windows")
def test_bundled_font_system_installation():
    """
    Test that the bundled fonts can be installed on Windows for all users.

    See spyder-ide/qtawesome#167 and spyder-ide/spyder#18642
    """
    qta.install_bundled_fonts_system_wide()
    fonts_expected = [
        "FontAwesome",
        "codicon",
        "elusiveicons",
        "Font Awesome 5 Brands Regular",
        "Font Awesome 5 Free Regular",
        "Font Awesome 5 Free Solid",
        "Material Design Icons 5.9.55 Regular",
        "Material Design Icons",
        "Phosphor",
        "remixicon",
    ]
    assert len(fonts_expected) == len(qta._BUNDLED_FONTS)
    fonts_command = [
        "powershell.exe",
        r'Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"',
    ]
    fonts_result = subprocess.run(
        fonts_command, capture_output=True, check=True, text=True
    ).stdout
    for font_filename in fonts_expected:
        assert font_filename in fonts_result


if __name__ == "__main__":
    pytest.main()

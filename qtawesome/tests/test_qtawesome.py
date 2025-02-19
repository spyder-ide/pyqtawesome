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
        sys.executable + ' -c "import qtawesome ; qtawesome.icon()"', shell=True
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
    fonts_result = (
        subprocess.run(fonts_command, capture_output=True, check=True, text=True)
        .stdout.replace("\n", "")
        .replace(" ", "")
    )
    for font_filename in fonts_expected:
        assert font_filename in fonts_result


def test_get_fonts_info():
    """
    Test that you can get the info of all the bundled fonts.
    """
    fonts_expected = [
        font_filename
        for _prefix, font_filename, _charmap_filename in qta._BUNDLED_FONTS
    ]
    fonts_root_dir, fonts_list = qta.get_fonts_info()
    assert os.path.normcase(fonts_root_dir) == os.path.normcase(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "fonts"
        )
    )
    assert set(fonts_list) == set(fonts_expected)


@pytest.mark.skipif(os.name != "nt", reason="Only meant for Windows")
def test_bundled_font_system_installation():
    """
    Test that the bundled fonts can be installed on Windows for all users.

    See spyder-ide/qtawesome#244

    Notes
    -----
    * When running this test, it's possible that a prompt for privileges
      may appear (UAC prompt).
    """
    qta.install_bundled_fonts_system_wide()
    fonts_expected = [
        font_filename
        for _prefix, font_filename, _charmap_filename in qta._BUNDLED_FONTS
    ]
    assert len(fonts_expected) == len(qta._BUNDLED_FONTS)
    fonts_command = [
        "powershell.exe",
        r'Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"',
    ]
    fonts_result = (
        subprocess.run(fonts_command, capture_output=True, check=True, text=True)
        .stdout.replace("\n", "")
        .replace(" ", "")
    )
    for font_filename in fonts_expected:
        assert font_filename in fonts_result


def test_font_load_from_system_fonts(monkeypatch):
    """
    Test that the bundled fonts can be accessed from the system fonts folder on
    Windows.

    Notes
    -----
    * This test ensures that the logic to load fonts from the system fonts
      only affects Windows even when it is being forced.
    * When running this test, it's possible that a prompt for privileges may
      appear (UAC prompt).
    """
    qta.install_bundled_fonts_system_wide()
    with monkeypatch.context() as m:
        qta._resource["iconic"] = None
        m.setenv("QTA_FORCE_SYSTEM_FONTS_LOAD", "true")
        qta._instance()


if __name__ == "__main__":
    pytest.main()

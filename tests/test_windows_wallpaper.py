from __future__ import annotations

import sys
from unittest.mock import MagicMock

from harite.windows_wallpaper import (
    SPIF_UPDATEINIFILE,
    TILE_WALLPAPER_OFF,
    WALLPAPER_STYLE_SPAN,
    apply_windows_wallpaper_file,
    ensure_span_style,
)


def _patch_windows_wallpaper_deps(monkeypatch):
    monkeypatch.setattr("harite.windows_wallpaper.platform.system", lambda: "Windows")

    key = MagicMock()
    mock_winreg = MagicMock()
    mock_winreg.OpenKey.return_value.__enter__.return_value = key
    mock_winreg.HKEY_CURRENT_USER = 0
    mock_winreg.KEY_SET_VALUE = 1
    mock_winreg.REG_SZ = 1
    monkeypatch.setitem(sys.modules, "winreg", mock_winreg)

    mock_user32 = MagicMock()
    mock_ctypes = MagicMock()
    mock_ctypes.windll.user32 = mock_user32
    monkeypatch.setitem(sys.modules, "ctypes", mock_ctypes)

    mock_subprocess = MagicMock()
    mock_subprocess.run = MagicMock(return_value=MagicMock(returncode=0))
    monkeypatch.setitem(sys.modules, "subprocess", mock_subprocess)

    return key, mock_user32, mock_subprocess


def test_ensure_span_style_sets_registry_on_windows(monkeypatch):
    _key, mock_user32, mock_subprocess = _patch_windows_wallpaper_deps(monkeypatch)

    assert ensure_span_style() is True

    mock_winreg = sys.modules["winreg"]
    assert mock_winreg.SetValueEx.call_count == 2
    calls = mock_winreg.SetValueEx.call_args_list
    assert calls[0].args[1] == "WallpaperStyle"
    assert calls[0].args[4] == WALLPAPER_STYLE_SPAN
    assert calls[1].args[1] == "TileWallpaper"
    assert calls[1].args[4] == TILE_WALLPAPER_OFF
    mock_user32.SystemParametersInfoW.assert_called_with(0x001F, 0, None, SPIF_UPDATEINIFILE)
    mock_subprocess.run.assert_called_once()


def test_ensure_span_style_noop_off_windows(monkeypatch):
    monkeypatch.setattr("harite.windows_wallpaper.platform.system", lambda: "Linux")
    assert ensure_span_style() is False


def test_apply_windows_wallpaper_file_sets_registry_and_refreshes_shell(monkeypatch, tmp_path):
    _patch_windows_wallpaper_deps(monkeypatch)
    image_path = tmp_path / "wall.jpg"
    image_path.write_bytes(b"jpeg")

    mock_user32 = sys.modules["ctypes"].windll.user32
    mock_user32.SystemParametersInfoW.return_value = 1

    assert apply_windows_wallpaper_file(image_path) is True

    mock_winreg = sys.modules["winreg"]
    wallpaper_call = mock_winreg.SetValueEx.call_args_list[0]
    assert wallpaper_call.args[1] == "Wallpaper"
    assert wallpaper_call.args[4] == str(image_path.resolve())
    mock_user32.SystemParametersInfoW.assert_any_call(20, 0, str(image_path.resolve()), 0x01 | 0x02)

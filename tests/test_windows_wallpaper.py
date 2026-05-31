from __future__ import annotations

import sys
from unittest.mock import MagicMock

from harite.windows_wallpaper import (
    TILE_WALLPAPER_OFF,
    WALLPAPER_STYLE_SPAN,
    ensure_span_style,
)


def test_ensure_span_style_sets_registry_on_windows(monkeypatch):
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

    assert ensure_span_style() is True

    assert mock_winreg.SetValueEx.call_count == 2
    calls = mock_winreg.SetValueEx.call_args_list
    assert calls[0].args[1] == "WallpaperStyle"
    assert calls[0].args[4] == WALLPAPER_STYLE_SPAN
    assert calls[1].args[1] == "TileWallpaper"
    assert calls[1].args[4] == TILE_WALLPAPER_OFF


def test_ensure_span_style_noop_off_windows(monkeypatch):
    monkeypatch.setattr("harite.windows_wallpaper.platform.system", lambda: "Linux")
    assert ensure_span_style() is False

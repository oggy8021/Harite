"""Windows desktop wallpaper style helpers (B-lite Span)."""

from __future__ import annotations

import logging
import platform

logger = logging.getLogger(__name__)

WALLPAPER_STYLE_SPAN = "22"
TILE_WALLPAPER_OFF = "0"
REG_DESKTOP_PATH = r"Control Panel\Desktop"


def ensure_span_style() -> bool:
    """Set HKCU wallpaper style to Span and refresh per-user parameters."""
    try:
        import ctypes

        if platform.system() != "Windows":
            return False

        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_DESKTOP_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, WALLPAPER_STYLE_SPAN)
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, TILE_WALLPAPER_OFF)

        try:
            ctypes.windll.user32.SystemParametersInfoW(0x001F, 0, None, 0x0002)
        except Exception:
            try:
                import subprocess

                subprocess.run(
                    ["rundll32.exe", "user32.dll,UpdatePerUserSystemParameters"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
            except Exception:
                pass
        return True
    except Exception:
        logger.exception("Failed to set Windows wallpaper Span style")
        return False

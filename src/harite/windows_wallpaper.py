"""Windows desktop wallpaper style helpers (B-lite Span)."""

from __future__ import annotations

import logging
import platform
from pathlib import Path

logger = logging.getLogger(__name__)

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02
WALLPAPER_STYLE_SPAN = "22"
TILE_WALLPAPER_OFF = "0"
REG_DESKTOP_PATH = r"Control Panel\Desktop"


def refresh_windows_wallpaper_shell() -> None:
    """Best-effort refresh so Explorer picks up HKCU wallpaper changes immediately."""
    if platform.system() != "Windows":
        return

    try:
        import ctypes

        ctypes.windll.user32.SystemParametersInfoW(0x001F, 0, None, SPIF_UPDATEINIFILE)
    except Exception:
        pass

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


def apply_windows_wallpaper_file(path: str | Path) -> bool:
    """Apply a local image file as the desktop wallpaper on Windows."""
    if platform.system() != "Windows":
        return False

    wallpaper_path = Path(path).expanduser().resolve()
    if not wallpaper_path.is_file():
        logger.error("Wallpaper file does not exist: %s", wallpaper_path)
        return False

    wallpaper = str(wallpaper_path)
    try:
        import ctypes
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_DESKTOP_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, wallpaper)

        flags = SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
        success = bool(
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper, flags)
        )
        if not success:
            logger.error("SystemParametersInfoW failed for %s", wallpaper)
            return False

        refresh_windows_wallpaper_shell()
        return True
    except Exception:
        logger.exception("Failed to apply wallpaper: %s", wallpaper_path)
        return False


def ensure_span_style() -> bool:
    """Set HKCU wallpaper style to Span and refresh per-user parameters."""
    try:
        if platform.system() != "Windows":
            return False

        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_DESKTOP_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, WALLPAPER_STYLE_SPAN)
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, TILE_WALLPAPER_OFF)

        refresh_windows_wallpaper_shell()
        return True
    except Exception:
        logger.exception("Failed to set Windows wallpaper Span style")
        return False

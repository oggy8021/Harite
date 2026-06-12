"""System tray icon variant selection from OS chrome / taskbar tone."""

from __future__ import annotations

import os
import sys

_TRUTHY_ENV = frozenset({"1", "true", "yes", "on"})
_FALSY_ENV = frozenset({"0", "false", "no", "off"})


def windows_system_uses_light_taskbar() -> bool | None:
    """Read Windows taskbar light-theme flag (SystemUsesLightTheme).

    Returns ``True`` when the taskbar uses a light tone, ``False`` for dark,
    or ``None`` when unavailable (non-Windows or registry read failed).
    """
    if sys.platform != "win32":
        return None
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
        return int(value) == 1
    except OSError:
        return None


def qt_application_prefers_light_chrome() -> bool | None:
    """Best-effort Qt desktop tone via ``QStyleHints.colorScheme()``."""
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        return None

    app = QApplication.instance()
    if app is None:
        return None
    try:
        scheme = app.styleHints().colorScheme()
    except AttributeError:
        return None

    if scheme == Qt.ColorScheme.Light:
        return True
    if scheme == Qt.ColorScheme.Dark:
        return False
    return None


def tray_light_surface_env_override() -> bool | None:
    """Optional ``HARITE_TRAY_LIGHT_SURFACE`` override (1/0, true/false, etc.)."""
    raw = os.environ.get("HARITE_TRAY_LIGHT_SURFACE", "").strip().lower()
    if not raw:
        return None
    if raw in _TRUTHY_ENV:
        return True
    if raw in _FALSY_ENV:
        return False
    return None


def tray_surface_is_light() -> bool:
    """Return whether the tray area is treated as a light surface.

    Light surfaces use dark-stroke tray icons. Detection order:

    1. ``HARITE_TRAY_LIGHT_SURFACE`` env override
    2. Windows ``SystemUsesLightTheme`` (taskbar)
    3. Linux: ``False`` (XFCE/Mint status trays are usually dark; Qt app theme is not the panel strip)
    4. Qt ``colorScheme()`` (other platforms)
    5. Default ``True`` (favor visibility on Windows light taskbars)
    """
    override = tray_light_surface_env_override()
    if override is not None:
        return override
    windows = windows_system_uses_light_taskbar()
    if windows is not None:
        return windows
    if sys.platform.startswith("linux"):
        return False
    qt = qt_application_prefers_light_chrome()
    if qt is not None:
        return qt
    return True


def tray_product_icon_basename(*, slideshow_running: bool, light_surface: bool) -> str:
    """Map slideshow state and surface tone to a product icon resource file."""
    if light_surface:
        return "harite_light_bg.svg" if slideshow_running else "harite_off_light_bg.svg"
    return "harite.svg" if slideshow_running else "harite_off.svg"

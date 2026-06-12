"""System tray icon variant selection from OS chrome / taskbar tone."""

from __future__ import annotations

import sys


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


def tray_surface_is_light() -> bool:
    """Return whether the tray area is treated as a light surface.

    Light surfaces use dark-stroke tray icons. Detection order:

    1. Windows ``SystemUsesLightTheme`` (taskbar)
    2. Qt ``colorScheme()`` (desktop chrome fallback)
    3. Default ``True`` (favor visibility on Windows light taskbars)
    """
    windows = windows_system_uses_light_taskbar()
    if windows is not None:
        return windows
    qt = qt_application_prefers_light_chrome()
    if qt is not None:
        return qt
    return True


def tray_product_icon_basename(*, slideshow_running: bool, light_surface: bool) -> str:
    """Map slideshow state and surface tone to a product icon resource file."""
    if light_surface:
        return "harite_light_bg.svg" if slideshow_running else "harite_off_light_bg.svg"
    return "harite.svg" if slideshow_running else "harite_off.svg"

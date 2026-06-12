"""Tests for tray icon surface detection and resource name mapping."""

from __future__ import annotations

import sys
import types

import pytest

from harite.gui import tray_icon_theme as theme


def test_tray_product_icon_basename_dark_surface_running():
    assert (
        theme.tray_product_icon_basename(slideshow_running=True, light_surface=False)
        == "harite.svg"
    )


def test_tray_product_icon_basename_dark_surface_stopped():
    assert (
        theme.tray_product_icon_basename(slideshow_running=False, light_surface=False)
        == "harite_off.svg"
    )


def test_tray_product_icon_basename_light_surface_running():
    assert (
        theme.tray_product_icon_basename(slideshow_running=True, light_surface=True)
        == "harite_light_bg.svg"
    )


def test_tray_product_icon_basename_light_surface_stopped():
    assert (
        theme.tray_product_icon_basename(slideshow_running=False, light_surface=True)
        == "harite_off_light_bg.svg"
    )


def test_tray_surface_is_light_prefers_windows_registry(monkeypatch):
    monkeypatch.setattr(theme, "windows_system_uses_light_taskbar", lambda: False)
    monkeypatch.setattr(theme, "qt_application_prefers_light_chrome", lambda: True)

    assert theme.tray_surface_is_light() is False


def test_tray_surface_is_light_falls_back_to_qt(monkeypatch):
    monkeypatch.setattr(theme, "windows_system_uses_light_taskbar", lambda: None)
    monkeypatch.setattr(theme, "qt_application_prefers_light_chrome", lambda: False)

    assert theme.tray_surface_is_light() is False


def test_tray_surface_is_light_defaults_to_dark_surface_on_linux(monkeypatch):
    monkeypatch.setattr(theme.sys, "platform", "linux")
    monkeypatch.setattr(theme, "windows_system_uses_light_taskbar", lambda: None)
    monkeypatch.setattr(theme, "qt_application_prefers_light_chrome", lambda: True)

    assert theme.tray_surface_is_light() is False


def test_tray_surface_is_light_defaults_to_light_surface_on_windows(monkeypatch):
    monkeypatch.setattr(theme.sys, "platform", "win32")
    monkeypatch.setattr(theme, "windows_system_uses_light_taskbar", lambda: None)
    monkeypatch.setattr(theme, "qt_application_prefers_light_chrome", lambda: None)

    assert theme.tray_surface_is_light() is True


def test_tray_light_surface_env_override(monkeypatch):
    monkeypatch.setattr(theme.sys, "platform", "linux")
    monkeypatch.setenv("HARITE_TRAY_LIGHT_SURFACE", "1")

    assert theme.tray_surface_is_light() is True


def test_windows_system_uses_light_taskbar_non_windows(monkeypatch):
    monkeypatch.setattr(theme.sys, "platform", "linux")

    assert theme.windows_system_uses_light_taskbar() is None


def test_windows_system_uses_light_taskbar_reads_registry(monkeypatch):
    monkeypatch.setattr(theme.sys, "platform", "win32")

    class FakeKey:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    def fake_open_key(_hive, _path):
        return FakeKey()

    def fake_query_value(_key, name):
        assert name == "SystemUsesLightTheme"
        return (1, None)

    fake_winreg = types.ModuleType("winreg")
    fake_winreg.HKEY_CURRENT_USER = object()
    fake_winreg.OpenKey = fake_open_key
    fake_winreg.QueryValueEx = fake_query_value
    monkeypatch.setitem(sys.modules, "winreg", fake_winreg)

    assert theme.windows_system_uses_light_taskbar() is True


def test_qt_application_prefers_light_chrome_without_app(monkeypatch):
    monkeypatch.setattr(theme, "windows_system_uses_light_taskbar", lambda: None)

    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        pytest.skip("PyQt6 not installed")

    original = QApplication.instance
    monkeypatch.setattr(QApplication, "instance", staticmethod(lambda: None))

    assert theme.qt_application_prefers_light_chrome() is None

    monkeypatch.setattr(QApplication, "instance", original)


def test_make_icon_uses_light_surface_resource(qapp, monkeypatch):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    monkeypatch.setattr(theme, "tray_surface_is_light", lambda: True)

    adapter = QtTaskTrayAdapter(signal_backend=object(), window=None)
    icon = adapter._make_icon(slideshow_running=True)

    assert not icon.isNull()

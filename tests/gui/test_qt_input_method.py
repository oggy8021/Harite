"""Tests for qt_input_method.py (MAT-06)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def test_resolve_qt_im_module_from_gtk_fcitx5():
    from harite.gui.adapters_qt.qt_input_method import resolve_qt_im_module

    assert resolve_qt_im_module(gtk_im_module="fcitx5") == "fcitx"


def test_resolve_qt_im_module_from_xmodifiers():
    from harite.gui.adapters_qt.qt_input_method import resolve_qt_im_module

    assert resolve_qt_im_module(xmodifiers="@im=fcitx") == "fcitx"
    assert resolve_qt_im_module(xmodifiers="@im=ibus") == "ibus"


def test_resolve_qt_im_module_prefers_existing_qt_value():
    from harite.gui.adapters_qt.qt_input_method import resolve_qt_im_module

    assert resolve_qt_im_module(qt_im_module="ibus", gtk_im_module="fcitx") == "ibus"


def test_prepare_qt_input_method_env_sets_fcitx_on_linux(monkeypatch):
    from harite.gui.adapters_qt import qt_input_method

    monkeypatch.setattr(qt_input_method.sys, "platform", "linux")
    monkeypatch.delenv("QT_IM_MODULE", raising=False)
    monkeypatch.setenv("GTK_IM_MODULE", "fcitx5")
    monkeypatch.setattr(qt_input_method, "link_system_fcitx_qt_plugin_if_missing", lambda: None)

    assert qt_input_method.prepare_qt_input_method_env() == "fcitx"
    assert qt_input_method.os.environ["QT_IM_MODULE"] == "fcitx"


def test_prepare_qt_input_method_env_noop_on_windows(monkeypatch):
    from harite.gui.adapters_qt import qt_input_method

    monkeypatch.setattr(qt_input_method.sys, "platform", "win32")
    monkeypatch.delenv("QT_IM_MODULE", raising=False)
    monkeypatch.setenv("GTK_IM_MODULE", "fcitx5")

    assert qt_input_method.prepare_qt_input_method_env() is None
    assert "QT_IM_MODULE" not in qt_input_method.os.environ


@pytest.mark.skipif(sys.platform == "win32", reason="fcitx plugin linking is Linux-only")
def test_link_system_fcitx_qt_plugin_if_missing_creates_symlink(monkeypatch, tmp_path: Path):
    from harite.gui.adapters_qt import qt_input_method

    target_dir = tmp_path / "pyqt_plugins"
    target_dir.mkdir()
    source_dir = tmp_path / "system_plugins"
    source_dir.mkdir()
    source_plugin = source_dir / "libfcitx5platforminputcontextplugin.so"
    source_plugin.write_bytes(b"plugin")

    monkeypatch.setattr(qt_input_method, "pyqt6_platform_input_context_dir", lambda: target_dir)
    monkeypatch.setattr(qt_input_method, "_SYSTEM_PLUGIN_DIRS", (source_dir,))

    linked = qt_input_method.link_system_fcitx_qt_plugin_if_missing()

    assert linked == target_dir / "libfcitx5platforminputcontextplugin.so"
    assert linked.is_symlink()
    assert linked.resolve() == source_plugin.resolve()


def test_discover_system_fcitx_qt_plugins_finds_nested_path(tmp_path: Path):
    from harite.gui.adapters_qt import qt_input_method

    nested = tmp_path / "usr" / "lib" / "qt6" / "plugins" / "platforminputcontexts"
    nested.mkdir(parents=True)
    plugin = nested / "libfcitx5platforminputcontextplugin.so"
    plugin.write_bytes(b"plugin")

    original_dirs = qt_input_method._SYSTEM_PLUGIN_DIRS
    original_roots = qt_input_method._SYSTEM_LIB_SEARCH_ROOTS
    qt_input_method._SYSTEM_PLUGIN_DIRS = (nested,)
    qt_input_method._SYSTEM_LIB_SEARCH_ROOTS = (tmp_path / "usr" / "lib",)
    try:
        found = qt_input_method.discover_system_fcitx_qt_plugins()
    finally:
        qt_input_method._SYSTEM_PLUGIN_DIRS = original_dirs
        qt_input_method._SYSTEM_LIB_SEARCH_ROOTS = original_roots

    assert found == [plugin]


def test_audit_qt_fcitx_input_method_reports_plugin_dir(monkeypatch, tmp_path: Path):
    from harite.gui.adapters_qt import qt_input_method

    plugins_dir = tmp_path / "platforminputcontexts"
    plugins_dir.mkdir()
    (plugins_dir / "libibusplatforminputcontextplugin.so").write_bytes(b"ibus")

    monkeypatch.setattr(qt_input_method, "pyqt6_platform_input_context_dir", lambda: plugins_dir)
    monkeypatch.setenv("QT_IM_MODULE", "fcitx")
    monkeypatch.setattr(qt_input_method, "link_system_fcitx_qt_plugin_if_missing", lambda: None)

    report = qt_input_method.audit_qt_fcitx_input_method()

    assert report["qt_im_module"] == "fcitx"
    assert report["fcitx_plugins_after_link"] == []
    assert report["system_fcitx_qt6_plugin_candidates"] == []


def test_discover_system_fcitx_qt_plugins_ignores_qt5_path(tmp_path: Path):
    from harite.gui.adapters_qt import qt_input_method

    qt5_dir = tmp_path / "usr" / "lib" / "x86_64-linux-gnu" / "qt5" / "plugins" / "platforminputcontexts"
    qt5_dir.mkdir(parents=True)
    (qt5_dir / "libfcitxplatforminputcontextplugin.so").write_bytes(b"qt5")

    qt6_dir = tmp_path / "usr" / "lib" / "x86_64-linux-gnu" / "qt6" / "plugins" / "platforminputcontexts"
    qt6_dir.mkdir(parents=True)
    qt6_plugin = qt6_dir / "libfcitx5platforminputcontextplugin.so"
    qt6_plugin.write_bytes(b"qt6")

    original_dirs = qt_input_method._SYSTEM_PLUGIN_DIRS
    original_roots = qt_input_method._SYSTEM_LIB_SEARCH_ROOTS
    qt_input_method._SYSTEM_PLUGIN_DIRS = (qt5_dir, qt6_dir)
    qt_input_method._SYSTEM_LIB_SEARCH_ROOTS = (tmp_path / "usr" / "lib",)
    try:
        found = qt_input_method.discover_system_fcitx_qt_plugins()
        qt5_only = qt_input_method.discover_system_fcitx_qt5_plugins()
    finally:
        qt_input_method._SYSTEM_PLUGIN_DIRS = original_dirs
        qt_input_method._SYSTEM_LIB_SEARCH_ROOTS = original_roots

    assert found == [qt6_plugin]
    assert qt5_only == [qt5_dir / "libfcitxplatforminputcontextplugin.so"]


def test_configure_text_input_widget_enables_input_method(qapp):
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QLineEdit

    from harite.gui.adapters_qt.qt_input_method import configure_text_input_widget

    entry = QLineEdit()
    configure_text_input_widget(entry)

    assert entry.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert entry.testAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled) is True

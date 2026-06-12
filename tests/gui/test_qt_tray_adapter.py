"""Tests for the Qt system tray adapter (Phase 7).

Many tray tests require ``qapp`` and skip automatically when the system tray
is unavailable (headless/offscreen CI).  Module-level and non-tray tests run
in all environments.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Module importability (no Qt required)
# ---------------------------------------------------------------------------


def test_qt_tray_adapter_importable():
    from harite.gui.adapters_qt import qt_tray_adapter  # noqa: F401

    assert callable(qt_tray_adapter.initialize_qt_tasktray)
    assert hasattr(qt_tray_adapter, "QtTaskTrayAdapter")
    assert callable(qt_tray_adapter.audit_qt_system_tray)


def test_system_tray_unavailable_message_mentions_xfce_on_linux(monkeypatch):
    from harite.gui.adapters_qt.qt_tray_adapter import system_tray_unavailable_message

    monkeypatch.setattr("harite.gui.adapters_qt.qt_tray_adapter.sys.platform", "linux")
    message = system_tray_unavailable_message()
    assert "Status Tray Plugin" in message


def test_audit_qt_system_tray_skips_without_display(monkeypatch):
    from harite.gui.adapters_qt.qt_tray_adapter import audit_qt_system_tray

    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    audit = audit_qt_system_tray()
    assert audit.get("skipped") is True


# ---------------------------------------------------------------------------
# initialize_qt_tasktray returns None when tray unavailable
# ---------------------------------------------------------------------------


def test_initialize_returns_none_when_unavailable(qapp, monkeypatch):
    from harite.gui.adapters_qt import qt_tray_adapter
    from PyQt6.QtWidgets import QSystemTrayIcon

    # Force isSystemTrayAvailable to return False
    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", staticmethod(lambda: False))

    result = qt_tray_adapter.initialize_qt_tasktray(_StubBackend())
    assert result is None


# ---------------------------------------------------------------------------
# QtTaskTrayAdapter: construction and menu structure
# ---------------------------------------------------------------------------


def test_adapter_constructs_without_tray(qapp):
    """Adapter can be constructed; install() is only called by initialize."""
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    adapter = QtTaskTrayAdapter(signal_backend=_StubBackend(), window=None)
    assert adapter._tray is None
    assert adapter._menu is None


def test_adapter_build_menu_creates_actions(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    adapter = QtTaskTrayAdapter(signal_backend=_StubBackend(), window=None)
    menu = adapter._build_menu()

    assert menu is not None

    # Collect action texts (non-separator)
    from PyQt6.QtGui import QAction

    action_texts = [a.text() for a in menu.actions() if isinstance(a, QAction)]
    assert "Visible" in action_texts
    assert "Start Slideshow" in action_texts
    assert "Stop Slideshow" in action_texts
    assert "Settings" in action_texts
    assert "BaseColor" in action_texts
    assert "About" in action_texts
    assert "Quit" in action_texts


def test_adapter_menu_has_separators(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    adapter = QtTaskTrayAdapter(signal_backend=_StubBackend(), window=None)
    menu = adapter._build_menu()

    separator_count = sum(1 for a in menu.actions() if a.isSeparator())
    assert separator_count >= 2


def test_adapter_action_references_set_after_build_menu(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    adapter = QtTaskTrayAdapter(signal_backend=_StubBackend(), window=None)
    adapter._build_menu()

    assert adapter._action_visible is not None
    assert adapter._action_start is not None
    assert adapter._action_stop is not None


# ---------------------------------------------------------------------------
# refresh() logic
# ---------------------------------------------------------------------------


def test_refresh_visible_label_when_window_hidden(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend(slideshow_running=False, can_start=True)
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=_StubWindow(visible=False))
    adapter._build_menu()  # sets _action_visible

    adapter.refresh()

    assert adapter._action_visible.text() == "Visible"


def test_refresh_visible_label_when_window_shown(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend(slideshow_running=False, can_start=True)
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=_StubWindow(visible=True))
    adapter._build_menu()

    adapter.refresh()

    assert adapter._action_visible.text() == "Invisible"


def test_refresh_start_enabled_when_can_start(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend(slideshow_running=False, can_start=True)
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=None)
    adapter._build_menu()

    adapter.refresh()

    assert adapter._action_start.isEnabled()
    assert not adapter._action_stop.isEnabled()


def test_refresh_stop_enabled_when_running(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend(slideshow_running=True, can_start=False)
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=None)
    adapter._build_menu()

    adapter.refresh()

    assert adapter._action_stop.isEnabled()
    assert not adapter._action_start.isEnabled()


# ---------------------------------------------------------------------------
# Visibility toggle
# ---------------------------------------------------------------------------


def test_toggle_visibility_hides_when_visible(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    window = _StubWindow(visible=True)
    adapter = QtTaskTrayAdapter(signal_backend=_StubBackend(), window=window)
    adapter._build_menu()

    adapter._on_toggle_visibility()

    assert not window.visible


def test_toggle_visibility_shows_when_hidden(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    window = _StubWindow(visible=False)
    adapter = QtTaskTrayAdapter(signal_backend=_StubBackend(), window=window)
    adapter._build_menu()

    adapter._on_toggle_visibility()

    assert window.shown


# ---------------------------------------------------------------------------
# Backend invocation
# ---------------------------------------------------------------------------


def test_on_slideshow_start_calls_backend(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend()
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=None)
    adapter._build_menu()

    adapter._on_slideshow_start()

    assert "_on_slideshow_start_clicked" in backend.called


def test_on_slideshow_stop_calls_backend(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend()
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=None)
    adapter._build_menu()

    adapter._on_slideshow_stop()

    assert "_on_slideshow_stop_clicked" in backend.called


def test_on_settings_calls_backend(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend()
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=_StubWindow())
    adapter._build_menu()

    adapter._on_open_settings()

    assert "_on_settings_clicked" in backend.called


def test_on_color_calls_backend(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend()
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=_StubWindow())
    adapter._build_menu()

    adapter._on_open_color()

    assert "_on_color_clicked" in backend.called


def test_on_about_calls_backend(qapp):
    from harite.gui.adapters_qt.qt_tray_adapter import QtTaskTrayAdapter

    backend = _StubBackend()
    adapter = QtTaskTrayAdapter(signal_backend=backend, window=_StubWindow())
    adapter._build_menu()

    adapter._on_open_about()

    assert "_on_about_clicked" in backend.called


# ---------------------------------------------------------------------------
# install_tray on backend
# ---------------------------------------------------------------------------


def test_backend_install_tray_returns_bool(qapp, monkeypatch):
    from PyQt6.QtWidgets import QSystemTrayIcon

    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", staticmethod(lambda: False))

    backend = load_qt_runtime_signal_backend()
    result = backend.install_tray()

    assert isinstance(result, bool)
    assert result is False
    assert backend.tray_adapter is None


def test_backend_tray_adapter_property_default_none(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    # install_tray not called → still None
    assert backend.tray_adapter is None


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class _StubWindow:
    def __init__(self, *, visible: bool = True) -> None:
        self.visible = visible
        self.shown = False

    def isVisible(self) -> bool:
        return self.visible

    def hide(self) -> None:
        self.visible = False

    def show(self) -> None:
        self.visible = True
        self.shown = True

    def raise_(self) -> None:
        pass

    def activateWindow(self) -> None:
        pass


class _StubBackend:
    def __init__(self, *, slideshow_running: bool = False, can_start: bool = True) -> None:
        self._slideshow_running_flag = slideshow_running
        self._can_start = can_start
        self.called: list[str] = []
        self.objects: dict = {}

    def _get_connected_owner(self) -> None:
        return None

    @property
    def _slideshow_running(self) -> bool:
        return self._slideshow_running_flag

    def _on_slideshow_start_clicked(self) -> None:
        self.called.append("_on_slideshow_start_clicked")

    def _on_slideshow_stop_clicked(self) -> None:
        self.called.append("_on_slideshow_stop_clicked")

    def _on_settings_clicked(self) -> None:
        self.called.append("_on_settings_clicked")

    def _on_color_clicked(self) -> None:
        self.called.append("_on_color_clicked")

    def _on_about_clicked(self) -> None:
        self.called.append("_on_about_clicked")

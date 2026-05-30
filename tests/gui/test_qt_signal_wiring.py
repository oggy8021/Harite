"""Tests for qt_signal_wiring.py and QtSignalBackend.connect_signals() (Phase 8)."""

from __future__ import annotations

import pytest

pytest.importorskip("PyQt6.QtWidgets")


# ---------------------------------------------------------------------------
# Import guards
# ---------------------------------------------------------------------------


def test_qt_signal_wiring_importable():
    from harite.gui.adapters_qt import qt_signal_wiring  # noqa: F401


def test_qt_object_registry_importable():
    from harite.gui.adapters_qt import qt_object_registry  # noqa: F401


# ---------------------------------------------------------------------------
# _safe_connect helper
# ---------------------------------------------------------------------------


def test_safe_connect_on_none_does_not_raise(qapp):
    from harite.gui.adapters_qt.qt_signal_wiring import _safe_connect

    _safe_connect(None, "clicked", lambda: None)  # must not raise


def test_safe_connect_wires_signal(qapp):
    from PyQt6.QtWidgets import QPushButton

    from harite.gui.adapters_qt.qt_signal_wiring import _safe_connect

    btn = QPushButton()
    results = []
    _safe_connect(btn, "clicked", lambda: results.append(1))
    btn.click()
    assert results == [1]


# ---------------------------------------------------------------------------
# build_qt_object_aliases
# ---------------------------------------------------------------------------


def test_build_qt_object_aliases_returns_dict(qapp):
    from harite.gui.adapters_qt.qt_object_registry import build_qt_object_aliases

    result = build_qt_object_aliases({})
    assert isinstance(result, dict)


def test_build_qt_object_aliases_known_keys_present(qapp):
    from harite.gui.adapters_qt.qt_object_registry import build_qt_object_aliases

    result = build_qt_object_aliases({})
    expected_keys = [
        "lblStatus",
        "lblError",
        "tglUpperL",
        "spnTopMargin",
        "btnSetting",
        "btnDaemonize",
        "radSlideshowModeSequential",
        "SettingsDialog",
        "ColorDialog",
        "AboutDialog",
        "ImgOpenDialog",
        "SrcdirDialog",
    ]
    for key in expected_keys:
        assert key in result


def test_build_qt_object_aliases_maps_snake_to_camel(qapp):
    """Verify that aliases correctly resolve to the snake_case registry values."""
    from PyQt6.QtWidgets import QLabel, QPushButton

    from harite.gui.adapters_qt.qt_object_registry import build_qt_object_aliases

    status_lbl = QLabel()
    btn = QPushButton()
    widgets = {
        "status_label": status_lbl,
        "btn_daemonize": btn,
    }
    aliases = build_qt_object_aliases(widgets)
    assert aliases.get("lblStatus") is status_lbl
    assert aliases.get("btnDaemonize") is btn


# ---------------------------------------------------------------------------
# connect_qt_widgets
# ---------------------------------------------------------------------------


def test_connect_qt_widgets_does_not_raise_with_empty_registry(qapp):
    from harite.gui.adapters_qt.qt_signal_wiring import connect_qt_widgets

    class _FakeBackend:
        _objects: dict = {}

        def _on_pick_input_clicked(self, side):
            pass

        def _on_clear_input_clicked(self, side):
            pass

        def _on_save_clicked(self):
            pass

        def _on_optimize_clicked(self):
            pass

        def _on_apply_clicked(self):
            pass

        def _on_settings_clicked(self):
            pass

        def _on_settings_apply_clicked(self):
            pass

        def _on_settings_save_clicked(self):
            pass

        def _on_settings_close_clicked(self):
            pass

        def _on_color_clicked(self):
            pass

        def _on_color_dialog_apply_clicked(self):
            pass

        def _on_color_dialog_cancel_clicked(self):
            pass

        def _on_color_pick_clicked(self):
            pass

        def _on_about_clicked(self):
            pass

        def _on_about_dialog_close_clicked(self):
            pass

        def _on_pick_srcdir_clicked(self, side):
            pass

        def _on_slideshow_interval_changed(self, widget):
            pass

        def _on_slideshow_start_clicked(self):
            pass

        def _on_slideshow_stop_clicked(self):
            pass

        def _on_direction_pressed(self, key):
            pass

        def _on_direction_toggled(self, key):
            pass

        def _on_direction_released(self, key):
            pass

        def _on_margin_changed(self, widget):
            pass

        def _on_apply_mode_toggled(self, widget, mode):
            pass

        def _on_slideshow_mode_toggled(self, widget, mode):
            pass

        def _on_margin_text_mode_toggled(self, widget, value):
            pass

        def _on_margin_text_changed(self, entry):
            pass

        def _on_margin_position_toggled(self, widget, value):
            pass

        def _on_margin_text_max_lines_changed(self, spin):
            pass

    backend = _FakeBackend()
    connect_qt_widgets(backend, {})  # no widgets → should not raise


def test_connect_qt_widgets_wires_optimize_btn(qapp):
    from PyQt6.QtWidgets import QPushButton

    from harite.gui.adapters_qt.qt_signal_wiring import connect_qt_widgets

    class _Backend:
        calls: list = []

        def _on_optimize_clicked(self):
            self.calls.append("optimize")

        # Stubs for wiring
        def _on_pick_input_clicked(self, s): pass
        def _on_clear_input_clicked(self, s): pass
        def _on_save_clicked(self): pass
        def _on_apply_clicked(self): pass
        def _on_settings_clicked(self): pass
        def _on_settings_apply_clicked(self): pass
        def _on_settings_save_clicked(self): pass
        def _on_settings_close_clicked(self): pass
        def _on_color_clicked(self): pass
        def _on_color_dialog_apply_clicked(self): pass
        def _on_color_dialog_cancel_clicked(self): pass
        def _on_color_pick_clicked(self): pass
        def _on_about_clicked(self): pass
        def _on_about_dialog_close_clicked(self): pass
        def _on_pick_srcdir_clicked(self, s): pass
        def _on_slideshow_interval_changed(self, w): pass
        def _on_slideshow_start_clicked(self): pass
        def _on_slideshow_stop_clicked(self): pass
        def _on_direction_pressed(self, k): pass
        def _on_direction_toggled(self, k): pass
        def _on_direction_released(self, k): pass
        def _on_margin_changed(self, w): pass
        def _on_apply_mode_toggled(self, w, m): pass
        def _on_slideshow_mode_toggled(self, w, m): pass
        def _on_margin_text_mode_toggled(self, w, v): pass
        def _on_margin_text_changed(self, e): pass
        def _on_margin_position_toggled(self, w, v): pass
        def _on_margin_text_max_lines_changed(self, s): pass

    btn = QPushButton()
    b = _Backend()
    connect_qt_widgets(b, {"optimize_modern_btn": btn})
    btn.click()
    assert "optimize" in b.calls


# ---------------------------------------------------------------------------
# QtSignalBackend.connect_signals integration
# ---------------------------------------------------------------------------


def test_qt_signal_backend_connect_signals_stores_dispatch(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    dispatch = {"on_optimize": lambda: True}
    backend.connect_signals(dispatch)
    assert backend._signal_handlers.get("on_optimize") is dispatch["on_optimize"]


def test_qt_signal_backend_has_all_handler_stubs(qapp):
    """Verify all RUNTIME_HANDLER_MAP keys can be dispatched (no AttributeError)."""
    from harite.gui.adapters.ui_adapter import RUNTIME_HANDLER_MAP
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    # Map all handlers to no-op callables
    dispatch = {k: lambda *a, **kw: None for k in RUNTIME_HANDLER_MAP}
    backend.connect_signals(dispatch)
    # Spot-check that a handler invocation doesn't crash
    backend._on_optimize_clicked()
    backend._on_apply_clicked()
    backend._on_slideshow_start_clicked()
    backend._on_slideshow_stop_clicked()


# ---------------------------------------------------------------------------
# QtSignalBackend widget helpers
# ---------------------------------------------------------------------------


def test_qt_backend_set_label_text(qapp):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    lbl = QLabel()
    backend._objects["myLbl"] = lbl
    backend._set_label_text("myLbl", "test-value")
    assert lbl.text() == "test-value"


def test_qt_backend_set_spin_and_read(qapp):
    from PyQt6.QtWidgets import QSpinBox

    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    spin = QSpinBox()
    spin.setRange(0, 9999)
    backend._objects["spnTest"] = spin
    backend._set_spin_value("spnTest", 77)
    assert backend._read_spin_int("spnTest") == 77


def test_qt_backend_aliases_present_after_build_layout(qapp):
    """After build_layout(), both snake_case and camelCase keys should resolve."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    # camelCase alias added by qt_object_registry
    assert "lblStatus" in backend._objects
    assert "btnDaemonize" in backend._objects
    assert "SettingsDialog" in backend._objects


def test_qt_backend_set_toggle_active(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    # tgl_upper_l is a checkable QPushButton from Phase 3
    backend._set_toggle_active("tglUpperL", True)
    assert backend._is_toggle_active("tglUpperL") is True
    backend._set_toggle_active("tglUpperL", False)
    assert backend._is_toggle_active("tglUpperL") is False


# ---------------------------------------------------------------------------
# _on_direction_pressed
# ---------------------------------------------------------------------------


def test_on_direction_pressed_calls_handler(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    calls = []
    backend._signal_handlers["on_toggle_position_pressed"] = lambda name: calls.append(name)
    backend._on_direction_pressed("tglUpperL")
    assert "tglUpperL" in calls


# ---------------------------------------------------------------------------
# Slideshow timer
# ---------------------------------------------------------------------------


def test_start_stop_slideshow_timer(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    assert backend._slideshow_timer is None
    started = backend._start_slideshow_timer(5)
    assert started is True
    assert backend._slideshow_timer is not None
    backend._stop_slideshow_timer()
    assert backend._slideshow_timer is None

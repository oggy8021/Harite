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

        def _on_swap_input_paths_clicked(self):
            pass

        def _on_swap_slideshow_srcdirs_clicked(self):
            pass

        def _on_clear_slideshow_srcdir_clicked(self, side):
            pass

        def _on_slideshow_source_combo_changed(self, side):
            pass

        def _on_slideshow_profile_combo_changed(self):
            pass

        def _on_manage_source_registry_clicked(self):
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

        def _on_margin_changed(self, widget_name, value):
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
        def _on_swap_input_paths_clicked(self): pass
        def _on_swap_slideshow_srcdirs_clicked(self): pass
        def _on_clear_slideshow_srcdir_clicked(self, s): pass
        def _on_slideshow_source_combo_changed(self, s): pass
        def _on_slideshow_profile_combo_changed(self): pass
        def _on_manage_source_registry_clicked(self): pass
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
        def _on_margin_changed(self, widget_name, value): pass
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


def test_qt_connect_signals_syncs_startup_settings_to_widgets(qapp, monkeypatch, tmp_path):
    from harite.gui.adapters.ui_adapter import RUNTIME_HANDLER_MAP, create_mainwindow_signal_dispatch
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow
    from harite.settings_file import save_settings

    target = tmp_path / "harite-settings.json"
    save_settings(
        target,
        {
            "plugin": "windows",
            "slideshow_interval_seconds": 33,
            "slideshow_srcdir_l": "/slideshow/left",
            "slideshow_srcdir_r": "/slideshow/right",
            "margins": "12,0,0,0",
        },
    )
    monkeypatch.setattr("harite.gui.views.main_window.resolve_default_settings_path", lambda: target)

    window = MainWindow()
    assert window.slideshow_interval_seconds == 33

    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window,
        tuple(RUNTIME_HANDLER_MAP.keys()),
        handler_map=RUNTIME_HANDLER_MAP,
        signal_backend=backend,
    )
    backend.connect_signals(dispatch)

    assert backend._read_spin_int("spnInterval") == 33
    assert backend._slideshow_srcdir_l == "/slideshow/left"
    assert backend._slideshow_srcdir_r == "/slideshow/right"
    assert backend._read_spin_int("spnLeftMargin") == 12

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


def test_on_direction_toggled_passes_active_and_calls_reset(qapp):
    """MAT-01: Qt must mirror GTK toggle callback contract (name, active)."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    calls: list[tuple] = []
    backend._signal_handlers["on_toggle_position"] = (
        lambda name, active: calls.append(("toggled", name, active))
    )
    backend._signal_handlers["on_toggle_position_reset"] = (
        lambda name: calls.append(("reset", name))
    )

    backend._set_toggle_active("tglUpperL", True)
    backend._on_direction_toggled("tglUpperL")
    assert calls == [("toggled", "tglUpperL", True)]

    calls.clear()
    backend._set_toggle_active("tglUpperL", False)
    backend._on_direction_toggled("tglUpperL")
    assert calls == [("toggled", "tglUpperL", False), ("reset", "tglUpperL")]


def test_qt_direction_toggle_updates_main_window_form_state(qapp):
    """End-to-end: wired toggle click updates MainWindow align/valign."""
    from harite.gui.adapters.ui_adapter import RUNTIME_HANDLER_MAP, create_mainwindow_signal_dispatch
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window,
        tuple(RUNTIME_HANDLER_MAP.keys()),
        handler_map=RUNTIME_HANDLER_MAP,
        signal_backend=backend,
    )
    backend.connect_signals(dispatch)

    upper_l = backend._objects["tglUpperL"]
    push_right_l = backend._objects["tglPushRightL"]

    upper_l.click()
    assert window.form_state.valign == ("top", "center")

    push_right_l.click()
    assert window.form_state.align == ("right", "center")

    upper_l.click()
    assert window.form_state.valign == ("center", "center")


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


# ---------------------------------------------------------------------------
# 3-layer audit: on_pick_input argument order (path, side)
# ---------------------------------------------------------------------------


def test_on_margin_text_mode_settings_no_recursion(qapp):
    """Selecting embed pattern 'Settings' must not recurse via margin text sync."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow
    from harite.gui.adapters.ui_adapter import (
        RUNTIME_HANDLER_MAP,
        connect_signal_dispatch,
        create_mainwindow_signal_dispatch,
    )

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window, tuple(RUNTIME_HANDLER_MAP.keys()), handler_map=RUNTIME_HANDLER_MAP
    )
    connect_signal_dispatch(backend, dispatch)

    settings_btn = backend._objects["margin_text_mode_settings"]
    try:
        settings_btn.click()
    except RecursionError as exc:
        raise AssertionError("Settings embed pattern toggled into recursion") from exc

    assert window.form_state.embed_info == "params"
    assert settings_btn.isChecked()


def test_margin_spin_change_updates_form_state(qapp):
    """Margin spins at 0 must remain editable and update MainWindow.margins."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow
    from harite.gui.adapters.ui_adapter import (
        RUNTIME_HANDLER_MAP,
        connect_signal_dispatch,
        create_mainwindow_signal_dispatch,
    )

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window, tuple(RUNTIME_HANDLER_MAP.keys()), handler_map=RUNTIME_HANDLER_MAP
    )
    connect_signal_dispatch(backend, dispatch)

    left_spin = backend._objects["left_margin_spin"]
    assert left_spin.value() == 0
    assert left_spin.isEnabled()

    left_spin.setValue(12)

    assert window.form_state.margins == "12,0,0,0"


def test_margin_text_entry_editable_for_text_only(qapp):
    """Text only embed pattern must unlock the margin text entry for editing."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow
    from harite.gui.adapters.ui_adapter import (
        RUNTIME_HANDLER_MAP,
        connect_signal_dispatch,
        create_mainwindow_signal_dispatch,
    )

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window, tuple(RUNTIME_HANDLER_MAP.keys()), handler_map=RUNTIME_HANDLER_MAP
    )
    connect_signal_dispatch(backend, dispatch)

    entry = backend._objects["txtMarginText"]
    tabs = backend._objects["marginTextTabs"]
    assert entry.isReadOnly()

    backend._objects["margin_text_mode_text"].click()

    assert window.form_state.embed_info == "free"
    assert tabs.currentIndex() == 1
    assert entry.isReadOnly() is False


def test_margin_text_entry_editable_for_both(qapp):
    """Both embed pattern must unlock the margin text entry for editing."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow
    from harite.gui.adapters.ui_adapter import (
        RUNTIME_HANDLER_MAP,
        connect_signal_dispatch,
        create_mainwindow_signal_dispatch,
    )

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window, tuple(RUNTIME_HANDLER_MAP.keys()), handler_map=RUNTIME_HANDLER_MAP
    )
    connect_signal_dispatch(backend, dispatch)

    entry = backend._objects["txtMarginText"]
    backend._objects["margin_text_mode_both"].click()

    assert window.form_state.embed_info == "combo"
    assert entry.isReadOnly() is False


def test_on_optimize_clicked_does_not_recurse_on_margin_sync(qapp):
    """Optimize sync must not loop through margin text change handlers."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    backend = load_qt_runtime_signal_backend()
    window = MainWindow()
    window.on_change_input_text("C:/test/image.jpg")
    backend._signal_handlers["on_optimize"] = window.on_optimize
    backend._signal_handlers["on_change_margin_text"] = window.on_change_margin_text

    try:
        backend._on_optimize_clicked()
    except RecursionError as exc:
        raise AssertionError("Optimize handler recursed through margin text sync") from exc
    except (ValueError, OSError):
        # Optimize may fail without real image files; recursion is the only failure here.
        pass


def test_qt_optimize_result_controls_apply_button_state(qapp, tmp_path):
    """Qt optimize click must mirror GTK: apply enabled + footer feedback (P-04)."""
    from harite.gui.adapters.ui_adapter import connect_signal_dispatch, create_mainwindow_signal_dispatch
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    backend = load_qt_runtime_signal_backend()
    window = MainWindow()
    window.can_optimize = True

    def _fake_optimize() -> bool:
        window.can_apply = True
        window.last_saved_files = [str(tmp_path / "optimized.jpg")]
        window.status_message = "optimize completed"
        return True

    window.on_optimize = _fake_optimize  # type: ignore[method-assign]
    dispatch = create_mainwindow_signal_dispatch(window, ("on_optimize",))
    connect_signal_dispatch(backend, dispatch)

    optimize_btn = backend._objects["btnOptimize"]
    apply_btn = backend._objects["btnSetWall"]
    status = backend._objects["lblStatus"]

    optimize_btn.setEnabled(True)
    backend._on_optimize_clicked()

    assert apply_btn.isEnabled() is True
    assert optimize_btn.isEnabled() is True
    assert "optimize completed" in status.text()


def test_qt_runtime_syncs_result_preview_image(qapp, tmp_path):
    """After optimize, Qt preview QLabel must show pixmap, not placeholder text."""
    from PIL import Image

    from harite.gui.adapters.ui_adapter import connect_signal_dispatch, create_mainwindow_signal_dispatch
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    backend = load_qt_runtime_signal_backend()
    window = MainWindow()
    source = tmp_path / "preview.jpg"
    Image.new("RGB", (320, 180), color=(20, 30, 40)).save(source)

    def run_optimize(_form_state):
        return [source], []

    window.controller.run_optimize = run_optimize
    window.can_optimize = True

    dispatch = create_mainwindow_signal_dispatch(window, ("on_optimize",))
    connect_signal_dispatch(backend, dispatch)

    backend._on_optimize_clicked()

    preview_l = backend._objects["imgPreviewL"]
    preview_r = backend._objects["imgPreviewR"]
    assert not preview_l.pixmap().isNull()
    assert not preview_r.pixmap().isNull()


def test_on_pick_input_enables_optimize_button(qapp):
    """After valid input pick, btnOptimize must reflect MainWindow.can_optimize."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    backend = load_qt_runtime_signal_backend()
    window = MainWindow()

    class _FakeProxy:
        def open(self, *, title="Open Image", callback=None):
            if callback:
                callback("/tmp/image.jpg")

    backend._objects["ImgOpenDialog"] = _FakeProxy()
    backend._signal_handlers["on_pick_input"] = window.on_pick_input
    backend._signal_handlers["on_close_open_image_dialog"] = window.on_close_open_image_dialog

    btn = backend._objects["btnOptimize"]
    assert btn.isEnabled() is False
    backend._on_pick_input_clicked("L")
    assert window.can_optimize is True
    assert btn.isEnabled() is True


def test_on_pick_input_passes_path_then_side(qapp):
    """on_pick_input callback must receive (path, side) — not (side, path)."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    received: list = []

    class _FakeProxy:
        def open(self, *, title="Open Image", callback=None):
            if callback:
                callback("/tmp/image.jpg")
            return "/tmp/image.jpg"

    backend._objects["ImgOpenDialog"] = _FakeProxy()
    backend._signal_handlers["on_pick_input"] = lambda path, side: received.append((path, side))
    backend._signal_handlers["on_close_open_image_dialog"] = lambda: None
    backend._on_pick_input_clicked("L")
    assert received == [("/tmp/image.jpg", "L")]


def test_on_pick_input_calls_close_handler_on_confirm(qapp):
    """on_close_open_image_dialog must be called after dialog confirms."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    closed: list = []

    class _FakeProxy:
        def open(self, *, title="Open Image", callback=None):
            if callback:
                callback("/tmp/img.jpg")

    backend._objects["ImgOpenDialog"] = _FakeProxy()
    backend._signal_handlers["on_pick_input"] = lambda p, s: None
    backend._signal_handlers["on_close_open_image_dialog"] = lambda: closed.append(1)
    backend._on_pick_input_clicked("R")
    assert closed == [1]


def test_on_pick_input_calls_close_handler_on_cancel(qapp):
    """on_close_open_image_dialog must be called even when user cancels."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    closed: list = []

    class _FakeProxy:
        def open(self, *, title="Open Image", callback=None):
            pass  # no callback → user canceled

    backend._objects["ImgOpenDialog"] = _FakeProxy()
    # on_pick_input must be registered so the dialog is actually opened.
    backend._signal_handlers["on_pick_input"] = lambda p, s: None
    backend._signal_handlers["on_close_open_image_dialog"] = lambda: closed.append(1)
    backend._on_pick_input_clicked("L")
    assert closed == [1]


# ---------------------------------------------------------------------------
# 3-layer audit: on_pick_srcdir argument order + close handler
# ---------------------------------------------------------------------------


def test_on_pick_srcdir_passes_path_then_side(qapp):
    """on_pick_slideshow_srcdir callback must receive (path, side)."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    received: list = []

    class _FakeProxy:
        def open(self, *, title="Select Source Directory", callback=None):
            if callback:
                callback("/home/user/pics")
            return "/home/user/pics"

    backend._objects["SrcdirDialog"] = _FakeProxy()
    backend._signal_handlers["on_pick_slideshow_srcdir"] = lambda path, side: received.append((path, side))
    backend._signal_handlers["on_close_srcdir_dialog"] = lambda: None
    backend._on_pick_srcdir_clicked("L")
    assert received == [("/home/user/pics", "L")]


def test_on_pick_srcdir_calls_close_handler(qapp):
    """on_close_srcdir_dialog must be called after the dialog interaction."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    closed: list = []

    class _FakeProxy:
        def open(self, *, title="", callback=None):
            pass  # cancel

    backend._objects["SrcdirDialog"] = _FakeProxy()
    # on_pick_slideshow_srcdir must be registered so the dialog is opened.
    backend._signal_handlers["on_pick_slideshow_srcdir"] = lambda p, s: None
    backend._signal_handlers["on_close_srcdir_dialog"] = lambda: closed.append(1)
    backend._on_pick_srcdir_clicked("R")
    assert closed == [1]


# ---------------------------------------------------------------------------
# 3-layer audit: Export Image (save) flow
# ---------------------------------------------------------------------------


def test_on_save_clicked_calls_on_save_as_without_args(qapp):
    """on_save_as() must be called with NO arguments."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    calls: list = []

    class _FakeProxy:
        def open(self, *, title="", callback=None):
            pass  # cancel

    backend._objects["SavePathDialog"] = _FakeProxy()
    backend._signal_handlers["on_save_as"] = lambda: calls.append("save_as")
    backend._signal_handlers["on_close_save_path_dialog"] = lambda: None
    backend._on_save_clicked()
    assert calls == ["save_as"]


def test_on_save_clicked_calls_on_save_path_selected_with_path(qapp):
    """After file selection, on_save_path_selected(path) must be called."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    selected: list = []

    class _FakeProxy:
        def open(self, *, title="", callback=None):
            if callback:
                callback("/tmp/output.jpg")
            return "/tmp/output.jpg"

    backend._objects["SavePathDialog"] = _FakeProxy()
    backend._signal_handlers["on_save_as"] = lambda: None
    backend._signal_handlers["on_save_path_selected"] = lambda p: selected.append(p)
    backend._signal_handlers["on_close_save_path_dialog"] = lambda: None
    backend._on_save_clicked()
    assert selected == ["/tmp/output.jpg"]


def test_on_save_clicked_calls_on_save_path_selection_canceled(qapp):
    """When user cancels, on_save_path_selection_canceled() must be called."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    canceled: list = []

    class _FakeProxy:
        def open(self, *, title="", callback=None):
            pass  # cancel — no callback

    backend._objects["SavePathDialog"] = _FakeProxy()
    backend._signal_handlers["on_save_as"] = lambda: None
    backend._signal_handlers["on_save_path_selection_canceled"] = lambda: canceled.append(1)
    backend._signal_handlers["on_close_save_path_dialog"] = lambda: None
    backend._on_save_clicked()
    assert canceled == [1]


def test_on_save_clicked_always_calls_close_dialog(qapp):
    """on_close_save_path_dialog must be called regardless of outcome."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    closed: list = []

    class _FakeProxy:
        def open(self, *, title="", callback=None):
            if callback:
                callback("/tmp/out.jpg")

    backend._objects["SavePathDialog"] = _FakeProxy()
    backend._signal_handlers["on_save_as"] = lambda: None
    backend._signal_handlers["on_close_save_path_dialog"] = lambda: closed.append(1)
    backend._on_save_clicked()
    assert closed == [1]


# ---------------------------------------------------------------------------
# 3-layer audit: help label text on mode toggle
# ---------------------------------------------------------------------------


def test_apply_mode_toggled_updates_radio_tooltips_single_file(qapp):
    """Toggling to single-file mode must update apply mode tooltips (P-04)."""
    from harite.apply_surface import apply_mode_help_text
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    backend._on_apply_mode_toggled(None, "single-file")
    expected = apply_mode_help_text("single-file")
    assert backend._objects["radApplySingle"].toolTip() == expected
    assert backend._objects["radApplyPerMonitor"].toolTip() == expected


def test_apply_mode_toggled_updates_radio_tooltips_auto_split(qapp):
    """Toggling to per-monitor-auto-split mode must update apply mode tooltips (P-04)."""
    from harite.apply_surface import apply_mode_help_text
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    backend._on_apply_mode_toggled(None, "per-monitor-auto-split")
    expected = apply_mode_help_text("per-monitor-auto-split")
    assert backend._objects["radApplyPerMonitor"].toolTip() == expected
    assert backend._objects["radApplySingle"].toolTip() == expected


def test_slideshow_mode_toggled_updates_lblSlideshowModeHelp_sequential(qapp):
    """Toggling to sequential must update lblSlideshowModeHelp."""
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    lbl = QLabel()
    backend._objects["lblSlideshowModeHelp"] = lbl
    backend._on_slideshow_mode_toggled(None, "sequential")
    assert lbl.text() == "Sequential rotates images."


def test_slideshow_mode_toggled_updates_lblSlideshowModeHelp_random(qapp):
    """Toggling to random must update lblSlideshowModeHelp."""
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    lbl = QLabel()
    backend._objects["lblSlideshowModeHelp"] = lbl
    backend._on_slideshow_mode_toggled(None, "random")
    assert lbl.text() == "Random rotates images."

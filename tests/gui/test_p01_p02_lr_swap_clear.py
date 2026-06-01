"""P-01 / P-02: L/R swap and Slideshow per-side srcdir clear (gui-spec §4.1)."""

from __future__ import annotations

import pytest

from harite.gui.adapters.ui_adapter import RUNTIME_HANDLER_MAP
from harite.gui.views.main_window import MainWindow

P01_P02_HANDLERS = (
    "on_swap_input_paths",
    "on_swap_slideshow_srcdirs",
    "on_clear_slideshow_srcdir",
)


def test_runtime_handler_map_includes_p01_p02_handlers():
    for handler_name in P01_P02_HANDLERS:
        assert handler_name in RUNTIME_HANDLER_MAP
        assert RUNTIME_HANDLER_MAP[handler_name] == handler_name


def test_on_swap_input_paths_swaps_l_and_r():
    window = MainWindow()
    window.input_path_l = "/images/left.jpg"
    window.input_path_r = "/images/right.jpg"
    window._apply_input_paths()

    ok = window.on_swap_input_paths()

    assert ok is True
    assert window.input_path_l == "/images/right.jpg"
    assert window.input_path_r == "/images/left.jpg"
    assert window.form_state.input_value == "/images/right.jpg,/images/left.jpg"


def test_on_swap_input_paths_with_one_empty_side():
    window = MainWindow()
    window.input_path_l = "/images/only.jpg"
    window.input_path_r = ""
    window._apply_input_paths()

    assert window.on_swap_input_paths() is True

    assert window.input_path_l == ""
    assert window.input_path_r == "/images/only.jpg"
    assert window.form_state.input_value == "/images/only.jpg"


def test_on_swap_input_paths_does_not_change_slideshow_state():
    window = MainWindow()
    window.input_path_l = "a.jpg"
    window.input_path_r = "b.jpg"
    window.slideshow_srcdir_l = "/slideshow/left"
    window.slideshow_srcdir_r = "/slideshow/right"
    window._apply_input_paths()

    window.on_swap_input_paths()

    assert window.slideshow_srcdir_l == "/slideshow/left"
    assert window.slideshow_srcdir_r == "/slideshow/right"


def test_on_swap_slideshow_srcdirs_swaps_values():
    window = MainWindow()

    window.slideshow_srcdir_l = "/srcdir/left"
    window.slideshow_srcdir_r = "/srcdir/right"
    window._update_slideshow_source_display()

    ok = window.on_swap_slideshow_srcdirs()

    assert ok is True
    assert window.slideshow_srcdir_l == "/srcdir/right"
    assert window.slideshow_srcdir_r == "/srcdir/left"
    assert "L=/srcdir/right" in window.slideshow_source_display
    assert "R=/srcdir/left" in window.slideshow_source_display


def test_on_swap_slideshow_srcdirs_refreshes_start_availability():
    window = MainWindow()
    window.slideshow_srcdir_l = "/srcdir/left"
    window.slideshow_srcdir_r = "/srcdir/right"
    window._refresh_action_availability()
    assert window.can_start_slideshow is True

    window.slideshow_srcdir_l = ""
    window._refresh_action_availability()
    assert window.can_start_slideshow is False

    window.on_swap_slideshow_srcdirs()

    assert window.slideshow_srcdir_l == "/srcdir/right"
    assert window.slideshow_srcdir_r == ""
    assert window.can_start_slideshow is False


def test_on_clear_slideshow_srcdir_clears_one_side_only():
    window = MainWindow()
    window.slideshow_srcdir_l = "/srcdir/left"
    window.slideshow_srcdir_r = "/srcdir/right"

    ok = window.on_clear_slideshow_srcdir("L")

    assert ok is True
    assert window.slideshow_srcdir_l == ""
    assert window.slideshow_srcdir_r == "/srcdir/right"
    assert "L=-" in window.slideshow_source_display
    assert "R=/srcdir/right" in window.slideshow_source_display


def test_on_clear_slideshow_srcdir_disables_start_when_incomplete():
    window = MainWindow()
    window.slideshow_srcdir_l = "/srcdir/left"
    window.slideshow_srcdir_r = "/srcdir/right"
    window._refresh_action_availability()
    assert window.can_start_slideshow is True

    window.on_clear_slideshow_srcdir("R")

    assert window.can_start_slideshow is False


def test_on_clear_slideshow_srcdir_rejects_invalid_side():
    window = MainWindow()
    window.slideshow_srcdir_l = "/srcdir/left"
    window.slideshow_srcdir_r = "/srcdir/right"

    ok = window.on_clear_slideshow_srcdir("")

    assert ok is False
    assert window.last_error == "slideshow srcdir clear side is required"
    assert window.slideshow_srcdir_l == "/srcdir/left"
    assert window.slideshow_srcdir_r == "/srcdir/right"


def test_on_clear_slideshow_srcdir_does_not_stop_running_slideshow():
    window = MainWindow()
    window.slideshow_srcdir_l = "/srcdir/left"
    window.slideshow_srcdir_r = "/srcdir/right"
    window.slideshow_running = True

    window.on_clear_slideshow_srcdir("L")

    assert window.slideshow_running is True
    assert window.slideshow_srcdir_l == ""


@pytest.fixture
def qapp():
    pytest.importorskip("PyQt6")
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_qt_build_exposes_swap_and_clear_srcdir_widgets(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    objects = backend._objects
    for key in (
        "btn_swap_input_paths",
        "btn_swap_slideshow_srcdirs",
        "btn_clr_srcdir_l",
        "btn_clr_srcdir_r",
    ):
        assert key in objects, f"missing widget {key}"


def test_qt_swap_input_paths_button_invokes_handler(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.adapters.ui_adapter import connect_signal_dispatch, create_mainwindow_signal_dispatch

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window,
        tuple(RUNTIME_HANDLER_MAP.keys()),
        handler_map=RUNTIME_HANDLER_MAP,
    )
    connect_signal_dispatch(backend, dispatch)

    window.input_path_l = "left.jpg"
    window.input_path_r = "right.jpg"
    window._apply_input_paths()

    backend._objects["btn_swap_input_paths"].click()

    assert window.input_path_l == "right.jpg"
    assert window.input_path_r == "left.jpg"


def test_qt_clear_srcdir_l_invokes_handler(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.adapters.ui_adapter import connect_signal_dispatch, create_mainwindow_signal_dispatch

    window = MainWindow()
    backend = load_qt_runtime_signal_backend()
    dispatch = create_mainwindow_signal_dispatch(
        window,
        tuple(RUNTIME_HANDLER_MAP.keys()),
        handler_map=RUNTIME_HANDLER_MAP,
    )
    connect_signal_dispatch(backend, dispatch)

    window.slideshow_srcdir_l = "/srcdir/left"
    window.slideshow_srcdir_r = "/srcdir/right"

    backend._objects["btn_clr_srcdir_l"].click()

    assert window.slideshow_srcdir_l == ""
    assert window.slideshow_srcdir_r == "/srcdir/right"

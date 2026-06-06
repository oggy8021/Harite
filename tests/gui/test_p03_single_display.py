"""P-03: single-display second-slot disable and slideshow start rules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from harite.gui.dual_display_ui import (
    SECOND_SLOT_WIDGET_NAMES,
    sync_second_slot_widget_enabled,
)
from harite.gui.views.main_window import MainWindow


@pytest.fixture
def window() -> MainWindow:
    return MainWindow()


def test_dual_display_available_delegates_to_detect(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )
    w = MainWindow()
    assert w.dual_display_available is False


def test_can_start_slideshow_single_display_l_only(monkeypatch, window: MainWindow):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )
    window.slideshow_srcdir_l = str(Path("/tmp/l"))
    window.slideshow_srcdir_r = ""
    window.slideshow_interval_seconds = 60
    assert window._can_start_slideshow_now() is True


def test_can_start_slideshow_dual_requires_both(monkeypatch, window: MainWindow):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: True,
    )
    window.slideshow_srcdir_l = str(Path("/tmp/l"))
    window.slideshow_srcdir_r = ""
    window.slideshow_interval_seconds = 60
    assert window._can_start_slideshow_now() is False


def test_pick_input_blocked_for_r_when_single_display(monkeypatch, window: MainWindow):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )
    window.input_path_r = "keep"
    window.on_pick_input("new-right.jpg", "R")
    assert window.input_path_r == "keep"


def test_pick_slideshow_srcdir_blocked_for_r_when_single_display(monkeypatch, window: MainWindow):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )
    window.slideshow_srcdir_r = "keep"
    assert window.on_pick_slideshow_srcdir("/new/r", "R") is False
    assert window.slideshow_srcdir_r == "keep"


def test_select_slideshow_source_blocked_for_r_when_single_display(monkeypatch, window: MainWindow):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )
    window.slideshow_source_id_r = "keep-id"
    assert window.on_select_slideshow_source("R", "src-r") is False


def test_second_slot_handlers_blocked_when_single_display(monkeypatch, window: MainWindow):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )
    window.input_path_r = "keep"
    assert window.on_clear_input("R") is False
    assert window.input_path_r == "keep"
    assert window.on_swap_input_paths() is False
    assert window.on_swap_slideshow_srcdirs() is False
    window.on_toggle_position("tglPushLeftR", True)
    assert window.on_clear_slideshow_srcdir("R") is False


def test_resolve_slideshow_srcdirs_ignores_r_when_single_display(monkeypatch, window: MainWindow):
    monkeypatch.setattr(
        "harite.gui.views.main_window.dual_display_detected",
        lambda: False,
    )
    window.slideshow_srcdir_l = "/data/l"
    window.slideshow_srcdir_r = "/data/r"
    window.slideshow_source_id_l = ""
    window.slideshow_source_id_r = "src-r"
    window.slideshow_profile_id = ""

    def fake_catalog():
        return MagicMock()

    monkeypatch.setattr(window, "load_source_catalog", fake_catalog)
    monkeypatch.setattr(window, "_sync_remote_sources_for_slideshow_start", lambda _c: None)

    assert window._resolve_slideshow_srcdirs_for_start() is True
    assert window.slideshow_srcdir_l == "/data/l"
    assert window.slideshow_srcdir_r == ""
    assert window.slideshow_source_id_r == ""


def test_sync_second_slot_widget_enabled_calls_backend():
    backend = MagicMock()
    sync_second_slot_widget_enabled(backend, second_slot_enabled=False)
    assert backend._set_widget_slot_blocked.call_count == len(SECOND_SLOT_WIDGET_NAMES)


def test_sync_second_slot_widget_enabled_falls_back_without_slot_blocked_helper():
    backend = MagicMock(spec=[])
    backend._set_widget_enabled = MagicMock()
    sync_second_slot_widget_enabled(backend, second_slot_enabled=False)
    assert backend._set_widget_enabled.call_count == len(SECOND_SLOT_WIDGET_NAMES)

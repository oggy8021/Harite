"""Tests for the Qt Slideshow tab (Phase 5).

Covers widget existence, initial states, and structural correctness.
All Qt tests require the ``qapp`` fixture from conftest.py.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Module importability
# ---------------------------------------------------------------------------


def test_qt_tab_slideshow_importable():
    from harite.gui.adapters_qt import qt_tab_slideshow  # noqa: F401

    assert callable(qt_tab_slideshow.build_slideshow_tab)


# ---------------------------------------------------------------------------
# Widget registry helper
# ---------------------------------------------------------------------------


def _make_slideshow_tab(qapp):
    from harite.gui.adapters_qt.qt_tab_slideshow import build_slideshow_tab

    return build_slideshow_tab()


# ---------------------------------------------------------------------------
# Required widgets present
# ---------------------------------------------------------------------------


def test_slideshow_tab_required_widgets(qapp):
    w = _make_slideshow_tab(qapp)

    expected = {
        "slideshow_tab_box",
        "slideshow_label",
        "slideshow_tab_title",
        "slideshow_codh_keyword_chip_row",
        "slideshow_codh_keyword_chip",
        "slideshow_profile_row",
        "combo_slideshow_profile",
        "left_source_block",
        "right_source_block",
        "combo_slideshow_source_l",
        "combo_slideshow_source_r",
        "btn_open_srcdir_l",
        "btn_open_srcdir_r",
        "slideshow_source_label_l",
        "slideshow_source_label_r",
        "btn_manage_source_registry",
        "slideshow_manage_registry_row",
        "btn_slideshow_options_more",
        "slideshow_options_drawer",
        "slideshow_options_drawer_top_border",
        "slideshow_options_trigger_row",
        "interval_label",
        "interval_spin",
        "slideshow_mode_label",
        "slideshow_mode_help_label",
        "rad_slideshow_mode_sequential",
        "rad_slideshow_mode_random",
        "btn_daemonize",
        "btn_cancel_daemonize",
        "slideshow_current_label",
        "slideshow_output_label",
    }
    assert expected <= set(w)


# ---------------------------------------------------------------------------
# Srcdir buttons and labels
# ---------------------------------------------------------------------------


def test_srcdir_buttons_icon_only_with_tooltips(qapp):
    w = _make_slideshow_tab(qapp)

    assert w["btn_open_srcdir_l"].text() == ""
    assert w["btn_open_srcdir_r"].text() == ""
    assert w["btn_clr_srcdir_l"].text() == ""
    assert w["btn_clr_srcdir_r"].text() == ""
    assert w["btn_open_srcdir_l"].toolTip() == "Srcdir-L"
    assert w["btn_clr_srcdir_l"].toolTip() == "Clear-L"


def test_srcdir_source_labels_initial(qapp):
    w = _make_slideshow_tab(qapp)

    assert w["slideshow_source_label_l"].text() == "L: -"
    assert w["slideshow_source_label_r"].text() == "R: -"


# ---------------------------------------------------------------------------
# Interval spin
# ---------------------------------------------------------------------------


def test_interval_spin_initial_value(qapp):
    w = _make_slideshow_tab(qapp)
    assert w["interval_spin"].value() == 60


def test_interval_spin_range(qapp):
    w = _make_slideshow_tab(qapp)
    assert w["interval_spin"].minimum() == 1
    assert w["interval_spin"].maximum() == 86400


# ---------------------------------------------------------------------------
# Mode radio buttons
# ---------------------------------------------------------------------------


def test_mode_default_is_random(qapp):
    w = _make_slideshow_tab(qapp)

    assert w["rad_slideshow_mode_random"].isChecked()
    assert not w["rad_slideshow_mode_sequential"].isChecked()


def test_mode_is_mutually_exclusive(qapp):
    w = _make_slideshow_tab(qapp)

    w["rad_slideshow_mode_sequential"].setChecked(True)
    assert w["rad_slideshow_mode_sequential"].isChecked()
    assert not w["rad_slideshow_mode_random"].isChecked()


def test_mode_radio_labels(qapp):
    w = _make_slideshow_tab(qapp)

    assert w["rad_slideshow_mode_sequential"].text() == "sequential"
    assert w["rad_slideshow_mode_random"].text() == "random"


def test_mode_help_label_text(qapp):
    w = _make_slideshow_tab(qapp)
    assert "Random" in w["slideshow_mode_help_label"].text()


# ---------------------------------------------------------------------------
# Start / Stop buttons
# ---------------------------------------------------------------------------


def test_start_stop_button_labels(qapp):
    w = _make_slideshow_tab(qapp)

    assert "Start" in w["btn_daemonize"].text()
    assert "Stop" in w["btn_cancel_daemonize"].text()


# ---------------------------------------------------------------------------
# Detail labels
# ---------------------------------------------------------------------------


def test_detail_label_initial_text(qapp):
    w = _make_slideshow_tab(qapp)

    assert "idle" in w["slideshow_current_label"].text()
    assert w["slideshow_output_label"].text() == "Slideshow output: ."


# ---------------------------------------------------------------------------
# Tab title label
# ---------------------------------------------------------------------------


def test_slideshow_tab_title_initial_text(qapp):
    w = _make_slideshow_tab(qapp)
    assert w["slideshow_tab_title"].text() == "Slideshow (stopped)"


def test_options_drawer_hidden_by_default(qapp):
    w = _make_slideshow_tab(qapp)
    assert not w["slideshow_options_drawer"].isVisible()
    assert w["btn_slideshow_options_more"].text() == "More slideshow options…"


def test_options_drawer_toggle_updates_trigger_label(qapp):
    from harite.gui.views.slideshow_options_drawer import toggle_slideshow_options_drawer

    w = _make_slideshow_tab(qapp)
    backend = type("B", (), {"_objects": w})()
    toggle_slideshow_options_drawer(backend)
    assert w["btn_slideshow_options_more"].text() == "Fewer slideshow options…"
    toggle_slideshow_options_drawer(backend)
    assert w["btn_slideshow_options_more"].text() == "More slideshow options…"


def test_options_drawer_toggle_applies_p07_open_state_styles(qapp):
    from harite.gui.views.slideshow_options_drawer import (
        QT_DRAWER_OBJECT_NAME,
        QT_TRIGGER_OBJECT_NAME,
        toggle_slideshow_options_drawer,
    )

    w = _make_slideshow_tab(qapp)
    drawer = w["slideshow_options_drawer"]
    trigger = w["btn_slideshow_options_more"]
    backend = type("B", (), {"_objects": w})()

    assert drawer.objectName() == QT_DRAWER_OBJECT_NAME
    assert drawer.styleSheet() == ""

    top_border = w["slideshow_options_drawer_top_border"]

    toggle_slideshow_options_drawer(backend)
    assert getattr(backend, "_slideshow_options_drawer_expanded", False)
    assert drawer.styleSheet() == ""
    assert drawer.autoFillBackground()
    assert "background-color:" in top_border.styleSheet()
    assert drawer.objectName() == f"{QT_DRAWER_OBJECT_NAME}Expanded"
    assert trigger.objectName() == f"{QT_TRIGGER_OBJECT_NAME}Expanded"
    assert "background-color:" in trigger.styleSheet()

    toggle_slideshow_options_drawer(backend)
    assert not getattr(backend, "_slideshow_options_drawer_expanded", True)
    assert not drawer.autoFillBackground()
    assert top_border.styleSheet() == ""
    assert drawer.styleSheet() == ""
    assert drawer.objectName() == QT_DRAWER_OBJECT_NAME
    assert trigger.objectName() == QT_TRIGGER_OBJECT_NAME
    assert trigger.styleSheet() == ""


def test_profile_row_has_no_applies_lr_label(qapp):
    w = _make_slideshow_tab(qapp)
    profile_row = w["slideshow_profile_row"]
    texts = [
        profile_row.layout().itemAt(index).widget().text()
        for index in range(profile_row.layout().count())
        if profile_row.layout().itemAt(index).widget() is not None and hasattr(profile_row.layout().itemAt(index).widget(), "text")
    ]
    assert not any("Applies L/R" in text for text in texts)


# ---------------------------------------------------------------------------
# Full layout integration
# ---------------------------------------------------------------------------


def test_full_layout_slideshow_tab_integrated(qapp):
    """After full layout build, Slideshow tab widgets appear in backend registry."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    reg = backend.objects

    assert "btn_open_srcdir_l" in reg
    assert "btn_open_srcdir_r" in reg
    assert "interval_spin" in reg
    assert "btn_daemonize" in reg
    assert "btn_cancel_daemonize" in reg
    assert "rad_slideshow_mode_random" in reg
    assert "slideshow_current_label" in reg
    assert "slideshow_output_label" in reg
    assert backend.objects["command_tabs"].tabText(2) == "Slideshow (stopped)"

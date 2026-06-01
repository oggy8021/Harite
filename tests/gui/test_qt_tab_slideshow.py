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


def test_srcdir_button_labels(qapp):
    w = _make_slideshow_tab(qapp)

    assert "Srcdir-L" in w["btn_open_srcdir_l"].text()
    assert "Srcdir-R" in w["btn_open_srcdir_r"].text()


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

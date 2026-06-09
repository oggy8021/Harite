"""Tests for Qt margin widgets (P-08: cross-grid on Main + options drawer).

Covers widget existence, initial states, and structural correctness.
All Qt tests require the ``qapp`` fixture from conftest.py.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Module importability
# ---------------------------------------------------------------------------


def test_qt_tab_margins_importable():
    from harite.gui.adapters_qt import qt_tab_margins  # noqa: F401

    assert callable(qt_tab_margins.build_margins_options_drawer)
    assert callable(qt_tab_margins.build_margin_cross_grid)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_margins_drawer(qapp):
    from harite.gui.adapters_qt.qt_tab_margins import build_margins_options_drawer

    return build_margins_options_drawer()


def _make_margin_cross_grid(qapp):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_tab_margins import build_margin_cross_grid

    return build_margin_cross_grid(compose_center=QLabel("compose-stub"))


# ---------------------------------------------------------------------------
# Margin spin controls (Main tab face)
# ---------------------------------------------------------------------------


def test_margin_cross_grid_required_spin_widgets(qapp):
    w = _make_margin_cross_grid(qapp)

    expected = {
        "margin_cross_grid",
        "top_margin_spin", "top_margin_label",
        "left_margin_spin", "left_margin_label",
        "right_margin_spin", "right_margin_label",
        "bottom_margin_spin", "bottom_margin_label",
        "all_margins_spin", "all_margins_label",
    }
    assert expected <= set(w)


def test_margin_spin_initial_values(qapp):
    w = _make_margin_cross_grid(qapp)

    for key in (
        "top_margin_spin",
        "left_margin_spin",
        "right_margin_spin",
        "bottom_margin_spin",
        "all_margins_spin",
    ):
        assert w[key].value() == 0, f"{key} should start at 0"


def test_margin_spin_ranges(qapp):
    w = _make_margin_cross_grid(qapp)

    assert w["top_margin_spin"].minimum() == 0
    assert w["top_margin_spin"].maximum() == 250
    assert w["bottom_margin_spin"].maximum() == 250
    assert w["left_margin_spin"].maximum() == 500
    assert w["right_margin_spin"].maximum() == 500
    assert w["all_margins_spin"].maximum() == 250


# ---------------------------------------------------------------------------
# Embed pattern radios (drawer)
# ---------------------------------------------------------------------------


def test_embed_pattern_required_widgets(qapp):
    w = _make_margins_drawer(qapp)

    expected = {
        "margin_text_mode_label",
        "margin_text_mode_off",
        "margin_text_mode_settings",
        "margin_text_mode_text",
        "margin_text_mode_both",
    }
    assert expected <= set(w)


def test_embed_pattern_default_is_off(qapp):
    w = _make_margins_drawer(qapp)

    assert w["margin_text_mode_off"].isChecked()
    assert not w["margin_text_mode_settings"].isChecked()
    assert not w["margin_text_mode_text"].isChecked()
    assert not w["margin_text_mode_both"].isChecked()


def test_embed_pattern_modes_are_mutually_exclusive(qapp):
    w = _make_margins_drawer(qapp)

    w["margin_text_mode_settings"].setChecked(True)
    assert w["margin_text_mode_settings"].isChecked()
    assert not w["margin_text_mode_off"].isChecked()

    w["margin_text_mode_both"].setChecked(True)
    assert w["margin_text_mode_both"].isChecked()
    assert not w["margin_text_mode_settings"].isChecked()


def test_embed_pattern_label_text(qapp):
    w = _make_margins_drawer(qapp)
    assert "embed pattern" in w["margin_text_mode_label"].text()


# ---------------------------------------------------------------------------
# Margin text sub-tabs (drawer)
# ---------------------------------------------------------------------------


def test_margin_text_tabs_required_widgets(qapp):
    w = _make_margins_drawer(qapp)

    expected = {
        "margin_text_tabs",
        "margin_settings_page",
        "margin_text_page",
        "margin_settings_preview_label",
        "margin_text_section_label",
        "margin_text_entry",
    }
    assert expected <= set(w)


def test_margin_text_tabs_has_two_tabs(qapp):
    w = _make_margins_drawer(qapp)
    assert w["margin_text_tabs"].count() == 2


def test_margin_text_tabs_labels(qapp):
    w = _make_margins_drawer(qapp)
    tabs = w["margin_text_tabs"]
    assert tabs.tabText(0) == "Settings"
    assert tabs.tabText(1) == "Text"


def test_margin_settings_preview_label_initial(qapp):
    w = _make_margins_drawer(qapp)
    assert w["margin_settings_preview_label"].text() == "resolution=-"


def test_margin_text_entry_is_readonly(qapp):
    w = _make_margins_drawer(qapp)
    assert w["margin_text_entry"].isReadOnly()


# ---------------------------------------------------------------------------
# Position selector (drawer)
# ---------------------------------------------------------------------------


def test_position_selector_required_widgets(qapp):
    w = _make_margins_drawer(qapp)

    expected = {
        "margin_position_shell",
        "margin_position_left_top",
        "margin_position_left_bottom",
        "margin_position_right_top",
        "margin_position_right_bottom",
    }
    assert expected <= set(w)


def test_position_selector_default_is_right_bottom(qapp):
    w = _make_margins_drawer(qapp)

    assert w["margin_position_right_bottom"].isChecked()
    assert not w["margin_position_left_top"].isChecked()
    assert not w["margin_position_left_bottom"].isChecked()
    assert not w["margin_position_right_top"].isChecked()


def test_position_selector_is_mutually_exclusive(qapp):
    w = _make_margins_drawer(qapp)

    w["margin_position_left_top"].setChecked(True)
    assert w["margin_position_left_top"].isChecked()
    assert not w["margin_position_right_bottom"].isChecked()


# ---------------------------------------------------------------------------
# C-04 Wave a: slim surface (no summary / notes on drawer face)
# ---------------------------------------------------------------------------


def test_margins_drawer_has_no_alignment_summary_widgets(qapp):
    w = _make_margins_drawer(qapp)

    assert "current_state_title_display" not in w
    assert "current_state_summary_display" not in w
    assert "notes_box" not in w


def test_margin_text_max_lines_spin_hidden_but_wired(qapp):
    w = _make_margins_drawer(qapp)
    spin = w["margin_text_max_lines_spin"]
    assert spin.value() == 3
    assert not spin.isVisible()


def test_margins_drawer_tooltips_on_primary_controls(qapp):
    from harite.gui.views.margins_surface import (
        MARGIN_BEHAVIOR_TOOLTIP,
        MARGIN_PRIORITY_RULE_TOOLTIP,
        MARGIN_TEXT_LINE_LIMITS_TOOLTIP,
    )

    cross = _make_margin_cross_grid(qapp)
    drawer = _make_margins_drawer(qapp)

    assert MARGIN_TEXT_LINE_LIMITS_TOOLTIP in drawer["margin_text_mode_label"].toolTip()
    assert MARGIN_TEXT_LINE_LIMITS_TOOLTIP in drawer["margin_text_entry"].toolTip()
    assert MARGIN_PRIORITY_RULE_TOOLTIP in drawer["margin_position_shell"].toolTip()
    assert MARGIN_BEHAVIOR_TOOLTIP in cross["top_margin_label"].toolTip()


# ---------------------------------------------------------------------------
# Full layout integration
# ---------------------------------------------------------------------------


def test_full_layout_margin_widgets_on_main_tab(qapp):
    """After full layout build, margin widgets appear in registry on Main tab."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    reg = backend.objects

    assert "top_margin_spin" in reg
    assert "left_margin_spin" in reg
    assert "right_margin_spin" in reg
    assert "bottom_margin_spin" in reg
    assert "margin_text_mode_off" in reg
    assert "margin_text_entry" in reg
    assert "margin_position_right_bottom" in reg
    assert "btn_margins_options_more" in reg

    tabs = backend.objects["command_tabs"]
    assert tabs.count() == 2
    assert tabs.tabText(0) == "Main"
    assert "Margins (for each display)" not in [tabs.tabText(i) for i in range(tabs.count())]

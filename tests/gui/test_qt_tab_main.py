"""Tests for the Qt Main tab (Phase 3).

Covers widget existence, initial states, and structural correctness.
All Qt tests require the ``qapp`` fixture from conftest.py.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Module importability
# ---------------------------------------------------------------------------


def test_qt_tab_main_importable():
    from harite.gui.adapters_qt import qt_tab_main  # noqa: F401

    assert callable(qt_tab_main.build_main_tab)
    assert callable(qt_tab_main.build_compose_grid_section)
    assert callable(qt_tab_main.build_action_cluster_section)


# ---------------------------------------------------------------------------
# Compose grid
# ---------------------------------------------------------------------------


def test_compose_grid_required_widgets(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_compose_grid_section

    w = build_compose_grid_section()

    expected = {
        "compose_grid",
        "left_panel", "center_panel", "right_panel",
        "tgl_upper_l", "tgl_lower_l", "tgl_push_left_l", "tgl_push_right_l",
        "btn_get_img_l",
        "tgl_upper_r", "tgl_lower_r", "tgl_push_left_r", "tgl_push_right_r",
        "btn_get_img_r",
        "input_display_l", "btn_clr_path_l",
        "input_display_r", "btn_clr_path_r",
        "pick_state_label",
    }
    assert expected <= set(w)


def test_direction_toggle_buttons_are_checkable(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_compose_grid_section

    w = build_compose_grid_section()

    toggle_names = [
        "tgl_upper_l", "tgl_lower_l", "tgl_push_left_l", "tgl_push_right_l",
        "tgl_upper_r", "tgl_lower_r", "tgl_push_left_r", "tgl_push_right_r",
    ]
    for name in toggle_names:
        assert w[name].isCheckable(), f"{name} should be checkable"


def test_direction_toggle_buttons_initial_state_unchecked(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_compose_grid_section

    w = build_compose_grid_section()

    toggle_names = [
        "tgl_upper_l", "tgl_lower_l", "tgl_push_left_l", "tgl_push_right_l",
        "tgl_upper_r", "tgl_lower_r", "tgl_push_left_r", "tgl_push_right_r",
    ]
    for name in toggle_names:
        assert not w[name].isChecked(), f"{name} should be unchecked initially"


def test_open_buttons_not_checkable(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_compose_grid_section

    w = build_compose_grid_section()
    assert not w["btn_get_img_l"].isCheckable()
    assert not w["btn_get_img_r"].isCheckable()


def test_compose_icon_only_buttons_use_tooltips(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_compose_grid_section

    w = build_compose_grid_section()
    assert w["btn_get_img_l"].text() == ""
    assert w["btn_get_img_r"].text() == ""
    assert w["btn_clr_path_l"].text() == ""
    assert w["btn_clr_path_r"].text() == ""
    assert w["btn_get_img_l"].toolTip() == "Open-L"
    assert w["btn_clr_path_l"].toolTip() == "Clear-L"
    assert w["tgl_upper_l"].toolTip() == "Top alignment-L"
    assert w["btn_swap_input_paths"].toolTip() == "Swap L/R"


def test_path_display_is_readonly(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_compose_grid_section

    w = build_compose_grid_section()
    assert w["input_display_l"].isReadOnly()
    assert w["input_display_r"].isReadOnly()


# ---------------------------------------------------------------------------
# Action cluster
# ---------------------------------------------------------------------------


def test_action_cluster_required_widgets(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")

    expected = {
        "action_cluster_row",
        "preview_group", "optimize_group", "apply_group",
        "optimize_modern_btn",
        "apply_btn",
        "rad_apply_single", "rad_apply_per_monitor",
        "preview_left", "preview_right",
    }
    assert expected <= set(w)


def test_optimize_button_disabled_by_default(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    assert not w["optimize_modern_btn"].isEnabled()


def test_apply_button_disabled_by_default(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    assert not w["apply_btn"].isEnabled()


def test_apply_mode_single_file_default(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    assert w["rad_apply_single"].isChecked()
    assert not w["rad_apply_per_monitor"].isChecked()


def test_apply_mode_per_monitor_default(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("per-monitor-auto-split")
    assert w["rad_apply_per_monitor"].isChecked()
    assert not w["rad_apply_single"].isChecked()


def test_apply_mode_radios_are_mutually_exclusive(qapp):
    """Selecting one radio should deselect the other."""
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    assert w["rad_apply_single"].isChecked()

    w["rad_apply_per_monitor"].setChecked(True)
    assert w["rad_apply_per_monitor"].isChecked()
    assert not w["rad_apply_single"].isChecked()


def test_preview_boxes_fixed_size(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    assert w["preview_left"].width() == 160
    assert w["preview_left"].height() == 90
    assert w["preview_right"].width() == 160
    assert w["preview_right"].height() == 90


def test_preview_thumbnails_idle_without_overlay_text(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    assert w["preview_left"].text() == ""
    assert w["preview_right"].text() == ""
    assert w["preview_left"].pixmap() is None or w["preview_left"].pixmap().isNull()


def test_action_cluster_groups_top_aligned(qapp):
    """Action cluster columns align at top across Preview / Optimize / Apply."""
    from PyQt6.QtCore import Qt
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    layout = w["action_cluster_row"].layout()
    for key in ("preview_group", "optimize_group", "apply_group"):
        item = layout.itemAt(layout.indexOf(w[key]))
        assert item.alignment() & Qt.AlignmentFlag.AlignTop


def test_optimize_group_contains_button_only(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    group_layout = w["optimize_group"].layout()
    assert group_layout.count() == 1
    assert group_layout.itemAt(0).widget() is w["optimize_modern_btn"]


def test_apply_group_button_then_mode_radios(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    group_layout = w["apply_group"].layout()
    btn_row = w["apply_btn"].parentWidget()
    mode_row = w["rad_apply_single"].parentWidget()
    btn_index = group_layout.indexOf(btn_row)
    mode_row_index = group_layout.indexOf(mode_row)
    assert btn_index >= 0 and mode_row_index > btn_index


def test_apply_button_uses_natural_width(qapp):
    from PyQt6.QtWidgets import QSizePolicy
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    assert w["apply_btn"].sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Minimum
    assert w["apply_group"].sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Minimum


def test_apply_mode_radios_have_tooltips(qapp):
    from harite.apply_surface import apply_mode_help_text
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    expected = apply_mode_help_text("single-file")
    assert w["rad_apply_single"].toolTip() == expected
    assert w["rad_apply_per_monitor"].toolTip() == expected
    assert w["apply_btn"].toolTip() == expected


# ---------------------------------------------------------------------------
# Full Main tab assembly
# ---------------------------------------------------------------------------


def test_build_main_tab_includes_compose_and_action_widgets(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab

    w = build_main_tab()

    compose_keys = {"compose_grid", "tgl_upper_l", "btn_get_img_l", "input_display_l"}
    action_keys = {"optimize_modern_btn", "apply_btn", "rad_apply_single"}
    state_keys = {"do_it_plan_label", "save_path_state_label", "save_target_label"}

    assert compose_keys <= set(w)
    assert action_keys <= set(w)
    assert state_keys <= set(w)
    assert w["main_col"] is not None


def test_full_layout_main_tab_integrated(qapp):
    """After full layout build, command_tabs[0] widget contains the Main tab."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    reg = backend.objects

    # Main tab widgets should be in the top-level registry
    assert "tgl_upper_l" in reg
    assert "tgl_upper_r" in reg
    assert "optimize_modern_btn" in reg
    assert "apply_btn" in reg
    assert "preview_left" in reg

    # First tab should be the Main tab
    assert backend.objects["command_tabs"].tabText(0) == "Main"


def test_apply_mode_span_label_on_windows(qapp, monkeypatch):
    monkeypatch.setattr("harite.apply_surface.platform.system", lambda: "Windows")
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("per-monitor-auto-split")
    assert w["rad_apply_per_monitor"].text() == "Span"
    assert w["rad_apply_single"].text() == "No Split"

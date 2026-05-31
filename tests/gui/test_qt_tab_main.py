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


def test_open_button_labels(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_compose_grid_section

    w = build_compose_grid_section()
    assert w["btn_get_img_l"].text() == "Open-L"
    assert w["btn_get_img_r"].text() == "Open-R"


def test_clear_button_labels(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_compose_grid_section

    w = build_compose_grid_section()
    assert w["btn_clr_path_l"].text() == "Clear-L"
    assert w["btn_clr_path_r"].text() == "Clear-R"


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
        "optimize_modern_btn", "optimize_result",
        "apply_btn", "apply_target",
        "rad_apply_single", "rad_apply_per_monitor",
        "apply_mode_label",
        "preview_left", "preview_right",
        "preview_left_assignment", "preview_right_assignment",
        "preview_left_result", "preview_right_result",
        "preview_state_label", "preview_source_label", "preview_assist_label",
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


def test_preview_default_labels(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    assert "L display" in w["preview_left_assignment"].text()
    assert "R display" in w["preview_right_assignment"].text()
    assert w["preview_state_label"].text() == "Preview: not-ready"


def test_action_cluster_groups_top_aligned(qapp):
    """Action cluster columns align at top so Optimize/Apply section labels line up."""
    from PyQt6.QtCore import Qt
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    layout = w["action_cluster_row"].layout()
    for key in ("preview_group", "optimize_group", "apply_group"):
        item = layout.itemAt(layout.indexOf(w[key]))
        assert item.alignment() & Qt.AlignmentFlag.AlignTop


def test_optimize_result_below_button(qapp):
    """Optimize result label sits below the button, not beside it (Qt / issue-342)."""
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    group_layout = w["optimize_group"].layout()
    btn_row_index = group_layout.indexOf(w["optimize_modern_btn"].parentWidget())
    result_index = group_layout.indexOf(w["optimize_result"])
    assert btn_row_index >= 0 and result_index > btn_row_index
    assert w["optimize_result"].parentWidget() is w["optimize_group"]


def test_apply_target_below_button(qapp):
    """Apply target label sits below the button; mode rows follow (Qt / issue-342)."""
    from harite.gui.adapters_qt.qt_tab_main import build_action_cluster_section

    w = build_action_cluster_section("single-file")
    group_layout = w["apply_group"].layout()
    btn_row_index = group_layout.indexOf(w["apply_btn"].parentWidget())
    target_index = group_layout.indexOf(w["apply_target"])
    mode_row_index = group_layout.indexOf(w["rad_apply_single"].parentWidget())
    assert btn_row_index >= 0 and target_index > btn_row_index and mode_row_index > target_index
    assert w["apply_target"].parentWidget() is w["apply_group"]


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

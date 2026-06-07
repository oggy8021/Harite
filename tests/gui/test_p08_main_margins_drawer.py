"""P-08: Main + Margins Drawer (gui-spec §3).

Spec-driven tests for the 2-tab notebook and Main-tab margin cross-grid +
options drawer. Expect failures until Qt/GTK implementation lands.
"""

from __future__ import annotations

import pytest

MORE_MARGIN_LABEL = "More margin options…"
FEWER_MARGIN_LABEL = "Fewer margin options…"


def _load_backend(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    return load_qt_runtime_signal_backend()


# ---------------------------------------------------------------------------
# Notebook (P8-1)
# ---------------------------------------------------------------------------


def test_command_tabs_has_two_pages(qapp):
    backend = _load_backend(qapp)
    tabs = backend.objects["command_tabs"]
    assert tabs.count() == 2


def test_command_tabs_labels_are_main_and_slideshow(qapp):
    backend = _load_backend(qapp)
    tabs = backend.objects["command_tabs"]
    assert tabs.tabText(0) == "Main"
    assert tabs.tabText(1).startswith("Slideshow")


def test_no_margins_notebook_tab(qapp):
    backend = _load_backend(qapp)
    tabs = backend.objects["command_tabs"]
    labels = [tabs.tabText(i) for i in range(tabs.count())]
    assert "Margins (for each display)" not in labels


# ---------------------------------------------------------------------------
# Registry — logical widget names preserved (planning §5)
# ---------------------------------------------------------------------------


def test_margin_widgets_remain_in_registry(qapp):
    backend = _load_backend(qapp)
    reg = backend.objects

    spin_keys = {
        "top_margin_spin",
        "left_margin_spin",
        "right_margin_spin",
        "bottom_margin_spin",
    }
    drawer_keys = {
        "margin_text_mode_off",
        "margin_text_entry",
        "margin_position_right_bottom",
    }
    assert spin_keys <= set(reg)
    assert drawer_keys <= set(reg)


# ---------------------------------------------------------------------------
# Main tab structure (P8-2, P8-3, P8-4)
# ---------------------------------------------------------------------------


def test_build_main_tab_includes_margin_cross_grid_and_drawer(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab

    w = build_main_tab()

    margin_face = {
        "margin_cross_grid",
        "top_margin_spin",
        "left_margin_spin",
        "right_margin_spin",
        "bottom_margin_spin",
    }
    drawer_shell = {
        "margins_options_trigger_row",
        "btn_margins_options_more",
        "margins_options_drawer",
        "margins_options_drawer_top_border",
    }
    assert margin_face <= set(w)
    assert drawer_shell <= set(w)


def test_margin_spins_visible_on_main_face(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab

    w = build_main_tab()
    for key in ("top_margin_spin", "left_margin_spin", "right_margin_spin", "bottom_margin_spin"):
        assert not w[key].isHidden(), f"{key} should be on the Main tab face"


def test_embed_and_position_widgets_live_in_drawer(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab

    w = build_main_tab()
    drawer = w["margins_options_drawer"]

    for key in (
        "margin_text_mode_off",
        "margin_text_tabs",
        "margin_position_shell",
    ):
        assert w[key].parent() is drawer or drawer.isAncestorOf(w[key])


def test_margins_drawer_hidden_by_default(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab

    w = build_main_tab()
    assert not w["margins_options_drawer"].isVisible()
    assert w["btn_margins_options_more"].text() == MORE_MARGIN_LABEL


def test_margins_drawer_trigger_centered_below_action_cluster(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab

    w = build_main_tab()
    main_layout = w["main_col"].layout()
    action_index = main_layout.indexOf(w["action_cluster_row"])
    trigger_index = main_layout.indexOf(w["margins_options_trigger_row"])
    drawer_index = main_layout.indexOf(w["margins_options_drawer"])
    assert action_index >= 0
    assert trigger_index > action_index
    assert drawer_index > trigger_index


def test_margin_cross_grid_wraps_compose_grid(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab

    w = build_main_tab()
    cross_grid = w["margin_cross_grid"]
    compose_grid = w["compose_grid"]
    assert cross_grid.isAncestorOf(compose_grid)


# ---------------------------------------------------------------------------
# Drawer toggle (P8-5 — P-07 parity)
# ---------------------------------------------------------------------------


def test_margins_drawer_toggle_updates_trigger_label(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab
    from harite.gui.views.margins_options_drawer import toggle_margins_options_drawer

    w = build_main_tab()
    backend = type("B", (), {"_objects": w})()
    toggle_margins_options_drawer(backend)
    assert w["btn_margins_options_more"].text() == FEWER_MARGIN_LABEL
    toggle_margins_options_drawer(backend)
    assert w["btn_margins_options_more"].text() == MORE_MARGIN_LABEL


def test_margins_drawer_toggle_applies_p07_open_state_styles(qapp):
    from harite.gui.adapters_qt.qt_tab_main import build_main_tab
    from harite.gui.views.margins_options_drawer import (
        QT_DRAWER_OBJECT_NAME,
        QT_TRIGGER_OBJECT_NAME,
        toggle_margins_options_drawer,
    )

    w = build_main_tab()
    drawer = w["margins_options_drawer"]
    trigger = w["btn_margins_options_more"]
    top_border = w["margins_options_drawer_top_border"]
    backend = type("B", (), {"_objects": w})()

    assert drawer.objectName() == QT_DRAWER_OBJECT_NAME
    assert drawer.styleSheet() == ""

    toggle_margins_options_drawer(backend)
    assert getattr(backend, "_margins_options_drawer_expanded", False)
    assert drawer.styleSheet() == ""
    assert drawer.autoFillBackground()
    assert "background-color:" in top_border.styleSheet()
    assert drawer.objectName() == f"{QT_DRAWER_OBJECT_NAME}Expanded"
    assert trigger.objectName() == f"{QT_TRIGGER_OBJECT_NAME}Expanded"

    toggle_margins_options_drawer(backend)
    assert not getattr(backend, "_margins_options_drawer_expanded", True)
    assert not drawer.autoFillBackground()
    assert top_border.styleSheet() == ""
    assert drawer.objectName() == QT_DRAWER_OBJECT_NAME
    assert trigger.objectName() == QT_TRIGGER_OBJECT_NAME


# ---------------------------------------------------------------------------
# Center body builder (layout-level)
# ---------------------------------------------------------------------------


def test_center_body_builds_two_tabs_without_margins_page(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import build_center_body_section

    w = build_center_body_section()
    tabs = w["command_tabs"]
    assert tabs.count() == 2
    assert tabs.tabText(0) == "Main"
    assert tabs.tabText(1).startswith("Slideshow")
    assert "margins_tab_box" not in w

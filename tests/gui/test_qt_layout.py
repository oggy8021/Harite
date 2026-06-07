"""Tests for the Qt backend layout skeleton (Phase 2).

All tests that need a live QApplication are guarded by
``pytest.importorskip("PyQt6.QtWidgets")`` so they skip gracefully in
environments without PyQt6.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Module importability
# ---------------------------------------------------------------------------


def test_qt_layout_builders_importable():
    from harite.gui.adapters_qt import qt_layout_builders  # noqa: F401

    assert callable(qt_layout_builders.build_main_layout)
    assert callable(qt_layout_builders.build_header_section)
    assert callable(qt_layout_builders.build_center_body_section)
    assert callable(qt_layout_builders.build_footer_section)


# ---------------------------------------------------------------------------
# Header section
# ---------------------------------------------------------------------------


def test_header_section_returns_required_widgets(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import build_header_section

    widgets = build_header_section()

    required = {
        "header_widget",
        "title",
        "btn_set_color",
        "btn_setting",
        "btn_about",
        "flow_legend_label",
        "optimize_btn",
    }
    assert required <= set(widgets)


def test_header_command_bar_button_labels(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import build_header_section

    w = build_header_section()
    assert w["btn_set_color"].text() == "Color"
    assert w["btn_setting"].text() == "Settings"
    assert w["btn_about"].text() == "About"


def test_header_flow_legend_text(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import build_header_section
    from harite.gui.views.flow_legend_surface import format_flow_legend_markup

    w = build_header_section()
    assert w["flow_legend_label"].text() == format_flow_legend_markup(active_step="compose")


def test_header_export_image_button_disabled_by_default(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import build_header_section

    w = build_header_section()
    assert not w["optimize_btn"].isEnabled()


# ---------------------------------------------------------------------------
# Center body (tabs)
# ---------------------------------------------------------------------------


def test_center_body_has_three_tabs(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import build_center_body_section

    w = build_center_body_section()
    tabs = w["command_tabs"]
    assert tabs.count() == 3


def test_center_body_tab_labels(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import (
        _TAB_MAIN,
        _TAB_MARGINS,
        _TAB_SLIDESHOW,
        build_center_body_section,
    )

    w = build_center_body_section()
    tabs = w["command_tabs"]
    assert tabs.tabText(0) == _TAB_MAIN
    assert tabs.tabText(1) == _TAB_MARGINS
    assert tabs.tabText(2) == _TAB_SLIDESHOW


def test_center_body_tab_labels_match_spec(qapp):
    """Tab labels must match the spec-defined values exactly."""
    from harite.gui.adapters_qt.qt_layout_builders import build_center_body_section

    w = build_center_body_section()
    tabs = w["command_tabs"]
    assert tabs.tabText(0) == "Main"
    assert tabs.tabText(1) == "Margins (for each display)"
    assert tabs.tabText(2) == "Slideshow (stopped)"


# ---------------------------------------------------------------------------
# Footer section
# ---------------------------------------------------------------------------


def test_footer_section_returns_required_widgets(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import build_footer_section

    widgets = build_footer_section()

    required = {
        "footer_widget",
        "status_label",
        "slideshow_summary_label",
        "error_label",
        "message_separator",
    }
    assert required <= set(widgets)


def test_footer_default_label_texts(qapp):
    from harite.gui.adapters_qt.qt_layout_builders import build_footer_section

    w = build_footer_section()
    assert w["status_label"].text() == "Status: ready"
    assert w["slideshow_summary_label"].text() == "Slideshow: stopped"
    assert w["error_label"].text() == "Error: none"


def test_footer_error_label_is_selectable_and_wraps(qapp):
    from PyQt6.QtCore import Qt

    from harite.gui.adapters_qt.qt_layout_builders import build_footer_section

    widgets = build_footer_section()
    error_label = widgets["error_label"]
    assert widgets["footer_widget"] is not None
    assert error_label.wordWrap() is True
    assert error_label.textInteractionFlags() == Qt.TextInteractionFlag.TextSelectableByMouse


# ---------------------------------------------------------------------------
# Full layout assembly (build_main_layout)
# ---------------------------------------------------------------------------


def test_build_main_layout_populates_central_widget(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    assert backend.qwindow.centralWidget() is not None


def test_build_main_layout_registry_contains_key_widgets(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    reg = backend.objects

    expected_keys = {
        "main_window",
        "command_tabs",
        "btn_set_color",
        "btn_setting",
        "btn_about",
        "optimize_btn",
        "status_label",
        "slideshow_summary_label",
        "error_label",
    }
    assert expected_keys <= set(reg)


def test_build_main_layout_command_tabs_has_three_tabs(qapp):
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    tabs = backend.objects["command_tabs"]
    assert tabs.count() == 3

"""Tests for shared Margins tab surface helpers (C-04 Wave a)."""

from __future__ import annotations


def test_margins_surface_tooltips_non_empty():
    from harite.gui.views import margins_surface as ms

    assert "margin text mode" in ms.MARGIN_TEXT_LINE_LIMITS_TOOLTIP.lower()
    assert "margins define area" in ms.MARGIN_PRIORITY_RULE_TOOLTIP.lower()
    assert "global" in ms.MARGIN_BEHAVIOR_TOOLTIP.lower()
    assert ms.MARGIN_CROSS_GRID_TOOLTIP.count("\n") == 2


def test_apply_widget_tooltip_qt_label(qapp):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.views.margins_surface import apply_widget_tooltip

    label = QLabel("x")
    apply_widget_tooltip(label, "hint text")
    assert label.toolTip() == "hint text"

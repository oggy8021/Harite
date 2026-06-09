"""Tests for shared Margins tab surface helpers (C-04 Wave a)."""

from __future__ import annotations


def test_margins_surface_tooltips_non_empty():
    from harite.gui.views import margins_surface as ms

    assert "margin text mode" in ms.MARGIN_TEXT_LINE_LIMITS_TOOLTIP.lower()
    assert "full display slot" in ms.MARGIN_PRIORITY_RULE_TOOLTIP.lower()
    assert "global" in ms.MARGIN_BEHAVIOR_TOOLTIP.lower()
    assert ms.MARGIN_CROSS_GRID_TOOLTIP.count("\n") == 2
    assert "same value" in ms.MARGIN_ALL_TOOLTIP.lower()


def test_margins_are_uniform():
    from harite.gui.views.margins_surface import margins_are_uniform

    assert margins_are_uniform((8, 8, 8, 8)) is True
    assert margins_are_uniform((8, 8, 8, 9)) is False
    assert margins_are_uniform((0, 0, 0, 0)) is True


def test_refresh_all_margins_bulk_controls_uniform(qapp):
    from harite.gui.adapters_qt.qt_tab_margins import build_margin_cross_grid
    from harite.gui.views.margins_surface import refresh_all_margins_bulk_controls
    from PyQt6.QtWidgets import QLabel

    widgets = build_margin_cross_grid(compose_center=QLabel("compose"))
    objects = {
        "lblAllMargins": widgets["all_margins_label"],
        "spnAllMargins": widgets["all_margins_spin"],
    }

    class _Backend:
        def _set_widget_enabled(self, name: str, enabled: bool) -> None:
            objects[name].setEnabled(enabled)

        def _set_spin_value(self, name: str, value: int) -> None:
            objects[name].setValue(value)

    refresh_all_margins_bulk_controls(_Backend(), (12, 12, 12, 12))

    assert widgets["all_margins_label"].isEnabled() is True
    assert widgets["all_margins_spin"].value() == 12


def test_refresh_all_margins_bulk_controls_mismatch_disables_label_only(qapp):
    from harite.gui.adapters_qt.qt_tab_margins import build_margin_cross_grid
    from harite.gui.views.margins_surface import refresh_all_margins_bulk_controls
    from PyQt6.QtWidgets import QLabel

    widgets = build_margin_cross_grid(compose_center=QLabel("compose"))
    widgets["all_margins_spin"].setValue(15)
    objects = {
        "lblAllMargins": widgets["all_margins_label"],
        "spnAllMargins": widgets["all_margins_spin"],
    }

    class _Backend:
        def _set_widget_enabled(self, name: str, enabled: bool) -> None:
            objects[name].setEnabled(enabled)

        def _set_spin_value(self, name: str, value: int) -> None:
            objects[name].setValue(value)

    refresh_all_margins_bulk_controls(_Backend(), (10, 20, 10, 10))

    assert widgets["all_margins_label"].isEnabled() is False
    assert widgets["all_margins_spin"].value() == 15


def test_apply_widget_tooltip_qt_label(qapp):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.views.margins_surface import apply_widget_tooltip

    label = QLabel("x")
    apply_widget_tooltip(label, "hint text")
    assert label.toolTip() == "hint text"

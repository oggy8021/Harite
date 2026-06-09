"""Margins tab surface helpers (C-04 Wave a)."""

from __future__ import annotations

from typing import Any

MARGIN_TEXT_LINE_LIMITS_TOOLTIP = (
    "Line limits are chosen automatically for the selected margin text mode."
)
MARGIN_PRIORITY_RULE_TEXT = (
    "Rule: margins constrain image size; align/valign use the full display slot."
)
MARGIN_PRIORITY_RULE_TOOLTIP = MARGIN_PRIORITY_RULE_TEXT
MARGIN_BEHAVIOR_TOOLTIP = "Current behavior: margins are global to the composite canvas."
MARGIN_CROSS_GRID_TOOLTIP = (
    f"{MARGIN_TEXT_LINE_LIMITS_TOOLTIP}\n{MARGIN_PRIORITY_RULE_TOOLTIP}\n{MARGIN_BEHAVIOR_TOOLTIP}"
)
MARGIN_ALL_TOOLTIP = (
    "Set left, right, top, and bottom margins to the same value. "
    "0 restores the default margins."
)


def margins_are_uniform(margins: tuple[int, int, int, int]) -> bool:
    left, right, top, bottom = margins
    return left == right == top == bottom


def refresh_all_margins_bulk_controls(backend: Any, margins: tuple[int, int, int, int]) -> None:
    """Sync all-margins spin/label with edge uniformity (MAT-09)."""
    if margins_are_uniform(margins):
        backend._set_widget_enabled("lblAllMargins", True)
        backend._set_spin_value("spnAllMargins", margins[0])
        return
    backend._set_widget_enabled("lblAllMargins", False)


def apply_widget_tooltip(widget: Any, text: str) -> None:
    if widget is None or not text.strip():
        return
    if hasattr(widget, "setToolTip"):
        widget.setToolTip(text)
        return
    if hasattr(widget, "set_tooltip_text"):
        widget.set_tooltip_text(text)

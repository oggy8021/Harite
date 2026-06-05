"""Margins tab surface helpers (C-04 Wave a)."""

from __future__ import annotations

from typing import Any

MARGIN_TEXT_LINE_LIMITS_TOOLTIP = (
    "Line limits are chosen automatically for the selected margin text mode."
)
MARGIN_PRIORITY_RULE_TOOLTIP = "Rule: margins define area; align/valign act inside it."
MARGIN_BEHAVIOR_TOOLTIP = "Current behavior: margins are global to the composite canvas."
MARGIN_CROSS_GRID_TOOLTIP = (
    f"{MARGIN_TEXT_LINE_LIMITS_TOOLTIP}\n{MARGIN_PRIORITY_RULE_TOOLTIP}\n{MARGIN_BEHAVIOR_TOOLTIP}"
)


def apply_widget_tooltip(widget: Any, text: str) -> None:
    if widget is None or not text.strip():
        return
    if hasattr(widget, "setToolTip"):
        widget.setToolTip(text)
        return
    if hasattr(widget, "set_tooltip_text"):
        widget.set_tooltip_text(text)

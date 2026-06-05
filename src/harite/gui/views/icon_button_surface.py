"""Icon-primary button surface helpers (C-04 Wave c)."""

from __future__ import annotations

from typing import Any

from harite.gui.views.margins_surface import apply_widget_tooltip


def apply_icon_only_button(widget: Any, tooltip: str) -> None:
    """Hide redundant on-face label text; carry meaning via tooltip."""
    if widget is None:
        return
    if hasattr(widget, "setText"):
        widget.setText("")
    elif hasattr(widget, "set_label"):
        widget.set_label("")
    apply_widget_tooltip(widget, tooltip)

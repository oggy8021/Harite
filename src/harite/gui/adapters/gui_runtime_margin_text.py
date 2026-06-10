from __future__ import annotations

from typing import Any


def sanitize_margin_text(value: str, *, max_lines: int = 5) -> str:
    return "\n".join(str(value or "").split("\n")[:max_lines])


def read_margin_text_widget_text(widget: Any) -> str:
    if hasattr(widget, "toPlainText"):
        return str(widget.toPlainText() or "")
    if hasattr(widget, "get_text"):
        return str(widget.get_text() or "")
    if hasattr(widget, "get_buffer"):
        buffer = widget.get_buffer()
        if buffer is not None and hasattr(buffer, "get_bounds") and hasattr(buffer, "get_text"):
            start, end = buffer.get_bounds()
            return str(buffer.get_text(start, end, True) or "")
    return ""


def should_block_margin_text_return(
    *,
    keyval: object,
    return_keys: set[object],
    current_text: str,
    max_lines: int = 5,
) -> bool:
    if keyval is None:
        return False
    if keyval not in return_keys:
        return False
    return len(str(current_text or "").split("\n")) >= max_lines
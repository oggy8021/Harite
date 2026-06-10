"""Path abbreviation helpers for GUI labels (Qt; was gui_runtime_file_dialog_flow)."""

from __future__ import annotations

from pathlib import Path


def format_input_display(path: str) -> str:
    value = str(path or "").strip()
    if not value:
        return ""
    name = Path(value).name or value

    max_length = 36
    if len(name) <= max_length:
        return name

    tail_length = 12
    head_length = max_length - tail_length - 3
    if head_length < 8:
        head_length = 8
        tail_length = max(4, max_length - head_length - 3)
    return f"{name[:head_length]}...{name[-tail_length:]}"


def format_slideshow_path_display(path: str) -> str:
    """Abbreviate a slideshow current path for on-screen display."""
    value = str(path or "").strip()
    if not value or value == "-":
        return value or "-"
    return format_input_display(value)

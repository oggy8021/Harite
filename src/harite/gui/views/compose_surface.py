"""Compose grid surface helpers."""

from __future__ import annotations


def direction_alignment_tooltip(direction: str, side: str) -> str:
    """Tooltip for a direction toggle on display *side* (l/r)."""
    return f"{direction} alignment-{side.upper()}"

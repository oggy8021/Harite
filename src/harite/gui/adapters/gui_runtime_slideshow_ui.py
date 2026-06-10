"""Slideshow interval commit helper (Qt backend)."""

from __future__ import annotations

from typing import Any


def commit_slideshow_interval_from_spin(backend: Any) -> int:
    """Apply the Interval spin value to owner state (may not have fired value-changed yet)."""
    interval_seconds = 0
    reader = getattr(backend, "_read_spin_int", None)
    if callable(reader):
        try:
            interval_seconds = int(reader("spnInterval"))
        except (TypeError, ValueError):
            interval_seconds = 0
    else:
        interval_widget = backend._objects.get("spnInterval")
        if interval_widget is not None and hasattr(interval_widget, "get_value_as_int"):
            interval_seconds = int(interval_widget.get_value_as_int())

    if interval_seconds > 0:
        callback = backend._signal_handlers.get("on_slideshow_interval_change")
        if callback is not None:
            try:
                callback(interval_seconds)
            except (TypeError, ValueError):
                pass
    return interval_seconds

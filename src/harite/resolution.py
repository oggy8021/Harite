"""Resolution string parsing shared by CLI and optimize paths."""

from __future__ import annotations


def parse_resolution(value: str) -> tuple[int, int]:
    """Parse resolution strings like '1920x1080'."""
    try:
        w_str, h_str = value.lower().split("x")
        w, h = int(w_str), int(h_str)
        if w <= 0 or h <= 0:
            raise ValueError("resolution must be positive")
        return w, h
    except Exception:
        raise ValueError("Invalid resolution format. Use WIDTHxHEIGHT, e.g. 3840x2160")

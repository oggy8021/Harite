"""Local timezone timestamps for cache metadata and diagnostics (MAT-16)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

_JST = timezone(timedelta(hours=9), name="JST")


def local_now_iso() -> str:
    """ISO8601 timestamp in the host local timezone (offset included)."""
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def jst_now_iso() -> str:
    """ISO8601 timestamp in JST (+09:00), for slideshow op log (MAT-08)."""
    return datetime.now(_JST).replace(microsecond=0).isoformat()

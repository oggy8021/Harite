"""Developer operation log for preset remote slideshow sync (MAT-08)."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_JST = timezone(timedelta(hours=9), name="JST")
_LOGGER = logging.getLogger("harite.slideshow.remote")


def _jst_now() -> str:
    return datetime.now(_JST).replace(microsecond=0).isoformat()


def _slideshow_op_log_target() -> str | None:
    raw = os.environ.get("HARITE_SLIDESHOW_OP_LOG", "").strip()
    if not raw:
        return None
    lowered = raw.lower()
    if lowered in {"1", "true", "yes", "stderr"}:
        return "stderr"
    return raw


def log_slideshow_op(step: str, *, ok: bool | None = None, **fields: Any) -> None:
    """Emit one JSONL record when ``HARITE_SLIDESHOW_OP_LOG`` is set."""
    target = _slideshow_op_log_target()
    if target is None:
        return

    record: dict[str, Any] = {"ts_jst": _jst_now(), "step": step}
    if ok is not None:
        record["ok"] = ok
    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        record[key] = value

    line = json.dumps(record, ensure_ascii=False)
    _LOGGER.info(line)
    if target != "stderr":
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

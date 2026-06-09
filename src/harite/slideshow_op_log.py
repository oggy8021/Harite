"""Developer operation log for preset remote slideshow sync (MAT-08)."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from harite.local_time import jst_now_iso

_LOGGER = logging.getLogger("harite.slideshow.remote")


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

    record: dict[str, Any] = {"ts_jst": jst_now_iso(), "step": step}
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

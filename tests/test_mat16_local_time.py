"""MAT-16: cache metadata timestamps use host local timezone."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from harite.local_time import jst_now_iso, local_now_iso
from harite.sources_remote_codh import save_codh_cycle
from harite.sources_remote_jma import save_jma_cycle


def test_local_now_iso_includes_utc_offset() -> None:
    stamp = local_now_iso()
    parsed = datetime.fromisoformat(stamp)
    assert parsed.tzinfo is not None
    assert parsed.microsecond == 0


def test_jst_now_iso_uses_fixed_offset() -> None:
    assert jst_now_iso().endswith("+09:00")


def test_save_jma_cycle_writes_local_updated_at(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fixed = datetime(2026, 5, 31, 15, 30, tzinfo=timezone(timedelta(hours=9)))
    monkeypatch.setattr("harite.sources_remote_jma.local_now_iso", lambda: fixed.isoformat())

    save_jma_cycle(tmp_path, preset_id="jma-near-color", filename="fresh_JRcolor.png")

    import json

    payload = json.loads((tmp_path / "jma-cycle.json").read_text(encoding="utf-8"))
    assert payload["updated_at"] == "2026-05-31T15:30:00+09:00"


def test_save_codh_cycle_writes_local_updated_at(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fixed = datetime(2026, 5, 31, 8, 0, tzinfo=timezone(timedelta(hours=-4)))
    monkeypatch.setattr("harite.sources_remote_codh.local_now_iso", lambda: fixed.isoformat())

    save_codh_cycle(
        tmp_path,
        {
            "query_key": "canvas|where:江戸",
            "mode": "sequential",
            "index": 0,
            "previous_image_url": "",
        },
    )

    import json

    payload = json.loads((tmp_path / "codh-cycle.json").read_text(encoding="utf-8"))
    assert payload["updated_at"] == "2026-05-31T08:00:00-04:00"

"""MAT-08: preset remote slideshow operation log."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import Request

import pytest

from harite.slideshow_op_log import log_slideshow_op
from harite.sources import empty_catalog
from harite.sources_preset import import_preset_source
from harite.sources_remote import JMA_LIST_URL, sync_remote_source
from harite.sources_remote_codh import codh_slideshow_tick
from harite.sources_remote_jma import jma_slideshow_tick
from tests.remote_sync_http_mocks import install_ndl_codh_urlopen_mock


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_log_slideshow_op_noop_without_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("HARITE_SLIDESHOW_OP_LOG", raising=False)
    log_path = tmp_path / "op.jsonl"
    log_slideshow_op("TEST_STEP", ok=True, note="ignored")
    assert not log_path.exists()


def test_log_slideshow_op_writes_jsonl(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_path = tmp_path / "op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))
    log_slideshow_op("TEST_STEP", ok=True, source_id="src-1", url="https://example.test/x")

    records = _read_jsonl(log_path)
    assert len(records) == 1
    record = records[0]
    assert record["step"] == "TEST_STEP"
    assert record["ok"] is True
    assert record["source_id"] == "src-1"
    assert record["url"] == "https://example.test/x"
    assert record["ts_jst"].endswith("+09:00")


def test_ndl_sync_emits_sequence_log(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "slideshow-op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))
    install_ndl_codh_urlopen_mock(monkeypatch)

    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-illust", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root, slideshow_phase="refresh")

    steps = [record["step"] for record in _read_jsonl(log_path)]
    assert steps[:2] == ["REMOTE_SYNC_BEGIN", "NDL_META_URL"]
    assert "NDL_IIIF_URL" in steps
    assert "NDL_IIIF_GET" in steps
    assert "NDL_CACHE_WRITE" in steps
    assert steps[-1] == "REMOTE_SYNC_END"
    assert _read_jsonl(log_path)[-1]["ok"] is True
    cache_write = next(record for record in _read_jsonl(log_path) if record["step"] == "NDL_CACHE_WRITE")
    assert cache_write["image_fetched"] is True
    assert cache_write["cache_written"] is True
    assert cache_write["had_previous"] is False
    assert cache_write["content_changed"] is True
    assert cache_write["overwritten"] is False


def test_codh_sync_emits_index_and_image_steps(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "slideshow-op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))
    install_ndl_codh_urlopen_mock(monkeypatch)

    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root, slideshow_phase="refresh")

    steps = [record["step"] for record in _read_jsonl(log_path)]
    assert "CODH_SYNC_PICK" in steps
    assert "CODH_INDEX_PROBE" in steps
    assert "CODH_INDEX_BUILT" in steps
    assert "CODH_IMAGE_URL" in steps
    assert "CODH_IMAGE_GET" in steps
    assert steps[-1] == "REMOTE_SYNC_END"
    image_get = next(record for record in _read_jsonl(log_path) if record["step"] == "CODH_IMAGE_GET")
    assert image_get["image_fetched"] is True
    assert image_get["cache_written"] is True
    assert image_get["content_changed"] is True


def test_codh_tick_logs_fetch_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from io import BytesIO
    from urllib.error import HTTPError

    log_path = tmp_path / "slideshow-op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))
    install_ndl_codh_urlopen_mock(monkeypatch)

    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    def fail_codh_image_get(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith("https://example.test/iiif/"):
            raise HTTPError(target, 404, "Not Found", hdrs=None, fp=BytesIO())
        raise AssertionError(f"unexpected url during tick: {target}")

    monkeypatch.setattr("harite.sources_remote.urlopen", fail_codh_image_get)
    log_path.write_text("", encoding="utf-8")

    ok = codh_slideshow_tick(catalog, entry.id, "sequential")
    assert ok is False

    records = _read_jsonl(log_path)
    assert any(record["step"] == "CODH_IMAGE_GET" and record["ok"] is False for record in records)
    assert records[-1]["step"] == "CODH_TICK"
    assert records[-1]["ok"] is False
    assert records[-1]["image_fetched"] is False
    assert records[-1]["cache_written"] is False


def test_ndl_tick_logs_overwrite_outcome(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from harite.sources_remote import ndl_slideshow_tick

    log_path = tmp_path / "slideshow-op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))
    install_ndl_codh_urlopen_mock(monkeypatch)

    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-illust", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    log_path.write_text("", encoding="utf-8")

    assert ndl_slideshow_tick(catalog, entry.id, side="L") is True

    tick = _read_jsonl(log_path)[-1]
    assert tick["step"] == "NDL_TICK"
    assert tick["image_fetched"] is True
    assert tick["cache_written"] is True
    assert tick["had_previous"] is True
    assert tick["overwritten"] is True


def test_jma_tick_logs_filename_unchanged_without_fetch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import json
    from io import BytesIO

    list_payload = {"near": {"now": ["stale_JRcolor.png", "fresh_JRcolor.png"]}}
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
    log_path = tmp_path / "slideshow-op.jsonl"
    monkeypatch.setenv("HARITE_SLIDESHOW_OP_LOG", str(log_path))

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target == JMA_LIST_URL:

            class _List:
                def read(self) -> bytes:
                    return json.dumps(list_payload).encode("utf-8")

                def __enter__(self) -> "_List":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _List()
        if target.endswith("fresh_JRcolor.png"):

            class _Png:
                def read(self) -> bytes:
                    return png_bytes

                def __enter__(self) -> "_Png":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Png()
        raise AssertionError(target)

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "jma-near-color", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    log_path.write_text("", encoding="utf-8")

    result = jma_slideshow_tick(catalog, entry.id, side="R")
    assert result.ok is True
    assert result.no_update is True

    tick = _read_jsonl(log_path)[-1]
    assert tick["step"] == "JMA_TICK"
    assert tick["ok"] is True
    assert tick["image_fetched"] is False
    assert tick["cache_written"] is False
    assert tick["skip_reason"] == "filename_unchanged"
    assert tick["had_previous"] is True

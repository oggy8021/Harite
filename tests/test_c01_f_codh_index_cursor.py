"""C-01-F: CODH index cache, cursor persistence, and slideshow tick."""

from __future__ import annotations

import json
from pathlib import Path
from io import BytesIO
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from harite.sources import empty_catalog
from harite.sources_preset import import_preset_source
from harite.sources_remote import sync_remote_source
from harite.sources_remote_codh import (
    CODH_CYCLE_FILENAME,
    CODH_INDEX_FILENAME,
    CODH_SYNC_RESUME,
    advance_codh_cursor,
    build_codh_index,
    codh_slideshow_tick,
    codh_sync_with_pick,
    load_codh_cycle,
    load_codh_index,
    reconcile_codh_cycle,
    resolve_codh_sync_context,
)

_JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 16
_THUMB_TEMPLATE = "https://example.test/iiif/book{idx}.tif/10,20,30,40/200,/0/default.jpg"
_MAX_TEMPLATE = "https://example.test/iiif/book{idx}.tif/10,20,30,40/max/0/default.jpg"


def _codh_results(total: int, *, start: int = 0, count: int | None = None) -> dict[str, Any]:
    if count is None:
        count = min(50, max(0, total - start))
    return {
        "total": total,
        "results": [
            {"canvasThumbnail": _THUMB_TEMPLATE.format(idx=start + offset)}
            for offset in range(count)
        ],
    }


def _install_codh_paging_mock(
    monkeypatch: pytest.MonkeyPatch,
    *,
    total: int = 5,
    image_fail_urls: set[str] | None = None,
) -> list[str]:
    seen: list[str] = []
    image_fail_urls = image_fail_urls or set()

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        seen.append(target)
        if "mp.ex.nii.ac.jp/api/" in target and "/search" in target:
            assert "limit=" in target
            if "limit=1" in target:
                payload = {"total": total}
            else:
                start = 0
                if "start=" in target:
                    start = int(target.split("start=")[1].split("&")[0])
                payload = _codh_results(total, start=start)
            return _json_response(payload)
        if target.startswith("https://example.test/iiif/"):
            if "/200,/" in target:
                raise AssertionError(f"unexpected thumbnail url: {target}")
            if target in image_fail_urls:
                raise HTTPError(target, 500, "fail", hdrs=None, fp=BytesIO())

            class _Img:
                def read(self) -> bytes:
                    return _JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        raise AssertionError(f"unexpected url: {target}")

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    return seen


def _json_response(payload: dict[str, Any]) -> Any:
    class _Json:
        def read(self) -> bytes:
            return json.dumps(payload).encode("utf-8")

        def __enter__(self) -> "_Json":
            return self

        def __exit__(self, *exc: object) -> None:
            return None

    return _Json()


def test_build_codh_index_pages_and_normalizes_urls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    seen = _install_codh_paging_mock(monkeypatch, total=5)
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=tmp_path / "cache")
    ctx = resolve_codh_sync_context(entry)

    index = build_codh_index(ctx)

    assert any("limit=1" in url for url in seen)
    assert any("limit=50" in url for url in seen)
    assert index["total"] == 5
    assert len(index["entries"]) == 5
    assert index["entries"][0]["image_url"] == _MAX_TEMPLATE.format(idx=0)
    saved = load_codh_index(ctx.cache_dir)
    assert saved is not None
    assert saved["query_key"] == index["query_key"]


def test_sync_refresh_writes_index_cycle_and_latest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_codh_paging_mock(monkeypatch, total=3)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=cache_root)

    sync_remote_source(catalog, entry.id, cache_root=cache_root, codh_sync_pick="refresh")

    cache_dir = Path(entry.path)
    assert (cache_dir / CODH_INDEX_FILENAME).is_file()
    assert (cache_dir / CODH_CYCLE_FILENAME).is_file()
    assert (cache_dir / "latest.jpg").is_file()


def test_resume_sync_does_not_advance_cursor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_codh_paging_mock(monkeypatch, total=3)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache_root)
    ctx = resolve_codh_sync_context(entry)
    build_codh_index(ctx)
    cycle = reconcile_codh_cycle(None, load_codh_index(ctx.cache_dir) or {})
    cycle["index"] = 2
    from harite.sources_remote_codh import save_codh_cycle

    save_codh_cycle(ctx.cache_dir, cycle)

    codh_sync_with_pick(ctx, CODH_SYNC_RESUME)

    restored = load_codh_cycle(ctx.cache_dir)
    assert restored is not None
    assert restored["index"] == 2


def test_codh_slideshow_tick_advances_sequential_cursor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    seen = _install_codh_paging_mock(monkeypatch, total=3)
    monkeypatch.setattr("harite.sources_remote_codh.random.randint", lambda _a, _b: 0)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root, codh_sync_pick="refresh")
    search_calls_before = sum(1 for url in seen if "/search" in url)

    assert codh_slideshow_tick(catalog, entry.id, "sequential") is True
    search_calls_after = sum(1 for url in seen if "/search" in url)
    assert search_calls_after == search_calls_before

    cycle = load_codh_cycle(Path(entry.path))
    assert cycle is not None
    assert cycle["index"] == 1


def test_codh_tick_image_failure_keeps_latest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fail_urls = {_MAX_TEMPLATE.format(idx=i) for i in range(3)}
    _install_codh_paging_mock(monkeypatch, total=3, image_fail_urls=fail_urls)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache_root)
    ctx = resolve_codh_sync_context(entry)
    build_codh_index(ctx)
    from harite.sources_remote_codh import save_codh_cycle

    save_codh_cycle(ctx.cache_dir, reconcile_codh_cycle({"index": 0}, load_codh_index(ctx.cache_dir) or {}))
    latest = Path(entry.path) / "latest.jpg"
    latest.write_bytes(_JPEG_BYTES)
    cycle_before = load_codh_cycle(Path(entry.path))

    assert codh_slideshow_tick(catalog, entry.id, "sequential") is False
    assert latest.read_bytes() == _JPEG_BYTES
    assert load_codh_cycle(Path(entry.path)) == cycle_before


def test_codh_tick_skips_failed_image_within_attempts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fail_url = _MAX_TEMPLATE.format(idx=1)
    _install_codh_paging_mock(monkeypatch, total=3, image_fail_urls={fail_url})
    monkeypatch.setattr("harite.sources_remote_codh.random.randint", lambda _a, _b: 0)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root, codh_sync_pick="refresh")

    assert codh_slideshow_tick(catalog, entry.id, "sequential") is True
    cycle = load_codh_cycle(Path(entry.path))
    assert cycle is not None
    assert cycle["index"] == 1

    assert codh_slideshow_tick(catalog, entry.id, "sequential") is True
    cycle = load_codh_cycle(Path(entry.path))
    assert cycle is not None
    assert cycle["index"] == 3
    assert cycle["previous_image_url"] == _MAX_TEMPLATE.format(idx=2)


def test_reconcile_resets_cursor_on_query_key_mismatch() -> None:
    index = {
        "query_key": "edo-spots|where:桜",
        "entries": [{"image_url": _MAX_TEMPLATE.format(idx=0)}],
    }
    cycle = {"query_key": "edo-spots|where:梅", "index": 4, "previous_image_url": "x"}
    reconciled = reconcile_codh_cycle(cycle, index)
    assert reconciled["query_key"] == index["query_key"]
    assert reconciled["index"] == 0
    assert reconciled["previous_image_url"] == ""


def test_advance_codh_cursor_sequential_wraps_at_end() -> None:
    index = {
        "entries": [
            {"image_url": _MAX_TEMPLATE.format(idx=0)},
            {"image_url": _MAX_TEMPLATE.format(idx=1)},
        ]
    }
    cycle = {"index": 2, "previous_image_url": ""}
    url, updated = advance_codh_cursor(index, cycle, "sequential")
    assert url == _MAX_TEMPLATE.format(idx=0)
    assert updated["index"] == 3

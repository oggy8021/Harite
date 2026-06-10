"""MAT-18b: NDL searchbytext keyword batch + cursor cycle."""

from __future__ import annotations

from pathlib import Path

import pytest

from harite.sources import empty_catalog, import_preset_source
from harite.sources_remote import ndl_slideshow_tick, sync_remote_source
from harite.sources_remote_ndl_keyword import (
    NDL_SEARCH_BATCH_FILENAME,
    NDL_SEARCH_PAGE_SIZE,
    load_ndl_search_batch,
    load_ndl_search_cycle,
)
from tests.remote_sync_http_mocks import (
    NDL_SEARCH_POOL,
    install_ndl_codh_urlopen_mock,
    ndl_iiif_url_from_illustration,
)


def _pid_at_cursor(cache_dir: Path) -> str:
    cycle = load_ndl_search_cycle(cache_dir)
    batch = load_ndl_search_batch(cache_dir)
    assert cycle is not None and batch is not None
    index = int(cycle["cursor_index"])
    return str(batch["entries"][index]["pid"])


def test_ndl_search_keyword_sync_resume_then_tick_advances_cursor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_ndl_codh_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache_root)
    cache_dir = Path(entry.path)

    sync_remote_source(catalog, entry.id, cache_root=cache_root, codh_sync_pick="resume")
    assert (cache_dir / "latest.jpg").is_file()
    assert _pid_at_cursor(cache_dir) == NDL_SEARCH_POOL[0]["pid"]
    cycle = load_ndl_search_cycle(cache_dir)
    assert cycle is not None
    assert cycle["cursor_index"] == 0
    assert (cache_dir / NDL_SEARCH_BATCH_FILENAME).is_file()

    assert ndl_slideshow_tick(catalog, entry.id, side="R") is True
    assert _pid_at_cursor(cache_dir) == NDL_SEARCH_POOL[1]["pid"]
    cycle = load_ndl_search_cycle(cache_dir)
    assert cycle is not None
    assert cycle["cursor_index"] == 1

    assert ndl_slideshow_tick(catalog, entry.id, side="R") is True
    assert _pid_at_cursor(cache_dir) == NDL_SEARCH_POOL[2]["pid"]
    cycle = load_ndl_search_cycle(cache_dir)
    assert cycle is not None
    assert cycle["cursor_index"] == 2


def test_ndl_search_keyword_refresh_resets_cursor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_ndl_codh_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache_root)
    cache_dir = Path(entry.path)

    sync_remote_source(catalog, entry.id, cache_root=cache_root, codh_sync_pick="resume")
    ndl_slideshow_tick(catalog, entry.id, side="R")

    sync_remote_source(catalog, entry.id, cache_root=cache_root, codh_sync_pick="refresh")
    assert _pid_at_cursor(cache_dir) == NDL_SEARCH_POOL[0]["pid"]
    cycle = load_ndl_search_cycle(cache_dir)
    assert cycle is not None
    assert cycle["cursor_index"] == 0
    assert cycle["from"] == 0


def test_ndl_search_keyword_wraps_from_offset_when_batch_exhausted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_ndl_codh_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache_root)
    cache_dir = Path(entry.path)

    sync_remote_source(catalog, entry.id, cache_root=cache_root, codh_sync_pick="resume")
    for _ in range(len(NDL_SEARCH_POOL) - 1):
        assert ndl_slideshow_tick(catalog, entry.id, side="R") is True

    assert ndl_slideshow_tick(catalog, entry.id, side="R") is True
    assert _pid_at_cursor(cache_dir) == NDL_SEARCH_POOL[0]["pid"]
    cycle = load_ndl_search_cycle(cache_dir)
    assert cycle is not None
    assert cycle["from"] == 0
    assert cycle["cursor_index"] == 0


def test_ndl_searchbytext_url_uses_page_size_and_from() -> None:
    from harite.sources_remote_ndl_keyword import ndl_searchbytext_url

    url = ndl_searchbytext_url("妖怪", from_offset=3, size=NDL_SEARCH_PAGE_SIZE)
    assert "keyword2vec=" in url
    assert f"size={NDL_SEARCH_PAGE_SIZE}" in url
    assert "from=3" in url
    assert ndl_iiif_url_from_illustration(NDL_SEARCH_POOL[0]).startswith("https://dl.ndl.go.jp/api/iiif/")

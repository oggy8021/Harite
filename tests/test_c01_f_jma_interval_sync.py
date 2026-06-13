"""C-01-F: JMA interval tick sync with filename skip."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from io import BytesIO
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from harite.sources import empty_catalog
from harite.sources_preset import import_preset_source
from harite.sources_remote import JMA_LIST_URL, sync_remote_source
from harite.sources_remote_jma import (
    JMA_CYCLE_FILENAME,
    jma_slideshow_tick,
    load_jma_cycle,
)

_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
_LIST_INITIAL = {
    "near": {"now": ["stale_JRcolor.png", "fresh_JRcolor.png"]},
}
_LIST_UPDATED = {
    "near": {"now": ["stale_JRcolor.png", "fresh_JRcolor.png", "newer_JRcolor.png"]},
}


def _install_jma_tick_mock(
    monkeypatch: pytest.MonkeyPatch,
    *,
    list_payloads: list[dict[str, Any]] | None = None,
    png_fail_filenames: set[str] | None = None,
) -> dict[str, int]:
    counts = {"list": 0, "png": 0}
    payloads = list(list_payloads or [_LIST_INITIAL])
    png_fail_filenames = png_fail_filenames or set()

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target == JMA_LIST_URL:
            counts["list"] += 1
            payload = payloads[min(counts["list"] - 1, len(payloads) - 1)]

            class _List:
                def read(self) -> bytes:
                    return json.dumps(payload).encode("utf-8")

                def __enter__(self) -> "_List":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _List()
        if "weather_map/data/png/" in target:
            counts["png"] += 1
            filename = target.rsplit("/", 1)[-1]
            if filename in png_fail_filenames:
                raise HTTPError(target, 500, "fail", hdrs=None, fp=BytesIO())

            class _Png:
                def read(self) -> bytes:
                    return _PNG_BYTES

                def __enter__(self) -> "_Png":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Png()
        raise AssertionError(f"unexpected url: {target}")

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    return counts


def test_jma_sync_writes_cycle_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_jma_tick_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "jma-near-color", cache_root=cache_root)

    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    cycle = load_jma_cycle(Path(entry.path))
    assert cycle is not None
    assert cycle["preset_id"] == "jma-near-color"
    assert cycle["filename"] == "fresh_JRcolor.png"
    assert (Path(entry.path) / JMA_CYCLE_FILENAME).is_file()


def test_jma_tick_skips_png_when_filename_unchanged(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    counts = _install_jma_tick_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "jma-near-color", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    counts["list"] = 0
    counts["png"] = 0

    result = jma_slideshow_tick(catalog, entry.id)
    assert result.ok is True
    assert result.no_update is True
    assert counts["list"] == 1
    assert counts["png"] == 0


def test_jma_tick_fetches_png_when_filename_changes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    counts = _install_jma_tick_mock(monkeypatch, list_payloads=[_LIST_INITIAL, _LIST_UPDATED])
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "jma-near-color", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    result = jma_slideshow_tick(catalog, entry.id)
    assert result.ok is True
    assert result.no_update is False
    assert counts["list"] == 2
    assert counts["png"] == 2

    cycle = load_jma_cycle(Path(entry.path))
    assert cycle is not None
    assert cycle["filename"] == "newer_JRcolor.png"


def test_jma_tick_png_failure_keeps_latest_and_cycle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    counts = _install_jma_tick_mock(
        monkeypatch,
        list_payloads=[_LIST_INITIAL, _LIST_UPDATED],
        png_fail_filenames={"newer_JRcolor.png"},
    )
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "jma-near-color", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    latest = Path(entry.path) / "latest.png"
    before = latest.read_bytes()
    cycle_before = load_jma_cycle(Path(entry.path))
    png_before = counts["png"]

    result = jma_slideshow_tick(catalog, entry.id)
    assert result.ok is False
    assert latest.read_bytes() == before
    assert load_jma_cycle(Path(entry.path)) == cycle_before
    assert counts["png"] == png_before + 1

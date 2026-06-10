"""C-01-E: NDL and CODH remote sync with mocked HTTP."""

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
from harite.sources_remote import (
    CODH_SEARCH_URL_TEMPLATE,
    NDL_RANDOM_FACET_URL,
    ndl_slideshow_tick,
    sync_remote_source,
)
from tests.remote_sync_http_mocks import (
    CODH_RESULTS,
    JPEG_BYTES,
    NDL_ILLUSTRATION,
    install_ndl_codh_urlopen_mock,
    ndl_iiif_url_from_sample,
)


def test_ndl_facet_sync_writes_latest_jpg(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_ndl_codh_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-illust", cache_root=cache_root)

    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    latest = Path(entry.path) / "latest.jpg"
    assert latest.is_file()
    assert latest.read_bytes() == JPEG_BYTES


def test_ndl_iiif_404_retries_next_illustration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    iiif_url = ndl_iiif_url_from_sample()
    facet_calls = {"count": 0}
    iiif_calls = {"count": 0}

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL):
            facet_calls["count"] += 1

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(NDL_ILLUSTRATION).encode("utf-8")

                def __enter__(self) -> "_Json":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Json()
        if target == iiif_url:
            iiif_calls["count"] += 1
            if iiif_calls["count"] == 1:
                raise HTTPError(target, 404, "Not Found", hdrs=None, fp=BytesIO())

            class _Img:
                def read(self) -> bytes:
                    return JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        raise AssertionError(target)

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-illust", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    assert facet_calls["count"] == 2
    assert iiif_calls["count"] == 2
    latest = Path(entry.path) / "latest.jpg"
    assert latest.is_file()


def test_ndl_iiif_400_retries_next_illustration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    iiif_url = ndl_iiif_url_from_sample()
    facet_calls = {"count": 0}
    iiif_calls = {"count": 0}

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL):
            facet_calls["count"] += 1

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(NDL_ILLUSTRATION).encode("utf-8")

                def __enter__(self) -> "_Json":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Json()
        if target == iiif_url:
            iiif_calls["count"] += 1
            if iiif_calls["count"] == 1:
                raise HTTPError(target, 400, "Bad Request", hdrs=None, fp=BytesIO())

            class _Img:
                def read(self) -> bytes:
                    return JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        raise AssertionError(target)

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-indoor", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    assert facet_calls["count"] == 2
    assert iiif_calls["count"] == 2
    latest = Path(entry.path) / "latest.jpg"
    assert latest.is_file()


def test_ndl_random_map_uses_facet_url(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    seen: list[str] = []

    iiif_url = ndl_iiif_url_from_sample()

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        seen.append(target)
        if target.startswith(NDL_RANDOM_FACET_URL):
            assert "f-graphictags.tagname=graphic_map" in target

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(NDL_ILLUSTRATION).encode("utf-8")

                def __enter__(self) -> "_Json":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Json()
        if target == iiif_url:

            class _Img:
                def read(self) -> bytes:
                    return JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        raise AssertionError(target)

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-map", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    assert any(u.startswith(NDL_RANDOM_FACET_URL) for u in seen)


def test_codh_edo_spots_keyword_sync(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_ndl_codh_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=cache_root)

    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    latest = Path(entry.path) / "latest.jpg"
    assert latest.is_file()
    assert latest.read_bytes() == JPEG_BYTES


def test_codh_random_sync_builds_paged_index(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    seen: list[str] = []

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        seen.append(target)
        if target.startswith(
            CODH_SEARCH_URL_TEMPLATE.format(indexer="edo-spots")
        ):
            assert "limit=" in target
            payload = (
                {"total": 5}
                if "limit=1" in target
                else CODH_RESULTS
            )

            class _Codh:
                def read(self) -> bytes:
                    return json.dumps(payload).encode("utf-8")

                def __enter__(self) -> "_Codh":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Codh()
        if target.startswith("https://example.test/iiif/"):

            class _Img:
                def read(self) -> bytes:
                    return JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        raise AssertionError(target)

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    assert any("limit=50" in u for u in seen)
    assert (Path(entry.path) / "codh-index.json").is_file()


def test_ndl_slideshow_tick_fetches_on_each_tick(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    facet_calls = {"count": 0}
    iiif_url = ndl_iiif_url_from_sample()

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL):
            facet_calls["count"] += 1

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(NDL_ILLUSTRATION).encode("utf-8")

                def __enter__(self) -> "_Json":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Json()
        if target == iiif_url:

            class _Img:
                def read(self) -> bytes:
                    return JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        raise AssertionError(target)

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-illust", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    facet_calls["count"] = 0

    assert ndl_slideshow_tick(catalog, entry.id) is True
    assert facet_calls["count"] == 1
    assert (Path(entry.path) / "latest.jpg").read_bytes() == JPEG_BYTES

    assert ndl_slideshow_tick(catalog, entry.id) is True
    assert facet_calls["count"] == 2


def test_ndl_slideshow_tick_failure_keeps_latest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    install_ndl_codh_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-illust", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    latest = Path(entry.path) / "latest.jpg"
    before = latest.read_bytes()
    iiif_url = ndl_iiif_url_from_sample()

    def failing_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL):

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(NDL_ILLUSTRATION).encode("utf-8")

                def __enter__(self) -> "_Json":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Json()
        if target == iiif_url:
            raise HTTPError(target, 404, "Not Found", hdrs=None, fp=BytesIO())
        raise AssertionError(target)

    monkeypatch.setattr("harite.sources_remote.urlopen", failing_urlopen)

    assert ndl_slideshow_tick(catalog, entry.id) is False
    assert latest.read_bytes() == before

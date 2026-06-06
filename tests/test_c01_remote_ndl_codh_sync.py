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
    NDL_IIIF_TEMPLATE,
    NDL_RANDOM_FACET_URL,
    sync_remote_source,
)

_JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 16
_NDL_ILLUSTRATION = [
    {
        "pid": "2558316",
        "page": 28,
        "x": 56.3,
        "y": 53.3,
        "w": 32.1,
        "h": 26.4,
    }
]
_CODH_THUMB = (
    "https://example.test/iiif/book.tif/10,20,30,40/200,/0/default.jpg"
)
_CODH_RESULTS = {
    "total": 3,
    "results": [{"canvasThumbnail": _CODH_THUMB}],
}


def _install_ndl_codh_urlopen_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    iiif_url = _ndl_iiif_url_from_sample()

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL):

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(_NDL_ILLUSTRATION).encode("utf-8")

                def __enter__(self) -> "_Json":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Json()
        if target == iiif_url or target.startswith("https://example.test/iiif/"):
            if "/200,/" in target:
                raise AssertionError(f"unexpected thumbnail url: {target}")

            class _Img:
                def read(self) -> bytes:
                    return _JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        if "mp.ex.nii.ac.jp/api/" in target and "/search" in target:
            if "limit=1" in target:
                payload: dict[str, Any] = {"total": _CODH_RESULTS["total"]}
            else:
                payload = _CODH_RESULTS

            class _Codh:
                def read(self) -> bytes:
                    return json.dumps(payload).encode("utf-8")

                def __enter__(self) -> "_Codh":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Codh()
        raise AssertionError(f"unexpected url: {target}")

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)


def _ndl_iiif_url_from_sample() -> str:
    item = _NDL_ILLUSTRATION[0]
    return NDL_IIIF_TEMPLATE.format(
        pid=item["pid"],
        page=item["page"],
        x=item["x"],
        y=item["y"],
        w=item["w"],
        h=item["h"],
    )


def test_ndl_facet_sync_writes_latest_jpg(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_ndl_codh_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-random-illust", cache_root=cache_root)

    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    latest = Path(entry.path) / "latest.jpg"
    assert latest.is_file()
    assert latest.read_bytes() == _JPEG_BYTES


def test_ndl_iiif_404_retries_next_illustration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    iiif_url = _ndl_iiif_url_from_sample()
    facet_calls = {"count": 0}
    iiif_calls = {"count": 0}

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL):
            facet_calls["count"] += 1

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(_NDL_ILLUSTRATION).encode("utf-8")

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
                    return _JPEG_BYTES

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
    iiif_url = _ndl_iiif_url_from_sample()
    facet_calls = {"count": 0}
    iiif_calls = {"count": 0}

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL):
            facet_calls["count"] += 1

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(_NDL_ILLUSTRATION).encode("utf-8")

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
                    return _JPEG_BYTES

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

    iiif_url = _ndl_iiif_url_from_sample()

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        seen.append(target)
        if target.startswith(NDL_RANDOM_FACET_URL):
            assert "f-graphictags.tagname=graphic_map" in target

            class _Json:
                def read(self) -> bytes:
                    return json.dumps(_NDL_ILLUSTRATION).encode("utf-8")

                def __enter__(self) -> "_Json":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Json()
        if target == iiif_url:

            class _Img:
                def read(self) -> bytes:
                    return _JPEG_BYTES

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
    _install_ndl_codh_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=cache_root)

    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    latest = Path(entry.path) / "latest.jpg"
    assert latest.is_file()
    assert latest.read_bytes() == _JPEG_BYTES


def test_codh_random_sync_builds_paged_index(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    seen: list[str] = []

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        seen.append(target)
        if target.startswith(
            CODH_SEARCH_URL_TEMPLATE.format(indexer="edo-shops")
        ):
            assert "limit=" in target
            payload = (
                {"total": 5}
                if "limit=1" in target
                else _CODH_RESULTS
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
                    return _JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        raise AssertionError(target)

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "codh-edo-shops-random", cache_root=cache_root)
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    assert any("limit=50" in u for u in seen)
    assert (Path(entry.path) / "codh-index.json").is_file()

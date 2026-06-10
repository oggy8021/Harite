"""Shared HTTP mocks for NDL/CODH remote sync tests."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs, urlparse
from urllib.request import Request

import pytest

from harite.sources_remote import NDL_IIIF_TEMPLATE, NDL_RANDOM_FACET_URL, NDL_SEARCHBYTEXT_URL

JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 16
NDL_ILLUSTRATION = [
    {
        "pid": "2558316",
        "page": 28,
        "x": 56.3,
        "y": 53.3,
        "w": 32.1,
        "h": 26.4,
    }
]
NDL_SEARCH_POOL = [
    NDL_ILLUSTRATION[0],
    {
        "pid": "1111111",
        "page": 10,
        "x": 12.0,
        "y": 13.0,
        "w": 20.0,
        "h": 21.0,
    },
    {
        "pid": "2222222",
        "page": 11,
        "x": 22.0,
        "y": 23.0,
        "w": 24.0,
        "h": 25.0,
    },
]
NDL_SEARCH_HIT = len(NDL_SEARCH_POOL)
NDL_SEARCHBYTEXT_RESPONSE = {
    "facets": {},
    "list": NDL_SEARCH_POOL,
    "hit": NDL_SEARCH_HIT,
    "from": 0,
}
CODH_THUMB = "https://example.test/iiif/book.tif/10,20,30,40/200,/0/default.jpg"
CODH_RESULTS = {
    "total": 3,
    "results": [{"canvasThumbnail": CODH_THUMB}],
}


def ndl_iiif_url_from_illustration(item: dict[str, Any]) -> str:
    return NDL_IIIF_TEMPLATE.format(
        pid=item["pid"],
        page=item["page"],
        x=item["x"],
        y=item["y"],
        w=item["w"],
        h=item["h"],
    )


def ndl_iiif_url_from_sample() -> str:
    return ndl_iiif_url_from_illustration(NDL_ILLUSTRATION[0])


def ndl_searchbytext_response_for_url(target: str) -> dict[str, Any]:
    query = parse_qs(urlparse(target).query)
    try:
        from_offset = int((query.get("from") or ["0"])[0])
    except (TypeError, ValueError):
        from_offset = 0
    try:
        size = int((query.get("size") or [str(len(NDL_SEARCH_POOL))])[0])
    except (TypeError, ValueError):
        size = len(NDL_SEARCH_POOL)
    items = NDL_SEARCH_POOL[from_offset : from_offset + size]
    return {
        "facets": {},
        "list": items,
        "hit": NDL_SEARCH_HIT,
        "from": from_offset,
    }


def install_ndl_codh_urlopen_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    iiif_url = ndl_iiif_url_from_sample()

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL) or target.startswith(NDL_SEARCHBYTEXT_URL):

            class _Json:
                def read(self) -> bytes:
                    if target.startswith(NDL_SEARCHBYTEXT_URL):
                        return json.dumps(ndl_searchbytext_response_for_url(target)).encode("utf-8")
                    return json.dumps(NDL_ILLUSTRATION).encode("utf-8")

                def __enter__(self) -> "_Json":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Json()
        if (
            target == iiif_url
            or target.startswith("https://dl.ndl.go.jp/api/iiif/")
            or target.startswith("https://example.test/iiif/")
        ):
            if "/200,/" in target:
                raise AssertionError(f"unexpected thumbnail url: {target}")

            class _Img:
                def read(self) -> bytes:
                    return JPEG_BYTES

                def __enter__(self) -> "_Img":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Img()
        if "mp.ex.nii.ac.jp/api/" in target and "/search" in target:
            if "limit=1" in target:
                payload: dict[str, Any] = {"total": CODH_RESULTS["total"]}
            else:
                payload = CODH_RESULTS

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

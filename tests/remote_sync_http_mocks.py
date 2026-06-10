"""Shared HTTP mocks for NDL/CODH remote sync tests."""

from __future__ import annotations

import json
from typing import Any
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
NDL_SEARCHBYTEXT_RESPONSE = {
    "facets": {},
    "list": NDL_ILLUSTRATION,
    "hit": 1,
    "from": 0,
}
CODH_THUMB = "https://example.test/iiif/book.tif/10,20,30,40/200,/0/default.jpg"
CODH_RESULTS = {
    "total": 3,
    "results": [{"canvasThumbnail": CODH_THUMB}],
}


def ndl_iiif_url_from_sample() -> str:
    item = NDL_ILLUSTRATION[0]
    return NDL_IIIF_TEMPLATE.format(
        pid=item["pid"],
        page=item["page"],
        x=item["x"],
        y=item["y"],
        w=item["w"],
        h=item["h"],
    )


def install_ndl_codh_urlopen_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    iiif_url = ndl_iiif_url_from_sample()

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.startswith(NDL_RANDOM_FACET_URL) or target.startswith(NDL_SEARCHBYTEXT_URL):

            class _Json:
                def read(self) -> bytes:
                    if target.startswith(NDL_SEARCHBYTEXT_URL):
                        return json.dumps(NDL_SEARCHBYTEXT_RESPONSE).encode("utf-8")
                    return json.dumps(NDL_ILLUSTRATION).encode("utf-8")

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

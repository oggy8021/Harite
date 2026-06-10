"""MAT-10: NDL kiriezu area presets — catalog, manifest cache, sync/tick cycle."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from harite.sources import empty_catalog, import_preset_source
from harite.sources_remote import KIND_NDL_KIRIEZU, sync_remote_source
from harite.sources_remote_ndl_kiriezu import (
    NDL_KIRIEZU_CYCLE_FILENAME,
    NDL_KIRIEZU_IIIF_WIDTH,
    NDL_KIRIEZU_MANIFEST_CACHE_FILENAME,
    advance_kiriezu_cycle,
    canvas_id_from_manifest,
    load_kiriezu_cycle,
    ndl_kiriezu_slideshow_tick,
    resolve_kiriezu_preset_spec,
)

_JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 32
def _manifest_for_pid(pid: str) -> dict[str, Any]:
    return {
        "sequences": [
            {
                "canvases": [
                    {
                        "images": [
                            {
                                "resource": {
                                    "@id": (
                                        f"https://dl.ndl.go.jp/api/iiif/{pid}/R0000001/"
                                        "full/full/0/default.jpg"
                                    ),
                                    "service": {
                                        "@id": f"https://dl.ndl.go.jp/api/iiif/{pid}/R0000001",
                                    },
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }


def _json_response(payload: dict[str, Any]) -> Any:
    class _Json:
        def read(self) -> bytes:
            return json.dumps(payload).encode("utf-8")

        def __enter__(self) -> "_Json":
            return self

        def __exit__(self, *exc: object) -> None:
            return None

    return _Json()


def _image_response() -> Any:
    class _Img:
        def read(self) -> bytes:
            return _JPEG_BYTES

        def __enter__(self) -> "_Img":
            return self

        def __exit__(self, *exc: object) -> None:
            return None

    return _Img()


def _install_kiriezu_mock(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        seen.append(target)
        if target.endswith("/manifest.json"):
            pid = target.split("/iiif/")[1].split("/")[0]
            return _json_response(_manifest_for_pid(pid))
        if "/full/1200,/0/default.jpg" in target:
            return _image_response()
        raise AssertionError(f"unexpected url: {target}")

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    return seen


def test_canvas_id_from_manifest() -> None:
    assert canvas_id_from_manifest(_manifest_for_pid("1286208"), "1286208") == "R0000001"


def test_kiriezu_all_preset_has_29_maps() -> None:
    spec = resolve_kiriezu_preset_spec("ndl-kiriezu-all")
    assert len(spec.maps) == 29
    pids = {entry.pid for entry in spec.maps}
    assert len(pids) == 29


def test_kiriezu_group_presets_partition_all_maps() -> None:
    all_spec = resolve_kiriezu_preset_spec("ndl-kiriezu-all")
    group_ids = (
        "ndl-kiriezu-group-shitamachi",
        "ndl-kiriezu-group-yamanote",
        "ndl-kiriezu-group-nihonbashi",
        "ndl-kiriezu-group-north",
        "ndl-kiriezu-group-south",
    )
    grouped: set[str] = set()
    for preset_id in group_ids:
        for entry in resolve_kiriezu_preset_spec(preset_id).maps:
            assert entry.pid not in grouped
            grouped.add(entry.pid)
    assert grouped == {entry.pid for entry in all_spec.maps}


def test_advance_kiriezu_cycle_wraps() -> None:
    spec = resolve_kiriezu_preset_spec("ndl-kiriezu-asakusa")
    cycle = {"preset_id": "ndl-kiriezu-asakusa", "cursor_index": 1}
    advanced = advance_kiriezu_cycle(spec, cycle)
    assert advanced["cursor_index"] == 0


def test_kiriezu_sync_resume_then_tick_advances_cursor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_kiriezu_mock(monkeypatch)
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-kiriezu-asakusa", cache_root=tmp_path / "cache")
    assert entry.kind == KIND_NDL_KIRIEZU

    sync_remote_source(catalog, entry.id, codh_sync_pick="resume")
    cycle = load_kiriezu_cycle(Path(entry.path))
    assert cycle is not None
    assert cycle["cursor_index"] == 0
    assert (Path(entry.path) / "latest.jpg").is_file()

    manifest_cache = Path(entry.path) / NDL_KIRIEZU_MANIFEST_CACHE_FILENAME
    assert manifest_cache.is_file()

    assert ndl_kiriezu_slideshow_tick(catalog, entry.id, side="R") is True
    cycle_after = load_kiriezu_cycle(Path(entry.path))
    assert cycle_after is not None
    assert cycle_after["cursor_index"] == 1


def test_kiriezu_refresh_resets_cursor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_kiriezu_mock(monkeypatch)
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-kiriezu-fukagawa", cache_root=tmp_path / "cache")
    cache_dir = Path(entry.path)
    cycle_path = cache_dir / NDL_KIRIEZU_CYCLE_FILENAME
    cycle_path.parent.mkdir(parents=True, exist_ok=True)
    cycle_path.write_text(
        json.dumps({"preset_id": "ndl-kiriezu-fukagawa", "cursor_index": 0}) + "\n",
        encoding="utf-8",
    )

    sync_remote_source(catalog, entry.id, codh_sync_pick="refresh")
    cycle = load_kiriezu_cycle(cache_dir)
    assert cycle is not None
    assert cycle["cursor_index"] == 0


def test_kiriezu_iiif_url_uses_1200_width(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seen = _install_kiriezu_mock(monkeypatch)
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-kiriezu-asakusa", cache_root=tmp_path / "cache")
    sync_remote_source(catalog, entry.id, codh_sync_pick="refresh")
    assert any(f"/full/{NDL_KIRIEZU_IIIF_WIDTH},/0/default.jpg" in url for url in seen)


def test_kiriezu_sync_skips_failed_iiif_within_attempts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fail_url = (
        "https://dl.ndl.go.jp/api/iiif/1286208/R0000001/"
        f"full/{NDL_KIRIEZU_IIIF_WIDTH},/0/default.jpg"
    )

    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target.endswith("/manifest.json"):
            pid = target.split("/iiif/")[1].split("/")[0]
            return _json_response(_manifest_for_pid(pid))
        if target == fail_url:
            raise HTTPError(target, 404, "missing", hdrs=None, fp=BytesIO())
        if "/full/1200,/0/default.jpg" in target:
            return _image_response()
        raise AssertionError(f"unexpected url: {target}")

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)
    catalog = empty_catalog()
    entry = import_preset_source(catalog, "ndl-kiriezu-asakusa", cache_root=tmp_path / "cache")
    sync_remote_source(catalog, entry.id, codh_sync_pick="refresh")
    assert (Path(entry.path) / "latest.jpg").is_file()

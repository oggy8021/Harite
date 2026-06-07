"""C-01 phase 2: JMA remote sync with mocked HTTP."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.request import Request

import pytest

from harite.sources import empty_catalog, resolve_source
from harite.sources_preset import import_preset_source
from harite.sources_remote import JMA_LIST_URL, sync_remote_source

_SAMPLE_LIST = {
    "near": {"now": ["stale_JRcolor.png", "fresh_JRcolor.png"]},
    "asia": {"now": ["asia_JRcolor.png"]},
    "near_monochrome": {"now": ["stale_JRjmahp.png", "fresh_JRjmahp.png"]},
    "asia_monochrome": {"now": ["asia_JRjmahp.png"]},
}
_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def _install_jma_urlopen_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target == JMA_LIST_URL:
            payload = _SAMPLE_LIST

            class _Response:
                def read(self) -> bytes:
                    import json

                    return json.dumps(payload).encode("utf-8")

                def __enter__(self) -> "_Response":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Response()
        if "weather_map/data/png/" in target:
            assert target.endswith(
                (
                    "fresh_JRcolor.png",
                    "asia_JRcolor.png",
                    "fresh_JRjmahp.png",
                    "asia_JRjmahp.png",
                )
            )

            class _PngResponse:
                def read(self) -> bytes:
                    return _PNG_BYTES

                def __enter__(self) -> "_PngResponse":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _PngResponse()
        raise AssertionError(f"unexpected url: {target}")

    monkeypatch.setattr("harite.sources_remote.urlopen", fake_urlopen)


def test_jma_sync_writes_latest_png(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_jma_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(
        catalog,
        "jma-near-color",
        cache_root=cache_root,
    )

    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    cache_dir = Path(entry.path)
    latest = cache_dir / "latest.png"
    assert latest.is_file()
    assert latest.read_bytes() == _PNG_BYTES
    assert list(cache_dir.glob("*.png")) == [latest]
    from harite.sources_remote_jma import load_jma_cycle

    cycle = load_jma_cycle(cache_dir)
    assert cycle is not None
    assert cycle["filename"] == "fresh_JRcolor.png"


def test_jma_sync_near_monochrome_preset_picks_jrjmahp_latest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_jma_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(
        catalog,
        "jma-near-monochrome",
        cache_root=cache_root,
    )

    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    assert (Path(entry.path) / "latest.png").read_bytes() == _PNG_BYTES


def test_jma_sync_asia_monochrome_preset(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_jma_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(
        catalog,
        "jma-asia-monochrome",
        cache_root=cache_root,
    )

    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    assert (Path(entry.path) / "latest.png").is_file()


def test_jma_sync_asia_preset_picks_asia_now(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_jma_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(
        catalog,
        "jma-asia-color",
        cache_root=cache_root,
    )

    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    assert (Path(entry.path) / "latest.png").is_file()


def test_resolve_source_after_sync(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_jma_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(
        catalog,
        "jma-near-color",
        cache_root=cache_root,
    )
    sync_remote_source(catalog, entry.id, cache_root=cache_root)

    resolved = resolve_source(catalog, entry.id)
    assert resolved == Path(entry.path).resolve()
    assert (resolved / "latest.png").is_file()


def test_resolve_remote_source_recreates_missing_cache_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import shutil

    _install_jma_urlopen_mock(monkeypatch)
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(
        catalog,
        "jma-near-color",
        cache_root=cache_root,
    )
    sync_remote_source(catalog, entry.id, cache_root=cache_root)
    cache_dir = Path(entry.path)
    assert cache_dir.is_dir()

    shutil.rmtree(cache_dir)
    assert not cache_dir.exists()

    resolved = resolve_source(catalog, entry.id)
    assert resolved == cache_dir.resolve()
    assert cache_dir.is_dir()
    assert not (resolved / "latest.png").is_file()


def test_update_source_rejects_remote_path_change(tmp_path: Path) -> None:
    from harite.sources import update_source as core_update_source

    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    entry = import_preset_source(
        catalog,
        "jma-near-color",
        cache_root=cache_root,
    )

    with pytest.raises(ValueError, match="path cannot be changed"):
        core_update_source(catalog, entry.id, path=tmp_path / "other")

"""C-01 phase 2: slideshow start syncs JMA remote cache before resolve."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import Request

import pytest

from harite.display_context import TwoScreenOptimizeContext
from harite.gui.views.main_window import MainWindow
from harite.sources import bootstrap_preset_sources, empty_catalog, save_catalog
from harite.sources_remote import JMA_LIST_URL
from harite.workspace import Display

_SAMPLE_LIST = {
    "near": {"now": ["near_JRcolor.png"]},
    "asia": {"now": ["asia_JRcolor.png"]},
}
_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def _install_jma_urlopen_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str | Request, *args: Any, **kwargs: Any) -> Any:
        target = url if isinstance(url, str) else url.full_url
        if target == JMA_LIST_URL:

            class _Response:
                def read(self) -> bytes:
                    return json.dumps(_SAMPLE_LIST).encode("utf-8")

                def __enter__(self) -> "_Response":
                    return self

                def __exit__(self, *exc: object) -> None:
                    return None

            return _Response()
        if "weather_map/data/png/" in target:

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


def _install_dual_slideshow_env(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    monkeypatch.setattr(
        "harite.gui.views.main_window.plugin_registry.get",
        lambda _name: DummyPlugin(),
    )
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="HDMI-1", width=1920, height=1080, x_offset=0, y_offset=0),
                Display(name="DP-1", width=1920, height=1080, x_offset=1920, y_offset=0),
            ),
            resolution=(3840, 1080),
            l_display=(1920, 1080),
            r_display=(1920, 1080),
        ),
    )

    def _apply_ok(self, left, right, cycle_phase="tick"):
        return True, None

    monkeypatch.setattr(MainWindow, "_apply_slideshow_selection", _apply_ok)


def test_slideshow_start_syncs_jma_profile_and_resolves_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from harite.gui.adapters_qt import qt_source_catalog

    _install_jma_urlopen_mock(monkeypatch)
    _install_dual_slideshow_env(monkeypatch)
    _materialize_orig = qt_source_catalog.materialize_source_catalog_at_path

    def _materialize_no_bulk_sync(path: Path, *, owner: object | None = None, **kwargs: object) -> object:
        return _materialize_orig(path, owner=owner, sync_remote=False)

    monkeypatch.setattr(
        qt_source_catalog,
        "materialize_source_catalog_at_path",
        _materialize_no_bulk_sync,
    )

    cache_root = tmp_path / "remote-cache"
    catalog_path = tmp_path / "harite-sources.json"
    catalog = empty_catalog()
    bootstrap_preset_sources(catalog, cache_root=cache_root, sync=False)
    save_catalog(catalog, catalog_path)
    profile_id = catalog.profiles[0].id

    window = MainWindow()
    window._source_catalog_path = catalog_path
    assert window.on_select_slideshow_profile(profile_id) is True

    assert window.on_slideshow_start() is True
    assert window.slideshow_srcdir_l
    assert window.slideshow_srcdir_r
    left_cache = Path(window.slideshow_srcdir_l)
    right_cache = Path(window.slideshow_srcdir_r)
    assert (left_cache / "latest.png").is_file()
    assert (right_cache / "latest.png").is_file()

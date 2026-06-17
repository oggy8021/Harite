"""#507: Slideshow tab L/R cursor position chips."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from harite.gui.views.slideshow_cursor_position import (
    SlideshowSideCursorDisplay,
    format_side_cursor_display,
    format_slideshow_side_cursor_chip,
    resolve_slideshow_cursor_displays,
)
from harite.slideshow import SlideshowCycleState
from harite.sources import empty_catalog, import_preset_source, save_catalog
from harite.sources_remote_codh import CODH_CYCLE_FILENAME, CODH_INDEX_FILENAME
from harite.sources_remote_jma import JMA_CYCLE_FILENAME
from harite.sources_remote_ndl_kiriezu import NDL_KIRIEZU_CYCLE_FILENAME
from harite.sources_remote_ndl_keyword import (
    NDL_SEARCH_BATCH_FILENAME,
    NDL_SEARCH_CYCLE_FILENAME,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_format_slideshow_side_cursor_chip() -> None:
    assert format_slideshow_side_cursor_chip("L", SlideshowSideCursorDisplay("2/29")) == "L: 2/29"
    assert format_slideshow_side_cursor_chip("R", None) == ""


def test_format_local_dir_cursor(tmp_path: Path) -> None:
    source_dir = tmp_path / "local"
    source_dir.mkdir()
    images = [source_dir / f"{index}.jpg" for index in range(1, 6)]
    for image in images:
        image.write_bytes(b"jpeg")

    class Owner:
        _slideshow_state_l = SlideshowCycleState(previous_selected=images[1])

    catalog = empty_catalog()
    display = format_side_cursor_display(
        entry=None,
        source_dir=source_dir,
        owner=Owner(),
        side="L",
    )
    assert display is not None
    assert display.label == "2/5"


def test_format_codh_cursor(tmp_path: Path) -> None:
    catalog = empty_catalog()
    cache = tmp_path / "cache"
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache)
    cache_dir = Path(entry.path)
    _write_json(
        cache_dir / CODH_INDEX_FILENAME,
        {"version": 1, "entries": [{"id": "a"}, {"id": "b"}, {"id": "c"}]},
    )
    _write_json(cache_dir / CODH_CYCLE_FILENAME, {"index": 1})

    display = format_side_cursor_display(entry=entry, source_dir=cache_dir, owner=object(), side="L")
    assert display is not None
    assert display.label == "2/3"


def test_format_jma_cursor_shows_filename(tmp_path: Path) -> None:
    from harite.gui.views.slideshow_cursor_position import format_jma_filename_for_chip

    catalog = empty_catalog()
    cache = tmp_path / "cache"
    entry = import_preset_source(catalog, "jma-near-color", cache_root=cache)
    cache_dir = Path(entry.path)
    _write_json(
        cache_dir / JMA_CYCLE_FILENAME,
        {"preset_id": "jma-near-color", "filename": "2026053112.png"},
    )

    display = format_side_cursor_display(entry=entry, source_dir=cache_dir, owner=object(), side="R")
    assert display is not None
    assert display.label == "2026053112.png"
    assert display.tooltip == "2026053112.png"

    long_name = "20260531120000.png"
    assert format_jma_filename_for_chip(long_name) == "…531120000.png"
    _write_json(
        cache_dir / JMA_CYCLE_FILENAME,
        {"preset_id": "jma-near-color", "filename": long_name},
    )
    display = format_side_cursor_display(entry=entry, source_dir=cache_dir, owner=object(), side="R")
    assert display is not None
    assert display.label == "…531120000.png"
    assert display.tooltip == long_name


def test_format_kiriezu_cursor(tmp_path: Path) -> None:
    catalog = empty_catalog()
    cache = tmp_path / "cache"
    entry = import_preset_source(catalog, "ndl-kiriezu-asakusa", cache_root=cache)
    cache_dir = Path(entry.path)
    _write_json(
        cache_dir / NDL_KIRIEZU_CYCLE_FILENAME,
        {"preset_id": "ndl-kiriezu-asakusa", "cursor_index": 0},
    )

    display = format_side_cursor_display(entry=entry, source_dir=cache_dir, owner=object(), side="L")
    assert display is not None
    assert display.label == "1/2"


def test_format_ndl_keyword_cursor_with_tooltip(tmp_path: Path) -> None:
    from harite.settings_file import save_settings

    catalog = empty_catalog()
    cache = tmp_path / "cache"
    entry = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache)
    cache_dir = Path(entry.path)
    settings_path = tmp_path / "harite-settings.json"
    save_settings(settings_path, {"ndl_keyword": "ペンギン"})
    _write_json(
        cache_dir / NDL_SEARCH_BATCH_FILENAME,
        {
            "keyword": "ペンギン",
            "hit": 42,
            "entries": [{"pid": "a"}, {"pid": "b"}, {"pid": "c"}],
        },
    )
    _write_json(
        cache_dir / NDL_SEARCH_CYCLE_FILENAME,
        {"keyword_key": "ペンギン", "cursor_index": 2, "from": 0},
    )

    class Owner:
        _settings_path = settings_path

    display = format_side_cursor_display(entry=entry, source_dir=cache_dir, owner=Owner(), side="R")
    assert display is not None
    assert display.label == "3/3"
    assert display.tooltip == "search hit 42"


def test_refresh_slideshow_cursor_position_chips(qapp, tmp_path: Path) -> None:
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_cursor_position_chips

    catalog = empty_catalog()
    cache = tmp_path / "cache"
    entry = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache)
    cache_dir = Path(entry.path)
    _write_json(
        cache_dir / CODH_INDEX_FILENAME,
        {"version": 1, "entries": [{"id": "a"}, {"id": "b"}]},
    )
    _write_json(cache_dir / CODH_CYCLE_FILENAME, {"index": 0})
    catalog_path = tmp_path / "harite-sources.json"
    save_catalog(catalog, catalog_path)

    class Owner:
        slideshow_source_id_l = entry.id
        slideshow_source_id_r = ""
        slideshow_profile_id = ""
        _source_catalog_path = catalog_path
        _source_catalog_cache = catalog
        _source_catalog_cache_mtime = catalog_path.stat().st_mtime

    chip_l = QLabel("")
    chip_r = QLabel("")
    backend = type(
        "Backend",
        (),
        {"_objects": {"lblSlideshowCursorL": chip_l, "lblSlideshowCursorR": chip_r}},
    )()

    refresh_slideshow_cursor_position_chips(backend, Owner())
    assert chip_l.isVisible()
    assert chip_l.text() == "L: 1/2"
    assert not chip_r.isVisible()

    Owner.slideshow_source_id_l = ""
    refresh_slideshow_cursor_position_chips(backend, Owner())
    assert not chip_l.isVisible()
    assert chip_l.text() == ""


def test_resolve_slideshow_cursor_displays_profile_members(tmp_path: Path) -> None:
    from harite.sources import add_profile, add_source

    catalog = empty_catalog()
    cache = tmp_path / "cache"
    codh = import_preset_source(catalog, "codh-edo-spots-random", cache_root=cache)
    codh_dir = Path(codh.path)
    _write_json(
        codh_dir / CODH_INDEX_FILENAME,
        {"version": 1, "entries": [{"id": "a"}, {"id": "b"}, {"id": "c"}]},
    )
    _write_json(codh_dir / CODH_CYCLE_FILENAME, {"index": 2})

    local_dir = tmp_path / "local"
    local_dir.mkdir()
    for index in range(1, 4):
        (local_dir / f"{index}.jpg").write_bytes(b"jpeg")
    local = add_source(catalog, name="Local", path=local_dir)
    profile = add_profile(catalog, name="Mixed", members={"L": codh.id, "R": local.id})

    class Owner:
        slideshow_profile_id = profile.id
        slideshow_srcdir_l = codh.path
        slideshow_srcdir_r = local.path
        _slideshow_state_r = SlideshowCycleState(previous_selected=local_dir / "2.jpg")

    left, right = resolve_slideshow_cursor_displays(catalog, Owner())
    assert left is not None and left.label == "3/3"
    assert right is not None and right.label == "2/3"

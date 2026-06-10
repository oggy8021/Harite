"""MAT-18: Slideshow NDL keyword read-only chip."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from harite.gui.views.slideshow_ndl_keyword_chip import (
    format_slideshow_ndl_keyword_chip,
    slideshow_uses_ndl_keyword_preset,
)
from harite.sources import add_profile, add_source, empty_catalog, import_preset_source


def test_format_slideshow_ndl_keyword_chip() -> None:
    assert format_slideshow_ndl_keyword_chip("ペンギン") == "NDL: ペンギン"
    assert format_slideshow_ndl_keyword_chip("  ") == ""


def test_slideshow_uses_ndl_keyword_preset_direct_selection(tmp_path: Path) -> None:
    catalog = empty_catalog()
    cache = tmp_path / "cache"
    keyword_source = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache)
    facet_source = import_preset_source(catalog, "ndl-random-illust", cache_root=cache)

    assert slideshow_uses_ndl_keyword_preset(
        catalog=catalog,
        source_id_l=keyword_source.id,
        source_id_r="",
        profile_id="",
    )
    assert not slideshow_uses_ndl_keyword_preset(
        catalog=catalog,
        source_id_l=facet_source.id,
        source_id_r="",
        profile_id="",
    )


def test_slideshow_uses_ndl_keyword_preset_via_profile(tmp_path: Path) -> None:
    catalog = empty_catalog()
    cache = tmp_path / "cache"
    keyword_source = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache)
    local_dir = tmp_path / "local"
    local_dir.mkdir()
    local_source = add_source(catalog, name="Local", path=local_dir)
    profile = add_profile(
        catalog,
        name="Mixed",
        members={"L": keyword_source.id, "R": local_source.id},
    )

    assert slideshow_uses_ndl_keyword_preset(
        catalog=catalog,
        source_id_l="",
        source_id_r="",
        profile_id=profile.id,
    )


def test_refresh_slideshow_ndl_keyword_chip_shows_and_hides(qapp, tmp_path: Path) -> None:
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_ndl_keyword_chip
    from harite.settings_file import save_settings
    from harite.sources import save_catalog

    catalog = empty_catalog()
    cache = tmp_path / "cache"
    keyword_source = import_preset_source(catalog, "ndl-search-keyword", cache_root=cache)
    catalog_path = tmp_path / "harite-sources.json"
    save_catalog(catalog, catalog_path)
    settings_path = tmp_path / "harite-settings.json"
    save_settings(settings_path, {"ndl_keyword": "ペンギン"})

    class Owner:
        slideshow_source_id_l = keyword_source.id
        slideshow_source_id_r = ""
        slideshow_profile_id = ""
        _source_catalog_path = catalog_path
        _source_catalog_cache = catalog
        _source_catalog_cache_mtime = catalog_path.stat().st_mtime
        _settings_path = settings_path

    chip = QLabel("")
    backend = type("Backend", (), {"_objects": {"lblSlideshowNdlKeyword": chip}})()

    refresh_slideshow_ndl_keyword_chip(backend, Owner())
    assert chip.isVisible()
    assert chip.text() == "NDL: ペンギン"

    Owner.slideshow_source_id_l = ""
    refresh_slideshow_ndl_keyword_chip(backend, Owner())
    assert not chip.isVisible()
    assert chip.text() == ""

"""C-02: Slideshow source registry GUI handlers (gui-spec §4.2)."""

from __future__ import annotations

from pathlib import Path

from harite.gui.adapters.ui_adapter import RUNTIME_HANDLER_MAP
from harite.gui.views.main_window import MainWindow
from harite.sources import add_profile, add_source, empty_catalog, save_catalog

C02_HANDLERS = (
    "on_select_slideshow_source",
    "on_select_slideshow_profile",
    "on_manage_source_registry",
)


def _write_catalog(path: Path, left: Path, right: Path) -> tuple[str, str, str]:
    catalog = empty_catalog()
    left_entry = add_source(catalog, name="Left NAS", path=left)
    right_entry = add_source(catalog, name="Right Cloud", path=right)
    profile = add_profile(
        catalog,
        name="Dual",
        members={"L": left_entry.id, "R": right_entry.id},
    )
    save_catalog(catalog, path)
    return left_entry.id, right_entry.id, profile.id


def test_runtime_handler_map_includes_c02_handlers():
    for handler_name in C02_HANDLERS:
        assert handler_name in RUNTIME_HANDLER_MAP


def test_on_select_slideshow_source_sets_path_and_id(tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    catalog_path = tmp_path / "sources.json"
    left_id, _, _ = _write_catalog(catalog_path, left_dir, right_dir)

    window = MainWindow()
    window._source_catalog_path = catalog_path

    assert window.on_select_slideshow_source("L", left_id) is True
    assert window.slideshow_srcdir_l == str(left_dir.resolve())
    assert window.slideshow_source_id_l == left_id
    assert window.slideshow_profile_id == ""


def test_on_select_slideshow_source_none_clears_id_only(tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    catalog_path = tmp_path / "sources.json"
    left_id, _, _ = _write_catalog(catalog_path, left_dir, right_dir)

    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_source("L", left_id)

    assert window.on_select_slideshow_source("L", None) is True
    assert window.slideshow_source_id_l == ""
    assert window.slideshow_srcdir_l == str(left_dir.resolve())


def test_on_pick_slideshow_srcdir_clears_saved_source_tracking(tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    browse_dir = tmp_path / "browse"
    left_dir.mkdir()
    right_dir.mkdir()
    browse_dir.mkdir()
    catalog_path = tmp_path / "sources.json"
    _, _, profile_id = _write_catalog(catalog_path, left_dir, right_dir)

    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_profile(profile_id)
    assert window.slideshow_profile_id == profile_id

    assert window.on_pick_slideshow_srcdir(str(browse_dir), "L") is True
    assert window.slideshow_srcdir_l == str(browse_dir)
    assert window.slideshow_source_id_l == ""
    assert window.slideshow_profile_id == ""


def test_on_select_slideshow_profile_applies_lr(tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    catalog_path = tmp_path / "sources.json"
    left_id, right_id, profile_id = _write_catalog(catalog_path, left_dir, right_dir)

    window = MainWindow()
    window._source_catalog_path = catalog_path

    assert window.on_select_slideshow_profile(profile_id) is True
    assert window.slideshow_srcdir_l == str(left_dir.resolve())
    assert window.slideshow_srcdir_r == str(right_dir.resolve())
    assert window.slideshow_source_id_l == left_id
    assert window.slideshow_source_id_r == right_id
    assert window.slideshow_profile_id == profile_id


def test_on_swap_slideshow_srcdirs_swaps_tracking_ids(tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    catalog_path = tmp_path / "sources.json"
    left_id, right_id, profile_id = _write_catalog(catalog_path, left_dir, right_dir)

    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_profile(profile_id)

    window.on_swap_slideshow_srcdirs()

    assert window.slideshow_source_id_l == right_id
    assert window.slideshow_source_id_r == left_id
    assert window.slideshow_profile_id == ""


def test_on_clear_slideshow_srcdir_clears_tracking(tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    catalog_path = tmp_path / "sources.json"
    left_id, _, _ = _write_catalog(catalog_path, left_dir, right_dir)

    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_source("L", left_id)

    assert window.on_clear_slideshow_srcdir("L") is True
    assert window.slideshow_srcdir_l == ""
    assert window.slideshow_source_id_l == ""


def test_export_settings_includes_registry_tracking_keys(tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    catalog_path = tmp_path / "sources.json"
    left_id, right_id, profile_id = _write_catalog(catalog_path, left_dir, right_dir)

    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_profile(profile_id)

    exported = window.export_settings()
    assert exported["slideshow_source_id_l"] == left_id
    assert exported["slideshow_source_id_r"] == right_id
    assert exported["slideshow_profile_id"] == profile_id


def test_load_settings_restores_registry_tracking(tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    left_id, right_id, profile_id = _write_catalog(tmp_path / "sources.json", left_dir, right_dir)

    settings = {
        "slideshow_srcdir_l": str(left_dir),
        "slideshow_srcdir_r": str(right_dir),
        "slideshow_source_id_l": left_id,
        "slideshow_source_id_r": right_id,
        "slideshow_profile_id": profile_id,
        "slideshow_interval_seconds": 60,
        "slideshow_mode": "random",
    }
    window = MainWindow()
    assert window.load_settings(settings) is True
    assert window.slideshow_source_id_l == left_id
    assert window.slideshow_profile_id == profile_id

"""C-05: slideshow start resolve and catalog change during run (source-spec §6.4, §7.6)."""

from __future__ import annotations

from pathlib import Path

import pytest

from harite.gui.adapters.ui_adapter import RUNTIME_HANDLER_MAP
from harite.gui.views.main_window import MainWindow
from harite.sources import (
    add_profile,
    add_source,
    delete_source,
    empty_catalog,
    load_catalog,
    save_catalog,
    update_source,
)


def _install_dummy_plugin(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    monkeypatch.setattr(
        "harite.gui.views.main_window.plugin_registry.get",
        lambda _name: DummyPlugin(),
    )


def _write_dual_catalog(path: Path, left: Path, right: Path) -> tuple[str, str, str]:
    catalog = empty_catalog()
    left_entry = add_source(catalog, name="Left", path=left)
    right_entry = add_source(catalog, name="Right", path=right)
    profile = add_profile(
        catalog,
        name="Dual",
        members={"L": left_entry.id, "R": right_entry.id},
    )
    save_catalog(catalog, path)
    return left_entry.id, right_entry.id, profile.id


def _prepare_dual_window(
    tmp_path: Path,
    *,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[MainWindow, Path, str, str, str]:
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left.jpg").write_bytes(b"L")
    (right_dir / "right.jpg").write_bytes(b"R")
    catalog_path = tmp_path / "harite-sources.json"
    left_id, right_id, profile_id = _write_dual_catalog(catalog_path, left_dir, right_dir)
    _install_dummy_plugin(monkeypatch)
    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_profile(profile_id)
    return window, catalog_path, left_id, right_id, profile_id


def test_runtime_handler_map_includes_c05_catalog_saved():
    assert "on_source_catalog_saved" in RUNTIME_HANDLER_MAP


def test_start_re_resolves_stale_srcdir_from_catalog(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    left_dir = tmp_path / "left"
    left_dir.mkdir()
    (left_dir / "old.jpg").write_bytes(b"old")
    catalog_path = tmp_path / "sources.json"
    catalog = empty_catalog()
    left_entry = add_source(catalog, name="Left", path=left_dir)
    save_catalog(catalog, catalog_path)

    new_dir = tmp_path / "left-new"
    new_dir.mkdir()
    (new_dir / "new.jpg").write_bytes(b"new")

    _install_dummy_plugin(monkeypatch)
    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_source("L", left_entry.id)
    window.slideshow_srcdir_r = str((tmp_path / "right-placeholder").resolve())
    (tmp_path / "right-placeholder").mkdir()
    (tmp_path / "right-placeholder" / "r.jpg").write_bytes(b"R")

    catalog = load_catalog(catalog_path)
    update_source(catalog, left_entry.id, path=new_dir)
    save_catalog(catalog, catalog_path)
    window.slideshow_srcdir_l = str(left_dir.resolve())

    assert window.on_slideshow_start() is True
    assert window.slideshow_srcdir_l == str(new_dir.resolve())
    assert "new.jpg" in window.slideshow_current_display


def test_start_fails_when_tracked_source_removed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "l.jpg").write_bytes(b"L")
    (right_dir / "r.jpg").write_bytes(b"R")
    catalog_path = tmp_path / "sources.json"
    catalog = empty_catalog()
    left_entry = add_source(catalog, name="Left", path=left_dir)
    right_entry = add_source(catalog, name="Right", path=right_dir)
    save_catalog(catalog, catalog_path)
    left_id = left_entry.id
    right_id = right_entry.id

    _install_dummy_plugin(monkeypatch)
    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_source("L", left_id)
    window.on_select_slideshow_source("R", right_id)

    catalog = load_catalog(catalog_path)
    delete_source(catalog, left_id)
    save_catalog(catalog, catalog_path)

    assert window.on_slideshow_start() is False
    assert window.slideshow_running is False
    assert "resolve failed" in window.status_message.lower() or "unknown" in (window.last_error or "").lower()


def test_catalog_path_change_stops_running_slideshow(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    window, catalog_path, left_id, _, _ = _prepare_dual_window(tmp_path, monkeypatch=monkeypatch)
    assert window.on_slideshow_start() is True

    new_left = tmp_path / "left-moved"
    new_left.mkdir()
    (new_left / "moved.jpg").write_bytes(b"M")
    catalog = load_catalog(catalog_path)
    update_source(catalog, left_id, path=new_left)
    save_catalog(catalog, catalog_path)

    assert window.on_source_catalog_saved() is True
    assert window.slideshow_running is False
    assert "catalog changed" in window.status_message


def test_catalog_notes_change_does_not_stop_running_slideshow(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    window, catalog_path, left_id, _, _ = _prepare_dual_window(tmp_path, monkeypatch=monkeypatch)
    assert window.on_slideshow_start() is True

    catalog = load_catalog(catalog_path)
    update_source(catalog, left_id, notes="updated notes only")
    save_catalog(catalog, catalog_path)

    assert window.on_source_catalog_saved() is True
    assert window.slideshow_running is True


def test_manual_srcdir_without_source_id_still_starts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "l.jpg").write_bytes(b"L")
    (right_dir / "r.jpg").write_bytes(b"R")

    _install_dummy_plugin(monkeypatch)
    window = MainWindow()
    window.on_pick_slideshow_srcdir(str(left_dir), "L")
    window.on_pick_slideshow_srcdir(str(right_dir), "R")
    assert window.slideshow_source_id_l == ""
    assert window.slideshow_source_id_r == ""

    assert window.on_slideshow_start() is True
    assert window.slideshow_running is True

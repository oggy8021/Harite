"""C-01 phase 4: Qt preset bootstrap, combo labels, interval floor."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from harite.gui.adapters_qt.qt_source_catalog import (
    prepare_owner_source_catalog,
    slideshow_profile_combo_label,
    slideshow_source_combo_label,
)
from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_registry_combos
from harite.gui.views.main_window import MainWindow
from harite.sources import bootstrap_preset_sources, empty_catalog, save_catalog


class _FakeBackend:
    def __init__(self) -> None:
        self._objects: dict = {}


def _normalize_combo_data(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def test_slideshow_source_combo_label_marks_presets(tmp_path: Path) -> None:
    from harite.sources import import_preset_source

    catalog = empty_catalog()
    entry = import_preset_source(catalog, "jma-near-color", cache_root=tmp_path / "cache")
    assert slideshow_source_combo_label(entry) == "*気象庁（日本付近）"


def test_refresh_registry_combos_shows_preset_star_labels(qapp, tmp_path: Path) -> None:
    from PyQt6.QtWidgets import QComboBox

    cache_root = tmp_path / "remote-cache"
    catalog_path = tmp_path / "harite-sources.json"
    catalog = empty_catalog()
    bootstrap_preset_sources(catalog, cache_root=cache_root, sync=False)
    save_catalog(catalog, catalog_path)

    owner = MainWindow()
    owner._source_catalog_path = catalog_path
    backend = _FakeBackend()
    backend._objects["combo_slideshow_profile"] = QComboBox()
    backend._objects["combo_slideshow_source_l"] = QComboBox()
    backend._objects["combo_slideshow_source_r"] = QComboBox()

    refresh_slideshow_registry_combos(backend, owner)

    source_l = backend._objects["combo_slideshow_source_l"]
    labels = [source_l.itemText(i) for i in range(source_l.count())]
    assert "*気象庁（日本付近）" in labels
    assert "*気象庁（アジア域）" in labels

    profile_combo = backend._objects["combo_slideshow_profile"]
    profile_labels = [profile_combo.itemText(i) for i in range(profile_combo.count())]
    assert "*気象庁 L/R" in profile_labels


def test_prepare_owner_source_catalog_materializes_presets(tmp_path: Path) -> None:
    catalog_path = tmp_path / "harite-sources.json"
    save_catalog(empty_catalog(), catalog_path)

    owner = MainWindow()
    owner._source_catalog_path = catalog_path
    catalog = prepare_owner_source_catalog(owner)

    assert any("気象庁" in entry.name for entry in catalog.sources)
    assert catalog.profiles


def test_profile_select_raises_interval_to_preset_floor(tmp_path: Path) -> None:
    cache_root = tmp_path / "remote-cache"
    catalog_path = tmp_path / "harite-sources.json"
    catalog = empty_catalog()
    bootstrap_preset_sources(catalog, cache_root=cache_root, sync=False)
    save_catalog(catalog, catalog_path)
    profile_id = catalog.profiles[0].id

    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.slideshow_interval_seconds = 30

    assert window.on_select_slideshow_profile(profile_id) is True
    assert window.slideshow_interval_seconds == 600


def test_slideshow_profile_combo_label_detects_preset_profile(tmp_path: Path) -> None:
    cache_root = tmp_path / "remote-cache"
    catalog = empty_catalog()
    bootstrap_preset_sources(catalog, cache_root=cache_root, sync=False)
    profile = catalog.profiles[0]
    assert slideshow_profile_combo_label(catalog, profile) == "*気象庁 L/R"

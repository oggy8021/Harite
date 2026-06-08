"""P-05: Manage dialog local / preset panel helpers."""

from __future__ import annotations

from pathlib import Path

from harite.gui.adapters_qt.qt_source_registry_dialog import (
    _LIST_HEADER_MARKER,
    catalog_sources_for_selection_combo,
    local_sources_for_manage_dialog,
    preset_list_rows_for_manage_dialog,
    preset_provider_group,
)
from harite.sources import add_source, empty_catalog, import_preset_source


def test_local_sources_for_manage_dialog_sorts_by_name(tmp_path: Path) -> None:
    catalog = empty_catalog()
    zebra = tmp_path / "z"
    alpha = tmp_path / "a"
    zebra.mkdir()
    alpha.mkdir()
    add_source(catalog, name="Zebra", path=zebra)
    add_source(catalog, name="alpha", path=alpha)

    names = [entry.name for entry in local_sources_for_manage_dialog(catalog)]
    assert names == ["alpha", "Zebra"]


def test_preset_list_rows_group_and_sort(tmp_path: Path) -> None:
    catalog = empty_catalog()
    cache = tmp_path / "cache"
    codh = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=cache)
    jma = import_preset_source(catalog, "jma-near-color", cache_root=cache)
    ndl = import_preset_source(catalog, "ndl-random-map", cache_root=cache)
    local_dir = tmp_path / "local"
    local_dir.mkdir()
    add_source(catalog, name="Local only", path=local_dir)

    rows = preset_list_rows_for_manage_dialog(catalog)
    labels = [row.label for row in rows]
    source_ids = [row.source_id for row in rows]

    assert "Local only" not in labels
    assert "JMA 天気図" in labels
    assert "NDL 図版" in labels
    assert "CODH 江戸" in labels
    assert labels.index("JMA 天気図") < labels.index("NDL 図版") < labels.index("CODH 江戸")
    assert jma.id in source_ids
    assert ndl.id in source_ids
    assert codh.id in source_ids
    assert preset_provider_group(jma) == "JMA 天気図"
    assert preset_provider_group(ndl) == "NDL 図版"
    assert preset_provider_group(codh) == "CODH 江戸"


def test_catalog_sources_for_selection_combo_orders_local_then_presets(tmp_path: Path) -> None:
    catalog = empty_catalog()
    cache = tmp_path / "cache"
    codh = import_preset_source(catalog, "codh-edo-spots-keyword", cache_root=cache)
    jma = import_preset_source(catalog, "jma-near-color", cache_root=cache)
    ndl = import_preset_source(catalog, "ndl-random-map", cache_root=cache)
    zebra = tmp_path / "z"
    alpha = tmp_path / "a"
    zebra.mkdir()
    alpha.mkdir()
    local_z = add_source(catalog, name="Zebra", path=zebra)
    local_a = add_source(catalog, name="alpha", path=alpha)

    ordered = catalog_sources_for_selection_combo(catalog)
    assert [entry.id for entry in ordered] == [
        local_a.id,
        local_z.id,
        jma.id,
        ndl.id,
        codh.id,
    ]

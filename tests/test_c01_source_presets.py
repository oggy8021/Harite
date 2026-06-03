"""C-01 phase 2: bundled presets, import, bootstrap, interval floor."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from harite.sources import (
    catalog_slideshow_interval_floor,
    empty_catalog,
    import_preset_profile,
    import_preset_source,
    load_source_presets,
    preset_min_slideshow_interval,
)
from harite.sources_preset import (
    bootstrap_preset_sources,
    find_catalog_source_for_preset,
    min_interval_from_notes,
    preset_catalog_from_dict,
)
from harite.sources_remote import (
    KIND_JMA_WEATHER_MAP,
    is_remote_kind,
    preset_id_from_notes,
)


def test_load_bundled_jma_presets() -> None:
    presets = load_source_presets()
    assert presets.preset_schema_version == 1
    ids = {template.preset_id for template in presets.sources}
    assert ids == {
        "jma-near-color",
        "jma-asia-color",
        "jma-near-monochrome",
        "jma-asia-monochrome",
    }
    profile_ids = {template.preset_id for template in presets.profiles}
    assert profile_ids == {"jma-dual-lr"}
    for template in presets.sources:
        assert template.kind == KIND_JMA_WEATHER_MAP
        assert template.min_slideshow_interval_seconds == 600


def test_import_preset_source_writes_marker_and_interval(tmp_path: Path) -> None:
    cache_root = tmp_path / "cache"
    catalog = empty_catalog()
    presets = load_source_presets()

    entry = import_preset_source(
        catalog,
        "jma-near-color",
        preset_catalog=presets,
        cache_root=cache_root,
    )

    assert entry.kind == KIND_JMA_WEATHER_MAP
    assert preset_id_from_notes(entry.notes) == "jma-near-color"
    assert min_interval_from_notes(entry.notes) == 600
    assert "出典" in entry.notes
    assert Path(entry.path).parent == cache_root


def test_import_preset_profile_resolves_member_presets(tmp_path: Path) -> None:
    cache_root = tmp_path / "cache"
    catalog = empty_catalog()
    presets = load_source_presets()

    profile = import_preset_profile(
        catalog,
        "jma-dual-lr",
        preset_catalog=presets,
        cache_root=cache_root,
    )

    assert profile.name == "気象庁 L/R"
    assert profile.members.L is not None
    assert profile.members.R is not None
    left = find_catalog_source_for_preset(catalog, "jma-near-color")
    right = find_catalog_source_for_preset(catalog, "jma-asia-color")
    assert left is not None and right is not None
    assert profile.members.L == left.id
    assert profile.members.R == right.id


def test_bootstrap_materializes_missing_presets(tmp_path: Path) -> None:
    cache_root = tmp_path / "cache"
    catalog = empty_catalog()

    changed = bootstrap_preset_sources(catalog, cache_root=cache_root, sync=False)

    assert changed is True
    for preset_id in (
        "jma-near-color",
        "jma-asia-color",
        "jma-near-monochrome",
        "jma-asia-monochrome",
    ):
        assert find_catalog_source_for_preset(catalog, preset_id) is not None
    assert len(catalog.profiles) == 1

    changed_again = bootstrap_preset_sources(catalog, cache_root=cache_root, sync=False)
    assert changed_again is False


def test_catalog_slideshow_interval_floor_from_profile(tmp_path: Path) -> None:
    cache_root = tmp_path / "cache"
    catalog = empty_catalog()
    import_preset_profile(catalog, "jma-dual-lr", cache_root=cache_root)
    profile = catalog.profiles[0]

    floor = catalog_slideshow_interval_floor(catalog, profile_id=profile.id)
    assert floor == 600


def test_preset_min_slideshow_interval_profile_uses_member_max() -> None:
    presets = load_source_presets()
    assert preset_min_slideshow_interval(presets, "jma-dual-lr") == 600


def test_preset_catalog_rejects_unsupported_schema_version() -> None:
    with pytest.raises(ValueError, match="unsupported preset_schema_version"):
        preset_catalog_from_dict({"preset_schema_version": 99, "sources": []})


def test_is_remote_kind_matches_spec_pattern() -> None:
    assert is_remote_kind("remote-jma-weather-map")
    assert not is_remote_kind("local-dir")
    assert not is_remote_kind("remote-INVALID")


def test_load_catalog_accepts_remote_without_cache_dir(tmp_path: Path) -> None:
    from harite.sources import catalog_from_dict, load_catalog

    catalog_path = tmp_path / "harite-sources.json"
    missing_cache = tmp_path / "cache" / "00000000-0000-4000-8000-000000000001"
    payload = {
        "schema_version": 1,
        "sources": [
            {
                "id": "00000000-0000-4000-8000-000000000001",
                "name": "JMA",
                "kind": KIND_JMA_WEATHER_MAP,
                "path": str(missing_cache),
                "notes": "harite-preset:jma-near-color",
            }
        ],
        "profiles": [],
    }
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    loaded = load_catalog(catalog_path)
    assert loaded.sources[0].kind == KIND_JMA_WEATHER_MAP

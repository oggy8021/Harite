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
    canonical_preset_source_notes,
    find_catalog_profile_for_preset,
    find_catalog_source_for_preset,
    min_interval_from_notes,
    preset_catalog_from_dict,
    repair_preset_profile_members,
    repair_preset_source_notes,
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


def test_format_preset_notes_does_not_duplicate_harite_preset_marker() -> None:
    presets = load_source_presets()
    template = next(t for t in presets.sources if t.preset_id == "jma-near-color")
    notes = canonical_preset_source_notes(template)
    assert notes.count("harite-preset:jma-near-color") == 1
    assert notes.count("harite-min-interval:600") == 1
    assert "出典" in notes


def test_repair_preset_source_notes_fixes_duplicated_markers(tmp_path: Path) -> None:
    from harite.sources import add_remote_source, empty_catalog, save_catalog

    presets = load_source_presets()
    template = next(t for t in presets.sources if t.preset_id == "jma-near-color")
    catalog = empty_catalog()
    entry = add_remote_source(
        catalog,
        name=template.name,
        kind=template.kind,
        notes=(
            "harite-preset:jma-near-color\n"
            "harite-preset:jma-near-color\n"
            "出典：気象庁ホームページ（https://www.jma.go.jp/）\n"
            "harite-min-interval:600"
        ),
        cache_root=tmp_path / "cache",
    )
    assert repair_preset_source_notes(catalog, preset_catalog=presets) is True
    assert entry.notes == canonical_preset_source_notes(template)


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


def test_repair_preset_profile_members_fixes_stale_source_ids(tmp_path: Path) -> None:
    from harite.sources import ProfileMembers, empty_catalog

    presets = load_source_presets()
    cache_root = tmp_path / "cache"
    catalog = empty_catalog()
    import_preset_source(catalog, "jma-near-color", cache_root=cache_root)
    asia = import_preset_source(catalog, "jma-asia-color", cache_root=cache_root)
    import_preset_profile(catalog, "jma-dual-lr", cache_root=cache_root)
    profile = find_catalog_profile_for_preset(catalog, "jma-dual-lr", preset_catalog=presets)
    assert profile is not None
    profile.members = ProfileMembers(L="00000000-0000-0000-0000-000000000099", R=asia.id)

    assert repair_preset_profile_members(catalog, preset_catalog=presets) is True
    near_live = find_catalog_source_for_preset(catalog, "jma-near-color")
    assert near_live is not None
    assert profile.members.L == near_live.id
    assert profile.members.R == asia.id


def test_materialize_loads_catalog_with_broken_profile_refs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import json

    from harite.gui.adapters_qt.qt_source_catalog import materialize_source_catalog_at_path
    from harite.sources import load_catalog
    from harite.sources_file import save_sources_json

    catalog_path = tmp_path / "harite-sources.json"
    near_id = "89164503-d394-49e0-b3e0-7d4e0b860733"
    save_sources_json(
        catalog_path,
        {
            "schema_version": 1,
            "sources": [
                {
                    "id": near_id,
                    "name": "気象庁（日本付近）",
                    "kind": "remote-jma-weather-map",
                    "path": str(tmp_path / "cache" / near_id),
                    "notes": "harite-preset:jma-near-color\n出典：気象庁",
                }
            ],
            "profiles": [
                {
                    "id": "prof-1",
                    "name": "気象庁 L/R",
                    "members": {"L": near_id, "R": "missing-id"},
                }
            ],
        },
    )

    def _noop_sync(_catalog: object, _source_id: str, **kwargs: object) -> None:
        return None

    monkeypatch.setattr("harite.sources_remote.sync_remote_source", _noop_sync)

    materialize_source_catalog_at_path(catalog_path)
    load_catalog(catalog_path)


def test_materialize_repairs_notes_and_saves_catalog(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from harite.gui.adapters_qt.qt_source_catalog import materialize_source_catalog_at_path
    from harite.sources import add_remote_source, empty_catalog, load_catalog, save_catalog

    presets = load_source_presets()
    template = next(t for t in presets.sources if t.preset_id == "jma-near-color")
    catalog_path = tmp_path / "harite-sources.json"
    catalog = empty_catalog()
    add_remote_source(
        catalog,
        name=template.name,
        kind=template.kind,
        notes="harite-preset:jma-near-color\nharite-preset:jma-near-color\n出典：気象庁",
        cache_root=tmp_path / "cache",
    )
    save_catalog(catalog, catalog_path)

    def _noop_sync(_catalog: object, _source_id: str, **kwargs: object) -> None:
        return None

    monkeypatch.setattr("harite.sources_remote.sync_remote_source", _noop_sync)

    materialize_source_catalog_at_path(catalog_path)
    reloaded = load_catalog(catalog_path)
    entry = find_catalog_source_for_preset(reloaded, "jma-near-color")
    assert entry is not None
    assert entry.notes == canonical_preset_source_notes(template)


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

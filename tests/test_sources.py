from __future__ import annotations

import json
from pathlib import Path

import pytest

from harite.sources import (
    MAX_NAME_LEN,
    MAX_NOTES_LEN,
    MAX_PROFILES,
    MAX_SOURCES,
    SCHEMA_VERSION,
    add_profile,
    add_source,
    catalog_from_dict,
    delete_profile,
    delete_source,
    empty_catalog,
    get_profile,
    get_source,
    load_catalog,
    normalize_directory_path,
    resolve_profile_members,
    resolve_source,
    save_catalog,
    update_profile,
    update_source,
)


@pytest.fixture
def left_dir(tmp_path: Path) -> Path:
    path = tmp_path / "left"
    path.mkdir()
    return path


@pytest.fixture
def right_dir(tmp_path: Path) -> Path:
    path = tmp_path / "right"
    path.mkdir()
    return path


def test_load_catalog_missing_file_returns_empty(tmp_path: Path) -> None:
    catalog = load_catalog(tmp_path / "missing.json")
    assert catalog.schema_version == SCHEMA_VERSION
    assert catalog.sources == []
    assert catalog.profiles == []


def test_save_and_load_roundtrip(tmp_path: Path, left_dir: Path, right_dir: Path) -> None:
    catalog_path = tmp_path / "sources.json"
    catalog = empty_catalog()
    left = add_source(catalog, name="Left", path=left_dir)
    right = add_source(catalog, name="Right", path=right_dir)
    add_profile(catalog, name="Dual", members={"L": left.id, "R": right.id})

    save_catalog(catalog, catalog_path)
    loaded = load_catalog(catalog_path)

    assert len(loaded.sources) == 2
    assert len(loaded.profiles) == 1
    assert loaded.profiles[0].members.L == left.id
    assert loaded.profiles[0].members.R == right.id


def test_add_source_normalizes_absolute_path(left_dir: Path) -> None:
    catalog = empty_catalog()
    entry = add_source(catalog, name="Wallpapers", path=left_dir)

    assert entry.kind == "local-dir"
    assert entry.path == str(left_dir.resolve())
    assert normalize_directory_path(entry.path) == left_dir.resolve()


def test_add_source_rejects_missing_directory(tmp_path: Path) -> None:
    catalog = empty_catalog()
    missing = tmp_path / "missing"

    with pytest.raises(ValueError, match="existing directory"):
        add_source(catalog, name="Ghost", path=missing)


def test_add_source_rejects_duplicate_name(left_dir: Path) -> None:
    catalog = empty_catalog()
    add_source(catalog, name="Same", path=left_dir)

    with pytest.raises(ValueError, match="duplicate source name"):
        add_source(catalog, name="Same", path=left_dir)


def test_profile_and_source_may_share_display_name(left_dir: Path, right_dir: Path) -> None:
    catalog = empty_catalog()
    source = add_source(catalog, name="Shared", path=left_dir)
    profile = add_profile(catalog, name="Shared", members={"L": source.id, "R": None})

    assert source.name == profile.name


def test_add_source_enforces_count_limit(tmp_path: Path) -> None:
    catalog = empty_catalog()
    for index in range(MAX_SOURCES):
        directory = tmp_path / f"src{index}"
        directory.mkdir()
        add_source(catalog, name=f"S{index}", path=directory)

    overflow = tmp_path / "overflow"
    overflow.mkdir()
    with pytest.raises(ValueError, match=str(MAX_SOURCES)):
        add_source(catalog, name="Overflow", path=overflow)


def test_add_profile_enforces_count_limit(tmp_path: Path, left_dir: Path) -> None:
    catalog = empty_catalog()
    source = add_source(catalog, name="Only", path=left_dir)

    for index in range(MAX_PROFILES):
        add_profile(catalog, name=f"P{index}", members={"L": source.id, "R": None})

    with pytest.raises(ValueError, match=str(MAX_PROFILES)):
        add_profile(catalog, name="Overflow", members={"L": source.id, "R": None})


def test_name_and_notes_length_limits(left_dir: Path) -> None:
    catalog = empty_catalog()

    with pytest.raises(ValueError, match="name must not be empty"):
        add_source(catalog, name="   ", path=left_dir)

    with pytest.raises(ValueError, match=str(MAX_NAME_LEN)):
        add_source(catalog, name="x" * (MAX_NAME_LEN + 1), path=left_dir)

    with pytest.raises(ValueError, match=str(MAX_NOTES_LEN)):
        add_source(catalog, name="Notes", path=left_dir, notes="n" * (MAX_NOTES_LEN + 1))


def test_update_source_changes_path(tmp_path: Path, left_dir: Path, right_dir: Path) -> None:
    catalog = empty_catalog()
    entry = add_source(catalog, name="Move", path=left_dir)

    update_source(catalog, entry.id, path=right_dir)

    assert get_source(catalog, entry.id).path == str(right_dir.resolve())


def test_delete_source_rejects_profile_reference(left_dir: Path, right_dir: Path) -> None:
    catalog = empty_catalog()
    left = add_source(catalog, name="Left", path=left_dir)
    add_source(catalog, name="Right", path=right_dir)
    add_profile(catalog, name="Pair", members={"L": left.id, "R": None})

    with pytest.raises(ValueError, match="referenced by a profile"):
        delete_source(catalog, left.id)


def test_delete_source_ok_when_unreferenced(left_dir: Path) -> None:
    catalog = empty_catalog()
    entry = add_source(catalog, name="Temp", path=left_dir)

    delete_source(catalog, entry.id)

    assert get_source(catalog, entry.id) is None


def test_delete_profile_always_allowed(left_dir: Path) -> None:
    catalog = empty_catalog()
    source = add_source(catalog, name="Left", path=left_dir)
    profile = add_profile(catalog, name="Pair", members={"L": source.id, "R": None})

    delete_profile(catalog, profile.id)

    assert get_profile(catalog, profile.id) is None
    assert get_source(catalog, source.id) is not None


def test_resolve_source_and_profile_members(left_dir: Path, right_dir: Path) -> None:
    catalog = empty_catalog()
    left = add_source(catalog, name="Left", path=left_dir)
    right = add_source(catalog, name="Right", path=right_dir)
    profile = add_profile(catalog, name="Dual", members={"L": left.id, "R": right.id})

    assert resolve_source(catalog, left.id) == left_dir.resolve()
    resolved = resolve_profile_members(catalog, profile.id)
    assert resolved["L"] == left_dir.resolve()
    assert resolved["R"] == right_dir.resolve()


def test_resolve_source_fails_when_directory_removed(left_dir: Path) -> None:
    catalog = empty_catalog()
    entry = add_source(catalog, name="Left", path=left_dir)
    source_id = entry.id

    for child in left_dir.iterdir():
        child.unlink()
    left_dir.rmdir()

    with pytest.raises(ValueError, match="existing directory"):
        resolve_source(catalog, source_id)


def test_add_profile_rejects_unknown_source_id(left_dir: Path) -> None:
    catalog = empty_catalog()

    with pytest.raises(ValueError, match="unknown source"):
        add_profile(catalog, name="Bad", members={"L": "missing-id", "R": None})


def test_load_rejects_unsupported_schema_version(tmp_path: Path) -> None:
    catalog_path = tmp_path / "sources.json"
    catalog_path.write_text(json.dumps({"schema_version": 99, "sources": [], "profiles": []}))

    with pytest.raises(ValueError, match="unsupported schema_version"):
        load_catalog(catalog_path)


def test_load_rejects_duplicate_ids(tmp_path: Path, left_dir: Path) -> None:
    catalog_path = tmp_path / "sources.json"
    shared_id = "11111111-1111-4111-8111-111111111111"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "sources": [
            {
                "id": shared_id,
                "name": "A",
                "kind": "local-dir",
                "path": str(left_dir.resolve()),
            }
        ],
        "profiles": [
            {
                "id": shared_id,
                "name": "P",
                "members": {"L": None, "R": None},
            }
        ],
    }
    catalog_path.write_text(json.dumps(payload))

    with pytest.raises(ValueError, match="duplicate catalog id"):
        load_catalog(catalog_path)


def test_catalog_from_dict_normalizes_missing_member_keys(left_dir: Path) -> None:
    catalog = catalog_from_dict(
        {
            "schema_version": SCHEMA_VERSION,
            "sources": [
                {
                    "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                    "name": "Left",
                    "kind": "local-dir",
                    "path": str(left_dir.resolve()),
                }
            ],
            "profiles": [
                {
                    "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                    "name": "Partial",
                    "members": {"L": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"},
                }
            ],
        }
    )

    profile = catalog.profiles[0]
    assert profile.members.L == "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    assert profile.members.R is None


def test_update_profile_members(left_dir: Path, right_dir: Path) -> None:
    catalog = empty_catalog()
    left = add_source(catalog, name="Left", path=left_dir)
    right = add_source(catalog, name="Right", path=right_dir)
    profile = add_profile(catalog, name="Dual", members={"L": left.id, "R": None})

    update_profile(catalog, profile.id, members={"L": left.id, "R": right.id})

    assert get_profile(catalog, profile.id).members.R == right.id

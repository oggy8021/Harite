from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any
import uuid

from harite.sources_file import (
    load_sources_json,
    resolve_default_sources_path,
    resolve_sources_path_for_load,
    save_sources_json,
)

SCHEMA_VERSION = 1
KIND_LOCAL_DIR = "local-dir"
MAX_SOURCES = 64
MAX_PROFILES = 32
MAX_NAME_LEN = 64
MAX_NOTES_LEN = 512
PROFILE_SIDES = ("L", "R")


@dataclass
class SourceEntry:
    id: str
    name: str
    kind: str
    path: str
    notes: str = ""


@dataclass
class ProfileMembers:
    L: str | None = None
    R: str | None = None


@dataclass
class ProfileEntry:
    id: str
    name: str
    members: ProfileMembers


@dataclass
class Catalog:
    schema_version: int = SCHEMA_VERSION
    sources: list[SourceEntry] = field(default_factory=list)
    profiles: list[ProfileEntry] = field(default_factory=list)


def empty_catalog() -> Catalog:
    return Catalog()


def normalize_directory_path(path: str | Path) -> Path:
    candidate = Path(path)
    try:
        resolved = candidate.resolve()
    except OSError as exc:
        raise ValueError(f"path is not accessible: {path}") from exc
    if not resolved.is_dir():
        raise ValueError(f"path must be an existing directory: {path}")
    normalized = Path(os.path.normpath(str(resolved)))
    if not normalized.is_absolute():
        raise ValueError(f"path must be absolute after normalization: {path}")
    return normalized


def _new_id(catalog: Catalog) -> str:
    while True:
        candidate = str(uuid.uuid4())
        if not _id_exists(catalog, candidate):
            return candidate


def _id_exists(catalog: Catalog, entry_id: str) -> bool:
    return any(entry.id == entry_id for entry in catalog.sources) or any(
        entry.id == entry_id for entry in catalog.profiles
    )


def _validate_name(name: str, *, label: str) -> str:
    trimmed = name.strip()
    if not trimmed:
        raise ValueError(f"{label} name must not be empty")
    if len(trimmed) > MAX_NAME_LEN:
        raise ValueError(f"{label} name exceeds {MAX_NAME_LEN} characters")
    return trimmed


def _validate_notes(notes: str | None) -> str:
    value = "" if notes is None else str(notes)
    if len(value) > MAX_NOTES_LEN:
        raise ValueError(f"notes exceed {MAX_NOTES_LEN} characters")
    return value


def _normalize_members(raw: object | None) -> ProfileMembers:
    if raw is None:
        return ProfileMembers()
    if not isinstance(raw, dict):
        raise ValueError("profile members must be an object")
    members: dict[str, str | None] = {}
    for side in PROFILE_SIDES:
        if side not in raw:
            members[side] = None
            continue
        value = raw[side]
        if value is None:
            members[side] = None
        else:
            members[side] = str(value)
    extra = set(raw) - set(PROFILE_SIDES)
    if extra:
        raise ValueError(f"unsupported profile member keys: {sorted(extra)}")
    return ProfileMembers(L=members["L"], R=members["R"])


def _validate_member_refs(catalog: Catalog, members: ProfileMembers) -> None:
    for side in PROFILE_SIDES:
        source_id = getattr(members, side)
        if source_id is None:
            continue
        if get_source(catalog, source_id) is None:
            raise ValueError(f"profile member {side} references unknown source: {source_id}")


def _source_name_taken(catalog: Catalog, name: str, *, exclude_id: str | None = None) -> bool:
    return any(entry.name == name and entry.id != exclude_id for entry in catalog.sources)


def _profile_name_taken(catalog: Catalog, name: str, *, exclude_id: str | None = None) -> bool:
    return any(entry.name == name and entry.id != exclude_id for entry in catalog.profiles)


def _validate_catalog(catalog: Catalog) -> None:
    if catalog.schema_version != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {catalog.schema_version}")

    seen_ids: set[str] = set()
    for entry in catalog.sources:
        if entry.id in seen_ids:
            raise ValueError(f"duplicate catalog id: {entry.id}")
        seen_ids.add(entry.id)
        _validate_name(entry.name, label="source")
        _validate_notes(entry.notes)
        if entry.kind != KIND_LOCAL_DIR:
            raise ValueError(f"unsupported source kind: {entry.kind}")

    source_names: set[str] = set()
    for entry in catalog.sources:
        if entry.name in source_names:
            raise ValueError(f"duplicate source name: {entry.name}")
        source_names.add(entry.name)

    if len(catalog.sources) > MAX_SOURCES:
        raise ValueError(f"source count exceeds {MAX_SOURCES}")

    profile_names: set[str] = set()
    for entry in catalog.profiles:
        if entry.id in seen_ids:
            raise ValueError(f"duplicate catalog id: {entry.id}")
        seen_ids.add(entry.id)
        _validate_name(entry.name, label="profile")
        if entry.name in profile_names:
            raise ValueError(f"duplicate profile name: {entry.name}")
        profile_names.add(entry.name)
        _validate_member_refs(catalog, entry.members)

    if len(catalog.profiles) > MAX_PROFILES:
        raise ValueError(f"profile count exceeds {MAX_PROFILES}")


def catalog_to_dict(catalog: Catalog) -> dict[str, Any]:
    _validate_catalog(catalog)
    return {
        "schema_version": catalog.schema_version,
        "sources": [
            {
                "id": entry.id,
                "name": entry.name,
                "kind": entry.kind,
                "path": entry.path,
                **({"notes": entry.notes} if entry.notes else {}),
            }
            for entry in catalog.sources
        ],
        "profiles": [
            {
                "id": entry.id,
                "name": entry.name,
                "members": {"L": entry.members.L, "R": entry.members.R},
            }
            for entry in catalog.profiles
        ],
    }


def catalog_from_dict(data: dict[str, Any]) -> Catalog:
    schema_version = data.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {schema_version}")

    raw_sources = data.get("sources", [])
    raw_profiles = data.get("profiles", [])
    if not isinstance(raw_sources, list) or not isinstance(raw_profiles, list):
        raise ValueError("sources and profiles must be arrays")

    sources: list[SourceEntry] = []
    for item in raw_sources:
        if not isinstance(item, dict):
            raise ValueError("source entry must be an object")
        for key in ("id", "name", "kind", "path"):
            if key not in item:
                raise ValueError(f"source entry missing {key}")
        sources.append(
            SourceEntry(
                id=str(item["id"]),
                name=str(item["name"]),
                kind=str(item["kind"]),
                path=str(item["path"]),
                notes=str(item.get("notes", "")),
            )
        )

    profiles: list[ProfileEntry] = []
    for item in raw_profiles:
        if not isinstance(item, dict):
            raise ValueError("profile entry must be an object")
        for key in ("id", "name", "members"):
            if key not in item:
                raise ValueError(f"profile entry missing {key}")
        profiles.append(
            ProfileEntry(
                id=str(item["id"]),
                name=str(item["name"]),
                members=_normalize_members(item["members"]),
            )
        )

    catalog = Catalog(schema_version=SCHEMA_VERSION, sources=sources, profiles=profiles)
    _validate_catalog(catalog)
    return catalog


def load_catalog(path: Path | None = None) -> Catalog:
    target = resolve_sources_path_for_load(path)
    if not target.exists():
        return empty_catalog()
    return catalog_from_dict(load_sources_json(target))


def save_catalog(catalog: Catalog, path: Path | None = None) -> Path:
    target = path or resolve_default_sources_path()
    return save_sources_json(target, catalog_to_dict(catalog))


def list_sources(catalog: Catalog) -> list[SourceEntry]:
    return list(catalog.sources)


def get_source(catalog: Catalog, source_id: str) -> SourceEntry | None:
    for entry in catalog.sources:
        if entry.id == source_id:
            return entry
    return None


def add_source(
    catalog: Catalog,
    *,
    name: str,
    path: str | Path,
    notes: str | None = None,
) -> SourceEntry:
    if len(catalog.sources) >= MAX_SOURCES:
        raise ValueError(f"source count exceeds {MAX_SOURCES}")

    validated_name = _validate_name(name, label="source")
    if _source_name_taken(catalog, validated_name):
        raise ValueError(f"duplicate source name: {validated_name}")

    normalized_path = normalize_directory_path(path)
    entry = SourceEntry(
        id=_new_id(catalog),
        name=validated_name,
        kind=KIND_LOCAL_DIR,
        path=str(normalized_path),
        notes=_validate_notes(notes),
    )
    catalog.sources.append(entry)
    return entry


def update_source(catalog: Catalog, source_id: str, **fields: Any) -> SourceEntry:
    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")

    if "id" in fields:
        raise ValueError("source id cannot be changed")

    if "name" in fields:
        validated_name = _validate_name(str(fields["name"]), label="source")
        if _source_name_taken(catalog, validated_name, exclude_id=source_id):
            raise ValueError(f"duplicate source name: {validated_name}")
        entry.name = validated_name

    if "path" in fields:
        entry.path = str(normalize_directory_path(fields["path"]))

    if "notes" in fields:
        entry.notes = _validate_notes(fields["notes"])

    if "kind" in fields and str(fields["kind"]) != KIND_LOCAL_DIR:
        raise ValueError(f"unsupported source kind: {fields['kind']}")

    return entry


def _profile_references_source(catalog: Catalog, source_id: str) -> bool:
    for profile in catalog.profiles:
        if profile.members.L == source_id or profile.members.R == source_id:
            return True
    return False


def delete_source(catalog: Catalog, source_id: str) -> None:
    if get_source(catalog, source_id) is None:
        raise ValueError(f"unknown source id: {source_id}")
    if _profile_references_source(catalog, source_id):
        raise ValueError(f"source is referenced by a profile: {source_id}")
    catalog.sources = [entry for entry in catalog.sources if entry.id != source_id]


def list_profiles(catalog: Catalog) -> list[ProfileEntry]:
    return list(catalog.profiles)


def get_profile(catalog: Catalog, profile_id: str) -> ProfileEntry | None:
    for entry in catalog.profiles:
        if entry.id == profile_id:
            return entry
    return None


def add_profile(
    catalog: Catalog,
    *,
    name: str,
    members: dict[str, str | None] | ProfileMembers,
) -> ProfileEntry:
    if len(catalog.profiles) >= MAX_PROFILES:
        raise ValueError(f"profile count exceeds {MAX_PROFILES}")

    validated_name = _validate_name(name, label="profile")
    if _profile_name_taken(catalog, validated_name):
        raise ValueError(f"duplicate profile name: {validated_name}")

    normalized_members = members if isinstance(members, ProfileMembers) else _normalize_members(members)
    _validate_member_refs(catalog, normalized_members)

    entry = ProfileEntry(
        id=_new_id(catalog),
        name=validated_name,
        members=normalized_members,
    )
    catalog.profiles.append(entry)
    return entry


def update_profile(catalog: Catalog, profile_id: str, **fields: Any) -> ProfileEntry:
    entry = get_profile(catalog, profile_id)
    if entry is None:
        raise ValueError(f"unknown profile id: {profile_id}")

    if "id" in fields:
        raise ValueError("profile id cannot be changed")

    if "name" in fields:
        validated_name = _validate_name(str(fields["name"]), label="profile")
        if _profile_name_taken(catalog, validated_name, exclude_id=profile_id):
            raise ValueError(f"duplicate profile name: {validated_name}")
        entry.name = validated_name

    if "members" in fields:
        normalized_members = _normalize_members(fields["members"])
        _validate_member_refs(catalog, normalized_members)
        entry.members = normalized_members

    return entry


def delete_profile(catalog: Catalog, profile_id: str) -> None:
    if get_profile(catalog, profile_id) is None:
        raise ValueError(f"unknown profile id: {profile_id}")
    catalog.profiles = [entry for entry in catalog.profiles if entry.id != profile_id]


def resolve_source(catalog: Catalog, source_id: str) -> Path:
    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    return normalize_directory_path(entry.path)


def resolve_profile_members(catalog: Catalog, profile_id: str) -> dict[str, Path | None]:
    entry = get_profile(catalog, profile_id)
    if entry is None:
        raise ValueError(f"unknown profile id: {profile_id}")

    resolved: dict[str, Path | None] = {}
    for side in PROFILE_SIDES:
        source_id = getattr(entry.members, side)
        resolved[side] = resolve_source(catalog, source_id) if source_id else None
    return resolved

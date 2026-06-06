"""Bundled source presets: load, import, bootstrap, slideshow interval floor."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from pathlib import Path
from typing import Any

from harite.gui.resource_access import gui_resource_path
from harite.sources import (
    MAX_PROFILES,
    MAX_SOURCES,
    Catalog,
    ProfileEntry,
    ProfileMembers,
    SourceEntry,
    add_profile,
    get_profile,
    get_source,
    list_sources,
)
from harite.sources_remote import (
    CODH_KEYWORD_DEFAULT,
    CODH_KEYWORD_NOTE_PREFIX,
    PRESET_MARKER_PREFIX,
    add_remote_source,
    codh_keyword_from_notes,
    is_codh_keyword_preset,
    is_remote_kind,
    preset_id_from_notes,
    sync_remote_source,
    upsert_codh_keyword_in_notes,
)

PRESET_SCHEMA_VERSION = 1
PRESET_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MIN_INTERVAL_NOTE_PREFIX = "harite-min-interval:"

_BUNDLED_PRESETS = ("source_presets", "harite-source-presets.json")


@dataclass
class PresetSourceTemplate:
    preset_id: str
    name: str
    kind: str
    notes: str = ""
    min_slideshow_interval_seconds: int | None = None


@dataclass
class PresetProfileTemplate:
    preset_id: str
    name: str
    members: ProfileMembers
    min_slideshow_interval_seconds: int | None = None


@dataclass
class PresetCatalog:
    preset_schema_version: int = PRESET_SCHEMA_VERSION
    sources: list[PresetSourceTemplate] = field(default_factory=list)
    profiles: list[PresetProfileTemplate] = field(default_factory=list)


def _validate_preset_id(preset_id: str) -> str:
    if not PRESET_ID_RE.fullmatch(preset_id):
        raise ValueError(f"invalid preset_id: {preset_id}")
    return preset_id


def _strip_managed_preset_note_lines(text: str) -> str:
    """Remove machine lines re-built by _format_preset_notes (preset marker, keyword, min interval)."""
    kept: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if (
            stripped.startswith(PRESET_MARKER_PREFIX)
            or stripped.startswith(MIN_INTERVAL_NOTE_PREFIX)
            or stripped.startswith(CODH_KEYWORD_NOTE_PREFIX)
        ):
            continue
        kept.append(stripped)
    return "\n".join(kept)


def _format_preset_notes(
    template: PresetSourceTemplate,
) -> str:
    lines = [f"{PRESET_MARKER_PREFIX}{template.preset_id}"]
    body = _strip_managed_preset_note_lines(template.notes)
    if body:
        lines.append(body)
    if is_codh_keyword_preset(template.preset_id):
        lines.append(f"{CODH_KEYWORD_NOTE_PREFIX}{CODH_KEYWORD_DEFAULT}")
    if template.min_slideshow_interval_seconds is not None:
        lines.append(f"{MIN_INTERVAL_NOTE_PREFIX}{template.min_slideshow_interval_seconds}")
    return "\n".join(lines)


def canonical_preset_source_notes(template: PresetSourceTemplate) -> str:
    from harite.sources import _validate_notes

    return _validate_notes(_format_preset_notes(template))


def repair_preset_profile_members(
    catalog: Catalog,
    *,
    preset_catalog: PresetCatalog | None = None,
) -> bool:
    """Re-link bundled profile L/R members to current preset source ids."""
    templates = preset_catalog or load_source_presets()
    changed = False
    for template in templates.profiles:
        profile = next((entry for entry in catalog.profiles if entry.name == template.name), None)
        if profile is None:
            continue
        new_members = ProfileMembers()
        for side in ("L", "R"):
            member_preset = getattr(template.members, side)
            if member_preset is None:
                setattr(new_members, side, None)
                continue
            source = find_catalog_source_for_preset(catalog, member_preset)
            setattr(new_members, side, source.id if source is not None else None)
        if profile.members.L != new_members.L or profile.members.R != new_members.R:
            profile.members = new_members
            changed = True
    return changed


def repair_preset_catalog_integrity(
    catalog: Catalog,
    *,
    preset_catalog: PresetCatalog | None = None,
) -> bool:
    return repair_preset_source_notes(catalog, preset_catalog=preset_catalog) or repair_preset_profile_members(
        catalog, preset_catalog=preset_catalog
    )


def repair_preset_source_notes(
    catalog: Catalog,
    *,
    preset_catalog: PresetCatalog | None = None,
) -> bool:
    """Normalize preset-derived source notes (fix duplicates, add missing markers)."""
    templates = preset_catalog or load_source_presets()
    changed = False
    for template in templates.sources:
        entry = find_catalog_source_for_preset(catalog, template.preset_id)
        if entry is None:
            continue
        canonical = canonical_preset_source_notes(template)
        if is_codh_keyword_preset(template.preset_id):
            user_keyword = codh_keyword_from_notes(entry.notes)
            if user_keyword:
                canonical = upsert_codh_keyword_in_notes(canonical, user_keyword)
        if entry.notes != canonical:
            entry.notes = canonical
            changed = True
    return changed


def min_interval_from_notes(notes: str) -> int | None:
    for line in notes.splitlines():
        stripped = line.strip()
        if stripped.startswith(MIN_INTERVAL_NOTE_PREFIX):
            raw = stripped[len(MIN_INTERVAL_NOTE_PREFIX) :].strip()
            try:
                value = int(raw)
            except ValueError:
                continue
            if value >= 1:
                return value
    return None


def preset_catalog_from_dict(data: dict[str, Any]) -> PresetCatalog:
    version = data.get("preset_schema_version")
    if version != PRESET_SCHEMA_VERSION:
        raise ValueError(f"unsupported preset_schema_version: {version}")

    raw_sources = data.get("sources", [])
    raw_profiles = data.get("profiles", [])
    if not isinstance(raw_sources, list) or not isinstance(raw_profiles, list):
        raise ValueError("preset sources and profiles must be arrays")

    sources: list[PresetSourceTemplate] = []
    for item in raw_sources:
        if not isinstance(item, dict):
            raise ValueError("preset source entry must be an object")
        preset_id = _validate_preset_id(str(item["preset_id"]))
        kind = str(item["kind"])
        if not is_remote_kind(kind):
            raise ValueError(f"preset source kind must be remote-*: {kind}")
        min_interval = item.get("min_slideshow_interval_seconds")
        sources.append(
            PresetSourceTemplate(
                preset_id=preset_id,
                name=str(item["name"]),
                kind=kind,
                notes=str(item.get("notes", "")),
                min_slideshow_interval_seconds=int(min_interval) if min_interval is not None else None,
            )
        )

    profiles: list[PresetProfileTemplate] = []
    for item in raw_profiles:
        if not isinstance(item, dict):
            raise ValueError("preset profile entry must be an object")
        preset_id = _validate_preset_id(str(item["preset_id"]))
        raw_members = item.get("members", {})
        if not isinstance(raw_members, dict):
            raise ValueError("preset profile members must be an object")
        members = ProfileMembers(
            L=str(raw_members["L"]) if raw_members.get("L") is not None else None,
            R=str(raw_members["R"]) if raw_members.get("R") is not None else None,
        )
        min_interval = item.get("min_slideshow_interval_seconds")
        profiles.append(
            PresetProfileTemplate(
                preset_id=preset_id,
                name=str(item["name"]),
                members=members,
                min_slideshow_interval_seconds=int(min_interval) if min_interval is not None else None,
            )
        )

    return PresetCatalog(preset_schema_version=PRESET_SCHEMA_VERSION, sources=sources, profiles=profiles)


def load_source_presets(*, path: Path | None = None) -> PresetCatalog:
    if path is not None:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("preset file root must be an object")
        return preset_catalog_from_dict(payload)

    with gui_resource_path(*_BUNDLED_PRESETS) as preset_path:
        payload = json.loads(preset_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("preset file root must be an object")
        return preset_catalog_from_dict(payload)


def _find_preset_source(preset_catalog: PresetCatalog, preset_id: str) -> PresetSourceTemplate:
    for template in preset_catalog.sources:
        if template.preset_id == preset_id:
            return template
    raise ValueError(f"unknown preset source id: {preset_id}")


def _find_preset_profile(preset_catalog: PresetCatalog, preset_id: str) -> PresetProfileTemplate:
    for template in preset_catalog.profiles:
        if template.preset_id == preset_id:
            return template
    raise ValueError(f"unknown preset profile id: {preset_id}")


def find_catalog_source_for_preset(catalog: Catalog, preset_id: str) -> SourceEntry | None:
    marker = f"{PRESET_MARKER_PREFIX}{preset_id}"
    for entry in catalog.sources:
        if marker in entry.notes:
            return entry
    return None


def find_catalog_profile_for_preset(
    catalog: Catalog,
    preset_id: str,
    *,
    preset_catalog: PresetCatalog | None = None,
) -> ProfileEntry | None:
    templates = preset_catalog or load_source_presets()
    try:
        template = _find_preset_profile(templates, preset_id)
    except ValueError:
        return None

    for entry in catalog.profiles:
        if entry.name != template.name:
            continue
        matches = True
        for side in ("L", "R"):
            expected_preset = getattr(template.members, side)
            if expected_preset is None:
                continue
            member_id = getattr(entry.members, side)
            if member_id is None:
                matches = False
                break
            source = get_source(catalog, member_id)
            if source is None or preset_id_from_notes(source.notes) != expected_preset:
                matches = False
                break
        if matches:
            return entry
    return None


def _unique_source_name(catalog: Catalog, base_name: str) -> str:
    if not any(entry.name == base_name for entry in catalog.sources):
        return base_name
    suffix = 2
    while True:
        candidate = f"{base_name} ({suffix})"
        if not any(entry.name == candidate for entry in catalog.sources):
            return candidate
        suffix += 1


def import_preset_source(
    user_catalog: Catalog,
    preset_id: str,
    *,
    preset_catalog: PresetCatalog | None = None,
    cache_root: Path | None = None,
) -> SourceEntry:
    if len(user_catalog.sources) >= MAX_SOURCES:
        raise ValueError(f"source count exceeds {MAX_SOURCES}")
    templates = preset_catalog or load_source_presets()
    template = _find_preset_source(templates, preset_id)
    name = _unique_source_name(user_catalog, template.name)
    return add_remote_source(
        user_catalog,
        name=name,
        kind=template.kind,
        notes=canonical_preset_source_notes(template),
        cache_root=cache_root,
    )


def import_preset_profile(
    user_catalog: Catalog,
    preset_id: str,
    *,
    preset_catalog: PresetCatalog | None = None,
    imported_sources: dict[str, str] | None = None,
    cache_root: Path | None = None,
) -> ProfileEntry:
    if len(user_catalog.profiles) >= MAX_PROFILES:
        raise ValueError(f"profile count exceeds {MAX_PROFILES}")
    templates = preset_catalog or load_source_presets()
    template = _find_preset_profile(templates, preset_id)
    id_map = dict(imported_sources or {})

    for side in ("L", "R"):
        member_preset = getattr(template.members, side)
        if member_preset is None:
            continue
        if member_preset not in id_map:
            existing = find_catalog_source_for_preset(user_catalog, member_preset)
            if existing is not None:
                id_map[member_preset] = existing.id
            else:
                imported = import_preset_source(
                    user_catalog,
                    member_preset,
                    preset_catalog=templates,
                    cache_root=cache_root,
                )
                id_map[member_preset] = imported.id

    members = {
        "L": id_map.get(template.members.L) if template.members.L else None,
        "R": id_map.get(template.members.R) if template.members.R else None,
    }
    return add_profile(user_catalog, name=template.name, members=members)


def preset_min_slideshow_interval(
    preset_catalog: PresetCatalog,
    preset_id: str,
) -> int | None:
    for template in preset_catalog.sources:
        if template.preset_id == preset_id:
            return template.min_slideshow_interval_seconds
    for template in preset_catalog.profiles:
        if template.preset_id == preset_id:
            if template.min_slideshow_interval_seconds is not None:
                return template.min_slideshow_interval_seconds
            floors: list[int] = []
            for side in ("L", "R"):
                member_preset = getattr(template.members, side)
                if member_preset:
                    member_floor = preset_min_slideshow_interval(preset_catalog, member_preset)
                    if member_floor is not None:
                        floors.append(member_floor)
            return max(floors) if floors else None
    raise ValueError(f"unknown preset id: {preset_id}")


def catalog_slideshow_interval_floor(
    catalog: Catalog,
    *,
    source_id_l: str | None = None,
    source_id_r: str | None = None,
    profile_id: str | None = None,
) -> int | None:
    floors: list[int] = []

    if profile_id:
        profile = get_profile(catalog, profile_id)
        if profile is None:
            return None
        for side in ("L", "R"):
            source_id = getattr(profile.members, side)
            if source_id:
                entry = get_source(catalog, source_id)
                if entry is not None:
                    floor = min_interval_from_notes(entry.notes)
                    if floor is not None:
                        floors.append(floor)
        return max(floors) if floors else None

    for source_id in (source_id_l, source_id_r):
        if not source_id:
            continue
        entry = get_source(catalog, source_id)
        if entry is None:
            continue
        floor = min_interval_from_notes(entry.notes)
        if floor is not None:
            floors.append(floor)
    return max(floors) if floors else None


def bootstrap_preset_sources(
    catalog: Catalog,
    *,
    preset_catalog: PresetCatalog | None = None,
    cache_root: Path | None = None,
    sync: bool = True,
) -> bool:
    templates = preset_catalog or load_source_presets()
    changed = False
    imported_sources: dict[str, str] = {}

    for template in templates.sources:
        if find_catalog_source_for_preset(catalog, template.preset_id) is not None:
            continue
        entry = import_preset_source(
            catalog,
            template.preset_id,
            preset_catalog=templates,
            cache_root=cache_root,
        )
        imported_sources[template.preset_id] = entry.id
        changed = True

    for template in templates.profiles:
        if find_catalog_profile_for_preset(
            catalog, template.preset_id, preset_catalog=templates
        ) is not None:
            continue
        if any(entry.name == template.name for entry in catalog.profiles):
            continue
        import_preset_profile(
            catalog,
            template.preset_id,
            preset_catalog=templates,
            imported_sources=imported_sources,
            cache_root=cache_root,
        )
        changed = True

    if sync:
        for entry in list_sources(catalog):
            if is_remote_kind(entry.kind) and PRESET_MARKER_PREFIX in entry.notes:
                try:
                    sync_remote_source(catalog, entry.id, cache_root=cache_root)
                except ValueError:
                    pass

    return changed

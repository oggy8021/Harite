"""Qt helpers for C-01 source catalog bootstrap and combo labels."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harite.sources import Catalog, ProfileEntry, SourceEntry, load_catalog, save_catalog
from harite.sources_preset import bootstrap_preset_sources, find_catalog_profile_for_preset, load_source_presets
from harite.sources_remote import PRESET_MARKER_PREFIX, is_remote_kind, preset_id_from_notes


def slideshow_source_combo_label(entry: SourceEntry) -> str:
    if preset_id_from_notes(entry.notes):
        return f"*{entry.name}"
    return entry.name


def slideshow_profile_combo_label(catalog: Catalog, entry: ProfileEntry) -> str:
    presets = load_source_presets()
    for template in presets.profiles:
        matched = find_catalog_profile_for_preset(
            catalog, template.preset_id, preset_catalog=presets
        )
        if matched is not None and matched.id == entry.id:
            return f"*{entry.name}"
    return entry.name


def materialize_source_catalog_at_path(path: Path, *, owner: Any | None = None) -> Catalog:
    """Bootstrap presets, best-effort remote sync, persist when new entries are added."""
    catalog = load_catalog(path)
    changed = bootstrap_preset_sources(catalog, sync=True)
    if changed:
        save_catalog(catalog, path)
        return catalog

    for entry in catalog.sources:
        if not is_remote_kind(entry.kind) or PRESET_MARKER_PREFIX not in entry.notes:
            continue
        try:
            from harite.sources_remote import sync_remote_source

            sync_remote_source(catalog, entry.id)
        except ValueError as exc:
            log = getattr(owner, "_log", None) if owner is not None else None
            if callable(log):
                log(f"Preset sync skipped ({entry.name}): {exc}")
    return catalog


def prepare_owner_source_catalog(owner: Any) -> Catalog:
    from harite.sources_file import resolve_default_sources_path

    path = getattr(owner, "_source_catalog_path", None) or resolve_default_sources_path()
    if not isinstance(path, Path):
        path = Path(path)
    setattr(owner, "_source_catalog_path", path)
    return materialize_source_catalog_at_path(path, owner=owner)


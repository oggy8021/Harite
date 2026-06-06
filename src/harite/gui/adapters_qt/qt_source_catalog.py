"""Qt helpers for C-01 source catalog bootstrap and combo labels."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harite.sources import Catalog, ProfileEntry, SourceEntry, load_catalog, save_catalog
from harite.sources_preset import (
    bootstrap_preset_sources,
    find_catalog_profile_for_preset,
    load_source_presets,
    repair_preset_catalog_integrity,
)
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


def _load_catalog_for_materialize(path: Path) -> Catalog:
    if not path.exists():
        return load_catalog(path)
    try:
        return load_catalog(path)
    except ValueError:
        return load_catalog(path, validate_member_refs=False)


def _remote_cache_has_latest_image(cache_dir: Path) -> bool:
    if not cache_dir.is_dir():
        return False
    return any((cache_dir / name).is_file() for name in ("latest.png", "latest.jpg"))


def materialize_source_catalog_at_path(
    path: Path,
    *,
    owner: Any | None = None,
    sync_remote: bool = False,
) -> Catalog:
    """Bootstrap presets, persist catalog updates.

    Remote fetch is **off by default** so GUI startup and catalog reads stay
    non-blocking. Use Manage **Refresh** or slideshow **Start** (see
    ``sync_remote_source``) to populate cache.
    """
    from harite.settings_file import resolve_default_settings_path
    from harite.sources_remote import load_codh_keyword_settings, migrate_codh_keyword_notes_to_settings

    catalog = _load_catalog_for_materialize(path)
    settings_path = resolve_default_settings_path()
    settings = load_codh_keyword_settings(settings_path)
    settings, catalog_migrated, settings_migrated = migrate_codh_keyword_notes_to_settings(catalog, settings)
    dirty = catalog_migrated
    if settings_migrated:
        from harite.sources_remote import CODH_KEYWORD_SETTINGS_KEY, save_codh_keyword_settings

        save_codh_keyword_settings(settings_path, str(settings[CODH_KEYWORD_SETTINGS_KEY]))
    dirty = repair_preset_catalog_integrity(catalog) or dirty
    dirty = bootstrap_preset_sources(catalog, sync=False) or dirty
    dirty = repair_preset_catalog_integrity(catalog) or dirty

    from harite.sources_remote import prune_orphan_remote_cache_dirs

    prune_orphan_remote_cache_dirs(catalog)

    if sync_remote:
        for entry in catalog.sources:
            if not is_remote_kind(entry.kind) or PRESET_MARKER_PREFIX not in entry.notes:
                continue
            cache_dir = Path(entry.path)
            if _remote_cache_has_latest_image(cache_dir):
                continue
            path_before = entry.path
            try:
                from harite.sources_remote import sync_remote_source

                sync_remote_source(catalog, entry.id)
            except ValueError as exc:
                log = getattr(owner, "_log", None) if owner is not None else None
                if callable(log):
                    log(f"Preset sync skipped ({entry.name}): {exc}")
            else:
                if entry.path != path_before:
                    dirty = True

    if dirty:
        save_catalog(catalog, path)
    return catalog


def _catalog_path_mtime(path: Path) -> float:
    if not path.exists():
        return 0.0
    return path.stat().st_mtime


def prepare_owner_source_catalog(owner: Any) -> Catalog:
    from harite.sources_file import resolve_default_sources_path

    path = getattr(owner, "_source_catalog_path", None) or resolve_default_sources_path()
    if not isinstance(path, Path):
        path = Path(path)
    setattr(owner, "_source_catalog_path", path)

    mtime = _catalog_path_mtime(path)
    cached = getattr(owner, "_source_catalog_cache", None)
    if cached is not None and getattr(owner, "_source_catalog_cache_mtime", None) == mtime:
        return cached

    catalog = materialize_source_catalog_at_path(path, owner=owner)
    setattr(owner, "_source_catalog_cache", catalog)
    setattr(owner, "_source_catalog_cache_mtime", _catalog_path_mtime(path))
    return catalog


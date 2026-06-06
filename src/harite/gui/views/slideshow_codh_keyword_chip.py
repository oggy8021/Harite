"""Slideshow tab CODH keyword read-only chip (P-06)."""

from __future__ import annotations

from harite.sources import Catalog, SourceEntry, get_profile, get_source
from harite.sources_remote import codh_keyword_from_settings, source_supports_codh_keyword


def _normalize_id(value: object) -> str:
    return str(value or "").strip()


def _entry_supports_chip(entry: SourceEntry | None) -> bool:
    return entry is not None and source_supports_codh_keyword(entry)


def slideshow_uses_codh_keyword_preset(
    *,
    catalog: Catalog,
    source_id_l: str,
    source_id_r: str,
    profile_id: str,
) -> bool:
    """True when the effective L/R slideshow selection includes a CODH keyword preset."""
    profile_key = _normalize_id(profile_id)
    if profile_key:
        profile = get_profile(catalog, profile_key)
        if profile is None:
            return False
        candidate_ids = (profile.members.L, profile.members.R)
    else:
        candidate_ids = (_normalize_id(source_id_l), _normalize_id(source_id_r))

    for raw_id in candidate_ids:
        if not raw_id:
            continue
        if _entry_supports_chip(get_source(catalog, raw_id)):
            return True
    return False


def format_slideshow_codh_keyword_chip(keyword: str) -> str:
    value = str(keyword or "").strip()
    return f"CODH: {value}" if value else ""

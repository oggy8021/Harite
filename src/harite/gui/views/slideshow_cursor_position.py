"""Slideshow tab cursor / list-position read-only chips (#507)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harite.sources import KIND_LOCAL_DIR, Catalog, SourceEntry, get_profile, get_source
from harite.sources_remote import (
    KIND_CODH_EDO,
    KIND_JMA_WEATHER_MAP,
    KIND_NDL_KIRIEZU,
    KIND_NDL_TSUGIDIGI,
    preset_id_from_notes,
    source_supports_ndl_keyword,
)
from harite.sources_remote_codh import load_codh_cycle, load_codh_index, reconcile_codh_cycle
from harite.sources_remote_jma import load_jma_cycle
from harite.sources_remote_ndl_kiriezu import (
    load_kiriezu_cycle,
    reconcile_kiriezu_cycle,
    resolve_kiriezu_preset_spec,
)
from harite.sources_remote_ndl_keyword import (
    load_ndl_search_batch,
    load_ndl_search_cycle,
    reconcile_ndl_search_cycle,
    resolve_ndl_keyword,
)


@dataclass(frozen=True)
class SlideshowSideCursorDisplay:
    label: str
    tooltip: str = ""


def _normalize_side(side: str) -> str:
    return side.strip().upper()


def resolve_slideshow_side_context(
    catalog: Catalog,
    owner: Any,
    side: str,
) -> tuple[SourceEntry | None, Path | None]:
    side_key = _normalize_side(side)
    if side_key not in ("L", "R"):
        return None, None

    id_attr = "slideshow_source_id_l" if side_key == "L" else "slideshow_source_id_r"
    path_attr = "slideshow_srcdir_l" if side_key == "L" else "slideshow_srcdir_r"
    profile_id = str(getattr(owner, "slideshow_profile_id", "") or "").strip()
    source_id = ""
    srcdir = ""

    if profile_id:
        profile = get_profile(catalog, profile_id)
        if profile is None:
            return None, None
        member_id = profile.members.L if side_key == "L" else profile.members.R
        source_id = str(member_id or "").strip()
        srcdir = str(getattr(owner, path_attr, "") or "").strip()
    else:
        source_id = str(getattr(owner, id_attr, "") or "").strip()
        srcdir = str(getattr(owner, path_attr, "") or "").strip()

    if source_id:
        entry = get_source(catalog, source_id)
        if entry is not None:
            return entry, Path(entry.path)

    if not srcdir:
        return None, None

    source_path = Path(srcdir)
    try:
        resolved = source_path.resolve()
    except OSError:
        resolved = source_path
    for entry in catalog.sources:
        try:
            if Path(entry.path).resolve() == resolved:
                return entry, source_path
        except OSError:
            continue
    return None, source_path


def _format_local_dir_cursor(owner: Any, side: str, source_dir: Path) -> SlideshowSideCursorDisplay | None:
    from harite.slideshow import collect_slideshow_input_images

    side_key = _normalize_side(side)
    try:
        images = collect_slideshow_input_images([source_dir])
    except ValueError:
        return None
    if not images:
        return None

    state = (
        getattr(owner, "_slideshow_state_l", None)
        if side_key == "L"
        else getattr(owner, "_slideshow_state_r", None)
    )
    previous = getattr(state, "previous_selected", None) if state is not None else None
    if previous is not None:
        try:
            resolved_previous = previous.resolve()
        except OSError:
            resolved_previous = previous
        for index, image in enumerate(images):
            try:
                if image.resolve() == resolved_previous:
                    return SlideshowSideCursorDisplay(f"{index + 1}/{len(images)}")
            except OSError:
                if image == previous:
                    return SlideshowSideCursorDisplay(f"{index + 1}/{len(images)}")
    return SlideshowSideCursorDisplay(f"1/{len(images)}")


CODH_RANDOM_CURSOR_POSITION = "-"


def _resolve_codh_slideshow_mode(cycle: dict[str, Any], owner: Any) -> str:
    mode = str(cycle.get("mode") or "").strip().lower()
    if mode in {"sequential", "random"}:
        return mode
    active = str(getattr(owner, "_slideshow_active_mode", "") or "").strip().lower()
    if active in {"sequential", "random"}:
        return active
    fallback = str(getattr(owner, "slideshow_mode", "random") or "random").strip().lower()
    return fallback if fallback in {"sequential", "random"} else "random"


def _format_codh_cursor(cache_dir: Path, owner: Any) -> SlideshowSideCursorDisplay | None:
    index = load_codh_index(cache_dir)
    if index is None:
        return None
    entries = index.get("entries")
    total = len(entries) if isinstance(entries, list) else 0
    if total < 1:
        return None
    cycle = reconcile_codh_cycle(load_codh_cycle(cache_dir), index)
    mode = _resolve_codh_slideshow_mode(cycle, owner)
    if mode == "random":
        return SlideshowSideCursorDisplay(f"{CODH_RANDOM_CURSOR_POSITION}/{total}")
    try:
        cursor_index = int(cycle.get("index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    cursor_index %= total
    return SlideshowSideCursorDisplay(f"{cursor_index + 1}/{total}")


JMA_CURSOR_CHIP_FILENAME_MAX = 14


def format_jma_filename_for_chip(filename: str, *, max_len: int = JMA_CURSOR_CHIP_FILENAME_MAX) -> str:
    """Compact JMA filename for the Slideshow cursor chip (#512)."""
    name = str(filename or "").strip()
    if not name or len(name) <= max_len:
        return name
    return f"…{name[-(max_len - 1):]}"


def _format_jma_cursor(cache_dir: Path) -> SlideshowSideCursorDisplay | None:
    cycle = load_jma_cycle(cache_dir)
    if cycle is None:
        return None
    filename = str(cycle.get("filename") or "").strip()
    if not filename:
        return None
    label = format_jma_filename_for_chip(filename)
    return SlideshowSideCursorDisplay(label, tooltip=filename)


def _format_kiriezu_cursor(entry: SourceEntry, cache_dir: Path) -> SlideshowSideCursorDisplay | None:
    preset_id = preset_id_from_notes(entry.notes)
    if not preset_id:
        return None
    try:
        spec = resolve_kiriezu_preset_spec(preset_id)
    except ValueError:
        return None
    cycle = reconcile_kiriezu_cycle(load_kiriezu_cycle(cache_dir), preset_id)
    try:
        cursor_index = int(cycle.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    total = len(spec.maps)
    if total < 1:
        return None
    cursor_index %= total
    return SlideshowSideCursorDisplay(f"{cursor_index + 1}/{total}")


def _format_ndl_keyword_cursor(cache_dir: Path, settings_path: Path | None) -> SlideshowSideCursorDisplay | None:
    keyword = resolve_ndl_keyword(settings_path)
    if not keyword:
        return None
    cycle = reconcile_ndl_search_cycle(load_ndl_search_cycle(cache_dir), keyword)
    batch = load_ndl_search_batch(cache_dir)
    if batch is None:
        return None
    entries = batch.get("entries")
    if not isinstance(entries, list) or not entries:
        return None
    try:
        cursor_index = int(cycle.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    total = len(entries)
    cursor_index %= total
    try:
        hit = int(batch.get("hit") or total)
    except (TypeError, ValueError):
        hit = total
    tooltip = f"search hit {hit}"
    return SlideshowSideCursorDisplay(f"{cursor_index + 1}/{total}", tooltip=tooltip)


def _owner_settings_path(owner: Any) -> Path | None:
    from harite.settings_file import resolve_default_settings_path

    path = getattr(owner, "_settings_path", None)
    if path is not None:
        return Path(path)
    return resolve_default_settings_path()


def format_side_cursor_display(
    *,
    entry: SourceEntry | None,
    source_dir: Path | None,
    owner: Any,
    side: str,
) -> SlideshowSideCursorDisplay | None:
    if source_dir is None:
        return None

    kind = entry.kind if entry is not None else KIND_LOCAL_DIR
    cache_dir = source_dir

    if kind == KIND_LOCAL_DIR:
        return _format_local_dir_cursor(owner, side, source_dir)

    if kind == KIND_CODH_EDO:
        return _format_codh_cursor(cache_dir, owner)

    if kind == KIND_JMA_WEATHER_MAP:
        return _format_jma_cursor(cache_dir)

    if kind == KIND_NDL_KIRIEZU and entry is not None:
        return _format_kiriezu_cursor(entry, cache_dir)

    if kind == KIND_NDL_TSUGIDIGI and entry is not None and source_supports_ndl_keyword(entry):
        return _format_ndl_keyword_cursor(cache_dir, _owner_settings_path(owner))

    return None


def format_slideshow_side_cursor_chip(side: str, display: SlideshowSideCursorDisplay | None) -> str:
    if display is None or not display.label.strip():
        return ""
    side_key = _normalize_side(side)
    return f"{side_key}: {display.label}"


def resolve_slideshow_cursor_displays(
    catalog: Catalog,
    owner: Any,
) -> tuple[SlideshowSideCursorDisplay | None, SlideshowSideCursorDisplay | None]:
    left_entry, left_dir = resolve_slideshow_side_context(catalog, owner, "L")
    right_entry, right_dir = resolve_slideshow_side_context(catalog, owner, "R")
    left = format_side_cursor_display(entry=left_entry, source_dir=left_dir, owner=owner, side="L")
    right = format_side_cursor_display(entry=right_entry, source_dir=right_dir, owner=owner, side="R")
    return left, right

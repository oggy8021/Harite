"""CODH remote slideshow: index cache, cursor persistence, and tick image fetch."""

from __future__ import annotations

from dataclasses import dataclass
import json
import random
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from harite.local_time import local_now_iso
from harite.sources import Catalog, SourceEntry, get_source
from harite.sources_remote import (
    CODH_SEARCH_URL_TEMPLATE,
    KIND_CODH_EDO,
    CacheWriteResult,
    _CODH_PRESET_SEARCH,
    _CodhSearchSpec,
    _http_get_bytes,
    _http_get_json,
    _write_latest_cache,
    preset_id_from_notes,
    remote_image_outcome_fields,
    resolve_codh_keyword,
)

CODH_INDEX_FILENAME = "codh-index.json"
CODH_CYCLE_FILENAME = "codh-cycle.json"
CODH_INDEX_VERSION = 1
CODH_PAGE_LIMIT = 50

CodhSyncPick = str
CODH_SYNC_REFRESH = "refresh"
CODH_SYNC_RESUME = "resume"


@dataclass(frozen=True)
class CodhSyncContext:
    cache_dir: Path
    spec: _CodhSearchSpec
    metadata_value: str | None
    query_key: str


def resolve_codh_sync_context(entry: SourceEntry) -> CodhSyncContext:
    preset_id = preset_id_from_notes(entry.notes)
    if preset_id is None:
        raise ValueError("CODH sync requires harite-preset marker in notes")
    spec = _CODH_PRESET_SEARCH.get(preset_id)
    if spec is None:
        raise ValueError(f"unsupported CODH preset for sync: {preset_id}")

    metadata_value: str | None = spec.metadata_value
    if spec.keyword_from_settings:
        metadata_value = resolve_codh_keyword()

    return CodhSyncContext(
        cache_dir=Path(entry.path),
        spec=spec,
        metadata_value=metadata_value,
        query_key=codh_query_key(spec, metadata_value),
    )


def codh_query_key(spec: _CodhSearchSpec, metadata_value: str | None) -> str:
    parts = [spec.indexer]
    if spec.keyword_where and metadata_value:
        parts.append(f"where:{metadata_value}")
    elif spec.metadata_label and metadata_value:
        parts.append(f"meta:{spec.metadata_label}={metadata_value}")
    return "|".join(parts)


def _codh_search_query(
    spec: _CodhSearchSpec,
    *,
    start: int | None = None,
    limit: int = 1,
    metadata_value: str | None = None,
) -> str:
    params: list[tuple[str, str]] = [
        ("select", "canvas"),
        ("from", "canvas,curation"),
        ("limit", str(limit)),
    ]
    if start is not None:
        params.append(("start", str(start)))
    effective_value = metadata_value if metadata_value is not None else spec.metadata_value
    if spec.keyword_where and effective_value:
        params.append(("where", effective_value))
    elif spec.metadata_label and effective_value:
        params.append(("where_metadata_label", spec.metadata_label))
        params.append(("where_metadata_value", effective_value))
    return urlencode(params)


def _normalize_codh_thumbnail_url(thumbnail: str) -> str:
    return thumbnail.replace("/200,/", "/max/")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_codh_index(cache_dir: Path) -> dict[str, Any] | None:
    path = cache_dir / CODH_INDEX_FILENAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return None
    return payload


def load_codh_cycle(cache_dir: Path) -> dict[str, Any] | None:
    path = cache_dir / CODH_CYCLE_FILENAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def save_codh_cycle(cache_dir: Path, cycle: dict[str, Any]) -> None:
    cycle = dict(cycle)
    cycle["updated_at"] = local_now_iso()
    _atomic_write_json(cache_dir / CODH_CYCLE_FILENAME, cycle)


def _default_cycle(query_key: str, *, mode: str = "sequential") -> dict[str, Any]:
    return {
        "query_key": query_key,
        "mode": mode,
        "index": 0,
        "previous_image_url": "",
    }


def reconcile_codh_cycle(cycle: dict[str, Any] | None, index: dict[str, Any]) -> dict[str, Any]:
    query_key = str(index.get("query_key") or "")
    entries = index.get("entries")
    total = len(entries) if isinstance(entries, list) else 0
    if total < 1:
        raise ValueError("CODH index has no entries")

    if cycle is None or str(cycle.get("query_key") or "") != query_key:
        return _default_cycle(query_key)

    normalized = dict(cycle)
    normalized["query_key"] = query_key
    try:
        cursor_index = int(normalized.get("index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    normalized["index"] = cursor_index % total
    if not isinstance(normalized.get("previous_image_url"), str):
        normalized["previous_image_url"] = ""
    return normalized


def build_codh_index(ctx: CodhSyncContext, *, source_id: str | None = None) -> dict[str, Any]:
    from harite.slideshow_op_log import log_slideshow_op

    base = CODH_SEARCH_URL_TEMPLATE.format(indexer=ctx.spec.indexer)
    probe_url = f"{base}?{_codh_search_query(ctx.spec, start=0, limit=1, metadata_value=ctx.metadata_value)}"
    log_slideshow_op(
        "CODH_INDEX_PROBE",
        source_id=source_id,
        query_key=ctx.query_key,
        url=probe_url,
    )
    probe = _http_get_json(probe_url)
    if not isinstance(probe, dict):
        raise ValueError("invalid CODH search response")
    total = int(probe.get("total") or 0)
    if total < 1:
        raise ValueError("CODH search returned no canvases")

    entries: list[dict[str, str]] = []
    start = 0
    while start < total:
        page_url = (
            f"{base}?{_codh_search_query(ctx.spec, start=start, limit=CODH_PAGE_LIMIT, metadata_value=ctx.metadata_value)}"
        )
        log_slideshow_op(
            "CODH_INDEX_PAGE",
            source_id=source_id,
            query_key=ctx.query_key,
            start=start,
            url=page_url,
        )
        payload = _http_get_json(page_url)
        if not isinstance(payload, dict):
            raise ValueError("invalid CODH search response")
        results = payload.get("results")
        if not isinstance(results, list) or not results:
            break
        for item in results:
            if not isinstance(item, dict):
                continue
            thumbnail = item.get("canvasThumbnail")
            if not isinstance(thumbnail, str) or not thumbnail.strip():
                continue
            entries.append({"image_url": _normalize_codh_thumbnail_url(thumbnail)})
        start += CODH_PAGE_LIMIT

    if not entries:
        raise ValueError("CODH index build returned no thumbnails")

    index_payload = {
        "version": CODH_INDEX_VERSION,
        "query_key": ctx.query_key,
        "total": total,
        "built_at": local_now_iso(),
        "entries": entries,
    }
    _atomic_write_json(ctx.cache_dir / CODH_INDEX_FILENAME, index_payload)
    log_slideshow_op(
        "CODH_INDEX_BUILT",
        ok=True,
        source_id=source_id,
        query_key=ctx.query_key,
        total=total,
        entries=len(entries),
    )
    return index_payload


def ensure_codh_index(
    ctx: CodhSyncContext,
    *,
    force_rebuild: bool,
    source_id: str | None = None,
) -> dict[str, Any]:
    if not force_rebuild:
        existing = load_codh_index(ctx.cache_dir)
        if existing is not None and str(existing.get("query_key") or "") == ctx.query_key:
            return existing
    return build_codh_index(ctx, source_id=source_id)


def _entry_urls(index: dict[str, Any]) -> list[str]:
    entries = index.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("CODH index has no entries")
    urls: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        url = entry.get("image_url")
        if isinstance(url, str) and url.strip():
            urls.append(url)
    if not urls:
        raise ValueError("CODH index has no entries")
    return urls


def pick_codh_url_at_cursor(index: dict[str, Any], cycle: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    urls = _entry_urls(index)
    try:
        cursor_index = int(cycle.get("index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    selected_index = cursor_index % len(urls)
    url = urls[selected_index]
    updated = dict(cycle)
    updated["previous_image_url"] = url
    return url, updated


def advance_codh_cursor(
    index: dict[str, Any],
    cycle: dict[str, Any],
    mode: str,
    *,
    rng: random.Random | None = None,
) -> tuple[str, dict[str, Any]]:
    urls = _entry_urls(index)
    normalized_mode = mode.lower().strip()
    updated = dict(cycle)
    try:
        cursor_index = int(updated.get("index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    previous = str(updated.get("previous_image_url") or "")

    if normalized_mode == "sequential":
        selected_index = cursor_index % len(urls)
        url = urls[selected_index]
        updated["index"] = cursor_index + 1
        updated["previous_image_url"] = url
        return url, updated

    if normalized_mode == "random":
        chooser = rng if rng is not None else random
        if len(urls) > 1 and previous in urls:
            candidates = [candidate for candidate in urls if candidate != previous]
            url = chooser.choice(candidates)
        else:
            url = chooser.choice(urls)
        updated["previous_image_url"] = url
        return url, updated

    raise ValueError("mode must be one of: sequential, random")


def codh_random_refresh_cycle(index: dict[str, Any], cycle: dict[str, Any] | None) -> dict[str, Any]:
    urls = _entry_urls(index)
    query_key = str(index.get("query_key") or "")
    pick_index = random.randint(0, len(urls) - 1)
    refreshed = _default_cycle(query_key, mode=str((cycle or {}).get("mode") or "sequential"))
    refreshed["index"] = pick_index
    refreshed["previous_image_url"] = urls[pick_index]
    return refreshed


def fetch_codh_image(
    cache_dir: Path,
    image_url: str,
    *,
    source_id: str | None = None,
    phase: str | None = None,
) -> tuple[bool, CacheWriteResult | None]:
    from harite.slideshow_op_log import log_slideshow_op

    try:
        image_bytes = _http_get_bytes(image_url)
    except ValueError as exc:
        log_slideshow_op(
            "CODH_IMAGE_GET",
            ok=False,
            source_id=source_id,
            phase=phase,
            error=str(exc),
            **remote_image_outcome_fields(
                image_fetched=False,
                cache_written=False,
                url=image_url,
                skip_reason="image_fetch_failed",
            ),
        )
        return False, None
    write_result = _write_latest_cache(cache_dir, image_bytes, url=image_url)
    log_slideshow_op(
        "CODH_IMAGE_GET",
        ok=True,
        source_id=source_id,
        phase=phase,
        **remote_image_outcome_fields(
            image_fetched=True,
            cache_written=True,
            write=write_result,
            url=image_url,
        ),
    )
    return True, write_result


def codh_sync_with_pick(
    ctx: CodhSyncContext,
    pick: CodhSyncPick,
    *,
    source_id: str | None = None,
) -> None:
    from harite.slideshow_op_log import log_slideshow_op

    force_rebuild = pick == CODH_SYNC_REFRESH
    log_slideshow_op(
        "CODH_SYNC_PICK",
        source_id=source_id,
        pick=pick,
        query_key=ctx.query_key,
        force_rebuild=force_rebuild,
    )
    index = ensure_codh_index(ctx, force_rebuild=force_rebuild, source_id=source_id)
    cycle = load_codh_cycle(ctx.cache_dir)

    if pick == CODH_SYNC_REFRESH:
        cycle = codh_random_refresh_cycle(index, cycle)
        image_url = str(cycle["previous_image_url"])
    else:
        cycle = reconcile_codh_cycle(cycle, index)
        image_url, cycle = pick_codh_url_at_cursor(index, cycle)

    log_slideshow_op(
        "CODH_IMAGE_URL",
        source_id=source_id,
        pick=pick,
        url=image_url,
        cursor_index=cycle.get("index"),
    )
    fetched, _write_result = fetch_codh_image(
        ctx.cache_dir,
        image_url,
        source_id=source_id,
        phase="sync",
    )
    if not fetched:
        raise ValueError(f"remote fetch failed for CODH image: {image_url}")
    save_codh_cycle(ctx.cache_dir, cycle)


def codh_slideshow_tick(catalog: Catalog, source_id: str, mode: str) -> bool:
    from harite.slideshow_op_log import log_slideshow_op

    entry = get_source(catalog, source_id)
    if entry is None or entry.kind != KIND_CODH_EDO:
        log_slideshow_op(
            "CODH_TICK",
            ok=False,
            source_id=source_id,
            mode=mode,
            reason="missing or non-CODH source",
        )
        return False

    ctx = resolve_codh_sync_context(entry)
    index = load_codh_index(ctx.cache_dir)
    if index is None or str(index.get("query_key") or "") != ctx.query_key:
        log_slideshow_op(
            "CODH_TICK",
            ok=False,
            source_id=source_id,
            mode=mode,
            query_key=ctx.query_key,
            reason="index missing or query_key mismatch",
        )
        return False

    cycle = reconcile_codh_cycle(load_codh_cycle(ctx.cache_dir), index)
    image_url, cycle = advance_codh_cursor(index, cycle, mode)
    log_slideshow_op(
        "CODH_TICK_CURSOR",
        source_id=source_id,
        mode=mode,
        url=image_url,
        cursor_index=cycle.get("index"),
    )
    fetched, write_result = fetch_codh_image(
        ctx.cache_dir,
        image_url,
        source_id=source_id,
        phase="tick",
    )
    if not fetched:
        log_slideshow_op(
            "CODH_TICK",
            ok=False,
            source_id=source_id,
            mode=mode,
            reason="image fetch failed",
            **remote_image_outcome_fields(
                image_fetched=False,
                cache_written=False,
                url=image_url,
                skip_reason="image_fetch_failed",
            ),
        )
        return False
    cycle["mode"] = mode.lower().strip()
    save_codh_cycle(ctx.cache_dir, cycle)
    log_slideshow_op(
        "CODH_TICK",
        ok=True,
        source_id=source_id,
        mode=mode,
        **remote_image_outcome_fields(
            image_fetched=True,
            cache_written=True,
            write=write_result,
            url=image_url,
        ),
    )
    return True


def resolve_codh_source_id_for_path(catalog: Catalog, source_dir: Path) -> str | None:
    try:
        resolved = source_dir.resolve()
    except OSError:
        resolved = source_dir
    for entry in catalog.sources:
        if entry.kind != KIND_CODH_EDO:
            continue
        try:
            if Path(entry.path).resolve() == resolved:
                return entry.id
        except OSError:
            continue
    return None

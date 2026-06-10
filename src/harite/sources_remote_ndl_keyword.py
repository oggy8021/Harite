"""NDL searchbytext keyword preset: batch fetch, cursor cycle, and tick sync."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from harite.local_time import local_now_iso
from harite.sources import Catalog, get_source
from harite.sources_remote import (
    NDL_IIIF_FETCH_MAX_ATTEMPTS,
    NDL_SEARCHBYTEXT_URL,
    CacheWriteResult,
    _http_get_json,
    _ndl_fetch_iiif_image_bytes,
    _ndl_iiif_url,
    _write_latest_cache,
    preset_id_from_notes,
    remote_image_outcome_fields,
    resolve_ndl_keyword,
)

NDL_SEARCH_BATCH_FILENAME = "ndl-search-batch.json"
NDL_SEARCH_CYCLE_FILENAME = "ndl-search-cycle.json"
NDL_SEARCH_PAGE_SIZE = 20


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_ndl_search_batch(cache_dir: Path) -> dict[str, Any] | None:
    path = cache_dir / NDL_SEARCH_BATCH_FILENAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def save_ndl_search_batch(cache_dir: Path, batch: dict[str, Any]) -> None:
    _atomic_write_json(cache_dir / NDL_SEARCH_BATCH_FILENAME, batch)


def load_ndl_search_cycle(cache_dir: Path) -> dict[str, Any] | None:
    path = cache_dir / NDL_SEARCH_CYCLE_FILENAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def save_ndl_search_cycle(cache_dir: Path, cycle: dict[str, Any]) -> None:
    updated = dict(cycle)
    updated["updated_at"] = local_now_iso()
    _atomic_write_json(cache_dir / NDL_SEARCH_CYCLE_FILENAME, updated)


def _default_cycle(keyword_key: str) -> dict[str, Any]:
    return {
        "keyword_key": keyword_key,
        "from": 0,
        "cursor_index": 0,
    }


def reconcile_ndl_search_cycle(cycle: dict[str, Any] | None, keyword_key: str) -> dict[str, Any]:
    if cycle is None or str(cycle.get("keyword_key") or "") != keyword_key:
        return _default_cycle(keyword_key)
    normalized = dict(cycle)
    normalized["keyword_key"] = keyword_key
    try:
        from_offset = int(normalized.get("from") or 0)
    except (TypeError, ValueError):
        from_offset = 0
    try:
        cursor_index = int(normalized.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    normalized["from"] = max(0, from_offset)
    normalized["cursor_index"] = max(0, cursor_index)
    return normalized


def ndl_searchbytext_url(keyword: str, *, from_offset: int, size: int) -> str:
    query = urlencode(
        [
            ("keyword2vec", keyword),
            ("size", str(size)),
            ("from", str(from_offset)),
        ]
    )
    return f"{NDL_SEARCHBYTEXT_URL}?{query}"


def _parse_search_payload(payload: Any) -> tuple[list[dict[str, Any]], int, int]:
    if not isinstance(payload, dict):
        raise ValueError("NDL searchbytext API returned invalid JSON")
    candidates = payload.get("list")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("NDL searchbytext API returned no results")
    try:
        hit = int(payload.get("hit") or len(candidates))
    except (TypeError, ValueError):
        hit = len(candidates)
    try:
        from_offset = int(payload.get("from") or 0)
    except (TypeError, ValueError):
        from_offset = 0
    entries = [item for item in candidates if isinstance(item, dict)]
    if not entries:
        raise ValueError("NDL searchbytext API returned no results")
    return entries, hit, from_offset


def fetch_ndl_search_batch(
    keyword: str,
    *,
    from_offset: int,
    size: int = NDL_SEARCH_PAGE_SIZE,
    source_id: str | None = None,
) -> dict[str, Any]:
    from harite.slideshow_op_log import log_slideshow_op

    meta_url = ndl_searchbytext_url(keyword, from_offset=from_offset, size=size)
    log_slideshow_op(
        "NDL_META_URL",
        source_id=source_id,
        preset_id="ndl-search-keyword",
        url=meta_url,
        from_offset=from_offset,
        size=size,
    )
    payload = _http_get_json(meta_url)
    entries, hit, response_from = _parse_search_payload(payload)
    batch = {
        "keyword_key": keyword,
        "from": response_from,
        "hit": hit,
        "size": size,
        "entries": entries,
        "fetched_at": local_now_iso(),
    }
    log_slideshow_op(
        "NDL_SEARCH_BATCH",
        ok=True,
        source_id=source_id,
        preset_id="ndl-search-keyword",
        keyword=keyword,
        from_offset=response_from,
        size=size,
        hit=hit,
        entries=len(entries),
    )
    return batch


def _batch_matches_cycle(batch: dict[str, Any] | None, cycle: dict[str, Any], keyword_key: str) -> bool:
    if batch is None:
        return False
    if str(batch.get("keyword_key") or "") != keyword_key:
        return False
    try:
        batch_from = int(batch.get("from") or -1)
        cycle_from = int(cycle.get("from") or -2)
    except (TypeError, ValueError):
        return False
    return batch_from == cycle_from


def ensure_ndl_search_batch(
    cache_dir: Path,
    keyword: str,
    cycle: dict[str, Any],
    *,
    source_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    keyword_key = keyword
    batch = load_ndl_search_batch(cache_dir)
    if _batch_matches_cycle(batch, cycle, keyword_key):
        return batch, cycle
    from_offset = int(cycle.get("from") or 0)
    batch = fetch_ndl_search_batch(
        keyword,
        from_offset=from_offset,
        source_id=source_id,
    )
    save_ndl_search_batch(cache_dir, batch)
    cycle = dict(cycle)
    try:
        cursor_index = int(cycle.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    cycle["from"] = int(batch.get("from") or from_offset)
    cycle["cursor_index"] = min(cursor_index, max(len(batch.get("entries") or []) - 1, 0))
    return batch, cycle


def _batch_entries(batch: dict[str, Any]) -> list[dict[str, Any]]:
    entries = batch.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("NDL search batch has no entries")
    return [item for item in entries if isinstance(item, dict)]


def pick_ndl_search_illustration(batch: dict[str, Any], cycle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], int]:
    entries = _batch_entries(batch)
    try:
        cursor_index = int(cycle.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    selected_index = cursor_index % len(entries)
    updated = dict(cycle)
    updated["cursor_index"] = selected_index
    return entries[selected_index], updated, selected_index


def advance_ndl_search_cycle(batch: dict[str, Any], cycle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], bool]:
    """Advance cursor for tick; returns (cycle, batch, needs_refetch)."""
    entries = _batch_entries(batch)
    try:
        hit = int(batch.get("hit") or len(entries))
    except (TypeError, ValueError):
        hit = len(entries)
    try:
        from_offset = int(cycle.get("from") or batch.get("from") or 0)
    except (TypeError, ValueError):
        from_offset = 0
    try:
        cursor_index = int(cycle.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0

    next_cursor = cursor_index + 1
    updated = dict(cycle)
    if next_cursor < len(entries):
        updated["cursor_index"] = next_cursor
        return updated, batch, False

    next_from = from_offset + len(entries)
    if next_from >= hit:
        next_from = 0
    updated["from"] = next_from
    updated["cursor_index"] = 0
    return updated, batch, True


def reset_ndl_search_cycle(cache_dir: Path, keyword_key: str) -> dict[str, Any]:
    batch_path = cache_dir / NDL_SEARCH_BATCH_FILENAME
    if batch_path.is_file():
        batch_path.unlink()
    cycle = _default_cycle(keyword_key)
    save_ndl_search_cycle(cache_dir, cycle)
    return cycle


def _fetch_illustration_with_retries(
    cache_dir: Path,
    batch: dict[str, Any],
    cycle: dict[str, Any],
    *,
    source_id: str | None,
    preset_id: str,
    start_index: int,
) -> tuple[CacheWriteResult, dict[str, Any], dict[str, Any], int]:
    from harite.slideshow_op_log import log_slideshow_op

    entries = _batch_entries(batch)
    last_skipped_url: str | None = None
    selected_index = start_index
    for attempt in range(1, NDL_IIIF_FETCH_MAX_ATTEMPTS + 1):
        if selected_index >= len(entries):
            break
        illustration = entries[selected_index]
        iiif_url = _ndl_iiif_url(illustration)
        log_slideshow_op(
            "NDL_IIIF_URL",
            source_id=source_id,
            preset_id=preset_id,
            attempt=attempt,
            url=iiif_url,
            cursor_index=selected_index,
            from_offset=batch.get("from"),
        )
        image_bytes = _ndl_fetch_iiif_image_bytes(iiif_url)
        if image_bytes is not None:
            log_slideshow_op(
                "NDL_IIIF_GET",
                ok=True,
                source_id=source_id,
                preset_id=preset_id,
                attempt=attempt,
                url=iiif_url,
                bytes=len(image_bytes),
                cursor_index=selected_index,
            )
            write_result = _write_latest_cache(cache_dir, image_bytes, url=iiif_url)
            log_slideshow_op(
                "NDL_CACHE_WRITE",
                ok=True,
                source_id=source_id,
                preset_id=preset_id,
                attempt=attempt,
                cursor_index=selected_index,
                from_offset=batch.get("from"),
                **remote_image_outcome_fields(
                    image_fetched=True,
                    cache_written=True,
                    write=write_result,
                    url=iiif_url,
                ),
            )
            updated_cycle = dict(cycle)
            updated_cycle["cursor_index"] = selected_index
            return write_result, batch, updated_cycle, selected_index
        log_slideshow_op(
            "NDL_IIIF_GET",
            ok=False,
            source_id=source_id,
            preset_id=preset_id,
            attempt=attempt,
            url=iiif_url,
            cursor_index=selected_index,
            reason="HTTP 404/400",
        )
        last_skipped_url = iiif_url
        selected_index += 1

    suffix = (
        f" (last skipped IIIF: {last_skipped_url})"
        if last_skipped_url
        else ""
    )
    raise ValueError(
        "remote fetch failed: NDL IIIF unavailable after "
        f"{NDL_IIIF_FETCH_MAX_ATTEMPTS} illustration attempts{suffix}"
    )


def ndl_search_keyword_sync(
    catalog: Catalog,
    source_id: str,
    *,
    advance_cursor: bool,
    force_reset: bool = False,
) -> CacheWriteResult:
    from harite.slideshow_op_log import log_slideshow_op

    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    preset_id = preset_id_from_notes(entry.notes)
    if preset_id is None:
        raise ValueError("NDL sync requires harite-preset marker in notes")

    keyword = resolve_ndl_keyword()
    keyword_key = keyword
    cache_dir = Path(entry.path)

    if force_reset:
        cycle = reset_ndl_search_cycle(cache_dir, keyword_key)
    else:
        cycle = reconcile_ndl_search_cycle(load_ndl_search_cycle(cache_dir), keyword_key)

    batch, cycle = ensure_ndl_search_batch(
        cache_dir,
        keyword,
        cycle,
        source_id=source_id,
    )

    if advance_cursor:
        cycle, batch, needs_refetch = advance_ndl_search_cycle(batch, cycle)
        if needs_refetch:
            batch_path = cache_dir / NDL_SEARCH_BATCH_FILENAME
            if batch_path.is_file():
                batch_path.unlink()
            batch, cycle = ensure_ndl_search_batch(
                cache_dir,
                keyword,
                cycle,
                source_id=source_id,
            )

    illustration, cycle, cursor_index = pick_ndl_search_illustration(batch, cycle)
    log_slideshow_op(
        "NDL_SEARCH_PICK",
        source_id=source_id,
        preset_id=preset_id,
        keyword=keyword,
        cursor_index=cursor_index,
        from_offset=batch.get("from"),
        pid=illustration.get("pid"),
        page=illustration.get("page"),
    )

    write_result, batch, cycle, _selected_index = _fetch_illustration_with_retries(
        cache_dir,
        batch,
        cycle,
        source_id=source_id,
        preset_id=preset_id,
        start_index=cursor_index,
    )
    save_ndl_search_cycle(cache_dir, cycle)
    return write_result


def ndl_search_keyword_slideshow_tick(
    catalog: Catalog,
    source_id: str,
    *,
    side: str | None = None,
) -> bool:
    from harite.slideshow_op_log import log_slideshow_op

    try:
        write_result = ndl_search_keyword_sync(
            catalog,
            source_id,
            advance_cursor=True,
        )
    except ValueError as exc:
        log_slideshow_op(
            "NDL_TICK",
            ok=False,
            side=side,
            source_id=source_id,
            phase="tick",
            **remote_image_outcome_fields(
                image_fetched=False,
                cache_written=False,
                skip_reason=str(exc),
            ),
        )
        return False
    log_slideshow_op(
        "NDL_TICK",
        ok=True,
        side=side,
        source_id=source_id,
        phase="tick",
        **remote_image_outcome_fields(
            image_fetched=True,
            cache_written=True,
            write=write_result,
        ),
    )
    return True

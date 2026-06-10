"""JMA remote slideshow: filename tracking and interval tick sync."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from harite.local_time import local_now_iso
from harite.sources import Catalog, SourceEntry, get_source
from harite.sources_remote import (
    JMA_LIST_URL,
    JMA_PNG_URL,
    KIND_JMA_WEATHER_MAP,
    CacheWriteResult,
    _JMA_PRESET_FILENAME_TAG,
    _JMA_PRESET_LIST_KEYS,
    _http_get_bytes,
    _http_get_json,
    _jma_pick_filename,
    _write_latest_cache,
    preset_id_from_notes,
    remote_image_outcome_fields,
)

JMA_CYCLE_FILENAME = "jma-cycle.json"


@dataclass(frozen=True)
class JmaSyncContext:
    cache_dir: Path
    preset_id: str
    list_path: tuple[str, ...]
    filename_tag: str


def resolve_jma_sync_context(entry: SourceEntry) -> JmaSyncContext:
    preset_id = preset_id_from_notes(entry.notes)
    if preset_id is None:
        raise ValueError("JMA sync requires harite-preset marker in notes")
    list_path = _JMA_PRESET_LIST_KEYS.get(preset_id)
    filename_tag = _JMA_PRESET_FILENAME_TAG.get(preset_id)
    if list_path is None or filename_tag is None:
        raise ValueError(f"unsupported JMA preset for sync: {preset_id}")
    return JmaSyncContext(
        cache_dir=Path(entry.path),
        preset_id=preset_id,
        list_path=list_path,
        filename_tag=filename_tag,
    )


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_jma_cycle(cache_dir: Path) -> dict[str, Any] | None:
    path = cache_dir / JMA_CYCLE_FILENAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def save_jma_cycle(cache_dir: Path, *, preset_id: str, filename: str) -> None:
    _atomic_write_json(
        cache_dir / JMA_CYCLE_FILENAME,
        {
            "preset_id": preset_id,
            "filename": filename,
            "updated_at": local_now_iso(),
        },
    )


def jma_fetch_current_filename(ctx: JmaSyncContext) -> str:
    list_payload = _http_get_json(JMA_LIST_URL)
    if not isinstance(list_payload, dict):
        raise ValueError("invalid list.json from JMA")
    return _jma_pick_filename(
        list_payload,
        ctx.list_path,
        filename_tag=ctx.filename_tag,
    )


def jma_fetch_png_to_latest(
    ctx: JmaSyncContext,
    filename: str,
) -> tuple[bool, CacheWriteResult | None]:
    from harite.slideshow_op_log import log_slideshow_op

    png_url = JMA_PNG_URL.format(filename=filename)
    try:
        png_bytes = _http_get_bytes(png_url)
    except ValueError as exc:
        log_slideshow_op(
            "JMA_IMAGE_GET",
            ok=False,
            preset_id=ctx.preset_id,
            phase="fetch",
            error=str(exc),
            **remote_image_outcome_fields(
                image_fetched=False,
                cache_written=False,
                filename=filename,
                url=png_url,
                skip_reason="png_fetch_failed",
            ),
        )
        return False, None
    write_result = _write_latest_cache(ctx.cache_dir, png_bytes, url=png_url)
    log_slideshow_op(
        "JMA_CACHE_WRITE",
        ok=True,
        preset_id=ctx.preset_id,
        **remote_image_outcome_fields(
            image_fetched=True,
            cache_written=True,
            write=write_result,
            url=png_url,
            filename=filename,
        ),
    )
    return True, write_result


def jma_sync_refresh(ctx: JmaSyncContext) -> None:
    filename = jma_fetch_current_filename(ctx)
    fetched, _write_result = jma_fetch_png_to_latest(ctx, filename)
    if not fetched:
        raise ValueError(f"remote fetch failed for JMA image: {filename}")
    save_jma_cycle(ctx.cache_dir, preset_id=ctx.preset_id, filename=filename)


def _jma_latest_had_previous(ctx: JmaSyncContext) -> bool:
    return (ctx.cache_dir / "latest.png").is_file()


def _log_jma_tick(
    *,
    ok: bool,
    source_id: str,
    side: str | None,
    filename: str,
    image_fetched: bool,
    cache_written: bool,
    write: CacheWriteResult | None = None,
    url: str | None = None,
    skip_reason: str | None = None,
    had_previous: bool | None = None,
) -> None:
    from harite.slideshow_op_log import log_slideshow_op

    log_slideshow_op(
        "JMA_TICK",
        ok=ok,
        side=side,
        source_id=source_id,
        phase="tick",
        **remote_image_outcome_fields(
            image_fetched=image_fetched,
            cache_written=cache_written,
            write=write,
            url=url,
            filename=filename,
            skip_reason=skip_reason,
            had_previous=had_previous,
        ),
    )


def jma_slideshow_tick(
    catalog: Catalog,
    source_id: str,
    *,
    side: str | None = None,
) -> bool:
    entry = get_source(catalog, source_id)
    if entry is None or entry.kind != KIND_JMA_WEATHER_MAP:
        return False

    ctx = resolve_jma_sync_context(entry)
    try:
        filename = jma_fetch_current_filename(ctx)
    except ValueError:
        _log_jma_tick(
            ok=False,
            source_id=source_id,
            side=side,
            filename="",
            image_fetched=False,
            cache_written=False,
            skip_reason="list_json_failed",
        )
        return False

    cycle = load_jma_cycle(ctx.cache_dir)
    if (
        cycle is not None
        and str(cycle.get("preset_id") or "") == ctx.preset_id
        and str(cycle.get("filename") or "") == filename
    ):
        _log_jma_tick(
            ok=True,
            source_id=source_id,
            side=side,
            filename=filename,
            image_fetched=False,
            cache_written=False,
            skip_reason="filename_unchanged",
            had_previous=_jma_latest_had_previous(ctx),
        )
        return True

    fetched, write_result = jma_fetch_png_to_latest(ctx, filename)
    if not fetched:
        _log_jma_tick(
            ok=False,
            source_id=source_id,
            side=side,
            filename=filename,
            image_fetched=False,
            cache_written=False,
            skip_reason="png_fetch_failed",
            had_previous=_jma_latest_had_previous(ctx),
        )
        return False
    save_jma_cycle(ctx.cache_dir, preset_id=ctx.preset_id, filename=filename)
    _log_jma_tick(
        ok=True,
        source_id=source_id,
        side=side,
        filename=filename,
        image_fetched=True,
        cache_written=True,
        write=write_result,
        url=JMA_PNG_URL.format(filename=filename),
    )
    return True


def resolve_jma_source_id_for_path(catalog: Catalog, source_dir: Path) -> str | None:
    try:
        resolved = source_dir.resolve()
    except OSError:
        resolved = source_dir
    for entry in catalog.sources:
        if entry.kind != KIND_JMA_WEATHER_MAP:
            continue
        try:
            if Path(entry.path).resolve() == resolved:
                return entry.id
        except OSError:
            continue
    return None

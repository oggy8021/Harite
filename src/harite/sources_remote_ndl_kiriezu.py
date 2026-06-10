"""NDL Edo kiriezu (尾張屋版) full-map preset: static catalog, cursor cycle, IIIF fetch."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from harite.local_time import local_now_iso
from harite.sources import Catalog, get_source
from harite.sources_remote import (
    NDL_IIIF_FETCH_MAX_ATTEMPTS,
    CacheWriteResult,
    _http_get_bytes,
    _http_get_json,
    _write_latest_cache,
    preset_id_from_notes,
    remote_image_outcome_fields,
)

NDL_KIRIEZU_CYCLE_FILENAME = "ndl-kiriezu-cycle.json"
NDL_KIRIEZU_MANIFEST_CACHE_FILENAME = "ndl-kiriezu-manifest-cache.json"
NDL_KIRIEZU_IIIF_WIDTH = 1200
NDL_KIRIEZU_MANIFEST_URL_TEMPLATE = "https://dl.ndl.go.jp/api/iiif/{pid}/manifest.json"
NDL_KIRIEZU_IMAGE_URL_TEMPLATE = (
    "https://dl.ndl.go.jp/api/iiif/{pid}/{canvas}/full/{width},/0/default.jpg"
)

_KIRIEZU_ATTRIBUTION = (
    "出典：国立国会図書館デジタルコレクション「江戸切絵図」（尾張屋版）。"
    "地図索引：CODH 江戸マップ（https://codh.rois.ac.jp/edo-maps/）"
)


@dataclass(frozen=True)
class KiriezuMapEntry:
    pid: str
    label: str


@dataclass(frozen=True)
class KiriezuPresetSpec:
    preset_id: str
    maps: tuple[KiriezuMapEntry, ...]


# owariya 一覧準拠（29 pid）。正本: https://codh.rois.ac.jp/edo-maps/owariya/
_KIRIEZU_ALL_MAPS: tuple[KiriezuMapEntry, ...] = (
    KiriezuMapEntry("1286656", "御江戸大名小路絵図"),
    KiriezuMapEntry("1286660", "築地八町堀日本橋南絵図"),
    KiriezuMapEntry("1286645", "日本橋北神田浜町絵図"),
    KiriezuMapEntry("1286662", "芝愛宕下絵図"),
    KiriezuMapEntry("1286663", "芝高輪辺絵図"),
    KiriezuMapEntry("1286659", "駿河台小川町絵図"),
    KiriezuMapEntry("1286657", "外桜田永田町絵図"),
    KiriezuMapEntry("1286668", "四ツ谷絵図"),
    KiriezuMapEntry("1286666", "赤坂絵図"),
    KiriezuMapEntry("1286658", "御江戸番町絵図"),
    KiriezuMapEntry("1286665", "麻布絵図"),
    KiriezuMapEntry("1286670", "市ヶ谷牛込絵図"),
    KiriezuMapEntry("1286207", "下谷絵図"),
    KiriezuMapEntry("1286680", "深川絵図"),
    KiriezuMapEntry("1286672", "小日向絵図"),
    KiriezuMapEntry("1286679", "本所絵図"),
    KiriezuMapEntry("1286209", "浅草御蔵前辺図"),
    KiriezuMapEntry("1286667", "青山渋谷絵図"),
    KiriezuMapEntry("1286673", "音羽絵図"),
    KiriezuMapEntry("1286676", "本郷湯島絵図"),
    KiriezuMapEntry("1286208", "今戸箕輪浅草絵図"),
    KiriezuMapEntry("1286675", "駒込絵図"),
    KiriezuMapEntry("1286674", "巣鴨絵図"),
    KiriezuMapEntry("1286671", "大久保絵図"),
    KiriezuMapEntry("1286664", "目黒白銀絵図"),
    KiriezuMapEntry("1154577", "小石川絵図"),
    KiriezuMapEntry("1286678", "隅田川向島絵図"),
    KiriezuMapEntry("1286677", "根岸谷中辺絵図"),
    KiriezuMapEntry("1286669", "内藤新宿千駄ヶ谷絵図"),
)

_KIRIEZU_BY_PID: dict[str, KiriezuMapEntry] = {entry.pid: entry for entry in _KIRIEZU_ALL_MAPS}


def _maps_for_pids(pids: tuple[str, ...]) -> tuple[KiriezuMapEntry, ...]:
    return tuple(_KIRIEZU_BY_PID[pid] for pid in pids)


def _preset(preset_id: str, pids: tuple[str, ...]) -> KiriezuPresetSpec:
    return KiriezuPresetSpec(preset_id, _maps_for_pids(pids))


_KIRIEZU_PRESET_SPECS: dict[str, KiriezuPresetSpec] = {
    # A — 全区巡回
    "ndl-kiriezu-all": _preset(
        "ndl-kiriezu-all",
        tuple(entry.pid for entry in _KIRIEZU_ALL_MAPS),
    ),
    # B — 大グループ（地域のまとまり）
    "ndl-kiriezu-group-shitamachi": _preset(
        "ndl-kiriezu-group-shitamachi",
        (
            "1286208",
            "1286209",
            "1286680",
            "1286679",
            "1286678",
            "1286207",
            "1286677",
        ),
    ),
    "ndl-kiriezu-group-yamanote": _preset(
        "ndl-kiriezu-group-yamanote",
        (
            "1286662",
            "1286663",
            "1286666",
            "1286665",
            "1286667",
            "1286670",
            "1286668",
            "1286675",
            "1286674",
            "1286669",
        ),
    ),
    "ndl-kiriezu-group-nihonbashi": _preset(
        "ndl-kiriezu-group-nihonbashi",
        ("1286660", "1286645", "1286656", "1286658"),
    ),
    "ndl-kiriezu-group-north": _preset(
        "ndl-kiriezu-group-north",
        ("1286657", "1286659", "1286676", "1154577", "1286673"),
    ),
    "ndl-kiriezu-group-south": _preset(
        "ndl-kiriezu-group-south",
        ("1286671", "1286664", "1286672"),
    ),
    # C — 単エリア（雰囲気固定）
    "ndl-kiriezu-asakusa": _preset("ndl-kiriezu-asakusa", ("1286208", "1286209")),
    "ndl-kiriezu-nihonbashi": _preset("ndl-kiriezu-nihonbashi", ("1286660", "1286645")),
    "ndl-kiriezu-shiba": _preset("ndl-kiriezu-shiba", ("1286662", "1286663")),
    "ndl-kiriezu-ueno": _preset("ndl-kiriezu-ueno", ("1286676", "1286207")),
    "ndl-kiriezu-fukagawa": _preset("ndl-kiriezu-fukagawa", ("1286680",)),
    "ndl-kiriezu-honjo": _preset("ndl-kiriezu-honjo", ("1286679",)),
    "ndl-kiriezu-yamanote": _preset(
        "ndl-kiriezu-yamanote",
        ("1286666", "1286665", "1286670"),
    ),
}

KIRIEZU_PRESET_IDS = frozenset(_KIRIEZU_PRESET_SPECS.keys())


def is_kiriezu_preset(preset_id: str | None) -> bool:
    return preset_id in KIRIEZU_PRESET_IDS if preset_id else False


def resolve_kiriezu_preset_spec(preset_id: str) -> KiriezuPresetSpec:
    spec = _KIRIEZU_PRESET_SPECS.get(preset_id)
    if spec is None:
        raise ValueError(f"unsupported kiriezu preset: {preset_id}")
    return spec


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_kiriezu_cycle(cache_dir: Path) -> dict[str, Any] | None:
    path = cache_dir / NDL_KIRIEZU_CYCLE_FILENAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def save_kiriezu_cycle(cache_dir: Path, cycle: dict[str, Any]) -> None:
    updated = dict(cycle)
    updated["updated_at"] = local_now_iso()
    _atomic_write_json(cache_dir / NDL_KIRIEZU_CYCLE_FILENAME, updated)


def _default_cycle(preset_id: str) -> dict[str, Any]:
    return {"preset_id": preset_id, "cursor_index": 0}


def reconcile_kiriezu_cycle(cycle: dict[str, Any] | None, preset_id: str) -> dict[str, Any]:
    if cycle is None or str(cycle.get("preset_id") or "") != preset_id:
        return _default_cycle(preset_id)
    normalized = dict(cycle)
    normalized["preset_id"] = preset_id
    try:
        cursor_index = int(normalized.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    normalized["cursor_index"] = max(0, cursor_index)
    return normalized


def load_manifest_cache(cache_dir: Path) -> dict[str, str]:
    path = cache_dir / NDL_KIRIEZU_MANIFEST_CACHE_FILENAME
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    canvases = payload.get("canvases")
    if not isinstance(canvases, dict):
        return {}
    result: dict[str, str] = {}
    for pid, canvas in canvases.items():
        if isinstance(pid, str) and isinstance(canvas, str) and pid.strip() and canvas.strip():
            result[pid] = canvas
    return result


def save_manifest_cache(cache_dir: Path, canvases: dict[str, str]) -> None:
    _atomic_write_json(
        cache_dir / NDL_KIRIEZU_MANIFEST_CACHE_FILENAME,
        {"canvases": dict(canvases)},
    )


def canvas_id_from_manifest(manifest: dict[str, Any], pid: str) -> str:
    sequences = manifest.get("sequences")
    if isinstance(sequences, list) and sequences:
        first_seq = sequences[0]
        if isinstance(first_seq, dict):
            canvases = first_seq.get("canvases")
            if isinstance(canvases, list) and canvases:
                canvas = canvases[0]
                if isinstance(canvas, dict):
                    images = canvas.get("images")
                    if isinstance(images, list) and images:
                        image = images[0]
                        if isinstance(image, dict):
                            resource = image.get("resource")
                            if isinstance(resource, dict):
                                service = resource.get("service")
                                if isinstance(service, dict):
                                    service_id = service.get("@id")
                                    if isinstance(service_id, str) and "/iiif/" in service_id:
                                        return service_id.rstrip("/").split("/")[-1]
                                at_id = resource.get("@id")
                                if isinstance(at_id, str) and "/iiif/" in at_id:
                                    tail = at_id.split("/iiif/", 1)[-1]
                                    parts = tail.split("/")
                                    if len(parts) >= 2:
                                        return parts[1]
    raise ValueError(f"cannot resolve IIIF canvas for kiriezu pid {pid}")


def resolve_kiriezu_canvas_id(cache_dir: Path, pid: str) -> str:
    cache = load_manifest_cache(cache_dir)
    cached = cache.get(pid)
    if cached:
        return cached
    manifest_url = NDL_KIRIEZU_MANIFEST_URL_TEMPLATE.format(pid=pid)
    manifest = _http_get_json(manifest_url)
    if not isinstance(manifest, dict):
        raise ValueError(f"invalid IIIF manifest for pid {pid}")
    canvas_id = canvas_id_from_manifest(manifest, pid)
    cache[pid] = canvas_id
    save_manifest_cache(cache_dir, cache)
    return canvas_id


def kiriezu_iiif_url(cache_dir: Path, entry: KiriezuMapEntry) -> str:
    canvas_id = resolve_kiriezu_canvas_id(cache_dir, entry.pid)
    return NDL_KIRIEZU_IMAGE_URL_TEMPLATE.format(
        pid=entry.pid,
        canvas=canvas_id,
        width=NDL_KIRIEZU_IIIF_WIDTH,
    )


def pick_kiriezu_entry(
    spec: KiriezuPresetSpec,
    cycle: dict[str, Any],
) -> tuple[KiriezuMapEntry, int]:
    try:
        cursor_index = int(cycle.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    selected_index = cursor_index % len(spec.maps)
    return spec.maps[selected_index], selected_index


def advance_kiriezu_cycle(spec: KiriezuPresetSpec, cycle: dict[str, Any]) -> dict[str, Any]:
    updated = dict(cycle)
    try:
        cursor_index = int(updated.get("cursor_index") or 0)
    except (TypeError, ValueError):
        cursor_index = 0
    updated["cursor_index"] = (cursor_index + 1) % len(spec.maps)
    return updated


def _fetch_kiriezu_image_with_retries(
    cache_dir: Path,
    spec: KiriezuPresetSpec,
    cycle: dict[str, Any],
    *,
    source_id: str | None,
    preset_id: str,
    start_index: int,
) -> tuple[CacheWriteResult, dict[str, Any], KiriezuMapEntry, int]:
    from harite.slideshow_op_log import log_slideshow_op

    total = len(spec.maps)
    last_error_url: str | None = None
    for offset in range(min(total, NDL_IIIF_FETCH_MAX_ATTEMPTS)):
        selected_index = (start_index + offset) % total
        entry = spec.maps[selected_index]
        iiif_url = kiriezu_iiif_url(cache_dir, entry)
        log_slideshow_op(
            "NDL_KIRIEZU_IIIF_URL",
            source_id=source_id,
            preset_id=preset_id,
            attempt=offset + 1,
            url=iiif_url,
            pid=entry.pid,
            map_label=entry.label,
            cursor_index=selected_index,
        )
        try:
            image_bytes = _http_get_bytes(iiif_url)
        except ValueError as exc:
            log_slideshow_op(
                "NDL_KIRIEZU_IIIF_GET",
                ok=False,
                source_id=source_id,
                preset_id=preset_id,
                attempt=offset + 1,
                url=iiif_url,
                pid=entry.pid,
                reason=str(exc),
            )
            last_error_url = iiif_url
            continue
        log_slideshow_op(
            "NDL_KIRIEZU_IIIF_GET",
            ok=True,
            source_id=source_id,
            preset_id=preset_id,
            attempt=offset + 1,
            url=iiif_url,
            pid=entry.pid,
            bytes=len(image_bytes),
        )
        write_result = _write_latest_cache(cache_dir, image_bytes, url=iiif_url)
        log_slideshow_op(
            "NDL_KIRIEZU_CACHE_WRITE",
            ok=True,
            source_id=source_id,
            preset_id=preset_id,
            pid=entry.pid,
            map_label=entry.label,
            cursor_index=selected_index,
            **remote_image_outcome_fields(
                image_fetched=True,
                cache_written=True,
                write=write_result,
                url=iiif_url,
            ),
        )
        updated_cycle = dict(cycle)
        updated_cycle["cursor_index"] = selected_index
        return write_result, updated_cycle, entry, selected_index

    suffix = f" (last url: {last_error_url})" if last_error_url else ""
    raise ValueError(
        "remote fetch failed: NDL kiriezu IIIF unavailable after "
        f"{NDL_IIIF_FETCH_MAX_ATTEMPTS} attempts{suffix}"
    )


def ndl_kiriezu_sync(
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
        raise ValueError("kiriezu sync requires harite-preset marker in notes")
    spec = resolve_kiriezu_preset_spec(preset_id)
    cache_dir = Path(entry.path)

    if force_reset:
        cycle = _default_cycle(preset_id)
    else:
        cycle = reconcile_kiriezu_cycle(load_kiriezu_cycle(cache_dir), preset_id)

    if advance_cursor:
        cycle = advance_kiriezu_cycle(spec, cycle)

    map_entry, cursor_index = pick_kiriezu_entry(spec, cycle)
    log_slideshow_op(
        "NDL_KIRIEZU_PICK",
        source_id=source_id,
        preset_id=preset_id,
        pid=map_entry.pid,
        map_label=map_entry.label,
        cursor_index=cursor_index,
    )

    write_result, cycle, _entry, _selected_index = _fetch_kiriezu_image_with_retries(
        cache_dir,
        spec,
        cycle,
        source_id=source_id,
        preset_id=preset_id,
        start_index=cursor_index,
    )
    save_kiriezu_cycle(cache_dir, cycle)
    return write_result


def ndl_kiriezu_slideshow_tick(
    catalog: Catalog,
    source_id: str,
    *,
    side: str | None = None,
) -> bool:
    from harite.slideshow_op_log import log_slideshow_op

    try:
        write_result = ndl_kiriezu_sync(
            catalog,
            source_id,
            advance_cursor=True,
            force_reset=False,
        )
    except ValueError as exc:
        log_slideshow_op(
            "NDL_KIRIEZU_TICK",
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
        "NDL_KIRIEZU_TICK",
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

"""Remote wallpaper sources: cache layout, provider registry, and JMA sync."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import random
import re
import sys
from typing import Any, Callable, Literal, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from harite.sources import (
    MAX_SOURCES,
    Catalog,
    SourceEntry,
    get_source,
    _new_id,
    _source_name_taken,
    _validate_name,
    _validate_notes,
)

REMOTE_KIND_RE = re.compile(r"^remote-[a-z0-9]+(?:-[a-z0-9]+)*$")
KIND_JMA_WEATHER_MAP = "remote-jma-weather-map"
KIND_NDL_TSUGIDIGI = "remote-ndl-tsugidigi"
KIND_CODH_EDO = "remote-codh-edo"

JMA_LIST_URL = "https://www.jma.go.jp/bosai/weather_map/data/list.json"
NDL_RANDOM_FACET_URL = "https://lab.ndl.go.jp/dl/api/illustration/randomwithfacet"
NDL_IIIF_FETCH_MAX_ATTEMPTS = 5
NDL_IIIF_TEMPLATE = (
    "https://dl.ndl.go.jp/api/iiif/{pid}/{page}/pct:{x},{y},{w},{h}/max/0/default.jpg"
)
CODH_SEARCH_URL_TEMPLATE = "https://mp.ex.nii.ac.jp/api/{indexer}/search"
JMA_PNG_URL = "https://www.jma.go.jp/bosai/weather_map/data/png/{filename}"

PRESET_MARKER_PREFIX = "harite-preset:"
CODH_KEYWORD_NOTE_PREFIX = "harite-codh-keyword:"
CODH_KEYWORD_SETTINGS_KEY = "codh_keyword"
CODH_KEYWORD_MAX_LEN = 16
CODH_KEYWORD_DEFAULT = "桜"
CODH_KEYWORD_PRESET_IDS = frozenset(
    {
        "codh-edo-spots-keyword",
        "codh-edo-shops-keyword",
    }
)

_JMA_PRESET_LIST_KEYS: dict[str, tuple[str, ...]] = {
    "jma-near-color": ("near", "now"),
    "jma-asia-color": ("asia", "now"),
    "jma-near-monochrome": ("near_monochrome", "now"),
    "jma-asia-monochrome": ("asia_monochrome", "now"),
}

_JMA_PRESET_FILENAME_TAG: dict[str, str] = {
    "jma-near-color": "JRcolor",
    "jma-asia-color": "JRcolor",
    "jma-near-monochrome": "JRjmahp",
    "jma-asia-monochrome": "JRjmahp",
}

_NDL_PRESET_FACET_TAG: dict[str, str] = {
    "ndl-random-map": "graphic_map",
    "ndl-random-illust": "graphic_illust",
    "ndl-random-illustcolor": "graphic_illustcolor",
    "ndl-random-indoor": "picture_indoor",
    "ndl-random-landmark": "picture_landmark",
    "ndl-random-outdoor": "picture_outdoor",
}

@dataclass(frozen=True)
class _CodhSearchSpec:
    indexer: str
    metadata_label: str | None = None
    metadata_value: str | None = None
    random_pick: bool = False
    keyword_from_settings: bool = False
    # User-entered text: Canvas Indexer ``where`` (partial match). Exact
    # ``where_metadata_*`` only hits the キーワード facet (e.g. 桜) and misses
    # place names (飛鳥山) stored under 名所（統一地名）.
    keyword_where: bool = False


CodhSyncPick = Literal["refresh", "resume"]
_CODH_SYNC_PICK: ContextVar[CodhSyncPick] = ContextVar("codh_sync_pick", default="refresh")

_CODH_PRESET_SEARCH: dict[str, _CodhSearchSpec] = {
    "codh-edo-spots-keyword": _CodhSearchSpec(
        indexer="edo-spots",
        random_pick=True,
        keyword_from_settings=True,
        keyword_where=True,
    ),
    "codh-edo-shops-keyword": _CodhSearchSpec(
        indexer="edo-shops",
        random_pick=True,
        keyword_from_settings=True,
        keyword_where=True,
    ),
    "codh-edo-spots-random": _CodhSearchSpec(indexer="edo-spots", random_pick=True),
    "codh-edo-shops-random": _CodhSearchSpec(indexer="edo-shops", random_pick=True),
}


class RemoteProvider(Protocol):
    kind: str

    def sync(self, catalog: Catalog, source_id: str) -> None: ...


@dataclass(frozen=True)
class _RegisteredProvider:
    kind: str
    sync: Callable[[Catalog, str], None]
    default_notes: str | None = None


_providers: dict[str, _RegisteredProvider] = {}


def is_remote_kind(kind: str) -> bool:
    return bool(REMOTE_KIND_RE.fullmatch(kind))


def register_remote_provider(
    kind: str,
    provider: RemoteProvider | _RegisteredProvider,
    *,
    default_notes: str | None = None,
) -> None:
    if not is_remote_kind(kind):
        raise ValueError(f"invalid remote kind: {kind}")
    if isinstance(provider, _RegisteredProvider):
        registered = provider
    else:
        registered = _RegisteredProvider(
            kind=provider.kind,
            sync=provider.sync,
            default_notes=getattr(provider, "default_notes", default_notes),
        )
    if registered.kind != kind:
        raise ValueError("provider kind must match registration key")
    _providers[kind] = registered


def get_remote_provider(kind: str) -> _RegisteredProvider:
    try:
        return _providers[kind]
    except KeyError as exc:
        raise ValueError(f"no remote provider registered for kind: {kind}") from exc


def resolve_default_remote_cache_root() -> Path:
    if sys.platform.startswith("linux"):
        cache_home = Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache"))
        root = cache_home / "harite" / "remote-cache"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        roaming = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        root = roaming / "harite" / "remote-cache"
    else:
        root = Path.home() / ".cache" / "harite" / "remote-cache"

    try:
        root.mkdir(parents=True, exist_ok=True)
        return root
    except OSError:
        if not sys.platform == "win32":
            raise ValueError("remote cache root is not accessible") from None

    profile = os.environ.get("USERPROFILE")
    if not profile:
        raise ValueError("remote cache root is not accessible")
    fallback = Path(profile) / "Pictures" / "harite_cache_dir" / "remote-cache"
    try:
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
    except OSError as exc:
        raise ValueError("remote cache root is not accessible") from exc


def remote_cache_dir_for_source(source_id: str, *, cache_root: Path | None = None) -> Path:
    root = cache_root or resolve_default_remote_cache_root()
    return root / source_id


def ensure_remote_cache_dir(entry: SourceEntry) -> Path:
    """Ensure the catalog path for a remote source exists (e.g. after manual cache clear)."""
    from harite.sources import normalize_directory_path

    cache_dir = Path(entry.path)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return normalize_directory_path(cache_dir)


def prune_orphan_remote_cache_dirs(
    catalog: Catalog,
    *,
    cache_root: Path | None = None,
) -> int:
    """Delete ``{cache_root}/{uuid}/`` directories not tied to a catalog remote source."""
    root = cache_root or resolve_default_remote_cache_root()
    if not root.is_dir():
        return 0

    active_ids = {entry.id for entry in catalog.sources if is_remote_kind(entry.kind)}
    removed = 0
    for child in root.iterdir():
        if not child.is_dir() or child.name in active_ids:
            continue
        try:
            shutil.rmtree(child)
        except OSError:
            continue
        removed += 1
    return removed


def preset_id_from_notes(notes: str) -> str | None:
    for line in notes.splitlines():
        stripped = line.strip()
        if stripped.startswith(PRESET_MARKER_PREFIX):
            return stripped[len(PRESET_MARKER_PREFIX) :].strip()
    return None


def is_codh_keyword_preset(preset_id: str | None) -> bool:
    return preset_id in CODH_KEYWORD_PRESET_IDS if preset_id else False


def codh_keyword_from_notes(notes: str) -> str | None:
    for line in notes.splitlines():
        stripped = line.strip()
        if stripped.startswith(CODH_KEYWORD_NOTE_PREFIX):
            value = stripped[len(CODH_KEYWORD_NOTE_PREFIX) :].strip()
            return value or None
    return None


def validate_codh_keyword(keyword: str) -> str:
    value = str(keyword).strip()
    if not value:
        raise ValueError("CODH keyword cannot be empty")
    if len(value) > CODH_KEYWORD_MAX_LEN:
        raise ValueError(f"CODH keyword exceeds {CODH_KEYWORD_MAX_LEN} characters")
    if "\n" in value or "\r" in value:
        raise ValueError("CODH keyword cannot contain newlines")
    return value


def strip_codh_keyword_from_notes(notes: str) -> str:
    kept: list[str] = []
    for line in notes.splitlines():
        stripped = line.strip()
        if stripped.startswith(CODH_KEYWORD_NOTE_PREFIX):
            continue
        if stripped:
            kept.append(stripped)
    return "\n".join(kept)


def codh_keyword_from_settings(settings: dict[str, Any]) -> str:
    raw = settings.get(CODH_KEYWORD_SETTINGS_KEY)
    if raw is None:
        return CODH_KEYWORD_DEFAULT
    text = str(raw).strip()
    if not text:
        return CODH_KEYWORD_DEFAULT
    return validate_codh_keyword(text)


def apply_codh_keyword_to_settings(settings: dict[str, Any], keyword: str) -> dict[str, Any]:
    updated = dict(settings)
    updated[CODH_KEYWORD_SETTINGS_KEY] = validate_codh_keyword(keyword)
    return updated


def save_codh_keyword_settings(settings_path: Path, keyword: str) -> Path:
    from harite.settings_file import patch_settings_value

    return patch_settings_value(settings_path, CODH_KEYWORD_SETTINGS_KEY, validate_codh_keyword(keyword))


def load_codh_keyword_settings(settings_path: Path | None = None) -> dict[str, Any]:
    from harite.settings_file import load_settings, resolve_default_settings_path

    path = settings_path or resolve_default_settings_path()
    if not path.exists():
        return {}
    return load_settings(path)


def resolve_codh_keyword(settings_path: Path | None = None) -> str:
    return codh_keyword_from_settings(load_codh_keyword_settings(settings_path))


def migrate_codh_keyword_notes_to_settings(
    catalog: Catalog,
    settings: dict[str, Any],
) -> tuple[dict[str, Any], bool, bool]:
    """Move legacy per-source keyword notes into settings and strip notes lines."""
    from harite.sources import list_sources, update_source

    catalog_changed = False
    settings_changed = False
    migrated: str | None = None
    for entry in list_sources(catalog):
        if not source_supports_codh_keyword(entry):
            continue
        keyword = codh_keyword_from_notes(entry.notes)
        stripped = strip_codh_keyword_from_notes(entry.notes)
        if stripped != entry.notes:
            update_source(catalog, entry.id, notes=stripped)
            catalog_changed = True
        if keyword and migrated is None:
            migrated = keyword
    if migrated is not None and CODH_KEYWORD_SETTINGS_KEY not in settings:
        settings = apply_codh_keyword_to_settings(settings, migrated)
        settings_changed = True
    return settings, catalog_changed, settings_changed


def source_supports_codh_keyword(entry: SourceEntry) -> bool:
    if entry.kind != KIND_CODH_EDO:
        return False
    return is_codh_keyword_preset(preset_id_from_notes(entry.notes))


def add_remote_source(
    catalog: Catalog,
    *,
    name: str,
    kind: str,
    notes: str | None = None,
    cache_root: Path | None = None,
) -> SourceEntry:
    if len(catalog.sources) >= MAX_SOURCES:
        raise ValueError(f"source count exceeds {MAX_SOURCES}")
    if not is_remote_kind(kind):
        raise ValueError(f"invalid remote kind: {kind}")
    get_remote_provider(kind)

    validated_name = _validate_name(name, label="source")
    if _source_name_taken(catalog, validated_name):
        raise ValueError(f"duplicate source name: {validated_name}")

    source_id = _new_id(catalog)
    cache_dir = remote_cache_dir_for_source(source_id, cache_root=cache_root)
    cache_dir.mkdir(parents=True, exist_ok=True)
    entry = SourceEntry(
        id=source_id,
        name=validated_name,
        kind=kind,
        path=str(cache_dir.resolve()),
        notes=_validate_notes(notes),
    )
    catalog.sources.append(entry)
    return entry


def format_remote_sync_error(
    side: str | None,
    source_name: str,
    cause: BaseException,
) -> ValueError:
    """Build a ValueError that names the slideshow side and source when sync fails."""
    label = f"{side} — {source_name}" if side else source_name
    return ValueError(f"remote sync failed ({label}): {cause}")


def sync_remote_source(
    catalog: Catalog,
    source_id: str,
    *,
    cache_root: Path | None = None,
    codh_sync_pick: CodhSyncPick = "refresh",
) -> None:
    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    if not is_remote_kind(entry.kind):
        raise ValueError(f"source is not remote: {source_id}")
    effective_root = cache_root
    if effective_root is None and entry.path.strip():
        effective_root = Path(entry.path).parent
    provider = get_remote_provider(entry.kind)
    token = _CODH_SYNC_PICK.set(codh_sync_pick)
    try:
        provider.sync(catalog, source_id)
    finally:
        _CODH_SYNC_PICK.reset(token)
    expected = remote_cache_dir_for_source(source_id, cache_root=effective_root)
    entry.path = str(expected.resolve())


def _http_get_bytes(url: str) -> bytes:
    payload = _http_get_bytes_or_none_on_404(url)
    if payload is None:
        raise ValueError(f"remote fetch failed: HTTP 404 for {url}")
    return payload


def _http_get_bytes_or_none_on_404(url: str) -> bytes | None:
    try:
        with urlopen(url, timeout=30) as response:
            return response.read()
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise ValueError(f"remote fetch failed: HTTP {exc.code} for {url}") from exc
    except URLError as exc:
        raise ValueError(f"remote fetch failed: {exc}") from exc


def _http_get_json(url: str) -> Any:
    raw = _http_get_bytes(url)
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON from remote: {url}") from exc


def _write_latest_cache(cache_dir: Path, image_bytes: bytes, *, url: str) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    if "default.jpg" in url or url.rstrip("/").endswith(".jpg"):
        latest = cache_dir / "latest.jpg"
        stale_globs = ("*.png", "*.jpg", "*.jpeg")
    else:
        latest = cache_dir / "latest.png"
        stale_globs = ("*.png", "*.jpg", "*.jpeg")
    latest.write_bytes(image_bytes)
    for pattern in stale_globs:
        for stale in cache_dir.glob(pattern):
            if stale != latest:
                stale.unlink(missing_ok=True)


def _jma_pick_filename(
    list_payload: dict[str, Any],
    list_path: tuple[str, ...],
    *,
    filename_tag: str,
) -> str:
    node: Any = list_payload
    for key in list_path:
        if not isinstance(node, dict) or key not in node:
            raise ValueError(f"list.json missing path: {'.'.join(list_path)}")
        node = node[key]
    if not isinstance(node, list):
        raise ValueError(f"list.json path is not an array: {'.'.join(list_path)}")
    candidates = [str(item) for item in node if filename_tag in str(item)]
    if not candidates:
        raise ValueError(f"no {filename_tag} weather map filename in list.json")
    return candidates[-1]


def _jma_sync(catalog: Catalog, source_id: str) -> None:
    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    preset_id = preset_id_from_notes(entry.notes)
    if preset_id is None:
        raise ValueError("JMA sync requires harite-preset marker in notes")
    list_path = _JMA_PRESET_LIST_KEYS.get(preset_id)
    filename_tag = _JMA_PRESET_FILENAME_TAG.get(preset_id)
    if list_path is None or filename_tag is None:
        raise ValueError(f"unsupported JMA preset for sync: {preset_id}")

    raw = _http_get_bytes(JMA_LIST_URL)
    try:
        list_payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid list.json from JMA") from exc
    if not isinstance(list_payload, dict):
        raise ValueError("invalid list.json from JMA")

    filename = _jma_pick_filename(list_payload, list_path, filename_tag=filename_tag)
    png_url = JMA_PNG_URL.format(filename=filename)
    png_bytes = _http_get_bytes(png_url)

    _write_latest_cache(Path(entry.path), png_bytes, url=png_url)

    provider = _providers[KIND_JMA_WEATHER_MAP]
    if not entry.notes.strip() and provider.default_notes:
        entry.notes = _validate_notes(provider.default_notes)


def _ndl_illustration_url(preset_id: str) -> str:
    facet = _NDL_PRESET_FACET_TAG.get(preset_id)
    if not facet:
        raise ValueError(f"unsupported NDL preset for sync: {preset_id}")
    query = urlencode([("size", "1"), ("f-graphictags.tagname", facet)])
    return f"{NDL_RANDOM_FACET_URL}?{query}"


def _ndl_iiif_url(illustration: dict[str, Any]) -> str:
    try:
        pid = str(illustration["pid"])
        page = int(illustration["page"])
        x = float(illustration["x"])
        y = float(illustration["y"])
        w = float(illustration["w"])
        h = float(illustration["h"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid illustration payload from NDL") from exc
    return NDL_IIIF_TEMPLATE.format(pid=pid, page=page, x=x, y=y, w=w, h=h)


def _ndl_fetch_iiif_image_bytes(url: str) -> bytes | None:
    """Return image bytes, or None when NDL IIIF rejects the candidate (404/400)."""
    try:
        with urlopen(url, timeout=30) as response:
            return response.read()
    except HTTPError as exc:
        if exc.code in (404, 400):
            return None
        raise ValueError(f"remote fetch failed: HTTP {exc.code} for {url}") from exc
    except URLError as exc:
        raise ValueError(f"remote fetch failed: {exc}") from exc


def _ndl_sync(catalog: Catalog, source_id: str) -> None:
    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    preset_id = preset_id_from_notes(entry.notes)
    if preset_id is None:
        raise ValueError("NDL sync requires harite-preset marker in notes")

    meta_url = _ndl_illustration_url(preset_id)
    last_skipped_url: str | None = None
    for _attempt in range(NDL_IIIF_FETCH_MAX_ATTEMPTS):
        payload = _http_get_json(meta_url)
        if not isinstance(payload, list) or not payload:
            raise ValueError("NDL illustration API returned no results")
        iiif_url = _ndl_iiif_url(payload[0])
        image_bytes = _ndl_fetch_iiif_image_bytes(iiif_url)
        if image_bytes is not None:
            _write_latest_cache(Path(entry.path), image_bytes, url=iiif_url)
            return
        last_skipped_url = iiif_url
    suffix = (
        f" (last skipped IIIF: {last_skipped_url})"
        if last_skipped_url
        else ""
    )
    raise ValueError(
        "remote fetch failed: NDL IIIF unavailable after "
        f"{NDL_IIIF_FETCH_MAX_ATTEMPTS} illustration attempts{suffix}"
    )


def _codh_search_query(
    spec: _CodhSearchSpec,
    *,
    start: int | None = None,
    metadata_value: str | None = None,
) -> str:
    params: list[tuple[str, str]] = [
        ("select", "canvas"),
        ("from", "canvas,curation"),
        ("limit", "1"),
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


def _codh_pick_thumbnail_url(
    spec: _CodhSearchSpec,
    *,
    metadata_value: str | None = None,
) -> str:
    base = CODH_SEARCH_URL_TEMPLATE.format(indexer=spec.indexer)
    if spec.random_pick:
        # Must pass limit=1: omitting limit returns the full corpus (~1300+ canvases, multi-MB JSON).
        probe_url = f"{base}?{_codh_search_query(spec, start=0, metadata_value=metadata_value)}"
        probe = _http_get_json(probe_url)
        if not isinstance(probe, dict):
            raise ValueError("invalid CODH search response")
        total = int(probe.get("total") or 0)
        if total < 1:
            raise ValueError("CODH search returned no canvases")
        start = random.randint(0, total - 1)
        search_url = f"{base}?{_codh_search_query(spec, start=start, metadata_value=metadata_value)}"
    else:
        search_url = f"{base}?{_codh_search_query(spec, metadata_value=metadata_value)}"
    payload = _http_get_json(search_url)
    if not isinstance(payload, dict):
        raise ValueError("invalid CODH search response")
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        raise ValueError("CODH search returned no results")
    first = results[0]
    if not isinstance(first, dict):
        raise ValueError("invalid CODH canvas result")
    thumbnail = first.get("canvasThumbnail")
    if not isinstance(thumbnail, str) or not thumbnail.strip():
        raise ValueError("CODH result missing canvasThumbnail")
    return thumbnail.replace("/200,/", "/max/")


def _codh_sync(catalog: Catalog, source_id: str) -> None:
    from harite.sources_remote_codh import (
        CODH_SYNC_REFRESH,
        CODH_SYNC_RESUME,
        codh_sync_with_pick,
        resolve_codh_sync_context,
    )

    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    pick = _CODH_SYNC_PICK.get()
    codh_sync_with_pick(
        resolve_codh_sync_context(entry),
        CODH_SYNC_REFRESH if pick == "refresh" else CODH_SYNC_RESUME,
    )


register_remote_provider(
    KIND_JMA_WEATHER_MAP,
    _RegisteredProvider(
        kind=KIND_JMA_WEATHER_MAP,
        sync=_jma_sync,
        default_notes=None,
    ),
)
register_remote_provider(
    KIND_NDL_TSUGIDIGI,
    _RegisteredProvider(
        kind=KIND_NDL_TSUGIDIGI,
        sync=_ndl_sync,
        default_notes=None,
    ),
)
register_remote_provider(
    KIND_CODH_EDO,
    _RegisteredProvider(
        kind=KIND_CODH_EDO,
        sync=_codh_sync,
        default_notes=None,
    ),
)

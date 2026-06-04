"""Remote wallpaper sources: cache layout, provider registry, and JMA sync."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import random
import re
import sys
from typing import Any, Callable, Protocol
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
NDL_RANDOM_URL = "https://lab.ndl.go.jp/dl/api/illustration/random"
NDL_RANDOM_FACET_URL = "https://lab.ndl.go.jp/dl/api/illustration/randomwithfacet"
NDL_IIIF_TEMPLATE = (
    "https://dl.ndl.go.jp/api/iiif/{pid}/{page}/pct:{x},{y},{w},{h}/max/0/default.jpg"
)
CODH_SEARCH_URL_TEMPLATE = "https://mp.ex.nii.ac.jp/api/{indexer}/search"
JMA_PNG_URL = "https://www.jma.go.jp/bosai/weather_map/data/png/{filename}"

PRESET_MARKER_PREFIX = "harite-preset:"

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

_NDL_PRESET_FACET_TAG: dict[str, str | None] = {
    "ndl-random": None,
    "ndl-random-map": "graphic_map",
}

@dataclass(frozen=True)
class _CodhSearchSpec:
    indexer: str
    metadata_label: str | None = None
    metadata_value: str | None = None
    random_pick: bool = False


_CODH_PRESET_SEARCH: dict[str, _CodhSearchSpec] = {
    "codh-edo-spots-sakura": _CodhSearchSpec(
        indexer="edo-spots",
        metadata_label="キーワード",
        metadata_value="桜",
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


def sync_remote_source(
    catalog: Catalog,
    source_id: str,
    *,
    cache_root: Path | None = None,
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
    provider.sync(catalog, source_id)
    expected = remote_cache_dir_for_source(source_id, cache_root=effective_root)
    entry.path = str(expected.resolve())


def _http_get_bytes(url: str) -> bytes:
    try:
        with urlopen(url, timeout=30) as response:
            return response.read()
    except HTTPError as exc:
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
    if facet is None and preset_id not in _NDL_PRESET_FACET_TAG:
        raise ValueError(f"unsupported NDL preset for sync: {preset_id}")
    if facet:
        query = urlencode([("size", "1"), ("f-graphictags.tagname", facet)])
        return f"{NDL_RANDOM_FACET_URL}?{query}"
    return f"{NDL_RANDOM_URL}?size=1"


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


def _ndl_sync(catalog: Catalog, source_id: str) -> None:
    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    preset_id = preset_id_from_notes(entry.notes)
    if preset_id is None:
        raise ValueError("NDL sync requires harite-preset marker in notes")

    meta_url = _ndl_illustration_url(preset_id)
    payload = _http_get_json(meta_url)
    if not isinstance(payload, list) or not payload:
        raise ValueError("NDL illustration API returned no results")
    iiif_url = _ndl_iiif_url(payload[0])
    image_bytes = _http_get_bytes(iiif_url)
    _write_latest_cache(Path(entry.path), image_bytes, url=iiif_url)


def _codh_search_query(spec: _CodhSearchSpec, *, start: int | None = None) -> str:
    params: list[tuple[str, str]] = [
        ("select", "canvas"),
        ("from", "canvas,curation"),
        ("limit", "1"),
    ]
    if start is not None:
        params.append(("start", str(start)))
    if spec.metadata_label and spec.metadata_value:
        params.append(("where_metadata_label", spec.metadata_label))
        params.append(("where_metadata_value", spec.metadata_value))
    return urlencode(params)


def _codh_pick_thumbnail_url(spec: _CodhSearchSpec) -> str:
    base = CODH_SEARCH_URL_TEMPLATE.format(indexer=spec.indexer)
    if spec.random_pick:
        # Must pass limit=1: omitting limit returns the full corpus (~1300+ canvases, multi-MB JSON).
        probe_url = f"{base}?{_codh_search_query(spec, start=0)}"
        probe = _http_get_json(probe_url)
        if not isinstance(probe, dict):
            raise ValueError("invalid CODH search response")
        total = int(probe.get("total") or 0)
        if total < 1:
            raise ValueError("CODH search returned no canvases")
        start = random.randint(0, total - 1)
        search_url = f"{base}?{_codh_search_query(spec, start=start)}"
    else:
        search_url = f"{base}?{_codh_search_query(spec)}"
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
    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    preset_id = preset_id_from_notes(entry.notes)
    if preset_id is None:
        raise ValueError("CODH sync requires harite-preset marker in notes")
    spec = _CODH_PRESET_SEARCH.get(preset_id)
    if spec is None:
        raise ValueError(f"unsupported CODH preset for sync: {preset_id}")

    image_url = _codh_pick_thumbnail_url(spec)
    image_bytes = _http_get_bytes(image_url)
    _write_latest_cache(Path(entry.path), image_bytes, url=image_url)


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

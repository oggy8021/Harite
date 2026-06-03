"""Remote wallpaper sources: cache layout, provider registry, and JMA sync."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Callable, Protocol
from urllib.error import HTTPError, URLError
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

JMA_LIST_URL = "https://www.jma.go.jp/bosai/weather_map/data/list.json"
JMA_PNG_URL = "https://www.jma.go.jp/bosai/weather_map/data/png/{filename}"

PRESET_MARKER_PREFIX = "harite-preset:"

_JMA_PRESET_LIST_KEYS: dict[str, tuple[str, ...]] = {
    "jma-near-color": ("near", "now"),
    "jma-asia-color": ("asia", "now"),
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


def _jma_pick_filename(list_payload: dict[str, Any], list_path: tuple[str, ...]) -> str:
    node: Any = list_payload
    for key in list_path:
        if not isinstance(node, dict) or key not in node:
            raise ValueError(f"list.json missing path: {'.'.join(list_path)}")
        node = node[key]
    if not isinstance(node, list):
        raise ValueError(f"list.json path is not an array: {'.'.join(list_path)}")
    candidates = [str(item) for item in node if "JRcolor" in str(item)]
    if not candidates:
        raise ValueError("no JRcolor weather map filename in list.json")
    return candidates[-1]


def _jma_sync(catalog: Catalog, source_id: str) -> None:
    entry = get_source(catalog, source_id)
    if entry is None:
        raise ValueError(f"unknown source id: {source_id}")
    preset_id = preset_id_from_notes(entry.notes)
    if preset_id is None:
        raise ValueError("JMA sync requires harite-preset marker in notes")
    list_path = _JMA_PRESET_LIST_KEYS.get(preset_id)
    if list_path is None:
        raise ValueError(f"unsupported JMA preset for sync: {preset_id}")

    raw = _http_get_bytes(JMA_LIST_URL)
    try:
        list_payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid list.json from JMA") from exc
    if not isinstance(list_payload, dict):
        raise ValueError("invalid list.json from JMA")

    filename = _jma_pick_filename(list_payload, list_path)
    png_bytes = _http_get_bytes(JMA_PNG_URL.format(filename=filename))

    cache_dir = Path(entry.path)
    cache_dir.mkdir(parents=True, exist_ok=True)
    latest = cache_dir / "latest.png"
    latest.write_bytes(png_bytes)
    for stale in cache_dir.glob("*.png"):
        if stale != latest:
            stale.unlink(missing_ok=True)

    provider = _providers[KIND_JMA_WEATHER_MAP]
    if not entry.notes.strip() and provider.default_notes:
        entry.notes = _validate_notes(provider.default_notes)


register_remote_provider(
    KIND_JMA_WEATHER_MAP,
    _RegisteredProvider(
        kind=KIND_JMA_WEATHER_MAP,
        sync=_jma_sync,
        default_notes=None,
    ),
)

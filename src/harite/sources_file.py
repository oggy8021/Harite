from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any

SOURCES_CATALOG_FILENAME = "harite-sources.json"
LEGACY_SOURCES_CATALOG_FILENAME = "sources.json"


def _harite_config_dir() -> Path:
    if sys.platform.startswith("linux"):
        config_home = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
        return config_home / "harite"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        roaming = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return roaming / "harite"
    return Path.home() / "harite"


def resolve_default_sources_path() -> Path:
    return _harite_config_dir() / SOURCES_CATALOG_FILENAME


def resolve_sources_path_for_load(path: Path | None = None) -> Path:
    """Return path for catalog load (new file, or legacy ``sources.json`` beside it)."""
    target = resolve_default_sources_path() if path is None else Path(path)
    if target.exists():
        return target
    default = resolve_default_sources_path()
    if path is None or target == default:
        legacy = target.parent / LEGACY_SOURCES_CATALOG_FILENAME
        if legacy.exists():
            return legacy
    return target


def load_sources_json(path: Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Sources catalog not found: {p}")
    try:
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON sources catalog: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("sources catalog root must be an object")
    return data


def save_sources_json(path: Path, payload: dict[str, Any]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return p

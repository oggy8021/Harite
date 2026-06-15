from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any


def resolve_default_settings_path() -> Path:
    if sys.platform.startswith("linux"):
        config_home = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
        return config_home / "harite" / "harite-settings.json"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        roaming = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return roaming / "harite" / "harite-settings.json"
    return Path.home() / "harite-settings.json"


def load_settings(path: Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    with p.open("r", encoding="utf-8") as fh:
        raw = fh.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON config: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("settings root must be an object")
    return data


def save_settings(path: Path, settings: dict[str, Any]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(settings, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return p


def patch_settings_value(path: Path, key: str, value: Any) -> Path:
    """Merge a single key into the on-disk settings file without dropping other keys."""
    p = Path(path)
    data: dict[str, Any] = load_settings(p) if p.exists() else {}
    data[key] = value
    return save_settings(p, data)


def merge_patch_only_settings_keys(
    payload: dict[str, Any],
    existing: dict[str, Any],
) -> dict[str, Any]:
    """Keep Manage-only keys when GUI settings save overwrites the file."""
    from harite.sources_remote import CODH_KEYWORD_SETTINGS_KEY, NDL_KEYWORD_SETTINGS_KEY

    merged = dict(payload)
    for key in (CODH_KEYWORD_SETTINGS_KEY, NDL_KEYWORD_SETTINGS_KEY):
        if key not in merged and key in existing:
            merged[key] = existing[key]
    return merged
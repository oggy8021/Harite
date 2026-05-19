from __future__ import annotations

import os
import sys
from importlib.resources import files
from pathlib import Path


def resolve_xdg_applications_dir() -> Path:
    data_home = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
    return data_home / "applications"


def resolve_desktop_entry_path(target_path: Path | None = None) -> Path:
    if target_path is not None:
        return Path(target_path)
    return resolve_xdg_applications_dir() / "harite.desktop"


def resolve_launcher_icon_path() -> Path | None:
    for icon_name in ("harite_app.svg", "harite.svg"):
        candidate = files("harite.gui").joinpath("resources", "icons", "product", icon_name)
        candidate_path = Path(str(candidate))
        if candidate_path.exists():
            return candidate_path
    return None


def build_desktop_entry_text() -> str:
    exec_args = [_quote_exec_arg(str(sys.executable)), "-m", "harite.gui.app"]
    icon_path = resolve_launcher_icon_path()
    icon_value = str(icon_path) if icon_path is not None else "harite"

    lines = [
        "[Desktop Entry]",
        "Version=1.0",
        "Type=Application",
        "Name=Harite",
        "Comment=Generate, arrange, and apply wallpapers for multi-display environments",
        f"Exec={' '.join(exec_args)}",
        f"Icon={icon_value}",
        "Terminal=false",
        "Categories=Graphics;Utility;",
        "StartupNotify=true",
    ]
    return "\n".join(lines) + "\n"


def install_desktop_entry(*, target_path: Path | None = None, overwrite: bool = False) -> Path:
    destination = resolve_desktop_entry_path(target_path)
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Desktop entry already exists: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_desktop_entry_text(), encoding="utf-8")
    return destination


def _quote_exec_arg(value: str) -> str:
    escaped = (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("$", "\\$")
        .replace("`", "\\`")
    )
    if any(character.isspace() for character in escaped) or any(character in escaped for character in ('"', "'", "\\", "$", "`")):
        return f'"{escaped}"'
    return escaped
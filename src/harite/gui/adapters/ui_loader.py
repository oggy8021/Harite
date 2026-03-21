"""Minimal UI loader prototype for Phase 3.

This module intentionally avoids GUI backend imports and only validates that the
staged Glade resource can be parsed and introspected.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class UiLoadResult:
    file_path: Path
    root_tag: str
    widget_count: int
    signal_count: int


def _default_glade_path() -> Path:
    return Path(__file__).resolve().parents[1] / "resources" / "wallpositapplet.glade"


def load_glade_prototype(file_path: Path | None = None) -> UiLoadResult:
    path = file_path or _default_glade_path()
    if not path.exists():
        raise FileNotFoundError(f"ui resource not found: {path}")

    tree = ET.parse(path)
    root = tree.getroot()
    widgets = root.findall(".//widget")
    signals = root.findall(".//signal")

    return UiLoadResult(
        file_path=path,
        root_tag=root.tag,
        widget_count=len(widgets),
        signal_count=len(signals),
    )

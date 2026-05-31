"""Helpers for loading package-internal GUI resources."""

from __future__ import annotations

from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, Iterator


def gui_resource(*path_parts: str):
    """Return a traversable handle for a GUI resource shipped inside the package."""
    resource = files("harite.gui").joinpath("resources", *path_parts)
    if not resource.is_file():
        joined = "/".join(path_parts)
        raise FileNotFoundError(f"GUI resource not found: {joined}")
    return resource


@contextmanager
def gui_resource_path(*path_parts: str) -> Iterator[Path]:
    """Yield a filesystem path for a packaged GUI resource."""
    with as_file(gui_resource(*path_parts)) as resource_path:
        yield resource_path


def set_qt_button_icon(widget: Any, *resource_parts: str) -> None:
    """Attach an SVG icon from the package resources to a Qt widget.

    Uses ``QIcon`` loaded from the SVG file path.  Silently skips if PyQt6 is
    not importable or the resource file is not found.
    """
    try:
        from PyQt6.QtGui import QIcon

        with gui_resource_path(*resource_parts) as icon_path:
            widget.setIcon(QIcon(str(icon_path)))
    except Exception:
        pass
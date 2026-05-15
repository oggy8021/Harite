"""Helpers for loading package-internal GUI resources."""

from __future__ import annotations

from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterator


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
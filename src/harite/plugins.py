"""Plugin registry and wallpaper application plugins.

This module provides a minimal plugin registry and a Windows plugin stub that
applies wallpapers. Plugins must implement `apply(path: str, *, dry_run: bool)`.
"""
from __future__ import annotations

from typing import Callable, Dict, Protocol
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PluginProtocol(Protocol):
    name: str

    def apply(self, path: str, *, dry_run: bool = True) -> bool:
        """Apply the wallpaper located at `path`.

        Return True on success, False on failure.
        """


@dataclass
class PluginEntry:
    name: str
    factory: Callable[[], PluginProtocol]


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, PluginEntry] = {}

    def register(self, name: str):
        def _decorator(factory: Callable[[], PluginProtocol]):
            self._plugins[name] = PluginEntry(name=name, factory=factory)
            logger.debug("Registered plugin: %s", name)
            return factory

        return _decorator

    def get(self, name: str) -> PluginProtocol:
        entry = self._plugins.get(name)
        if entry is None:
            raise KeyError(f"No such plugin: {name}")
        return entry.factory()

    def list(self):
        return list(self._plugins.keys())


registry = PluginRegistry()


class WindowsPlugin:
    name = "windows"

    def apply(self, path: str, *, dry_run: bool = True) -> bool:
        p = Path(path)
        if not p.exists():
            logger.error("Wallpaper file does not exist: %s", path)
            return False
        if dry_run:
            logger.info("Dry-run: would apply wallpaper: %s", path)
            return True

        # Attempt to set Windows wallpaper. This code is intentionally guarded
        # and should only run when the caller explicitly sets `dry_run=False`.
        try:
            import ctypes

            SPI_SETDESKWALLPAPER = 20
            r = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, str(p), 3)
            success = bool(r)
            if not success:
                logger.error("SystemParametersInfoW failed for %s", path)
            return success
        except Exception as exc:  # pragma: no cover - platform specific
            logger.exception("Failed to apply wallpaper: %s", exc)
            return False



@registry.register("windows")
def make_windows_plugin() -> WindowsPlugin:
    return WindowsPlugin()

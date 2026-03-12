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


class MacOSPlugin:
    name = "macos"

    def apply(self, path: str, *, dry_run: bool = True) -> bool:
        p = Path(path)
        if not p.exists():
            logger.error("Wallpaper file does not exist: %s", path)
            return False
        if dry_run:
            logger.info("Dry-run: would apply wallpaper (macOS): %s", path)
            return True

        # Attempt to set macOS wallpaper using AppleScript via osascript.
        try:
            import subprocess

            script = f'tell application "System Events" to set picture of every desktop to "{str(p)}"'
            res = subprocess.run(["osascript", "-e", script], check=False)
            return res.returncode == 0
        except Exception:  # pragma: no cover - platform specific
            logger.exception("Failed to apply macOS wallpaper")
            return False


@registry.register("macos")
def make_macos_plugin() -> MacOSPlugin:
    return MacOSPlugin()


class LinuxPlugin:
    name = "linux"

    def apply(self, path: str, *, dry_run: bool = True) -> bool:
        p = Path(path)
        if not p.exists():
            logger.error("Wallpaper file does not exist: %s", path)
            return False
        if dry_run:
            logger.info("Dry-run: would apply wallpaper (linux): %s", path)
            return True

        # Try common desktop environment commands (gsettings, feh). This is a best-effort
        # and intentionally not guaranteed to work on all distributions / DEs.
        try:
            import shutil
            import subprocess

            if shutil.which("gsettings"):
                # Common for GNOME
                cmd = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{str(p)}"]
                res = subprocess.run(cmd, check=False)
                return res.returncode == 0
            if shutil.which("xfconf-query"):
                # XFCE: try to find and set image properties under xfce4-desktop
                try:
                    list_proc = subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-l"], check=False, capture_output=True, text=True)
                    props = []
                    if list_proc.returncode == 0 and list_proc.stdout:
                        for line in list_proc.stdout.splitlines():
                            line = line.strip()
                            if not line:
                                continue
                            # common properties include names with 'last-image' or 'image'
                            if "image" in line or "last-image" in line:
                                props.append(line)
                    # Prefer workspace-specific last-image entries, then monitor image-paths,
                    # then any last-image / last-single-image fallbacks.
                    props_workspace = [q for q in props if "workspace" in q and "last-image" in q]
                    props_monitor_image = [q for q in props if ("/monitor" in q and "image" in q and "workspace" not in q)]
                    props_last_image = [q for q in props if ("last-image" in q and "workspace" not in q)]
                    props_last_single = [q for q in props if "last-single-image" in q]
                    candidates = props_workspace + props_monitor_image + props_last_image + props_last_single

                    if dry_run:
                        logger.info("Dry-run: xfconf candidates (in order): %s", candidates)
                        # Indicate dry-run succeeded if there are candidates to try
                        if candidates:
                            return True
                    success_any = False
                    for prop in candidates:
                        cmd = ["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", str(p)]
                        logger.info("Running: %s", " ".join(cmd))
                        res = subprocess.run(cmd, check=False)
                        if res.returncode == 0:
                            success_any = True
                            break
                    if success_any:
                        return True
                except Exception:
                    logger.exception("xfconf-query attempt failed")
            if shutil.which("feh"):
                # Lightweight viewers
                cmd = ["feh", "--bg-scale", str(p)]
                res = subprocess.run(cmd, check=False)
                return res.returncode == 0
            logger.error("No known wallpaper setter found on PATH")
            return False
        except Exception:  # pragma: no cover - platform specific
            logger.exception("Failed to apply linux wallpaper")
            return False


@registry.register("linux")
def make_linux_plugin() -> LinuxPlugin:
    return LinuxPlugin()

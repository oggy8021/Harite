"""Plugin registry and wallpaper application plugins.

This module provides a minimal plugin registry and a Windows plugin stub that
applies wallpapers. Plugins must implement `apply(path: str, *, dry_run: bool)`.
"""
from __future__ import annotations

from typing import Callable, Dict, Protocol
from dataclasses import dataclass
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)


def _normalize_identifier(s: str) -> str:
    """Normalize monitor/property names for fuzzy matching.

    Lowercase and strip non-alphanumeric characters so that names like
    "HDMI-1" and "hdmi1" compare equal.
    """
    return re.sub(r"[^a-z0-9]", "", s.lower())


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
        # Support per-monitor mapping dicts: {monitor_name: path}
        is_map = isinstance(path, dict)
        if is_map:
            mapping = path
        else:
            p = Path(path)
            if not p.exists():
                logger.error("Wallpaper file does not exist: %s", path)
                return False
            if dry_run:
                logger.info("Dry-run: would apply wallpaper (linux): %s", path)
                # When running a dry-run and the file exists, report success immediately.
                # Older behavior attempted to enumerate xfconf candidates for logging,
                # but tests and CI expect dry-run to be considered successful even when
                # no external wallpaper setters are present on PATH.
                return True

        # Try common desktop environment commands (gsettings, feh). This is a best-effort
        # and intentionally not guaranteed to work on all distributions / DEs.
        simulated = False
        try:
            import shutil
            import subprocess

            # Prefer enumerating XFCE properties first so dry-run can log candidates.
            if shutil.which("xfconf-query"):
                try:
                    list_proc = subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-l"], check=False, capture_output=True, text=True)
                    props = []
                    if list_proc.returncode == 0 and list_proc.stdout:
                        for line in list_proc.stdout.splitlines():
                            line = line.strip()
                            if not line:
                                continue
                            if "image" in line or "last-image" in line:
                                props.append(line)

                    props_workspace = [q for q in props if "workspace" in q and "last-image" in q]
                    props_monitor_image = [q for q in props if ("/monitor" in q and "image" in q and "workspace" not in q)]
                    props_last_image = [q for q in props if ("last-image" in q and "workspace" not in q)]
                    props_last_single = [q for q in props if "last-single-image" in q]
                    candidates = props_workspace + props_monitor_image + props_last_image + props_last_single

                    logger.info("XFCE: discovered props count=%d", len(props))
                    simulated = False
                    if dry_run:
                        logger.info("Dry-run: xfconf candidates (in order): %s", candidates)
                        # mark that we simulated work so dry-run can report success
                        if candidates:
                            simulated = True
                    success_any = False
                    # If dry_run, do not execute commands; only simulate logging.
                    # When actually applying (dry_run==False), try all candidate
                    # properties instead of stopping at the first success so that
                    # per-monitor properties for multiple displays are updated.
                    # If mapping provided, apply per-monitor; otherwise apply general file
                    if is_map:
                        # mapping keys are monitor names (e.g., 'DP-1')
                        for mon_name, mon_path in mapping.items():
                            applied_any = False
                            # select candidates that reference this monitor name using normalized comparison
                            mon_norm = _normalize_identifier(mon_name)
                            def _prop_norm(p: str) -> str:
                                return _normalize_identifier(p)
                            filtered = [c for c in candidates if (mon_name in c or mon_norm in _prop_norm(c) or ("/monitor" in c and mon_norm in _prop_norm(c)))]
                            if not filtered:
                                # fallback to workspace entries or general entries
                                filtered = [c for c in candidates if "workspace" in c or "last-image" in c]
                            for prop in filtered:
                                cmd = ["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", str(mon_path)]
                                logger.info("XFCE: would run: %s", " ".join(cmd))
                                if not dry_run:
                                    res = subprocess.run(cmd, check=False)
                                    if res.returncode == 0:
                                        applied_any = True
                                    else:
                                        logger.debug("XFCE: command failed (%s): %s", res.returncode, " ".join(cmd))
                            if applied_any:
                                success_any = True
                    else:
                        for prop in candidates:
                            cmd = ["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", str(p)]
                            logger.info("XFCE: would run: %s", " ".join(cmd))
                            if not dry_run:
                                res = subprocess.run(cmd, check=False)
                                if res.returncode == 0:
                                    success_any = True
                                else:
                                    logger.debug("XFCE: command failed (%s): %s", res.returncode, " ".join(cmd))
                    if success_any:
                        return True
                except Exception:
                    logger.exception("xfconf-query attempt failed")

            # Next try GNOME gsettings (if present). For dry-run, log the command instead
            # of executing so we don't prematurely short-circuit logging.
            if shutil.which("gsettings") and not is_map:
                cmd = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{str(p)}"]
                if dry_run:
                    logger.info("Dry-run: would run gsettings: %s", " ".join(cmd))
                    simulated = True
                else:
                    res = subprocess.run(cmd, check=False)
                    if res.returncode == 0:
                        return True
            if shutil.which("feh") and not is_map:
                # Lightweight viewers
                cmd = ["feh", "--bg-scale", str(p)]
                if dry_run:
                    logger.info("Dry-run: would run feh: %s", " ".join(cmd))
                    simulated = True
                else:
                    res = subprocess.run(cmd, check=False)
                    if res.returncode == 0:
                        return True
            # If dry-run and we simulated any candidate/command, treat as success
            if dry_run and simulated:
                logger.info("Dry-run: simulated commands present, reporting success")
                return True
            logger.error("No known wallpaper setter found on PATH")
            return False
        except Exception:  # pragma: no cover - platform specific
            logger.exception("Failed to apply linux wallpaper")
            return False


@registry.register("linux")
def make_linux_plugin() -> LinuxPlugin:
    return LinuxPlugin()

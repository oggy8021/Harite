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
from harite import workspace

logger = logging.getLogger(__name__)

# Threshold (pixels) for considering a position-based match
POS_MATCH_THRESHOLD = 200


def _normalize_identifier(s: str) -> str:
    """Normalize monitor/property names for fuzzy matching.

    Lowercase and strip non-alphanumeric characters so that names like
    "HDMI-1" and "hdmi1" compare equal.
    """
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _name_variants(name: str) -> set[str]:
    """Return normalized name variants to handle common aliases.

    Examples:
    - "DP-1" -> {"dp1", "displayport1"}
    - "HDMI-1" -> {"hdmi1"}
    """
    norm = _normalize_identifier(name)
    # split into alpha prefix and numeric suffix
    m = re.match(r"([a-z]+)(\d*)", norm)
    variants: set[str] = {norm}
    if m:
        prefix = m.group(1)
        suffix = m.group(2) or ""
        # common abbreviation map
        ABBREVS = {"displayport": "dp", "display": "dp", "edp": "edp"}
        # add abbreviation forms
        if prefix in ABBREVS:
            variants.add(ABBREVS[prefix] + suffix)
        # add expanded forms if prefix is abbreviated
        for long, short in ABBREVS.items():
            if prefix == short:
                variants.add(long + suffix)
    return variants


def _extract_resolution(prop: str):
    m = re.search(r"(\d+)x(\d+)", prop)
    if not m:
        return None
    try:
        return int(m.group(1)), int(m.group(2))
    except Exception:
        return None


def _extract_index(prop: str):
    m = re.search(r"/monitor(?:/|)(\d+)", prop)
    if not m:
        m2 = re.search(r"monitor(?:_|-|)(\d+)", prop)
        if not m2:
            return None
        m = m2
    try:
        return int(m.group(1))
    except Exception:
        return None


def _extract_position(prop: str):
    """Extract position offsets (x, y) from property strings.

    Supports patterns like `1920x1080+1024+0` and simple `+1024+0` offsets.
    Returns tuple (x, y) or None.
    """
    # try common geometry pattern with resolution and offsets (support signed offsets)
    m = re.search(r"(\d+)x(\d+)([+-]\d+)([+-]\d+)", prop)
    if m:
        try:
            return int(m.group(3)), int(m.group(4))
        except Exception:
            return None
    # try plain signed offsets like +1024+0 or -512+0
    m2 = re.search(r"([+-]\d+)\+([+-]?\d+)", prop)
    if m2:
        try:
            return int(m2.group(1)), int(m2.group(2))
        except Exception:
            return None
    return None


def _enumerate_xfconf_candidates() -> list:
    """Return a list of XFCE-related property paths discovered via xfconf-query.

    Isolated for testability: calls `xfconf-query -c xfce4-desktop -l` and
    returns only properties that look like image/last-image entries.
    """
    try:
        import subprocess
        props = []
        list_proc = subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-l"], check=False, capture_output=True, text=True)
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
        return candidates
    except Exception:
        logger.exception("xfconf-query enumeration failed")
        return []


def _match_candidates_for_mapping(mapping: dict, candidates: list) -> dict:
    """Return filtered candidate lists per mapping key (monitor name).

    Encapsulates index/resolution/position/composite heuristics used when a
    per-monitor `mapping` is provided. Returns a dict {monitor_name: [candidates]}.
    """
    result: dict = {}
    try:
        displays = workspace.detect_displays()
    except Exception:
        displays = []

    for mon_name in mapping.keys():
        filtered = []
        mon_variants = _name_variants(mon_name)

        def _prop_norm(p: str) -> str:
            return _normalize_identifier(p)

        def _matches_prop(prop: str) -> bool:
            pn = _prop_norm(prop)
            for v in mon_variants:
                if v and v in pn:
                    return True
            if mon_name in prop:
                return True
            return False

        filtered = [c for c in candidates if _matches_prop(c)]

        if not filtered:
            # composite token matching (index+res or resolution-only)
            try:
                if displays:
                    size_map = {(d.width, d.height): d.name for d in displays}
                    for c in candidates:
                        idx = _extract_index(c)
                        res = _extract_resolution(c)
                        if idx is not None and res is not None:
                            if idx < len(displays):
                                d = displays[idx]
                                if d.name in mapping:
                                    filtered = [c]
                                    break
                                for v in _name_variants(d.name):
                                    if v in mapping:
                                        filtered = [c]
                                        break
                                if filtered:
                                    break
                        if res is not None:
                            if res in size_map and size_map[res] in mapping:
                                filtered = [c]
                                break
            except Exception:
                logger.exception("Composite-token xfconf matching attempt failed")

        if not filtered:
            # index-based matching
            try:
                props_with_index = []
                for c in candidates:
                    m = re.search(r"/monitor(?:/|)(\d+)", c)
                    if not m:
                        m2 = re.search(r"monitor(\d+)", c)
                        m = m2
                    if m:
                        try:
                            props_with_index.append((int(m.group(1)), c))
                        except Exception:
                            continue
                if props_with_index and displays:
                    for idx, prop in props_with_index:
                        if idx < len(displays):
                            mon = displays[idx].name
                            if mon in mapping:
                                filtered = [prop]
                                break
            except Exception:
                logger.exception("Index-based xfconf matching attempt failed")

        if not filtered:
            # resolution-based matching
            try:
                if displays:
                    size_map = {(d.width, d.height): d.name for d in displays}
                    for c in candidates:
                        mres = re.search(r"(\d+)x(\d+)", c)
                        if mres:
                            try:
                                w = int(mres.group(1))
                                h = int(mres.group(2))
                            except Exception:
                                continue
                            if (w, h) in size_map:
                                mon_name_for_res = size_map[(w, h)]
                                if mon_name_for_res in mapping:
                                    filtered = [c]
                                    break
            except Exception:
                logger.exception("Resolution-based xfconf matching attempt failed")

        if not filtered:
            # position-based matching
            try:
                if displays:
                    for c in candidates:
                        pos = _extract_position(c)
                        if pos is None:
                            continue
                        x_off, y_off = pos

                        def _dist(disp):
                            dx = (getattr(disp, "x_offset", 0) or 0) - x_off
                            dy = (getattr(disp, "y_offset", 0) or 0) - y_off
                            return abs(dx) + abs(dy)

                        closest = min(displays, key=_dist)
                        distance = _dist(closest)
                        if distance <= POS_MATCH_THRESHOLD and closest.name in mapping:
                            filtered = [c]
                            break
                        if distance <= POS_MATCH_THRESHOLD:
                            for v in _name_variants(closest.name):
                                if v in mapping:
                                    filtered = [c]
                                    break
                            if filtered:
                                break
            except Exception:
                logger.exception("Position-based xfconf matching attempt failed")

        # fallback for single mapping pragmatics
        if not filtered and len(mapping) == 1:
            try:
                idx_cand = None
                if displays:
                    for c in candidates:
                        m = re.search(r"/monitor(?:/|)(\d+)", c)
                        if not m:
                            m2 = re.search(r"monitor(\d+)", c)
                            m = m2
                        if not m:
                            continue
                        try:
                            idx = int(m.group(1))
                        except Exception:
                            continue
                        if idx < len(displays):
                            mon_nm = displays[idx].name
                            if mon_nm in mapping:
                                idx_cand = c
                                break
                            for v in _name_variants(mon_nm):
                                if v in mapping:
                                    idx_cand = c
                                    break
                        if idx_cand:
                            break
                    if idx_cand is None:
                        any_display_matches = False
                        for d in displays:
                            if d.name in mapping:
                                any_display_matches = True
                                break
                            for v in _name_variants(d.name):
                                if v in mapping:
                                    any_display_matches = True
                                    break
                            if any_display_matches:
                                break
                        if not any_display_matches:
                            for c in candidates:
                                if re.search(r"/monitor(?:/|)\d+", c) or re.search(r"monitor\d+", c):
                                    pos = _extract_position(c)
                                    if pos is not None and displays:
                                        x_off, y_off = pos
                                        def _dist_to_disp(d):
                                            dx = (getattr(d, "x_offset", 0) or 0) - x_off
                                            dy = (getattr(d, "y_offset", 0) or 0) - y_off
                                            return abs(dx) + abs(dy)

                                        min_dist = min(_dist_to_disp(d) for d in displays)
                                        if min_dist > POS_MATCH_THRESHOLD:
                                            continue
                                    idx_cand = c
                                    break
                else:
                    for c in candidates:
                        if re.search(r"/monitor(?:/|)\d+", c) or re.search(r"monitor\d+", c):
                            idx_cand = c
                            break
                if idx_cand:
                    filtered = [idx_cand]
            except Exception:
                logger.exception("Fallback matching attempt failed")

        if not filtered:
            # For per-monitor mapping we avoid falling back to workspace-level
            # entries (they would affect all displays). Return empty to indicate
            # no suitable per-monitor candidate was found.
            filtered = []

        result[mon_name] = filtered

    return result


def _apply_xfconf_candidates(is_map: bool, mapping: dict | None, candidates: list, p: Path | None, dry_run: bool) -> tuple[bool, bool]:
    """Execute or simulate XFCE `xfconf-query` commands for candidates.

    Returns (success_any, simulated) where `simulated` is True when dry_run
    observed candidate commands to log, and `success_any` is True when any
    command returned success (returncode == 0) during real execution.
    """
    import subprocess

    simulated = False
    success_any = False

    if dry_run and candidates:
        simulated = True

    if is_map:
        if mapping is None:
            return False, simulated
        try:
            matched = _match_candidates_for_mapping(mapping, candidates)
        except Exception:
            logger.exception("Failed to obtain matched candidates for mapping")
            matched = {k: [] for k in (mapping.keys() if mapping else [])}

        for mon_name, mon_path in (mapping.items() if mapping else []):
            applied_any = False
            filtered = matched.get(mon_name, [])
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

    return success_any, simulated


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
            mapping = {
                str(mon_name): str(Path(mon_path).expanduser().resolve())
                for mon_name, mon_path in path.items()
            }
        else:
            p = Path(path).expanduser().resolve()
            if not p.exists():
                logger.error("Wallpaper file does not exist: %s", path)
                return False
            if dry_run:
                logger.info("Dry-run: would apply wallpaper (linux): %s", p)
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
                    candidates = _enumerate_xfconf_candidates()
                    success_any, simulated_xfce = _apply_xfconf_candidates(is_map, mapping if is_map else None, candidates, p if not is_map else None, dry_run)
                    if success_any:
                        return True
                    if simulated_xfce:
                        simulated = True
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

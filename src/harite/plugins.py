"""Plugin registry and wallpaper application plugins.

This module provides a minimal plugin registry and a Windows plugin stub that
applies wallpapers. Plugins must implement `apply(path_or_map)`.
"""
from __future__ import annotations

from typing import Callable, Dict, Protocol
from dataclasses import dataclass
import logging
from pathlib import Path
import re
from harite.display_context import closest_display_for_offset, get_display_at_index, get_ordered_displays
from harite import workspace

logger = logging.getLogger(__name__)

# Threshold (pixels) for considering a position-based match
POS_MATCH_THRESHOLD = 200


def _normalize_identifier(s: str) -> str:
    """識別子文字列を正規化する。

    Summary:
        小文字化して英数字以外を削除し、'HDMI-1' と 'hdmi1' のような差を吸収する。

    Args:
        s: 元の文字列。

    Returns:
        正規化済み文字列。
    """
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _name_variants(name: str) -> set[str]:
    """名前の派生バリアントを返す。

    Summary:
        通常の略称や展開形を含む正規化バリアント集合を返す。

    Args:
        name: モニタ名などの文字列。

    Returns:
        バリアントの集合。
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
    """文字列から幅×高さの解像度を抽出する。

    Args:
        prop: 解析対象文字列。

    Returns:
        (width, height) のタプル、抽出できない場合は None。
    """
    m = re.search(r"(\d+)x(\d+)", prop)
    if not m:
        return None
    try:
        return int(m.group(1)), int(m.group(2))
    except Exception:
        return None


def _extract_index(prop: str):
    """文字列からモニタインデックスを抽出する。

    Returns:
        インデックス整数または None。
    """
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
    """プロパティ文字列から位置オフセット (x, y) を抽出する。

    サポート: `1920x1080+1024+0` や `+1024+0` など。
    抽出できなければ None を返す。
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
    """`xfconf-query` で列挙される XFCE 関連のプロパティ候補を返す。

    テスト容易性のため分離。外部コマンドを呼ぶため失敗時は空リストを返す。
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
    """与えられたモニタマッピングに対して候補をフィルタリングする。

    Summary:
        インデックス、解像度、位置などのヒューリスティックを使って候補を絞る。

    Args:
        mapping: ユーザ提供のモニタ名 -> パス マッピング。
        candidates: 列挙されたプロパティ候補リスト。

    Returns:
        モニタ名 -> 候補リストの辞書。
    """
    result: dict = {}
    try:
        displays = get_ordered_displays()
    except Exception:
        displays = []

    def _mapping_matches_display(display_name: str) -> bool:
        if display_name in mapping:
            return True
        for variant in _name_variants(display_name):
            if variant in mapping:
                return True
        return False

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
                            display = get_display_at_index(idx, displays)
                            if display is not None:
                                if _mapping_matches_display(display.name):
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
                    idx = _extract_index(c)
                    if idx is not None:
                        props_with_index.append((idx, c))
                if props_with_index and displays:
                    for idx, prop in props_with_index:
                        display = get_display_at_index(idx, displays)
                        if display is not None:
                            mon = display.name
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
                        closest, distance = closest_display_for_offset(pos[0], pos[1], displays)
                        if closest is None or distance is None:
                            continue
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
                        idx = _extract_index(c)
                        if idx is None:
                            continue
                        display = get_display_at_index(idx, displays)
                        if display is not None:
                            mon_nm = display.name
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
                            if _mapping_matches_display(d.name):
                                any_display_matches = True
                                break
                            if any_display_matches:
                                break
                        if not any_display_matches:
                            for c in candidates:
                                if re.search(r"/monitor(?:/|)\d+", c) or re.search(r"monitor\d+", c):
                                    pos = _extract_position(c)
                                    if pos is not None and displays:
                                        _closest, min_dist = closest_display_for_offset(pos[0], pos[1], displays)
                                        if min_dist is None or min_dist > POS_MATCH_THRESHOLD:
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


def _apply_xfconf_candidates(is_map: bool, mapping: dict | None, candidates: list, p: Path | None) -> bool:
    """XFCE 候補に対して `xfconf-query` を実行する。

    Args:
        is_map: path 引数がマッピング(dict)か。
        mapping: マッピング（is_map=True のとき）。
        candidates: 候補パスリスト。
        p: 単一パス（is_map=False のとき）。
    Returns:
        適用成功時は True。
    """
    import subprocess

    success_any = False

    if is_map:
        if mapping is None:
            return False
        try:
            matched = _match_candidates_for_mapping(mapping, candidates)
        except Exception:
            logger.exception("Failed to obtain matched candidates for mapping")
            matched = {k: [] for k in (mapping.keys() if mapping else [])}

        success_all = bool(mapping)
        for mon_name, mon_path in (mapping.items() if mapping else []):
            applied_any = False
            filtered = matched.get(mon_name, [])
            for prop in filtered:
                cmd = ["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", str(mon_path)]
                logger.info("XFCE: run: %s", " ".join(cmd))
                res = subprocess.run(cmd, check=False)
                if res.returncode == 0:
                    applied_any = True
                else:
                    logger.debug("XFCE: command failed (%s): %s", res.returncode, " ".join(cmd))
            if not applied_any:
                success_all = False
                logger.warning("XFCE: no matching per-monitor apply candidate succeeded for %s", mon_name)
        return success_all
    else:
        for prop in candidates:
            cmd = ["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", str(p)]
            logger.info("XFCE: run: %s", " ".join(cmd))
            res = subprocess.run(cmd, check=False)
            if res.returncode == 0:
                success_any = True
            else:
                logger.debug("XFCE: command failed (%s): %s", res.returncode, " ".join(cmd))

    return success_any


class PluginProtocol(Protocol):
    name: str

    def apply(self, path: str) -> bool:
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

    def apply(self, path: str) -> bool:
        if isinstance(path, dict):
            logger.error("Per-monitor mapping is not supported by the windows plugin")
            return False
        p = Path(path)
        if not p.exists():
            logger.error("Wallpaper file does not exist: %s", path)
            return False

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

    def apply(self, path: str) -> bool:
        if isinstance(path, dict):
            logger.error("Per-monitor mapping is not supported by the macos plugin")
            return False
        p = Path(path)
        if not p.exists():
            logger.error("Wallpaper file does not exist: %s", path)
            return False

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

    def apply(self, path: str) -> bool:
        # Support per-monitor mapping dicts: {monitor_name: path}
        is_map = isinstance(path, dict)
        if is_map:
            mapping = {
                str(mon_name): str(Path(mon_path).expanduser().resolve())
                for mon_name, mon_path in path.items()
            }
            for mon_path in mapping.values():
                try:
                    Path(mon_path).touch()
                except OSError:
                    logger.debug("Could not touch wallpaper file before apply: %s", mon_path)
        else:
            p = Path(path).expanduser().resolve()
            if not p.exists():
                logger.error("Wallpaper file does not exist: %s", path)
                return False
            try:
                p.touch()
            except OSError:
                logger.debug("Could not touch wallpaper file before apply: %s", p)

        # Try common desktop environment commands (gsettings, feh). This is a best-effort
        # and intentionally not guaranteed to work on all distributions / DEs.
        try:
            import shutil
            import subprocess

            if shutil.which("xfconf-query"):
                try:
                    candidates = _enumerate_xfconf_candidates()
                    if _apply_xfconf_candidates(is_map, mapping if is_map else None, candidates, p if not is_map else None):
                        return True
                except Exception:
                    logger.exception("xfconf-query attempt failed")

            if shutil.which("gsettings") and not is_map:
                cmd = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{str(p)}"]
                res = subprocess.run(cmd, check=False)
                if res.returncode == 0:
                    return True
            if shutil.which("feh") and not is_map:
                cmd = ["feh", "--bg-scale", str(p)]
                res = subprocess.run(cmd, check=False)
                if res.returncode == 0:
                    return True
            logger.error("No known wallpaper setter found on PATH")
            return False
        except Exception:  # pragma: no cover - platform specific
            logger.exception("Failed to apply linux wallpaper")
            return False


@registry.register("linux")
def make_linux_plugin() -> LinuxPlugin:
    return LinuxPlugin()

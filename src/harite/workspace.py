"""WorkSpace / display detection helpers.

Provides a small cross-platform `detect_displays()` helper that returns a
list of `Display` objects with name, size and offset information. Implemented
to be test-friendly (subprocess calls can be mocked in unit tests).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List
import re
import platform
import subprocess


@dataclass
class Display:
    name: str
    width: int
    height: int
    x_offset: int = 0
    y_offset: int = 0
    primary: bool = False
    scale_percent: int | None = None


def detect_displays() -> List[Display]:
    """Detect displays for the current host and return `Display` list.

    On Linux this parses `xrandr --query`. On Windows this uses
    ``EnumDisplayMonitors`` / ``GetMonitorInfoW``. On macOS returns basic
    size-only ``Display`` entries (name may be empty).
    """
    system = platform.system()
    if system == "Linux":
        return _detect_linux()
    if system == "Darwin":
        return _detect_macos()
    if system == "Windows":
        return _detect_windows()
    return []


def _detect_linux() -> List[Display]:
    """Linux ホストでディスプレイ情報を検出する。

    Summary:
        `xrandr --query` の出力を解析して接続中のディスプレイ名、解像度、オフセットを
        抽出し `Display` のリストを返す。失敗時は空リストを返す。
    """
    try:
        out = subprocess.check_output(["xrandr", "--query"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []

    displays: List[Display] = []
    for line in out.splitlines():
        line = line.strip()
        if " connected " in line:
            parts = line.split()
            name = parts[0]
            primary = "primary" in parts
            w = h = x_off = 0
            y_off = 0
            # Use regex to robustly extract geometry like 2048x1280+2048+0
            m = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
            if m:
                try:
                    w = int(m.group(1))
                    h = int(m.group(2))
                    x_off = int(m.group(3))
                    y_off = int(m.group(4))
                except Exception:
                    w = h = x_off = 0
                    y_off = 0
            else:
                # Fallback: try token-based parsing to handle malformed/residual formats
                for p in parts:
                    if "x" in p:
                        try:
                            wh = p.split("+")[0]
                            if "x" in wh:
                                w_str, h_str = wh.split("x")
                                try:
                                    w = int(w_str)
                                except Exception:
                                    # try to extract leading digits
                                    m2 = re.match(r"(\d+)", w_str)
                                    if m2:
                                        w = int(m2.group(1))
                                try:
                                    h = int(h_str)
                                except Exception:
                                    h = 0
                                try:
                                    x_off = int(p.split("+")[1])
                                except Exception:
                                    x_off = 0
                                try:
                                    y_off = int(p.split("+")[2])
                                except Exception:
                                    y_off = 0
                                break
                        except Exception:
                            continue
            displays.append(Display(name=name, width=w, height=h, x_offset=x_off, y_offset=y_off, primary=primary))
    return displays


def _detect_macos() -> List[Display]:
    """macOS で表示解像度を検出する（system_profiler を使用）。

    解析に失敗した場合は空リストを返す。
    """
    try:
        out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []

    displays: List[Display] = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Resolution:"):
            try:
                _, rest = line.split("Resolution:", 1)
                parts = rest.strip().split()
                if len(parts) >= 3 and parts[1] == "x":
                    w = int(parts[0])
                    h = int(parts[2])
                    displays.append(Display(name="", width=w, height=h))
                else:
                    nums = [p for p in parts if p.isdigit()]
                    if len(nums) >= 2:
                        displays.append(Display(name="", width=int(nums[0]), height=int(nums[1])))
            except Exception:
                continue
    return displays


def _scale_percent_from_effective_dpi(dpi_x: int, dpi_y: int = 0) -> int:
    """Map Win32 effective DPI to Windows Settings scale percent (96 -> 100)."""
    _ = dpi_y
    return int(round(int(dpi_x) * 100 / 96))


def _ensure_windows_dpi_aware(user32: object) -> None:
    """Best-effort Per-Monitor v2 DPI awareness with legacy fallback."""
    import ctypes

    try:
        pmv2 = ctypes.c_void_p(-4)
        if user32.SetProcessDpiAwarenessContext(pmv2):
            return
    except Exception:
        pass
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass


def _display_from_win32_monitor(
    *,
    name: str,
    left: int,
    top: int,
    right: int,
    bottom: int,
    primary: bool,
    scale_percent: int | None = None,
) -> Display:
    """Build ``Display`` from Win32 monitor rectangle and device name."""
    return Display(
        name=str(name).strip(),
        width=max(0, int(right - left)),
        height=max(0, int(bottom - top)),
        x_offset=int(left),
        y_offset=int(top),
        primary=bool(primary),
        scale_percent=scale_percent,
    )


def _enumerate_windows_displays(user32: object) -> List[Display]:
    """Enumerate monitors using Win32 ``user32`` bindings."""
    import ctypes
    from ctypes import wintypes

    class _RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    class _MONITORINFOEXW(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", _RECT),
            ("rcWork", _RECT),
            ("dwFlags", wintypes.DWORD),
            ("szDevice", wintypes.WCHAR * 32),
        ]

    MONITORINFOF_PRIMARY = 1
    MDT_EFFECTIVE_DPI = 0
    collected: List[Display] = []

    try:
        shcore = ctypes.windll.shcore
    except Exception:
        shcore = None

    def _callback(hmonitor, _hdc, _prect, _lparam):
        info = _MONITORINFOEXW()
        info.cbSize = ctypes.sizeof(_MONITORINFOEXW)
        if not user32.GetMonitorInfoW(hmonitor, ctypes.byref(info)):
            return 1
        rect = info.rcMonitor
        scale_percent: int | None = None
        if shcore is not None:
            dpi_x = wintypes.UINT()
            dpi_y = wintypes.UINT()
            try:
                if shcore.GetDpiForMonitor(hmonitor, MDT_EFFECTIVE_DPI, ctypes.byref(dpi_x), ctypes.byref(dpi_y)) == 0:
                    scale_percent = _scale_percent_from_effective_dpi(dpi_x.value, dpi_y.value)
            except Exception:
                pass
        collected.append(
            _display_from_win32_monitor(
                name=str(info.szDevice),
                left=int(rect.left),
                top=int(rect.top),
                right=int(rect.right),
                bottom=int(rect.bottom),
                primary=bool(info.dwFlags & MONITORINFOF_PRIMARY),
                scale_percent=scale_percent,
            )
        )
        return 1

    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(_RECT),
        wintypes.LPARAM,
    )
    enum_proc = MONITORENUMPROC(_callback)
    user32.EnumDisplayMonitors(None, None, enum_proc, 0)
    return collected


def _win32_user32() -> object:
    """Return Win32 ``user32`` bindings (overridable in unit tests on non-Windows hosts)."""
    import ctypes

    return ctypes.windll.user32


def _windows_fallback_scale_percent(user32: object) -> int | None:
    """Best-effort scale percent when monitor enumeration is unavailable."""
    try:
        dpi = int(user32.GetDpiForSystem())
        if dpi > 0:
            return _scale_percent_from_effective_dpi(dpi)
    except Exception:
        pass
    return None


def _detect_windows() -> List[Display]:
    """Windows で接続モニタを列挙する（EnumDisplayMonitors / GetMonitorInfoW）。

    ``DeviceName``（例: ``\\\\.\\DISPLAY1``）と monitor 矩形から
    ``Display`` を構築する。列挙失敗時のみ primary 1 枚 fallback する。
    """
    try:
        user32 = _win32_user32()
        _ensure_windows_dpi_aware(user32)

        collected = _enumerate_windows_displays(user32)
        if collected:
            return collected

        width = int(user32.GetSystemMetrics(0))
        height = int(user32.GetSystemMetrics(1))
        if width > 0 and height > 0:
            return [
                Display(
                    name="",
                    width=width,
                    height=height,
                    primary=True,
                    scale_percent=_windows_fallback_scale_percent(user32),
                )
            ]
        return []
    except Exception:
        return []

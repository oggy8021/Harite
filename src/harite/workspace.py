"""WorkSpace / display detection helpers.

Provides a small cross-platform `detect_displays()` helper that returns a
list of `Display` objects with name, size and offset information. Implemented
to be test-friendly (subprocess calls can be mocked in unit tests).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List
import platform
import subprocess


@dataclass
class Display:
    name: str
    width: int
    height: int
    x_offset: int = 0
    primary: bool = False


def detect_displays() -> List[Display]:
    """Detect displays for the current host and return `Display` list.

    On Linux this parses `xrandr --query`. On macOS/Windows returns basic
    size-only `Display` entries (name may be empty).
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
            for p in parts:
                if "x" in p and "+" in p:
                    try:
                        wh = p.split("+")[0]
                        w_str, h_str = wh.split("x")
                        w = int(w_str)
                        h = int(h_str)
                        try:
                            x_off = int(p.split("+")[1])
                        except Exception:
                            x_off = 0
                        break
                    except Exception:
                        continue
            displays.append(Display(name=name, width=w, height=h, x_offset=x_off, primary=primary))
    return displays


def _detect_macos() -> List[Display]:
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


def _detect_windows() -> List[Display]:
    try:
        import ctypes as _ctypes

        user32 = _ctypes.windll.user32
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return [Display(name="", width=int(width), height=int(height))]
    except Exception:
        return []

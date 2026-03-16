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

"""WorkSpace / display detection helpers.

Provides a minimal cross-platform `detect_displays()` helper that returns a
list of (width, height) tuples. Implementations try platform-specific probes
but are safe to call from CI: tests mock subprocess/implementations.
"""
from __future__ import annotations

from typing import List, Tuple
import platform
import subprocess


def detect_displays() -> List[Tuple[int, int]]:
    system = platform.system()
    if system == "Linux":
        return _detect_linux()
    if system == "Darwin":
        return _detect_macos()
    if system == "Windows":
        return _detect_windows()
    return []


def _detect_linux() -> List[Tuple[int, int]]:
    """Parse `xrandr --query` output to find connected displays.

    Returns list of (width, height). If xrandr is not available, returns [].
    """
    try:
        out = subprocess.check_output(["xrandr", "--query"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []

    displays: List[Tuple[int, int]] = []
    for line in out.splitlines():
        line = line.strip()
        if " connected " in line:
            # example: HDMI-1 connected primary 1920x1080+0+0 ...
            parts = line.split()
            for p in parts:
                if "x" in p and "+" in p:
                    try:
                        wh = p.split("+")[0]
                        w, h = wh.split("x")
                        displays.append((int(w), int(h)))
                        break
                    except Exception:
                        continue
    return displays


def _detect_macos() -> List[Tuple[int, int]]:
    """Use `system_profiler SPDisplaysDataType` and parse 'Resolution:' lines.

    Returns list of (width, height). If command fails, returns [].
    """
    try:
        out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []

    displays: List[Tuple[int, int]] = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Resolution:"):
            # Example: Resolution: 2560 x 1440 Retina
            try:
                _, rest = line.split("Resolution:", 1)
                parts = rest.strip().split()
                if len(parts) >= 3 and parts[1] == "x":
                    w = int(parts[0])
                    h = int(parts[2])
                    displays.append((w, h))
                else:
                    # fallback parse like '2560 x 1440'
                    nums = [p for p in parts if p.isdigit()]
                    if len(nums) >= 2:
                        displays.append((int(nums[0]), int(nums[1])))
            except Exception:
                continue
    return displays


def _detect_windows() -> List[Tuple[int, int]]:
    """Attempt to enumerate displays on Windows using ctypes.

    This is best-effort and will return [] when run on non-Windows hosts
    (or when APIs are unavailable). The function is intentionally small and
    unintrusive so it can be used in tests and local runs.
    """
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        # Get primary monitor size
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return [(int(width), int(height))]
    except Exception:
        return []

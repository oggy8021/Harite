import sys
import types
import subprocess
import platform

import pytest

from harite import workspace


def test_detect_linux_parses_xrandr(monkeypatch):
    sample = """
HDMI-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 520mm x 290mm
DP-1 connected 2560x1440+1920+0 (normal left inverted right x axis y axis) 600mm x 340mm
"""

    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: sample)

    displays = workspace.detect_displays()
    assert (1920, 1080) in displays
    assert (2560, 1440) in displays


def test_detect_linux_returns_empty_on_error(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")

    def bad(*a, **k):
        raise subprocess.CalledProcessError(1, "xrandr")

    monkeypatch.setattr(subprocess, "check_output", bad)

    displays = workspace.detect_displays()
    assert displays == []


def test_detect_macos_parses_system_profiler(monkeypatch):
    sample = """
Graphics/Displays:
    Resolution: 2560 x 1440 Retina
    Resolution: 1920 x 1080
"""
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: sample)

    displays = workspace.detect_displays()
    assert (2560, 1440) in displays
    assert (1920, 1080) in displays


def test_detect_windows_uses_ctypes(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")

    # create fake ctypes module
    fake = types.SimpleNamespace()
    class User32:
        def SetProcessDPIAware(self):
            return 1

        def GetSystemMetrics(self, idx):
            return 800 if idx == 0 else 600

    fake.windll = types.SimpleNamespace(user32=User32())
    sys.modules["ctypes"] = fake

    displays = workspace.detect_displays()
    assert displays == [(800, 600)]

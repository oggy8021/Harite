import platform
import subprocess
import types

from harite import workspace


def test_detect_displays_parses_xrandr(monkeypatch):
    sample = '''
Screen 0: minimum 320 x 200, current 4096 x 1280, maximum 16384 x 16384
HDMI-1 connected primary 2048x1280+0+0 (normal)
DP-1 connected 2048x1280+2048+0 (normal)
'''

    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: sample)
    displays = workspace._detect_linux()
    assert len(displays) == 2
    names = [d.name for d in displays]
    assert "HDMI-1" in names
    assert "DP-1" in names
    hdmi = next(d for d in displays if d.name == "HDMI-1")
    assert hdmi.width == 2048
    assert hdmi.height == 1280
    assert hdmi.x_offset == 0


def test_detect_linux_parses_xrandr(monkeypatch):
    sample = """
HDMI-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 520mm x 290mm
DP-1 connected 2560x1440+1920+0 (normal left inverted right x axis y axis) 600mm x 340mm
"""

    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: sample)

    displays = workspace.detect_displays()
    # displays now return Display objects
    names = {(d.width, d.height) for d in displays}
    assert (1920, 1080) in names
    assert (2560, 1440) in names


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
    names = {(d.width, d.height) for d in displays}
    assert (2560, 1440) in names
    assert (1920, 1080) in names


def test_detect_windows_uses_ctypes(monkeypatch):
    class User32:
        def SetProcessDpiAwarenessContext(self, _ctx):
            return 1

        def SetProcessDPIAware(self):
            return 1

        def EnumDisplayMonitors(self, *_args):
            return 0

        def GetSystemMetrics(self, idx):
            return 800 if idx == 0 else 600

        def GetDpiForSystem(self):
            return 96

    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(workspace, "_enumerate_windows_displays", lambda _user32: [])
    monkeypatch.setattr(workspace, "_win32_user32", lambda: User32())

    displays = workspace.detect_displays()
    assert len(displays) == 1
    assert displays[0].width == 800 and displays[0].height == 600
    assert displays[0].primary is True
    assert displays[0].scale_percent == 100

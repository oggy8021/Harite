import sys
import types
import platform
import subprocess

from harite import workspace


def test_linux_parses_primary_and_offsets(monkeypatch):
    sample = """
HDMI-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 520mm x 290mm
DP-1 connected 2560x1440+1920+0 (normal left inverted right x axis y axis) 600mm x 340mm
"""

    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: sample)

    displays = workspace._detect_linux()
    names = {d.name: (d.width, d.height, d.x_offset, d.primary) for d in displays}
    assert "HDMI-1" in names
    assert names["HDMI-1"] == (1920, 1080, 0, True)
    assert "DP-1" in names
    assert names["DP-1"] == (2560, 1440, 1920, False)


def test_linux_handles_malformed_resolution(monkeypatch):
    sample = """
VGA-1 connected 1024x+0+0 (normal)
"""

    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: sample)

    displays = workspace._detect_linux()
    assert len(displays) == 1
    # malformed resolution should produce a display entry with partial parse (width parsed, height 0)
    assert displays[0].width == 1024 and displays[0].height == 0


def test_macos_parses_various_resolution_formats(monkeypatch):
    sample = """
Graphics/Displays:
    Resolution: 2560 x 1440 Retina
    Resolution: 1024 x 768
    Resolution: 1366 x 768
    Resolution: 300 x 200 extra
"""

    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: sample)

    displays = workspace._detect_macos()
    sizes = {(d.width, d.height) for d in displays}
    assert (2560, 1440) in sizes
    assert (1024, 768) in sizes
    assert (1366, 768) in sizes
    assert (300, 200) in sizes


def test_windows_returns_empty_when_ctypes_unusable(monkeypatch):
    # Simulate a ctypes module that lacks windll attribute (causes exception)
    fake = types.SimpleNamespace()
    monkeypatch.setitem(sys.modules, "ctypes", fake)

    displays = workspace._detect_windows()
    assert displays == []

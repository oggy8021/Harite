import subprocess

from harite.workspace import detect_displays


def test_xrandr_parsing(monkeypatch):
    sample = """Screen 0: minimum 8 x 8, current 3840 x 1080, maximum 32767 x 32767
DP-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 521mm x 293mm
HDMI-1 connected 1920x1080+1920+0 (normal left inverted right x axis y axis) 477mm x 268mm
"""

    def fake_check_output(cmd, text=True, stderr=None):
        return sample

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    displays = detect_displays()
    assert len(displays) == 2
    assert displays[0].name == "DP-1"
    assert displays[0].width == 1920
    assert displays[0].x_offset == 0
    assert displays[1].name == "HDMI-1"
    assert displays[1].x_offset == 1920

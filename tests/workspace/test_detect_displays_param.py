import pytest
import subprocess
import platform

from harite import workspace


@pytest.mark.parametrize(
    "sample, expected",
    [
        (
            # dual-monitor (real-world sample)
            """
Screen 0: current 4096 x 1280
HDMI-1 connected primary 2048x1280+0+0 (normal)
DP-1 connected 2048x1280+2048+0 (normal)
""",
            [
                ("HDMI-1", 2048, 1280, 0),
                ("DP-1", 2048, 1280, 2048),
            ],
        ),
        (
            # geometry token missing trailing +y but contains +x
            """
HDMI-1 connected 1920x1080+0 (normal)
""",
            [("HDMI-1", 1920, 1080, 0)],
        ),
        (
            # corrupted height digits -> height falls back to 0
            """
HDMI-1 connected 2048xabc+0+0 (normal)
""",
            [("HDMI-1", 2048, 0, 0)],
        ),
        (
            # no connected displays
            """
Screen 0: current 0 x 0
""",
            [],
        ),
    ],
)
def test_detect_displays_parametrize(monkeypatch, sample, expected):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: sample)

    displays = workspace.detect_displays()
    got = [(d.name, d.width, d.height, d.x_offset) for d in displays]

    # order-insensitive check: convert to sets for comparison
    assert set(got) == set(expected)

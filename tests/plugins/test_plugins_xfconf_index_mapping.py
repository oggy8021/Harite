import shutil
import subprocess
from types import SimpleNamespace

from harite import workspace
from harite.plugins import LinuxPlugin


def _make_list_proc(stdout: str, rc: int = 0):
    return SimpleNamespace(returncode=rc, stdout=stdout)


def test_index_based_mapping(monkeypatch):
    # xfconf available and lists monitor0/monitor1 properties
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    sample_props = "/backdrop/screen0/monitor0/image\n/backdrop/screen0/monitor1/image\n"

    def fake_run(cmd, check=False, capture_output=False, text=False):
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    # patch detect_displays in unsorted order; helper should normalize by offsets
    monkeypatch.setattr(
        "harite.display_context.detect_displays",
        lambda: [workspace.Display("HDMI-1", 2048, 1280, 2048), workspace.Display("DP-1", 2048, 1280, 0)],
    )

    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/w1.jpg", "HDMI-1": "/tmp/w2.jpg"}

    # applying should succeed by index-based matching
    assert plugin.apply(mapping) is True

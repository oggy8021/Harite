import shutil
import subprocess
from types import SimpleNamespace

from harite import workspace
from harite.plugins import LinuxPlugin


def _make_list_proc(stdout: str, rc: int = 0):
    return SimpleNamespace(returncode=rc, stdout=stdout)


def test_position_matching(monkeypatch):
    # xfconf available and lists props that include position offsets like +1024+0
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    sample_props = "/backdrop/screen0/monitor0/image_1920x1080+1024+0\n/backdrop/screen0/workspace0/last-image\n"

    def fake_run(cmd, check=False, capture_output=False, text=False):
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    # patch detect_displays to return displays where DP-1 has x_offset 1024
    monkeypatch.setattr(workspace, "detect_displays", lambda: [workspace.Display("eDP-1", 1024, 768, 0), workspace.Display("DP-1", 2048, 1280, 1024)])

    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/wall.jpg"}

    # applying should succeed by position-based matching
    assert plugin.apply(mapping, dry_run=False) is True

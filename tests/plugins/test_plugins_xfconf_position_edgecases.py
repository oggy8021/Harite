import shutil
import subprocess
from types import SimpleNamespace

from harite import workspace
from harite.plugins import LinuxPlugin


def _make_list_proc(stdout: str, rc: int = 0):
    return SimpleNamespace(returncode=rc, stdout=stdout)


def test_negative_offset_matching(monkeypatch):
    # xfconf available and lists props that include negative offsets like -512+0
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    sample_props = "/backdrop/screen0/monitor0/image_-512+0\n/backdrop/screen0/workspace0/last-image\n"

    def fake_run(cmd, check=False, capture_output=False, text=False):
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    # patch detect_displays to return displays where DP-1 has x_offset -512
    monkeypatch.setattr(workspace, "detect_displays", lambda: [workspace.Display("eDP-1", 1024, 768, 0), workspace.Display("DP-1", 2048, 1280, -512)])

    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/wall.jpg"}

    # applying should succeed by position-based matching with negative offset
    assert plugin.apply(mapping, dry_run=False) is True


def test_duplicate_size_position_scoring(monkeypatch):
    # xfconf available and lists two candidates with same resolution but different offsets
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    sample_props = "/backdrop/screen0/monitor0/image_1920x1080+0+0\n/backdrop/screen0/monitor1/image_1920x1080+1920+0\n"

    def fake_run(cmd, check=False, capture_output=False, text=False):
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    # two displays with identical resolution; DP-1 is the right-side one at x_offset 1920
    monkeypatch.setattr(workspace, "detect_displays", lambda: [workspace.Display("eDP-1", 1920, 1080, 0), workspace.Display("DP-1", 1920, 1080, 1920)])

    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/wall.jpg"}

    # applying should succeed by selecting the candidate with +1920+0 via position matching
    assert plugin.apply(mapping, dry_run=False) is True

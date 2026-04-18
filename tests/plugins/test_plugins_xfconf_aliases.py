import shutil
import subprocess
from types import SimpleNamespace

from harite import workspace
from harite.plugins import LinuxPlugin


def _make_list_proc(stdout: str, rc: int = 0):
    return SimpleNamespace(returncode=rc, stdout=stdout)


def test_name_alias_matching(monkeypatch):
    # xfconf available and lists props that include abbreviated monitor tokens (dp1)
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    # property contains dp1 token while detected display is named DP-1
    sample_props = "/backdrop/screen0/monitor_dp1/image\n/backdrop/screen0/workspace0/last-image\n"

    def fake_run(cmd, check=False, capture_output=False, text=False):
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    # patch detect_displays to return a display named DP-1
    monkeypatch.setattr("harite.display_context.detect_displays", lambda: [workspace.Display("DP-1", 2048, 1280, 0)])

    plugin = LinuxPlugin()
    # mapping uses a different alias form 'displayport1' (or 'dp1') to ensure alias handling
    mapping = {"displayport1": "/tmp/wall.jpg"}

    # applying should succeed by alias-based matching
    assert plugin.apply(mapping, dry_run=False) is True

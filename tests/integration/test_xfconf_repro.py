import types
from types import SimpleNamespace
import shutil
import subprocess

import pytest

from harite import workspace
from harite.plugins import LinuxPlugin


def _make_list_proc(stdout: str):
    return SimpleNamespace(returncode=0, stdout=stdout)


def test_xfconf_sample_apply(monkeypatch):
    """Use representative xfconf-query listings and verify plugin behavior.

    This test ensures the LinuxPlugin detects xfconf candidates
    and issues set commands during apply.
    """
    # Ensure xfconf-query is reported present
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    # Representative xfconf properties that include index/resolution/position tokens
    sample_props = (
        "/backdrop/screen0/monitor0/workspace0/last-image\n"
        "/backdrop/screen0/monitor0/image\n"
        "/backdrop/screen0/monitor1/image\n"
        "/backdrop/screen0/workspace0/last-image\n"
    )

    calls = []

    def fake_run(cmd, check=False, capture_output=False, text=False):
        calls.append(cmd)
        # listing invocation
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        # simulate successful set/apply
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    # Patch detect_displays to deterministic layout for heuristics
    monkeypatch.setattr(
        "harite.display_context.detect_displays",
        lambda: [
            workspace.Display("eDP-1", 1920, 1080, 0),
            workspace.Display("DP-1", 1920, 1080, 1920),
        ],
    )

    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/wall_dp.jpg", "eDP-1": "/tmp/wall_edp.jpg"}

    assert plugin.apply(mapping) is True
    assert plugin.apply(mapping) is True
    assert any(isinstance(c, list) and c[0] == "xfconf-query" and "-s" in c for c in calls)


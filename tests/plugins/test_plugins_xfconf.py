import types
from types import SimpleNamespace
import shutil
import subprocess

import pytest

from harite import workspace
from harite.plugins import LinuxPlugin


def _make_list_proc(stdout: str):
    return SimpleNamespace(returncode=0, stdout=stdout)


def test_linux_plugin_apply_with_xfconf_candidates(monkeypatch):
    # xfconf available and lists several image-related properties
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)
    monkeypatch.setattr(
        "harite.display_context.detect_displays",
        lambda: [
            workspace.Display("DP-1", 1920, 1080, 0),
            workspace.Display("HDMI-1", 1920, 1080, 1920),
        ],
    )

    sample_props = """
/backdrop/screen0/monitor0/workspace0/last-image
/backdrop/screen0/monitor0/image
/backdrop/screen0/monitor1/image
/backdrop/screen0/workspace0/last-image
"""

    def fake_run(cmd, check=False, capture_output=False, text=False):
        # list invocation
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/wall1.jpg", "HDMI-1": "/tmp/wall2.jpg"}

    assert plugin.apply(mapping) is True


def test_linux_plugin_apply_mapping_executes_commands(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    sample_props = "/backdrop/screen0/monitor1/image\n/backdrop/screen0/workspace0/last-image\n"

    calls = []

    def fake_run(cmd, check=False, capture_output=False, text=False):
        calls.append(cmd)
        # listing
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        # apply commands -> simulate success
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/wall1.jpg"}

    # apply should attempt commands and return True
    assert plugin.apply(mapping) is True
    # ensure at least one xfconf set command was attempted
    assert any(isinstance(c, list) and c[0] == "xfconf-query" and "-s" in c for c in calls)


def test_linux_plugin_apply_mapping_requires_all_requested_monitors(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    sample_props = "/backdrop/screen0/monitor1/image\n"

    def fake_run(cmd, check=False, capture_output=False, text=False):
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/wall1.jpg", "HDMI-1": "/tmp/wall2.jpg"}

    assert plugin.apply(mapping) is False


def test_linux_plugin_no_setter_returns_false(monkeypatch, tmp_path):
    # No xfconf, gsettings, or feh available
    monkeypatch.setattr(shutil, "which", lambda name: None)

    # create a real temporary file for non-map path
    f = tmp_path / "wall.jpg"
    f.write_text("x")

    plugin = LinuxPlugin()
    # with no known setter, applying should fail
    assert plugin.apply(str(f)) is False

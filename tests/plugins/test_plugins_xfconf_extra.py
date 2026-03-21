import shutil
import subprocess
from types import SimpleNamespace

import pytest

from harite.plugins import LinuxPlugin


def _make_list_proc(stdout: str, rc: int = 0):
    return SimpleNamespace(returncode=rc, stdout=stdout)


def test_fuzzy_monitor_name_matching(monkeypatch):
    # xfconf available and lists properties using variant names
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    sample_props = "/backdrop/screen0/monitor0/hdmi1/image\n/backdrop/screen0/workspace0/last-image\n"
    calls = []

    def fake_run(cmd, check=False, capture_output=False, text=False):
        calls.append(cmd)
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc(sample_props)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    plugin = LinuxPlugin()
    mapping = {"HDMI-1": "/tmp/wall.jpg"}

    assert plugin.apply(mapping, dry_run=False) is True
    # ensure an xfconf set command targeting a property was attempted
    assert any(cmd[0] == "xfconf-query" and "-s" in cmd for cmd in calls)


def test_dryrun_prefers_gsettings_when_present(monkeypatch, tmp_path):
    # no xfconf, but gsettings present
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gsettings" if name == "gsettings" else None)

    f = tmp_path / "wall.jpg"
    f.write_text("x")

    recorded = []

    def fake_run(cmd, check=False, capture_output=False, text=False):
        recorded.append(cmd)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    plugin = LinuxPlugin()
    assert plugin.apply(str(f), dry_run=True) is True


def test_dryrun_prefers_feh_when_present(monkeypatch, tmp_path):
    # neither xfconf nor gsettings, but feh present
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/feh" if name == "feh" else None)

    f = tmp_path / "wall.jpg"
    f.write_text("x")

    recorded = []

    def fake_run(cmd, check=False, capture_output=False, text=False):
        recorded.append(cmd)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    plugin = LinuxPlugin()
    assert plugin.apply(str(f), dry_run=True) is True


def test_xfconf_list_failure_falls_back_and_reports_false(monkeypatch, tmp_path):
    # xfconf present but listing fails (non-zero) and no other setters
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    def fake_run(cmd, check=False, capture_output=False, text=False):
        if cmd[:3] == ["xfconf-query", "-c", "xfce4-desktop"] and "-l" in cmd:
            return _make_list_proc("", rc=1)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    plugin = LinuxPlugin()
    f = tmp_path / "wall.jpg"
    f.write_text("x")

    # with xfconf list failure and no other setters, applying should return False
    assert plugin.apply(str(f), dry_run=False) is False

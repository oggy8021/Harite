import shutil
import subprocess
from types import SimpleNamespace
from harite.plugins import LinuxPlugin


def test_linuxplugin_candidate_matching(monkeypatch):
    # Simulate xfconf-query being present
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/xfconf-query" if name == "xfconf-query" else None)

    # Simulate xfconf-query -l output with monitor-specific properties
    props = """
/backdrop/screen0/monitorHDMI-1/workspace0/last-image
/backdrop/screen0/monitorDP-1/workspace0/last-image
/backdrop/screen0/workspace0/last-image
"""

    def fake_run(args, check=False, capture_output=False, text=False):
        cmd = args[0] if isinstance(args, (list, tuple)) else args
        if "-l" in args:
            return SimpleNamespace(returncode=0, stdout=props)
        # For other calls (would be setters), return a non-error when executed
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    plugin = LinuxPlugin()
    # Provide a mapping for DP-1 – dry_run should detect candidates and report success
    res = plugin.apply({"DP-1": "/tmp/fake.jpg"}, dry_run=True)
    assert res is True
from harite import plugins
from pathlib import Path


def test_registry_contains_windows():
    names = plugins.registry.list()
    assert "windows" in names
    assert "macos" in names
    assert "linux" in names


def test_windows_plugin_dry_run_success():
    plugin = plugins.registry.get("windows")
    # use existing test asset
    p = Path("tests/data/left.jpg")
    assert p.exists()
    assert plugin.apply(str(p), dry_run=True) is True


def test_windows_plugin_missing_file():
    plugin = plugins.registry.get("windows")
    assert plugin.apply("nonexistent-file.jpg", dry_run=True) is False


def test_macos_plugin_dry_run():
    plugin = plugins.registry.get("macos")
    p = Path("tests/data/left.jpg")
    assert plugin.apply(str(p), dry_run=True) is True


def test_linux_plugin_dry_run():
    plugin = plugins.registry.get("linux")
    p = Path("tests/data/left.jpg")
    assert plugin.apply(str(p), dry_run=True) is True


def test_macos_plugin_missing_file():
    plugin = plugins.registry.get("macos")
    assert plugin.apply("nonexistent-file.jpg", dry_run=True) is False


def test_linux_plugin_missing_file():
    plugin = plugins.registry.get("linux")
    assert plugin.apply("nonexistent-file.jpg", dry_run=True) is False

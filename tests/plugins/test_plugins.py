import shutil
import subprocess
import ctypes
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
    # Provide a mapping for DP-1 and ensure candidate application succeeds.
    res = plugin.apply({"DP-1": "/tmp/fake.jpg"})
    assert res is True
from harite import plugins
from pathlib import Path


def test_registry_contains_windows():
    names = plugins.registry.list()
    assert "windows" in names
    assert "macos" in names
    assert "linux" in names


def test_windows_plugin_apply_success(monkeypatch):
    plugin = plugins.registry.get("windows")
    p = Path("tests/data/left.jpg")
    assert p.exists()
    monkeypatch.setattr(
        "harite.windows_wallpaper.apply_windows_wallpaper_file",
        lambda path: str(path).endswith("left.jpg"),
    )
    assert plugin.apply(str(p)) is True


def test_windows_plugin_missing_file():
    plugin = plugins.registry.get("windows")
    assert plugin.apply("nonexistent-file.jpg") is False


def test_windows_plugin_rejects_monitor_map():
    plugin = plugins.registry.get("windows")
    assert plugin.apply({"HDMI-1": "tests/data/left.jpg"}) is False


def test_macos_plugin_apply(monkeypatch):
    plugin = plugins.registry.get("macos")
    p = Path("tests/data/left.jpg")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=""))
    assert plugin.apply(str(p)) is True


def test_macos_plugin_rejects_monitor_map():
    plugin = plugins.registry.get("macos")
    assert plugin.apply({"HDMI-1": "tests/data/left.jpg"}) is False


def test_linux_plugin_apply(monkeypatch):
    plugin = plugins.registry.get("linux")
    p = Path("tests/data/left.jpg")
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/gsettings" if name == "gsettings" else None)
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=""))
    assert plugin.apply(str(p)) is True


def test_macos_plugin_missing_file():
    plugin = plugins.registry.get("macos")
    assert plugin.apply("nonexistent-file.jpg") is False


def test_linux_plugin_missing_file():
    plugin = plugins.registry.get("linux")
    assert plugin.apply("nonexistent-file.jpg") is False

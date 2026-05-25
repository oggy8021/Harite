import shutil
import subprocess
from pathlib import Path

from harite.plugins import LinuxPlugin


def test_linux_plugin_mapping_apply(monkeypatch, caplog):
    sample_props = "/backdrop/screen0/monitorDP-1/workspace0/last-image\n/backdrop/screen0/monitorHDMI-1/last-image\n"

    class FakeRun:
        def __init__(self, returncode=0, stdout=""):
            self.returncode = returncode
            self.stdout = stdout

    def fake_which(cmd):
        return "/usr/bin/xfconf-query" if cmd == "xfconf-query" else None

    monkeypatch.setattr(shutil, "which", fake_which)

    def fake_run(args, check=False, capture_output=False, text=False, stderr=None):
        # listing call
        if args[:3] == ["xfconf-query", "-c", "xfce4-desktop"]:
            return FakeRun(returncode=0, stdout=sample_props)
        return FakeRun(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    caplog.set_level("INFO")
    plugin = LinuxPlugin()
    mapping = {"DP-1": "/tmp/left.jpg", "HDMI-1": "/tmp/right.jpg"}
    ok = plugin.apply(mapping)
    assert ok
    assert "XFCE: run" in caplog.text
    assert str(Path("/tmp/left.jpg").resolve()) in caplog.text
    assert str(Path("/tmp/right.jpg").resolve()) in caplog.text

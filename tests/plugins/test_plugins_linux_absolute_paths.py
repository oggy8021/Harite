import shutil
import subprocess
from types import SimpleNamespace

from harite.plugins import LinuxPlugin


def test_linux_plugin_resolves_relative_path_before_xfconf_set(tmp_path, monkeypatch):
    wallpaper = tmp_path / "wall.png"
    wallpaper.write_bytes(b"fakepng")

    monkeypatch.chdir(tmp_path)

    def fake_which(cmd):
        if cmd == "xfconf-query":
            return "/usr/bin/xfconf-query"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)

    calls = []

    def fake_run(args, check=False, capture_output=False, text=False):
        calls.append(args)
        if args[:4] == ["xfconf-query", "-c", "xfce4-desktop", "-l"]:
            return SimpleNamespace(returncode=0, stdout="/backdrop/screen0/monitor0/workspace0/last-image\n")
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    lp = LinuxPlugin()
    assert lp.apply("wall.png") is True

    set_calls = [c for c in calls if c[:4] != ["xfconf-query", "-c", "xfce4-desktop", "-l"]]
    assert set_calls
    # -s argument should be absolute path
    assert str(wallpaper.resolve()) in set_calls[0]

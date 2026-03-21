import subprocess
import shutil
from types import SimpleNamespace

from harite.plugins import LinuxPlugin


def test_feh_apply_non_dry_run(tmp_path, monkeypatch):
    p = tmp_path / "wall.png"
    p.write_bytes(b"fakepng")

    # no xfconf-query/gsettings, feh present
    def fake_which(cmd):
        if cmd == "feh":
            return "/usr/bin/feh"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)

    def fake_run(args, check=False, capture_output=False, text=False):
        if isinstance(args, list) and args[0] == "feh":
            return SimpleNamespace(returncode=0, stdout="")
        return SimpleNamespace(returncode=1, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    lp = LinuxPlugin()
    assert lp.apply(str(p), dry_run=False) is True

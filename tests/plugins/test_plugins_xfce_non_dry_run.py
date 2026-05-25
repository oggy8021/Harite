import subprocess
import shutil
from types import SimpleNamespace

from harite.plugins import LinuxPlugin


def test_xfce_apply_non_dry_run(tmp_path, monkeypatch):
    # create a fake wallpaper file
    p = tmp_path / "wall.png"
    p.write_bytes(b"fakepng")

    # make xfconf-query present, gsettings/feh absent
    def fake_which(cmd):
        if cmd == "xfconf-query":
            return "/usr/bin/xfconf-query"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)

    # simulate `xfconf-query -c xfce4-desktop -l` returning some properties
    def fake_run(args, check=False, capture_output=False, text=False):
        cmd = args if isinstance(args, list) else args
        # listing properties
        if cmd[:4] == ["xfconf-query", "-c", "xfce4-desktop", "-l"]:
            return SimpleNamespace(returncode=0, stdout="/xfce4-desktop/last-image\n/xfce4-desktop/workspace0/last-image\n/xfce4-desktop/monitor1/image\n")
        # setting property -> success
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    lp = LinuxPlugin()
    assert lp.apply(str(p)) is True

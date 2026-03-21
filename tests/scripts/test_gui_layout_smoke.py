import json
from pathlib import Path
import subprocess
import sys


def test_gui_layout_smoke_runs_and_writes(tmp_path: Path):
    out = tmp_path / "layout.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--out-file",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "title" in data
    assert "form_state" in data

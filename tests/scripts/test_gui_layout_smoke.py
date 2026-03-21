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


def test_gui_layout_smoke_validate_passes_with_simulation(tmp_path: Path):
    out = tmp_path / "layout-validate-pass.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--out-file",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["validation"]["ok"] is True


def test_gui_layout_smoke_validate_fails_without_input(tmp_path: Path):
    out = tmp_path / "layout-validate-fail.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--validate",
            "--out-file",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["validation"]["ok"] is False
    assert data["validation"]["input_present"] is False

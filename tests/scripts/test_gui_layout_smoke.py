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
    assert data["validation"]["failed_checks"] == []


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
    assert "input_present" in data["validation"]["failed_checks"]


def test_gui_layout_smoke_writes_markdown_report(tmp_path: Path):
    out_json = tmp_path / "layout-md.json"
    out_md = tmp_path / "layout.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--scope",
            "windows/gui",
            "--out-file",
            str(out_json),
            "--markdown-out",
            str(out_md),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    text = out_md.read_text(encoding="utf-8")
    assert "### Manual device validation" in text
    assert "- Scope: windows/gui" in text
    assert "- GUI smoke: pass" in text


def test_gui_layout_smoke_markdown_report_can_fail(tmp_path: Path):
    out_json = tmp_path / "layout-md-fail.json"
    out_md = tmp_path / "layout-fail.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--validate",
            "--out-file",
            str(out_json),
            "--markdown-out",
            str(out_md),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    text = out_md.read_text(encoding="utf-8")
    assert "- GUI smoke: fail" in text
    assert "- Failed checks:" in text


def test_gui_layout_smoke_print_markdown_to_stdout(tmp_path: Path):
    out_json = tmp_path / "layout-print-md.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--scope",
            "windows/gui",
            "--out-file",
            str(out_json),
            "--print-markdown",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "### Manual device validation" in proc.stdout
    assert "- Scope: windows/gui" in proc.stdout

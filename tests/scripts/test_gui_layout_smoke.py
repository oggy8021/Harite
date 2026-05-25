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


def test_gui_layout_smoke_writes_pr_comment_template(tmp_path: Path):
    out_json = tmp_path / "layout-pr-comment.json"
    out_pr = tmp_path / "pr-comment.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--scope",
            "windows/gui",
            "--notes",
            "manual screenshots attached",
            "--optimize-result",
            "pass",
            "--apply-result",
            "pass",
            "--out-file",
            str(out_json),
            "--pr-comment-out",
            str(out_pr),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    text = out_pr.read_text(encoding="utf-8")
    assert "### Manual device validation" in text
    assert "- Scope: windows/gui" in text
    assert "- optimize: pass" in text
    assert "- apply: pass" in text
    assert "- GUI smoke: pass" in text
    assert "- Notes: manual screenshots attached" in text


def test_gui_layout_smoke_pr_comment_includes_screenshots_when_provided(tmp_path: Path):
    out_json = tmp_path / "layout-pr-comment-shots.json"
    out_pr = tmp_path / "pr-comment-shots.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--out-file",
            str(out_json),
            "--pr-comment-out",
            str(out_pr),
            "--screenshot-mainwindow",
            "out/manual-validation/pr-146-xfce-mainwindow.png",
            "--screenshot-optimize",
            "out/manual-validation/pr-146-xfce-optimize.png",
            "--screenshot-apply",
            "out/manual-validation/pr-146-xfce-apply.png",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    text = out_pr.read_text(encoding="utf-8")
    assert "### Screenshots" in text
    assert "- MainWindow: out/manual-validation/pr-146-xfce-mainwindow.png" in text


def test_gui_layout_smoke_print_pr_comment_to_stdout(tmp_path: Path):
    out_json = tmp_path / "layout-pr-comment-print.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--validate",
            "--out-file",
            str(out_json),
            "--print-pr-comment",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "### Manual device validation" in proc.stdout
    assert "- GUI smoke: fail" in proc.stdout


def test_gui_layout_smoke_writes_full_validation_report(tmp_path: Path):
    out_json = tmp_path / "layout-report.json"
    out_report = tmp_path / "manual-report.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--pr-number",
            "140",
            "--scope",
            "windows/gui",
            "--date",
            "2026-03-21",
            "--operator",
            "owner",
            "--optimize-result",
            "pass",
            "--apply-result",
            "pass",
            "--screenshot-mainwindow",
            "out/manual-validation/pr-140-windows-mainwindow.png",
            "--screenshot-optimize",
            "out/manual-validation/pr-140-windows-optimize.png",
            "--screenshot-apply",
            "out/manual-validation/pr-140-windows-apply.png",
            "--out-file",
            str(out_json),
            "--report-out",
            str(out_report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    text = out_report.read_text(encoding="utf-8")
    assert "# GUI Manual Validation Report" in text
    assert "- PR: 140" in text
    assert "| optimize | pass | manual declaration |" in text
    assert "| apply | pass | manual declaration |" in text
    assert "- MainWindow: out/manual-validation/pr-140-windows-mainwindow.png" in text


def test_gui_layout_smoke_print_report_to_stdout(tmp_path: Path):
    out_json = tmp_path / "layout-report-print.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--validate",
            "--out-file",
            str(out_json),
            "--print-report",
            "--pr-number",
            "local",
            "--scope",
            "windows/gui",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "# GUI Manual Validation Report" in proc.stdout
    assert "| GUI smoke | fail |" in proc.stdout


def test_gui_layout_smoke_auto_artifacts_writes_all_outputs(tmp_path: Path):
    artifact_dir = tmp_path / "out" / "manual-validation"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--auto-artifacts",
            "--artifact-dir",
            str(artifact_dir),
            "--pr-number",
            "141",
            "--scope",
            "windows/gui",
            "--optimize-result",
            "pass",
            "--apply-result",
            "pass",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    out_json = artifact_dir / "pr-141-windows.json"
    out_report = artifact_dir / "pr-141-windows.md"
    out_pr = artifact_dir / "pr-141-windows-pr-comment.md"
    out_smoke = artifact_dir / "pr-141-windows-smoke.md"

    assert out_json.exists()
    assert out_report.exists()
    assert out_pr.exists()
    assert out_smoke.exists()

    report_text = out_report.read_text(encoding="utf-8")
    assert "- PR: 141" in report_text
    assert "## Screenshots" not in report_text
    assert "- Screenshot(mainwindow):" not in report_text


def test_gui_layout_smoke_auto_artifacts_uses_scope_fallback_name(tmp_path: Path):
    artifact_dir = tmp_path / "out" / "manual-validation"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--auto-artifacts",
            "--artifact-dir",
            str(artifact_dir),
            "--pr-number",
            "142",
            "--scope",
            "xfce/linux",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    # scope prefix is used as OS name for artifact keys
    assert (artifact_dir / "pr-142-xfce.json").exists()


def test_gui_layout_smoke_normalizes_manual_result_aliases(tmp_path: Path):
    out_json = tmp_path / "layout-legacy-alias.json"
    out_pr = tmp_path / "pr-comment-legacy.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--optimize-result",
            "n/a (manual)",
            "--apply-result",
            "n/a",
            "--out-file",
            str(out_json),
            "--pr-comment-out",
            str(out_pr),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    text = out_pr.read_text(encoding="utf-8")
    assert "- optimize: not-available" in text
    assert "- apply: not-available" in text


def test_gui_layout_smoke_rejects_invalid_manual_result(tmp_path: Path):
    out_json = tmp_path / "layout-invalid-result.json"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--optimize-result",
            "maybe",
            "--out-file",
            str(out_json),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 2
    assert "invalid manual result" in proc.stderr


def test_gui_layout_smoke_require_screenshots_fails_when_missing(tmp_path: Path):
    out_json = tmp_path / "layout-require-shot.json"
    out_report = tmp_path / "report.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--out-file",
            str(out_json),
            "--report-out",
            str(out_report),
            "--require-screenshots",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 3
    assert "missing required screenshot path(s)" in proc.stderr


def test_gui_layout_smoke_require_screenshots_fails_for_pr_comment_when_missing(tmp_path: Path):
    out_json = tmp_path / "layout-require-shot-pr-comment.json"
    out_pr = tmp_path / "pr-comment.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--out-file",
            str(out_json),
            "--pr-comment-out",
            str(out_pr),
            "--require-screenshots",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 3
    assert "missing required screenshot path(s)" in proc.stderr


def test_gui_layout_smoke_require_screenshots_passes_with_paths(tmp_path: Path):
    out_json = tmp_path / "layout-require-shot-ok.json"
    out_report = tmp_path / "report-ok.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--out-file",
            str(out_json),
            "--report-out",
            str(out_report),
            "--require-screenshots",
            "--screenshot-mainwindow",
            "out/manual-validation/pr-143-windows-mainwindow.png",
            "--screenshot-optimize",
            "out/manual-validation/pr-143-windows-optimize.png",
            "--screenshot-apply",
            "out/manual-validation/pr-143-windows-apply.png",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    assert out_report.exists()
    text = out_report.read_text(encoding="utf-8")
    assert "## Screenshots" in text
    assert "- MainWindow: out/manual-validation/pr-143-windows-mainwindow.png" in text


def test_gui_layout_smoke_verify_screenshot_files_fails_when_missing(tmp_path: Path):
    out_json = tmp_path / "layout-verify-shot.json"
    out_report = tmp_path / "report-verify.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--out-file",
            str(out_json),
            "--report-out",
            str(out_report),
            "--require-screenshots",
            "--verify-screenshot-files",
            "--screenshot-mainwindow",
            "missing-mainwindow.png",
            "--screenshot-optimize",
            "missing-optimize.png",
            "--screenshot-apply",
            "missing-apply.png",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 4
    assert "missing screenshot file(s):" in proc.stderr


def test_gui_layout_smoke_verify_screenshot_files_fails_for_pr_comment_when_missing(tmp_path: Path):
    out_json = tmp_path / "layout-verify-shot-pr-comment.json"
    out_pr = tmp_path / "pr-comment.md"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--out-file",
            str(out_json),
            "--pr-comment-out",
            str(out_pr),
            "--require-screenshots",
            "--verify-screenshot-files",
            "--screenshot-mainwindow",
            "missing-mainwindow.png",
            "--screenshot-optimize",
            "missing-optimize.png",
            "--screenshot-apply",
            "missing-apply.png",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 4
    assert "missing screenshot file(s):" in proc.stderr


def test_gui_layout_smoke_verify_screenshot_files_passes_when_present(tmp_path: Path):
    out_json = tmp_path / "layout-verify-shot-ok.json"
    out_report = tmp_path / "report-verify-ok.md"
    main = tmp_path / "mainwindow.png"
    optimize = tmp_path / "optimize.png"
    apply = tmp_path / "apply.png"
    main.write_bytes(b"x")
    optimize.write_bytes(b"x")
    apply.write_bytes(b"x")

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--out-file",
            str(out_json),
            "--report-out",
            str(out_report),
            "--require-screenshots",
            "--verify-screenshot-files",
            "--screenshot-mainwindow",
            str(main),
            "--screenshot-optimize",
            str(optimize),
            "--screenshot-apply",
            str(apply),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    assert out_report.exists()


def test_gui_layout_smoke_strict_manual_fails_without_screenshots(tmp_path: Path):
    artifact_dir = tmp_path / "out" / "manual-validation"
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--strict-manual",
            "--artifact-dir",
            str(artifact_dir),
            "--pr-number",
            "145",
            "--scope",
            "windows/gui",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 4
    assert "missing screenshot file(s):" in proc.stderr


def test_gui_layout_smoke_strict_manual_passes_with_existing_screenshots(tmp_path: Path):
    artifact_dir = tmp_path / "out" / "manual-validation"
    main = artifact_dir / "pr-145-windows-mainwindow.png"
    optimize = artifact_dir / "pr-145-windows-optimize.png"
    apply = artifact_dir / "pr-145-windows-apply.png"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    main.write_bytes(b"x")
    optimize.write_bytes(b"x")
    apply.write_bytes(b"x")

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/gui_layout_smoke.py",
            "--simulate",
            "--validate",
            "--strict-manual",
            "--artifact-dir",
            str(artifact_dir),
            "--pr-number",
            "145",
            "--scope",
            "windows/gui",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    assert (artifact_dir / "pr-145-windows.json").exists()
    assert (artifact_dir / "pr-145-windows.md").exists()
    assert (artifact_dir / "pr-145-windows-pr-comment.md").exists()
    report_text = (artifact_dir / "pr-145-windows.md").read_text(encoding="utf-8")
    pr_comment_text = (artifact_dir / "pr-145-windows-pr-comment.md").read_text(
        encoding="utf-8"
    )
    assert "## Screenshots" in report_text
    assert "- Screenshot(mainwindow): out/manual-validation/pr-145-windows-mainwindow.png" in report_text
    assert "### Screenshots" in pr_comment_text
    assert "- MainWindow:" in pr_comment_text
    assert "pr-145-windows-mainwindow.png" in pr_comment_text

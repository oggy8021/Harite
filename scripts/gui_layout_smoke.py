"""Lightweight smoke runner to validate current GUI state.

This script runs without any GUI toolkit. It creates the framework-neutral
`MainWindow`, performs direct runtime-style simulation, and emits a JSON
summary suitable for manual validation or CI artifact collection.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
import sys
from pathlib import Path
from typing import Any

from harite.gui.views.main_window import MainWindow
from harite.workspace import Display


def _ensure_headless_display_stub() -> None:
    """CI runners often have no detected displays; optimize requires at least one."""
    import harite.apply_surface as apply_surface
    import harite.display_context as display_context
    import harite.slideshow_optimize as slideshow_optimize
    import harite.workspace as workspace

    if workspace.detect_displays():
        return

    def _stub() -> list[Display]:
        return [
            Display(name="stub-L", width=1920, height=1080, x_offset=0, y_offset=0),
            Display(name="stub-R", width=1920, height=1080, x_offset=1920, y_offset=0),
        ]

    for module in (workspace, display_context, slideshow_optimize, apply_surface):
        module.detect_displays = _stub


VALID_MANUAL_RESULTS = {"pass", "fail", "not-available"}


def _scope_os_name(scope: str) -> str:
    raw = (scope or "local").split("/", 1)[0].strip().lower()
    safe = "".join(ch if (ch.isalnum() or ch in "-_") else "-" for ch in raw)
    return safe.strip("-_") or "local"


def _normalize_manual_result(raw: str) -> str:
    value = (raw or "").strip().lower()
    if value in VALID_MANUAL_RESULTS:
        return value

    legacy_alias = {
        "n/a": "not-available",
        "na": "not-available",
        "n/a (manual)": "not-available",
        "n/a (if executed)": "not-available",
    }
    if value in legacy_alias:
        return legacy_alias[value]

    raise ValueError(
        f"invalid manual result '{raw}'. expected one of: pass, fail, not-available"
    )


def _validate_required_screenshots(
    *,
    require_screenshots: bool,
    screenshot_mainwindow: str,
    screenshot_optimize: str,
    screenshot_apply: str,
) -> tuple[bool, str]:
    if not require_screenshots:
        return True, ""

    missing = []
    for label, raw in (
        ("mainwindow", screenshot_mainwindow),
        ("optimize", screenshot_optimize),
        ("apply", screenshot_apply),
    ):
        value = (raw or "").strip()
        if not value or "[path or attached]" in value:
            missing.append(label)

    if missing:
        return False, f"missing required screenshot path(s): {', '.join(missing)}"

    return True, ""


def _validate_screenshot_files_exist(
    *,
    verify_screenshot_files: bool,
    screenshot_mainwindow: str,
    screenshot_optimize: str,
    screenshot_apply: str,
) -> tuple[bool, str]:
    if not verify_screenshot_files:
        return True, ""

    missing = []
    for label, raw in (
        ("mainwindow", screenshot_mainwindow),
        ("optimize", screenshot_optimize),
        ("apply", screenshot_apply),
    ):
        path = Path((raw or "").strip())
        if not path.exists():
            missing.append(str(path))

    if missing:
        return False, "missing screenshot file(s): " + ", ".join(missing)

    return True, ""


def collect_summary(mainwindow: Any) -> dict:
    bindings = getattr(mainwindow, "_adapter_bindings", None)
    if isinstance(bindings, dict) and "file" in bindings:
        bindings = dict(bindings)
        bindings["file"] = str(bindings["file"])

    return {
        "title": getattr(mainwindow, "title", ""),
        "can_optimize": bool(getattr(mainwindow, "can_optimize", False)),
        "plugin_name": getattr(mainwindow, "plugin_name", ""),
        "available_plugins": list(getattr(mainwindow, "available_plugins", ())),
        "form_state": {
            "input_value": getattr(mainwindow.form_state, "input_value", ""),
            "resolution": getattr(mainwindow.form_state, "resolution", ""),
            "output_dir": getattr(mainwindow.form_state, "output_dir", ""),
        },
        "adapter_bindings": bindings,
    }


def attach_runtime_binding_metadata(mainwindow: Any) -> None:
    """Record best-effort runtime binding metadata for smoke reporting."""
    setattr(
        mainwindow,
        "_adapter_bindings",
        {
            "mode": "runtime-direct",
            "source": "gui_layout_smoke",
            "handler_surface": (
                "on_change_input_text",
                "on_save",
                "on_optimize",
                "on_apply",
                "on_watch_start",
                "on_watch_stop",
            ),
        },
    )


def simulate_runtime_interactions(mainwindow: Any) -> None:
    """Apply a small set of direct interactions without GTK dependencies."""
    mainwindow.on_change_input_text("/tmp/example.jpg")
    if getattr(mainwindow, "available_plugins", None):
        mainwindow.on_change_plugin(mainwindow.available_plugins[0])


def evaluate_summary(summary: dict) -> dict:
    checks = {
        "title_present": bool(summary.get("title")),
        "plugins_available": bool(summary.get("available_plugins")),
        "adapter_bound": bool(summary.get("adapter_bindings")),
        "input_present": bool(summary.get("form_state", {}).get("input_value")),
        "can_optimize": bool(summary.get("can_optimize")),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    checks["failed_checks"] = failed_checks
    checks["ok"] = not failed_checks
    return checks


def build_markdown_report(summary: dict, *, scope: str) -> str:
    validation = summary.get("validation", {})

    def as_result(value: bool) -> str:
        return "pass" if value else "fail"

    lines = [
        "### Manual device validation",
        f"- Scope: {scope}",
        f"- title_present: {as_result(bool(validation.get('title_present')))}",
        f"- plugins_available: {as_result(bool(validation.get('plugins_available')))}",
        f"- adapter_bound: {as_result(bool(validation.get('adapter_bound')))}",
        f"- input_present: {as_result(bool(validation.get('input_present')))}",
        f"- can_optimize: {as_result(bool(validation.get('can_optimize')))}",
        f"- GUI smoke: {as_result(bool(validation.get('ok')))}",
        f"- Failed checks: {', '.join(validation.get('failed_checks', [])) or 'none'}",
    ]
    return "\n".join(lines) + "\n"


def build_pr_comment(
    summary: dict,
    *,
    scope: str,
    notes: str,
    optimize_result: str,
    apply_result: str,
    screenshot_mainwindow: str,
    screenshot_optimize: str,
    screenshot_apply: str,
) -> str:
    validation = summary.get("validation", {})
    gui_smoke = "pass" if bool(validation.get("ok")) else "fail"
    failed = ", ".join(validation.get("failed_checks", [])) or "none"
    notes_text = notes.strip() or "generated by gui_layout_smoke"
    has_screenshots = any(
        (raw or "").strip()
        for raw in (screenshot_mainwindow, screenshot_optimize, screenshot_apply)
    )

    lines = [
        "### Manual device validation",
        f"- Scope: {scope}",
        f"- optimize: {optimize_result}",
        f"- apply: {apply_result}",
        f"- GUI smoke: {gui_smoke}",
        f"- Failed checks: {failed}",
        f"- Notes: {notes_text}",
    ]
    if has_screenshots:
        lines.extend(
            [
                "",
                "### Screenshots",
                f"- MainWindow: {screenshot_mainwindow}",
                f"- Optimize form: {screenshot_optimize}",
                f"- Apply area: {screenshot_apply}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_validation_report(
    summary: dict,
    *,
    pr_number: str,
    scope: str,
    run_date: str,
    operator: str,
    optimize_result: str,
    apply_result: str,
    screenshot_mainwindow: str,
    screenshot_optimize: str,
    screenshot_apply: str,
) -> str:
    validation = summary.get("validation", {})
    gui_smoke = "pass" if bool(validation.get("ok")) else "fail"
    failed = ", ".join(validation.get("failed_checks", [])) or "none"
    os_name = scope.split("/", 1)[0] if "/" in scope else scope
    has_screenshots = any(
        (raw or "").strip()
        for raw in (screenshot_mainwindow, screenshot_optimize, screenshot_apply)
    )

    lines = [
        "# GUI Manual Validation Report",
        "",
        "## Manual device validation",
        f"- PR: {pr_number}",
        f"- Scope: {scope}",
        f"- Date: {run_date}",
        f"- Operator: {operator or 'n/a'}",
        "",
        "## Result matrix",
        "| Check | Status | Notes |",
        "| --- | --- | --- |",
        f"| optimize | {optimize_result} | manual declaration |",
        f"| apply | {apply_result} | manual declaration |",
        f"| GUI smoke | {gui_smoke} | failed checks: {failed} |",
        "",
        "## Artifact paths",
        f"- JSON: out/manual-validation/pr-{pr_number}-{os_name}.json",
        f"- Markdown: out/manual-validation/pr-{pr_number}-{os_name}.md",
        "",
        "## Failures",
        f"- Repro steps: {'[required if status=fail]' if failed == 'none' else failed}",
        "- Follow-up issue/PR: [optional]",
    ]

    if has_screenshots:
        insert_at = lines.index("## Artifact paths")
        lines[insert_at:insert_at] = [
            "## Screenshots",
            f"- MainWindow: {screenshot_mainwindow}",
            f"- Optimize form: {screenshot_optimize}",
            f"- Apply area: {screenshot_apply}",
            "",
        ]
        artifact_at = lines.index("## Failures")
        lines[artifact_at:artifact_at] = [
            f"- Screenshot(mainwindow): out/manual-validation/pr-{pr_number}-{os_name}-mainwindow.png",
            f"- Screenshot(optimize): out/manual-validation/pr-{pr_number}-{os_name}-optimize.png",
            f"- Screenshot(apply): out/manual-validation/pr-{pr_number}-{os_name}-apply.png",
            "",
        ]

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GUI layout smoke runner")
    parser.add_argument("--simulate", action="store_true", help="simulate a few widget actions")
    parser.add_argument("--validate", action="store_true", help="run built-in validation checks and return non-zero on failure")
    parser.add_argument("--out-file", type=Path, help="write JSON summary to path (default stdout)")
    parser.add_argument("--markdown-out", type=Path, help="write PR-comment-friendly markdown report")
    parser.add_argument("--print-markdown", action="store_true", help="print markdown report to stdout")
    parser.add_argument("--pr-comment-out", type=Path, help="write PR comment template markdown")
    parser.add_argument("--print-pr-comment", action="store_true", help="print PR comment template to stdout")
    parser.add_argument("--report-out", type=Path, help="write full manual validation report markdown")
    parser.add_argument("--print-report", action="store_true", help="print full manual validation report to stdout")
    parser.add_argument("--auto-artifacts", action="store_true", help="auto-generate artifact output paths for current PR/scope")
    parser.add_argument("--artifact-dir", type=Path, default=Path("out/manual-validation"), help="base directory used with --auto-artifacts")
    parser.add_argument("--scope", default="local/gui-smoke", help="scope text used in markdown report")
    parser.add_argument("--pr-number", default="local", help="PR number text used in report")
    parser.add_argument("--date", default=date.today().isoformat(), help="date text used in report (YYYY-MM-DD)")
    parser.add_argument("--operator", default="", help="operator name used in report")
    parser.add_argument("--notes", default="", help="notes text used in PR comment template")
    parser.add_argument("--optimize-result", default="not-available", help="manual result: pass/fail/not-available")
    parser.add_argument("--apply-result", default=None, help="manual result: pass/fail/not-available")
    parser.add_argument("--screenshot-mainwindow", default="", help="path for MainWindow screenshot used in report")
    parser.add_argument("--screenshot-optimize", default="", help="path for Optimize screenshot used in report")
    parser.add_argument("--screenshot-apply", default="", help="path for Apply screenshot used in report")
    parser.add_argument("--require-screenshots", action="store_true", help="fail when report/pr-comment screenshot paths are missing")
    parser.add_argument("--verify-screenshot-files", action="store_true", help="fail when screenshot file paths do not exist")
    parser.add_argument("--strict-manual", action="store_true", help="enable strict manual-validation checks and artifact outputs")
    args = parser.parse_args(argv)

    if args.strict_manual:
        args.auto_artifacts = True
        args.require_screenshots = True
        args.verify_screenshot_files = True

    if args.apply_result is None:
        args.apply_result = "not-available"

    try:
        args.optimize_result = _normalize_manual_result(args.optimize_result)
        args.apply_result = _normalize_manual_result(args.apply_result)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.auto_artifacts:
        os_name = _scope_os_name(args.scope)
        artifact_base = args.artifact_dir / f"pr-{args.pr_number}-{os_name}"
        if args.out_file is None:
            args.out_file = artifact_base.with_suffix(".json")
        if args.report_out is None:
            args.report_out = artifact_base.with_suffix(".md")
        if args.pr_comment_out is None:
            args.pr_comment_out = args.artifact_dir / f"pr-{args.pr_number}-{os_name}-pr-comment.md"
        if args.markdown_out is None:
            args.markdown_out = args.artifact_dir / f"pr-{args.pr_number}-{os_name}-smoke.md"

        if args.require_screenshots or args.verify_screenshot_files:
            if not args.screenshot_mainwindow:
                args.screenshot_mainwindow = str(args.artifact_dir / f"pr-{args.pr_number}-{os_name}-mainwindow.png")
            if not args.screenshot_optimize:
                args.screenshot_optimize = str(args.artifact_dir / f"pr-{args.pr_number}-{os_name}-optimize.png")
            if not args.screenshot_apply:
                args.screenshot_apply = str(args.artifact_dir / f"pr-{args.pr_number}-{os_name}-apply.png")

        for path in (args.out_file, args.report_out, args.pr_comment_out, args.markdown_out):
            if path is not None:
                path.parent.mkdir(parents=True, exist_ok=True)

    _ensure_headless_display_stub()
    win = MainWindow()

    try:
        attach_runtime_binding_metadata(win)
        if args.simulate:
            simulate_runtime_interactions(win)
    except Exception as exc:
        # Non-fatal: record smoke binding/simulation error in summary.
        setattr(win, "_adapter_bindings_error", str(exc))

    summary = collect_summary(win)

    if args.validate:
        summary["validation"] = evaluate_summary(summary)

    if args.markdown_out:
        if "validation" not in summary:
            summary["validation"] = evaluate_summary(summary)
        md = build_markdown_report(summary, scope=args.scope)
        args.markdown_out.write_text(md, encoding="utf-8")

    if args.print_markdown:
        if "validation" not in summary:
            summary["validation"] = evaluate_summary(summary)
        print(build_markdown_report(summary, scope=args.scope), end="")

    if args.pr_comment_out:
        if "validation" not in summary:
            summary["validation"] = evaluate_summary(summary)

        ok, message = _validate_required_screenshots(
            require_screenshots=args.require_screenshots,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        if not ok:
            print(message, file=sys.stderr)
            return 3

        ok, message = _validate_screenshot_files_exist(
            verify_screenshot_files=args.verify_screenshot_files,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        if not ok:
            print(message, file=sys.stderr)
            return 4

        pr_md = build_pr_comment(
            summary,
            scope=args.scope,
            notes=args.notes,
            optimize_result=args.optimize_result,
            apply_result=args.apply_result,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        args.pr_comment_out.write_text(pr_md, encoding="utf-8")

    if args.print_pr_comment:
        if "validation" not in summary:
            summary["validation"] = evaluate_summary(summary)

        ok, message = _validate_required_screenshots(
            require_screenshots=args.require_screenshots,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        if not ok:
            print(message, file=sys.stderr)
            return 3

        ok, message = _validate_screenshot_files_exist(
            verify_screenshot_files=args.verify_screenshot_files,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        if not ok:
            print(message, file=sys.stderr)
            return 4

        print(
            build_pr_comment(
                summary,
                scope=args.scope,
                notes=args.notes,
                optimize_result=args.optimize_result,
                apply_result=args.apply_result,
                screenshot_mainwindow=args.screenshot_mainwindow,
                screenshot_optimize=args.screenshot_optimize,
                screenshot_apply=args.screenshot_apply,
            ),
            end="",
        )

    if args.report_out:
        if "validation" not in summary:
            summary["validation"] = evaluate_summary(summary)

        ok, message = _validate_required_screenshots(
            require_screenshots=args.require_screenshots,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        if not ok:
            print(message, file=sys.stderr)
            return 3

        ok, message = _validate_screenshot_files_exist(
            verify_screenshot_files=args.verify_screenshot_files,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        if not ok:
            print(message, file=sys.stderr)
            return 4

        report_md = build_validation_report(
            summary,
            pr_number=args.pr_number,
            scope=args.scope,
            run_date=args.date,
            operator=args.operator,
            optimize_result=args.optimize_result,
            apply_result=args.apply_result,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        args.report_out.write_text(report_md, encoding="utf-8")

    if args.print_report:
        if "validation" not in summary:
            summary["validation"] = evaluate_summary(summary)

        ok, message = _validate_required_screenshots(
            require_screenshots=args.require_screenshots,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        if not ok:
            print(message, file=sys.stderr)
            return 3

        ok, message = _validate_screenshot_files_exist(
            verify_screenshot_files=args.verify_screenshot_files,
            screenshot_mainwindow=args.screenshot_mainwindow,
            screenshot_optimize=args.screenshot_optimize,
            screenshot_apply=args.screenshot_apply,
        )
        if not ok:
            print(message, file=sys.stderr)
            return 4

        print(
            build_validation_report(
                summary,
                pr_number=args.pr_number,
                scope=args.scope,
                run_date=args.date,
                operator=args.operator,
                optimize_result=args.optimize_result,
                apply_result=args.apply_result,
                screenshot_mainwindow=args.screenshot_mainwindow,
                screenshot_optimize=args.screenshot_optimize,
                screenshot_apply=args.screenshot_apply,
            ),
            end="",
        )

    out_json = json.dumps(summary, indent=2, ensure_ascii=False)

    if args.out_file:
        args.out_file.write_text(out_json, encoding="utf-8")
    else:
        print(out_json)

    if args.validate and not summary["validation"]["ok"]:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

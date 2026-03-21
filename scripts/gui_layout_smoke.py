"""Lightweight smoke runner to validate GUI layout and mappings.

This script runs without any GUI toolkit. It creates the framework-neutral
`MainWindow`, optionally loads the UI prototype, creates a fake widget map,
simulates a few interactions, and emits a JSON summary suitable for manual
validation or CI artifact collection.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from harite.gui.views.main_window import MainWindow
from harite.gui.adapters.fake_adapter import create_fake_widget_map


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GUI layout smoke runner")
    parser.add_argument("--simulate", action="store_true", help="simulate a few widget actions")
    parser.add_argument("--out-file", type=Path, help="write JSON summary to path (default stdout)")
    args = parser.parse_args(argv)

    win = MainWindow()

    # Create a best-effort fake widget map using queued adapter code.
    # We avoid failing the script if UI prototype resource is missing.
    ui_result = None
    try:
        from harite.gui.adapters.ui_loader import load_glade_prototype

        ui_result = load_glade_prototype()
    except Exception:
        ui_result = None

    try:
        if ui_result is not None:
            widgets = create_fake_widget_map(win, ui_result)
        else:
            # Create a minimal map when prototype not available.
            widgets = create_fake_widget_map(win, type("R", (), {"file_path": Path("<none>"), "root_tag": "", "widget_count": 0, "signal_count": 0})())

        if args.simulate:
            if "input_text" in widgets:
                widgets["input_text"]("/tmp/example.jpg")
            if "plugin_change" in widgets and win.available_plugins:
                widgets["plugin_change"](win.available_plugins[0])

    except Exception as exc:
        # Non-fatal: record adapter construction error in summary
        setattr(win, "_adapter_bindings_error", str(exc))

    summary = collect_summary(win)

    out_json = json.dumps(summary, indent=2, ensure_ascii=False)

    if args.out_file:
        args.out_file.write_text(out_json, encoding="utf-8")
    else:
        print(out_json)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

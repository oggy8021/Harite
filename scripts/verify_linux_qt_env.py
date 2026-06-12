#!/usr/bin/env python3
"""Verify Linux Qt + fcitx + SVG prerequisites for harite-qt (XFCE/Mint/Ubuntu).

Run from an activated venv after following requirements-linux-qt.txt:

    python scripts/verify_linux_qt_env.py

Exit 0 when the environment matches Harite's documented Linux Qt recipe.
"""

from __future__ import annotations

import sys


def _fail(messages: list[str]) -> int:
    for line in messages:
        print(line, file=sys.stderr)
    return 1


def main() -> int:
    if not sys.platform.startswith("linux"):
        print("verify_linux_qt_env: skip (not Linux)")
        return 0

    errors: list[str] = []
    notes: list[str] = []

    try:
        import PyQt6
    except ImportError:
        return _fail(
            [
                "FAIL: PyQt6 is not importable.",
                "  Install distro package: sudo apt install python3-pyqt6",
                "  Then recreate venv with: python3 -m venv .venv --system-site-packages",
            ]
        )

    pyqt_path = PyQt6.__file__
    print(f"OK: PyQt6 importable ({pyqt_path})")

    from harite.gui.adapters_qt.qt_input_method import (
        audit_qt_fcitx_input_method,
        pyqt6_install_is_pip_venv,
    )
    from harite.gui.adapters_qt.qt_svg_support import audit_qt_svg_support

    if pyqt6_install_is_pip_venv():
        errors.append(
            "FAIL: PyQt6 is installed under site-packages (pip venv copy). "
            "Harite Linux Qt expects distro PyQt6 via --system-site-packages venv. "
            "Do not: pip install PyQt6. See requirements-linux-qt.txt"
        )
    else:
        print("OK: PyQt6 resolves from system/distro packages")

    svg_audit = audit_qt_svg_support()
    if not svg_audit.get("packaged_svg_icon_loads"):
        errors.append(f"FAIL: SVG icons do not load. {svg_audit.get('package_hint')}")
    else:
        print("OK: packaged SVG icon loads")

    im_audit = audit_qt_fcitx_input_method()
    print(
        "INFO: QT_IM_MODULE={qt} GTK_IM_MODULE={gtk} XMODIFIERS={xm}".format(
            qt=im_audit.get("qt_im_module") or "(unset)",
            gtk=im_audit.get("gtk_im_module") or "(unset)",
            xm=im_audit.get("xmodifiers") or "(unset)",
        )
    )

    if im_audit.get("pip_pyqt6_fcitx_incompatible"):
        errors.append(f"FAIL: pip PyQt6 cannot use fcitx. {im_audit.get('pip_pyqt6_hint')}")
    elif not im_audit.get("fcitx_input_method_available"):
        candidates = im_audit.get("system_fcitx_qt6_plugin_candidates") or []
        if not candidates:
            errors.append(
                "FAIL: no fcitx Qt6 IM plugin found. "
                f"{im_audit.get('package_hint')}"
            )
        else:
            notes.append(
                "WARN: fcitx plugin files exist but Harite reports IM unavailable. "
                "Ensure fcitx5 is running and session env sets GTK_IM_MODULE=fcitx "
                "(Harite will set QT_IM_MODULE on startup). "
                f"Candidates: {candidates}"
            )
    else:
        print("OK: fcitx Qt input method available to PyQt6")

    for line in notes:
        print(line, file=sys.stderr)

    if errors:
        return _fail(errors)

    print("verify_linux_qt_env: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

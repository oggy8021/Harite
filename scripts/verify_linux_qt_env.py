#!/usr/bin/env python3
"""Verify Linux Qt + fcitx + SVG prerequisites for harite-qt (XFCE/Mint/Ubuntu).

Run from an activated venv after following requirements-linux-qt.txt:

    python scripts/verify_linux_qt_env.py

Exit 0 when the environment matches Harite's documented Linux Qt recipe.
"""

from __future__ import annotations

import os
import sys

_XFCE_PANEL_HINT = (
    "On XFCE, add panel item 'Status Tray Plugin' or 'Notification Area' "
    "and enable status notifier / legacy systray support."
)


def _audit_qt_system_tray_fallback() -> dict[str, object]:
    display_set = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    audit: dict[str, object] = {
        "display_set": display_set,
        "system_tray_available": False,
        "panel_hint": _XFCE_PANEL_HINT,
    }
    if not display_set:
        audit["skipped"] = True
        audit["skip_reason"] = "no DISPLAY or WAYLAND_DISPLAY"
        return audit

    try:
        from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
    except ImportError as exc:
        audit["error"] = str(exc)
        return audit

    qapp = QApplication.instance()
    created_app = False
    if qapp is None:
        qapp = QApplication([])
        created_app = True
    try:
        audit["system_tray_available"] = bool(QSystemTrayIcon.isSystemTrayAvailable())
    finally:
        if created_app and qapp is not None:
            qapp.quit()
    return audit


def _audit_qt_system_tray() -> dict[str, object]:
    """Tray diagnostics; prefers harite helper when installed."""
    try:
        from harite.gui.adapters_qt.qt_tray_adapter import audit_qt_system_tray

        return audit_qt_system_tray()
    except ImportError:
        return _audit_qt_system_tray_fallback()


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

    tray_audit = _audit_qt_system_tray()
    if tray_audit.get("skipped"):
        notes.append(
            "WARN: system tray check skipped ({reason}). Run from a graphical session.".format(
                reason=tray_audit.get("skip_reason", "no display"),
            )
        )
    elif not tray_audit.get("system_tray_available"):
        errors.append(
            "FAIL: Qt system tray is unavailable in this session. "
            f"{tray_audit.get('panel_hint')}"
        )
    else:
        print("OK: Qt system tray available")

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

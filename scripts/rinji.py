#!/usr/bin/env python3
"""Standalone Linux Qt / tray diagnostic (copy-paste friendly).

Use when verify_linux_qt_env.py references symbols not yet on your branch.
Does not import audit_qt_system_tray from harite; tray checks are inlined.

    python scripts/rinji.py

Run from a graphical XFCE session terminal (DISPLAY or WAYLAND_DISPLAY set).
"""

from __future__ import annotations

import os
import sys


XFCE_PANEL_HINT = (
    "On XFCE, add panel item 'Status Tray Plugin' or 'Notification Area' "
    "and enable status notifier / legacy systray support."
)


def _fail(messages: list[str]) -> int:
    for line in messages:
        print(line, file=sys.stderr)
    return 1


TRAY_ICON_SIZES = (16, 22, 24, 32)


def _display_session_active() -> bool:
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def probe_tray_pixmaps_inline(icon_path: object) -> dict[str, object]:
    """Requires an active QGuiApplication (see run_qt_tray_checks_inline)."""
    from pathlib import Path

    path = Path(icon_path)
    result: dict[str, object] = {
        "path": str(path),
        "exists": path.exists(),
        "sizes": {},
        "any_pixmap": False,
    }
    if not path.exists():
        return result
    try:
        from PyQt6.QtCore import QSize
        from PyQt6.QtGui import QGuiApplication, QIcon
        from PyQt6.QtWidgets import QApplication
    except ImportError as exc:
        result["error"] = str(exc)
        return result

    if QGuiApplication.instance() is None and QApplication.instance() is None:
        result["error"] = "QGuiApplication required before QPixmap"
        return result

    source = QIcon(str(path))
    sizes: dict[int, bool] = {}
    for size_px in TRAY_ICON_SIZES:
        pixmap = source.pixmap(QSize(size_px, size_px))
        ok = not pixmap.isNull() and pixmap.width() > 0 and pixmap.height() > 0
        sizes[size_px] = ok
        if ok:
            result["any_pixmap"] = True
    result["sizes"] = sizes
    return result


def run_qt_tray_checks_inline(*, tray_icon_path: object | None = None) -> dict[str, object]:
    """Pixmap + tray availability under one QApplication (avoids QPixmap abort)."""
    audit: dict[str, object] = {
        "display_set": _display_session_active(),
        "system_tray_available": False,
        "panel_hint": XFCE_PANEL_HINT,
        "pixmap_audit": None,
    }
    if not audit["display_set"]:
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
        if tray_icon_path is not None:
            audit["pixmap_audit"] = probe_tray_pixmaps_inline(tray_icon_path)
        audit["system_tray_available"] = bool(QSystemTrayIcon.isSystemTrayAvailable())
    finally:
        if created_app and qapp is not None:
            qapp.quit()
    return audit


def main() -> int:
    if not sys.platform.startswith("linux"):
        print("rinji: skip (not Linux)")
        return 0

    errors: list[str] = []
    notes: list[str] = []

    try:
        import PyQt6
    except ImportError:
        return _fail(
            [
                "FAIL: PyQt6 is not importable.",
                "  sudo apt install python3-pyqt6",
                "  venv: python3 -m venv .venv --system-site-packages",
            ]
        )

    print(f"OK: PyQt6 importable ({PyQt6.__file__})")

    try:
        from harite.gui.adapters_qt.qt_input_method import (
            audit_qt_fcitx_input_method,
            pyqt6_install_is_pip_venv,
        )
        from harite.gui.adapters_qt.qt_svg_support import audit_qt_svg_support

        if pyqt6_install_is_pip_venv():
            errors.append(
                "FAIL: PyQt6 is under site-packages (pip venv). "
                "Use --system-site-packages venv + distro python3-pyqt6."
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
                    "WARN: fcitx plugin exists but IM unavailable. "
                    f"Candidates: {candidates}"
                )
        else:
            print("OK: fcitx Qt input method available to PyQt6")
    except ImportError as exc:
        notes.append(f"WARN: harite package checks skipped ({exc}). Tray check still runs.")

    tray_icon_path = None
    try:
        from harite.gui.resource_access import gui_resource_path

        with gui_resource_path("icons", "product", "harite_app.svg") as resolved:
            tray_icon_path = resolved
    except Exception as exc:
        notes.append(f"WARN: tray pixmap probe skipped ({exc})")

    tray_audit = run_qt_tray_checks_inline(tray_icon_path=tray_icon_path)
    if tray_audit.get("skipped"):
        notes.append(
            "WARN: system tray check skipped ({reason}). Run from a graphical session.".format(
                reason=tray_audit.get("skip_reason", "no display"),
            )
        )
    elif tray_audit.get("error"):
        errors.append(f"FAIL: tray check error: {tray_audit.get('error')}")
    else:
        pixmap_audit = tray_audit.get("pixmap_audit")
        if isinstance(pixmap_audit, dict):
            if pixmap_audit.get("error"):
                errors.append(f"FAIL: tray pixmap probe error: {pixmap_audit.get('error')}")
            elif pixmap_audit.get("any_pixmap"):
                print(
                    "OK: tray-sized pixmaps from harite_app.svg "
                    f"({pixmap_audit.get('sizes')})"
                )
            elif tray_icon_path is not None:
                errors.append(
                    "FAIL: could not build tray-sized pixmaps from harite_app.svg. "
                    "Install python3-pyqt6.qtsvg and retry."
                )
        if not tray_audit.get("system_tray_available"):
            errors.append(
                "FAIL: Qt system tray is unavailable in this session. "
                f"{tray_audit.get('panel_hint')}"
            )
        else:
            print("OK: Qt system tray available")

    for line in notes:
        print(line, file=sys.stderr)

    if errors:
        return _fail(errors)

    print("rinji: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

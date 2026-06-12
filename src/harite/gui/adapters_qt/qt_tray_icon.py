"""Build rasterized QIcons for Linux/XFCE system tray hosts."""

from __future__ import annotations

from pathlib import Path

TRAY_ICON_SIZES = (16, 22, 24, 32)


def build_tray_qicon_from_path(icon_path: Path) -> object | None:
    """Return a QIcon with explicit tray-sized pixmaps (SNI hosts often reject raw SVG)."""
    try:
        from PyQt6.QtCore import QSize
        from PyQt6.QtGui import QIcon
    except ImportError:
        return None

    source = QIcon(str(icon_path))
    if source.isNull():
        return None

    icon = QIcon()
    added = False
    for size_px in TRAY_ICON_SIZES:
        pixmap = source.pixmap(QSize(size_px, size_px))
        if pixmap.isNull():
            continue
        icon.addPixmap(pixmap)
        added = True
    if not added:
        return source
    return icon


def probe_tray_icon_pixmaps(icon_path: Path) -> dict[str, object]:
    """Report whether tray-sized pixmaps can be built from an SVG resource."""
    result: dict[str, object] = {
        "path": str(icon_path),
        "exists": icon_path.exists(),
        "sizes": {},
        "any_pixmap": False,
    }
    if not icon_path.exists():
        return result

    try:
        from PyQt6.QtCore import QSize
        from PyQt6.QtGui import QGuiApplication, QIcon
        from PyQt6.QtWidgets import QApplication
    except ImportError as exc:
        result["error"] = str(exc)
        return result

    qapp = QApplication.instance()
    created_app = False
    if QGuiApplication.instance() is None and qapp is None:
        qapp = QApplication([])
        created_app = True

    source = QIcon(str(icon_path))
    sizes: dict[int, bool] = {}
    for size_px in TRAY_ICON_SIZES:
        pixmap = source.pixmap(QSize(size_px, size_px))
        ok = not pixmap.isNull() and pixmap.width() > 0 and pixmap.height() > 0
        sizes[size_px] = ok
        if ok:
            result["any_pixmap"] = True
    result["sizes"] = sizes
    if created_app and qapp is not None:
        qapp.quit()
    return result

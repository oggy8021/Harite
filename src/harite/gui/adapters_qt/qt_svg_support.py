"""Qt SVG icon support checks (distro PyQt6 often omits the image plugin)."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)

_QT_SVG_PACKAGE_HINT = (
    "Qt cannot load SVG icons (QPixmap/QIcon null). "
    "Debian/Ubuntu/Mint distro PyQt6 needs the QtSvg add-on: "
    "sudo apt install python3-pyqt6.qtsvg"
)


def qt_svg_image_format_available() -> bool:
    try:
        from PyQt6.QtGui import QImageReader
    except ImportError:
        return False

    formats = {
        bytes(fmt).decode("ascii", errors="ignore").lower()
        for fmt in QImageReader.supportedImageFormats()
    }
    return "svg" in formats


def probe_packaged_svg_icon() -> bool:
    try:
        from PyQt6.QtGui import QIcon

        from harite.gui.resource_access import gui_resource_path

        with gui_resource_path("icons", "lucide", "info.svg") as icon_path:
            return not QIcon(str(icon_path)).isNull()
    except Exception:
        return False


def audit_qt_svg_support() -> dict[str, object]:
    return {
        "svg_image_format": qt_svg_image_format_available(),
        "packaged_svg_icon_loads": probe_packaged_svg_icon(),
        "package_hint": _QT_SVG_PACKAGE_HINT,
    }


def warn_missing_qt_svg_support() -> None:
    """Warn when Harite SVG button icons cannot be rendered."""
    if not sys.platform.startswith("linux"):
        return
    if probe_packaged_svg_icon():
        return
    logger.warning("Qt SVG: %s", _QT_SVG_PACKAGE_HINT)

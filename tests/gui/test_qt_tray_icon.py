from __future__ import annotations

from harite.gui.adapters_qt.qt_tray_icon import build_tray_qicon_from_path, probe_tray_icon_pixmaps
from harite.gui.resource_access import gui_resource_path


def test_build_tray_qicon_from_product_svg(qapp):
    with gui_resource_path("icons", "product", "harite_app.svg") as icon_path:
        icon = build_tray_qicon_from_path(icon_path)
    assert icon is not None
    assert not icon.isNull()


def test_probe_tray_icon_pixmaps_reports_sizes(qapp):
    with gui_resource_path("icons", "product", "harite_app.svg") as icon_path:
        audit = probe_tray_icon_pixmaps(icon_path)
    assert audit.get("any_pixmap") is True
    assert audit.get("sizes")

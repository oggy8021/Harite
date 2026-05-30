"""Qt stylesheet for the Harite Qt backend (Phase 9).

Provides a minimal application-level stylesheet that complements the
platform default (Fusion on Windows, native on other platforms).

Design goals:
- Keep it neutral so it works on both light and dark system themes.
- Apply only specific overrides; let Qt defaults handle the rest.
- Preview boxes (QLabel#previewBox) get a dark background so empty
  placeholders are visually distinct.
"""

from __future__ import annotations

from typing import Any

# Minimal stylesheet applied to the entire QApplication.
# Uses only stable Qt stylesheet selectors.
_HARITE_QT_STYLESHEET = """
/* ---- Global ---- */
QWidget {
    font-size: 9pt;
}

/* ---- Buttons ---- */
QPushButton {
    padding: 3px 8px;
    min-width: 60px;
}
QPushButton:checked {
    font-weight: bold;
}

/* ---- Labels ---- */
QLabel#statusLabel, QLabel#errorLabel {
    color: #555;
    font-size: 8pt;
}

/* ---- Preview boxes ---- */
QLabel#previewBox {
    background-color: #2b2b2b;
    color: #888;
    border: 1px solid #555;
    min-width: 160px;
    min-height: 90px;
}

/* ---- Tabs ---- */
QTabBar::tab {
    padding: 4px 12px;
}
QTabBar::tab:selected {
    font-weight: bold;
}
"""


def build_qt_stylesheet() -> str:
    """Return the stylesheet string to be applied via QApplication.setStyleSheet()."""
    return _HARITE_QT_STYLESHEET


def apply_qt_stylesheet(qapp: Any) -> None:
    """Apply the Harite stylesheet to *qapp*.

    Silently skips if ``setStyleSheet`` is not available (e.g. during
    headless unit testing with a stub QApplication).
    """
    if qapp is None:
        return
    try:
        qapp.setStyleSheet(build_qt_stylesheet())
    except Exception:
        pass

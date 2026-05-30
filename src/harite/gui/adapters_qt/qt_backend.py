"""Qt runtime backend for Harite GUI (Phase 1: empty window skeleton)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from harite.gui.views.main_window import MainWindow

_WINDOW_TITLE = "Harite"
_WINDOW_WIDTH = 900
_WINDOW_HEIGHT = 640


class QtSignalBackend:
    """Thin wrapper around QApplication + QMainWindow.

    Responsibilities (Phase 1):
    - Hold the QApplication instance.
    - Build and own the top-level QMainWindow.
    - Apply window title, icon, and initial size.

    Signal wiring (Phase 3+) will be added to connect_signals().
    """

    def __init__(self, qapp: Any, qwindow: Any) -> None:
        self._qapp = qapp
        self._qwindow = qwindow

    @property
    def qapp(self) -> Any:
        return self._qapp

    @property
    def qwindow(self) -> Any:
        return self._qwindow

    def connect_signals(self, dispatch: dict[str, Any]) -> None:
        """Bind handler names to QWidget signals.  Implemented in Phase 3+."""

    def present(self) -> None:
        """Show the window and start the Qt event loop."""
        self._qwindow.show()
        self._qapp.exec()


def _make_window_icon(qwindow: Any) -> None:
    """Set harite_app.svg as the window icon if PyQt6.QtSvg is available."""
    try:
        from PyQt6.QtGui import QIcon
        from PyQt6.QtSvgWidgets import QSvgWidget  # noqa: F401 – presence check

        from harite.gui.resource_access import gui_resource_path

        with gui_resource_path("icons", "product", "harite_app.svg") as icon_path:
            qwindow.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        pass


def load_qt_runtime_signal_backend() -> QtSignalBackend:
    """Create QApplication + QMainWindow and return a QtSignalBackend.

    Raises RuntimeError if PyQt6 is not installed.
    """
    try:
        import sys

        from PyQt6.QtWidgets import QApplication, QMainWindow
    except ImportError as exc:
        raise RuntimeError(
            "Harite Qt backend requires PyQt6. "
            "Install it with: pip install 'harite[gui-qt]'"
        ) from exc

    qapp = QApplication.instance() or QApplication(sys.argv)
    qwindow = QMainWindow()
    qwindow.setWindowTitle(_WINDOW_TITLE)
    qwindow.resize(_WINDOW_WIDTH, _WINDOW_HEIGHT)
    _make_window_icon(qwindow)

    return QtSignalBackend(qapp, qwindow)

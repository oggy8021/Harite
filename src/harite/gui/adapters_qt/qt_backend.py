"""Qt runtime backend for Harite GUI (Phase 7: tray integrated)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from harite.gui.views.main_window import MainWindow

_WINDOW_TITLE = "Harite"
_WINDOW_WIDTH = 900
_WINDOW_HEIGHT = 640


class QtSignalBackend:
    """Qt runtime backend wrapping QApplication + QMainWindow.

    Responsibilities (Phases 2–7):
    - Hold the QApplication instance and QMainWindow.
    - Build the 3-layer layout (header / center body / footer) via
      qt_layout_builders, and keep a widget registry for signal wiring.
    - Build all dialogs (Settings / Color / About + file proxies) and
      register them in the same widget registry.
    - Optionally install a QSystemTrayIcon (Phase 7).
    - Apply window title, icon, and initial size.

    Signal wiring (Phase 8) will be added to connect_signals().
    """

    def __init__(self, qapp: Any, qwindow: Any) -> None:
        self._qapp = qapp
        self._qwindow = qwindow
        self._objects: dict[str, Any] = {"main_window": qwindow}
        self._tray_adapter: Any | None = None

    @property
    def qapp(self) -> Any:
        return self._qapp

    @property
    def qwindow(self) -> Any:
        return self._qwindow

    @property
    def objects(self) -> dict[str, Any]:
        """Widget registry keyed by logical name (GTK adapter naming convention)."""
        return self._objects

    @property
    def tray_adapter(self) -> Any | None:
        """The active QtTaskTrayAdapter, or None if tray is unavailable."""
        return self._tray_adapter

    def build_layout(self) -> None:
        """Populate QMainWindow with the 3-layer layout skeleton and dialogs."""
        from harite.gui.adapters_qt.qt_dialogs import build_dialogs
        from harite.gui.adapters_qt.qt_layout_builders import build_main_layout

        self._objects = build_main_layout(self._qwindow)
        self._objects.update(build_dialogs(self._qwindow))
        self._objects["main_window"] = self._qwindow

    def install_tray(self) -> bool:
        """Install QSystemTrayIcon if the system tray is available.

        Returns True when the tray was successfully installed, False when the
        system tray is unavailable (e.g. headless CI / Wayland without support).
        Does not raise on unavailability.
        """
        from harite.gui.adapters_qt.qt_tray_adapter import initialize_qt_tasktray

        adapter = initialize_qt_tasktray(self)
        self._tray_adapter = adapter
        return adapter is not None

    def connect_signals(self, dispatch: dict[str, Any]) -> None:
        """Bind handler names to QWidget signals.  Implemented in Phase 8."""

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
    """Create QApplication + QMainWindow, build layout, and return a QtSignalBackend.

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

    backend = QtSignalBackend(qapp, qwindow)
    backend.build_layout()
    return backend

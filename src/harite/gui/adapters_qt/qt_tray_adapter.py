"""Qt System Tray adapter for Harite GUI (Phase 7).

Replaces the GTK AppIndicator3 / AyatanaAppIndicator3 tray with a
cross-platform ``QSystemTrayIcon`` + ``QMenu``.

Menu structure (matches GTK adapter):
    Visible / Invisible  (toggle, updates with window state)
    Start Slideshow      (enabled when can_start_slideshow)
    Stop Slideshow       (enabled when slideshow_running)
    ─────────────────
    Settings
    BaseColor
    About
    ─────────────────
    Quit

``initialize_qt_tasktray`` is the public entry point, mirroring
``tasktray_adapter.initialize_tasktray``.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def initialize_qt_tasktray(signal_backend: Any) -> "QtTaskTrayAdapter | None":
    """Create and install the Qt system tray adapter.

    Returns ``None`` if the system tray is unavailable (e.g. headless CI).
    Raises ``RuntimeError`` if PyQt6 is not installed.
    """
    try:
        from PyQt6.QtWidgets import QSystemTrayIcon
    except ImportError as exc:
        raise RuntimeError(
            "Qt tray requires PyQt6. Install it with: pip install 'harite[gui-qt]'"
        ) from exc

    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None

    window = _resolve_main_window(signal_backend)

    adapter = QtTaskTrayAdapter(signal_backend=signal_backend, window=window)
    adapter.install()
    return adapter


def _resolve_main_window(signal_backend: Any) -> Any | None:
    # Try the objects registry first
    objects = getattr(signal_backend, "objects", None) or getattr(signal_backend, "_objects", None)
    if isinstance(objects, dict):
        for key in ("main_window", "qwindow"):
            w = objects.get(key)
            if w is not None:
                return w
    # Fallback: direct attribute
    for attr in ("qwindow", "_qwindow"):
        w = getattr(signal_backend, attr, None)
        if w is not None:
            return w
    return None


# ---------------------------------------------------------------------------
# Adapter class
# ---------------------------------------------------------------------------


class QtTaskTrayAdapter:
    """Qt implementation of the system tray adapter.

    Qt system-tray adapter for slideshow controls.
    """

    def __init__(
        self,
        *,
        signal_backend: Any,
        window: Any | None,
    ) -> None:
        self._signal_backend = signal_backend
        self._window = window
        self._tray: Any | None = None
        self._menu: Any | None = None

        # QAction references for state updates in refresh()
        self._action_visible: Any | None = None
        self._action_start: Any | None = None
        self._action_stop: Any | None = None

        # Poll timer (1-second interval, mirrors GLib.timeout_add_seconds)
        self._timer: Any | None = None

    # ------------------------------------------------------------------
    # Installation
    # ------------------------------------------------------------------

    def install(self) -> None:
        """Create QSystemTrayIcon, attach the menu, start the poll timer."""
        from PyQt6.QtWidgets import QApplication, QSystemTrayIcon

        qapp = QApplication.instance()

        icon = self._make_icon(slideshow_running=False)
        tray = QSystemTrayIcon(icon, qapp)
        tray.setToolTip("Harite")

        menu = self._build_menu()
        tray.setContextMenu(menu)

        tray.activated.connect(self._on_tray_activated)
        tray.show()

        self._tray = tray
        self._menu = menu

        # Connect window show/hide to refresh
        if self._window is not None:
            try:
                self._window.showEvent  # noqa: B018 – presence check
                # QMainWindow doesn't have a simple "show" signal, so we
                # hook the tray's activated signal and refresh periodically.
            except AttributeError:
                pass

        self._start_poll_timer()
        self.refresh()

    def _start_poll_timer(self) -> None:
        from PyQt6.QtCore import QTimer

        timer = QTimer()
        timer.setInterval(1000)
        timer.timeout.connect(self.refresh)
        timer.start()
        self._timer = timer

    # ------------------------------------------------------------------
    # Menu construction
    # ------------------------------------------------------------------

    def _build_menu(self) -> Any:
        from PyQt6.QtGui import QAction
        from PyQt6.QtWidgets import QMenu

        menu = QMenu()
        self._menu = menu  # keep alive before any possible GC

        action_visible = QAction("Visible", menu)
        action_visible.triggered.connect(self._on_toggle_visibility)
        menu.addAction(action_visible)
        self._action_visible = action_visible

        action_start = QAction("Start Slideshow", menu)
        action_start.triggered.connect(self._on_slideshow_start)
        menu.addAction(action_start)
        self._action_start = action_start

        action_stop = QAction("Stop Slideshow", menu)
        action_stop.triggered.connect(self._on_slideshow_stop)
        menu.addAction(action_stop)
        self._action_stop = action_stop

        menu.addSeparator()

        action_settings = QAction("Settings", menu)
        action_settings.triggered.connect(self._on_open_settings)
        menu.addAction(action_settings)

        action_color = QAction("BaseColor", menu)
        action_color.triggered.connect(self._on_open_color)
        menu.addAction(action_color)

        action_about = QAction("About", menu)
        action_about.triggered.connect(self._on_open_about)
        menu.addAction(action_about)

        menu.addSeparator()

        action_quit = QAction("Quit", menu)
        action_quit.triggered.connect(self._on_quit)
        menu.addAction(action_quit)

        return menu

    # ------------------------------------------------------------------
    # State polling and refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Update menu item states and tray icon based on current backend state."""
        slideshow_running = self._slideshow_running()
        can_start = self._can_start_slideshow()
        visible = self._window_visible()

        if self._action_visible is not None:
            self._action_visible.setText("Invisible" if visible else "Visible")

        if self._action_start is not None:
            self._action_start.setEnabled(can_start)

        if self._action_stop is not None:
            self._action_stop.setEnabled(slideshow_running)

        if self._tray is not None:
            icon = self._make_icon(slideshow_running=slideshow_running)
            self._tray.setIcon(icon)

    # ------------------------------------------------------------------
    # State readers
    # ------------------------------------------------------------------

    def _connected_owner(self) -> Any | None:
        getter = getattr(self._signal_backend, "_get_connected_owner", None)
        if callable(getter):
            return getter()
        return None

    def _slideshow_running(self) -> bool:
        owner = self._connected_owner()
        if owner is not None:
            return bool(getattr(owner, "slideshow_running", False))
        return bool(getattr(self._signal_backend, "_slideshow_running", False))

    def _can_start_slideshow(self) -> bool:
        owner = self._connected_owner()
        if owner is not None:
            return bool(getattr(owner, "can_start_slideshow", False))
        return not self._slideshow_running()

    def _window_visible(self) -> bool:
        if self._window is None:
            return False
        if hasattr(self._window, "isVisible"):
            return bool(self._window.isVisible())
        return True

    # ------------------------------------------------------------------
    # Icon helpers
    # ------------------------------------------------------------------

    def _make_icon(self, *, slideshow_running: bool) -> Any:
        from PyQt6.QtGui import QIcon

        resource_name = "harite.svg" if slideshow_running else "harite_off.svg"
        try:
            from harite.gui.resource_access import gui_resource_path

            with gui_resource_path("icons", "product", resource_name) as p:
                if p.exists():
                    return QIcon(str(p))
        except Exception:
            pass

        # Fallback to a built-in theme icon
        fallback = "media-playback-start" if slideshow_running else "media-playback-pause"
        icon = QIcon.fromTheme(fallback)
        if icon.isNull():
            icon = QIcon()
        return icon

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _present_main_window(self) -> None:
        if self._window is None:
            return
        if hasattr(self._window, "show"):
            self._window.show()
        if hasattr(self._window, "raise_"):
            self._window.raise_()
        if hasattr(self._window, "activateWindow"):
            self._window.activateWindow()

    def _invoke_backend(self, method_name: str, *, present_main_window: bool = False) -> None:
        callback = getattr(self._signal_backend, method_name, None)
        if not callable(callback):
            return
        if present_main_window:
            self._present_main_window()
        callback()
        self.refresh()

    def _on_tray_activated(self, reason: Any) -> None:
        """Double-click or trigger on the tray icon toggles window visibility."""
        try:
            from PyQt6.QtWidgets import QSystemTrayIcon

            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                self._on_toggle_visibility()
        except Exception:
            pass

    def _on_toggle_visibility(self, *_args: Any) -> None:
        if self._window_visible():
            if self._window is not None and hasattr(self._window, "hide"):
                self._window.hide()
        else:
            self._present_main_window()
        self.refresh()

    def _on_slideshow_start(self, *_args: Any) -> None:
        self._invoke_backend("_on_slideshow_start_clicked")

    def _on_slideshow_stop(self, *_args: Any) -> None:
        self._invoke_backend("_on_slideshow_stop_clicked")

    def _on_open_settings(self, *_args: Any) -> None:
        self._invoke_backend("_on_settings_clicked", present_main_window=True)

    def _on_open_color(self, *_args: Any) -> None:
        self._invoke_backend("_on_color_clicked", present_main_window=True)

    def _on_open_about(self, *_args: Any) -> None:
        self._invoke_backend("_on_about_clicked", present_main_window=True)

    def _on_quit(self, *_args: Any) -> None:
        try:
            from PyQt6.QtWidgets import QApplication

            qapp = QApplication.instance()
            if qapp is not None:
                qapp.quit()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def uninstall(self) -> None:
        """Stop the poll timer and hide the tray icon."""
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        if self._tray is not None:
            self._tray.hide()

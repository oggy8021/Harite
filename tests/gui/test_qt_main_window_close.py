"""Tests for Qt main window close-to-hide behavior (gui-spec §7)."""

from __future__ import annotations

from types import SimpleNamespace


def test_load_qt_runtime_disables_quit_on_last_window_closed(qapp) -> None:
    from harite.gui.adapters_qt import qt_backend

    qapp.setQuitOnLastWindowClosed(True)
    backend = qt_backend.load_qt_runtime_signal_backend()
    assert qapp.quitOnLastWindowClosed() is False
    assert backend.qwindow is not None


def test_handle_main_window_close_event_hides_without_accepting(qapp) -> None:
    from PyQt6.QtGui import QCloseEvent

    from harite.gui.adapters_qt.qt_backend import HariteQtMainWindow, QtSignalBackend

    qapp.setQuitOnLastWindowClosed(False)
    qwindow = HariteQtMainWindow.create()
    backend = QtSignalBackend(qapp, qwindow)
    qwindow._harite_backend = backend  # type: ignore[attr-defined]
    qwindow.show()
    assert qwindow.isVisible()

    event = QCloseEvent()
    backend.handle_main_window_close_event(event)

    assert event.isAccepted() is False
    assert qwindow.isVisible() is False


def test_handle_main_window_close_event_refreshes_tray(qapp) -> None:
    from PyQt6.QtGui import QCloseEvent

    from harite.gui.adapters_qt.qt_backend import HariteQtMainWindow, QtSignalBackend

    qwindow = HariteQtMainWindow.create()
    backend = QtSignalBackend(qapp, qwindow)
    refreshed: list[int] = []
    backend._tray_adapter = SimpleNamespace(refresh=lambda: refreshed.append(1))

    backend.handle_main_window_close_event(QCloseEvent())

    assert refreshed == [1]


def test_close_event_on_subclass_delegates_to_backend(qapp) -> None:
    from PyQt6.QtGui import QCloseEvent

    from harite.gui.adapters_qt.qt_backend import HariteQtMainWindow, QtSignalBackend

    qwindow = HariteQtMainWindow.create()
    backend = QtSignalBackend(qapp, qwindow)
    qwindow._harite_backend = backend  # type: ignore[attr-defined]
    qwindow.show()

    event = QCloseEvent()
    qwindow.closeEvent(event)

    assert event.isAccepted() is False
    assert qwindow.isVisible() is False

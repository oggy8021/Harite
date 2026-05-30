"""Tests for the Qt backend entrypoint (harite-qt / app_qt.py).

PyQt6 is required for the Qt-specific tests.  Tests that need a live
QApplication are decorated with pytest.importorskip so they are skipped
gracefully in environments without PyQt6.
"""

from __future__ import annotations

import pytest

from harite.gui import app_qt


# ---------------------------------------------------------------------------
# Importability and structure
# ---------------------------------------------------------------------------


def test_app_qt_module_importable():
    assert callable(app_qt.run)
    assert callable(app_qt.main)


def test_run_falls_back_to_show_when_qt_missing(monkeypatch):
    called = {"show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    monkeypatch.setattr(app_qt, "MainWindow", DummyWindow)
    monkeypatch.setattr(
        app_qt,
        "_load_qt_signal_backend",
        lambda: (_ for _ in ()).throw(RuntimeError("no PyQt6")),
    )

    app_qt.run(present_ui_window=False)

    assert called["show"] == 1


def test_run_exits_with_message_when_qt_missing_and_present_requested(monkeypatch):
    class DummyWindow:
        def show(self) -> None:
            raise AssertionError("show should not be called")

    monkeypatch.setattr(app_qt, "MainWindow", DummyWindow)
    monkeypatch.setattr(
        app_qt,
        "_load_qt_signal_backend",
        lambda: (_ for _ in ()).throw(RuntimeError("no PyQt6")),
    )

    with pytest.raises(SystemExit, match="Harite Qt backend is unavailable"):
        app_qt.run(present_ui_window=True)


def test_run_calls_present_when_backend_available(monkeypatch):
    called = {"present": 0, "show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class DummyBackend:
        def connect_signals(self, dispatch) -> None:
            pass

        def present(self) -> None:
            called["present"] += 1

    monkeypatch.setattr(app_qt, "MainWindow", DummyWindow)
    monkeypatch.setattr(app_qt, "_load_qt_signal_backend", lambda: DummyBackend())

    app_qt.run(present_ui_window=True)

    assert called["present"] == 1
    assert called["show"] == 0


def test_run_skips_present_when_disabled(monkeypatch):
    called = {"present": 0, "show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class DummyBackend:
        def connect_signals(self, dispatch) -> None:
            pass

        def present(self) -> None:
            called["present"] += 1

    monkeypatch.setattr(app_qt, "MainWindow", DummyWindow)
    monkeypatch.setattr(app_qt, "_load_qt_signal_backend", lambda: DummyBackend())

    app_qt.run(present_ui_window=False)

    assert called["present"] == 0
    assert called["show"] == 1


def test_main_parses_no_flags(monkeypatch):
    called = {}

    def fake_run(*, present_ui_window=None):
        called["present_ui_window"] = present_ui_window

    monkeypatch.setattr(app_qt, "run", fake_run)
    exit_code = app_qt.main([])

    assert exit_code == 0
    assert called == {"present_ui_window": None}


def test_main_parses_no_present_flag(monkeypatch):
    called = {}

    def fake_run(*, present_ui_window=None):
        called["present_ui_window"] = present_ui_window

    monkeypatch.setattr(app_qt, "run", fake_run)
    exit_code = app_qt.main(["--no-present-ui-window"])

    assert exit_code == 0
    assert called == {"present_ui_window": False}


# ---------------------------------------------------------------------------
# Qt-specific tests (require PyQt6)
# ---------------------------------------------------------------------------


def test_load_qt_signal_backend_returns_backend(qapp):
    """load_qt_runtime_signal_backend() returns a QtSignalBackend instance."""
    from harite.gui.adapters_qt.qt_backend import (
        QtSignalBackend,
        load_qt_runtime_signal_backend,
    )

    backend = load_qt_runtime_signal_backend()
    assert isinstance(backend, QtSignalBackend)
    assert backend.qapp is not None
    assert backend.qwindow is not None


def test_qt_window_title(qapp):
    """QMainWindow title is 'Harite'."""
    from harite.gui.adapters_qt.qt_backend import (
        _WINDOW_TITLE,
        load_qt_runtime_signal_backend,
    )

    backend = load_qt_runtime_signal_backend()
    assert backend.qwindow.windowTitle() == _WINDOW_TITLE


def test_qt_window_initial_size(qapp):
    """QMainWindow initial size matches spec (900×640)."""
    from harite.gui.adapters_qt.qt_backend import (
        _WINDOW_HEIGHT,
        _WINDOW_WIDTH,
        load_qt_runtime_signal_backend,
    )

    backend = load_qt_runtime_signal_backend()
    assert backend.qwindow.width() == _WINDOW_WIDTH
    assert backend.qwindow.height() == _WINDOW_HEIGHT

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


def test_console_script_entrypoints_use_main():
    from importlib.metadata import entry_points

    scripts = entry_points(group="console_scripts")
    for name in ("harite-qt", "harite-gui"):
        matches = [ep for ep in scripts if ep.name == name]
        assert len(matches) == 1
        ep = matches[0]
        assert ep.value == "harite.gui.app_qt:main"


def test_windows_entry_qt_source_calls_main():
    from pathlib import Path

    text = (
        Path(__file__).resolve().parents[2]
        / "packaging"
        / "windows"
        / "entry_qt.py"
    ).read_text(encoding="utf-8")
    assert "from harite.gui.app_qt import main" in text
    assert "SystemExit(main())" in text


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


def test_run_calls_show_main_window_and_event_loop_when_backend_available(monkeypatch):
    called = {"show_main_window": 0, "run_event_loop": 0, "install_tray": 0}

    class DummyWindow:
        def show(self) -> None:
            raise AssertionError("legacy show() should not be called")

    class DummyBackend:
        def connect_signals(self, dispatch) -> None:
            pass

        def install_tray(self) -> bool:
            called["install_tray"] += 1
            return False

        def show_main_window(self) -> None:
            called["show_main_window"] += 1

        def run_event_loop(self) -> None:
            called["run_event_loop"] += 1

    monkeypatch.setattr(app_qt, "MainWindow", DummyWindow)
    monkeypatch.setattr(app_qt, "_load_qt_signal_backend", lambda: DummyBackend())

    app_qt.run(present_ui_window=True)

    assert called["install_tray"] == 1
    assert called["show_main_window"] == 1
    assert called["run_event_loop"] == 1


def test_run_skips_show_main_window_but_still_runs_event_loop(monkeypatch):
    called = {"show_main_window": 0, "run_event_loop": 0, "install_tray": 0}

    class DummyWindow:
        def show(self) -> None:
            raise AssertionError("legacy show() should not be called")

    class DummyBackend:
        def connect_signals(self, dispatch) -> None:
            pass

        def install_tray(self) -> bool:
            called["install_tray"] += 1
            return False

        def show_main_window(self) -> None:
            called["show_main_window"] += 1

        def run_event_loop(self) -> None:
            called["run_event_loop"] += 1

    monkeypatch.setattr(app_qt, "MainWindow", DummyWindow)
    monkeypatch.setattr(app_qt, "_load_qt_signal_backend", lambda: DummyBackend())

    app_qt.run(present_ui_window=False)

    assert called["install_tray"] == 1
    assert called["show_main_window"] == 0
    assert called["run_event_loop"] == 1


def test_run_attaches_tasktray_adapter_when_installed(monkeypatch):
    class DummyTray:
        pass

    class DummyWindow:
        def show(self) -> None:
            pass

    class DummyBackend:
        _tray = DummyTray()

        def connect_signals(self, dispatch) -> None:
            pass

        @property
        def tray_adapter(self):
            return self._tray

        def install_tray(self) -> bool:
            return True

        def show_main_window(self) -> None:
            pass

        def run_event_loop(self) -> None:
            pass

    window = DummyWindow()
    backend = DummyBackend()
    monkeypatch.setattr(app_qt, "MainWindow", lambda: window)
    monkeypatch.setattr(app_qt, "_load_qt_signal_backend", lambda: backend)

    app_qt.run(present_ui_window=False)

    assert getattr(window, "_tasktray_adapter", None) is backend._tray
    assert getattr(backend, "_tasktray_adapter", None) is backend._tray


def test_main_parses_no_flags(monkeypatch):
    called = {}

    def fake_run(*, present_ui_window=None, startup_launch=None):
        called["present_ui_window"] = present_ui_window
        called["startup_launch"] = startup_launch

    monkeypatch.setattr(app_qt, "run", fake_run)
    exit_code = app_qt.main([])

    assert exit_code == 0
    assert called == {"present_ui_window": None, "startup_launch": None}


def test_main_parses_no_present_flag(monkeypatch):
    called = {}

    def fake_run(*, present_ui_window=None, startup_launch=None):
        called["present_ui_window"] = present_ui_window
        called["startup_launch"] = startup_launch

    monkeypatch.setattr(app_qt, "run", fake_run)
    exit_code = app_qt.main(["--no-present-ui-window"])

    assert exit_code == 0
    assert called == {"present_ui_window": False, "startup_launch": None}


def test_main_parses_startup_launch_flag(monkeypatch):
    called = {}

    def fake_run(*, present_ui_window=None, startup_launch=None):
        called["present_ui_window"] = present_ui_window
        called["startup_launch"] = startup_launch

    monkeypatch.setattr(app_qt, "run", fake_run)
    exit_code = app_qt.main(["--no-present-ui-window", "--startup-launch"])

    assert exit_code == 0
    assert called == {"present_ui_window": False, "startup_launch": True}


def test_schedule_startup_slideshow_invokes_start_when_eligible(monkeypatch):
    called = {"start": 0}

    class DummyWindow:
        pass

    class DummyBackend:
        def _on_slideshow_start_clicked(self) -> None:
            called["start"] += 1

    monkeypatch.setattr(
        "harite.gui.startup_slideshow.should_auto_start_from_owner",
        lambda owner, is_startup_launch: True,
    )

    class DummyTimer:
        @staticmethod
        def singleShot(_delay: int, callback) -> None:
            callback()

    import sys
    from types import SimpleNamespace

    monkeypatch.setitem(sys.modules, "PyQt6.QtCore", SimpleNamespace(QTimer=DummyTimer))

    app_qt._schedule_startup_slideshow_if_needed(
        DummyWindow(),
        DummyBackend(),
        startup_launch=True,
    )

    assert called["start"] == 1


def test_schedule_startup_slideshow_skips_when_not_eligible(monkeypatch):
    called = {"start": 0}

    class DummyBackend:
        def _on_slideshow_start_clicked(self) -> None:
            called["start"] += 1

    monkeypatch.setattr(
        "harite.gui.startup_slideshow.should_auto_start_from_owner",
        lambda owner, is_startup_launch: False,
    )

    app_qt._schedule_startup_slideshow_if_needed(
        object(),
        DummyBackend(),
        startup_launch=True,
    )

    assert called["start"] == 0


def test_schedule_startup_slideshow_skips_without_startup_launch_flag():
    called = {"start": 0}

    class DummyBackend:
        def _on_slideshow_start_clicked(self) -> None:
            called["start"] += 1

    app_qt._schedule_startup_slideshow_if_needed(
        object(),
        DummyBackend(),
        startup_launch=False,
    )

    assert called["start"] == 0


def test_register_application_quit_persistence_connects_about_to_quit():
    called = {"quit": 0}

    class DummyWindow:
        def on_prepare_application_quit(self) -> None:
            called["quit"] += 1

    handlers: list = []

    class DummySignal:
        def connect(self, handler) -> None:
            handlers.append(handler)

    class DummyQApp:
        aboutToQuit = DummySignal()

    class DummyBackend:
        qapp = DummyQApp()

    app_qt._register_application_quit_persistence(DummyWindow(), DummyBackend())

    assert len(handlers) == 1
    handlers[0]()
    assert called["quit"] == 1


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

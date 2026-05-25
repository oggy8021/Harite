import pytest

from harite.gui import app
from types import SimpleNamespace


def test_run_constructs_main_window_and_calls_show(monkeypatch):
    called = {"show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    monkeypatch.setattr(app, "MainWindow", DummyWindow)

    app.run(bind_ui_backend=False, present_ui_window=False)

    assert called["show"] == 1


def test_app_module_importable_without_gui_backend():
    # This verifies the entrypoint module is importable in headless CI environments.
    assert callable(app.run)


def test_run_binds_signal_backend_when_enabled(monkeypatch):
    called = {"show": 0, "connect_signals": 0}
    backend = None

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

        def on_change_input_text(self, _text: str) -> None:
            return None

        def on_optimize(self) -> bool:
            return True

        def on_apply(self) -> bool:
            return True

    class DummyBackend:
        def connect_signals(self, mapping):
            called["connect_signals"] += 1
            self.mapping = dict(mapping)

    def fake_backend_loader():
        nonlocal backend
        backend = DummyBackend()
        return backend

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)

    app.run(bind_ui_backend=True)

    assert called["connect_signals"] == 1
    assert called["show"] == 1
    assert backend is not None
    assert set(backend.mapping.keys()) >= {"on_change_input_text", "on_optimize", "on_apply"}
    assert "on_btnOptimize_clicked" not in backend.mapping
    assert "on_btnSetWall_clicked" not in backend.mapping


def test_run_uses_no_option_defaults_for_runtime_gui(monkeypatch):
    called = {"present": 0, "show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

        def on_change_input_text(self, _text: str) -> None:
            return None

        def on_optimize(self) -> bool:
            return True

        def on_apply(self) -> bool:
            return True

    class DummyBackend:
        def __init__(self):
            self.mapping = {}

        def connect_signals(self, mapping):
            self.mapping.update(mapping)

    def fake_backend_loader():
        return DummyBackend()

    def fake_present(_signal_backend):
        called["present"] += 1
        return True

    monkeypatch.delenv("HARITE_GUI_BIND_SIGNALS", raising=False)
    monkeypatch.delenv("HARITE_GUI_PRESENT_WINDOW", raising=False)
    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    app.run()

    assert called["present"] == 1
    assert called["show"] == 0


def test_run_env_override_can_disable_default_runtime_gui(monkeypatch):
    called = {"show": 0, "backend": 0, "present": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    def fake_backend_loader():
        called["backend"] += 1
        raise AssertionError("backend loader should not be called")

    def fake_present(_signal_backend):
        called["present"] += 1
        raise AssertionError("present should not be called")

    monkeypatch.setenv("HARITE_GUI_BIND_SIGNALS", "0")
    monkeypatch.setenv("HARITE_GUI_PRESENT_WINDOW", "0")
    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    app.run()

    assert called == {"show": 1, "backend": 0, "present": 0}


def test_run_continues_when_signal_backend_load_fails(monkeypatch):
    called = {"show": 0, "signal_backend": "unset"}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    def fake_backend_loader():
        raise RuntimeError("backend missing")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)

    app.run(bind_ui_backend=True, present_ui_window=False)

    assert called["show"] == 1


def test_run_exits_with_message_when_gui_runtime_is_missing(monkeypatch):
    class DummyWindow:
        def show(self) -> None:
            raise AssertionError("show should not be used when GUI runtime is required")

    def fake_backend_loader():
        raise RuntimeError("backend missing")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)

    with pytest.raises(SystemExit, match="Harite GUI runtime is unavailable"):
        app.run(bind_ui_backend=True, present_ui_window=True)


def test_run_propagates_unexpected_signal_backend_load_error(monkeypatch):
    class DummyWindow:
        def show(self) -> None:
            return None

    def fake_backend_loader():
        raise ValueError("unexpected backend load error")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)

    with pytest.raises(ValueError, match="unexpected backend load error"):
        app.run(bind_ui_backend=True)


def test_run_presents_real_window_when_enabled(monkeypatch):
    called = {"show": 0, "present": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class DummyBackend:
        def connect_signals(self, mapping):
            self.mapping = dict(mapping)

    def fake_backend_loader():
        return DummyBackend()

    def fake_present(_signal_backend):
        called["present"] += 1
        return True

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    app.run(bind_ui_backend=True, present_ui_window=True)

    assert called["present"] == 1
    assert called["show"] == 0


def test_run_falls_back_when_window_presentation_fails(monkeypatch):
    called = {"show": 0, "present": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class DummyBackend:
        def connect_signals(self, mapping):
            self.mapping = dict(mapping)

    def fake_backend_loader():
        return DummyBackend()

    def fake_present(_signal_backend):
        called["present"] += 1
        raise RuntimeError("no display")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    with pytest.raises(SystemExit, match="Harite GUI runtime is unavailable"):
        app.run(bind_ui_backend=True, present_ui_window=True)

    assert called["present"] == 1
    assert called["show"] == 0


def test_run_propagates_unexpected_window_presentation_error(monkeypatch):
    class DummyWindow:
        def show(self) -> None:
            return None

    class DummyBackend:
        def connect_signals(self, mapping):
            self.mapping = dict(mapping)

    def fake_backend_loader():
        return DummyBackend()

    def fake_present(_signal_backend):
        raise ValueError("unexpected present error")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    with pytest.raises(ValueError, match="unexpected present error"):
        app.run(bind_ui_backend=True, present_ui_window=True)


def test_run_can_present_without_prototype_load(monkeypatch):
    called = {"show": 0, "present": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class DummyBackend:
        def connect_signals(self, mapping):
            self.mapping = dict(mapping)

    def fake_backend_loader():
        return DummyBackend()

    def fake_present(_signal_backend):
        called["present"] += 1
        return True

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    app.run(bind_ui_backend=True, present_ui_window=True)

    assert called["present"] == 1
    assert called["show"] == 0


def test_run_runtime_fallback_dispatch_ready_path_is_quiet(monkeypatch, capsys):
    class DummyWindow:
        def show(self) -> None:
            return None

        # Provide minimum handlers so runtime fallback can build dispatch.
        def on_change_input_text(self, _text: str) -> None:
            return None

        def on_optimize(self) -> bool:
            return True

        def on_apply(self) -> bool:
            return True

    class DummyBackend:
        def __init__(self):
            self.mapping = {}

        def connect_signals(self, mapping):
            self.mapping.update(mapping)

    def fake_backend_loader():
        return DummyBackend()

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(app, "_initialize_tasktray", lambda _signal_backend: None)

    app.run(bind_ui_backend=True, present_ui_window=False)

    out = capsys.readouterr().out
    assert out == ""


def test_run_continues_when_signal_dispatch_binding_is_unsupported(monkeypatch):
    called = {"show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", lambda: object())
    monkeypatch.setattr(app, "_initialize_tasktray", lambda _signal_backend: None)

    app.run(bind_ui_backend=True, present_ui_window=False)

    assert called["show"] == 1


def test_run_propagates_unexpected_signal_dispatch_binding_error(monkeypatch):
    class DummyWindow:
        def show(self) -> None:
            return None

        def on_change_input_text(self, _text: str) -> None:
            return None

        def on_optimize(self) -> bool:
            return True

        def on_apply(self) -> bool:
            return True

    class DummyBackend:
        def connect_signals(self, _mapping):
            return None

    def fake_backend_loader():
        return DummyBackend()

    def fake_connect_signal_dispatch(_signal_backend, _dispatch):
        raise ValueError("unexpected dispatch binding error")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr("harite.gui.adapters.ui_adapter.connect_signal_dispatch", fake_connect_signal_dispatch)

    with pytest.raises(ValueError, match="unexpected dispatch binding error"):
        app.run(bind_ui_backend=True, present_ui_window=False)


def test_run_propagates_unexpected_tasktray_error(monkeypatch):
    class DummyWindow:
        def show(self) -> None:
            return None

        def on_change_input_text(self, _text: str) -> None:
            return None

        def on_optimize(self) -> bool:
            return True

        def on_apply(self) -> bool:
            return True

    class DummyBackend:
        def __init__(self):
            self.mapping = {}

        def connect_signals(self, mapping):
            self.mapping.update(mapping)

    def fake_backend_loader():
        return DummyBackend()

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(
        app,
        "_initialize_tasktray",
        lambda _signal_backend: (_ for _ in ()).throw(ValueError("unexpected tasktray error")),
    )

    with pytest.raises(ValueError, match="unexpected tasktray error"):
        app.run(bind_ui_backend=True, present_ui_window=False)


def test_present_ui_window_uses_env_window_id(monkeypatch):
    captured = {}

    def fake_present(signal_backend, *, window_id="main_window"):
        captured["backend"] = signal_backend
        captured["window_id"] = window_id
        return True

    monkeypatch.setenv("HARITE_GUI_WINDOW_ID", "Custom_Main_Window")
    monkeypatch.setattr("harite.gui.adapters.gtk_backend.present_gtk_window", fake_present)

    result = app._present_ui_window(SimpleNamespace(name="dummy"))
    assert result is True
    assert captured["window_id"] == "Custom_Main_Window"


def test_main_parses_cli_flags_and_calls_run(monkeypatch):
    called = {}

    def fake_run(*, bind_ui_backend=None, present_ui_window=None):
        called["bind_ui_backend"] = bind_ui_backend
        called["present_ui_window"] = present_ui_window

    monkeypatch.setattr(app, "run", fake_run)

    exit_code = app.main([
        "--bind-ui-backend",
        "--present-ui-window",
    ])

    assert exit_code == 0
    assert called == {
        "bind_ui_backend": True,
        "present_ui_window": True,
    }


def test_main_uses_none_defaults_without_cli_flags(monkeypatch):
    called = {}

    def fake_run(*, bind_ui_backend=None, present_ui_window=None):
        called["bind_ui_backend"] = bind_ui_backend
        called["present_ui_window"] = present_ui_window

    monkeypatch.setattr(app, "run", fake_run)

    exit_code = app.main([])

    assert exit_code == 0
    assert called == {
        "bind_ui_backend": None,
        "present_ui_window": None,
    }


def test_main_can_disable_runtime_gui_defaults(monkeypatch):
    called = {}

    def fake_run(*, bind_ui_backend=None, present_ui_window=None):
        called["bind_ui_backend"] = bind_ui_backend
        called["present_ui_window"] = present_ui_window

    monkeypatch.setattr(app, "run", fake_run)

    exit_code = app.main([
        "--no-bind-ui-backend",
        "--no-present-ui-window",
    ])

    assert exit_code == 0
    assert called == {
        "bind_ui_backend": False,
        "present_ui_window": False,
    }

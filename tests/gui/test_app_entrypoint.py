from harite.gui import app
from types import SimpleNamespace


def test_run_constructs_main_window_and_calls_show(monkeypatch):
    called = {"show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    monkeypatch.setattr(app, "MainWindow", DummyWindow)

    app.run()

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


def test_run_continues_when_signal_backend_load_fails(monkeypatch):
    called = {"show": 0, "signal_backend": "unset"}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    def fake_backend_loader():
        raise RuntimeError("backend missing")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)

    app.run(bind_ui_backend=True)

    assert called["show"] == 1


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

    app.run(bind_ui_backend=True, present_ui_window=True)

    assert called["present"] == 1
    assert called["show"] == 1


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


def test_run_runtime_fallback_dispatch_ready_log(monkeypatch, capsys):
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

    app.run(bind_ui_backend=True, present_ui_window=False)

    out = capsys.readouterr().out
    assert "UI runtime fallback dispatch ready" in out


def test_present_ui_window_uses_env_window_id(monkeypatch):
    captured = {}

    def fake_present(signal_backend, *, window_id="WallPosit_MainWindow"):
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

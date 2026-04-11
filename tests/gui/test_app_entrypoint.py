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


def test_run_loads_ui_prototype_when_enabled(monkeypatch):
    called = {"loader": 0, "show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    def fake_loader():
        called["loader"] += 1

        class Result:
            widget_count = 1
            signal_count = 2

        return Result()

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr("harite.gui.adapters.ui_loader.load_glade_prototype", fake_loader)

    app.run(load_ui_prototype=True)

    assert called["loader"] == 1
    assert called["show"] == 1


def test_run_continues_when_ui_loader_fails(monkeypatch):
    called = {"show": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    def boom_loader():
        raise RuntimeError("broken ui")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr("harite.gui.adapters.ui_loader.load_glade_prototype", boom_loader)

    app.run(load_ui_prototype=True)

    assert called["show"] == 1


def test_run_binds_signal_backend_when_enabled(monkeypatch):
    called = {"show": 0, "signal_backend": None}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class Result:
        file_path = "dummy.glade"
        widget_count = 1
        signal_count = 1

    class DummyBackend:
        def connect_signals(self, mapping):
            self.mapping = dict(mapping)

    def fake_loader():
        return Result()

    def fake_backend_loader(_ui_file):
        return DummyBackend()

    def fake_bind(mainwindow, ui_result, signal_backend=None):
        called["signal_backend"] = signal_backend

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr("harite.gui.adapters.ui_loader.load_glade_prototype", fake_loader)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr("harite.gui.adapters.ui_adapter.bind_mainwindow", fake_bind)

    app.run(load_ui_prototype=True, bind_ui_backend=True)

    assert called["show"] == 1
    assert called["signal_backend"] is not None


def test_run_continues_when_signal_backend_load_fails(monkeypatch):
    called = {"show": 0, "signal_backend": "unset"}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class Result:
        file_path = "dummy.glade"
        widget_count = 1
        signal_count = 1

    def fake_loader():
        return Result()

    def fake_backend_loader(_ui_file):
        raise RuntimeError("backend missing")

    def fake_bind(mainwindow, ui_result, signal_backend=None):
        called["signal_backend"] = signal_backend

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr("harite.gui.adapters.ui_loader.load_glade_prototype", fake_loader)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr("harite.gui.adapters.ui_adapter.bind_mainwindow", fake_bind)

    app.run(load_ui_prototype=True, bind_ui_backend=True)

    assert called["show"] == 1
    assert called["signal_backend"] is None


def test_run_presents_real_window_when_enabled(monkeypatch):
    called = {"show": 0, "present": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class Result:
        file_path = "dummy.glade"
        widget_count = 1
        signal_count = 1

    class DummyBackend:
        pass

    def fake_loader():
        return Result()

    def fake_backend_loader(_ui_file):
        return DummyBackend()

    def fake_bind(mainwindow, ui_result, signal_backend=None):
        return None

    def fake_present(_signal_backend):
        called["present"] += 1
        return True

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr("harite.gui.adapters.ui_loader.load_glade_prototype", fake_loader)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr("harite.gui.adapters.ui_adapter.bind_mainwindow", fake_bind)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    app.run(load_ui_prototype=True, bind_ui_backend=True, present_ui_window=True)

    assert called["present"] == 1
    assert called["show"] == 0


def test_run_falls_back_when_window_presentation_fails(monkeypatch):
    called = {"show": 0, "present": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class Result:
        file_path = "dummy.glade"
        widget_count = 1
        signal_count = 1

    class DummyBackend:
        pass

    def fake_loader():
        return Result()

    def fake_backend_loader(_ui_file):
        return DummyBackend()

    def fake_bind(mainwindow, ui_result, signal_backend=None):
        return None

    def fake_present(_signal_backend):
        called["present"] += 1
        raise RuntimeError("no display")

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr("harite.gui.adapters.ui_loader.load_glade_prototype", fake_loader)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr("harite.gui.adapters.ui_adapter.bind_mainwindow", fake_bind)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    app.run(load_ui_prototype=True, bind_ui_backend=True, present_ui_window=True)

    assert called["present"] == 1
    assert called["show"] == 1


def test_run_can_present_without_glade_load(monkeypatch):
    called = {"show": 0, "present": 0}

    class DummyWindow:
        def show(self) -> None:
            called["show"] += 1

    class DummyBackend:
        pass

    def boom_loader():
        raise RuntimeError("legacy glade parse failed")

    def fake_backend_loader(_ui_file):
        return DummyBackend()

    def fake_present(_signal_backend):
        called["present"] += 1
        return True

    monkeypatch.setattr(app, "MainWindow", DummyWindow)
    monkeypatch.setattr("harite.gui.adapters.ui_loader.load_glade_prototype", boom_loader)
    monkeypatch.setattr(app, "_load_ui_signal_backend", fake_backend_loader)
    monkeypatch.setattr(app, "_present_ui_window", fake_present)

    app.run(load_ui_prototype=True, bind_ui_backend=True, present_ui_window=True)

    assert called["present"] == 1
    assert called["show"] == 0


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

    def fake_run(*, load_ui_prototype=None, bind_ui_backend=None, present_ui_window=None):
        called["load_ui_prototype"] = load_ui_prototype
        called["bind_ui_backend"] = bind_ui_backend
        called["present_ui_window"] = present_ui_window

    monkeypatch.setattr(app, "run", fake_run)

    exit_code = app.main([
        "--load-ui-prototype",
        "--bind-ui-backend",
        "--present-ui-window",
    ])

    assert exit_code == 0
    assert called == {
        "load_ui_prototype": True,
        "bind_ui_backend": True,
        "present_ui_window": True,
    }


def test_main_uses_none_defaults_without_cli_flags(monkeypatch):
    called = {}

    def fake_run(*, load_ui_prototype=None, bind_ui_backend=None, present_ui_window=None):
        called["load_ui_prototype"] = load_ui_prototype
        called["bind_ui_backend"] = bind_ui_backend
        called["present_ui_window"] = present_ui_window

    monkeypatch.setattr(app, "run", fake_run)

    exit_code = app.main([])

    assert exit_code == 0
    assert called == {
        "load_ui_prototype": None,
        "bind_ui_backend": None,
        "present_ui_window": None,
    }

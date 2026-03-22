from harite.gui import app


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

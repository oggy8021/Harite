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

import pytest

from harite.gui.adapters.gtk_backend import _resolve_window
from harite.gui.adapters.ui_adapter import RUNTIME_HANDLER_MAP, connect_signal_dispatch, create_mainwindow_signal_dispatch


class DummyWindow:
    def on_change_input_text(self, text: str) -> None:
        self.last_input = text

    def on_save_as(self) -> bool:
        self.save_as_called = True
        return True

    def on_open_settings_dialog(self) -> bool:
        self.settings_opened = True
        return True

    def on_get_settings_config(self) -> dict[str, object]:
        return {"plugin": "linux", "apply_mode": "single-file"}

    def on_apply_settings(self, config: dict[str, object]) -> bool:
        self.applied_settings = dict(config)
        return True

    def on_load_settings_file(self, path: str) -> bool:
        self.loaded_settings_path = path
        return True

    def on_save_settings_file(self, path: str, config: dict[str, object] | None = None) -> bool:
        self.saved_settings = (path, config)
        return True

    def on_optimize(self) -> bool:
        self.optimize_called = True
        return True

    def on_apply(self) -> bool:
        self.apply_called = True
        return True


class BackendWithConnectSignals:
    def __init__(self) -> None:
        self.received = None

    def connect_signals(self, mapping):
        self.received = dict(mapping)


class BackendWithConnect:
    def __init__(self) -> None:
        self.calls = []

    def connect(self, name, callback):
        self.calls.append((name, callback))


def test_connect_signal_dispatch_uses_connect_signals_strategy():
    backend = BackendWithConnectSignals()
    dispatch = {
        "on_change_input_text": lambda _text: None,
        "on_save_as": lambda: True,
    }

    info = connect_signal_dispatch(backend, dispatch)

    assert info["strategy"] == "connect_signals"
    assert info["connected_count"] == 2
    assert set(backend.received.keys()) == set(dispatch.keys())


def test_connect_signal_dispatch_uses_connect_strategy():
    backend = BackendWithConnect()
    dispatch = {
        "on_change_input_text": lambda _text: None,
        "on_save_as": lambda: True,
    }

    info = connect_signal_dispatch(backend, dispatch)

    assert info["strategy"] == "connect"
    assert info["connected_count"] == 2
    assert {name for name, _ in backend.calls} == set(dispatch.keys())


def test_connect_signal_dispatch_raises_for_unsupported_backend():
    with pytest.raises(TypeError, match="signal backend must provide"):
        connect_signal_dispatch(object(), {"on_save_as": lambda: True})


def test_create_mainwindow_signal_dispatch_binds_current_runtime_handlers():
    window = DummyWindow()

    dispatch = create_mainwindow_signal_dispatch(
        window,
        ("on_change_input_text", "on_save_as", "on_optimize", "on_apply"),
        handler_map=RUNTIME_HANDLER_MAP,
    )

    assert set(dispatch.keys()) == {"on_change_input_text", "on_save_as", "on_optimize", "on_apply"}

    dispatch["on_change_input_text"]("/tmp/input.jpg")
    assert window.last_input == "/tmp/input.jpg"
    assert dispatch["on_save_as"]() is True
    assert window.save_as_called is True
    assert dispatch["on_optimize"]() is True
    assert window.optimize_called is True
    assert dispatch["on_apply"]() is True
    assert window.apply_called is True


def test_create_mainwindow_signal_dispatch_skips_unimplemented_runtime_methods():
    class PartialWindow:
        def on_change_input_text(self, text: str) -> None:
            self.last_input = text

    dispatch = create_mainwindow_signal_dispatch(
        PartialWindow(),
        ("on_change_input_text", "on_save_as", "on_optimize", "on_missing"),
        handler_map=RUNTIME_HANDLER_MAP,
    )

    assert set(dispatch.keys()) == {"on_change_input_text"}


def test_create_mainwindow_signal_dispatch_binds_canonical_traceability_handlers():
    window = DummyWindow()

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_save_as",
            "on_open_settings_dialog",
            "on_get_settings_config",
            "on_apply_settings",
            "on_load_settings_file",
            "on_save_settings_file",
        ),
        handler_map=RUNTIME_HANDLER_MAP,
    )

    assert set(dispatch.keys()) == {
        "on_save_as",
        "on_open_settings_dialog",
        "on_get_settings_config",
        "on_apply_settings",
        "on_load_settings_file",
        "on_save_settings_file",
    }

    assert dispatch["on_save_as"]() is True
    assert window.save_as_called is True
    assert dispatch["on_open_settings_dialog"]() is True
    assert window.settings_opened is True
    assert dispatch["on_get_settings_config"]() == {"plugin": "linux", "apply_mode": "single-file"}
    assert dispatch["on_apply_settings"]({"plugin": "xfce"}) is True
    assert window.applied_settings == {"plugin": "xfce"}
    assert dispatch["on_load_settings_file"]("/tmp/settings.json") is True
    assert window.loaded_settings_path == "/tmp/settings.json"
    assert dispatch["on_save_settings_file"]("/tmp/settings.json", {"plugin": "xfce"}) is True
    assert window.saved_settings == ("/tmp/settings.json", {"plugin": "xfce"})


def test_create_mainwindow_signal_dispatch_skips_legacy_save_alias_handler():
    window = DummyWindow()

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_save",
            "on_get_preferences_config",
            "on_apply_preferences",
            "on_load_preferences_file",
            "on_save_preferences_file",
        ),
        handler_map=RUNTIME_HANDLER_MAP,
    )

    assert dispatch == {}


def test_create_mainwindow_signal_dispatch_skips_legacy_settings_alias_handlers():
    window = DummyWindow()

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_get_preferences_config",
            "on_apply_preferences",
            "on_load_preferences_file",
            "on_save_preferences_file",
        ),
        handler_map=RUNTIME_HANDLER_MAP,
    )

    assert dispatch == {}


def test_resolve_window_uses_canonical_ids_before_top_level_fallback():
    class Backend:
        def __init__(self):
            self._window = object()

        def get_object(self, name):
            if name == "main_window":
                return self._window
            return None

        def get_objects(self):
            return []

    backend = Backend()

    assert _resolve_window(backend, "WallPosit_MainWindow") is backend._window


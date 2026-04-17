import pytest

from harite.gui.adapters.ui_adapter import RUNTIME_HANDLER_MAP, connect_signal_dispatch, create_mainwindow_signal_dispatch


class DummyWindow:
    def on_change_input_text(self, text: str) -> None:
        self.last_input = text

    def on_save(self) -> bool:
        self.optimized = True
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
        "on_save": lambda: True,
    }

    info = connect_signal_dispatch(backend, dispatch)

    assert info["strategy"] == "connect_signals"
    assert info["connected_count"] == 2
    assert set(backend.received.keys()) == set(dispatch.keys())


def test_connect_signal_dispatch_uses_connect_strategy():
    backend = BackendWithConnect()
    dispatch = {
        "on_change_input_text": lambda _text: None,
        "on_save": lambda: True,
    }

    info = connect_signal_dispatch(backend, dispatch)

    assert info["strategy"] == "connect"
    assert info["connected_count"] == 2
    assert {name for name, _ in backend.calls} == set(dispatch.keys())


def test_connect_signal_dispatch_raises_for_unsupported_backend():
    with pytest.raises(TypeError, match="signal backend must provide"):
        connect_signal_dispatch(object(), {"on_save": lambda: True})


def test_create_mainwindow_signal_dispatch_binds_current_runtime_handlers():
    window = DummyWindow()

    dispatch = create_mainwindow_signal_dispatch(
        window,
        ("on_change_input_text", "on_save", "on_optimize", "on_apply"),
        handler_map=RUNTIME_HANDLER_MAP,
    )

    assert set(dispatch.keys()) == {"on_change_input_text", "on_save", "on_optimize", "on_apply"}

    dispatch["on_change_input_text"]("/tmp/input.jpg")
    assert window.last_input == "/tmp/input.jpg"
    assert dispatch["on_save"]() is True
    assert window.optimized is True
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
        ("on_change_input_text", "on_save", "on_optimize", "on_missing"),
        handler_map=RUNTIME_HANDLER_MAP,
    )

    assert set(dispatch.keys()) == {"on_change_input_text"}


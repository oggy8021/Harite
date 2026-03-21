from pathlib import Path

import pytest

from harite.gui.adapters.ui_adapter import bind_mainwindow, connect_signal_dispatch
from harite.gui.adapters.ui_loader import UiLoadResult


class DummyWindow:
    def on_change_input_text(self, text: str) -> None:
        self.last_input = text

    def on_optimize(self) -> bool:
        self.optimized = True
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
        "on_entPath_insert_text": lambda _text: None,
        "on_btnSave_clicked": lambda: True,
    }

    info = connect_signal_dispatch(backend, dispatch)

    assert info["strategy"] == "connect_signals"
    assert info["connected_count"] == 2
    assert set(backend.received.keys()) == set(dispatch.keys())


def test_connect_signal_dispatch_uses_connect_strategy():
    backend = BackendWithConnect()
    dispatch = {
        "on_entPath_insert_text": lambda _text: None,
        "on_btnSave_clicked": lambda: True,
    }

    info = connect_signal_dispatch(backend, dispatch)

    assert info["strategy"] == "connect"
    assert info["connected_count"] == 2
    assert {name for name, _ in backend.calls} == set(dispatch.keys())


def test_connect_signal_dispatch_raises_for_unsupported_backend():
    with pytest.raises(TypeError, match="signal backend must provide"):
        connect_signal_dispatch(object(), {"on_btnSave_clicked": lambda: True})


def test_bind_mainwindow_records_signal_connection_metadata():
    win = DummyWindow()
    backend = BackendWithConnectSignals()
    result = UiLoadResult(
        file_path=Path("/tmp/fake.glade"),
        root_tag="interface",
        widget_count=3,
        signal_count=2,
        signal_handlers=(
            "on_entPath_insert_text",
            "on_btnSave_clicked",
        ),
    )

    bind_mainwindow(win, result, signal_backend=backend)

    assert "signal_connection" in win._adapter_bindings
    conn = win._adapter_bindings["signal_connection"]
    assert conn["strategy"] == "connect_signals"
    assert conn["connected_count"] == 2

from pathlib import Path

from harite.gui.adapters.ui_adapter import bind_mainwindow, create_mainwindow_signal_dispatch
from harite.gui.adapters.ui_loader import UiLoadResult


class DummyWindow:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def on_change_input_text(self, text: str) -> None:
        self.calls.append(("input", text))

    def on_optimize(self) -> bool:
        self.calls.append(("optimize", True))
        return True

    def on_apply_dry_run(self) -> bool:
        self.calls.append(("apply_dry", True))
        return True


def test_create_mainwindow_signal_dispatch_maps_input_optimize_apply_handlers():
    win = DummyWindow()
    handlers = (
        "on_entPath_insert_text",
        "on_btnSave_clicked",
        "on_btnSetWall_clicked",
    )

    dispatch = create_mainwindow_signal_dispatch(win, handlers)

    assert set(dispatch.keys()) == set(handlers)
    dispatch["on_entPath_insert_text"]("a.jpg")
    assert dispatch["on_btnSave_clicked"]() is True
    assert dispatch["on_btnSetWall_clicked"]() is True
    assert win.calls == [
        ("input", "a.jpg"),
        ("optimize", True),
        ("apply_dry", True),
    ]


def test_bind_mainwindow_stores_dispatch_handlers_metadata_and_table():
    win = DummyWindow()
    result = UiLoadResult(
        file_path=Path("/tmp/fake.glade"),
        root_tag="interface",
        widget_count=3,
        signal_count=3,
        signal_handlers=(
            "on_entPath_insert_text",
            "on_btnSave_clicked",
            "on_btnSetWall_clicked",
        ),
    )

    bind_mainwindow(win, result)

    assert hasattr(win, "_adapter_bindings")
    assert hasattr(win, "_adapter_signal_dispatch")
    assert set(win._adapter_bindings["dispatch_handlers"]) == {
        "on_entPath_insert_text",
        "on_btnSave_clicked",
        "on_btnSetWall_clicked",
    }
    assert set(win._adapter_signal_dispatch.keys()) == {
        "on_entPath_insert_text",
        "on_btnSave_clicked",
        "on_btnSetWall_clicked",
    }

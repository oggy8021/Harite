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

    def on_change_margins(self, left: int, right: int, top: int, bottom: int) -> None:
        self.calls.append(("margins", (left, right, top, bottom)))

    def on_toggle_fixed(self, enabled: bool) -> None:
        self.calls.append(("fixed", enabled))


class _SpinValue:
    def __init__(self, value: int) -> None:
        self._value = value

    def get_value_as_int(self) -> int:
        return self._value


class _ToggleWidget:
    def __init__(self, active: bool) -> None:
        self._active = active

    def get_active(self) -> bool:
        return self._active


class _BackendWithGetObject:
    def __init__(self) -> None:
        self.widgets = {
            "spnLMergin": _SpinValue(10),
            "spnRMergin": _SpinValue(20),
            "spnTopMergin": _SpinValue(30),
            "spnBtmMergin": _SpinValue(40),
        }

    def get_object(self, name: str):
        return self.widgets.get(name)


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


def test_dispatch_handles_gtk_style_signal_arguments():
    win = DummyWindow()
    handlers = (
        "on_entPath_insert_text",
        "on_btnSave_clicked",
        "on_btnSetWall_clicked",
    )

    dispatch = create_mainwindow_signal_dispatch(win, handlers)

    # GTK style: (editable, new_text, new_text_length, position)
    dispatch["on_entPath_insert_text"](object(), "gtk.jpg", 7, None)
    # GTK clicked style often passes widget instance
    assert dispatch["on_btnSave_clicked"](object()) is True
    assert dispatch["on_btnSetWall_clicked"](object()) is True

    assert win.calls == [
        ("input", "gtk.jpg"),
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


def test_dispatch_handles_margins_and_fixed_toggle_signals():
    win = DummyWindow()
    backend = _BackendWithGetObject()
    handlers = (
        "on_spnMergin_value_changed",
        "on_radFixed_toggled",
    )

    dispatch = create_mainwindow_signal_dispatch(win, handlers, signal_backend=backend)

    dispatch["on_spnMergin_value_changed"](object())
    dispatch["on_radFixed_toggled"](_ToggleWidget(True))

    assert win.calls == [
        ("margins", (10, 20, 30, 40)),
        ("fixed", True),
    ]

from pathlib import Path

from harite.gui.adapters.ui_adapter import bind_mainwindow, create_mainwindow_signal_dispatch
from harite.gui.adapters.ui_loader import UiLoadResult


class DummyWindow:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def on_change_input_text(self, text: str) -> None:
        self.calls.append(("input", text))

    def on_save(self) -> bool:
        self.calls.append(("save", True))
        return True

    def on_apply_dry_run(self) -> bool:
        self.calls.append(("apply_dry", True))
        return True

    def on_change_margins(self, left: int, right: int, top: int, bottom: int) -> None:
        self.calls.append(("margins", (left, right, top, bottom)))

    def on_toggle_fixed(self, enabled: bool) -> None:
        self.calls.append(("fixed", enabled))

    def on_watch_start(self) -> bool:
        self.calls.append(("watch_start", True))
        return False

    def on_watch_stop(self) -> bool:
        self.calls.append(("watch_stop", True))
        return False

    def on_watch_interval_change(self, seconds: int) -> bool:
        self.calls.append(("watch_interval", seconds))
        return True

    def on_clear_input(self) -> bool:
        self.calls.append(("clear_input", True))
        return True

    def on_about(self) -> bool:
        self.calls.append(("about", True))
        return False

    def on_set_color(self) -> bool:
        self.calls.append(("set_color", True))
        return False

    def on_save_dialog_cancel(self) -> bool:
        self.calls.append(("save_dialog_cancel", True))
        return True

    def on_save_dialog_confirm(self, path: str | None = None) -> bool:
        self.calls.append(("save_dialog_confirm", path or True))
        return True


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


class _SaveDialogWidget:
    def __init__(self, path: str) -> None:
        self._path = path

    def get_filename(self) -> str:
        return self._path


class _BackendWithSaveDialog:
    def __init__(self, path: str) -> None:
        self.widgets = {
            "SaveWallpaperDialog": _SaveDialogWidget(path),
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
        ("save", True),
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
        ("save", True),
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


def test_dispatch_handles_watch_signals():
    win = DummyWindow()
    handlers = (
        "on_btnDaemonize_clicked",
        "on_btnCancelDaemonize_clicked",
        "on_spnInterval_value_changed",
    )

    dispatch = create_mainwindow_signal_dispatch(win, handlers)

    assert dispatch["on_btnDaemonize_clicked"](object()) is False
    assert dispatch["on_btnCancelDaemonize_clicked"](object()) is False
    assert dispatch["on_spnInterval_value_changed"](90) is True

    assert win.calls == [
        ("watch_start", True),
        ("watch_stop", True),
        ("watch_interval", 90),
    ]


def test_dispatch_handles_about_clear_and_save_dialog_button_signals():
    win = DummyWindow()
    handlers = (
        "on_btnClrPath_clicked",
        "on_btnAbout_clicked",
        "on_btnSetColor_clicked",
        "on_btnCancelSave_clicked",
        "on_btnOpenSave_clicked",
    )

    dispatch = create_mainwindow_signal_dispatch(win, handlers)

    assert dispatch["on_btnClrPath_clicked"](object()) is True
    assert dispatch["on_btnAbout_clicked"](object()) is False
    assert dispatch["on_btnSetColor_clicked"](object()) is False
    assert dispatch["on_btnCancelSave_clicked"](object()) is True
    assert dispatch["on_btnOpenSave_clicked"](object()) is False
    assert dispatch["on_btnOpenSave_clicked"]("/tmp/out.jpg") is True

    assert win.calls == [
        ("clear_input", True),
        ("about", True),
        ("set_color", True),
        ("save_dialog_cancel", True),
        ("save_dialog_confirm", "/tmp/out.jpg"),
    ]


def test_dispatch_open_save_returns_false_when_no_path_is_resolved():
    win = DummyWindow()
    handlers = ("on_btnOpenSave_clicked",)
    dispatch = create_mainwindow_signal_dispatch(win, handlers)

    assert dispatch["on_btnOpenSave_clicked"](object()) is False
    assert win.calls == []


def test_dispatch_reads_save_path_from_backend_dialog_when_clicked_arg_has_no_path():
    win = DummyWindow()
    backend = _BackendWithSaveDialog("/tmp/from-dialog.jpg")
    handlers = ("on_btnOpenSave_clicked",)

    dispatch = create_mainwindow_signal_dispatch(win, handlers, signal_backend=backend)

    assert dispatch["on_btnOpenSave_clicked"](object()) is True
    assert win.calls == [("save_dialog_confirm", "/tmp/from-dialog.jpg")]

from pathlib import Path

from harite.gui.adapters.ui_adapter import bind_mainwindow, create_mainwindow_signal_dispatch
from harite.gui.adapters.ui_loader import UiLoadResult


class DummyWindow:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def on_change_input_text(self, text: str) -> None:
        self.calls.append(("input", text))

    def on_pick_input(self, path: str) -> None:
        self.calls.append(("input", path))

    def on_save(self) -> bool:
        self.calls.append(("save", True))
        return True

    def on_optimize(self) -> bool:
        self.calls.append(("optimize", True))
        return True

    def on_apply_dry_run(self) -> bool:
        self.calls.append(("apply_dry", True))
        return True

    def on_change_margins(self, *args) -> None:
        self.calls.append(("margins", args))

    def on_toggle_fixed(self, enabled: bool) -> None:
        self.calls.append(("fixed", enabled))

    def on_toggle_position_pressed(self, widget_name: str) -> None:
        self.calls.append(("toggle_pressed", widget_name))

    def on_toggle_position(self, widget_name: str, active: bool) -> None:
        self.calls.append(("toggle_toggled", (widget_name, active)))

    def on_toggle_position_reset(self, widget_name: str) -> None:
        self.calls.append(("toggle_reset", widget_name))

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
    def __init__(self, active: bool, name: str = "tglUpperL") -> None:
        self._active = active
        self._name = name

    def get_active(self) -> bool:
        return self._active

    def set_active(self, active: bool) -> None:
        self._active = active

    def get_name(self) -> str:
        return self._name


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


class _EntryWidget:
    def __init__(self, text: str) -> None:
        self._text = text

    def get_text(self) -> str:
        return self._text


class _BackendWithEntry:
    def __init__(self, text: str) -> None:
        self.widgets = {
            "entPathL": _EntryWidget(text),
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
        "on_btnOptimize_clicked",
    }
    assert set(win._adapter_signal_dispatch.keys()) == {
        "on_entPath_insert_text",
        "on_btnSave_clicked",
        "on_btnSetWall_clicked",
        "on_btnOptimize_clicked",
    }


def test_bind_mainwindow_adds_optimize_dispatch_when_mainwindow_supports_it():
    win = DummyWindow()
    result = UiLoadResult(
        file_path=Path("/tmp/fake.glade"),
        root_tag="interface",
        widget_count=1,
        signal_count=1,
        signal_handlers=("on_btnSave_clicked",),
    )

    bind_mainwindow(win, result)

    assert "on_btnOptimize_clicked" in win._adapter_signal_dispatch
    assert win._adapter_signal_dispatch["on_btnOptimize_clicked"]() is True
    assert ("optimize", True) in win.calls


def test_dispatch_handles_margins_and_fixed_toggle_signals():
    win = DummyWindow()
    backend = _BackendWithGetObject()
    handlers = (
        "on_spnMergin_value_changed",
        "on_radFixed_toggled",
    )

    dispatch = create_mainwindow_signal_dispatch(win, handlers, signal_backend=backend)

    margin_widget = backend.get_object("spnLMergin")
    setattr(margin_widget, "get_name", lambda: "spnLMergin")

    dispatch["on_spnMergin_value_changed"](margin_widget)
    dispatch["on_radFixed_toggled"](_ToggleWidget(True))

    assert win.calls == [
        ("margins", ("spnLMergin", 10)),
        ("fixed", True),
    ]


def test_dispatch_handles_toggle_pressed_toggled_and_released_signals():
    win = DummyWindow()
    backend = _BackendWithGetObject()
    backend.widgets["tglUpperL"] = _ToggleWidget(False, "tglUpperL")
    backend.widgets["tglLowerL"] = _ToggleWidget(True, "tglLowerL")
    handlers = (
        "on_tglBtn_pressed",
        "on_tglBtn_toggled",
        "on_tglBtn_released",
    )

    dispatch = create_mainwindow_signal_dispatch(win, handlers, signal_backend=backend)

    widget = backend.get_object("tglUpperL")
    dispatch["on_tglBtn_pressed"](widget)
    widget.set_active(True)
    dispatch["on_tglBtn_toggled"](widget)
    widget.set_active(False)
    dispatch["on_tglBtn_released"](widget)

    assert backend.get_object("tglLowerL").get_active() is False
    assert win.calls == [
        ("toggle_pressed", "tglUpperL"),
        ("toggle_toggled", ("tglUpperL", True)),
        ("toggle_reset", "tglUpperL"),
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


def test_dispatch_reads_pick_path_from_backend_entry_when_clicked_arg_has_no_path():
    win = DummyWindow()
    backend = _BackendWithEntry("/tmp/from-entry.jpg")
    handlers = ("on_btnGetImg_clicked",)

    dispatch = create_mainwindow_signal_dispatch(win, handlers, signal_backend=backend)

    assert dispatch["on_btnGetImg_clicked"](object()) is None
    assert win.calls == [("input", "/tmp/from-entry.jpg")]

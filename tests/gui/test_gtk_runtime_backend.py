from __future__ import annotations

from harite.gui.adapters.gtk_backend import GtkRuntimeSignalBackend


class _Orientation:
    VERTICAL = 1
    HORIZONTAL = 2


class _WidgetBase:
    def __init__(self):
        self._signals = {}
        self._name = ""

    def connect(self, name, callback):
        self._signals.setdefault(name, []).append(callback)

    def emit(self, name, *args):
        for cb in self._signals.get(name, []):
            cb(*args)

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name


class _Window(_WidgetBase):
    def __init__(self, title=""):
        super().__init__()
        self.title = title
        self.child = None

    def set_default_size(self, *_args):
        return None

    def set_resizable(self, _enabled):
        return None

    def add(self, child):
        self.child = child


class _Box(_WidgetBase):
    def __init__(self, **_kwargs):
        super().__init__()
        self.children = []

    def set_border_width(self, _width):
        return None

    def pack_start(self, child, *_args):
        self.children.append(child)


class _Label(_WidgetBase):
    def __init__(self, label=""):
        super().__init__()
        self.text = label

    def set_xalign(self, _value):
        return None

    def set_text(self, text):
        self.text = text


class _Entry(_WidgetBase):
    def __init__(self):
        super().__init__()
        self._text = ""

    def set_placeholder_text(self, _text):
        return None

    def set_text(self, text):
        self._text = text

    def get_text(self):
        return self._text


class _Button(_WidgetBase):
    def __init__(self, label=""):
        super().__init__()
        self.label = label
        self.sensitive = True

    def set_sensitive(self, enabled):
        self.sensitive = bool(enabled)

    def click(self):
        self.emit("clicked", self)


class _ToggleButton(_Button):
    def __init__(self, label=""):
        super().__init__(label=label)
        self._active = False

    def set_active(self, active):
        self._active = bool(active)

    def get_active(self):
        return self._active

    def click(self):
        self.emit("pressed", self)
        self._active = not self._active
        self.emit("toggled", self)
        self.emit("released", self)
        self.emit("clicked", self)


class _SpinButton(_WidgetBase):
    def __init__(self):
        super().__init__()
        self.numeric = False
        self._value = 0

    def set_numeric(self, enabled):
        self.numeric = bool(enabled)

    def set_value(self, value):
        self._value = int(value)

    def get_value(self):
        return self._value

    def get_value_as_int(self):
        return int(self._value)


class _RadioButton(_ToggleButton):
    @classmethod
    def new_with_label(cls, _group, label):
        return cls(label=label)

    @classmethod
    def new_with_label_from_widget(cls, _widget, label):
        return cls(label=label)


class _FakeGtk:
    Orientation = _Orientation
    Window = _Window
    Box = _Box
    Label = _Label
    Entry = _Entry
    Button = _Button
    ToggleButton = _ToggleButton
    SpinButton = _SpinButton
    RadioButton = _RadioButton


def test_runtime_backend_input_controls_optimize_button_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    optimize_btn = backend.get_object("btnSave")
    optimize_modern_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_entPath_insert_text": lambda _text: None})

    assert optimize_btn.sensitive is False
    assert optimize_modern_btn.sensitive is False
    assert apply_btn.sensitive is False

    entry.set_text("/tmp/example.jpg")
    entry.emit("changed", entry)

    assert optimize_btn.sensitive is True
    assert optimize_modern_btn.sensitive is True
    assert apply_btn.sensitive is False
    assert status.text == "Input: updated"
    assert error.text == "Error: none"


def test_runtime_backend_optimize_result_controls_apply_button_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    optimize_result = backend.get_object("lblOptimizeResult")
    apply_target = backend.get_object("lblApplyTarget")

    backend.connect_signals({"on_btnOptimize_clicked": lambda: True})
    optimize_btn.click()

    assert apply_btn.sensitive is True
    assert status.text == "Optimize: ok"
    assert error.text == "Error: none"
    assert optimize_result.text == "Optimize result: success"
    assert apply_target.text == "Apply target: ready"

    backend.connect_signals({"on_btnOptimize_clicked": lambda: False})
    optimize_btn.click()

    assert apply_btn.sensitive is False
    assert status.text == "Optimize: failed"
    assert error.text == "Error: optimize returned false"
    assert optimize_result.text == "Optimize result: failed"
    assert apply_target.text == "Apply target: not-ready"


def test_runtime_backend_exposes_main_optimize_apply_sections():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    assert backend.get_object("boxRoot") is not None
    assert backend.get_object("lblMainSection") is not None
    assert backend.get_object("boxMainSection") is not None
    assert backend.get_object("tglUpperL") is not None
    assert backend.get_object("tglUpperR") is not None
    assert backend.get_object("tglPushLeftL") is not None
    assert backend.get_object("tglPushRightL") is not None
    assert backend.get_object("tglLowerL") is not None
    assert backend.get_object("tglPushLeftR") is not None
    assert backend.get_object("tglPushRightR") is not None
    assert backend.get_object("tglLowerR") is not None
    assert backend.get_object("btnGetImgL") is not None
    assert backend.get_object("btnGetImgR") is not None
    assert backend.get_object("entPathL") is not None
    assert backend.get_object("entPathR") is not None
    assert backend.get_object("lblOptimizeSection") is not None
    assert backend.get_object("boxOptimizeSection") is not None
    assert backend.get_object("btnOptimize") is not None
    assert backend.get_object("lblOptimizeResult") is not None
    assert backend.get_object("lblApplySection") is not None
    assert backend.get_object("boxApplySection") is not None
    assert backend.get_object("lblApplyTarget") is not None
    assert backend.get_object("lblDoItPlanned") is not None
    assert backend.get_object("lblSaveDialogState") is not None
    assert backend.get_object("lblPriorityRule") is not None
    assert backend.get_object("lblStyleLegend") is not None
    assert backend.get_object("lblCurrentStateSection") is not None
    assert backend.get_object("lblCurrentFixed") is not None
    assert backend.get_object("lblCurrentMargins") is not None
    assert backend.get_object("lblCurrentStateL") is not None
    assert backend.get_object("lblCurrentStateR") is not None
    assert backend.get_object("lblCommandSection") is not None
    assert backend.get_object("lblFlowLegend") is not None
    assert backend.get_object("lblWatchSection") is not None
    assert backend.get_object("lblError") is not None


def test_runtime_backend_current_state_panel_defaults_are_visible():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    assert backend.get_object("lblCurrentStateSection").text == "Current state"
    assert backend.get_object("lblCurrentFixed").text == "Current fixed: off"
    assert backend.get_object("lblCurrentMargins").text == "Current margins: 0,0,0,0"
    assert backend.get_object("lblCurrentStateL").text == "Current L: align=center valign=center"
    assert backend.get_object("lblCurrentStateR").text == "Current R: align=center valign=center"


def test_runtime_backend_shows_p5_3_planned_and_priority_labels():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    do_it = backend.get_object("lblDoItPlanned")
    priority = backend.get_object("lblPriorityRule")
    watch_section = backend.get_object("lblWatchSection")
    interval = backend.get_object("lblInterval")
    color_btn = backend.get_object("btnSetColor")
    save_open = backend.get_object("btnOpenSave")
    save_cancel = backend.get_object("btnCancelSave")
    save_dialog = backend.get_object("SaveWallpaperDialog")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    watch_start = backend.get_object("btnDaemonize")
    watch_stop = backend.get_object("btnCancelDaemonize")
    pick_state = backend.get_object("lblPickState")
    style_legend = backend.get_object("lblStyleLegend")
    command_section = backend.get_object("lblCommandSection")
    flow_legend = backend.get_object("lblFlowLegend")
    prefs_btn = backend.get_object("btnSetting")
    about_btn = backend.get_object("btnAbout")
    help_btn = backend.get_object("btnHelp")
    save_btn = backend.get_object("btnSave")
    optimize_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    tgl_upper_l = backend.get_object("tglUpperL")
    tgl_upper_r = backend.get_object("tglUpperR")
    tgl_push_left_l = backend.get_object("tglPushLeftL")
    tgl_push_right_l = backend.get_object("tglPushRightL")
    tgl_lower_l = backend.get_object("tglLowerL")
    tgl_push_left_r = backend.get_object("tglPushLeftR")
    tgl_push_right_r = backend.get_object("tglPushRightR")
    tgl_lower_r = backend.get_object("tglLowerR")

    assert do_it.text == "do-it: planned"
    assert priority.text == "Rule: fixed > margin > toggles"
    assert watch_section.text == "Watch (planned)"
    assert interval.text == "Interval (planned)"
    assert color_btn.label == "Color (planned)"
    assert save_open.label == "Save Confirm"
    assert save_cancel.label == "Save Cancel"
    assert save_open.sensitive is False
    assert save_cancel.sensitive is False
    assert hasattr(save_dialog, "get_filename")
    assert hasattr(save_dialog, "set_filename")
    assert save_dialog_state.text == "SaveDialog: closed"
    assert watch_start.label == "Watch Start (planned)"
    assert watch_stop.label == "Watch Stop (planned)"
    assert pick_state.text == "Picker: idle"
    assert style_legend.text == "Style cues: secondary(about/help) | planned"
    assert command_section.text == "Commands"
    assert flow_legend.text == "Flow: Compose -> Optimize -> Apply"
    assert prefs_btn.label == "Prefs"
    assert about_btn.label == "About (secondary)"
    assert help_btn.label == "Help (secondary)"
    assert save_btn.label == "Save"
    assert optimize_btn.label == "Optimize"
    assert apply_btn.label == "Apply (dry-run)"
    assert tgl_upper_l.label == "Top-L"
    assert tgl_upper_r.label == "Top-R"
    assert tgl_push_left_l.label == "Left-L"
    assert tgl_push_right_l.label == "Right-L"
    assert tgl_lower_l.label == "Bottom-L"
    assert tgl_push_left_r.label == "Left-R"
    assert tgl_push_right_r.label == "Right-R"
    assert tgl_lower_r.label == "Bottom-R"


def test_runtime_backend_open_l_uses_entry_path_and_calls_pick_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    open_l = backend.get_object("btnGetImgL")
    pick_state = backend.get_object("lblPickState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"path": None}

    def on_pick(path):
        observed["path"] = path

    backend.connect_signals({"on_btnGetImg_clicked": on_pick})
    entry.set_text("/tmp/left.jpg")
    open_l.click()

    assert observed["path"] == "/tmp/left.jpg"
    assert pick_state.text == "Open-L: selected"
    assert status.text == "Open-L: selected"
    assert error.text == "Error: none"


def test_runtime_backend_open_r_without_entry_path_marks_planned():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    open_r = backend.get_object("btnGetImgR")
    pick_state = backend.get_object("lblPickState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    open_r.click()

    assert pick_state.text == "Open-R: planned(path-required)"
    assert status.text == "Open-R: planned"
    assert error.text == "Error: path input required"


def test_runtime_backend_open_r_uses_right_entry_path_and_calls_pick_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry_l = backend.get_object("entPathL")
    entry_r = backend.get_object("entPathR")
    open_r = backend.get_object("btnGetImgR")
    pick_state = backend.get_object("lblPickState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"path": None}

    def on_pick(path):
        observed["path"] = path

    backend.connect_signals({"on_btnGetImg_clicked": on_pick})
    entry_l.set_text("/tmp/left.jpg")
    entry_r.set_text("/tmp/right.jpg")
    open_r.click()

    assert observed["path"] == "/tmp/right.jpg"
    assert pick_state.text == "Open-R: selected"
    assert status.text == "Open-R: selected"
    assert error.text == "Error: none"


def test_runtime_backend_right_input_enables_optimize_buttons():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry_l = backend.get_object("entPathL")
    entry_r = backend.get_object("entPathR")
    optimize_btn = backend.get_object("btnSave")
    optimize_modern_btn = backend.get_object("btnOptimize")

    backend.connect_signals({"on_entPath_insert_text": lambda _text: None})

    entry_l.set_text("")
    entry_r.set_text("/tmp/right-only.jpg")
    entry_r.emit("changed", entry_r)

    assert optimize_btn.sensitive is True
    assert optimize_modern_btn.sensitive is True


def test_runtime_backend_color_click_sets_planned_status():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    color_btn = backend.get_object("btnSetColor")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    color_btn.click()

    assert status.text == "Color: planned"
    assert error.text == "Error: none"


def test_runtime_backend_save_dialog_confirm_passes_dialog_object_to_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_open = backend.get_object("btnOpenSave")
    save_dialog = backend.get_object("SaveWallpaperDialog")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {}

    save_dialog.set_filename("/tmp/from-runtime-dialog.jpg")

    def on_open_save(dialog):
        observed["filename"] = dialog.get_filename()
        return True

    backend.connect_signals({"on_btnOpenSave_clicked": on_open_save})
    backend.get_object("btnSave").click()
    save_dialog.set_filename("/tmp/from-runtime-dialog.jpg")
    assert save_open.sensitive is True
    assert backend.get_object("btnCancelSave").sensitive is True
    save_open.click()

    assert observed["filename"] == "/tmp/from-runtime-dialog.jpg"
    assert save_dialog.is_visible() is False
    assert save_open.sensitive is False
    assert backend.get_object("btnCancelSave").sensitive is False
    assert save_dialog_state.text == "SaveDialog: closed(confirm)"
    assert status.text == "SaveDialog: confirm-ok"
    assert error.text == "Error: none"


def test_runtime_backend_save_dialog_confirm_without_path_keeps_dialog_open():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_open = backend.get_object("btnOpenSave")
    save_dialog = backend.get_object("SaveWallpaperDialog")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    called = {"count": 0}

    def on_open_save(_dialog):
        called["count"] += 1
        return True

    backend.connect_signals({"on_btnOpenSave_clicked": on_open_save})
    backend.get_object("btnSave").click()
    assert save_open.sensitive is False
    assert backend.get_object("btnCancelSave").sensitive is True
    save_open.click()

    assert called["count"] == 0
    assert save_dialog.is_visible() is True
    assert save_open.sensitive is False
    assert backend.get_object("btnCancelSave").sensitive is True
    assert save_dialog_state.text == "SaveDialog: open(path-required)"
    assert status.text == "SaveDialog: confirm-pending-path"
    assert error.text == "Error: save path is required"


def test_runtime_backend_save_dialog_confirm_is_ignored_when_closed():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_open = backend.get_object("btnOpenSave")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    called = {"count": 0}

    def on_open_save(_dialog):
        called["count"] += 1
        return True

    backend.connect_signals({"on_btnOpenSave_clicked": on_open_save})
    save_open.click()

    assert called["count"] == 0
    assert save_dialog_state.text == "SaveDialog: closed"
    assert status.text == "SaveDialog: ignored-closed"
    assert error.text == "Error: none"


def test_runtime_backend_save_dialog_cancel_is_ignored_when_closed():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_cancel = backend.get_object("btnCancelSave")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    called = {"count": 0}

    def on_cancel_save():
        called["count"] += 1
        return True

    backend.connect_signals({"on_btnCancelSave_clicked": on_cancel_save})
    save_cancel.click()

    assert called["count"] == 0
    assert save_dialog_state.text == "SaveDialog: closed"
    assert status.text == "SaveDialog: ignored-closed"
    assert error.text == "Error: none"


def test_runtime_backend_save_dialog_cancel_calls_legacy_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_cancel = backend.get_object("btnCancelSave")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"called": False}

    def on_cancel_save():
        observed["called"] = True
        return True

    backend.connect_signals({"on_btnCancelSave_clicked": on_cancel_save})
    backend.get_object("btnSave").click()
    assert save_cancel.sensitive is True
    assert backend.get_object("btnOpenSave").sensitive is False
    save_cancel.click()

    assert observed["called"] is True
    assert backend.get_object("SaveWallpaperDialog").is_visible() is False
    assert save_cancel.sensitive is False
    assert backend.get_object("btnOpenSave").sensitive is False
    assert save_dialog_state.text == "SaveDialog: closed(cancel)"
    assert status.text == "SaveDialog: cancel-ok"
    assert error.text == "Error: none"


def test_runtime_backend_save_click_opens_save_dialog_proxy():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_btn = backend.get_object("btnSave")
    save_dialog = backend.get_object("SaveWallpaperDialog")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    status = backend.get_object("lblStatus")

    assert save_dialog.is_visible() is False
    assert backend.get_object("btnOpenSave").sensitive is False
    assert backend.get_object("btnCancelSave").sensitive is False
    save_btn.click()

    assert save_dialog.is_visible() is True
    assert backend.get_object("btnOpenSave").sensitive is False
    assert backend.get_object("btnCancelSave").sensitive is True
    assert save_dialog_state.text == "SaveDialog: open"
    assert status.text == "Status: ready"


def test_runtime_backend_save_dialog_filename_selection_enables_confirm():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_btn = backend.get_object("btnSave")
    save_dialog = backend.get_object("SaveWallpaperDialog")
    save_open = backend.get_object("btnOpenSave")
    save_dialog_state = backend.get_object("lblSaveDialogState")

    save_btn.click()
    assert save_open.sensitive is False

    save_dialog.set_filename("/tmp/selected.jpg")

    assert save_open.sensitive is True
    assert save_dialog_state.text == "SaveDialog: open(path-ready)"


def test_runtime_backend_input_clear_closes_save_dialog_and_disables_confirm_buttons():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    save_btn = backend.get_object("btnSave")
    save_dialog = backend.get_object("SaveWallpaperDialog")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    save_open = backend.get_object("btnOpenSave")
    save_cancel = backend.get_object("btnCancelSave")

    backend.connect_signals({"on_entPath_insert_text": lambda _text: None})

    entry.set_text("/tmp/example.jpg")
    entry.emit("changed", entry)
    save_btn.click()
    save_dialog.set_filename("/tmp/selected.jpg")
    assert save_dialog.is_visible() is True
    assert save_open.sensitive is True
    assert save_cancel.sensitive is True

    entry.set_text("")
    entry.emit("changed", entry)

    assert save_dialog.is_visible() is False
    assert save_open.sensitive is False
    assert save_cancel.sensitive is False
    assert save_dialog_state.text == "SaveDialog: closed(input-reset)"


def test_runtime_backend_apply_success_updates_apply_target():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    apply_target = backend.get_object("lblApplyTarget")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_btnOptimize_clicked": lambda: True})
    backend.connect_signals({"on_btnSetWall_clicked": lambda: True})

    optimize_btn.click()
    apply_btn.click()

    assert status.text == "Apply: dry-run-ok"
    assert error.text == "Error: none"
    assert apply_target.text == "Apply target: consumed"


def test_runtime_backend_optimize_sets_running_state_before_handler_call():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    status = backend.get_object("lblStatus")

    observed = {}

    def on_optimize_clicked():
        observed["status_when_called"] = status.text
        return True

    backend.connect_signals({"on_btnOptimize_clicked": on_optimize_clicked})
    optimize_btn.click()

    assert observed["status_when_called"] == "Optimize: running"


def test_runtime_backend_apply_failure_updates_error_message():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_btnSetWall_clicked": lambda: False})
    apply_btn.click()

    assert status.text == "Apply: dry-run-failed"
    assert error.text == "Error: apply returned false"


def test_runtime_backend_optimize_handler_missing_sets_status_and_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    optimize_result = backend.get_object("lblOptimizeResult")
    apply_target = backend.get_object("lblApplyTarget")

    optimize_btn.click()

    assert status.text == "Optimize: handler-missing"
    assert error.text == "Error: handler not connected"
    assert optimize_result.text == "Optimize result: handler-missing"
    assert apply_target.text == "Apply target: not-ready"


def test_runtime_backend_save_button_opens_dialog_without_optimize_handler_call():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_btn = backend.get_object("btnSave")
    save_dialog = backend.get_object("SaveWallpaperDialog")
    save_dialog_state = backend.get_object("lblSaveDialogState")
    status = backend.get_object("lblStatus")
    calls = []

    backend.connect_signals({
        "on_btnSave_clicked": lambda: calls.append("save") or True,
        "on_btnOptimize_clicked": lambda: calls.append("optimize") or False,
    })

    save_btn.click()

    assert calls == []
    assert save_dialog.is_visible() is True
    assert save_dialog_state.text == "SaveDialog: open"
    assert status.text == "Status: ready"


def test_runtime_backend_optimize_button_does_not_fallback_to_save_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    optimize_result = backend.get_object("lblOptimizeResult")
    apply_target = backend.get_object("lblApplyTarget")
    calls = []

    backend.connect_signals({
        "on_btnSave_clicked": lambda: calls.append("save") or True,
    })

    optimize_btn.click()

    assert calls == []
    assert status.text == "Optimize: handler-missing"
    assert error.text == "Error: handler not connected"
    assert optimize_result.text == "Optimize result: handler-missing"
    assert apply_target.text == "Apply target: not-ready"


def test_runtime_backend_apply_handler_missing_sets_status_and_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    apply_target = backend.get_object("lblApplyTarget")

    apply_btn.click()

    assert status.text == "Apply: handler-missing"
    assert error.text == "Error: handler not connected"
    assert apply_target.text == "Apply target: handler-missing"


def test_runtime_backend_toggle_exclusivity_for_left_vertical_direction():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    upper = backend.get_object("tglUpperL")
    lower = backend.get_object("tglLowerL")

    upper.click()
    assert upper.get_active() is True
    assert lower.get_active() is False

    lower.click()
    assert lower.get_active() is True
    assert upper.get_active() is False

    lower.click()
    assert lower.get_active() is False
    assert upper.get_active() is False


def test_runtime_backend_toggle_exclusivity_for_right_horizontal_direction():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    left = backend.get_object("tglPushLeftR")
    right = backend.get_object("tglPushRightR")

    left.click()
    assert left.get_active() is True
    assert right.get_active() is False

    right.click()
    assert right.get_active() is True
    assert left.get_active() is False

    right.click()
    assert right.get_active() is False
    assert left.get_active() is False


def test_runtime_backend_same_direction_on_other_side_remains_enabled():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    upper_l = backend.get_object("tglUpperL")
    upper_r = backend.get_object("tglUpperR")

    upper_l.click()

    assert upper_l.get_active() is True
    assert upper_r.sensitive is True

    upper_r.click()

    assert upper_r.get_active() is True
    assert upper_l.get_active() is True


def test_runtime_backend_toggle_callbacks_follow_upstream_order():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    calls = []

    backend.connect_signals(
        {
            "on_tglBtn_pressed": lambda widget: calls.append(("pressed", widget.get_name())),
            "on_tglBtn_toggled": lambda widget: calls.append(("toggled", widget.get_name(), widget.get_active())),
            "on_tglBtn_released": lambda widget: calls.append(("released", widget.get_name())),
        }
    )

    toggle = backend.get_object("tglUpperL")
    toggle.click()
    toggle.click()

    assert calls == [
        ("pressed", "tglUpperL"),
        ("toggled", "tglUpperL", True),
        ("released", "tglUpperL"),
        ("pressed", "tglUpperL"),
        ("toggled", "tglUpperL", False),
        ("released", "tglUpperL"),
    ]


def test_runtime_backend_margin_change_propagates_all_values():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("spnLMergin").set_value(11)
    backend.get_object("spnRMergin").set_value(22)
    backend.get_object("spnTopMergin").set_value(33)
    backend.get_object("spnBtmMergin").set_value(44)

    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    captured = {}

    def on_margins(widget):
        captured["name"] = widget.get_name()
        captured["value"] = widget.get_value_as_int()

    backend.connect_signals({"on_spnMergin_value_changed": on_margins})
    backend.get_object("spnLMergin").emit("value-changed", backend.get_object("spnLMergin"))

    assert captured == {"name": "spnLMergin", "value": 11}
    assert status.text == "Margins: updated"
    assert error.text == "Error: none"
    assert backend.get_object("lblCurrentMargins").text == "Current margins: 11,22,33,44"


def test_runtime_backend_current_state_panel_updates_for_toggle_and_fixed():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("tglPushRightL").click()
    backend.get_object("tglUpperR").click()
    backend.get_object("radFixed").click()

    assert backend.get_object("lblCurrentFixed").text == "Current fixed: on"
    assert backend.get_object("lblCurrentStateL").text == "Current L: align=right valign=center"
    assert backend.get_object("lblCurrentStateR").text == "Current R: align=center valign=top"

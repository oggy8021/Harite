from __future__ import annotations

from harite.gui.adapters.gtk_backend import GtkRuntimeSignalBackend
from harite.gui.adapters.ui_adapter import create_mainwindow_signal_dispatch
from harite.gui.views.main_window import MainWindow


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


class _Grid(_WidgetBase):
    def __init__(self, **_kwargs):
        super().__init__()
        self.children = []
        self.row_spacing = 0
        self.column_spacing = 0

    def set_row_spacing(self, spacing):
        self.row_spacing = int(spacing)

    def set_column_spacing(self, spacing):
        self.column_spacing = int(spacing)

    def attach(self, child, left, top, width, height):
        self.children.append((child, int(left), int(top), int(width), int(height)))


class _Notebook(_WidgetBase):
    def __init__(self):
        super().__init__()
        self.pages = []

    def append_page(self, child, tab_label):
        self.pages.append((child, tab_label))


class _Label(_WidgetBase):
    def __init__(self, label=""):
        super().__init__()
        self.text = label

    def set_xalign(self, _value):
        return None

    def set_text(self, text):
        self.text = text

    def get_text(self):
        return self.text


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
        self.minimum = None
        self.maximum = None
        self.step_increment = None
        self.page_increment = None

    def set_numeric(self, enabled):
        self.numeric = bool(enabled)

    def set_range(self, minimum, maximum):
        self.minimum = int(minimum)
        self.maximum = int(maximum)

    def set_increments(self, step, page):
        self.step_increment = int(step)
        self.page_increment = int(page)

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
    Grid = _Grid
    Notebook = _Notebook
    Label = _Label
    Entry = _Entry
    Button = _Button
    ToggleButton = _ToggleButton
    SpinButton = _SpinButton
    RadioButton = _RadioButton


class _NativeResponseType:
    CANCEL = 0
    OK = 1


class _NativeFileChooserAction:
    OPEN = 1
    SAVE = 2


class _NativeFileChooserDialog:
    next_response = _NativeResponseType.CANCEL
    next_filename = ""
    last_created = None

    def __init__(self, title="", parent=None, action=None):
        self.title = title
        self.parent = parent
        self.action = action
        self.filename = ""
        self.current_folder = ""
        self.current_name = ""
        self.overwrite_confirmation = False
        _NativeFileChooserDialog.last_created = self

    def add_buttons(self, *_args):
        return None

    def set_modal(self, _enabled):
        return None

    def set_transient_for(self, _parent):
        return None

    def set_destroy_with_parent(self, _enabled):
        return None

    def set_do_overwrite_confirmation(self, enabled):
        self.overwrite_confirmation = bool(enabled)

    def set_current_folder(self, folder):
        self.current_folder = str(folder)

    def set_current_name(self, name):
        self.current_name = str(name)

    def set_filename(self, filename):
        self.filename = str(filename)

    def show_all(self):
        return None

    def run(self):
        return self.next_response

    def get_filename(self):
        return self.filename or self.next_filename

    def destroy(self):
        return None


class _NativeFakeGtk(_FakeGtk):
    FileChooserDialog = _NativeFileChooserDialog
    FileChooserAction = _NativeFileChooserAction
    ResponseType = _NativeResponseType
    STOCK_CANCEL = "gtk-cancel"
    STOCK_SAVE = "gtk-save"


def test_runtime_backend_updates_mainwindow_form_state_for_toggles_and_margins():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    dispatch = create_mainwindow_signal_dispatch(window, tuple(backend._signal_handlers.keys()) if backend._signal_handlers else tuple())

    if not dispatch:
        dispatch = create_mainwindow_signal_dispatch(window, (
            "on_toggle_fixed",
            "on_toggle_position_pressed",
            "on_toggle_position",
            "on_toggle_position_reset",
            "on_change_margins",
        ))
    backend.connect_signals(dispatch)

    backend.get_object("tglPushRightL").click()
    backend.get_object("tglUpperR").click()
    backend.get_object("spnTopMergin").set_value(25)
    backend.get_object("spnTopMergin").emit("value-changed", backend.get_object("spnTopMergin"))

    assert window.form_state.align == "right"
    assert window.form_state.valign == "top"
    assert window.form_state.margins == "0,0,25,0"


def test_runtime_backend_input_controls_optimize_button_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    optimize_btn = backend.get_object("btnSave")
    optimize_modern_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_change_input_text": lambda _text: None})

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

    backend.connect_signals({"on_optimize": lambda: True})
    optimize_btn.click()

    assert apply_btn.sensitive is True
    assert status.text == "Optimize: ok"
    assert error.text == "Error: none"
    assert optimize_result.text == "Optimize result: success"
    assert apply_target.text == "Apply target: ready"

    backend.connect_signals({"on_optimize": lambda: False})
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
    assert backend.get_object("lblSavePathState") is not None
    assert backend.get_object("lblSaveTarget") is not None
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


def test_runtime_backend_shows_p5_3_planned_and_policy_labels():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    do_it = backend.get_object("lblDoItPlanned")
    priority = backend.get_object("lblPriorityRule")
    watch_section = backend.get_object("lblWatchSection")
    interval = backend.get_object("lblInterval")
    color_btn = backend.get_object("btnSetColor")
    save_path_chooser = backend.get_object("SavePathDialog")
    save_path_state = backend.get_object("lblSavePathState")
    watch_start = backend.get_object("btnDaemonize")
    watch_stop = backend.get_object("btnCancelDaemonize")
    pick_state = backend.get_object("lblPickState")
    style_legend = backend.get_object("lblStyleLegend")
    command_section = backend.get_object("lblCommandSection")
    flow_legend = backend.get_object("lblFlowLegend")
    watch_sources = backend.get_object("lblWatchSources")
    watch_current = backend.get_object("lblWatchCurrent")
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

    assert do_it.text == "Debug: apply is immediate"
    assert priority.text == "Rule: margins define area; align/valign act inside it; fixed binds L/R"
    assert watch_section.text == "Watch"
    assert interval.text == "Interval"
    assert color_btn.label == "Color"
    assert backend.get_object("btnOpenSave") is None
    assert backend.get_object("btnCancelSave") is None
    assert hasattr(save_path_chooser, "get_filename")
    assert hasattr(save_path_chooser, "set_filename")
    assert save_path_state.text == "Save path: idle"
    assert watch_start.label == "Watch Start"
    assert watch_stop.label == "Watch Stop"
    assert watch_sources.text == "Watch srcdirs: L=- | R=-"
    assert watch_current.text == "Watch current: idle"
    assert pick_state.text == ""
    assert style_legend.text == "Reserved slot for future placement"
    assert command_section.text == ""
    assert flow_legend.text == "Compose -> Optimize -> Apply"
    assert prefs_btn.label == "Prefs"
    assert about_btn.label == "About"
    assert help_btn.label == "Help"
    assert save_btn.label == "Save As"
    assert optimize_btn.label == "Optimize"
    assert apply_btn.label == "Apply"
    assert tgl_upper_l.label == "Top-L"
    assert tgl_upper_r.label == "Top-R"
    assert tgl_push_left_l.label == "Left-L"
    assert tgl_push_right_l.label == "Right-L"
    assert tgl_lower_l.label == "Bottom-L"
    assert tgl_push_left_r.label == "Left-R"
    assert tgl_push_right_r.label == "Right-R"
    assert tgl_lower_r.label == "Bottom-R"


def test_runtime_backend_watch_srcdir_selection_and_watch_cycle_updates_labels(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    srcdir_r = backend.get_object("btnOpenSrcdirR")
    interval = backend.get_object("spnInterval")
    watch_start = backend.get_object("btnDaemonize")
    watch_stop = backend.get_object("btnCancelDaemonize")
    watch_sources = backend.get_object("lblWatchSources")
    watch_current = backend.get_object("lblWatchCurrent")
    status = backend.get_object("lblStatus")

    left_dir = tmp_path / "watch-left"
    right_dir = tmp_path / "watch-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    backend.connect_signals(
        {
            "on_pick_watch_srcdir": lambda path, side: bool(path) and side in {"L", "R"},
            "on_watch_start": lambda: True,
            "on_watch_stop": lambda: True,
            "on_watch_interval_change": lambda widget: int(widget.get_value_as_int()) > 0,
        }
    )

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()
    srcdir_r.click()
    srcdir_dialog.set_current_folder(str(right_dir))
    srcdir_dialog.confirm()

    assert watch_sources.text == f"Watch srcdirs: L={left_dir} | R={right_dir}"

    interval.set_value(90)
    interval.emit("value-changed", interval)
    assert status.text == "Watch: interval-updated(90s)"

    watch_start.click()
    assert status.text == "Watch: started"
    assert watch_current.text == f"Watch current: L={left_dir / 'left-1.jpg'} | R={right_dir / 'right-1.png'}"

    watch_stop.click()
    assert status.text == "Watch: stopped"


def test_runtime_backend_open_l_uses_dialog_selection_and_calls_pick_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    dialog = backend.get_object("ImgOpenDialog")
    entry = backend.get_object("entPathL")
    open_l = backend.get_object("btnGetImgL")
    pick_state = backend.get_object("lblPickState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"path": None, "side": None}

    def on_pick(path, side=None):
        observed["path"] = path
        observed["side"] = side

    backend.connect_signals({"on_pick_input": on_pick})
    open_l.click()
    dialog.set_filename("/tmp/left.jpg")
    dialog.confirm()

    assert observed["path"] == "/tmp/left.jpg"
    assert observed["side"] == "L"
    assert entry.get_text() == "left.jpg"
    assert pick_state.text == "Open-L: selected"
    assert status.text == "Open-L: selected"
    assert error.text == "Error: none"


def test_runtime_backend_clear_l_clears_only_left_side_and_keeps_right_input():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry_l = backend.get_object("entPathL")
    entry_r = backend.get_object("entPathR")
    clear_l = backend.get_object("btnClrPathL")
    optimize_btn = backend.get_object("btnOptimize")
    status = backend.get_object("lblStatus")
    observed = {"text": None}

    def on_change(text):
        observed["text"] = text

    backend.connect_signals({"on_change_input_text": on_change})
    backend.connect_signals({"on_pick_input": lambda path, side=None: True})

    dialog = backend.get_object("ImgOpenDialog")
    backend.get_object("btnGetImgL").click()
    dialog.set_filename("/tmp/left-image.jpg")
    dialog.confirm()
    backend.get_object("btnGetImgR").click()
    dialog.set_filename("/tmp/right-image.jpg")
    dialog.confirm()

    clear_l.click()

    assert entry_l.get_text() == ""
    assert entry_r.get_text() == "right-image.jpg"
    assert observed["text"] == "/tmp/right-image.jpg"
    assert optimize_btn.sensitive is True
    assert status.text == "Clear-L: ok"


def test_runtime_backend_clear_r_disables_actions_when_last_input_cleared():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry_r = backend.get_object("entPathR")
    clear_r = backend.get_object("btnClrPathR")
    save_btn = backend.get_object("btnSave")
    optimize_btn = backend.get_object("btnOptimize")

    backend.connect_signals({"on_change_input_text": lambda _text: None})
    backend.connect_signals({"on_pick_input": lambda path, side=None: True})

    dialog = backend.get_object("ImgOpenDialog")
    backend.get_object("btnGetImgR").click()
    dialog.set_filename("/tmp/right-image.jpg")
    dialog.confirm()

    clear_r.click()

    assert entry_r.get_text() == ""
    assert save_btn.sensitive is False
    assert optimize_btn.sensitive is False


def test_runtime_backend_open_r_opens_dialog_without_entry_path_requirement():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    dialog = backend.get_object("ImgOpenDialog")
    open_r = backend.get_object("btnGetImgR")
    pick_state = backend.get_object("lblPickState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    open_r.click()

    assert dialog.is_visible() is True
    assert dialog.get_side() == "R"
    assert dialog.get_title() == "Open image (R)"
    assert pick_state.text == "Open-R: dialog-open"
    assert status.text == "Open-R: dialog-open"
    assert error.text == "Error: none"


def test_runtime_backend_open_r_cancel_updates_status_and_closes_dialog():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    dialog = backend.get_object("ImgOpenDialog")
    open_r = backend.get_object("btnGetImgR")
    pick_state = backend.get_object("lblPickState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    open_r.click()
    dialog.cancel()

    assert dialog.is_visible() is False
    assert pick_state.text == "Open-R: canceled"
    assert status.text == "Open-R: canceled"
    assert error.text == "Error: none"


def test_runtime_backend_right_input_enables_optimize_buttons():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry_l = backend.get_object("entPathL")
    entry_r = backend.get_object("entPathR")
    optimize_btn = backend.get_object("btnSave")
    optimize_modern_btn = backend.get_object("btnOptimize")

    backend.connect_signals({"on_change_input_text": lambda _text: None})

    entry_l.set_text("")
    entry_r.set_text("/tmp/right-only.jpg")
    entry_r.emit("changed", entry_r)

    assert optimize_btn.sensitive is True
    assert optimize_modern_btn.sensitive is True


def test_runtime_backend_color_click_sets_deferred_status():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    color_btn = backend.get_object("btnSetColor")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    color_btn.click()

    assert status.text == "Color: deferred"
    assert error.text == "Error: none"


def test_runtime_backend_save_click_passes_selected_path_to_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_path_chooser = backend.get_object("SavePathDialog")
    save_path_state = backend.get_object("lblSavePathState")
    save_target = backend.get_object("lblSaveTarget")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {}

    save_path_chooser.set_filename("/tmp/from-runtime-dialog.jpg")

    def on_open_save(path):
        observed["filename"] = path
        return True

    backend.connect_signals({"on_save_path_selected": on_open_save})
    backend.get_object("btnSave").click()

    assert observed["filename"] == "/tmp/from-runtime-dialog.jpg"
    assert save_path_chooser.is_visible() is False
    assert save_path_state.text == "Save path: saved"
    assert save_target.text == "Save target: /tmp/from-runtime-dialog.jpg"
    assert status.text == "SavePath: saved"
    assert error.text == "Error: none"


def test_runtime_backend_native_save_path_chooser_confirm_runs_modal_flow():
    backend = GtkRuntimeSignalBackend(_NativeFakeGtk)

    save_path_state = backend.get_object("lblSavePathState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"save": 0, "confirm": None, "cancel": 0}

    def on_save():
        observed["save"] += 1
        return True

    def on_open_save(path):
        observed["confirm"] = path
        return True

    def on_cancel_save():
        observed["cancel"] += 1
        return True

    _NativeFileChooserDialog.next_response = _NativeFakeGtk.ResponseType.OK
    _NativeFileChooserDialog.next_filename = "/tmp/native-save.jpg"
    backend.connect_signals(
        {
            "on_save": on_save,
            "on_save_path_selected": on_open_save,
            "on_save_path_selection_canceled": on_cancel_save,
        }
    )

    backend.get_object("btnSave").click()

    assert observed == {"save": 1, "confirm": "/tmp/native-save.jpg", "cancel": 0}
    assert save_path_state.text == "Save path: saved"
    assert status.text == "SavePath: saved"
    assert error.text == "Error: none"
    assert _NativeFileChooserDialog.last_created is not None
    assert _NativeFileChooserDialog.last_created.action == _NativeFakeGtk.FileChooserAction.SAVE
    assert _NativeFileChooserDialog.last_created.overwrite_confirmation is True
    assert _NativeFileChooserDialog.last_created.current_name == "harite-output.jpg"


def test_runtime_backend_native_save_path_chooser_cancel_does_not_continue_save_flow():
    backend = GtkRuntimeSignalBackend(_NativeFakeGtk)

    save_path_state = backend.get_object("lblSavePathState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"save": 0, "confirm": 0, "cancel": 0}

    def on_save():
        observed["save"] += 1
        return True

    def on_open_save(_path):
        observed["confirm"] += 1
        return True

    def on_cancel_save():
        observed["cancel"] += 1
        return True

    _NativeFileChooserDialog.next_response = _NativeFakeGtk.ResponseType.CANCEL
    _NativeFileChooserDialog.next_filename = ""
    backend.connect_signals(
        {
            "on_save": on_save,
            "on_save_path_selected": on_open_save,
            "on_save_path_selection_canceled": on_cancel_save,
        }
    )

    backend.get_object("btnSave").click()

    assert observed == {"save": 1, "confirm": 0, "cancel": 1}
    assert save_path_state.text == "Save path: canceled"
    assert status.text == "SavePath: canceled"
    assert error.text == "Error: none"


def test_runtime_backend_save_click_without_path_uses_default_filename():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_path_chooser = backend.get_object("SavePathDialog")
    save_path_state = backend.get_object("lblSavePathState")
    save_target = backend.get_object("lblSaveTarget")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    called = {"filename": None}

    def on_open_save(path):
        called["filename"] = path
        return True

    backend.connect_signals({"on_save_path_selected": on_open_save})
    backend.get_object("btnSave").click()

    assert called["filename"].endswith("harite-output.jpg")
    assert save_path_chooser.is_visible() is False
    assert save_path_state.text == "Save path: saved"
    assert save_target.text.endswith("harite-output.jpg")
    assert status.text == "SavePath: saved"
    assert error.text == "Error: none"


def test_runtime_backend_save_path_chooser_proxy_no_longer_exposes_confirm_cancel_buttons():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    assert backend.get_object("btnOpenSave") is None
    assert backend.get_object("btnCancelSave") is None


def test_runtime_backend_save_path_chooser_cancel_calls_current_handler_on_native_cancel():
    backend = GtkRuntimeSignalBackend(_NativeFakeGtk)

    save_path_state = backend.get_object("lblSavePathState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"called": False}

    def on_cancel_save():
        observed["called"] = True
        return True

    _NativeFileChooserDialog.next_response = _NativeFakeGtk.ResponseType.CANCEL
    _NativeFileChooserDialog.next_filename = ""
    backend.connect_signals({"on_save_path_selection_canceled": on_cancel_save})
    backend.get_object("btnSave").click()

    assert observed["called"] is True
    assert save_path_state.text == "Save path: canceled"
    assert status.text == "SavePath: canceled"
    assert error.text == "Error: none"


def test_runtime_backend_save_path_chooser_filename_change_updates_target_label():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_path_chooser = backend.get_object("SavePathDialog")
    save_path_state = backend.get_object("lblSavePathState")
    save_target = backend.get_object("lblSaveTarget")

    save_path_chooser.show()
    save_path_chooser.set_filename("/tmp/selected.jpg")

    assert save_path_state.text == "Save path: ready"
    assert save_target.text == "Save target: /tmp/selected.jpg"


def test_runtime_backend_prefers_save_path_dialog_destroy_signal_name():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    observed = {"destroy": 0}

    def on_destroy() -> None:
        observed["destroy"] += 1

    backend.connect_signals(
        {
            "on_save_path_selected": lambda _path: True,
            "on_SavePathDialog_destroy": on_destroy,
        }
    )

    backend.get_object("SavePathDialog").set_filename("/tmp/from-save-path-destroy.jpg")
    backend.get_object("btnSave").click()

    assert observed["destroy"] == 1


def test_runtime_backend_apply_success_updates_apply_target():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    apply_target = backend.get_object("lblApplyTarget")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_optimize": lambda: True})
    backend.connect_signals({"on_apply": lambda: True})

    optimize_btn.click()
    apply_btn.click()

    assert status.text == "Apply: ok"
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

    backend.connect_signals({"on_optimize": on_optimize_clicked})
    optimize_btn.click()

    assert observed["status_when_called"] == "Optimize: running"


def test_runtime_backend_apply_failure_updates_error_message():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_apply": lambda: False})
    apply_btn.click()

    assert status.text == "Apply: failed"
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


def test_runtime_backend_save_button_skips_optimize_handler_and_reports_missing_path_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_btn = backend.get_object("btnSave")
    save_path_chooser = backend.get_object("SavePathDialog")
    save_path_state = backend.get_object("lblSavePathState")
    status = backend.get_object("lblStatus")
    calls = []

    backend.connect_signals({
        "on_save": lambda: calls.append("save") or True,
        "on_optimize": lambda: calls.append("optimize") or False,
    })

    save_btn.click()

    assert calls == ["save"]
    assert save_path_chooser.is_visible() is False
    assert save_path_state.text == "Save path: idle"
    assert status.text == "SavePath: handler-missing"


def test_runtime_backend_optimize_button_does_not_fallback_to_save_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    optimize_result = backend.get_object("lblOptimizeResult")
    apply_target = backend.get_object("lblApplyTarget")
    calls = []

    backend.connect_signals({
        "on_save": lambda: calls.append("save") or True,
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
            "on_toggle_position_pressed": lambda name: calls.append(("pressed", name)),
            "on_toggle_position": lambda name, active: calls.append(("toggled", name, active)),
            "on_toggle_position_reset": lambda name: calls.append(("released", name)),
        }
    )

    toggle = backend.get_object("tglUpperL")
    toggle.click()
    toggle.click()

    assert calls == [
        ("pressed", "tglUpperL"),
        ("toggled", "tglUpperL", True),
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

    def on_margins(name, value):
        captured["name"] = name
        captured["value"] = value

    backend.connect_signals({"on_change_margins": on_margins})
    backend.get_object("spnLMergin").emit("value-changed", backend.get_object("spnLMergin"))

    assert captured == {"name": "spnLMergin", "value": 11}
    assert status.text == "Margins: updated"
    assert error.text == "Error: none"
    assert backend.get_object("lblCurrentMargins").text == "Current margins: 11,22,33,44"


def test_runtime_backend_margin_spin_matches_upstream_adjustments():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    top = backend.get_object("spnTopMergin")
    left = backend.get_object("spnLMergin")
    right = backend.get_object("spnRMergin")
    bottom = backend.get_object("spnBtmMergin")

    assert (top.minimum, top.maximum, top.step_increment, top.page_increment) == (0, 250, 1, 10)
    assert (bottom.minimum, bottom.maximum, bottom.step_increment, bottom.page_increment) == (0, 250, 1, 10)
    assert (left.minimum, left.maximum, left.step_increment, left.page_increment) == (0, 500, 1, 10)
    assert (right.minimum, right.maximum, right.step_increment, right.page_increment) == (0, 500, 1, 10)


def test_runtime_backend_interval_spin_matches_upstream_adjustments():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    interval = backend.get_object("spnInterval")

    assert (interval.minimum, interval.maximum, interval.step_increment, interval.page_increment) == (1, 86400, 1, 10)
    assert interval.get_value_as_int() == 60


def test_runtime_backend_current_state_panel_updates_for_toggle_and_fixed():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("tglPushRightL").click()
    backend.get_object("tglUpperR").click()
    backend.get_object("radFixed").click()

    assert backend.get_object("lblCurrentFixed").text == "Current fixed: on"
    assert backend.get_object("lblCurrentStateL").text == "Current L: align=right valign=center"
    assert backend.get_object("lblCurrentStateR").text == "Current R: align=center valign=top"


def test_runtime_backend_current_state_margin_labels_follow_spin_values():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("spnLMergin").set_value(5)
    backend.get_object("spnRMergin").set_value(15)
    backend.get_object("spnTopMergin").set_value(25)
    backend.get_object("spnBtmMergin").set_value(35)
    backend.get_object("spnTopMergin").emit("value-changed", backend.get_object("spnTopMergin"))

    assert backend.get_object("lblCurrentMargins").text == "Current margins: 5,15,25,35"


def test_runtime_backend_margin_and_top_alignment_coexist_in_current_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("spnTopMergin").set_value(5)
    backend.get_object("spnTopMergin").emit("value-changed", backend.get_object("spnTopMergin"))
    backend.get_object("tglUpperL").click()

    assert backend.get_object("lblCurrentMargins").text == "Current margins: 0,0,5,0"
    assert backend.get_object("lblCurrentStateL").text == "Current L: align=center valign=top"

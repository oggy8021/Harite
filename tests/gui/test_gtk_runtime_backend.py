from __future__ import annotations

from PIL import Image

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
        self._parent = None

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
        if getattr(child, "_parent", None) is not None:
            raise AssertionError("child already has a parent")
        child._parent = self
        self.child = child


class _Box(_WidgetBase):
    def __init__(self, **_kwargs):
        super().__init__()
        self.children = []

    def set_border_width(self, _width):
        return None

    def pack_start(self, child, *_args):
        if getattr(child, "_parent", None) is not None:
            raise AssertionError("child already has a parent")
        child._parent = self
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
        if getattr(child, "_parent", None) is not None:
            raise AssertionError("child already has a parent")
        child._parent = self
        self.children.append((child, int(left), int(top), int(width), int(height)))


class _Notebook(_WidgetBase):
    def __init__(self):
        super().__init__()
        self.pages = []

    def append_page(self, child, tab_label):
        if getattr(child, "_parent", None) is not None:
            raise AssertionError("child already has a parent")
        child._parent = self
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

    def set_size_request(self, *_args):
        return None


class _TextBuffer(_WidgetBase):
    def __init__(self):
        super().__init__()
        self._text = ""

    def set_text(self, text):
        self._text = text
        self.emit("changed", self)

    def get_start_iter(self):
        return 0

    def get_end_iter(self):
        return len(self._text)

    def get_bounds(self):
        return (0, len(self._text))

    def get_text(self, _start, _end, _include_hidden):
        return self._text


class _TextView(_WidgetBase):
    def __init__(self):
        super().__init__()
        self._buffer = _TextBuffer()

    def set_placeholder_text(self, _text):
        return None

    def set_size_request(self, *_args):
        return None

    def get_buffer(self):
        return self._buffer

    def set_text(self, text):
        self._buffer.set_text(text)

    def get_text(self):
        return self._buffer.get_text(0, len(self._buffer._text), True)


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
    def __init__(self, label="", group=None):
        super().__init__(label=label)
        if group is None:
            self._group = [self]
        else:
            self._group = group
            self._group.append(self)

    @classmethod
    def new_with_label(cls, _group, label):
        return cls(label=label)

    @classmethod
    def new_with_label_from_widget(cls, _widget, label):
        group = getattr(_widget, "_group", [_widget])
        return cls(label=label, group=group)

    def click(self):
        self.emit("pressed", self)
        for member in getattr(self, "_group", [self]):
            member._active = member is self
            member.emit("toggled", member)
        self.emit("released", self)
        self.emit("clicked", self)


class _FakeGtk:
    Orientation = _Orientation
    Window = _Window
    Box = _Box
    Grid = _Grid
    Notebook = _Notebook
    Label = _Label
    Entry = _Entry
    TextView = _TextView
    Button = _Button
    ToggleButton = _ToggleButton
    SpinButton = _SpinButton
    RadioButton = _RadioButton


class _FakeGLib:
    next_source_id = 1
    registered_sources = {}
    removed_sources = []

    @classmethod
    def reset(cls):
        cls.next_source_id = 1
        cls.registered_sources = {}
        cls.removed_sources = []

    @classmethod
    def timeout_add(cls, interval_ms, callback):
        source_id = cls.next_source_id
        cls.next_source_id += 1
        cls.registered_sources[source_id] = {
            "interval_ms": int(interval_ms),
            "callback": callback,
        }
        return source_id

    @classmethod
    def source_remove(cls, source_id):
        cls.removed_sources.append(int(source_id))
        cls.registered_sources.pop(int(source_id), None)
        return True


class _TimerFakeGtk(_FakeGtk):
    GLib = _FakeGLib


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

    assert window.form_state.align == ("right", "center")
    assert window.form_state.valign == ("center", "top")
    assert window.form_state.margins == "0,0,25,0"


def test_runtime_backend_updates_mainwindow_apply_mode_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    dispatch = create_mainwindow_signal_dispatch(window, ("on_change_apply_mode",))
    backend.connect_signals(dispatch)

    backend.get_object("radApplyPerMonitor").click()

    assert window.apply_mode == "per-monitor-auto-split"


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
    assert backend.get_object("lblPreviewSection") is not None
    assert backend.get_object("boxPreviewSection") is not None
    assert backend.get_object("imgPreviewL") is not None
    assert backend.get_object("imgPreviewR") is not None
    assert backend.get_object("lblPreviewAssignL") is not None
    assert backend.get_object("lblPreviewAssignR") is not None
    assert backend.get_object("lblPreviewResultL") is not None
    assert backend.get_object("lblPreviewResultR") is not None
    assert backend.get_object("lblPreviewState") is not None
    assert backend.get_object("lblPreviewSource") is not None
    assert backend.get_object("lblPreviewAssist") is not None
    assert backend.get_object("marginsTab") is not None
    assert backend.get_object("lblMarginsTabTitle") is not None
    assert backend.get_object("lblMarginsSection") is not None
    assert backend.get_object("lblMarginTextSection") is not None
    assert backend.get_object("radMarginTextModeOff") is not None
    assert backend.get_object("radMarginTextModeSettings") is not None
    assert backend.get_object("radMarginTextModeText") is not None
    assert backend.get_object("radMarginTextModeBoth") is not None
    assert backend.get_object("txtMarginText") is not None
    assert backend.get_object("radMarginTextPositionLeftTop") is not None
    assert backend.get_object("radMarginTextPositionRightBottom") is not None
    assert backend.get_object("radMarginTextPositionLeftBottom") is not None
    assert backend.get_object("radMarginTextPositionRightTop") is not None
    assert backend.get_object("lblDoItPlanned") is not None
    assert backend.get_object("lblSavePathState") is not None
    assert backend.get_object("lblSaveTarget") is not None
    assert backend.get_object("lblPriorityRule") is not None
    assert backend.get_object("lblStyleLegend") is not None
    assert backend.get_object("lblCurrentStateSection") is not None
    assert backend.get_object("lblCurrentMargins") is not None
    assert backend.get_object("lblCurrentStateL") is not None
    assert backend.get_object("lblCurrentStateR") is not None
    assert backend.get_object("lblCommandSection") is not None
    assert backend.get_object("lblFlowLegend") is not None
    assert backend.get_object("lblWatchSection") is not None
    assert backend.get_object("lblError") is not None


def test_runtime_backend_current_state_panel_defaults_are_available():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    assert backend.get_object("lblCurrentStateSection").text == "Main Window Current alignment:"


def test_runtime_backend_adds_margins_tab_and_syncs_owner_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    window.form_state.embed_info = "combo"
    window.form_state.embed_text = "margin-note"
    window.form_state.embed_position = "bottom"
    window.form_state.embed_max_lines = 4

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_change_margin_text_mode",
            "on_change_margin_text",
            "on_change_margin_text_position",
            "on_change_margin_text_max_lines",
        ),
    )
    backend.connect_signals(dispatch)

    notebook = backend.get_object("commandTabs")
    assert len(notebook.pages) == 3
    assert notebook.pages[0][1].text == "Main"
    assert notebook.pages[1][1].text == "Margins"
    assert notebook.pages[2][1].text == "Watch (stopped)"
    assert backend.get_object("lblMarginsTabTitle").text == "Margins"
    assert backend.get_object("radMarginTextModeBoth").get_active() is True
    assert backend.get_object("txtMarginText").get_text() == "margin-note"
    assert backend.get_object("radMarginTextPositionRightBottom").get_active() is True


def test_runtime_backend_margins_tab_updates_owner_state_and_cli_preview(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    window.form_state.input_value = "a.jpg"
    window.form_state.output_dir = str(out_dir)
    window.form_state.margins = "10,10,20,10"

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_change_margin_text_mode",
            "on_change_margin_text",
            "on_change_margin_text_position",
            "on_change_margins",
        ),
    )
    backend.connect_signals(dispatch)

    backend.get_object("spnTopMergin").set_value(24)
    backend.get_object("spnTopMergin").emit("value-changed", backend.get_object("spnTopMergin"))
    backend.get_object("radMarginTextModeText").click()
    backend.get_object("txtMarginText").set_text("hello\nworld")
    backend.get_object("radMarginTextPositionLeftTop").click()

    assert window.form_state.margins == "10,10,24,10"
    assert window.form_state.embed_info == "free"
    assert window.form_state.embed_text == "hello\nworld"
    assert window.form_state.embed_position == "top"
    assert backend.get_object("lblStatus").text.startswith("Margins: margin text ready in left top position")
    assert backend.get_object("lblError").text == "Error: none"

    preview = window.build_optimize_cli_preview()
    assert "--margins 10,10,24,10" in preview
    assert "--embed-info free" in preview
    assert "--embed-text hello\nworld" in preview
    assert "--embed-position top" in preview
    assert "--embed-max-lines" not in preview


def test_runtime_backend_clamps_margin_text_to_five_lines():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    dispatch = create_mainwindow_signal_dispatch(window, ("on_change_margin_text",))
    backend.connect_signals(dispatch)

    backend.get_object("txtMarginText").set_text("1\n2\n3\n4\n5\n6")

    assert window.form_state.embed_text == "1\n2\n3\n4\n5"
    assert backend.get_object("txtMarginText").get_text() == "1\n2\n3\n4\n5"


def test_runtime_backend_preserves_trailing_newline_while_editing_margin_text():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    dispatch = create_mainwindow_signal_dispatch(window, ("on_change_margin_text",))
    backend.connect_signals(dispatch)

    backend.get_object("txtMarginText").set_text("1\n")

    assert window.form_state.embed_text == "1\n"
    assert backend.get_object("txtMarginText").get_text() == "1\n"


def test_runtime_backend_margin_text_preflight_reports_small_margin_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    window.form_state.resolution = "1920x1080"
    window.form_state.margins = "10,10,20,10"

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_change_margin_text_mode",
            "on_change_margin_text",
            "on_change_margin_text_position",
        ),
    )
    backend.connect_signals(dispatch)

    backend.get_object("radMarginTextModeSettings").click()
    backend.get_object("radMarginTextPositionRightBottom").click()

    assert backend.get_object("lblStatus").text == "Margins: margin text does not fit current margin area"
    assert backend.get_object("lblError").text == "Error: selected margin area is too small for margin text"


def test_runtime_backend_syncs_result_preview_from_mainwindow(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    source = tmp_path / "preview.jpg"
    Image.new("RGB", (320, 180), color=(20, 30, 40)).save(source)

    def run_optimize(_form_state):
        return [source], []

    window.controller.run_optimize = run_optimize

    dispatch = create_mainwindow_signal_dispatch(window, ("on_change_input_text", "on_optimize", "on_change_apply_mode"))
    backend.connect_signals(dispatch)

    backend.get_object("entPathL").set_text("left.jpg")
    backend.get_object("entPathL").emit("changed", backend.get_object("entPathL"))
    backend.get_object("btnOptimize").click()

    assert backend.get_object("lblPreviewAssignL").text == "L display <- left.jpg"
    assert backend.get_object("lblPreviewAssignR").text == "R display <- left.jpg"
    assert backend.get_object("lblPreviewResultL").text == "Result: full optimized image"
    assert backend.get_object("lblPreviewResultR").text == "Result: full optimized image"
    assert backend.get_object("lblPreviewState").text == "Preview: same image on both displays"
    assert backend.get_object("lblPreviewSource").text == "Preview source: preview.jpg"
    assert backend.get_object("lblPreviewAssist").text == "Assist: same optimized image will be applied to both displays"
    assert backend.get_object("imgPreviewL").text == "preview.jpg"
    assert backend.get_object("imgPreviewR").text == "preview.jpg"

    backend.get_object("entPathR").set_text("right.jpg")
    backend.get_object("entPathR").emit("changed", backend.get_object("entPathR"))

    backend.get_object("radApplyPerMonitor").click()

    assert backend.get_object("lblPreviewAssignL").text == "L display <- left.jpg"
    assert backend.get_object("lblPreviewAssignR").text == "R display <- right.jpg"
    assert backend.get_object("lblPreviewResultL").text == "Result: auto-split left crop"
    assert backend.get_object("lblPreviewResultR").text == "Result: auto-split right crop"
    assert backend.get_object("lblPreviewState").text == "Preview: pseudo auto-split by display widths"
    assert backend.get_object("lblPreviewAssist").text == "Assist: auto-split by current left/right display widths"
    assert backend.get_object("lblCurrentMargins").text == "margins=0,0,0,0"
    assert backend.get_object("lblCurrentStateL").text == "L: align=center valign=center"
    assert backend.get_object("lblCurrentStateR").text == "R: align=center valign=center"


def test_runtime_backend_shows_phase6_labels_and_controls():
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
    watch_output = backend.get_object("lblWatchOutput")
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
    assert priority.text == "Rule: margins define area; align/valign act inside it"
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
    assert watch_output.text == "Watch output: ."
    assert pick_state.text == ""
    assert style_legend.text == "Current behavior: margins are global to the composite canvas"
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


def test_runtime_backend_watch_srcdir_selection_and_watch_cycle_updates_labels(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    interval = backend.get_object("spnInterval")
    watch_start = backend.get_object("btnDaemonize")
    watch_stop = backend.get_object("btnCancelDaemonize")
    watch_sources = backend.get_object("lblWatchSources")
    watch_current = backend.get_object("lblWatchCurrent")
    watch_output = backend.get_object("lblWatchOutput")
    watch_tab_title = backend.get_object("lblWatchTabTitle")
    status = backend.get_object("lblStatus")

    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_watch_srcdir",
            "on_watch_start",
            "on_watch_tick",
            "on_watch_stop",
            "on_watch_interval_change",
        ),
    )
    backend.connect_signals(dispatch)
    window.form_state.output_dir = str(tmp_path / "watch-output")
    backend._sync_watch_state_from_owner(window)

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    assert watch_sources.text == f"Watch srcdirs: L={left_dir} | R=-"
    assert watch_output.text == f"Watch output: {tmp_path / 'watch-output'}"

    interval.set_value(90)
    interval.emit("value-changed", interval)
    assert status.text == "Watch: interval-updated(90s)"
    assert watch_tab_title.text == "Watch (stopped)"

    watch_start.click()
    assert status.text == "Watch: started"
    assert watch_tab_title.text == "Watch (running)"
    assert watch_current.text == f"Watch current: L={left_dir / 'left-1.jpg'} | R=-"

    assert backend.run_watch_cycle_once() is True
    assert watch_tab_title.text == "Watch (running)"
    assert watch_current.text == f"Watch current: L={left_dir / 'left-2.jpg'} | R=-"

    watch_stop.click()
    assert status.text == "Watch: stopped"
    assert watch_tab_title.text == "Watch (stopped)"
    assert backend.run_watch_cycle_once() is False


def test_runtime_backend_connect_signals_syncs_watch_output_from_owner():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    window.form_state.output_dir = "/gui/pictures"

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_watch_start",
            "on_watch_tick",
            "on_watch_stop",
            "on_watch_interval_change",
        ),
    )
    backend.connect_signals(dispatch)

    assert backend.get_object("lblWatchOutput").text == "Watch output: /gui/pictures"


def test_runtime_backend_watch_start_registers_timer_and_stop_removes_it(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            self.calls.append((path, dry_run))
            return True

    _FakeGLib.reset()
    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    backend = GtkRuntimeSignalBackend(_TimerFakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    interval = backend.get_object("spnInterval")
    watch_start = backend.get_object("btnDaemonize")
    watch_stop = backend.get_object("btnCancelDaemonize")
    watch_current = backend.get_object("lblWatchCurrent")

    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_watch_srcdir",
            "on_watch_start",
            "on_watch_tick",
            "on_watch_stop",
            "on_watch_interval_change",
        ),
    )
    backend.connect_signals(dispatch)

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    interval.set_value(45)
    interval.emit("value-changed", interval)

    watch_start.click()

    assert backend._watch_timer_source_id == 1
    assert _FakeGLib.registered_sources[1]["interval_ms"] == 45000
    assert plugin.calls == [(str(left_dir / "left-1.jpg"), False)]

    timer_callback = _FakeGLib.registered_sources[1]["callback"]
    assert timer_callback() is True
    assert watch_current.text == f"Watch current: L={left_dir / 'left-2.jpg'} | R=-"
    assert plugin.calls[-1] == (str(left_dir / "left-2.jpg"), False)

    watch_stop.click()

    assert backend._watch_timer_source_id is None
    assert _FakeGLib.removed_sources == [1]


def test_runtime_backend_shows_owner_watch_start_failure_reason(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: None,
    )

    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    window.plugin_name = "linux"

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    srcdir_r = backend.get_object("btnOpenSrcdirR")
    watch_start = backend.get_object("btnDaemonize")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    watch_tab_title = backend.get_object("lblWatchTabTitle")

    left_dir = tmp_path / "watch-left"
    right_dir = tmp_path / "watch-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_watch_srcdir",
            "on_watch_start",
            "on_watch_tick",
            "on_watch_stop",
            "on_watch_interval_change",
        ),
    )
    backend.connect_signals(dispatch)

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()
    srcdir_r.click()
    srcdir_dialog.set_current_folder(str(right_dir))
    srcdir_dialog.confirm()

    watch_start.click()

    assert status.text == "Watch: dual-source watch requires two detected displays"
    assert error.text == "Error: dual-source watch requires two detected displays"
    assert watch_tab_title.text == "Watch (stopped)"


def test_runtime_backend_shows_owner_watch_tick_failure_reason(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = 0

        def apply(self, path: str, *, dry_run: bool = True) -> bool:
            self.calls += 1
            return self.calls == 1

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    watch_start = backend.get_object("btnDaemonize")
    watch_current = backend.get_object("lblWatchCurrent")
    watch_tab_title = backend.get_object("lblWatchTabTitle")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    left_dir = tmp_path / "watch-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_watch_srcdir",
            "on_watch_start",
            "on_watch_tick",
            "on_watch_stop",
            "on_watch_interval_change",
        ),
    )
    backend.connect_signals(dispatch)

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    watch_start.click()
    assert status.text == "Watch: started"
    assert watch_tab_title.text == "Watch (running)"

    assert backend.run_watch_cycle_once() is False
    assert status.text == "Watch: watch tick single-file apply failed"
    assert error.text == "Error: watch tick single-file apply failed"
    assert watch_tab_title.text == "Watch (stopped)"
    assert watch_current.text == f"Watch current: L={left_dir / 'left-2.jpg'} | R=-"


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


def test_runtime_backend_open_l_truncates_long_display_name():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    dialog = backend.get_object("ImgOpenDialog")
    entry = backend.get_object("entPathL")

    backend.connect_signals({"on_pick_input": lambda *_args: None})
    backend.get_object("btnGetImgL").click()
    dialog.set_filename("/tmp/Higashiyama-Kaii-Cho-un-1080x1920-700x1244.jpg")
    dialog.confirm()

    assert entry.get_text() == "Higashiyama-Kaii-Cho-...700x1244.jpg"


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
    assert apply_target.text == "Apply target: last applied"


def test_runtime_backend_apply_mode_defaults_to_single_file():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    assert backend.get_object("radApplySingle").label == "No Split"
    assert backend.get_object("radApplyPerMonitor").label == "Auto-Split"
    assert backend.get_object("radApplySingle").get_active() is True
    assert backend.get_object("radApplyPerMonitor").get_active() is False
    assert backend.get_object("lblApplyMode").text == "Apply the optimized image as a single file."


def test_runtime_backend_apply_mode_toggle_dispatches_and_updates_label():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    observed = {}

    backend.connect_signals({"on_change_apply_mode": lambda mode: observed.setdefault("mode", mode) or True})

    backend.get_object("radApplyPerMonitor").click()

    assert observed["mode"] == "per-monitor-auto-split"
    assert backend.get_object("lblApplyMode").text == "Split the optimized image and apply per display."
    assert backend.get_object("lblStatus").text == "ApplyMode: updated"


def test_runtime_backend_apply_mode_can_return_to_default_from_per_monitor():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    observed = []

    backend.connect_signals({"on_change_apply_mode": lambda mode: observed.append(mode) or True})

    backend.get_object("radApplyPerMonitor").click()
    backend.get_object("radApplySingle").click()

    assert observed == ["per-monitor-auto-split", "single-file"]
    assert backend.get_object("lblApplyMode").text == "Apply the optimized image as a single file."


def test_runtime_backend_cross_layout_places_top_and_bottom_per_side():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    compose_grid = backend.get_object("composeGrid")
    left_col = backend.get_object("leftDisplayCol")
    right_col = backend.get_object("rightDisplayCol")

    assert compose_grid.children == [
        (left_col, 0, 0, 1, 1),
        (backend.get_object("inputRowL"), 0, 1, 1, 1),
        (right_col, 1, 0, 1, 1),
        (backend.get_object("inputRowR"), 1, 1, 1, 1),
        (backend.get_object("actionClusterRow"), 0, 2, 2, 1),
    ]

    assert left_col.children == [
        (backend.get_object("tglUpperL"), 1, 0, 1, 1),
        (backend.get_object("tglPushLeftL"), 0, 1, 1, 1),
        (backend.get_object("btnGetImgL"), 1, 1, 1, 1),
        (backend.get_object("tglPushRightL"), 2, 1, 1, 1),
        (backend.get_object("tglLowerL"), 1, 2, 1, 1),
    ]
    assert right_col.children == [
        (backend.get_object("tglUpperR"), 1, 0, 1, 1),
        (backend.get_object("tglPushLeftR"), 0, 1, 1, 1),
        (backend.get_object("btnGetImgR"), 1, 1, 1, 1),
        (backend.get_object("tglPushRightR"), 2, 1, 1, 1),
        (backend.get_object("tglLowerR"), 1, 2, 1, 1),
    ]


def test_runtime_backend_prefs_button_dispatches_open_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    observed = {"opened": 0}

    backend.connect_signals(
        {
            "on_open_settings_dialog": lambda: observed.__setitem__("opened", observed["opened"] + 1) or True,
            "on_get_preferences_config": lambda: {"plugin": "linux", "apply_mode": "single-file"},
        }
    )

    backend.get_object("btnSetting").click()

    assert observed["opened"] == 1
    assert backend.get_object("lblStatus").text == "Prefs: opened"
    assert backend.get_object("SettingsDialog").is_visible() is True
    assert backend.get_object("SettingsDialog").get_preferences_config()["plugin"] == "linux"
    assert backend.get_object("entPrefsPlugin").get_text() == "linux"
    assert backend.get_object("radPrefsApplySingle").label == "Apply Default"
    assert backend.get_object("radPrefsApplyPerMonitor").label == "Apply Auto-split"
    assert backend.get_object("radPrefsApplySingle").get_active() is True
    assert backend.get_object("spnPrefsWatchInterval") is None


def test_runtime_backend_prefs_apply_load_save_and_close_dispatch_handlers(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")
    observed = {"apply": None, "load": None, "save": None, "close": 0}

    import_path = tmp_path / "load-prefs.json"
    export_path = tmp_path / "save-prefs.json"
    dialog.set_preferences_config(
        {
            "resolution": "1920x1080",
            "plugin": "linux",
            "apply_mode": "single-file",
            "watch_interval_seconds": 60,
            "watch_srcdir_l": "/watch/left",
        }
    )
    dialog.set_import_path(str(import_path))
    dialog.set_export_path(str(export_path))
    dialog.show()

    backend.connect_signals(
        {
            "on_apply_preferences": lambda config: observed.__setitem__("apply", config) or True,
            "on_load_preferences_file": lambda path: observed.__setitem__("load", path) or True,
            "on_save_preferences_file": lambda path, config=None: observed.__setitem__("save", (path, config)) or True,
            "on_get_preferences_config": lambda: {"plugin": "xfce", "apply_mode": "per-monitor-auto-split"},
            "on_close_settings_dialog": lambda: observed.__setitem__("close", observed["close"] + 1) or True,
        }
    )

    backend.get_object("entPrefsResolution").set_text("auto")
    backend.get_object("entPrefsPlugin").set_text("xfce")
    backend.get_object("entPrefsImportPath").set_text(str(import_path))
    backend.get_object("entPrefsExportPath").set_text(str(export_path))
    backend.get_object("radPrefsTwoScreenAuto").set_active(True)
    backend.get_object("radPrefsTwoScreenOn").set_active(False)
    backend.get_object("radPrefsTwoScreenOff").set_active(False)
    backend.get_object("radPrefsApplySingle").set_active(False)
    backend.get_object("radPrefsApplyPerMonitor").set_active(True)

    backend.get_object("btnPrefsApply").click()
    assert observed["apply"]["resolution"] == "auto"
    assert observed["apply"]["two_screen"] == "auto"
    assert observed["apply"]["align"] == ["center", "center"]
    assert observed["apply"]["valign"] == ["center", "center"]
    assert observed["apply"]["plugin"] == "xfce"
    assert observed["apply"]["apply_mode"] == "per-monitor-auto-split"
    assert observed["apply"]["watch_interval_seconds"] == 60
    assert observed["apply"]["watch_srcdir_l"] == "/watch/left"
    assert dialog.is_visible() is False
    assert backend.get_object("lblPrefsState").text == "Prefs: applied"

    dialog.show()
    backend.get_object("btnPrefsLoad").click()
    assert observed["load"] == str(import_path)
    assert dialog.get_preferences_config()["plugin"] == "xfce"
    assert backend.get_object("entPrefsPlugin").get_text() == "xfce"
    assert backend.get_object("entPrefsAlign").get_text() == "center,center"
    assert backend.get_object("entPrefsValign").get_text() == "center,center"
    assert backend.get_object("radPrefsApplyPerMonitor").get_active() is True
    assert backend.get_object("lblPrefsState").text == "Prefs: loaded"

    backend.get_object("entPrefsPlugin").set_text("saved-plugin")

    backend.get_object("btnPrefsSave").click()
    assert observed["save"][0] == str(export_path)
    assert observed["save"][1]["plugin"] == "saved-plugin"
    assert observed["save"][1]["watch_interval_seconds"] == 60
    assert observed["save"][1]["watch_srcdir_l"] == "/watch/left"
    assert backend.get_object("lblPrefsState").text == "Prefs: saved"

    backend.get_object("btnPrefsClose").click()
    assert observed["close"] == 1
    assert dialog.is_visible() is False
    assert backend.get_object("lblPrefsState").text == "Prefs: closed"


def test_runtime_backend_prefs_load_updates_watch_tab_state(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    import_path = tmp_path / "watch-prefs.json"
    import_path.write_text(
        """
{
    "margins": "5,15,25,35",
    "align": ["right", "center"],
    "valign": ["center", "top"],
  "plugin": "linux",
  "apply_mode": "per-monitor-auto-split",
  "watch_interval_seconds": 45,
  "watch_srcdir_l": "/watch/left",
  "watch_srcdir_r": "/watch/right"
}
""".strip(),
        encoding="utf-8",
    )

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_open_settings_dialog",
            "on_get_preferences_config",
            "on_load_preferences_file",
            "on_close_settings_dialog",
        ),
    )
    backend.connect_signals(dispatch)

    backend.get_object("btnSetting").click()
    backend.get_object("entPrefsImportPath").set_text(str(import_path))
    backend.get_object("btnPrefsLoad").click()

    assert backend.get_object("lblWatchSources").text == "Watch srcdirs: L=/watch/left | R=/watch/right"
    assert backend.get_object("spnInterval").get_value_as_int() == 45
    assert backend.get_object("lblCurrentMargins").text == "margins=5,15,25,35"
    assert backend.get_object("lblCurrentStateL").text == "L: align=right valign=center"
    assert backend.get_object("lblCurrentStateR").text == "R: align=center valign=top"


def test_runtime_backend_prefs_preserves_explicit_apply_mode_when_unedited(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")
    observed = {"apply": None, "save": None}

    import_path = tmp_path / "explicit-load.json"
    export_path = tmp_path / "explicit-save.json"
    dialog.set_preferences_config(
        {
            "plugin": "linux",
            "apply_mode": "per-monitor-explicit",
        }
    )
    dialog.set_import_path(str(import_path))
    dialog.set_export_path(str(export_path))
    dialog.show()

    backend.connect_signals(
        {
            "on_apply_preferences": lambda config: observed.__setitem__("apply", config) or True,
            "on_load_preferences_file": lambda path: True,
            "on_save_preferences_file": lambda path, config=None: observed.__setitem__("save", (path, config)) or True,
            "on_get_preferences_config": lambda: {"plugin": "linux", "apply_mode": "per-monitor-explicit"},
        }
    )

    backend.get_object("btnPrefsLoad").click()

    assert backend.get_object("radPrefsApplySingle").get_active() is False
    assert backend.get_object("radPrefsApplyPerMonitor").get_active() is False

    backend.get_object("btnPrefsApply").click()
    assert observed["apply"]["apply_mode"] == "per-monitor-explicit"

    dialog.show()
    backend.get_object("entPrefsExportPath").set_text(str(export_path))
    backend.get_object("btnPrefsSave").click()
    assert observed["save"][0] == str(export_path)
    assert observed["save"][1]["apply_mode"] == "per-monitor-explicit"


def test_runtime_backend_prefs_can_override_preserved_explicit_apply_mode(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")
    observed = {"apply": None}

    import_path = tmp_path / "explicit-load.json"
    dialog.set_preferences_config(
        {
            "plugin": "linux",
            "apply_mode": "per-monitor-explicit",
        }
    )
    dialog.set_import_path(str(import_path))
    dialog.show()

    backend.connect_signals(
        {
            "on_apply_preferences": lambda config: observed.__setitem__("apply", config) or True,
            "on_load_preferences_file": lambda path: True,
            "on_get_preferences_config": lambda: {"plugin": "linux", "apply_mode": "per-monitor-explicit"},
        }
    )

    backend.get_object("btnPrefsLoad").click()
    backend.get_object("radPrefsApplyPerMonitor").click()
    backend.get_object("btnPrefsApply").click()

    assert observed["apply"]["apply_mode"] == "per-monitor-auto-split"


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
    assert backend.get_object("lblCurrentMargins").text == "margins=11,22,33,44"


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


def test_runtime_backend_current_state_panel_updates_for_toggle_positions():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("tglPushRightL").click()
    backend.get_object("tglUpperR").click()

    assert backend.get_object("lblCurrentStateL").text == "L: align=right valign=center"
    assert backend.get_object("lblCurrentStateR").text == "R: align=center valign=top"


def test_runtime_backend_current_state_margin_labels_follow_spin_values():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("spnLMergin").set_value(5)
    backend.get_object("spnRMergin").set_value(15)
    backend.get_object("spnTopMergin").set_value(25)
    backend.get_object("spnBtmMergin").set_value(35)
    backend.get_object("spnTopMergin").emit("value-changed", backend.get_object("spnTopMergin"))

    assert backend.get_object("lblCurrentMargins").text == "margins=5,15,25,35"


def test_runtime_backend_margin_and_top_alignment_coexist_in_current_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("spnTopMergin").set_value(5)
    backend.get_object("spnTopMergin").emit("value-changed", backend.get_object("spnTopMergin"))
    backend.get_object("tglUpperL").click()

    assert backend.get_object("lblCurrentMargins").text == "margins=0,0,5,0"
    assert backend.get_object("lblCurrentStateL").text == "L: align=center valign=top"

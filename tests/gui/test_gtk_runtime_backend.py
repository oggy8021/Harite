from __future__ import annotations

from pathlib import Path

from PIL import Image
import pytest

from harite.apply_settings import EffectiveApplySettings
from harite.display_context import TwoScreenOptimizeContext
from harite.gui.adapters.gtk_backend import GtkRuntimeSignalBackend
from harite.gui.adapters.gtk_backend import load_gtk_runtime_signal_backend
from harite.gui.adapters.gtk_backend import present_gtk_window
from harite.gui.adapters.gtk_runtime_dialogs import ColorDialogProxy
from harite.gui.adapters.gtk_runtime_file_dialog_flow import format_input_display
from harite.gui.adapters.gtk_runtime_file_dialog_flow import notify_open_dialog_destroy
from harite.gui.adapters.gtk_runtime_margin_text_gtk import apply_margin_text_widget_style
from harite.gui.adapters.gtk_runtime_margin_text_gtk import on_margin_text_key_press
from harite.gui.adapters.gtk_runtime_slideshow import get_glib_module
from harite.gui.adapters.ui_adapter import create_mainwindow_signal_dispatch
from harite.gui.views.main_window import MainWindow
from harite.workspace import Display

from harite.gui.adapters_qt.qt_widget_helpers import format_slideshow_output_label_text


def _setup_linux_pictures_env(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    home = tmp_path / "home"
    pictures_root = home / "Pictures"
    pictures_root.mkdir(parents=True)
    xdg_config = tmp_path / "xdg-config"
    xdg_config.mkdir()
    (xdg_config / "user-dirs.dirs").write_text('XDG_PICTURES_DIR="$HOME/Pictures"\n', encoding="utf-8")
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")
    work_dir = pictures_root / "Harite" / "slideshow"
    return pictures_root, work_dir


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

    def get_children(self):
        return list(self.children)

    def remove(self, child):
        self.children.remove(child)
        child._parent = None


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
        self.markup = label
        self.selectable = False
        self.wrap = False

    def set_xalign(self, _value):
        return None

    def set_selectable(self, value: bool) -> None:
        self.selectable = bool(value)

    def set_wrap(self, value: bool) -> None:
        self.wrap = bool(value)

    def set_text(self, text):
        self.text = text
        self.markup = text

    def set_markup(self, markup):
        self.markup = markup
        self.text = markup.replace("<b>", "").replace("</b>", "")

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
        self.tooltip_text = ""
        self.sensitive = True
        self.image = None
        self.always_show_image = False

    def set_tooltip_text(self, text):
        self.tooltip_text = text

    def set_sensitive(self, enabled):
        self.sensitive = bool(enabled)

    def set_image(self, image):
        self.image = image

    def set_always_show_image(self, enabled):
        self.always_show_image = bool(enabled)

    def set_label(self, label):
        self.label = label

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


class _CheckButton(_ToggleButton):
    def set_no_show_all(self, _hidden):
        return None


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


class _Image(_WidgetBase):
    def __init__(self):
        super().__init__()
        self.file_path = ""

    @classmethod
    def new_from_file(cls, file_path):
        image = cls()
        image.file_path = str(file_path)
        return image

    def set_from_file(self, file_path):
        self.file_path = str(file_path)


class _Revealer(_WidgetBase):
    def __init__(self):
        super().__init__()
        self._revealed = False
        self.child = None

    def set_reveal_child(self, revealed):
        self._revealed = bool(revealed)

    def get_reveal_child(self):
        return self._revealed

    def add(self, child):
        if getattr(child, "_parent", None) is not None:
            raise AssertionError("child already has a parent")
        child._parent = self
        self.child = child


class _FakeGtk:
    Orientation = _Orientation
    Revealer = _Revealer
    Window = _Window
    Box = _Box
    Grid = _Grid
    Notebook = _Notebook
    Label = _Label
    Entry = _Entry
    TextView = _TextView
    Button = _Button
    ToggleButton = _ToggleButton
    CheckButton = _CheckButton
    SpinButton = _SpinButton
    RadioButton = _RadioButton
    Image = _Image


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


class _FakeRgba:
    def __init__(self):
        self.red = 0.0
        self.green = 0.0
        self.blue = 0.0
        self.alpha = 1.0


class _NativeColorChooserDialog:
    next_response = _NativeResponseType.CANCEL
    next_hex_text = None
    next_responses = []
    next_hex_texts = []
    last_created = None

    def __init__(self, title="", parent=None):
        self.title = title
        self.parent = parent
        self._content_area = _Box()
        self._action_area = _Box()
        self._rgba = _FakeRgba()
        self._signals = {}
        self._action_area.pack_start(_Button(label="キャンセル(C)"), False, False, 0)
        self._action_area.pack_start(_Button(label="選択(S)"), False, False, 0)
        _NativeColorChooserDialog.last_created = self

    def set_modal(self, _enabled):
        return None

    def set_transient_for(self, _parent):
        return None

    def set_destroy_with_parent(self, _enabled):
        return None

    def get_content_area(self):
        return self._content_area

    def get_action_area(self):
        return self._action_area

    def connect(self, name, callback):
        self._signals.setdefault(name, []).append(callback)

    def set_rgba(self, rgba):
        self._rgba = rgba

    def get_rgba(self):
        return self._rgba

    def show_all(self):
        return None

    def run(self):
        next_hex_text = self.next_hex_texts.pop(0) if self.next_hex_texts else self.next_hex_text
        if next_hex_text is not None and hasattr(self, "_harite_hex_entry"):
            self._harite_hex_entry.set_text(next_hex_text)
        return self.next_responses.pop(0) if self.next_responses else self.next_response

    def destroy(self):
        return None


class _NativeColorFakeGtk(_FakeGtk):
    ColorChooserDialog = _NativeColorChooserDialog
    ResponseType = _NativeResponseType


class _NativeColorChooserWidget(_Box):
    def __init__(self):
        super().__init__()
        self._rgba = _FakeRgba()

    def set_use_alpha(self, _enabled):
        return None

    def connect(self, name, callback):
        super().connect(name, callback)

    def set_rgba(self, rgba):
        self._rgba = rgba
        self.emit("notify::rgba", self)

    def get_rgba(self):
        return self._rgba


class _EmbeddedNativeColorFakeGtk(_NativeColorFakeGtk):
    ColorChooserWidget = _NativeColorChooserWidget


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
    backend.get_object("spnTopMargin").set_value(25)
    backend.get_object("spnTopMargin").emit("value-changed", backend.get_object("spnTopMargin"))

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


def test_runtime_backend_exposes_and_updates_slideshow_mode_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    dispatch = create_mainwindow_signal_dispatch(window, ("on_change_slideshow_mode",))
    backend.connect_signals(dispatch)

    assert backend.get_object("radSlideshowModeRandom").get_active() is True
    assert backend.get_object("radSlideshowModeSequential").get_active() is False
    assert backend.get_object("lblSlideshowModeHelp").text == "Random rotates images."

    backend.get_object("radSlideshowModeSequential").click()

    assert window.slideshow_mode == "sequential"
    assert backend.get_object("radSlideshowModeSequential").get_active() is True
    assert backend.get_object("radSlideshowModeRandom").get_active() is False
    assert backend.get_object("lblSlideshowModeHelp").text == "Sequential rotates images."


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
    assert status.text == "Status: ready"
    assert error.text == "Error: none"


def test_runtime_backend_input_change_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    backend.connect_signals({"on_change_input_text": lambda: None})

    entry.set_text("/tmp/example.jpg")
    entry.emit("changed", entry)

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_input_change_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    backend.connect_signals(
        {
            "on_change_input_text": lambda _text: (_ for _ in ()).throw(RuntimeError("input change exploded")),
        }
    )

    entry.set_text("/tmp/example.jpg")

    with pytest.raises(RuntimeError, match="input change exploded"):
        entry.emit("changed", entry)


def test_runtime_backend_optimize_result_controls_apply_button_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    backend.connect_signals({"on_optimize": lambda: True})
    optimize_btn.click()

    assert apply_btn.sensitive is True
    assert status.text == "Status: optimize completed"
    assert error.text == "Error: none"

    backend.connect_signals({"on_optimize": lambda: False})
    optimize_btn.click()

    assert apply_btn.sensitive is False
    assert status.text == "Status: ready"
    assert error.text == "Error: optimize returned false"


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
    assert backend.get_object("boxOptimizeSection") is not None
    assert backend.get_object("btnOptimize") is not None
    assert backend.get_object("boxApplySection") is not None
    assert backend.get_object("btnSetWall") is not None
    assert backend.get_object("boxPreviewSection") is not None
    assert backend.get_object("imgPreviewL") is not None
    assert backend.get_object("imgPreviewR") is not None
    assert backend.get_object("radApplySingle") is not None
    assert backend.get_object("radApplyPerMonitor") is not None
    assert backend.get_object("btnMarginsOptionsMore") is not None
    assert backend.get_object("marginsOptionsDrawer") is not None
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
    assert backend.get_object("lblSlideshowSection") is not None
    assert backend.get_object("lblError") is not None


def test_runtime_backend_current_state_panel_defaults_are_available():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    assert backend.get_object("lblCurrentStateSection").text == "Main Window Current alignment:"


def test_runtime_backend_wires_required_runtime_widget_signals():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    input_left = backend.get_object("entPathL")
    input_right = backend.get_object("entPathR")
    margin_text = backend.get_object("txtMarginText")

    assert "changed" in input_left._signals
    assert "changed" in input_right._signals
    assert "key-press-event" in margin_text._signals
    assert "changed" in margin_text.get_buffer()._signals


def test_runtime_backend_adds_main_margins_drawer_and_syncs_owner_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    window.form_state.embed_info = "combo"
    window.form_state.embed_text = "margin-note"
    window.form_state.embed_position = "right-bottom"
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
    assert len(notebook.pages) == 2
    assert notebook.pages[0][1].text == "Main"
    assert notebook.pages[1][1].text == "Slideshow (stopped)"
    assert backend.get_object("btnMarginsOptionsMore").label == "More margin options…"
    assert backend.get_object("radMarginTextModeBoth").get_active() is True
    assert backend.get_object("txtMarginText").get_text() == "margin-note"
    assert backend.get_object("radMarginTextPositionRightBottom").get_active() is True


def test_runtime_backend_options_drawer_objects_and_toggle():
    from harite.gui.views.margins_options_drawer import FEWER_LABEL, MORE_LABEL, toggle_margins_options_drawer
    from harite.gui.views.slideshow_options_drawer import toggle_slideshow_options_drawer

    backend = GtkRuntimeSignalBackend(_FakeGtk)

    margins_revealer = backend._objects["margins_options_revealer"]
    slideshow_revealer = backend._objects["slideshow_options_revealer"]
    margins_trigger = backend._objects["btn_margins_options_more"]
    slideshow_trigger = backend._objects["btn_slideshow_options_more"]

    assert margins_revealer is not None
    assert slideshow_revealer is not None
    assert not margins_revealer.get_reveal_child()
    assert not slideshow_revealer.get_reveal_child()

    toggle_margins_options_drawer(backend)
    assert margins_revealer.get_reveal_child()
    assert margins_trigger.label == FEWER_LABEL
    toggle_margins_options_drawer(backend)
    assert not margins_revealer.get_reveal_child()
    assert margins_trigger.label == MORE_LABEL

    toggle_slideshow_options_drawer(backend)
    assert slideshow_revealer.get_reveal_child()
    toggle_slideshow_options_drawer(backend)
    assert not slideshow_revealer.get_reveal_child()


def test_runtime_backend_slideshow_tab_uses_centered_page_shell():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    notebook = backend.get_object("commandTabs")
    slideshow_page = notebook.pages[1][0]
    slideshow_tab_box = backend._objects["slideshow_tab_box"]
    assert slideshow_tab_box._parent is not None
    assert slideshow_page is slideshow_tab_box._parent._parent


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

    backend.get_object("spnTopMargin").set_value(24)
    backend.get_object("spnTopMargin").emit("value-changed", backend.get_object("spnTopMargin"))
    backend.get_object("radMarginTextModeText").click()
    backend.get_object("txtMarginText").set_text("hello\nworld")
    backend.get_object("radMarginTextPositionLeftTop").click()

    assert window.form_state.margins == "10,10,24,10"
    assert window.form_state.embed_info == "free"
    assert window.form_state.embed_text == "hello\nworld"
    assert window.form_state.embed_position == "left-top"
    assert backend.get_object("lblStatus").text.startswith("Status: margin text ready in left top position")
    assert backend.get_object("lblError").text == "Error: none"

    preview = window.build_optimize_cli_preview()
    assert "--margins 10,10,24,10" in preview
    assert "--embed-info free" in preview
    assert "--embed-text hello\nworld" in preview
    assert "--embed-position left-top" in preview
    assert "--embed-max-lines" not in preview


def test_runtime_backend_margin_text_mode_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_change_margin_text_mode": lambda: True})
    backend.get_object("radMarginTextModeText").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_margin_text_mode_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_change_margin_text_mode": lambda _value: (_ for _ in ()).throw(RuntimeError("margin text mode exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="margin text mode exploded"):
        backend.get_object("radMarginTextModeText").click()


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


def test_runtime_backend_margin_text_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_change_margin_text": lambda: True})
    backend.get_object("txtMarginText").set_text("hello")

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_margin_text_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_change_margin_text": lambda _value: (_ for _ in ()).throw(RuntimeError("margin text exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="margin text exploded"):
        backend.get_object("txtMarginText").set_text("hello")


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

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: selected margin area is too small for margin text"


def test_runtime_backend_margin_text_position_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_change_margin_text_position": lambda: True})
    backend.get_object("radMarginTextPositionLeftTop").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_margin_text_position_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_change_margin_text_position": lambda _value: (_ for _ in ()).throw(RuntimeError("margin position exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="margin position exploded"):
        backend.get_object("radMarginTextPositionLeftTop").click()


def test_runtime_backend_margin_text_max_lines_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_change_margin_text_max_lines": lambda: True})
    backend.get_object("spnMarginTextMaxLines").emit("value-changed", backend.get_object("spnMarginTextMaxLines"))

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_margin_text_max_lines_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_change_margin_text_max_lines": lambda _value: (_ for _ in ()).throw(RuntimeError("margin max lines exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="margin max lines exploded"):
        backend.get_object("spnMarginTextMaxLines").emit("value-changed", backend.get_object("spnMarginTextMaxLines"))


def test_runtime_backend_margin_text_preflight_uses_two_screen_display_slice_area():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    window.form_state.two_screen = True
    window.form_state.resolution = "3200x1080"
    window.form_state.l_display = "1920x1080"
    window.form_state.r_display = "1280x1024"
    window.form_state.margins = "100,150,80,90"

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_change_margin_text_mode",
            "on_change_margin_text_position",
        ),
    )
    backend.connect_signals(dispatch)

    backend.get_object("radMarginTextModeSettings").click()
    backend.get_object("radMarginTextPositionRightTop").click()

    assert window.form_state.embed_position == "right-top"
    assert backend.get_object("lblStatus").text == "Status: margin text ready in right top position (1030x80)"
    assert backend.get_object("lblError").text == "Error: none"


def test_runtime_backend_syncs_result_preview_from_mainwindow(tmp_path, monkeypatch):
    import harite.apply_surface as apply_surface_mod

    monkeypatch.setattr(apply_surface_mod.platform, "system", lambda: "Linux")
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

    assert Path(backend.get_object("imgPreviewL").file_path).name == "preview.jpg"
    assert Path(backend.get_object("imgPreviewR").file_path).name == "preview.jpg"

    backend.get_object("entPathR").set_text("right.jpg")
    backend.get_object("entPathR").emit("changed", backend.get_object("entPathR"))

    backend.get_object("radApplyPerMonitor").click()

    assert backend.get_object("lblCurrentMargins").text == "margins=0,0,0,0"
    assert backend.get_object("lblCurrentStateL").text == "L: align=center valign=center"
    assert backend.get_object("lblCurrentStateR").text == "R: align=center valign=center"


def test_runtime_backend_shows_current_labels_and_controls():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    do_it = backend.get_object("lblDoItPlanned")
    priority = backend.get_object("lblPriorityRule")
    slideshow_section = backend.get_object("lblSlideshowSection")
    interval = backend.get_object("lblInterval")
    color_btn = backend.get_object("btnSetColor")
    save_path_chooser = backend.get_object("SavePathDialog")
    save_path_state = backend.get_object("lblSavePathState")
    slideshow_start = backend.get_object("btnSlideshowStart")
    slideshow_stop = backend.get_object("btnSlideshowStop")
    pick_state = backend.get_object("lblPickState")
    style_legend = backend.get_object("lblStyleLegend")
    command_section = backend.get_object("lblCommandSection")
    flow_legend = backend.get_object("lblFlowLegend")
    slideshow_source_l = backend.get_object("lblSlideshowSourceL")
    slideshow_source_r = backend.get_object("lblSlideshowSourceR")
    slideshow_current = backend.get_object("lblSlideshowCurrent")
    slideshow_output = backend.get_object("lblSlideshowOutput")
    settings_btn = backend.get_object("btnSetting")
    about_btn = backend.get_object("btnAbout")
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
    btn_get_img_l = backend.get_object("btnGetImgL")

    assert do_it.text == "Apply updates wallpaper immediately"
    assert priority.text == "Rule: margins define area; align/valign act inside it"
    assert slideshow_section.text == ""
    assert interval.text == "Interval"
    assert color_btn.label == "Color"
    assert backend.get_object("btnOpenSave") is None
    assert backend.get_object("btnCancelSave") is None
    assert hasattr(save_path_chooser, "get_filename")
    assert hasattr(save_path_chooser, "set_filename")
    assert save_path_state.text == "Export path: idle"
    assert slideshow_start.label == "Slideshow Start"
    assert slideshow_stop.label == "Slideshow Stop"
    assert slideshow_source_l.text == "L: -"
    assert slideshow_source_r.text == "R: -"
    assert slideshow_current.text == "Slideshow current: idle"
    assert slideshow_output.text == "Slideshow output: ."
    assert pick_state.text == ""
    assert style_legend.text == "Current behavior: margins are global to the composite canvas"
    assert command_section.text == ""
    assert flow_legend.text == "Compose -> Optimize -> Apply"
    assert settings_btn.label == "Settings"
    assert about_btn.label == "About"
    assert color_btn.image is not None
    assert settings_btn.image is not None
    assert about_btn.image is not None
    assert save_btn.label == "Export Image"
    assert save_btn.image is not None
    assert save_btn.image.file_path.endswith("image-down.svg")
    assert optimize_btn.label == "Optimize"
    assert apply_btn.label == "Apply"
    assert tgl_upper_l.label == ""
    assert tgl_upper_r.label == ""
    assert tgl_push_left_l.label == ""
    assert tgl_push_right_l.label == ""
    assert tgl_lower_l.label == ""
    assert tgl_push_left_r.label == ""
    assert tgl_push_right_r.label == ""
    assert tgl_lower_r.label == ""
    assert tgl_upper_l.tooltip_text == "Top alignment-L"
    assert btn_get_img_l.label == ""
    assert btn_get_img_l.tooltip_text == "Open-L"


def test_runtime_backend_slideshow_srcdir_selection_and_slideshow_cycle_updates_labels(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    interval = backend.get_object("spnInterval")
    slideshow_start = backend.get_object("btnSlideshowStart")
    slideshow_stop = backend.get_object("btnSlideshowStop")
    slideshow_source_l = backend.get_object("lblSlideshowSourceL")
    slideshow_source_r = backend.get_object("lblSlideshowSourceR")
    slideshow_current = backend.get_object("lblSlideshowCurrent")
    slideshow_output = backend.get_object("lblSlideshowOutput")
    slideshow_tab_title = backend.get_object("lblSlideshowTabTitle")
    status = backend.get_object("lblStatus")

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_slideshow_srcdir",
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
            "on_slideshow_interval_change",
        ),
    )
    backend.connect_signals(dispatch)
    window.slideshow_mode = "sequential"
    window.form_state.output_dir = str(pictures_root)
    backend._sync_slideshow_state_from_owner(window)

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    assert slideshow_source_l.text == f"L: {left_dir}"
    assert slideshow_source_r.text == "R: -"
    expected_output_label, _ = format_slideshow_output_label_text(str(work_dir))
    assert slideshow_output.text == expected_output_label

    interval.set_value(90)
    interval.emit("value-changed", interval)
    assert status.text == "Status: ready"
    assert slideshow_tab_title.text == "Slideshow (stopped)"

    slideshow_start.click()
    assert status.text == "Status: ready"
    assert slideshow_tab_title.text == "Slideshow (running)"
    assert slideshow_current.text == "Slideshow current: L=left-1.jpg | R=-"

    assert backend.run_slideshow_cycle_once() is True
    assert slideshow_tab_title.text == "Slideshow (running)"
    assert slideshow_current.text == "Slideshow current: L=left-2.jpg | R=-"

    slideshow_stop.click()
    assert status.text == "Status: ready"
    assert slideshow_tab_title.text == "Slideshow (stopped)"
    assert backend.run_slideshow_cycle_once() is False


def test_runtime_backend_slideshow_start_button_requires_both_srcdirs(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    srcdir_r = backend.get_object("btnOpenSrcdirR")
    slideshow_start = backend.get_object("btnSlideshowStart")
    slideshow_stop = backend.get_object("btnSlideshowStop")

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.jpg").write_bytes(b"right")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_slideshow_srcdir",
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
            "on_slideshow_interval_change",
        ),
    )
    backend.connect_signals(dispatch)

    assert slideshow_start.sensitive is False
    assert slideshow_stop.sensitive is False

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    assert slideshow_start.sensitive is False

    srcdir_r.click()
    srcdir_dialog.set_current_folder(str(right_dir))
    srcdir_dialog.confirm()

    assert slideshow_start.sensitive is True


def test_runtime_backend_slideshow_srcdir_confirm_reports_legacy_handler_signature_error(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()

    backend.connect_signals({"on_pick_slideshow_srcdir": lambda: True})

    backend.get_object("btnOpenSrcdirL").click()
    backend.get_object("SrcdirDialog").set_current_folder(str(left_dir))
    backend.get_object("SrcdirDialog").confirm()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_slideshow_srcdir_confirm_propagates_unexpected_runtime_error(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()

    backend.connect_signals(
        {
            "on_pick_slideshow_srcdir": lambda _folder, _side: (_ for _ in ()).throw(RuntimeError("srcdir confirm exploded")),
        }
    )

    backend.get_object("btnOpenSrcdirL").click()
    backend.get_object("SrcdirDialog").set_current_folder(str(left_dir))

    with pytest.raises(RuntimeError, match="srcdir confirm exploded"):
        backend.get_object("SrcdirDialog").confirm()


def test_runtime_backend_connect_signals_syncs_slideshow_output_from_owner(monkeypatch, tmp_path):
    pictures_root, work_dir = _setup_linux_pictures_env(monkeypatch, tmp_path)
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    window.form_state.output_dir = str(pictures_root)

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
            "on_slideshow_interval_change",
        ),
    )
    backend.connect_signals(dispatch)

    expected_output_label, _ = format_slideshow_output_label_text(str(work_dir))
    assert backend.get_object("lblSlideshowOutput").text == expected_output_label


def test_runtime_backend_slideshow_interval_change_uses_integer_contract_without_owner():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    interval = backend.get_object("spnInterval")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {}

    def on_slideshow_interval_change(seconds):
        observed["seconds"] = seconds
        return True

    backend.connect_signals({"on_slideshow_interval_change": on_slideshow_interval_change})

    interval.set_value(75)
    interval.emit("value-changed", interval)

    assert observed == {"seconds": 75}
    assert status.text == "Status: ready"
    assert error.text == "Error: none"


def test_runtime_backend_slideshow_interval_change_reports_legacy_widget_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    interval = backend.get_object("spnInterval")

    backend.connect_signals({"on_slideshow_interval_change": lambda widget, extra: True})

    interval.set_value(75)
    interval.emit("value-changed", interval)

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "required positional argument" in backend.get_object("lblError").text or "positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_slideshow_start_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_slideshow_start": lambda: (_ for _ in ()).throw(RuntimeError("slideshow start exploded"))})

    with pytest.raises(RuntimeError, match="slideshow start exploded"):
        backend.get_object("btnSlideshowStart").click()


def test_runtime_backend_slideshow_stop_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    backend._slideshow_running = True

    backend.connect_signals({"on_slideshow_stop": lambda: (_ for _ in ()).throw(RuntimeError("slideshow stop exploded"))})

    with pytest.raises(RuntimeError, match="slideshow stop exploded"):
        backend.get_object("btnSlideshowStop").click()


def test_runtime_backend_slideshow_tick_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    backend._slideshow_running = True

    backend.connect_signals({"on_slideshow_tick": lambda: (_ for _ in ()).throw(RuntimeError("slideshow tick exploded"))})

    with pytest.raises(RuntimeError, match="slideshow tick exploded"):
        backend.run_slideshow_cycle_once()


def test_runtime_backend_slideshow_start_registers_timer_and_stop_removes_it(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: str) -> bool:
            self.calls.append(path)
            return True

    _FakeGLib.reset()
    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)

    backend = GtkRuntimeSignalBackend(_TimerFakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    interval = backend.get_object("spnInterval")
    slideshow_start = backend.get_object("btnSlideshowStart")
    slideshow_stop = backend.get_object("btnSlideshowStop")
    slideshow_current = backend.get_object("lblSlideshowCurrent")

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_slideshow_srcdir",
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
            "on_slideshow_interval_change",
        ),
    )
    backend.connect_signals(dispatch)
    window.slideshow_mode = "sequential"

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    interval.set_value(45)
    interval.emit("value-changed", interval)

    slideshow_start.click()

    assert backend._slideshow_timer_source_id == 1
    assert _FakeGLib.registered_sources[1]["interval_ms"] == 45000
    assert plugin.calls == [str(left_dir / "left-1.jpg")]

    timer_callback = _FakeGLib.registered_sources[1]["callback"]
    assert timer_callback() is True
    assert slideshow_current.text == "Slideshow current: L=left-2.jpg | R=-"
    assert plugin.calls[-1] == str(left_dir / "left-2.jpg")

    slideshow_stop.click()

    assert backend._slideshow_timer_source_id is None
    assert _FakeGLib.removed_sources == [1]


def test_runtime_backend_slideshow_start_uses_spin_interval_without_value_changed(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    _FakeGLib.reset()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    backend = GtkRuntimeSignalBackend(_TimerFakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    interval = backend.get_object("spnInterval")
    slideshow_start = backend.get_object("btnSlideshowStart")

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_slideshow_srcdir",
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
            "on_slideshow_interval_change",
        ),
    )
    backend.connect_signals(dispatch)
    window.slideshow_interval_seconds = 60

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    interval.set_value(3)

    slideshow_start.click()

    assert window.slideshow_interval_seconds == 3
    assert backend._slideshow_timer_source_id == 1
    assert _FakeGLib.registered_sources[1]["interval_ms"] == 3000


def test_runtime_backend_slideshow_current_abbreviates_long_paths(monkeypatch, tmp_path):
    class DummyPlugin:
        def apply(self, path: str) -> bool:
            return True

    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: DummyPlugin())

    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    slideshow_start = backend.get_object("btnSlideshowStart")
    slideshow_current = backend.get_object("lblSlideshowCurrent")

    left_dir = tmp_path / "google-drive-root" / "My Drive" / "photos"
    left_dir.mkdir(parents=True)
    image_path = left_dir / "wallpaper.jpg"
    image_path.write_bytes(b"left")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_slideshow_srcdir",
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
        ),
    )
    backend.connect_signals(dispatch)

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    slideshow_start.click()

    assert str(image_path) not in slideshow_current.text
    assert "wallpaper.jpg" in slideshow_current.text


def test_runtime_backend_shows_owner_slideshow_start_failure_reason(monkeypatch, tmp_path):
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
    slideshow_start = backend.get_object("btnSlideshowStart")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    slideshow_tab_title = backend.get_object("lblSlideshowTabTitle")

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (right_dir / "right-1.png").write_bytes(b"right")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_slideshow_srcdir",
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
            "on_slideshow_interval_change",
        ),
    )
    backend.connect_signals(dispatch)
    window.slideshow_mode = "sequential"

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()
    srcdir_r.click()
    srcdir_dialog.set_current_folder(str(right_dir))
    srcdir_dialog.confirm()

    slideshow_start.click()

    assert status.text == "Status: ready"
    assert error.text == "Error: dual-source slideshow requires two detected displays"
    assert slideshow_tab_title.text == "Slideshow (stopped)"


def test_runtime_backend_shows_owner_slideshow_tick_failure_reason(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = 0

        def apply(self, path: str) -> bool:
            self.calls += 1
            return self.calls == 1

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    monkeypatch.setattr(MainWindow, "_load_default_settings_on_startup", lambda self: None)

    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    slideshow_start = backend.get_object("btnSlideshowStart")
    slideshow_current = backend.get_object("lblSlideshowCurrent")
    slideshow_tab_title = backend.get_object("lblSlideshowTabTitle")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    left_dir = tmp_path / "slideshow-left"
    left_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_slideshow_srcdir",
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
            "on_slideshow_interval_change",
        ),
    )
    backend.connect_signals(dispatch)
    window.slideshow_mode = "sequential"

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()

    slideshow_start.click()
    assert status.text == "Status: ready"
    assert slideshow_tab_title.text == "Slideshow (running)"

    assert backend.run_slideshow_cycle_once() is False
    assert status.text == "Status: ready"
    assert error.text == "Error: slideshow cycle single-file apply failed"
    assert slideshow_tab_title.text == "Slideshow (stopped)"
    assert slideshow_current.text == "Slideshow current: L=left-2.jpg | R=-"


def test_runtime_backend_slideshow_cycle_pauses_when_detected_displays_temporarily_drop(monkeypatch, tmp_path):
    class DummyPlugin:
        def __init__(self):
            self.calls = []

        def apply(self, path: object) -> bool:
            self.calls.append(path)
            return True

    plugin = DummyPlugin()
    monkeypatch.setattr("harite.gui.views.main_window.plugin_registry.get", lambda _name: plugin)
    monkeypatch.setattr(
        "harite.gui.views.main_window.build_two_screen_optimize_context",
        lambda: TwoScreenOptimizeContext(
            displays=(
                Display(name="HDMI-1", width=1920, height=1080, x_offset=0, y_offset=0),
                Display(name="DP-1", width=1920, height=1080, x_offset=1920, y_offset=0),
            ),
            resolution=(3840, 1080),
            l_display=(1920, 1080),
            r_display=(1920, 1080),
        ),
    )

    composite = tmp_path / "slideshow-composite.jpg"
    composite.write_bytes(b"composite")

    resolve_calls = 0
    optimize_calls = 0

    def fake_run_optimize(state):
        nonlocal optimize_calls
        optimize_calls += 1
        return ([composite], [])

    def fake_resolve_apply_settings(**_kwargs):
        nonlocal resolve_calls
        resolve_calls += 1
        if resolve_calls == 1:
            return EffectiveApplySettings(
                apply_mode="per-monitor-auto-split",
                target={"HDMI-1": str(tmp_path / "split1.jpg"), "DP-1": str(tmp_path / "split2.jpg")},
            )
        raise ValueError("per-monitor apply requires at least two detected displays")

    monkeypatch.setattr("harite.gui.views.main_window.resolve_apply_settings", fake_resolve_apply_settings)

    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    window.plugin_name = "linux"
    monkeypatch.setattr(window.controller, "run_optimize", fake_run_optimize)

    left_dir = tmp_path / "slideshow-left"
    right_dir = tmp_path / "slideshow-right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "left-1.jpg").write_bytes(b"left")
    (left_dir / "left-2.jpg").write_bytes(b"left-2")
    (right_dir / "right-1.png").write_bytes(b"right")
    (right_dir / "right-2.png").write_bytes(b"right-2")

    dispatch = create_mainwindow_signal_dispatch(
        window,
        (
            "on_pick_slideshow_srcdir",
            "on_slideshow_start",
            "on_slideshow_tick",
            "on_slideshow_stop",
        ),
    )
    backend.connect_signals(dispatch)

    srcdir_dialog = backend.get_object("SrcdirDialog")
    srcdir_l = backend.get_object("btnOpenSrcdirL")
    srcdir_r = backend.get_object("btnOpenSrcdirR")
    slideshow_start = backend.get_object("btnSlideshowStart")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    slideshow_tab_title = backend.get_object("lblSlideshowTabTitle")

    srcdir_l.click()
    srcdir_dialog.set_current_folder(str(left_dir))
    srcdir_dialog.confirm()
    srcdir_r.click()
    srcdir_dialog.set_current_folder(str(right_dir))
    srcdir_dialog.confirm()

    slideshow_start.click()
    assert status.text == "Status: ready"
    assert slideshow_tab_title.text == "Slideshow (running)"

    assert backend.run_slideshow_cycle_once() is True
    assert status.text == "Status: ready"
    assert error.text == "Error: none"
    assert slideshow_tab_title.text == "Slideshow (paused)"


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
    assert status.text == "Status: ready"
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


def test_runtime_backend_open_dialog_confirm_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_pick_input": lambda: True})
    backend.get_object("btnGetImgL").click()
    backend.get_object("ImgOpenDialog").set_filename("/tmp/left.jpg")
    backend.get_object("ImgOpenDialog").confirm()

    assert backend.get_object("lblPickState").text == "Open-L: error"
    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_open_dialog_confirm_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_pick_input": lambda _path, _side: (_ for _ in ()).throw(RuntimeError("open confirm exploded")),
        }
    )
    backend.get_object("btnGetImgL").click()
    backend.get_object("ImgOpenDialog").set_filename("/tmp/left.jpg")

    with pytest.raises(RuntimeError, match="open confirm exploded"):
        backend.get_object("ImgOpenDialog").confirm()


def test_runtime_backend_clear_l_clears_only_left_side_and_keeps_right_input():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    entry_l = backend.get_object("entPathL")
    entry_r = backend.get_object("entPathR")
    clear_l = backend.get_object("btnClrPathL")
    optimize_btn = backend.get_object("btnOptimize")
    status = backend.get_object("lblStatus")

    dispatch = create_mainwindow_signal_dispatch(window, ("on_pick_input", "on_change_input_text", "on_clear_input"))
    backend.connect_signals(dispatch)

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
    assert window.form_state.input_value == "/tmp/right-image.jpg"
    assert optimize_btn.sensitive is True
    assert status.text == "Status: ready"


def test_runtime_backend_clear_r_disables_actions_when_last_input_cleared():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()

    entry_r = backend.get_object("entPathR")
    clear_r = backend.get_object("btnClrPathR")
    save_btn = backend.get_object("btnSave")
    optimize_btn = backend.get_object("btnOptimize")

    dispatch = create_mainwindow_signal_dispatch(window, ("on_pick_input", "on_change_input_text", "on_clear_input"))
    backend.connect_signals(dispatch)

    dialog = backend.get_object("ImgOpenDialog")
    backend.get_object("btnGetImgR").click()
    dialog.set_filename("/tmp/right-image.jpg")
    dialog.confirm()

    clear_r.click()

    assert entry_r.get_text() == ""
    assert save_btn.sensitive is False
    assert optimize_btn.sensitive is False


def test_runtime_backend_clear_button_reports_missing_clear_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("btnClrPathL").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: handler not connected"


def test_runtime_backend_clear_button_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_clear_input": lambda: True})
    backend.get_object("btnClrPathL").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_clear_button_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_clear_input": lambda _side: (_ for _ in ()).throw(RuntimeError("clear input exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="clear input exploded"):
        backend.get_object("btnClrPathL").click()


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
    assert status.text == "Status: ready"
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
    assert status.text == "Status: ready"
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


def test_runtime_backend_color_click_opens_dialog():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    color_btn = backend.get_object("btnSetColor")
    color_dialog = backend.get_object("ColorDialog")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    color_btn.click()

    assert color_dialog.is_visible() is True
    assert status.text == "Status: ready"
    assert error.text == "Error: none"


def test_runtime_backend_color_apply_updates_handler_and_feedback():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    observed = {}

    def on_set_color(color=None):
        if color is None:
            return True
        observed["color"] = color
        return True

    backend.connect_signals(
        {
            "on_set_color": on_set_color,
            "on_get_settings": lambda: {"background_color": "#1E1E1E"},
        }
    )

    backend.get_object("btnSetColor").click()
    backend.get_object("entColorValue").set_text("#224466")
    backend.get_object("btnColorApply").click()

    assert observed["color"] == "#224466"
    assert backend.get_object("ColorDialog").is_visible() is False
    assert backend.get_object("lblColorState").text == "Color: #224466"
    assert backend.get_object("lblColorNotice").text == ""
    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: none"


def test_runtime_backend_color_open_reports_settings_getter_failure():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_set_color": lambda *_args: True,
            "on_get_settings": lambda: (_ for _ in ()).throw(RuntimeError("color settings getter failed")),
        }
    )

    backend.get_object("btnSetColor").click()

    assert backend.get_object("ColorDialog").is_visible() is False
    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: color settings getter failed"


def test_runtime_backend_color_open_propagates_unexpected_getter_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_set_color": lambda *_args: True,
            "on_get_settings": lambda: (_ for _ in ()).throw(LookupError("unexpected color getter error")),
        }
    )

    with pytest.raises(LookupError, match="unexpected color getter error"):
        backend.get_object("btnSetColor").click()


def test_runtime_backend_color_open_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_set_color": lambda *_args: (_ for _ in ()).throw(RuntimeError("color open exploded")),
            "on_get_settings": lambda: {"background_color": "#1E1E1E"},
        }
    )

    with pytest.raises(RuntimeError, match="color open exploded"):
        backend.get_object("btnSetColor").click()


def test_runtime_backend_color_apply_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_set_color": lambda color=None: (_ for _ in ()).throw(RuntimeError("color apply exploded")) if color is not None else True,
            "on_get_settings": lambda: {"background_color": "#1E1E1E"},
        }
    )

    backend.get_object("btnSetColor").click()
    backend.get_object("entColorValue").set_text("#224466")

    with pytest.raises(RuntimeError, match="color apply exploded"):
        backend.get_object("btnColorApply").click()


def test_runtime_backend_color_apply_shows_invalid_color_feedback():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    window = MainWindow()
    backend.connect_signals(create_mainwindow_signal_dispatch(window, ("on_set_color",)))

    backend.get_object("btnSetColor").click()
    backend.get_object("entColorValue").set_text("hoge")
    backend.get_object("btnColorApply").click()

    assert backend.get_object("ColorDialog").is_visible() is True
    assert backend.get_object("lblColorState").text == "Color: #1E1E1E"
    assert backend.get_object("lblColorNotice").text == "Color: invalid background color"
    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: none"


def test_runtime_backend_color_pick_button_updates_pending_color(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.adapters.gtk_runtime_dialogs.ColorDialogProxy._load_gdk_module",
        lambda self: type("_FakeGdk", (), {"RGBA": _FakeRgba}),
    )
    monkeypatch.setattr(
        "harite.gui.adapters.gtk_runtime_dialogs.ColorDialogProxy.supports_native_dialog",
        lambda self: False,
    )
    _NativeColorChooserDialog.next_response = _NativeResponseType.OK
    _NativeColorChooserDialog.next_hex_text = "#224466"

    backend = GtkRuntimeSignalBackend(_NativeColorFakeGtk)

    backend.get_object("btnSetColor").click()
    backend.get_object("btnColorPick").click()

    assert backend.get_object("ColorDialog").is_visible() is True
    assert backend.get_object("entColorValue").get_text() == "#224466"
    assert backend.get_object("lblColorState").text == "Color: #224466"
    assert backend.get_object("lblColorNotice").text == ""


def test_runtime_backend_color_open_uses_embedded_chooser_with_reserved_notice_row(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.adapters.gtk_runtime_dialogs.ColorDialogProxy._load_gdk_module",
        lambda self: type("_FakeGdk", (), {"RGBA": _FakeRgba}),
    )
    _NativeColorChooserDialog.last_created = None

    backend = GtkRuntimeSignalBackend(_EmbeddedNativeColorFakeGtk)

    backend.get_object("btnSetColor").click()

    color_dialog = backend.get_object("ColorDialog")
    assert color_dialog.is_visible() is True
    assert _NativeColorChooserDialog.last_created is None
    assert color_dialog._embedded_color_chooser is not None
    assert backend.get_object("btnColorPick").sensitive is False
    assert color_dialog._window.child.children[-2] is backend.get_object("lblColorState")
    assert color_dialog._window.child.children[-1] is backend.get_object("lblColorNotice")

    chooser = color_dialog._embedded_color_chooser
    rgba = _FakeRgba()
    rgba.red = 0x22 / 255.0
    rgba.green = 0x44 / 255.0
    rgba.blue = 0x66 / 255.0
    chooser.set_rgba(rgba)

    assert backend.get_object("entColorValue").get_text() == "#224466"


def test_color_dialog_proxy_gdk_probe_propagates_unexpected_runtime_error(monkeypatch):
    def fake_import_module(name):
        if name == "gi":
            raise RuntimeError("gdk probe failed")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    with pytest.raises(RuntimeError, match="gdk probe failed"):
        ColorDialogProxy()._load_gdk_module()


def test_color_dialog_proxy_native_hex_sync_propagates_unexpected_rgba_conversion_failure(monkeypatch):
    color_dialog = ColorDialogProxy()
    entry = _Entry()

    class _Dialog:
        def get_rgba(self):
            return object()

    monkeypatch.setattr(color_dialog, "_color_from_rgba", lambda _rgba: (_ for _ in ()).throw(RuntimeError("rgba sync failed")))

    with pytest.raises(RuntimeError, match="rgba sync failed"):
        color_dialog._sync_native_hex_entry_from_dialog(_Dialog(), entry)


def test_color_dialog_proxy_embedded_chooser_change_propagates_unexpected_rgba_conversion_failure(monkeypatch):
    color_dialog = ColorDialogProxy(entry=_Entry())

    class _Chooser:
        def get_rgba(self):
            return object()

    monkeypatch.setattr(color_dialog, "_color_from_rgba", lambda _rgba: (_ for _ in ()).throw(RuntimeError("embedded rgba sync failed")))

    with pytest.raises(RuntimeError, match="embedded rgba sync failed"):
        color_dialog._on_embedded_color_chooser_changed(_Chooser())


def test_color_dialog_proxy_native_hex_change_propagates_unexpected_set_rgba_failure(monkeypatch):
    color_dialog = ColorDialogProxy()

    class _Dialog:
        def set_rgba(self, _rgba):
            raise RuntimeError("native set_rgba failed")

    entry = _Entry()
    entry.set_text("#224466")
    monkeypatch.setattr(color_dialog, "_rgba_from_color", lambda _color: object())

    with pytest.raises(RuntimeError, match="native set_rgba failed"):
        color_dialog._on_native_hex_entry_changed(_Dialog(), entry)


def test_color_dialog_proxy_internal_vbox_probe_allows_signature_mismatch_fallback():
    class _Buildable:
        @staticmethod
        def get_internal_child(_dialog, _builder, _name):
            raise TypeError("signature mismatch")

    class _Gtk:
        Buildable = _Buildable

    class _Dialog:
        def get_internal_child(self, name):
            if name == "vbox":
                return "vbox-child"
            return None

    color_dialog = ColorDialogProxy()

    assert color_dialog._get_dialog_internal_vbox(_Gtk, _Dialog()) == "vbox-child"


def test_color_dialog_proxy_internal_vbox_probe_propagates_unexpected_runtime_error():
    class _Buildable:
        @staticmethod
        def get_internal_child(_dialog, _builder, _name):
            raise RuntimeError("internal child probe failed")

    class _Gtk:
        Buildable = _Buildable

    color_dialog = ColorDialogProxy()

    with pytest.raises(RuntimeError, match="internal child probe failed"):
        color_dialog._get_dialog_internal_vbox(_Gtk, object())


def test_color_dialog_proxy_get_parent_widget_allows_signature_mismatch_fallback():
    class _Widget:
        def get_parent(self):
            raise TypeError("signature mismatch")

    color_dialog = ColorDialogProxy()

    assert color_dialog._get_parent_widget(_Widget()) is None


def test_color_dialog_proxy_get_parent_widget_propagates_unexpected_runtime_error():
    class _Widget:
        def get_parent(self):
            raise RuntimeError("parent probe failed")

    color_dialog = ColorDialogProxy()

    with pytest.raises(RuntimeError, match="parent probe failed"):
        color_dialog._get_parent_widget(_Widget())


def test_apply_margin_text_widget_style_allows_expected_import_failure(monkeypatch):
    monkeypatch.setattr("importlib.import_module", lambda _name: (_ for _ in ()).throw(ImportError("gdk unavailable")))

    apply_margin_text_widget_style(object(), object(), object())


def test_apply_margin_text_widget_style_propagates_unexpected_runtime_error(monkeypatch):
    def fake_import_module(name):
        if name == "gi":
            raise RuntimeError("style probe failed")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    with pytest.raises(RuntimeError, match="style probe failed"):
        apply_margin_text_widget_style(object(), object(), object())


def test_on_margin_text_key_press_allows_expected_import_failure(monkeypatch):
    monkeypatch.setattr("importlib.import_module", lambda _name: (_ for _ in ()).throw(ImportError("gdk unavailable")))

    event = type("_Event", (), {"keyval": 13})()

    assert on_margin_text_key_press(_TextView(), event) is False


def test_on_margin_text_key_press_propagates_unexpected_runtime_error(monkeypatch):
    def fake_import_module(name):
        if name == "gi":
            raise RuntimeError("key press probe failed")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    event = type("_Event", (), {"keyval": 13})()

    with pytest.raises(RuntimeError, match="key press probe failed"):
        on_margin_text_key_press(_TextView(), event)


def test_get_glib_module_allows_expected_import_failure(monkeypatch):
    backend = type("_Backend", (), {"_gtk": object()})()
    monkeypatch.setattr("importlib.import_module", lambda _name: (_ for _ in ()).throw(ImportError("glib unavailable")))

    assert get_glib_module(backend) is None


def test_get_glib_module_propagates_unexpected_runtime_error(monkeypatch):
    backend = type("_Backend", (), {"_gtk": object()})()

    def fake_import_module(name):
        if name == "gi":
            raise RuntimeError("glib probe failed")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    with pytest.raises(RuntimeError, match="glib probe failed"):
        get_glib_module(backend)


def test_load_gtk_runtime_signal_backend_propagates_unexpected_runtime_error(monkeypatch):
    def fake_import_module(name):
        if name == "gi":
            raise RuntimeError("gtk backend probe failed")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    with pytest.raises(RuntimeError, match="gtk backend probe failed"):
        load_gtk_runtime_signal_backend()


def test_present_gtk_window_propagates_unexpected_runtime_error(monkeypatch):
    def fake_import_module(name):
        if name == "gi":
            raise RuntimeError("gtk runtime probe failed")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    with pytest.raises(RuntimeError, match="gtk runtime probe failed"):
        present_gtk_window(object())


def test_present_gtk_window_uses_loaded_gtk_module_main(monkeypatch):
    class _FakeGiModule:
        @staticmethod
        def require_version(name, version):
            assert name == "Gtk"
            assert version == "3.0"

    class _FakeGtkModule:
        main_calls = 0
        main_quit_calls = 0

        @classmethod
        def main(cls):
            cls.main_calls += 1

        @classmethod
        def main_quit(cls):
            cls.main_quit_calls += 1

    class _FakeWindow:
        def __init__(self):
            self._signals = {}
            self._harite_quit_hooked = False
            self.show_all_calls = 0
            self.present_calls = 0

        def connect(self, name, callback):
            self._signals[name] = callback

        def show_all(self):
            self.show_all_calls += 1

        def present(self):
            self.present_calls += 1

    window = _FakeWindow()

    class _FakeBackend:
        def get_object(self, name):
            if name == "main_window":
                return window
            return None

    def fake_import_module(name):
        if name == "gi":
            return _FakeGiModule()
        if name == "gi.repository.Gtk":
            return _FakeGtkModule
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    assert present_gtk_window(_FakeBackend()) is True
    assert _FakeGtkModule.main_calls == 1
    assert window.show_all_calls == 1
    assert window.present_calls == 1
    assert "delete-event" in window._signals

    window._signals["delete-event"]()

    assert _FakeGtkModule.main_quit_calls == 1


def test_format_input_display_uses_basename_and_truncates_long_names():
    display = format_input_display("/tmp/Higashiyama-Kaii-Cho-Long-Long-Long-700x1244.jpg")

    assert display.startswith("Higashiyama-Kaii-")
    assert display.endswith("700x1244.jpg")
    assert len(display) <= 36


def test_runtime_backend_about_click_opens_dialog():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_about": lambda: True,
            "on_get_about_dialog_info": lambda: {
                "app_name": "Harite",
                "version": "0.1.2",
                "description": "壁紙最適化ツール（リファクタリング版）",
                "credits": "Created by oggy8021",
                "license_name": "MIT License",
            },
        }
    )

    backend.get_object("btnAbout").click()

    assert backend.get_object("AboutDialog").is_visible() is True
    assert backend.get_object("lblAboutTitle").text == "Harite"
    assert backend.get_object("lblAboutVersion").text == "Version: 0.1.2"
    assert backend.get_object("lblStatus").text == "Status: ready"


def test_runtime_backend_about_open_reports_info_getter_failure():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_about": lambda: True,
            "on_get_about_dialog_info": lambda: (_ for _ in ()).throw(RuntimeError("about info getter failed")),
        }
    )

    backend.get_object("btnAbout").click()

    assert backend.get_object("AboutDialog").is_visible() is False
    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: about info getter failed"


def test_runtime_backend_about_open_propagates_unexpected_getter_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_about": lambda: True,
            "on_get_about_dialog_info": lambda: (_ for _ in ()).throw(LookupError("unexpected about getter error")),
        }
    )

    with pytest.raises(LookupError, match="unexpected about getter error"):
        backend.get_object("btnAbout").click()


def test_runtime_backend_about_open_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_about": lambda: (_ for _ in ()).throw(RuntimeError("about open exploded")),
            "on_get_about_dialog_info": lambda: {
                "app_name": "Harite",
                "version": "0.1.2",
                "description": "壁紙最適化ツール（リファクタリング版）",
                "credits": "Created by oggy8021",
                "license_name": "MIT License",
            },
        }
    )

    with pytest.raises(RuntimeError, match="about open exploded"):
        backend.get_object("btnAbout").click()


def test_runtime_backend_color_confirm_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_set_color": lambda _color=None: (_ for _ in ()).throw(RuntimeError("color confirm exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="color confirm exploded"):
        backend._on_color_dialog_confirmed("#224466")


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
    assert save_path_state.text == "Export path: saved"
    assert save_target.text == "Export target: /tmp/from-runtime-dialog.jpg"
    assert status.text == "Status: ready"
    assert error.text == "Error: none"


def test_runtime_backend_native_save_path_chooser_confirm_runs_modal_flow():
    backend = GtkRuntimeSignalBackend(_NativeFakeGtk)

    save_path_state = backend.get_object("lblSavePathState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"save": 0, "confirm": None, "cancel": 0}

    def on_save_as():
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
            "on_save_as": on_save_as,
            "on_save_path_selected": on_open_save,
            "on_save_path_selection_canceled": on_cancel_save,
        }
    )

    backend.get_object("btnSave").click()

    assert observed == {"save": 1, "confirm": "/tmp/native-save.jpg", "cancel": 0}
    assert save_path_state.text == "Export path: saved"
    assert status.text == "Status: ready"
    assert error.text == "Error: none"
    assert _NativeFileChooserDialog.last_created is not None
    assert _NativeFileChooserDialog.last_created.title == "Export Image"
    assert _NativeFileChooserDialog.last_created.action == _NativeFakeGtk.FileChooserAction.SAVE
    assert _NativeFileChooserDialog.last_created.overwrite_confirmation is True
    assert _NativeFileChooserDialog.last_created.current_name == "harite-output.jpg"


def test_runtime_backend_native_save_path_chooser_cancel_does_not_continue_save_flow():
    backend = GtkRuntimeSignalBackend(_NativeFakeGtk)

    save_path_state = backend.get_object("lblSavePathState")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    observed = {"save": 0, "confirm": 0, "cancel": 0}

    def on_save_as():
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
            "on_save_as": on_save_as,
            "on_save_path_selected": on_open_save,
            "on_save_path_selection_canceled": on_cancel_save,
        }
    )

    backend.get_object("btnSave").click()

    assert observed == {"save": 1, "confirm": 0, "cancel": 1}
    assert save_path_state.text == "Export path: canceled"
    assert status.text == "Status: ready"
    assert error.text == "Error: none"


def test_runtime_backend_save_click_handler_failure_surfaces_feedback():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    def on_save_as():
        raise RuntimeError("save path open failed")

    backend.connect_signals({"on_save_as": on_save_as})

    backend.get_object("btnSave").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: save path open failed"
    assert backend.get_object("SavePathDialog").is_visible() is False


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
    assert save_path_state.text == "Export path: saved"
    assert save_target.text.endswith("harite-output.jpg")
    assert save_target.text.startswith("Export target: ")
    assert status.text == "Status: ready"
    assert error.text == "Error: none"


def test_runtime_backend_save_path_confirm_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_save_path_selected": lambda: True})

    backend.get_object("SavePathDialog").set_filename("/tmp/from-runtime-dialog.jpg")
    backend.get_object("btnSave").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_save_path_confirm_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_save_path_selected": lambda _path: (_ for _ in ()).throw(RuntimeError("save path confirm exploded")),
        }
    )

    backend.get_object("SavePathDialog").set_filename("/tmp/from-runtime-dialog.jpg")

    with pytest.raises(RuntimeError, match="save path confirm exploded"):
        backend.get_object("btnSave").click()


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
    assert save_path_state.text == "Export path: canceled"
    assert status.text == "Status: ready"
    assert error.text == "Error: none"


def test_runtime_backend_save_path_cancel_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_NativeFakeGtk)

    _NativeFileChooserDialog.next_response = _NativeFakeGtk.ResponseType.CANCEL
    _NativeFileChooserDialog.next_filename = ""
    backend.connect_signals({"on_save_path_selection_canceled": lambda _arg: True})

    backend.get_object("btnSave").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "required positional argument" in backend.get_object("lblError").text or "positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_save_path_cancel_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_NativeFakeGtk)

    _NativeFileChooserDialog.next_response = _NativeFakeGtk.ResponseType.CANCEL
    _NativeFileChooserDialog.next_filename = ""
    backend.connect_signals(
        {
            "on_save_path_selection_canceled": lambda: (_ for _ in ()).throw(RuntimeError("save path cancel exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="save path cancel exploded"):
        backend.get_object("btnSave").click()


def test_runtime_backend_save_path_chooser_filename_change_updates_target_label():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_path_chooser = backend.get_object("SavePathDialog")
    save_path_state = backend.get_object("lblSavePathState")
    save_target = backend.get_object("lblSaveTarget")

    save_path_chooser.show()
    save_path_chooser.set_filename("/tmp/selected.jpg")

    assert save_path_state.text == "Export path: ready"
    assert save_target.text == "Export target: /tmp/selected.jpg"


def test_runtime_backend_prefers_save_path_dialog_close_handler_name():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    observed = {"destroy": 0}

    def on_destroy() -> None:
        observed["destroy"] += 1

    backend.connect_signals(
        {
            "on_save_path_selected": lambda _path: True,
            "on_close_save_path_dialog": on_destroy,
        }
    )

    backend.get_object("SavePathDialog").set_filename("/tmp/from-save-path-destroy.jpg")
    backend.get_object("btnSave").click()

    assert observed["destroy"] == 1


def test_runtime_backend_save_path_destroy_callback_exception_propagates():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_close_save_path_dialog": lambda: (_ for _ in ()).throw(RuntimeError("save-path close failed")),
        }
    )

    with pytest.raises(RuntimeError, match="save-path close failed"):
        backend._notify_save_path_dialog_destroy()


def test_runtime_backend_srcdir_destroy_callback_exception_propagates():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_close_srcdir_dialog": lambda: (_ for _ in ()).throw(RuntimeError("srcdir close failed")),
        }
    )

    with pytest.raises(RuntimeError, match="srcdir close failed"):
        backend._notify_srcdir_dialog_destroy()


def test_runtime_backend_open_dialog_destroy_callback_exception_propagates():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_close_open_image_dialog": lambda: (_ for _ in ()).throw(RuntimeError("open-dialog close failed")),
        }
    )

    with pytest.raises(RuntimeError, match="open-dialog close failed"):
        notify_open_dialog_destroy(backend)


def test_runtime_backend_settings_close_callback_exception_propagates():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_close_settings_dialog": lambda: (_ for _ in ()).throw(RuntimeError("settings close failed")),
        }
    )

    with pytest.raises(RuntimeError, match="settings close failed"):
        backend._on_settings_close_clicked()


def test_runtime_backend_about_close_callback_exception_propagates():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_close_about_dialog": lambda: (_ for _ in ()).throw(RuntimeError("about close failed")),
        }
    )

    with pytest.raises(RuntimeError, match="about close failed"):
        backend._on_about_dialog_close_clicked()


def test_runtime_backend_color_close_callback_exception_propagates():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_close_color_dialog": lambda: (_ for _ in ()).throw(RuntimeError("color close failed")),
        }
    )

    with pytest.raises(RuntimeError, match="color close failed"):
        backend._on_color_dialog_cancel_clicked()


def test_runtime_backend_apply_success_updates_footer():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_optimize": lambda: True})
    backend.connect_signals({"on_apply": lambda: True})

    optimize_btn.click()
    apply_btn.click()

    assert status.text == "Status: wallpaper applied"
    assert error.text == "Error: none"


def test_runtime_backend_apply_mode_defaults_to_single_file(monkeypatch):
    monkeypatch.setattr("harite.gui.adapters.gtk_backend.sys.platform", "linux")
    monkeypatch.setattr("harite.apply_surface.platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "harite.workspace.detect_displays",
        lambda: [Display(name="L", width=1920, height=1080, x_offset=0)],
    )
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    assert backend.get_object("radApplySingle").label == "No Split"
    assert backend.get_object("radApplyPerMonitor").label == "Auto-Split"
    from harite.apply_surface import apply_mode_help_text

    assert backend.get_object("radApplySingle").get_active() is True
    assert backend.get_object("radApplyPerMonitor").get_active() is False
    assert backend.get_object("radApplySingle").tooltip_text == apply_mode_help_text("single-file")


def test_runtime_backend_apply_mode_toggle_dispatches_and_updates_label(monkeypatch):
    monkeypatch.setattr("harite.apply_surface.platform.system", lambda: "Linux")
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    observed = {}

    backend.connect_signals({"on_change_apply_mode": lambda mode: observed.setdefault("mode", mode) or True})

    backend.get_object("radApplyPerMonitor").click()

    from harite.apply_surface import apply_mode_help_text

    assert observed["mode"] == "per-monitor-auto-split"
    assert backend.get_object("radApplyPerMonitor").tooltip_text == apply_mode_help_text(
        "per-monitor-auto-split"
    )
    assert backend.get_object("lblStatus").text == "Status: ready"


def test_runtime_backend_apply_mode_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_change_apply_mode": lambda: True})

    backend.get_object("radApplyPerMonitor").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 0 positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_apply_mode_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_change_apply_mode": lambda _mode: (_ for _ in ()).throw(RuntimeError("apply mode exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="apply mode exploded"):
        backend.get_object("radApplyPerMonitor").click()


def test_runtime_backend_apply_mode_can_return_to_default_from_per_monitor(monkeypatch):
    monkeypatch.setattr("harite.apply_surface.platform.system", lambda: "Linux")
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    observed = []

    backend.connect_signals({"on_change_apply_mode": lambda mode: observed.append(mode) or True})

    backend.get_object("radApplyPerMonitor").click()
    backend.get_object("radApplySingle").click()

    from harite.apply_surface import apply_mode_help_text

    assert observed == ["per-monitor-auto-split", "single-file"]
    assert backend.get_object("radApplySingle").tooltip_text == apply_mode_help_text("single-file")


def test_runtime_backend_cross_layout_places_top_and_bottom_per_side():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    compose_grid = backend.get_object("composeGrid")
    left_col = backend.get_object("leftDisplayCol")
    right_col = backend.get_object("rightDisplayCol")

    assert compose_grid.children == [
        (left_col._parent, 0, 0, 1, 1),
        (backend.get_object("lblPickState")._parent, 1, 0, 1, 1),
        (right_col._parent, 2, 0, 1, 1),
    ]

    assert backend.get_object("actionClusterRow") in backend.get_object("boxMainSection").children

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


def test_runtime_backend_settings_button_dispatches_open_handler(monkeypatch, tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    observed = {"opened": 0}
    export_path = tmp_path / "settings-not-saved-yet.json"
    monkeypatch.setattr(
        "harite.gui.adapters.gtk_runtime_settings_dialogs.resolve_default_settings_path",
        lambda: export_path,
    )

    backend.connect_signals(
        {
            "on_open_settings_dialog": lambda: observed.__setitem__("opened", observed["opened"] + 1) or True,
            "on_get_settings": lambda: {"plugin": "linux", "apply_mode": "single-file"},
        }
    )

    backend.get_object("btnSettings").click()

    assert observed["opened"] == 1
    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("SettingsDialog").is_visible() is True
    assert backend.get_object("SettingsDialog").get_settings()["plugin"] == "linux"
    assert backend.get_object("entSettingsPlugin").get_text() == "linux"
    assert backend.get_object("radSettingsApplySingle").label == "Apply Default"
    assert backend.get_object("radSettingsApplyPerMonitor").label == "Apply Auto-split"
    assert backend.get_object("radSettingsApplySingle").get_active() is True
    assert backend.get_object("lblSettingsNotice").text == "現在は未保存です"


def test_runtime_backend_settings_open_reports_notice_build_failure(monkeypatch):
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    class _BrokenPath:
        def exists(self):
            raise RuntimeError("settings path probe failed")

    monkeypatch.setattr(
        "harite.gui.adapters.gtk_runtime_settings_dialogs.resolve_default_settings_path",
        lambda: _BrokenPath(),
    )

    backend.connect_signals(
        {
            "on_open_settings_dialog": lambda: True,
            "on_get_settings": lambda: {"plugin": "linux", "apply_mode": "single-file"},
        }
    )

    backend.get_object("btnSettings").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: settings path probe failed"


def test_runtime_backend_settings_open_propagates_unexpected_notice_build_error(monkeypatch):
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    class _BrokenPath:
        def exists(self):
            raise LookupError("unexpected settings path probe error")

    monkeypatch.setattr(
        "harite.gui.adapters.gtk_runtime_settings_dialogs.resolve_default_settings_path",
        lambda: _BrokenPath(),
    )

    backend.connect_signals(
        {
            "on_open_settings_dialog": lambda: True,
            "on_get_settings": lambda: {"plugin": "linux", "apply_mode": "single-file"},
        }
    )

    with pytest.raises(LookupError, match="unexpected settings path probe error"):
        backend.get_object("btnSettings").click()


def test_runtime_backend_settings_open_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_open_settings_dialog": lambda: (_ for _ in ()).throw(RuntimeError("settings open exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="settings open exploded"):
        backend.get_object("btnSettings").click()


def test_runtime_backend_settings_ok_save_and_cancel_dispatch_handlers(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")
    save_btn = backend.get_object("btnSettingsSave")
    observed = {"apply": None, "save": None, "close": 0}

    assert save_btn.image is not None
    assert save_btn.label == "Save Settings"
    assert save_btn.image.file_path.endswith("save.svg")

    export_path = tmp_path / "save-settings.json"
    dialog.set_settings(
        {
            "resolution": "1920x1080",
            "plugin": "linux",
            "apply_mode": "single-file",
            "slideshow_interval_seconds": 60,
            "slideshow_srcdir_l": "/slideshow/left",
        }
    )
    dialog.set_export_path(str(export_path))
    dialog.show()

    backend.connect_signals(
        {
            "on_apply_settings": lambda settings: observed.__setitem__("apply", settings) or True,
            "on_save_settings_file": lambda path, settings: observed.__setitem__("save", (path, settings)) or True,
            "on_get_settings": lambda: {"plugin": "xfce", "apply_mode": "per-monitor-auto-split"},
            "on_close_settings_dialog": lambda: observed.__setitem__("close", observed["close"] + 1) or True,
        }
    )

    backend.get_object("entSettingsResolution").set_text("auto")
    backend.get_object("entSettingsPlugin").set_text("xfce")
    backend.get_object("radSettingsTwoScreenAuto").set_active(True)
    backend.get_object("radSettingsTwoScreenOn").set_active(False)
    backend.get_object("radSettingsTwoScreenOff").set_active(False)
    backend.get_object("radSettingsApplySingle").set_active(False)
    backend.get_object("radSettingsApplyPerMonitor").set_active(True)

    backend.get_object("btnSettingsOk").click()
    assert observed["apply"]["resolution"] == "auto"
    assert observed["apply"]["two_screen"] == "auto"
    assert observed["apply"]["align"] == ["center", "center"]
    assert observed["apply"]["valign"] == ["center", "center"]
    assert observed["apply"]["plugin"] == "xfce"
    assert observed["apply"]["apply_mode"] == "per-monitor-auto-split"
    assert observed["apply"]["slideshow_interval_seconds"] == 60
    assert observed["apply"]["slideshow_srcdir_l"] == "/slideshow/left"
    assert dialog.is_visible() is False
    assert backend.get_object("lblSettingsState").text == "Settings: current values"
    assert backend.get_object("lblStatus").text == "Status: ready"

    dialog.show()
    backend.get_object("lblSettingsState").set_text("Settings: current values")

    backend.get_object("entSettingsPlugin").set_text("saved-plugin")

    backend.get_object("btnSettingsSave").click()
    assert observed["save"][0] == str(export_path)
    assert observed["save"][1]["plugin"] == "saved-plugin"
    assert observed["save"][1]["slideshow_interval_seconds"] == 60
    assert observed["save"][1]["slideshow_srcdir_l"] == "/slideshow/left"
    assert backend.get_object("lblSettingsState").text == "Settings: current values"
    assert backend.get_object("lblSettingsNotice").text == "Settings: saved"

    backend.get_object("btnSettingsCancel").click()
    assert observed["close"] == 1
    assert dialog.is_visible() is False
    assert backend.get_object("lblSettingsNotice").text == ""


def test_runtime_backend_settings_apply_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")

    dialog.set_settings({"plugin": "linux", "apply_mode": "single-file"})
    dialog.show()

    backend.connect_signals(
        {
            "on_apply_settings": lambda _settings: (_ for _ in ()).throw(RuntimeError("settings apply exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="settings apply exploded"):
        backend.get_object("btnSettingsOk").click()


def test_runtime_backend_settings_save_reports_legacy_handler_signature_error(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")

    export_path = tmp_path / "save-settings.json"
    dialog.set_settings({"plugin": "linux", "apply_mode": "single-file"})
    dialog.set_export_path(str(export_path))
    dialog.show()

    backend.connect_signals(
        {
            "on_save_settings_file": lambda path: True,
        }
    )

    backend.get_object("btnSettingsSave").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "takes 1 positional argument" in backend.get_object("lblError").text


def test_runtime_backend_settings_save_propagates_unexpected_runtime_error(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")

    export_path = tmp_path / "save-settings.json"
    dialog.set_settings({"plugin": "linux", "apply_mode": "single-file"})
    dialog.set_export_path(str(export_path))
    dialog.show()

    backend.connect_signals(
        {
            "on_save_settings_file": lambda _path, _settings: (_ for _ in ()).throw(RuntimeError("settings save exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="settings save exploded"):
        backend.get_object("btnSettingsSave").click()


def test_runtime_backend_settings_preserves_explicit_apply_mode_when_unedited(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")
    observed = {"apply": None, "save": None}

    export_path = tmp_path / "explicit-save.json"
    dialog.set_settings(
        {
            "plugin": "linux",
            "apply_mode": "per-monitor-explicit",
        }
    )
    dialog.set_export_path(str(export_path))
    dialog.show()

    backend.connect_signals(
        {
            "on_open_settings_dialog": lambda: True,
            "on_apply_settings": lambda settings: observed.__setitem__("apply", settings) or True,
            "on_save_settings_file": lambda path, settings: observed.__setitem__("save", (path, settings)) or True,
            "on_get_settings": lambda: {"plugin": "linux", "apply_mode": "per-monitor-explicit"},
        }
    )

    backend.get_object("btnSettings").click()

    assert backend.get_object("radSettingsApplySingle").get_active() is False
    assert backend.get_object("radSettingsApplyPerMonitor").get_active() is False

    backend.get_object("btnSettingsOk").click()
    assert observed["apply"]["apply_mode"] == "per-monitor-explicit"

    dialog.show()
    backend.get_object("btnSettingsSave").click()
    assert observed["save"][0] == str(export_path)
    assert observed["save"][1]["apply_mode"] == "per-monitor-explicit"


def test_runtime_backend_settings_can_override_preserved_explicit_apply_mode(tmp_path):
    backend = GtkRuntimeSignalBackend(_FakeGtk)
    dialog = backend.get_object("SettingsDialog")
    observed = {"apply": None}

    dialog.set_settings(
        {
            "plugin": "linux",
            "apply_mode": "per-monitor-explicit",
        }
    )
    dialog.show()

    backend.connect_signals(
        {
            "on_open_settings_dialog": lambda: True,
            "on_apply_settings": lambda settings: observed.__setitem__("apply", settings) or True,
            "on_get_settings": lambda: {"plugin": "linux", "apply_mode": "per-monitor-explicit"},
        }
    )
    backend.get_object("btnSettings").click()
    backend.get_object("radSettingsApplyPerMonitor").click()
    backend.get_object("btnSettingsOk").click()

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

    assert observed["status_when_called"] == "Status: ready"


def test_runtime_backend_optimize_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_optimize": lambda _arg: True})
    backend.get_object("btnOptimize").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "required positional argument" in backend.get_object("lblError").text or "positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_optimize_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_optimize": lambda: (_ for _ in ()).throw(RuntimeError("optimize exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="optimize exploded"):
        backend.get_object("btnOptimize").click()


def test_runtime_backend_apply_failure_updates_error_message():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_apply": lambda: False})
    apply_btn.click()

    assert status.text == "Status: ready"
    assert error.text == "Error: apply returned false"


def test_runtime_backend_apply_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_apply": lambda _arg: True})
    backend.get_object("btnSetWall").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "required positional argument" in backend.get_object("lblError").text or "positional arguments" in backend.get_object("lblError").text


def test_runtime_backend_apply_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_apply": lambda: (_ for _ in ()).throw(RuntimeError("apply exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="apply exploded"):
        backend.get_object("btnSetWall").click()


def test_runtime_backend_optimize_handler_missing_sets_status_and_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    optimize_btn.click()

    assert status.text == "Status: ready"
    assert error.text == "Error: handler not connected"


def test_runtime_backend_save_button_skips_optimize_handler_and_reports_missing_path_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_btn = backend.get_object("btnSave")
    save_path_chooser = backend.get_object("SavePathDialog")
    save_path_state = backend.get_object("lblSavePathState")
    status = backend.get_object("lblStatus")
    calls = []

    backend.connect_signals({
        "on_save_as": lambda: calls.append("save") or True,
        "on_optimize": lambda: calls.append("optimize") or False,
    })

    save_btn.click()

    assert calls == ["save"]
    assert save_path_chooser.is_visible() is False
    assert save_path_state.text == "Export path: idle"
    assert status.text == "Status: ready"


def test_runtime_backend_optimize_button_does_not_fallback_to_save_handler():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnOptimize")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    calls = []

    backend.connect_signals({
        "on_save": lambda: calls.append("save") or True,
    })

    optimize_btn.click()

    assert calls == []
    assert status.text == "Status: ready"
    assert error.text == "Error: handler not connected"


def test_runtime_backend_save_button_does_not_use_legacy_save_alias():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    save_btn = backend.get_object("btnSave")
    status = backend.get_object("lblStatus")
    calls = []

    backend.connect_signals({
        "on_save": lambda: calls.append("save") or True,
    })

    save_btn.click()

    assert calls == []
    assert status.text == "Status: ready"


def test_runtime_backend_apply_handler_missing_sets_status_and_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    apply_btn.click()

    assert status.text == "Status: ready"
    assert error.text == "Error: handler not connected"


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


def test_runtime_backend_toggle_position_failure_surfaces_feedback():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    def on_toggle(_name, _active):
        raise RuntimeError("toggle position failed")

    backend.connect_signals({"on_toggle_position": on_toggle})

    backend.get_object("tglUpperL").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: toggle position failed"


def test_runtime_backend_toggle_position_reset_failure_surfaces_feedback():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    def on_reset(_name):
        raise RuntimeError("toggle reset failed")

    backend.connect_signals({"on_toggle_position_reset": on_reset})

    toggle = backend.get_object("tglUpperL")
    toggle.click()
    toggle.click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: toggle reset failed"


def test_runtime_backend_toggle_position_pressed_failure_surfaces_feedback():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    def on_pressed(_name):
        raise RuntimeError("toggle press failed")

    backend.connect_signals({"on_toggle_position_pressed": on_pressed})

    backend.get_object("tglUpperL").click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: toggle press failed"


def test_runtime_backend_toggle_position_opposite_reset_failure_surfaces_feedback():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    def on_reset(name):
        if name == "tglPushLeftL":
            raise RuntimeError("toggle opposite reset failed")

    backend.connect_signals({"on_toggle_position_reset": on_reset})

    left = backend.get_object("tglPushLeftL")
    right = backend.get_object("tglPushRightL")
    left.set_active(True)

    right.click()

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert backend.get_object("lblError").text == "Error: toggle opposite reset failed"


def test_runtime_backend_margin_change_propagates_all_values():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("spnLeftMargin").set_value(11)
    backend.get_object("spnRightMargin").set_value(22)
    backend.get_object("spnTopMargin").set_value(33)
    backend.get_object("spnBottomMargin").set_value(44)

    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    captured = {}

    def on_margins(name, value):
        captured["name"] = name
        captured["value"] = value

    backend.connect_signals({"on_change_margins": on_margins})
    backend.get_object("spnLeftMargin").emit("value-changed", backend.get_object("spnLeftMargin"))

    assert captured == {"name": "spnLeftMargin", "value": 11}
    assert status.text == "Status: ready"
    assert error.text == "Error: none"
    assert backend.get_object("lblCurrentMargins").text == "margins=11,22,33,44"


def test_runtime_backend_margin_change_reports_legacy_handler_signature_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals({"on_change_margins": lambda _name: True})
    backend.get_object("spnLeftMargin").emit("value-changed", backend.get_object("spnLeftMargin"))

    assert backend.get_object("lblStatus").text == "Status: ready"
    assert "positional argument" in backend.get_object("lblError").text


def test_runtime_backend_margin_change_propagates_unexpected_runtime_error():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.connect_signals(
        {
            "on_change_margins": lambda _name, _value: (_ for _ in ()).throw(RuntimeError("margin change exploded")),
        }
    )

    with pytest.raises(RuntimeError, match="margin change exploded"):
        backend.get_object("spnLeftMargin").emit("value-changed", backend.get_object("spnLeftMargin"))


def test_runtime_backend_margin_spin_matches_upstream_adjustments():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    top = backend.get_object("spnTopMargin")
    left = backend.get_object("spnLeftMargin")
    right = backend.get_object("spnRightMargin")
    bottom = backend.get_object("spnBottomMargin")

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

    backend.get_object("spnLeftMargin").set_value(5)
    backend.get_object("spnRightMargin").set_value(15)
    backend.get_object("spnTopMargin").set_value(25)
    backend.get_object("spnBottomMargin").set_value(35)
    backend.get_object("spnTopMargin").emit("value-changed", backend.get_object("spnTopMargin"))

    assert backend.get_object("lblCurrentMargins").text == "margins=5,15,25,35"


def test_runtime_backend_margin_and_top_alignment_coexist_in_current_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    backend.get_object("spnTopMargin").set_value(5)
    backend.get_object("spnTopMargin").emit("value-changed", backend.get_object("spnTopMargin"))
    backend.get_object("tglUpperL").click()

    assert backend.get_object("lblCurrentMargins").text == "margins=0,0,5,0"
    assert backend.get_object("lblCurrentStateL").text == "L: align=center valign=top"

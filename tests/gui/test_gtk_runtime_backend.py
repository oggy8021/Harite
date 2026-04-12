from __future__ import annotations

from harite.gui.adapters.gtk_backend import GtkRuntimeSignalBackend


class _Orientation:
    VERTICAL = 1
    HORIZONTAL = 2


class _WidgetBase:
    def __init__(self):
        self._signals = {}

    def connect(self, name, callback):
        self._signals.setdefault(name, []).append(callback)

    def emit(self, name, *args):
        for cb in self._signals.get(name, []):
            cb(*args)


class _Window(_WidgetBase):
    def __init__(self, title=""):
        super().__init__()
        self.title = title
        self.child = None

    def set_default_size(self, *_args):
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


class _FakeGtk:
    Orientation = _Orientation
    Window = _Window
    Box = _Box
    Label = _Label
    Entry = _Entry
    Button = _Button


def test_runtime_backend_input_controls_optimize_button_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    entry = backend.get_object("entPathL")
    optimize_btn = backend.get_object("btnSave")
    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_entPath_insert_text": lambda _text: None})

    assert optimize_btn.sensitive is False
    assert apply_btn.sensitive is False

    entry.set_text("/tmp/example.jpg")
    entry.emit("changed", entry)

    assert optimize_btn.sensitive is True
    assert apply_btn.sensitive is False
    assert status.text == "Input: updated"
    assert error.text == "Error: none"


def test_runtime_backend_optimize_result_controls_apply_button_state():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnSave")
    apply_btn = backend.get_object("btnSetWall")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")
    optimize_result = backend.get_object("lblOptimizeResult")
    apply_target = backend.get_object("lblApplyTarget")

    backend.connect_signals({"on_btnSave_clicked": lambda: True})
    optimize_btn.click()

    assert apply_btn.sensitive is True
    assert status.text == "Optimize: ok"
    assert error.text == "Error: none"
    assert optimize_result.text == "Optimize result: success"
    assert apply_target.text == "Apply target: ready"

    backend.connect_signals({"on_btnSave_clicked": lambda: False})
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
    assert backend.get_object("lblOptimizeSection") is not None
    assert backend.get_object("boxOptimizeSection") is not None
    assert backend.get_object("lblOptimizeResult") is not None
    assert backend.get_object("lblApplySection") is not None
    assert backend.get_object("boxApplySection") is not None
    assert backend.get_object("lblApplyTarget") is not None
    assert backend.get_object("lblError") is not None


def test_runtime_backend_apply_success_updates_apply_target():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnSave")
    apply_btn = backend.get_object("btnSetWall")
    apply_target = backend.get_object("lblApplyTarget")
    status = backend.get_object("lblStatus")
    error = backend.get_object("lblError")

    backend.connect_signals({"on_btnSave_clicked": lambda: True})
    backend.connect_signals({"on_btnSetWall_clicked": lambda: True})

    optimize_btn.click()
    apply_btn.click()

    assert status.text == "Apply: dry-run-ok"
    assert error.text == "Error: none"
    assert apply_target.text == "Apply target: consumed"


def test_runtime_backend_optimize_sets_running_state_before_handler_call():
    backend = GtkRuntimeSignalBackend(_FakeGtk)

    optimize_btn = backend.get_object("btnSave")
    status = backend.get_object("lblStatus")

    observed = {}

    def on_optimize_clicked():
        observed["status_when_called"] = status.text
        return True

    backend.connect_signals({"on_btnSave_clicked": on_optimize_clicked})
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

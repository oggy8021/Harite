from pathlib import Path

import pytest

from harite.gui.adapters import gtk_runtime_preview
from harite.gui.adapters.gtk_runtime_preview import build_preview_crop_boxes, preview_target_size, set_preview_widget


class _Backend:
    def __init__(self, container):
        self._objects = {"boxPreviewImagesRow": container}


class _BadWidthContainer:
    def get_allocated_width(self):
        raise ValueError("width missing")


class _ExplodingWidthContainer:
    def get_allocated_width(self):
        raise RuntimeError("width probe failed")


class _PreviewWidget:
    def __init__(self):
        self.file_path = None
        self.pixbuf = None
        self.size_requests = []

    def set_size_request(self, width, height):
        self.size_requests.append((width, height))

    def set_from_pixbuf(self, pixbuf):
        self.pixbuf = pixbuf

    def set_from_file(self, file_path):
        self.file_path = str(file_path)


class _PreviewBackend:
    def __init__(self, widget):
        self._objects = {"imgPreviewL": widget}


def test_preview_target_size_falls_back_on_value_error():
    backend = _Backend(_BadWidthContainer())

    assert preview_target_size(backend) == (160, 90)


def test_preview_target_size_propagates_unexpected_width_probe_failure():
    backend = _Backend(_ExplodingWidthContainer())

    with pytest.raises(RuntimeError, match="width probe failed"):
        preview_target_size(backend)


def test_get_gdkpixbuf_module_propagates_unexpected_runtime_error(monkeypatch):
    backend = object()

    def fake_import_module(name):
        if name == "gi":
            raise RuntimeError("pixbuf probe failed")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("importlib.import_module", fake_import_module)

    with pytest.raises(RuntimeError, match="pixbuf probe failed"):
        gtk_runtime_preview.get_gdkpixbuf_module(backend)


def test_build_preview_crop_boxes_returns_none_for_invalid_image_file(tmp_path):
    source = tmp_path / "broken-preview.jpg"
    source.write_bytes(b"not-an-image")

    assert build_preview_crop_boxes(source, l_display=(1920, 1080), r_display=(1920, 1080)) is None


def test_build_preview_crop_boxes_propagates_unexpected_image_open_failure(monkeypatch):
    class _BrokenImageModule:
        @staticmethod
        def open(_source_path):
            raise RuntimeError("image open failed")

    monkeypatch.setitem(__import__("sys").modules, "PIL.Image", _BrokenImageModule)
    monkeypatch.setattr(gtk_runtime_preview, "__builtins__", gtk_runtime_preview.__builtins__)

    original_import = __import__

    def _fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "PIL":
            class _PILModule:
                Image = _BrokenImageModule

            return _PILModule()
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _fake_import)

    with pytest.raises(RuntimeError, match="image open failed"):
        build_preview_crop_boxes(Path("preview.jpg"), l_display=(1920, 1080), r_display=(1920, 1080))


def test_set_preview_widget_falls_back_to_set_from_file_on_expected_pixbuf_load_error(monkeypatch, tmp_path):
    class _BrokenPixbuf:
        @staticmethod
        def new_from_file(_file_path):
            raise OSError("cannot decode image")

    class _FakeGdkPixbuf:
        Pixbuf = _BrokenPixbuf

        class InterpType:
            BILINEAR = object()

    source = tmp_path / "preview.jpg"
    source.write_bytes(b"not-an-image")
    widget = _PreviewWidget()
    backend = _PreviewBackend(widget)
    monkeypatch.setattr(gtk_runtime_preview, "get_gdkpixbuf_module", lambda _backend: _FakeGdkPixbuf)

    set_preview_widget(backend, "imgPreviewL", source)

    assert Path(widget.file_path).name == "preview.jpg"


def test_set_preview_widget_propagates_unexpected_pixbuf_failure(monkeypatch, tmp_path):
    class _ExplodingPixbuf:
        @staticmethod
        def new_from_file(_file_path):
            raise RuntimeError("pixbuf loader failed")

    class _FakeGdkPixbuf:
        Pixbuf = _ExplodingPixbuf

        class InterpType:
            BILINEAR = object()

    source = tmp_path / "preview.jpg"
    source.write_bytes(b"preview")
    widget = _PreviewWidget()
    backend = _PreviewBackend(widget)
    monkeypatch.setattr(gtk_runtime_preview, "get_gdkpixbuf_module", lambda _backend: _FakeGdkPixbuf)

    with pytest.raises(RuntimeError, match="pixbuf loader failed"):
        set_preview_widget(backend, "imgPreviewL", source)


def test_set_preview_widget_propagates_unexpected_set_from_file_failure(monkeypatch, tmp_path):
    source = tmp_path / "preview.jpg"
    source.write_bytes(b"preview")
    widget = _PreviewWidget()
    backend = _PreviewBackend(widget)
    monkeypatch.setattr(gtk_runtime_preview, "get_gdkpixbuf_module", lambda _backend: None)

    def _explode(_file_path):
        raise RuntimeError("set_from_file failed")

    widget.set_from_file = _explode

    with pytest.raises(RuntimeError, match="set_from_file failed"):
        set_preview_widget(backend, "imgPreviewL", source)
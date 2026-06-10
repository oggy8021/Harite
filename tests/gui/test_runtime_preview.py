from pathlib import Path

import pytest

from harite.gui.adapters.gui_runtime_preview import build_preview_crop_boxes, preview_target_size, set_preview_widget


class _Backend:
    def __init__(self, container):
        self._objects = {"boxPreviewImagesRow": container}


class _WidthContainer:
    def __init__(self, width: int):
        self._width = width

    def width(self):
        return self._width


class _BadWidthContainer:
    def width(self):
        raise ValueError("width missing")


class _ExplodingWidthContainer:
    def width(self):
        raise RuntimeError("width probe failed")


def test_preview_target_size_scales_from_container_width():
    backend = _Backend(_WidthContainer(800))

    assert preview_target_size(backend) == (320, 180)


def test_preview_target_size_falls_back_on_value_error():
    backend = _Backend(_BadWidthContainer())

    assert preview_target_size(backend) == (160, 90)


def test_preview_target_size_propagates_unexpected_width_probe_failure():
    backend = _Backend(_ExplodingWidthContainer())

    with pytest.raises(RuntimeError, match="width probe failed"):
        preview_target_size(backend)


def test_build_preview_crop_boxes_returns_none_for_invalid_image_file(tmp_path):
    source = tmp_path / "broken-preview.jpg"
    source.write_bytes(b"not-an-image")

    assert build_preview_crop_boxes(source, l_display=(1920, 1080), r_display=(1920, 1080)) is None


def test_set_preview_widget_delegates_to_backend(tmp_path):
    source = tmp_path / "preview.jpg"
    source.write_bytes(b"preview")
    calls: list[tuple] = []

    class _BackendWithSetter:
        def __init__(self):
            self._objects = {}

        def _set_preview_widget(self, object_name, source_path, *, crop_box=None):
            calls.append((object_name, source_path, crop_box))

    backend = _BackendWithSetter()
    set_preview_widget(backend, "imgPreviewL", source)

    assert len(calls) == 1
    assert calls[0][0] == "imgPreviewL"
    assert calls[0][1] == source

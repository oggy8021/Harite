from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any


def get_gdkpixbuf_module(backend: Any) -> Any | None:
    try:
        gi = importlib.import_module("gi")
        gi.require_version("GdkPixbuf", "2.0")
        return importlib.import_module("gi.repository.GdkPixbuf")
    except (ImportError, ValueError):
        return None


def clear_preview_widget(backend: Any, object_name: str, message: str) -> None:
    widget = backend._objects.get(object_name)
    if widget is None:
        return
    if hasattr(widget, "set_text"):
        widget.set_text(message)
        return
    if hasattr(widget, "set_from_pixbuf"):
        widget.set_from_pixbuf(None)


def preview_target_size(backend: Any) -> tuple[int, int]:
    fallback_width = 160
    fallback_height = 90

    container = backend._objects.get("boxPreviewImagesRow") or backend._objects.get("boxPreviewSection")
    if container is None:
        return fallback_width, fallback_height

    allocated_width = None
    if hasattr(container, "get_allocated_width"):
        try:
            allocated_width = int(container.get_allocated_width())
        except (TypeError, ValueError):
            allocated_width = None
    elif hasattr(container, "allocation"):
        allocation = getattr(container, "allocation", None)
        allocated_width = int(getattr(allocation, "width", 0) or 0)

    if not allocated_width or allocated_width <= 0:
        return fallback_width, fallback_height

    target_width = max(120, min(320, int((allocated_width - 6) * 0.48)))
    target_height = max(68, int(round(target_width * 9 / 16)))
    return target_width, target_height


def set_preview_widget(
    backend: Any,
    object_name: str,
    source_path: Path | None,
    *,
    crop_box: tuple[int, int, int, int] | None = None,
) -> None:
    widget = backend._objects.get(object_name)
    if widget is None:
        return
    if source_path is None:
        clear_preview_widget(backend, object_name, f"{object_name}: not-ready")
        return

    if hasattr(widget, "set_text"):
        widget.set_text(str(source_path.name))
        return

    target_width, target_height = preview_target_size(backend)
    if hasattr(widget, "set_size_request"):
        try:
            widget.set_size_request(target_width, target_height)
        except TypeError:
            pass

    gdkpixbuf = get_gdkpixbuf_module(backend)
    if gdkpixbuf is not None and hasattr(widget, "set_from_pixbuf"):
        try:
            pixbuf = gdkpixbuf.Pixbuf.new_from_file(str(source_path))
            if crop_box is not None:
                x, y, width, height = crop_box
                pixbuf = pixbuf.new_subpixbuf(int(x), int(y), int(width), int(height))
            scaled = pixbuf.scale_simple(target_width, target_height, gdkpixbuf.InterpType.BILINEAR)
            widget.set_from_pixbuf(scaled or pixbuf)
            return
        except (FileNotFoundError, OSError, TypeError, ValueError):
            pass

    if hasattr(widget, "set_from_file"):
        try:
            widget.set_from_file(str(source_path))
        except (FileNotFoundError, OSError, TypeError, ValueError):
            pass


def build_preview_crop_boxes(
    source_path: Path,
    *,
    l_display: tuple[int, int] | None,
    r_display: tuple[int, int] | None,
) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]] | None:
    try:
        from PIL import Image

        with Image.open(source_path) as image:
            comp_width, comp_height = image.size
    except (ImportError, OSError, ValueError):
        return None

    left_width = int(l_display[0]) if l_display is not None else 1
    right_width = int(r_display[0]) if r_display is not None else 1
    total_width = max(1, left_width + right_width)
    split_x = int(round((left_width / total_width) * comp_width))
    split_x = max(1, min(comp_width - 1, split_x)) if comp_width > 1 else comp_width
    return (
        (0, 0, split_x, comp_height),
        (split_x, 0, max(1, comp_width - split_x), comp_height),
    )


def sync_result_preview_from_owner(backend: Any, owner: Any) -> None:
    builder = getattr(owner, "build_result_preview_state", None)
    if not callable(builder):
        clear_preview_widget(backend, "imgPreviewL", "Preview L: not-ready")
        clear_preview_widget(backend, "imgPreviewR", "Preview R: not-ready")
        backend._set_label_text("lblPreviewAssignL", "L display <- -")
        backend._set_label_text("lblPreviewAssignR", "R display <- -")
        backend._set_label_text("lblPreviewResultL", "Result: not-ready")
        backend._set_label_text("lblPreviewResultR", "Result: not-ready")
        backend._set_label_text("lblPreviewState", "Preview: not-ready")
        backend._set_label_text("lblPreviewSource", "Preview source: -")
        backend._set_label_text("lblPreviewAssist", "Assist: not-ready")
        return

    state = builder()
    source_path = getattr(state, "source_file", None)
    if source_path is None:
        clear_preview_widget(backend, "imgPreviewL", "Preview L: not-ready")
        clear_preview_widget(backend, "imgPreviewR", "Preview R: not-ready")
        backend._set_label_text("lblPreviewAssignL", "L display <- -")
        backend._set_label_text("lblPreviewAssignR", "R display <- -")
        backend._set_label_text("lblPreviewResultL", "Result: not-ready")
        backend._set_label_text("lblPreviewResultR", "Result: not-ready")
        backend._set_label_text("lblPreviewState", "Preview: not-ready")
        backend._set_label_text("lblPreviewSource", "Preview source: -")
        backend._set_label_text("lblPreviewAssist", "Assist: not-ready")
        return

    mode = str(getattr(state, "apply_mode", "single-file") or "single-file").strip().lower()
    backend._set_label_text("lblPreviewAssignL", str(getattr(state, "l_assignment", "") or "L display <- -"))
    backend._set_label_text("lblPreviewAssignR", str(getattr(state, "r_assignment", "") or "R display <- -"))
    backend._set_label_text("lblPreviewResultL", str(getattr(state, "l_result_note", "") or "Result: not-ready"))
    backend._set_label_text("lblPreviewResultR", str(getattr(state, "r_result_note", "") or "Result: not-ready"))
    backend._set_label_text("lblPreviewSource", f"Preview source: {Path(source_path).name}")
    backend._set_label_text("lblPreviewAssist", str(getattr(state, "assist_summary", "") or "Assist: not-ready"))
    if mode == "per-monitor-auto-split":
        boxes = build_preview_crop_boxes(
            Path(source_path),
            l_display=getattr(state, "l_display", None),
            r_display=getattr(state, "r_display", None),
        )
        backend._set_label_text("lblPreviewState", "Preview: pseudo auto-split by display widths")
        if boxes is not None:
            set_preview_widget(backend, "imgPreviewL", Path(source_path), crop_box=boxes[0])
            set_preview_widget(backend, "imgPreviewR", Path(source_path), crop_box=boxes[1])
            return

    backend._set_label_text("lblPreviewState", "Preview: same image on both displays")
    set_preview_widget(backend, "imgPreviewL", Path(source_path))
    set_preview_widget(backend, "imgPreviewR", Path(source_path))
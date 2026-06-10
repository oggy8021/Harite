"""Preview sync helpers (Qt backend delegates widget updates)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def clear_preview_widget(backend: Any, object_name: str, message: str = "") -> None:
    clearer = getattr(backend, "_clear_preview_widget", None)
    if callable(clearer):
        clearer(object_name, message)


def preview_target_size(backend: Any) -> tuple[int, int]:
    fallback_width = 160
    fallback_height = 90

    container = backend._objects.get("boxPreviewImagesRow") or backend._objects.get("boxPreviewSection")
    if container is None:
        return fallback_width, fallback_height

    allocated_width = None
    if hasattr(container, "width"):
        try:
            allocated_width = int(container.width())
        except (TypeError, ValueError):
            allocated_width = None

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
    setter = getattr(backend, "_set_preview_widget", None)
    if callable(setter):
        setter(object_name, source_path, crop_box=crop_box)


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
    """Sync preview thumbnails only (P-04 — no assignment/result/state labels)."""
    builder = getattr(owner, "build_result_preview_state", None)
    if not callable(builder):
        clear_preview_widget(backend, "imgPreviewL")
        clear_preview_widget(backend, "imgPreviewR")
        return

    state = builder()
    source_path = getattr(state, "source_file", None)
    if source_path is None:
        clear_preview_widget(backend, "imgPreviewL")
        clear_preview_widget(backend, "imgPreviewR")
        return

    mode = str(getattr(state, "apply_mode", "single-file") or "single-file").strip().lower()
    if mode == "per-monitor-auto-split":
        boxes = build_preview_crop_boxes(
            Path(source_path),
            l_display=getattr(state, "l_display", None),
            r_display=getattr(state, "r_display", None),
        )
        if boxes is not None:
            set_preview_widget(backend, "imgPreviewL", Path(source_path), crop_box=boxes[0])
            set_preview_widget(backend, "imgPreviewR", Path(source_path), crop_box=boxes[1])
            return

    set_preview_widget(backend, "imgPreviewL", Path(source_path))
    set_preview_widget(backend, "imgPreviewR", Path(source_path))

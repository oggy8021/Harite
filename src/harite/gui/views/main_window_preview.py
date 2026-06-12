from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harite.apply_surface import preview_assist_summary, preview_result_notes
from harite.gui.services.cli_mapper import OptimizeRequest, to_cli_args
from harite.optimize_settings import resolve_optimize_display_settings


@dataclass(frozen=True)
class ResultPreviewState:
    source_file: Path | None
    apply_mode: str
    l_display: tuple[int, int] | None = None
    r_display: tuple[int, int] | None = None
    assist_summary: str = "Assist: not-ready"
    l_assignment: str = "L display <- -"
    r_assignment: str = "R display <- -"
    l_result_note: str = "Result: not-ready"
    r_result_note: str = "Result: not-ready"


def format_display_summary(display: tuple[int, int] | None) -> str | None:
    if display is None:
        return None
    return f"{display[0]}x{display[1]}"


def build_preview_assist_summary(
    apply_mode: str,
    l_display: tuple[int, int] | None,
    r_display: tuple[int, int] | None,
) -> str:
    return preview_assist_summary(apply_mode, l_display, r_display)


def format_preview_assignment_name(value: str, max_length: int = 36) -> str:
    name = Path(value).name
    if len(name) <= max_length:
        return name

    tail_length = 12
    head_length = max_length - tail_length - 3
    if head_length < 8:
        head_length = 8
        tail_length = max(4, max_length - head_length - 3)
    return f"{name[:head_length]}...{name[-tail_length:]}"


def build_preview_assignments(input_values: list[str]) -> tuple[str, str]:
    normalized = [format_preview_assignment_name(value) for value in input_values if str(value or "").strip()]
    if len(normalized) >= 2:
        return f"L display <- {normalized[0]}", f"R display <- {normalized[1]}"
    if len(normalized) == 1:
        return f"L display <- {normalized[0]}", f"R display <- {normalized[0]}"
    return "L display <- -", "R display <- -"


def build_preview_result_notes(apply_mode: str) -> tuple[str, str]:
    return preview_result_notes(apply_mode)


def build_result_preview_state(owner: Any) -> ResultPreviewState:
    source_file = owner.last_saved_files[-1] if owner.last_saved_files else None
    if source_file is None:
        return ResultPreviewState(source_file=None, apply_mode=owner.apply_mode)

    input_values = [part.strip() for part in owner.form_state.input_value.split(",") if part.strip()]
    l_display = None
    r_display = None

    try:
        display_settings = resolve_optimize_display_settings(
            input_values=input_values,
            canvas_scale_percent=owner.form_state.canvas_scale_percent,
        )
        l_display = owner._parse_resolution_value(display_settings.l_display)
        r_display = owner._parse_resolution_value(display_settings.r_display)
    except ValueError:
        pass

    l_assignment, r_assignment = build_preview_assignments(input_values)
    l_result_note, r_result_note = build_preview_result_notes(owner.apply_mode)

    return ResultPreviewState(
        source_file=source_file,
        apply_mode=owner.apply_mode,
        l_display=l_display,
        r_display=r_display,
        assist_summary=build_preview_assist_summary(owner.apply_mode, l_display, r_display),
        l_assignment=l_assignment,
        r_assignment=r_assignment,
        l_result_note=l_result_note,
        r_result_note=r_result_note,
    )


def build_optimize_cli_preview(owner: Any) -> str:
    req = OptimizeRequest(
        input_value=owner.form_state.input_value,
        output_dir=Path(owner.form_state.output_dir),
        canvas_scale_percent=owner.form_state.canvas_scale_percent,
        scaling=owner.form_state.scaling,
        margins=owner.form_state.margins,
        align=owner.form_state.align,
        valign=owner.form_state.valign,
        quality=owner.form_state.quality,
        background_color=owner.form_state.background_color,
        embed_info=owner.form_state.embed_info,
        embed_text=owner.form_state.embed_text,
        embed_position=owner.form_state.embed_position,
        embed_max_lines=owner._effective_margin_text_max_lines(),
    )
    args = to_cli_args(req)
    preview = "harite " + " ".join(args)
    owner._log(f"CLI preview: {preview}")
    return preview

from __future__ import annotations

from typing import Any

from harite.core import EMBED_POSITION_VALUES, _build_embed_settings_lines
from harite.apply_surface import apply_mode_help_text
from harite.optimize_settings import compute_output_resolution, resolve_optimize_display_settings
from harite.positioning import format_position_pair, parse_position_pair
from harite.resolution import parse_resolution


def parse_margin_values(value: object | None) -> tuple[int, int, int, int]:
    raw = str(value or "").strip()
    if not raw:
        return (0, 0, 0, 0)

    parts = [part.strip() for part in raw.split(",")]
    if len(parts) != 4:
        return (0, 0, 0, 0)

    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        return (0, 0, 0, 0)


def sync_slideshow_state_from_owner(backend: Any, owner: Any) -> None:
    backend._slideshow_srcdir_l = str(getattr(owner, "slideshow_srcdir_l", backend._slideshow_srcdir_l) or "")
    backend._slideshow_srcdir_r = str(getattr(owner, "slideshow_srcdir_r", backend._slideshow_srcdir_r) or "")
    backend._slideshow_source_id_l = str(getattr(owner, "slideshow_source_id_l", "") or "")
    backend._slideshow_source_id_r = str(getattr(owner, "slideshow_source_id_r", "") or "")
    backend._slideshow_profile_id = str(getattr(owner, "slideshow_profile_id", "") or "")
    backend.slideshow_mode = str(getattr(owner, "slideshow_mode", getattr(backend, "slideshow_mode", "random")) or "random")
    backend._slideshow_active_mode = str(
        getattr(owner, "_slideshow_active_mode", getattr(backend, "_slideshow_active_mode", backend.slideshow_mode))
        or backend.slideshow_mode
    )
    backend._slideshow_running = bool(getattr(owner, "slideshow_running", backend._slideshow_running))
    backend._slideshow_paused = bool(getattr(owner, "slideshow_paused", getattr(backend, "_slideshow_paused", False)))
    backend._slideshow_state_l = getattr(owner, "_slideshow_state_l", backend._slideshow_state_l)
    backend._slideshow_state_r = getattr(owner, "_slideshow_state_r", backend._slideshow_state_r)
    backend._slideshow_previous_l = getattr(owner, "_slideshow_previous_l", backend._slideshow_previous_l)
    backend._slideshow_previous_r = getattr(owner, "_slideshow_previous_r", backend._slideshow_previous_r)
    for side_key, attr in (("l", "slideshow_l_auto_display_scale"), ("r", "slideshow_r_auto_display_scale")):
        widget = backend._objects.get(f"chk_slideshow_auto_display_scale_{side_key}")
        if widget is not None and hasattr(widget, "setChecked"):
            widget.blockSignals(True)
            try:
                widget.setChecked(bool(getattr(owner, attr, False)))
            finally:
                widget.blockSignals(False)
    interval_seconds = int(getattr(owner, "slideshow_interval_seconds", 0) or 0)
    backend._set_spin_value("spnInterval", interval_seconds if interval_seconds > 0 else 60)
    backend._set_toggle_active("radSlideshowModeSequential", backend.slideshow_mode == "sequential")
    backend._set_toggle_active("radSlideshowModeRandom", backend.slideshow_mode == "random")
    backend._set_label_text(
        "lblSlideshowModeHelp",
        "Sequential rotates images."
        if backend.slideshow_mode == "sequential"
        else "Random rotates images.",
    )
    backend._set_button_enabled("btnDaemonize", bool(getattr(owner, "can_start_slideshow", False)))
    backend._set_button_enabled("btnCancelDaemonize", bool(getattr(owner, "slideshow_running", False)))
    if hasattr(backend, "_refresh_slideshow_mode_controls"):
        backend._refresh_slideshow_source_labels(owner)
        backend._refresh_slideshow_mode_controls(owner)
    else:
        backend._refresh_slideshow_source_labels()
    if hasattr(backend, "_refresh_slideshow_registry_combos"):
        backend._refresh_slideshow_registry_combos(owner)
    if hasattr(backend, "_refresh_slideshow_codh_keyword_chip"):
        backend._refresh_slideshow_codh_keyword_chip(owner)
    backend._refresh_slideshow_summary_label()
    backend._refresh_slideshow_current_label()
    from harite.gui.adapters_qt.qt_widget_helpers import slideshow_output_dir_from_owner

    backend._refresh_slideshow_output_label(slideshow_output_dir_from_owner(owner))


def sync_main_state_from_owner(backend: Any, owner: Any) -> None:
    form_state = getattr(owner, "form_state", None)
    if form_state is None:
        return

    margin_left, margin_right, margin_top, margin_bottom = parse_margin_values(
        getattr(form_state, "margins", None)
    )
    backend._set_spin_value("spnLeftMargin", margin_left)
    backend._set_spin_value("spnRightMargin", margin_right)
    backend._set_spin_value("spnTopMargin", margin_top)
    backend._set_spin_value("spnBottomMargin", margin_bottom)
    from harite.gui.views.margins_surface import refresh_all_margins_bulk_controls

    refresh_all_margins_bulk_controls(
        backend,
        (margin_left, margin_right, margin_top, margin_bottom),
    )

    align_left, align_right = parse_position_pair(getattr(form_state, "align", "center"), axis="align")
    valign_left, valign_right = parse_position_pair(getattr(form_state, "valign", "center"), axis="valign")

    backend._set_toggle_active("tglPushLeftL", align_left == "left")
    backend._set_toggle_active("tglPushRightL", align_left == "right")
    backend._set_toggle_active("tglPushLeftR", align_right == "left")
    backend._set_toggle_active("tglPushRightR", align_right == "right")
    backend._set_toggle_active("tglUpperL", valign_left == "top")
    backend._set_toggle_active("tglLowerL", valign_left == "bottom")
    backend._set_toggle_active("tglUpperR", valign_right == "top")
    backend._set_toggle_active("tglLowerR", valign_right == "bottom")

    from harite.gui.views.display_scale_surface import set_display_scale_combo

    combo_l = backend._objects.get("combo_display_scale_l") or backend._objects.get("cmbDisplayScaleL")
    if combo_l is not None:
        set_display_scale_combo(combo_l, getattr(form_state, "l_display_scale", 1.0) or 1.0)
    combo_r = backend._objects.get("combo_display_scale_r") or backend._objects.get("cmbDisplayScaleR")
    if combo_r is not None:
        set_display_scale_combo(combo_r, getattr(form_state, "r_display_scale", 1.0) or 1.0)

    for side_key, attr in (("l", "l_auto_display_scale"), ("r", "r_auto_display_scale")):
        widget = backend._objects.get(f"chk_auto_display_scale_{side_key}")
        if widget is not None and hasattr(widget, "setChecked"):
            widget.blockSignals(True)
            try:
                widget.setChecked(bool(getattr(form_state, attr, False)))
            finally:
                widget.blockSignals(False)

    backend._refresh_current_state_labels()
    sync_apply_mode_from_owner(backend, owner)
    refresh_margin_settings_preview_label(backend, owner)


def sync_apply_mode_from_owner(backend: Any, owner: Any) -> None:
    mode = str(getattr(owner, "apply_mode", "single-file") or "single-file").strip().lower()
    is_span = mode == "per-monitor-auto-split"
    backend._set_toggle_active("radApplyPerMonitor", is_span)
    backend._set_toggle_active("radApplySingle", not is_span)

    from harite.gui.views.main_action_surface import sync_apply_mode_tooltips

    sync_apply_mode_tooltips(backend, owner, mode=mode)


def sync_action_availability_from_owner(backend: Any, owner: Any) -> None:
    """Mirror MainWindow action flags onto header / action-cluster buttons."""
    backend._set_button_enabled("btnSave", bool(getattr(owner, "can_optimize", False)))
    backend._set_button_enabled("btnOptimize", bool(getattr(owner, "can_optimize", False)))
    backend._set_button_enabled("btnSetWall", bool(getattr(owner, "can_apply", False)))
    backend._set_button_enabled("btnDaemonize", bool(getattr(owner, "can_start_slideshow", False)))
    from harite.gui.dual_display_ui import sync_dual_display_slot_availability_from_owner

    sync_dual_display_slot_availability_from_owner(backend, owner)
    sync_flow_legend_from_owner(backend, owner)


def sync_flow_legend_from_owner(backend: Any, owner: Any | None) -> None:
    from harite.gui.views.flow_legend_surface import apply_flow_legend_markup

    widget = backend._objects.get("lblFlowLegend")
    apply_flow_legend_markup(widget, owner=owner)


def sync_input_state_from_owner(backend: Any, owner: Any) -> None:
    form_state = getattr(owner, "form_state", None)
    if form_state is None:
        return

    backend._input_path_l = str(getattr(owner, "input_path_l", "") or "")
    backend._input_path_r = str(getattr(owner, "input_path_r", "") or "")
    backend._set_entry_text("entPathL", backend._format_input_display(backend._input_path_l))
    backend._set_entry_text("entPathR", backend._format_input_display(backend._input_path_r))

    sync_action_availability_from_owner(backend, owner)
    backend._set_save_path_dialog_open_state(bool(getattr(owner, "save_path_dialog_open", False)))
    refresh_margin_settings_preview_label(backend, owner)


def _collect_optimize_input_values(owner: Any | None, backend: Any) -> list[str]:
    form_state = getattr(owner, "form_state", None) if owner is not None else None
    if form_state is not None:
        parts = [part.strip() for part in str(getattr(form_state, "input_value", "") or "").split(",") if part.strip()]
        if parts:
            return parts
    values: list[str] = []
    path_l = str(getattr(owner, "input_path_l", "") or getattr(backend, "_input_path_l", "") or "").strip()
    path_r = str(getattr(owner, "input_path_r", "") or getattr(backend, "_input_path_r", "") or "").strip()
    if path_l:
        values.append(path_l)
    if path_r:
        values.append(path_r)
    return values


def build_margin_settings_preview(backend: Any, owner: Any | None = None) -> str:
    form_state = getattr(owner, "form_state", None) if owner is not None else None
    margins = parse_margin_values(getattr(form_state, "margins", None)) if form_state is not None else (
        backend._read_spin_int("spnLeftMargin"),
        backend._read_spin_int("spnRightMargin"),
        backend._read_spin_int("spnTopMargin"),
        backend._read_spin_int("spnBottomMargin"),
    )
    inputs = _collect_optimize_input_values(owner, backend)
    if not inputs:
        return "input required for settings preview"
    try:
        canvas_scale_percent = int(getattr(form_state, "canvas_scale_percent", 100) or 100) if form_state is not None else 100
        display_settings = resolve_optimize_display_settings(
            input_values=inputs,
            canvas_scale_percent=canvas_scale_percent,
        )
        target_resolution = compute_output_resolution(
            parse_resolution(display_settings.resolution),
            display_settings.canvas_scale_percent,
        )
        l_display = None if not display_settings.l_display else parse_resolution(display_settings.l_display)
        r_display = None if not display_settings.r_display else parse_resolution(display_settings.r_display)
    except ValueError:
        return "display unavailable for settings preview"

    if form_state is not None:
        align = format_position_pair(getattr(form_state, "align", "center"), axis="align")
        valign = format_position_pair(getattr(form_state, "valign", "center"), axis="valign")
        l_display_scale = float(getattr(form_state, "l_display_scale", 1.0) or 1.0)
        r_display_scale = float(getattr(form_state, "r_display_scale", 1.0) or 1.0)
        l_auto_display_scale = bool(getattr(form_state, "l_auto_display_scale", False))
        r_auto_display_scale = bool(getattr(form_state, "r_auto_display_scale", False))
    else:
        align_left, valign_left = backend._current_side_state("L")
        align_right, valign_right = backend._current_side_state("R")
        align = f"{align_left},{align_right}"
        valign = f"{valign_left},{valign_right}"
        l_display_scale = 1.0
        r_display_scale = 1.0
        l_auto_display_scale = False
        r_auto_display_scale = False

    lines = _build_embed_settings_lines(
        target_resolution=target_resolution,
        margins=margins,
        align=align,
        valign=valign,
        input_count=len(inputs),
        two_screen=display_settings.two_screen,
        l_display=l_display,
        r_display=r_display,
        canvas_scale_percent=display_settings.canvas_scale_percent,
        l_display_scale=l_display_scale,
        r_display_scale=r_display_scale,
        l_auto_display_scale=l_auto_display_scale,
        r_auto_display_scale=r_auto_display_scale,
    )
    return "\n".join(lines)


def refresh_margin_settings_preview_label(backend: Any, owner: Any | None = None) -> None:
    """Update the Settings embed preview label (shared with JPEG burn-in lines)."""
    backend._set_label_text("lblMarginSettingsPreview", build_margin_settings_preview(backend, owner))


def refresh_margins_controls(backend: Any, owner: Any | None = None) -> None:
    form_state = getattr(owner, "form_state", None) if owner is not None else None
    margin_text_mode = str(getattr(form_state, "embed_info", "none") or "none").strip().lower() if form_state is not None else "none"

    settings_enabled = margin_text_mode in {"settings", "params", "combo"}
    text_enabled = margin_text_mode in {"free", "combo"}

    backend._set_widget_enabled("marginSettingsPage", settings_enabled)
    backend._set_widget_enabled("marginTextPage", text_enabled)
    backend._set_widget_enabled("txtMarginText", text_enabled)
    entry = backend._objects.get("txtMarginText")
    if entry is not None:
        if hasattr(entry, "set_editable"):
            entry.set_editable(bool(text_enabled))
        elif hasattr(entry, "setReadOnly"):
            entry.setReadOnly(not bool(text_enabled))

    if margin_text_mode in {"settings", "params"}:
        backend._set_notebook_page("marginTextTabs", 0)
    elif margin_text_mode in {"free", "combo"}:
        backend._set_notebook_page("marginTextTabs", 1)
    else:
        backend._set_notebook_page("marginTextTabs", 0)

    refresh_margin_settings_preview_label(backend, owner)


def sync_margins_state_from_owner(backend: Any, owner: Any) -> None:
    form_state = getattr(owner, "form_state", None)
    if form_state is None:
        return

    margin_text_mode = str(getattr(form_state, "embed_info", "none") or "none").lower()
    margin_text_position = str(getattr(form_state, "embed_position", "right-bottom") or "right-bottom").lower()
    if margin_text_position not in EMBED_POSITION_VALUES:
        margin_text_position = "right-bottom"
    backend._set_toggle_active("radMarginTextModeOff", margin_text_mode == "none")
    backend._set_toggle_active("radMarginTextModeSettings", margin_text_mode in {"settings", "params"})
    backend._set_toggle_active("radMarginTextModeText", margin_text_mode == "free")
    backend._set_toggle_active("radMarginTextModeBoth", margin_text_mode == "combo")
    backend._set_entry_text("txtMarginText", getattr(form_state, "embed_text", None))
    backend._set_toggle_active("radMarginTextPositionLeftTop", margin_text_position == "left-top")
    backend._set_toggle_active("radMarginTextPositionRightBottom", margin_text_position == "right-bottom")
    backend._set_toggle_active("radMarginTextPositionLeftBottom", margin_text_position == "left-bottom")
    backend._set_toggle_active("radMarginTextPositionRightTop", margin_text_position == "right-top")
    backend._set_spin_value("spnMarginTextMaxLines", int(getattr(form_state, "embed_max_lines", 3) or 3))
    refresh_margins_controls(backend, owner)


def sync_feedback_from_owner(backend: Any, owner: Any) -> None:
    level = str(getattr(owner, "status_level", "") or "").strip().lower()
    phase = str(getattr(owner, "status_phase", "") or "").strip() or "slideshow"
    message = str(getattr(owner, "status_message", "") or "").strip() or "state-updated"
    error = str(getattr(owner, "last_error", "") or "").strip() or None
    if error and error == message and level != "error":
        error = None
    backend._set_feedback(
        phase=phase.capitalize(),
        state=message,
        error=error,
        status_level=level or None,
    )
    sync_flow_legend_from_owner(backend, owner)

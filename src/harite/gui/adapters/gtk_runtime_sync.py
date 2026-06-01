from __future__ import annotations

from typing import Any

from harite.core import EMBED_POSITION_VALUES
from harite.apply_surface import apply_mode_help_text
from harite.apply_surface import margin_settings_split_label
from harite.positioning import parse_position_pair


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
    backend._refresh_slideshow_source_labels()
    if hasattr(backend, "_refresh_slideshow_registry_combos"):
        backend._refresh_slideshow_registry_combos(owner)
    backend._refresh_slideshow_summary_label()
    backend._refresh_slideshow_current_label()
    form_state = getattr(owner, "form_state", None)
    backend._refresh_slideshow_output_label(getattr(form_state, "output_dir", None) if form_state is not None else None)


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

    backend._refresh_current_state_labels()
    sync_apply_mode_from_owner(backend, owner)


def sync_apply_mode_from_owner(backend: Any, owner: Any) -> None:
    mode = str(getattr(owner, "apply_mode", "single-file") or "single-file").strip().lower()
    is_span = mode == "per-monitor-auto-split"
    backend._set_toggle_active("radApplyPerMonitor", is_span)
    backend._set_toggle_active("radApplySingle", not is_span)

    span_opt_in = False
    prefs = getattr(owner, "preferences", None)
    apply_prefs = getattr(prefs, "apply", None) if prefs is not None else None
    if apply_prefs is not None:
        span_opt_in = bool(getattr(apply_prefs, "windows_apply_span", False))
    backend._set_label_text("lblApplyMode", apply_mode_help_text(mode, windows_apply_span=span_opt_in))


def sync_action_availability_from_owner(backend: Any, owner: Any) -> None:
    """Mirror MainWindow action flags onto header / action-cluster buttons."""
    backend._set_button_enabled("btnSave", bool(getattr(owner, "can_optimize", False)))
    backend._set_button_enabled("btnOptimize", bool(getattr(owner, "can_optimize", False)))
    backend._set_button_enabled("btnSetWall", bool(getattr(owner, "can_apply", False)))
    backend._set_button_enabled("btnDaemonize", bool(getattr(owner, "can_start_slideshow", False)))


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
    backend._set_label_text("lblOptimizeResult", "Optimize result: not-run")
    backend._set_label_text("lblApplyTarget", "Apply target: not-ready")


def build_margin_settings_preview(backend: Any, owner: Any | None = None) -> str:
    form_state = getattr(owner, "form_state", None) if owner is not None else None
    resolution = str(getattr(form_state, "resolution", "-") or "-")
    margins = parse_margin_values(getattr(form_state, "margins", None)) if form_state is not None else (
        backend._read_spin_int("spnLeftMargin"),
        backend._read_spin_int("spnRightMargin"),
        backend._read_spin_int("spnTopMargin"),
        backend._read_spin_int("spnBottomMargin"),
    )
    left, right, top, bottom = margins
    if form_state is not None:
        align_left, align_right = parse_position_pair(getattr(form_state, "align", "center"), axis="align")
        valign_left, valign_right = parse_position_pair(getattr(form_state, "valign", "center"), axis="valign")
        two_screen = bool(getattr(form_state, "two_screen", False))
    else:
        align_left, valign_left = backend._current_side_state("L")
        align_right, valign_right = backend._current_side_state("R")
        two_screen = False
    split_text = margin_settings_split_label(two_screen)
    return "\n".join(
        (
            f"resolution={resolution}",
            f"margins=L{left},R{right},U{top},B{bottom}",
            f"align={align_left},{align_right} valign={valign_left},{valign_right}",
            split_text,
        )
    )


def refresh_margins_controls(backend: Any, owner: Any | None = None) -> None:
    form_state = getattr(owner, "form_state", None) if owner is not None else None
    margin_text_mode = str(getattr(form_state, "embed_info", "none") or "none").strip().lower() if form_state is not None else "none"

    settings_enabled = margin_text_mode in {"params", "combo"}
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

    if margin_text_mode == "params":
        backend._set_notebook_page("marginTextTabs", 0)
    elif margin_text_mode in {"free", "combo"}:
        backend._set_notebook_page("marginTextTabs", 1)
    else:
        backend._set_notebook_page("marginTextTabs", 0)

    backend._set_label_text("lblMarginSettingsPreview", build_margin_settings_preview(backend, owner))


def sync_margins_state_from_owner(backend: Any, owner: Any) -> None:
    form_state = getattr(owner, "form_state", None)
    if form_state is None:
        return

    margin_text_mode = str(getattr(form_state, "embed_info", "none") or "none").lower()
    margin_text_position = str(getattr(form_state, "embed_position", "right-bottom") or "right-bottom").lower()
    if margin_text_position not in EMBED_POSITION_VALUES:
        margin_text_position = "right-bottom"
    backend._set_toggle_active("radMarginTextModeOff", margin_text_mode == "none")
    backend._set_toggle_active("radMarginTextModeSettings", margin_text_mode == "params")
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
    phase = str(getattr(owner, "status_phase", "") or "").strip() or "slideshow"
    message = str(getattr(owner, "status_message", "") or "").strip() or "state-updated"
    error = str(getattr(owner, "last_error", "") or "").strip() or None
    if error == message:
        error = None
    backend._set_feedback(phase=phase.capitalize(), state=message, error=error)

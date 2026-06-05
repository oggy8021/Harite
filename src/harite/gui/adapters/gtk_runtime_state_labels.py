from __future__ import annotations

from typing import Any


def current_side_state(backend: Any, side: str) -> tuple[str, str]:
    align = "center"
    valign = "center"

    if backend._is_toggle_active(f"tglPushLeft{side}"):
        align = "left"
    elif backend._is_toggle_active(f"tglPushRight{side}"):
        align = "right"

    if backend._is_toggle_active(f"tglUpper{side}"):
        valign = "top"
    elif backend._is_toggle_active(f"tglLower{side}"):
        valign = "bottom"

    return align, valign


def refresh_current_state_labels(backend: Any) -> None:
    left = backend._read_spin_int("spnLeftMargin")
    right = backend._read_spin_int("spnRightMargin")
    top = backend._read_spin_int("spnTopMargin")
    bottom = backend._read_spin_int("spnBottomMargin")
    align_l, valign_l = current_side_state(backend, "L")
    align_r, valign_r = current_side_state(backend, "R")

    backend._set_label_text("lblCurrentMargins", f"margins={left},{right},{top},{bottom}")
    backend._set_label_text("lblCurrentStateL", f"L: align={align_l} valign={valign_l}")
    backend._set_label_text("lblCurrentStateR", f"R: align={align_r} valign={valign_r}")
    backend._set_label_text("lblMarginSettingsPreview", backend._build_margin_settings_preview())


def opposite_toggle_name(object_name: str) -> str | None:
    opposites = {
        "tglPushLeftL": "tglPushRightL",
        "tglPushRightL": "tglPushLeftL",
        "tglUpperL": "tglLowerL",
        "tglLowerL": "tglUpperL",
        "tglPushLeftR": "tglPushRightR",
        "tglPushRightR": "tglPushLeftR",
        "tglUpperR": "tglLowerR",
        "tglLowerR": "tglUpperR",
    }
    return opposites.get(object_name)
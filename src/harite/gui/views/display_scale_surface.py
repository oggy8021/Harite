"""Shared display-scale preset controls for Qt/GTK compose panels."""

from __future__ import annotations

from typing import Any

from harite.display_scale import DISPLAY_SCALE_PRESETS, format_display_scale_label, normalize_display_scale


def _scale_values_equal(left: object, right: object) -> bool:
    return normalize_display_scale(left) == normalize_display_scale(right)


def populate_display_scale_combo_qt(combo: Any) -> None:
    combo.clear()
    for scale in DISPLAY_SCALE_PRESETS:
        combo.addItem(format_display_scale_label(scale), scale)


def set_display_scale_combo_qt(combo: Any, scale: float | object) -> None:
    normalized = normalize_display_scale(scale)
    for index in range(combo.count()):
        if _scale_values_equal(combo.itemData(index), normalized):
            combo.setCurrentIndex(index)
            return
    combo.setCurrentIndex(0)


def read_display_scale_combo_qt(combo: Any) -> float:
    data = combo.currentData()
    if data is not None:
        return normalize_display_scale(data)
    return normalize_display_scale(combo.currentText())


def build_display_scale_combo_gtk(gtk_module: Any) -> Any:
    combo = gtk_module.ComboBoxText()
    for scale in DISPLAY_SCALE_PRESETS:
        if hasattr(combo, "append"):
            combo.append(str(scale), format_display_scale_label(scale))
        else:
            combo.append_text(format_display_scale_label(scale))
    combo.set_active(0)
    return combo


def _display_scale_index(scale: float | object) -> int:
    normalized = normalize_display_scale(scale)
    for index, preset in enumerate(DISPLAY_SCALE_PRESETS):
        if preset == normalized:
            return index
    return 0


def set_display_scale_combo_gtk(combo: Any, scale: float | object) -> None:
    index = _display_scale_index(scale)
    if combo.get_active() == index:
        return
    combo.set_active(index)


def read_display_scale_combo_gtk(combo: Any) -> float:
    active = combo.get_active()
    if active < 0 or active >= len(DISPLAY_SCALE_PRESETS):
        return 1.0
    return DISPLAY_SCALE_PRESETS[active]


def set_display_scale_combo(combo: Any, scale: float | object) -> None:
    if hasattr(combo, "count") and hasattr(combo, "itemData"):
        if _scale_values_equal(read_display_scale_combo_qt(combo), scale):
            return
        blocked = combo.blockSignals(True)
        try:
            set_display_scale_combo_qt(combo, scale)
        finally:
            combo.blockSignals(blocked)
        return
    set_display_scale_combo_gtk(combo, scale)


def read_display_scale_combo(combo: Any) -> float:
    if hasattr(combo, "count") and hasattr(combo, "itemData"):
        return read_display_scale_combo_qt(combo)
    return read_display_scale_combo_gtk(combo)

"""Display-scale preset controls for Qt compose panels."""

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


def set_display_scale_combo(combo: Any, scale: float | object) -> None:
    if _scale_values_equal(read_display_scale_combo_qt(combo), scale):
        return
    blocked = combo.blockSignals(True)
    try:
        set_display_scale_combo_qt(combo, scale)
    finally:
        combo.blockSignals(blocked)


def read_display_scale_combo(combo: Any) -> float:
    return read_display_scale_combo_qt(combo)

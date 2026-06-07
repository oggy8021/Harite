"""Main tab action cluster surface helpers (P-04)."""

from __future__ import annotations

from typing import Any

from harite.apply_surface import apply_mode_help_text
from harite.gui.views.margins_surface import apply_widget_tooltip


def apply_mode_tooltip_text(mode: str, *, windows_apply_span: bool = False) -> str:
    return apply_mode_help_text(mode, windows_apply_span=windows_apply_span)


def apply_apply_mode_tooltips(
    *,
    rad_single: Any,
    rad_per_monitor: Any,
    mode: str,
    apply_btn: Any | None = None,
    windows_apply_span: bool = False,
) -> None:
    text = apply_mode_tooltip_text(mode, windows_apply_span=windows_apply_span)
    for widget in (rad_single, rad_per_monitor, apply_btn):
        apply_widget_tooltip(widget, text)


def _resolve_apply_mode_widgets(backend: Any) -> tuple[Any | None, Any | None, Any | None]:
    objects = getattr(backend, "_objects", {})
    rad_single = objects.get("radApplySingle") or objects.get("rad_apply_single")
    rad_per_monitor = objects.get("radApplyPerMonitor") or objects.get("rad_apply_per_monitor")
    apply_btn = objects.get("btnSetWall") or objects.get("apply_btn")
    return rad_single, rad_per_monitor, apply_btn


def sync_apply_mode_tooltips(backend: Any, owner: Any | None, *, mode: str | None = None) -> None:
    normalized = str(mode or getattr(owner, "apply_mode", "single-file") or "single-file").strip().lower()
    span_opt_in = False
    if owner is not None:
        prefs = getattr(owner, "preferences", None)
        apply_prefs = getattr(prefs, "apply", None) if prefs is not None else None
        if apply_prefs is not None:
            span_opt_in = bool(getattr(apply_prefs, "windows_apply_span", False))
    rad_single, rad_per_monitor, apply_btn = _resolve_apply_mode_widgets(backend)
    apply_apply_mode_tooltips(
        rad_single=rad_single,
        rad_per_monitor=rad_per_monitor,
        apply_btn=apply_btn,
        mode=normalized,
        windows_apply_span=span_opt_in,
    )

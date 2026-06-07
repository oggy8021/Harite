"""Header flow legend helpers (phase highlight)."""

from __future__ import annotations

from typing import Any

FLOW_STEPS: tuple[str, ...] = ("Compose", "Optimize", "Apply")
FLOW_ARROW = " -> "


def flow_legend_active_step(owner: Any | None) -> str:
    """Return the step key to emphasize: compose | optimize | apply."""
    if owner is None:
        return "compose"

    phase = str(getattr(owner, "status_phase", "") or "").strip().lower()
    level = str(getattr(owner, "status_level", "") or "").strip().lower()
    message = str(getattr(owner, "status_message", "") or "").strip().lower()

    if phase == "apply" and level in {"success", "idle"} and "completed" in message:
        return "apply"
    if bool(getattr(owner, "can_apply", False)):
        return "optimize"
    if bool(getattr(owner, "can_optimize", False)):
        return "compose"
    return "compose"


def format_flow_legend_plain(*, active_step: str | None = None, owner: Any | None = None) -> str:
    _ = active_step
    return FLOW_ARROW.join(FLOW_STEPS)


def format_flow_legend_markup(*, owner: Any | None = None, active_step: str | None = None) -> str:
    active = (active_step or flow_legend_active_step(owner)).strip().lower()
    parts: list[str] = []
    for step in FLOW_STEPS:
        key = step.lower()
        if key == active:
            parts.append(f"<b>{step}</b>")
        else:
            parts.append(step)
    return FLOW_ARROW.join(parts)


def apply_flow_legend_markup(widget: Any, *, owner: Any | None = None, active_step: str | None = None) -> None:
    markup = format_flow_legend_markup(owner=owner, active_step=active_step)
    if widget is None:
        return
    if hasattr(widget, "set_markup"):
        widget.set_markup(markup)
        return
    if hasattr(widget, "setText"):
        try:
            from PyQt6.QtCore import Qt

            widget.setTextFormat(Qt.TextFormat.RichText)
        except ImportError:
            pass
        widget.setText(markup)
        return
    if hasattr(widget, "set_text"):
        widget.set_text(markup)

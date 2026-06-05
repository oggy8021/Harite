"""Slideshow options drawer toggle (C-04 Wave b)."""

from __future__ import annotations

from typing import Any

MORE_LABEL = "More slideshow options…"
FEWER_LABEL = "Fewer slideshow options…"


def _set_trigger_label(trigger: Any, *, expanded: bool) -> None:
    label = FEWER_LABEL if expanded else MORE_LABEL
    if hasattr(trigger, "setText"):
        trigger.setText(label)
        return
    if hasattr(trigger, "set_label"):
        trigger.set_label(label)
        return
    if hasattr(trigger, "set_text"):
        trigger.set_text(label)


def toggle_slideshow_options_drawer(backend: Any) -> None:
    """Show or hide the Slideshow tab auxiliary drawer (Qt + GTK)."""
    trigger = backend._objects.get("btn_slideshow_options_more")
    revealer = backend._objects.get("slideshow_options_revealer")
    if revealer is not None and hasattr(revealer, "get_reveal_child") and hasattr(revealer, "set_reveal_child"):
        expanded = not bool(revealer.get_reveal_child())
        revealer.set_reveal_child(expanded)
        _set_trigger_label(trigger, expanded=expanded)
        return

    drawer = backend._objects.get("slideshow_options_drawer")
    if drawer is None:
        return
    if hasattr(drawer, "isHidden"):
        expanded = bool(drawer.isHidden())
        if hasattr(drawer, "setVisible"):
            drawer.setVisible(expanded)
        _set_trigger_label(trigger, expanded=expanded)
        return
    if hasattr(drawer, "isVisible"):
        expanded = not drawer.isVisible()
        drawer.setVisible(expanded)
        _set_trigger_label(trigger, expanded=expanded)
        return
    if hasattr(drawer, "get_visible") and hasattr(drawer, "set_visible"):
        expanded = not bool(drawer.get_visible())
        drawer.set_visible(expanded)
        _set_trigger_label(trigger, expanded=expanded)

from __future__ import annotations

from typing import Any


def sync_non_preview_state_from_owner(backend: Any, owner: Any) -> None:
    backend._sync_input_state_from_owner(owner)
    backend._sync_main_state_from_owner(owner)
    backend._sync_margins_state_from_owner(owner)
    backend._sync_slideshow_state_from_owner(owner)
    backend._sync_feedback_from_owner(owner)
    from harite.gui.dual_display_ui import sync_dual_display_slot_availability_from_owner

    sync_dual_display_slot_availability_from_owner(backend, owner)


def sync_preview_state_from_owner(
    backend: Any,
    owner: Any,
    *,
    include_input: bool = False,
    include_feedback: bool = False,
) -> None:
    if include_input:
        backend._sync_input_state_from_owner(owner)
    backend._sync_result_preview_from_owner(owner)
    if include_feedback:
        backend._sync_feedback_from_owner(owner)


def sync_input_preview_state_from_owner(
    backend: Any,
    owner: Any,
    *,
    include_feedback: bool = False,
) -> None:
    sync_preview_state_from_owner(backend, owner, include_input=True, include_feedback=include_feedback)


def sync_margins_state_with_feedback_from_owner(backend: Any, owner: Any) -> None:
    backend._sync_margins_state_from_owner(owner)
    backend._sync_feedback_from_owner(owner)


def sync_slideshow_state_with_feedback_from_owner(backend: Any, owner: Any) -> None:
    backend._sync_slideshow_state_from_owner(owner)
    backend._sync_feedback_from_owner(owner)


def sync_slideshow_state_only_from_owner(backend: Any, owner: Any) -> None:
    backend._sync_slideshow_state_from_owner(owner)
from __future__ import annotations

from typing import Any, Callable


def run_optimize_clicked(backend: Any, callback: Callable[..., Any] | None) -> None:
    """Run optimize handler; feedback goes to footer via owner sync (P-04)."""
    if callback is None:
        backend._set_feedback(
            phase="Optimize",
            state="handler-missing",
            error="handler not connected",
        )
        backend._set_button_enabled("btnSetWall", False)
        return
    try:
        backend._set_feedback(phase="Optimize", state="running")
        ok = callback()
        backend._set_button_enabled("btnSetWall", bool(ok))
        owner = backend._get_handler_owner("on_optimize")
        if owner is not None:
            backend._sync_preview_state_from_owner(owner)
            backend._sync_action_availability_from_owner(owner)
            backend._sync_feedback_from_owner(owner)
        elif ok:
            backend._set_feedback(phase="Optimize", state="optimize completed")
        else:
            backend._set_feedback(
                phase="Optimize",
                state="optimize failed",
                error="optimize returned false",
            )
    except TypeError as exc:
        backend._set_button_enabled("btnSetWall", False)
        backend._set_feedback(phase="Optimize", state="error", error=str(exc))


def run_apply_clicked(backend: Any, callback: Callable[..., Any] | None) -> None:
    """Run apply handler; feedback goes to footer via owner sync (P-04)."""
    if callback is None:
        backend._set_feedback(
            phase="Apply",
            state="handler-missing",
            error="handler not connected",
        )
        return
    try:
        backend._set_feedback(phase="Apply", state="running")
        ok = callback()
        owner = backend._get_handler_owner("on_apply")
        if owner is not None:
            backend._sync_feedback_from_owner(owner)
        elif ok:
            backend._set_feedback(phase="Apply", state="wallpaper applied")
        else:
            backend._set_feedback(
                phase="Apply",
                state="apply failed",
                error="apply returned false",
            )
    except TypeError as exc:
        backend._set_feedback(phase="Apply", state="error", error=str(exc))

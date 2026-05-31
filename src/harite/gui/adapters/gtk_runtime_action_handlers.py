from __future__ import annotations

from typing import Any, Callable


def run_optimize_clicked(backend: Any, callback: Callable[..., Any] | None) -> None:
    """Run optimize handler and mirror result onto action-cluster labels (GTK/Qt shared)."""
    if callback is None:
        backend._set_feedback(
            phase="Optimize",
            state="handler-missing",
            error="handler not connected",
        )
        backend._set_button_enabled("btnSetWall", False)
        backend._set_label_text("lblOptimizeResult", "Optimize result: handler-missing")
        backend._set_label_text("lblApplyTarget", "Apply target: not-ready")
        return
    try:
        backend._set_feedback(phase="Optimize", state="running")
        ok = callback()
        backend._set_button_enabled("btnSetWall", bool(ok))
        owner = backend._get_handler_owner("on_optimize")
        if ok:
            if owner is not None:
                backend._sync_preview_state_from_owner(owner)
                backend._sync_action_availability_from_owner(owner)
            backend._set_feedback(phase="Optimize", state="ok")
            backend._set_label_text("lblOptimizeResult", "Optimize result: success")
            backend._set_label_text("lblApplyTarget", "Apply target: ready")
        else:
            if owner is not None:
                backend._sync_preview_state_from_owner(owner)
                backend._sync_action_availability_from_owner(owner)
            backend._set_feedback(
                phase="Optimize",
                state="failed",
                error="optimize returned false",
            )
            backend._set_label_text("lblOptimizeResult", "Optimize result: failed")
            backend._set_label_text("lblApplyTarget", "Apply target: not-ready")
    except TypeError as exc:
        backend._set_button_enabled("btnSetWall", False)
        backend._set_feedback(phase="Optimize", state="error", error=str(exc))
        backend._set_label_text("lblOptimizeResult", "Optimize result: error")
        backend._set_label_text("lblApplyTarget", "Apply target: not-ready")


def run_apply_clicked(backend: Any, callback: Callable[..., Any] | None) -> None:
    """Run apply handler and mirror result onto action-cluster labels (GTK/Qt shared)."""
    if callback is None:
        backend._set_feedback(
            phase="Apply",
            state="handler-missing",
            error="handler not connected",
        )
        backend._set_label_text("lblApplyTarget", "Apply target: handler-missing")
        return
    try:
        backend._set_feedback(phase="Apply", state="running")
        ok = callback()
        if ok:
            backend._set_feedback(phase="Apply", state="ok")
            backend._set_label_text("lblApplyTarget", "Apply target: last applied")
        else:
            backend._set_feedback(
                phase="Apply",
                state="failed",
                error="apply returned false",
            )
    except TypeError as exc:
        backend._set_feedback(phase="Apply", state="error", error=str(exc))

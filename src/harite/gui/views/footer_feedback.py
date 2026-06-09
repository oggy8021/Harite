"""Footer status/error label formatting (C-04 Wave 0).

Maps internal ``phase`` / ``state`` / ``error`` trace fields to user-facing
footer labels.  Shared by GTK and Qt widget helpers.
"""

from __future__ import annotations

from typing import Any

STATUS_READY = "Status: ready"
ERROR_NONE = "Error: none"

# MAT-13: active footer errors — shared by Qt stylesheet and GTK CSS.
FOOTER_ERROR_ACTIVE_COLOR = "#c62828"
FOOTER_ERROR_IDLE_COLOR = "#888888"

_TRACE_STATES = frozenset(
    {
        "planned",
        "updated",
        "cleared",
        "ok",
        "selected",
        "dialog-open",
        "canceled",
        "opened",
        "closed",
        "deferred",
        "unavailable",
        "stop-ignored",
        "stopped",
        "started",
        "applied",
        "saved",
        "input ready",
        "failed",
        "error",
        "handler-missing",
        "info-error",
        "text-error",
        "position-error",
        "max-lines-error",
        "start-failed",
        "interval-failed",
        "dialog-unavailable",
        "clear-rejected",
        "path-required",
        "state-updated",
        "ready",
        "info-updated",
        "text-updated",
        "position-updated",
        "max-lines-updated",
        "info-rejected",
        "text-rejected",
        "position-rejected",
        "max-lines-rejected",
        "rejected",
        "margin text off",
        "running",
    }
)

_ERROR_LEVELS = frozenset({"error"})
_SUPPRESS_STATUS_LEVELS = frozenset({"error", "paused"})


def _normalized(value: str | None) -> str:
    return str(value or "").strip()


def _is_trace_state(state: str) -> bool:
    if not state:
        return True
    if state in _TRACE_STATES:
        return True
    return state.startswith("interval-updated(")


_FAILURE_STATE_SUFFIXES = ("-failed", "-rejected", "-error", "-missing")


def _is_failure_state(state: str) -> bool:
    if not state:
        return False
    if state == "failed":
        return True
    return any(state.endswith(suffix) for suffix in _FAILURE_STATE_SUFFIXES)


def _format_failure_state_message(state: str) -> str:
    return state.replace("-", " ")


def format_footer_status(
    *,
    phase: str,
    state: str,
    error: str | None = None,
    status_level: str | None = None,
) -> str:
    """Return the full ``lblStatus`` text (includes ``Status:`` prefix)."""
    _ = phase
    level = _normalized(status_level).lower()
    if level in _SUPPRESS_STATUS_LEVELS:
        return STATUS_READY
    if _normalized(error):
        return STATUS_READY
    state_s = _normalized(state)
    if _is_trace_state(state_s):
        return STATUS_READY
    return f"Status: {state_s}"


def format_footer_error(
    *,
    phase: str,
    state: str,
    error: str | None = None,
    status_level: str | None = None,
) -> str:
    """Return the full ``lblError`` text (includes ``Error:`` prefix)."""
    _ = phase
    error_s = _normalized(error)
    if error_s:
        return f"Error: {error_s}"
    state_s = _normalized(state)
    if state_s == "dialog-unavailable":
        return "Error: Could not open file dialog"
    if _is_failure_state(state_s):
        return f"Error: {_format_failure_state_message(state_s)}"
    level = _normalized(status_level).lower()
    if level in _ERROR_LEVELS and state_s and not _is_trace_state(state_s):
        return f"Error: {state_s}"
    return ERROR_NONE


def footer_error_is_active(error_text: str) -> bool:
    return _normalized(error_text) not in {"", ERROR_NONE}


def configure_footer_error_label_qt(label: Any) -> None:
    """Footer error row: selectable text + wrap (~2 lines) on Qt."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QSizePolicy

    label.setWordWrap(True)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


def configure_footer_error_label_gtk(label: Any) -> None:
    """Footer error row: selectable text + wrap on GTK."""
    if hasattr(label, "set_selectable"):
        label.set_selectable(True)
    if hasattr(label, "set_wrap"):
        label.set_wrap(True)
    if hasattr(label, "set_wrap_mode"):
        label.set_wrap_mode(2)  # Pango.WrapMode.WORD

"""Qt margin text input helpers (MAT-07)."""

from __future__ import annotations

from typing import Any

from harite.gui.adapters.gtk_runtime_margin_text import (
    read_margin_text_widget_text,
    should_block_margin_text_return,
)

_MARGIN_TEXT_MAX_LINES = 5


def install_margin_text_key_handler(entry: Any) -> None:
    """Block Enter at the line cap and avoid redundant plain-text resets elsewhere."""
    try:
        from PyQt6.QtCore import QEvent, QObject, Qt
    except ImportError:
        return

    class _MarginTextEnterGuard(QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:  # noqa: N802
            if watched is not entry or event.type() != QEvent.Type.KeyPress:
                return False
            if event.key() not in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
                return False
            current = read_margin_text_widget_text(entry)
            return should_block_margin_text_return(
                keyval=event.key(),
                return_keys={Qt.Key.Key_Return, Qt.Key.Key_Enter},
                current_text=current,
                max_lines=_MARGIN_TEXT_MAX_LINES,
            )

    guard = _MarginTextEnterGuard(entry)
    entry.installEventFilter(guard)
    entry._harite_margin_text_enter_guard = guard  # prevent GC

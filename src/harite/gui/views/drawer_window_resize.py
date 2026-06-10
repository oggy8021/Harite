"""Resize the top-level window frame when a fixed-layout drawer opens or closes."""

from __future__ import annotations

from typing import Any, Callable


def _resolve_top_level_window(backend: Any) -> Any | None:
    objects = getattr(backend, "_objects", None)
    if isinstance(objects, dict):
        window = objects.get("main_window")
        if window is not None:
            return window
    for attr in ("qwindow", "_qwindow"):
        window = getattr(backend, attr, None)
        if window is not None:
            return window
    return None


def _read_window_width(window: Any) -> int | None:
    if hasattr(window, "width"):
        try:
            return int(window.width())
        except (TypeError, ValueError):
            pass
    if hasattr(window, "get_size"):
        try:
            size = window.get_size()
            return int(size[0])
        except (TypeError, ValueError, IndexError):
            pass
    return None


def _read_window_height(window: Any) -> int | None:
    if hasattr(window, "height"):
        try:
            return int(window.height())
        except (TypeError, ValueError):
            pass
    if hasattr(window, "get_size"):
        try:
            size = window.get_size()
            return int(size[1])
        except (TypeError, ValueError, IndexError):
            pass
    return None


def _content_fit_window_height(window: Any) -> int | None:
    if hasattr(window, "minimumSizeHint"):
        try:
            return int(window.minimumSizeHint().height())
        except (TypeError, ValueError, AttributeError):
            pass
    if hasattr(window, "get_preferred_height"):
        try:
            return int(window.get_preferred_height()[1])
        except (TypeError, ValueError, IndexError, AttributeError):
            pass
    if hasattr(window, "get_size_request"):
        try:
            request = window.get_size_request()
            return int(request[1])
        except (TypeError, ValueError, IndexError, AttributeError):
            pass
    return None


def _set_window_height(window: Any, height: int) -> None:
    width = _read_window_width(window)
    if hasattr(window, "resize") and width is not None:
        window.resize(width, int(height))
        return
    if hasattr(window, "set_default_size") and width is not None:
        window.set_default_size(width, int(height))


def _flush_qt_layout() -> None:
    try:
        from PyQt6.QtWidgets import QApplication
    except Exception:
        return
    app = QApplication.instance()
    if app is not None and hasattr(app, "processEvents"):
        app.processEvents()


def _schedule_on_next_event_loop(callback: Callable[[], None]) -> bool:
    try:
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QApplication

        if QApplication.instance() is not None:
            QTimer.singleShot(0, callback)
            return True
    except Exception:
        pass
    return False


def _apply_content_fit_grow(window: Any) -> bool:
    """Grow the window when drawer content needs more vertical space."""
    _flush_qt_layout()
    needed = _content_fit_window_height(window)
    current = _read_window_height(window)
    if needed is not None and current is not None and needed > current:
        _set_window_height(window, needed)
        _flush_qt_layout()
        return True
    return False


def _clear_qt_window_minimum_height(window: Any) -> None:
    if hasattr(window, "setMinimumHeight"):
        try:
            window.setMinimumHeight(0)
        except Exception:
            return


def _apply_content_fit_shrink(window: Any) -> bool:
    """Shrink the window when extra vertical space remains after drawer close."""
    _flush_qt_layout()
    compact = _content_fit_window_height(window)
    current = _read_window_height(window)
    if compact is None or current is None or current <= compact:
        return False
    _clear_qt_window_minimum_height(window)
    _set_window_height(window, compact)
    _flush_qt_layout()
    after = _read_window_height(window)
    return after is not None and after <= compact


def _read_tab_minimum_height(tab: Any) -> int | None:
    if hasattr(tab, "minimumSizeHint"):
        try:
            return int(tab.minimumSizeHint().height())
        except (TypeError, ValueError, AttributeError):
            pass
    return None


def _tab_compact_hint_attr(tab_attr: str) -> str:
    return f"{tab_attr}_drawer_compact_hint"


def save_tab_compact_hint_before_expand(backend: Any, *, tab_attr: str) -> None:
    """Capture tab content height while the drawer is still collapsed."""
    hint_attr = _tab_compact_hint_attr(tab_attr)
    if hasattr(backend, hint_attr):
        return
    tab = backend._objects.get(tab_attr)
    height = _read_tab_minimum_height(tab) if tab is not None else None
    if height is not None:
        setattr(backend, hint_attr, height)


def _clear_tab_compact_hint(backend: Any, *, tab_attr: str | None) -> None:
    if not tab_attr:
        return
    hint_attr = _tab_compact_hint_attr(tab_attr)
    if hasattr(backend, hint_attr):
        delattr(backend, hint_attr)


def _apply_tab_content_delta_grow(backend: Any, window: Any, *, tab_attr: str) -> bool:
    """Grow by tab-content delta when the window already exceeds minimumSizeHint."""
    hint_attr = _tab_compact_hint_attr(tab_attr)
    compact = getattr(backend, hint_attr, None)
    tab = backend._objects.get(tab_attr)
    if compact is None or tab is None:
        return False
    try:
        compact_height = int(compact)
    except (TypeError, ValueError):
        return False
    _flush_qt_layout()
    current_tab = _read_tab_minimum_height(tab)
    current_win = _read_window_height(window)
    if current_tab is None or current_win is None:
        return False
    delta = current_tab - compact_height
    if delta <= 0:
        return False
    _set_window_height(window, current_win + delta)
    _flush_qt_layout()
    return True


def _grow_top_level_window_to_content_fit(window: Any) -> None:
    if _apply_content_fit_grow(window):
        return

    def _retry() -> None:
        _apply_content_fit_grow(window)

    if not _schedule_on_next_event_loop(_retry):
        _apply_content_fit_grow(window)


def _shrink_top_level_window_to_content_fit(
    window: Any,
    *,
    saved_height: int | None = None,
    max_attempts: int = 16,
) -> None:
    attempts = {"remaining": max_attempts}

    def _target_height() -> int | None:
        if saved_height is not None:
            return saved_height
        return _content_fit_window_height(window)

    def _apply_target_shrink() -> bool:
        target = _target_height()
        current = _read_window_height(window)
        if target is None or current is None or current <= target:
            return current is not None and target is not None and current <= target
        _clear_qt_window_minimum_height(window)
        _set_window_height(window, target)
        _flush_qt_layout()
        after = _read_window_height(window)
        return after is not None and after <= target

    def _try_shrink() -> bool:
        if saved_height is not None:
            return _apply_target_shrink()
        if _apply_content_fit_shrink(window):
            return True
        return _apply_target_shrink()

    def _attempt() -> None:
        if _try_shrink():
            return
        attempts["remaining"] -= 1
        if attempts["remaining"] <= 0:
            return
        if not _schedule_on_next_event_loop(_attempt):
            _attempt()

    if _try_shrink():
        return
    _attempt()


def grow_window_after_drawer_expand(
    backend: Any,
    *,
    state_attr: str | None = None,
    tab_attr: str | None = None,
) -> None:
    """Option B: keep tab content fixed; grow the window frame for drawer content."""
    window = _resolve_top_level_window(backend)
    if window is None:
        return
    if state_attr is not None and not hasattr(backend, state_attr):
        current = _read_window_height(window)
        if current is not None:
            setattr(backend, state_attr, current)
    if tab_attr is not None and _apply_tab_content_delta_grow(backend, window, tab_attr=tab_attr):
        return
    _grow_top_level_window_to_content_fit(window)


def shrink_window_after_drawer_collapse(
    backend: Any,
    *,
    state_attr: str,
    tab_attr: str | None = None,
) -> None:
    """Option B: remove drawer slack from the window frame after collapse."""
    saved_height = getattr(backend, state_attr, None)
    if isinstance(saved_height, bool) or saved_height is not None:
        try:
            saved_height = int(saved_height)
        except (TypeError, ValueError):
            saved_height = None
    window = _resolve_top_level_window(backend)
    if window is None:
        if hasattr(backend, state_attr):
            delattr(backend, state_attr)
        _clear_tab_compact_hint(backend, tab_attr=tab_attr)
        return
    _shrink_top_level_window_to_content_fit(window, saved_height=saved_height)
    if hasattr(backend, state_attr):
        delattr(backend, state_attr)
    _clear_tab_compact_hint(backend, tab_attr=tab_attr)


# Backward-compatible aliases used by slideshow drawer (collapse only).
def restore_window_height_after_drawer_collapse(backend: Any, *, state_attr: str) -> None:
    shrink_window_after_drawer_collapse(backend, state_attr=state_attr)


def sync_drawer_window_height(backend: Any, *, expanded: bool, state_attr: str) -> None:
    if expanded:
        return
    shrink_window_after_drawer_collapse(backend, state_attr=state_attr)

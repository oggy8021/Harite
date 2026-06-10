"""Slideshow options drawer toggle (C-04 Wave b, P-07 open-state styling)."""

from __future__ import annotations

from typing import Any

MORE_LABEL = "More slideshow options…"
FEWER_LABEL = "Fewer slideshow options…"

QT_DRAWER_OBJECT_NAME = "hariteSlideshowOptionsDrawer"
QT_TRIGGER_OBJECT_NAME = "hariteSlideshowOptionsTrigger"

_SLIDESHOW_DRAWER_SAVED_WINDOW_HEIGHT = "_slideshow_options_drawer_saved_window_height"


def _set_trigger_label(trigger: Any, *, expanded: bool) -> None:
    if trigger is None or not hasattr(trigger, "setText"):
        return
    trigger.setText(FEWER_LABEL if expanded else MORE_LABEL)


def _chevron_icon_name(*, expanded: bool) -> str:
    return "arrow-up.svg" if expanded else "arrow-down.svg"


def _set_trigger_chevron(trigger: Any, *, expanded: bool) -> None:
    if trigger is None or not hasattr(trigger, "setIcon"):
        return
    from harite.gui.resource_access import set_qt_button_icon

    set_qt_button_icon(trigger, "icons", "lucide", _chevron_icon_name(expanded=expanded))


def _qt_widget_palette(widget: Any | None) -> Any:
    from PyQt6.QtWidgets import QApplication

    if widget is not None:
        return widget.palette()
    return QApplication.palette()


def _qt_chrome_tint_color(palette: Any, *, ratio: float = 0.06) -> Any:
    """Drawer chrome tint: mix(window bg, window text, ratio)."""
    from PyQt6.QtGui import QColor, QPalette

    bg = palette.color(QPalette.ColorRole.Window)
    fg = palette.color(QPalette.ColorRole.WindowText)

    def _mix(channel: str) -> int:
        b = getattr(bg, channel)()
        f = getattr(fg, channel)()
        return max(0, min(255, round(b * (1.0 - ratio) + f * ratio)))

    return QColor(_mix("red"), _mix("green"), _mix("blue"))


def _qt_trigger_expanded_stylesheet(trigger: Any | None) -> str:
    from PyQt6.QtGui import QPalette

    palette = _qt_widget_palette(trigger)
    chrome = _qt_chrome_tint_color(palette).name()
    mid = palette.color(QPalette.ColorRole.Mid).name()
    return (
        f"QPushButton#{QT_TRIGGER_OBJECT_NAME}Expanded {{"
        f"background-color: {chrome};"
        f"border-top: 1px solid {mid};"
        f"border-left: 1px solid {mid};"
        f"border-right: 1px solid {mid};"
        "border-bottom-width: 0px;"
        "padding: 4px 12px;"
        "}"
    )


def _qt_set_drawer_panel_palette(drawer: Any, *, expanded: bool) -> None:
    """Paint drawer chrome via QPalette only — avoids QSS cascading to children."""
    from PyQt6.QtGui import QPalette
    from PyQt6.QtWidgets import QApplication

    if not hasattr(drawer, "setAutoFillBackground"):
        return
    if expanded:
        palette = drawer.palette()
        chrome = _qt_chrome_tint_color(palette)
        palette.setColor(QPalette.ColorRole.Window, chrome)
        drawer.setPalette(palette)
        drawer.setAutoFillBackground(True)
        return

    drawer.setAutoFillBackground(False)
    parent = drawer.parent() if hasattr(drawer, "parent") else None
    if parent is not None:
        drawer.setPalette(parent.palette())
    else:
        drawer.setPalette(QApplication.palette())


def _qt_set_drawer_layout_margins(drawer: Any, *, expanded: bool) -> None:
    layout = drawer.layout() if hasattr(drawer, "layout") else None
    if layout is None or not hasattr(layout, "setContentsMargins"):
        return
    if expanded:
        layout.setContentsMargins(8, 4, 8, 0)
    else:
        layout.setContentsMargins(0, 8, 0, 0)


def _qt_set_drawer_top_border(top_border: Any | None, drawer: Any | None, *, expanded: bool) -> None:
    if top_border is None:
        return
    if hasattr(top_border, "setVisible"):
        top_border.setVisible(expanded)
    if not expanded:
        if hasattr(top_border, "setStyleSheet"):
            top_border.setStyleSheet("")
        return
    from PyQt6.QtGui import QPalette

    palette = _qt_widget_palette(drawer)
    mid = palette.color(QPalette.ColorRole.Mid).name()
    if hasattr(top_border, "setStyleSheet"):
        top_border.setStyleSheet(f"background-color: {mid}; border: none; min-height: 1px; max-height: 1px;")


def _apply_qt_drawer_open_state(
    drawer: Any | None,
    trigger: Any | None,
    *,
    expanded: bool,
    top_border: Any | None = None,
) -> None:
    if drawer is not None and hasattr(drawer, "setStyleSheet"):
        drawer.setObjectName(f"{QT_DRAWER_OBJECT_NAME}Expanded" if expanded else QT_DRAWER_OBJECT_NAME)
        drawer.setStyleSheet("")
        _qt_set_drawer_panel_palette(drawer, expanded=expanded)
        _qt_set_drawer_layout_margins(drawer, expanded=expanded)
        _qt_set_drawer_top_border(top_border, drawer, expanded=expanded)
    if trigger is not None and hasattr(trigger, "setStyleSheet"):
        if expanded:
            trigger.setObjectName(f"{QT_TRIGGER_OBJECT_NAME}Expanded")
            trigger.setStyleSheet(_qt_trigger_expanded_stylesheet(trigger))
        else:
            trigger.setObjectName(QT_TRIGGER_OBJECT_NAME)
            trigger.setStyleSheet("")
    _set_trigger_chevron(trigger, expanded=expanded)


def apply_slideshow_options_drawer_open_state(backend: Any, *, expanded: bool) -> None:
    """Update drawer/trigger visuals for expanded or collapsed state."""
    drawer = backend._objects.get("slideshow_options_drawer")
    trigger = backend._objects.get("btn_slideshow_options_more")
    top_border = backend._objects.get("slideshow_options_drawer_top_border")
    _set_trigger_label(trigger, expanded=expanded)
    _apply_qt_drawer_open_state(drawer, trigger, expanded=expanded, top_border=top_border)


def _sync_slideshow_drawer_window_frame(backend: Any, *, expanded: bool) -> None:
    from harite.gui.views.drawer_window_resize import (
        grow_window_after_drawer_expand,
        shrink_window_after_drawer_collapse,
    )

    if expanded:
        grow_window_after_drawer_expand(
            backend,
            state_attr=_SLIDESHOW_DRAWER_SAVED_WINDOW_HEIGHT,
            tab_attr="slideshow_tab_box",
        )
        return
    shrink_window_after_drawer_collapse(
        backend,
        state_attr=_SLIDESHOW_DRAWER_SAVED_WINDOW_HEIGHT,
        tab_attr="slideshow_tab_box",
    )


def _set_drawer_expanded(backend: Any, *, expanded: bool) -> None:
    if expanded:
        from harite.gui.views.drawer_window_resize import save_tab_compact_hint_before_expand

        save_tab_compact_hint_before_expand(backend, tab_attr="slideshow_tab_box")
    setattr(backend, "_slideshow_options_drawer_expanded", expanded)
    drawer = backend._objects.get("slideshow_options_drawer")
    if drawer is None or not hasattr(drawer, "setVisible"):
        return
    drawer.setVisible(expanded)
    apply_slideshow_options_drawer_open_state(backend, expanded=expanded)
    _sync_slideshow_drawer_window_frame(backend, expanded=expanded)


def _is_drawer_expanded(backend: Any) -> bool:
    if hasattr(backend, "_slideshow_options_drawer_expanded"):
        return bool(getattr(backend, "_slideshow_options_drawer_expanded"))

    drawer = backend._objects.get("slideshow_options_drawer")
    if drawer is None or not hasattr(drawer, "isVisible"):
        return False
    return bool(drawer.isVisible())


def toggle_slideshow_options_drawer(backend: Any) -> None:
    """Show or hide the Slideshow tab auxiliary drawer."""
    _set_drawer_expanded(backend, expanded=not _is_drawer_expanded(backend))

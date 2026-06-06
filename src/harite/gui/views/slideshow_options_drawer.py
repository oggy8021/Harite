"""Slideshow options drawer toggle (C-04 Wave b, P-07 open-state styling)."""

from __future__ import annotations

from typing import Any

MORE_LABEL = "More slideshow options…"
FEWER_LABEL = "Fewer slideshow options…"

QT_DRAWER_OBJECT_NAME = "hariteSlideshowOptionsDrawer"
QT_TRIGGER_OBJECT_NAME = "hariteSlideshowOptionsTrigger"

GTK_DRAWER_STYLE_CLASS = "harite-slideshow-options-drawer-expanded"
GTK_TRIGGER_STYLE_CLASS = "harite-slideshow-options-trigger-expanded"

_GTK_DRAWER_CSS = b"""
.harite-slideshow-options-drawer-expanded {
  background-color: mix(@theme_bg_color, @theme_fg_color, 0.06);
  border-top: 1px solid @borders;
  padding-left: 8px;
  padding-right: 8px;
}
button.harite-slideshow-options-trigger-expanded {
  background-color: mix(@theme_bg_color, @theme_fg_color, 0.06);
  border: 1px solid @borders;
  border-bottom: none;
}
"""

_gtk_drawer_css_loaded = False


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


def _chevron_icon_name(*, expanded: bool) -> str:
    return "arrow-up.svg" if expanded else "arrow-down.svg"


def _set_trigger_chevron(trigger: Any, *, expanded: bool) -> None:
    if trigger is None:
        return
    icon_name = _chevron_icon_name(expanded=expanded)
    if hasattr(trigger, "setIcon"):
        from harite.gui.resource_access import set_qt_button_icon

        set_qt_button_icon(trigger, "icons", "lucide", icon_name)
        return
    if hasattr(trigger, "set_image"):
        try:
            from harite.gui.adapters.gtk_layout_builders import set_button_icon_if_supported

            import gi

            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk

            set_button_icon_if_supported(Gtk, trigger, "icons", "lucide", icon_name)
        except Exception:
            return


def _ensure_gtk_drawer_styles() -> None:
    global _gtk_drawer_css_loaded
    if _gtk_drawer_css_loaded:
        return
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except Exception:
        return

    css_provider_cls = getattr(Gtk, "CssProvider", None)
    style_context_cls = getattr(Gtk, "StyleContext", None)
    if css_provider_cls is None or style_context_cls is None:
        return
    try:
        provider = css_provider_cls()
        provider.load_from_data(_GTK_DRAWER_CSS)
        screen = None
        gdk = getattr(Gtk, "gdk", None)
        if gdk is not None:
            screen_getter = getattr(getattr(gdk, "Screen", None), "get_default", None)
            if screen_getter is not None:
                screen = screen_getter()
        priority = getattr(Gtk, "STYLE_PROVIDER_PRIORITY_APPLICATION", 600)
        if screen is not None:
            style_context_cls.add_provider_for_screen(screen, provider, priority)
        _gtk_drawer_css_loaded = True
    except Exception:
        return


def _gtk_style_context(widget: Any) -> Any | None:
    getter = getattr(widget, "get_style_context", None)
    if getter is None:
        return None
    try:
        return getter()
    except Exception:
        return None


def _gtk_toggle_class(widget: Any, class_name: str, *, enabled: bool) -> None:
    ctx = _gtk_style_context(widget)
    if ctx is None:
        return
    add_class = getattr(ctx, "add_class", None)
    remove_class = getattr(ctx, "remove_class", None)
    if not add_class or not remove_class:
        return
    if enabled:
        add_class(class_name)
    else:
        remove_class(class_name)


def _qt_widget_palette(widget: Any | None) -> Any:
    from PyQt6.QtWidgets import QApplication

    if widget is not None:
        return widget.palette()
    return QApplication.palette()


def _qt_trigger_expanded_stylesheet(trigger: Any | None) -> str:
    from PyQt6.QtGui import QPalette

    palette = _qt_widget_palette(trigger)
    alternate = palette.color(QPalette.ColorRole.AlternateBase).name()
    mid = palette.color(QPalette.ColorRole.Mid).name()
    return (
        f"QPushButton#{QT_TRIGGER_OBJECT_NAME}Expanded {{"
        f"background-color: {alternate};"
        f"border: 1px solid {mid};"
        "border-bottom: none;"
        "padding: 4px 12px;"
        "}}"
    )


def _qt_set_drawer_panel_palette(drawer: Any, *, expanded: bool) -> None:
    """Paint drawer chrome via QPalette only — avoids QSS cascading to children."""
    from PyQt6.QtGui import QPalette
    from PyQt6.QtWidgets import QApplication

    if not hasattr(drawer, "setAutoFillBackground"):
        return
    if expanded:
        palette = drawer.palette()
        alternate = palette.color(QPalette.ColorRole.AlternateBase)
        palette.setColor(QPalette.ColorRole.Window, alternate)
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


def _apply_gtk_drawer_open_state(drawer: Any | None, trigger: Any | None, *, expanded: bool) -> None:
    if drawer is None and trigger is None:
        return
    if drawer is not None and not hasattr(drawer, "setStyleSheet"):
        _ensure_gtk_drawer_styles()
        _gtk_toggle_class(drawer, GTK_DRAWER_STYLE_CLASS, enabled=expanded)
    if trigger is not None and not hasattr(trigger, "setStyleSheet"):
        _gtk_toggle_class(trigger, GTK_TRIGGER_STYLE_CLASS, enabled=expanded)
        _set_trigger_chevron(trigger, expanded=expanded)


def apply_slideshow_options_drawer_open_state(backend: Any, *, expanded: bool) -> None:
    """Update drawer/trigger visuals for expanded or collapsed state (Qt + GTK)."""
    drawer = backend._objects.get("slideshow_options_drawer")
    trigger = backend._objects.get("btn_slideshow_options_more")
    top_border = backend._objects.get("slideshow_options_drawer_top_border")
    _set_trigger_label(trigger, expanded=expanded)
    _apply_qt_drawer_open_state(drawer, trigger, expanded=expanded, top_border=top_border)
    _apply_gtk_drawer_open_state(drawer, trigger, expanded=expanded)


def _set_drawer_expanded(backend: Any, *, expanded: bool) -> None:
    setattr(backend, "_slideshow_options_drawer_expanded", expanded)
    revealer = backend._objects.get("slideshow_options_revealer")
    if revealer is not None and hasattr(revealer, "set_reveal_child"):
        revealer.set_reveal_child(expanded)
        apply_slideshow_options_drawer_open_state(backend, expanded=expanded)
        return

    drawer = backend._objects.get("slideshow_options_drawer")
    if drawer is None:
        return
    if hasattr(drawer, "setVisible"):
        drawer.setVisible(expanded)
        apply_slideshow_options_drawer_open_state(backend, expanded=expanded)
        return
    if hasattr(drawer, "set_visible"):
        drawer.set_visible(expanded)
        apply_slideshow_options_drawer_open_state(backend, expanded=expanded)


def _is_drawer_expanded(backend: Any) -> bool:
    if hasattr(backend, "_slideshow_options_drawer_expanded"):
        return bool(getattr(backend, "_slideshow_options_drawer_expanded"))

    revealer = backend._objects.get("slideshow_options_revealer")
    if revealer is not None and hasattr(revealer, "get_reveal_child"):
        return bool(revealer.get_reveal_child())

    drawer = backend._objects.get("slideshow_options_drawer")
    if drawer is None:
        return False
    if hasattr(drawer, "isVisible"):
        return bool(drawer.isVisible())
    if hasattr(drawer, "get_visible"):
        return bool(drawer.get_visible())
    return False


def toggle_slideshow_options_drawer(backend: Any) -> None:
    """Show or hide the Slideshow tab auxiliary drawer (Qt + GTK)."""
    _set_drawer_expanded(backend, expanded=not _is_drawer_expanded(backend))

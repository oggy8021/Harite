from __future__ import annotations

from importlib import import_module
from importlib.resources import files
from typing import Any


def initialize_tasktray(signal_backend: Any) -> Any | None:
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import GLib, Gtk
    except Exception as exc:
        raise RuntimeError(f"PyGObject/GTK unavailable: {exc}") from exc

    indicator_binding = _load_indicator_binding()
    if indicator_binding is None:
        raise RuntimeError("AppIndicator binding unavailable: tried AyatanaAppIndicator3, AppIndicator3")
    if not hasattr(signal_backend, "get_object"):
        raise RuntimeError("signal backend does not provide get_object(name)")

    window = _resolve_main_window(signal_backend)
    if window is None:
        raise RuntimeError("main GTK window not found for task tray binding")

    indicator_module, binding_name = indicator_binding
    adapter = GtkTaskTrayAdapter(
        gtk_module=Gtk,
        glib_module=GLib,
        indicator_module=indicator_module,
        binding_name=binding_name,
        signal_backend=signal_backend,
        window=window,
    )
    adapter.install()
    return adapter


def _load_indicator_binding() -> tuple[Any, str] | None:
    try:
        import gi
    except Exception:
        return None

    for binding_name in ("AyatanaAppIndicator3", "AppIndicator3"):
        try:
            gi.require_version(binding_name, "0.1")
            return import_module(f"gi.repository.{binding_name}"), binding_name
        except Exception:
            continue
    return None


def _resolve_main_window(signal_backend: Any) -> Any | None:
    for candidate in ("WallPosit_MainWindow", "main_window"):
        window = signal_backend.get_object(candidate)
        if window is not None:
            return window

    if hasattr(signal_backend, "get_objects"):
        for obj in signal_backend.get_objects():
            if obj.__class__.__name__.endswith("Window"):
                return obj
    return None


class GtkTaskTrayAdapter:
    def __init__(
        self,
        *,
        gtk_module: Any,
        glib_module: Any,
        indicator_module: Any,
        binding_name: str,
        signal_backend: Any,
        window: Any,
    ) -> None:
        self._gtk = gtk_module
        self._glib = glib_module
        self._indicator_module = indicator_module
        self._binding_name = binding_name
        self._signal_backend = signal_backend
        self._window = window
        self._indicator: Any | None = None
        self._menu: Any | None = None
        self._visible_item: Any | None = None
        self._watch_start_item: Any | None = None
        self._watch_stop_item: Any | None = None

    def install(self) -> None:
        menu = self._build_menu()
        indicator = self._create_indicator()
        if indicator is None:
            return

        self._menu = menu
        self._indicator = indicator
        if hasattr(indicator, "set_menu"):
            indicator.set_menu(menu)

        active_status = getattr(getattr(self._indicator_module, "IndicatorStatus", object()), "ACTIVE", None)
        if active_status is not None and hasattr(indicator, "set_status"):
            indicator.set_status(active_status)

        if hasattr(menu, "show_all"):
            menu.show_all()
        if hasattr(menu, "connect"):
            menu.connect("show", lambda *_args: self.refresh())
        if hasattr(self._window, "connect"):
            self._window.connect("show", lambda *_args: self.refresh())
            self._window.connect("hide", lambda *_args: self.refresh())

        self._glib.timeout_add_seconds(1, self._poll_state)
        self.refresh()

    def _build_menu(self) -> Any:
        menu = self._gtk.Menu()

        self._visible_item = self._gtk.MenuItem(label="Visible")
        self._visible_item.connect("activate", self._on_toggle_visibility)
        menu.append(self._visible_item)

        self._watch_start_item = self._gtk.MenuItem(label="Start Watch")
        self._watch_start_item.connect("activate", self._on_watch_start)
        menu.append(self._watch_start_item)

        self._watch_stop_item = self._gtk.MenuItem(label="Stop Watch")
        self._watch_stop_item.connect("activate", self._on_watch_stop)
        menu.append(self._watch_stop_item)

        separator = self._gtk.SeparatorMenuItem()
        menu.append(separator)

        settings_item = self._gtk.MenuItem(label="Settings")
        settings_item.connect("activate", self._on_open_settings)
        menu.append(settings_item)

        color_item = self._gtk.MenuItem(label="BaseColor")
        color_item.connect("activate", self._on_open_color)
        menu.append(color_item)

        about_item = self._gtk.MenuItem(label="About")
        about_item.connect("activate", self._on_open_about)
        menu.append(about_item)

        quit_item = self._gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self._on_quit)
        menu.append(quit_item)

        return menu

    def _create_indicator(self) -> Any | None:
        indicator_class = getattr(self._indicator_module, "Indicator", None)
        category = getattr(getattr(self._indicator_module, "IndicatorCategory", object()), "APPLICATION_STATUS", None)
        if indicator_class is None or category is None:
            return None

        icon_name = self._current_icon_name(watch_running=False)
        indicator = indicator_class.new("harite-tasktray", icon_name, category)
        if hasattr(indicator, "set_title"):
            indicator.set_title(f"Harite ({self._binding_name})")
        return indicator

    def _poll_state(self) -> bool:
        self.refresh()
        return True

    def refresh(self) -> None:
        watch_running = self._watch_running()
        can_start_watch = self._can_start_watch()
        visible = self._window_visible()

        if self._visible_item is not None and hasattr(self._visible_item, "set_label"):
            self._visible_item.set_label("Invisible" if visible else "Visible")
        if self._watch_start_item is not None and hasattr(self._watch_start_item, "set_sensitive"):
            self._watch_start_item.set_sensitive(can_start_watch)
        if self._watch_stop_item is not None and hasattr(self._watch_stop_item, "set_sensitive"):
            self._watch_stop_item.set_sensitive(watch_running)

        indicator = self._indicator
        if indicator is not None:
            icon_name = self._current_icon_name(watch_running=watch_running)
            for method_name in ("set_icon_full", "set_icon"):
                method = getattr(indicator, method_name, None)
                if not callable(method):
                    continue
                try:
                    if method_name == "set_icon_full":
                        method(icon_name, "Harite")
                    else:
                        method(icon_name)
                    break
                except Exception:
                    continue

    def _window_visible(self) -> bool:
        if hasattr(self._window, "is_visible"):
            return bool(self._window.is_visible())
        if hasattr(self._window, "get_visible"):
            return bool(self._window.get_visible())
        return True

    def _connected_owner(self) -> Any | None:
        getter = getattr(self._signal_backend, "_get_connected_owner", None)
        if callable(getter):
            return getter()
        return None

    def _watch_running(self) -> bool:
        owner = self._connected_owner()
        if owner is not None:
            return bool(getattr(owner, "watch_running", False))
        return bool(getattr(self._signal_backend, "_watch_running", False))

    def _can_start_watch(self) -> bool:
        owner = self._connected_owner()
        if owner is not None:
            return bool(getattr(owner, "can_start_watch", False))
        return not self._watch_running()

    def _present_main_window(self) -> None:
        if hasattr(self._window, "show_all"):
            self._window.show_all()
        elif hasattr(self._window, "show"):
            self._window.show()
        if hasattr(self._window, "present"):
            self._window.present()

    def _current_icon_name(self, *, watch_running: bool) -> str:
        resource_name = "harite.svg" if watch_running else "harite_off.svg"
        try:
            resource_path = files("harite.gui").joinpath("resources", "icons", "product", resource_name)
            if resource_path.is_file():
                return str(resource_path)
        except Exception:
            pass
        return "applications-graphics" if watch_running else "media-playback-pause"

    def _invoke_backend(self, method_name: str, *, present_main_window: bool = False) -> None:
        callback = getattr(self._signal_backend, method_name, None)
        if not callable(callback):
            return
        if present_main_window:
            self._present_main_window()
        callback()
        self.refresh()

    def _on_toggle_visibility(self, *_args: Any) -> None:
        if self._window_visible():
            if hasattr(self._window, "hide"):
                self._window.hide()
        else:
            self._present_main_window()
        self.refresh()

    def _on_watch_start(self, *_args: Any) -> None:
        self._invoke_backend("_on_watch_start_clicked")

    def _on_watch_stop(self, *_args: Any) -> None:
        self._invoke_backend("_on_watch_stop_clicked")

    def _on_open_settings(self, *_args: Any) -> None:
        self._invoke_backend("_on_settings_clicked")

    def _on_open_color(self, *_args: Any) -> None:
        self._invoke_backend("_on_color_clicked")

    def _on_open_about(self, *_args: Any) -> None:
        self._invoke_backend("_on_about_clicked")

    def _on_quit(self, *_args: Any) -> None:
        try:
            if hasattr(self._window, "destroy"):
                self._window.destroy()
        finally:
            if hasattr(self._gtk, "main_quit"):
                self._gtk.main_quit()
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from harite.config import resolve_default_settings_path
from harite.core import DEFAULT_BACKGROUND_COLOR_HEX, is_background_color_literal, normalize_background_color


class SavePathDialogProxy:
    """Minimal file chooser-like object used by runtime fallback backend."""

    def __init__(
        self,
        gtk_module: Any | None = None,
        parent_window: Any | None = None,
        on_filename_change: Callable[[str], None] | None = None,
        on_confirm: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        self._gtk = gtk_module
        self._parent_window = parent_window
        self._filename = ""
        self._visible = False
        self._on_filename_change = on_filename_change
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

    def supports_native_dialog(self) -> bool:
        gtk = self._gtk
        return bool(
            gtk is not None
            and hasattr(gtk, "FileChooserDialog")
            and hasattr(gtk, "FileChooserAction")
            and hasattr(gtk, "ResponseType")
        )

    def _build_native_dialog(self) -> Any:
        gtk = self._gtk
        assert gtk is not None
        dialog = gtk.FileChooserDialog(
            title="Save wallpaper",
            parent=self._parent_window,
            action=gtk.FileChooserAction.SAVE,
        )
        if hasattr(dialog, "add_buttons"):
            dialog.add_buttons(
                getattr(gtk, "STOCK_CANCEL", "gtk-cancel"),
                gtk.ResponseType.CANCEL,
                getattr(gtk, "STOCK_SAVE", "gtk-save"),
                gtk.ResponseType.OK,
            )
        if hasattr(dialog, "set_modal"):
            dialog.set_modal(True)
        if hasattr(dialog, "set_transient_for") and self._parent_window is not None:
            dialog.set_transient_for(self._parent_window)
        if hasattr(dialog, "set_destroy_with_parent"):
            dialog.set_destroy_with_parent(True)
        if hasattr(dialog, "set_do_overwrite_confirmation"):
            dialog.set_do_overwrite_confirmation(True)
        return dialog

    def open_dialog(self) -> None:
        if self.supports_native_dialog():
            self._run_native_dialog()
            return
        self.show()

    def _run_native_dialog(self) -> None:
        gtk = self._gtk
        if gtk is None:
            self.show()
            return

        dialog = self._build_native_dialog()
        self._visible = True
        try:
            if self._filename:
                target = Path(self._filename).expanduser()
                if hasattr(dialog, "set_filename"):
                    dialog.set_filename(str(target.resolve()))
            else:
                home_dir = str(Path.home())
                if hasattr(dialog, "set_current_folder"):
                    dialog.set_current_folder(home_dir)
                if hasattr(dialog, "set_current_name"):
                    dialog.set_current_name("harite-output.jpg")

            if hasattr(dialog, "show_all"):
                dialog.show_all()
            response = dialog.run() if hasattr(dialog, "run") else None
            self._visible = False
            if response == gtk.ResponseType.OK:
                if hasattr(dialog, "get_filename"):
                    self.set_filename(str(dialog.get_filename() or ""))
                if self._on_confirm is not None:
                    self._on_confirm()
                return
            if self._on_cancel is not None:
                self._on_cancel()
        finally:
            if hasattr(dialog, "destroy"):
                dialog.destroy()

    def set_filename(self, filename: str) -> None:
        self._filename = str(filename or "")
        if self._on_filename_change is not None:
            self._on_filename_change(self._filename)

    def get_filename(self) -> str:
        return self._filename

    def show(self) -> None:
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def is_visible(self) -> bool:
        return self._visible


class OpenDialogProxy:
    """Minimal image chooser-like object used by runtime fallback backend."""

    def __init__(
        self,
        gtk_module: Any | None = None,
        parent_window: Any | None = None,
        on_confirm: Callable[[], None] | None = None,
        on_cancel: Callable[[bool], None] | None = None,
    ) -> None:
        self._gtk = gtk_module
        self._parent_window = parent_window
        self._filename = ""
        self._visible = False
        self._side = ""
        self._title = "Open image"
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

    def open_for_side(self, side: str, filename: str = "") -> None:
        self._side = str(side or "").upper()
        self._filename = str(filename or "")
        self._title = f"Open image ({self._side})"
        if self._supports_native_dialog():
            self._run_native_dialog()
            return
        self._visible = True

    def _supports_native_dialog(self) -> bool:
        gtk = self._gtk
        return bool(
            gtk is not None
            and hasattr(gtk, "FileChooserDialog")
            and hasattr(gtk, "FileChooserAction")
            and hasattr(gtk, "ResponseType")
            and hasattr(gtk, "FileFilter")
        )

    def _build_native_dialog(self) -> Any:
        gtk = self._gtk
        assert gtk is not None
        dialog = gtk.FileChooserDialog(
            title=self._title,
            parent=self._parent_window,
            action=gtk.FileChooserAction.OPEN,
        )
        if hasattr(dialog, "add_buttons"):
            dialog.add_buttons(
                getattr(gtk, "STOCK_CANCEL", "gtk-cancel"),
                gtk.ResponseType.CANCEL,
                getattr(gtk, "STOCK_OPEN", "gtk-open"),
                gtk.ResponseType.OK,
            )
        if hasattr(dialog, "set_modal"):
            dialog.set_modal(True)
        if hasattr(dialog, "set_transient_for") and self._parent_window is not None:
            dialog.set_transient_for(self._parent_window)
        if hasattr(dialog, "set_destroy_with_parent"):
            dialog.set_destroy_with_parent(True)
        if hasattr(dialog, "set_show_hidden"):
            dialog.set_show_hidden(True)

        image_filter = gtk.FileFilter()
        image_filter.set_name("画像")
        for mime_type in ("image/png", "image/jpeg", "image/bmp", "image/gif"):
            image_filter.add_mime_type(mime_type)
        for pattern in ("*.png", "*.jpeg", "*.jpg", "*.bmp", "*.gif"):
            image_filter.add_pattern(pattern)
        if hasattr(dialog, "add_filter"):
            dialog.add_filter(image_filter)

        all_files_filter = gtk.FileFilter()
        all_files_filter.set_name("全て")
        all_files_filter.add_pattern("*")
        if hasattr(dialog, "add_filter"):
            dialog.add_filter(all_files_filter)

        return dialog

    def _run_native_dialog(self) -> None:
        gtk = self._gtk
        if gtk is None:
            self._visible = True
            return

        dialog = self._build_native_dialog()
        self._visible = True
        try:
            if self._filename:
                if hasattr(dialog, "set_filename"):
                    dialog.set_filename(str(Path(self._filename).expanduser().resolve()))
            else:
                home_dir = str(Path.home())
                if hasattr(dialog, "set_current_folder"):
                    dialog.set_current_folder(home_dir)

            if hasattr(dialog, "show_all"):
                dialog.show_all()
            response = dialog.run() if hasattr(dialog, "run") else None
            if response == gtk.ResponseType.OK:
                if hasattr(dialog, "get_filename"):
                    self._filename = str(dialog.get_filename() or "")
                self._visible = False
                if self._on_confirm is not None:
                    self._on_confirm()
                return

            self._visible = False
            if self._on_cancel is not None:
                self._on_cancel(False)
        finally:
            if hasattr(dialog, "destroy"):
                dialog.destroy()

    def set_filename(self, filename: str) -> None:
        self._filename = str(filename or "")

    def get_filename(self) -> str:
        return self._filename

    def get_side(self) -> str:
        return self._side

    def set_title(self, title: str) -> None:
        self._title = str(title or "")

    def get_title(self) -> str:
        return self._title

    def show(self) -> None:
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def is_visible(self) -> bool:
        return self._visible

    def confirm(self) -> None:
        if self._on_confirm is not None:
            self._on_confirm()

    def cancel(self) -> None:
        if self._on_cancel is not None:
            self._on_cancel(False)

    def destroy(self) -> None:
        if self._on_cancel is not None:
            self._on_cancel(True)


class SrcdirDialogProxy:
    """Minimal folder chooser-like object used by runtime fallback backend."""

    def __init__(
        self,
        gtk_module: Any | None = None,
        parent_window: Any | None = None,
        on_confirm: Callable[[], None] | None = None,
        on_cancel: Callable[[bool], None] | None = None,
    ) -> None:
        self._gtk = gtk_module
        self._parent_window = parent_window
        self._current_folder = ""
        self._visible = False
        self._side = ""
        self._title = "Source directory"
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

    def open_for_side(self, side: str, current_folder: str = "") -> None:
        self._side = str(side or "").upper()
        self._current_folder = str(current_folder or "")
        self._title = f"Source directory ({self._side})"
        if self._supports_native_dialog():
            self._run_native_dialog()
            return
        self._visible = True

    def _supports_native_dialog(self) -> bool:
        gtk = self._gtk
        return bool(
            gtk is not None
            and hasattr(gtk, "FileChooserDialog")
            and hasattr(gtk, "FileChooserAction")
            and hasattr(gtk.FileChooserAction, "SELECT_FOLDER")
            and hasattr(gtk, "ResponseType")
        )

    def _build_native_dialog(self) -> Any:
        gtk = self._gtk
        assert gtk is not None
        dialog = gtk.FileChooserDialog(
            title=self._title,
            parent=self._parent_window,
            action=gtk.FileChooserAction.SELECT_FOLDER,
        )
        if hasattr(dialog, "add_buttons"):
            dialog.add_buttons(
                getattr(gtk, "STOCK_CANCEL", "gtk-cancel"),
                gtk.ResponseType.CANCEL,
                getattr(gtk, "STOCK_OPEN", "gtk-open"),
                gtk.ResponseType.OK,
            )
        if hasattr(dialog, "set_modal"):
            dialog.set_modal(True)
        if hasattr(dialog, "set_transient_for") and self._parent_window is not None:
            dialog.set_transient_for(self._parent_window)
        if hasattr(dialog, "set_destroy_with_parent"):
            dialog.set_destroy_with_parent(True)
        return dialog

    def _run_native_dialog(self) -> None:
        gtk = self._gtk
        if gtk is None:
            self._visible = True
            return

        dialog = self._build_native_dialog()
        self._visible = True
        try:
            target_folder = self._current_folder or str(Path.home())
            if hasattr(dialog, "set_current_folder"):
                dialog.set_current_folder(target_folder)

            if hasattr(dialog, "show_all"):
                dialog.show_all()
            response = dialog.run() if hasattr(dialog, "run") else None
            if response == gtk.ResponseType.OK:
                if hasattr(dialog, "get_filename"):
                    self._current_folder = str(dialog.get_filename() or "")
                elif hasattr(dialog, "get_current_folder"):
                    self._current_folder = str(dialog.get_current_folder() or "")
                self._visible = False
                if self._on_confirm is not None:
                    self._on_confirm()
                return

            self._visible = False
            if self._on_cancel is not None:
                self._on_cancel(False)
        finally:
            if hasattr(dialog, "destroy"):
                dialog.destroy()

    def set_current_folder(self, folder: str) -> None:
        self._current_folder = str(folder or "")

    def get_current_folder(self) -> str:
        return self._current_folder

    def get_side(self) -> str:
        return self._side

    def show(self) -> None:
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def is_visible(self) -> bool:
        return self._visible

    def confirm(self) -> None:
        if self._on_confirm is not None:
            self._on_confirm()

    def cancel(self) -> None:
        if self._on_cancel is not None:
            self._on_cancel(False)

    def destroy(self) -> None:
        if self._on_cancel is not None:
            self._on_cancel(True)


class SettingsDialogProxy:
    """Minimal settings dialog model used by runtime fallback backend."""

    def __init__(self, window: Any | None = None) -> None:
        self._visible = False
        self._window = window
        self._preferences_config: dict[str, object] = {}
        default_path = str(resolve_default_settings_path())
        self._import_path = default_path
        self._export_path = default_path

    def show(self) -> None:
        self._visible = True
        if self._window is not None:
            if hasattr(self._window, "show_all"):
                self._window.show_all()
            elif hasattr(self._window, "show"):
                self._window.show()
            if hasattr(self._window, "present"):
                self._window.present()

    def hide(self) -> None:
        self._visible = False
        if self._window is not None and hasattr(self._window, "hide"):
            self._window.hide()

    def is_visible(self) -> bool:
        return self._visible

    def set_preferences_config(self, config: dict[str, object]) -> None:
        self._preferences_config = dict(config)

    def get_preferences_config(self) -> dict[str, object]:
        return dict(self._preferences_config)

    def update_preference(self, key: str, value: object) -> None:
        self._preferences_config[str(key)] = value

    def set_import_path(self, path: str) -> None:
        self._import_path = str(path or "")

    def get_import_path(self) -> str:
        return self._import_path

    def set_export_path(self, path: str) -> None:
        self._export_path = str(path or "")

    def get_export_path(self) -> str:
        return self._export_path


class ColorDialogProxy:
    """Color dialog wrapper with native GTK chooser support and fallback UI."""

    def __init__(
        self,
        gtk_module: Any | None = None,
        parent_window: Any | None = None,
        window: Any | None = None,
        entry: Any | None = None,
        state_label: Any | None = None,
        notice_label: Any | None = None,
        picker_host: Any | None = None,
        pick_button: Any | None = None,
        on_confirm: Callable[[str], None] | None = None,
        on_cancel: Callable[[bool], None] | None = None,
    ) -> None:
        self._visible = False
        self._gtk = gtk_module
        self._parent_window = parent_window
        self._window = window
        self._entry = entry
        self._state_label = state_label
        self._notice_label = notice_label
        self._picker_host = picker_host
        self._pick_button = pick_button
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._color = DEFAULT_BACKGROUND_COLOR_HEX
        self._embedded_color_chooser = None
        self._syncing_embedded_color_chooser = False
        self._attach_embedded_color_chooser()
        if self._pick_button is not None and hasattr(self._pick_button, "connect"):
            self._pick_button.connect("clicked", lambda *_args: self.pick_color())
        self._configure_pick_button_role()
        self.set_color(self._color)

    def _configure_pick_button_role(self) -> None:
        if self._pick_button is None:
            return
        embedded_picker_active = self._embedded_color_chooser is not None
        if embedded_picker_active and hasattr(self._pick_button, "set_no_show_all"):
            self._pick_button.set_no_show_all(True)
        elif not embedded_picker_active and hasattr(self._pick_button, "set_no_show_all"):
            self._pick_button.set_no_show_all(False)
        if hasattr(self._pick_button, "set_sensitive"):
            self._pick_button.set_sensitive(not embedded_picker_active)
        if embedded_picker_active and hasattr(self._pick_button, "hide"):
            self._pick_button.hide()
        elif not embedded_picker_active and hasattr(self._pick_button, "show"):
            self._pick_button.show()

    def _attach_embedded_color_chooser(self) -> None:
        gtk = self._gtk
        if (
            gtk is None
            or self._picker_host is None
            or not hasattr(self._picker_host, "pack_start")
            or not hasattr(gtk, "ColorChooserWidget")
        ):
            return
        chooser = gtk.ColorChooserWidget()
        if hasattr(chooser, "set_use_alpha"):
            chooser.set_use_alpha(False)
        if hasattr(chooser, "connect"):
            chooser.connect("notify::rgba", lambda widget, *_args: self._on_embedded_color_chooser_changed(widget))
        self._picker_host.pack_start(chooser, True, True, 0)
        self._embedded_color_chooser = chooser
        if self._entry is not None and hasattr(self._entry, "connect"):
            self._entry.connect("changed", lambda entry, *_args: self._on_embedded_color_entry_changed(entry))

    def _on_embedded_color_chooser_changed(self, chooser: Any) -> None:
        if self._syncing_embedded_color_chooser or not hasattr(chooser, "get_rgba"):
            return
        try:
            color = self._color_from_rgba(chooser.get_rgba())
        except (TypeError, ValueError):
            return
        self._syncing_embedded_color_chooser = True
        try:
            if self._entry is not None and hasattr(self._entry, "set_text"):
                self._entry.set_text(color)
        finally:
            self._syncing_embedded_color_chooser = False
        self._set_current_color_label(color)

    def _on_embedded_color_entry_changed(self, entry: Any) -> None:
        if self._syncing_embedded_color_chooser or self._embedded_color_chooser is None:
            return
        if entry is None or not hasattr(entry, "get_text"):
            return
        value = str(entry.get_text() or "").strip()
        if not is_background_color_literal(value):
            return
        rgba = self._rgba_from_color(normalize_background_color(value))
        if rgba is None or not hasattr(self._embedded_color_chooser, "set_rgba"):
            return
        self._syncing_embedded_color_chooser = True
        try:
            self._embedded_color_chooser.set_rgba(rgba)
        finally:
            self._syncing_embedded_color_chooser = False

    def supports_native_dialog(self) -> bool:
        gtk = self._gtk
        if gtk is None:
            return False
        if not hasattr(gtk, "ColorChooserDialog") or not hasattr(gtk, "ResponseType"):
            return False
        return self._load_gdk_module() is not None

    def supports_native_picker(self) -> bool:
        gtk = self._gtk
        if gtk is None:
            return False
        if not hasattr(gtk, "ColorChooserDialog") or not hasattr(gtk, "ResponseType"):
            return False
        return self._load_gdk_module() is not None

    def _load_gdk_module(self) -> Any | None:
        try:
            import importlib

            gi = importlib.import_module("gi")
            gi.require_version("Gdk", "3.0")
            return importlib.import_module("gi.repository.Gdk")
        except (ImportError, ValueError):
            return None

    def _build_native_dialog(self) -> Any:
        gtk = self._gtk
        assert gtk is not None
        dialog = gtk.ColorChooserDialog(title="Background Color", parent=self._parent_window)
        if hasattr(dialog, "set_modal"):
            dialog.set_modal(True)
        if hasattr(dialog, "set_transient_for") and self._parent_window is not None:
            dialog.set_transient_for(self._parent_window)
        if hasattr(dialog, "set_destroy_with_parent"):
            dialog.set_destroy_with_parent(True)
        self._attach_native_hex_entry(dialog)
        return dialog

    def _attach_native_hex_entry(self, dialog: Any) -> None:
        gtk = self._gtk
        if gtk is None or not hasattr(dialog, "get_content_area"):
            return
        content_area = dialog.get_content_area()
        if content_area is None or not hasattr(gtk, "Box") or not hasattr(gtk, "Label") or not hasattr(gtk, "Entry"):
            return
        action_area = dialog.get_action_area() if hasattr(dialog, "get_action_area") else None

        native_hex_box = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=4)
        native_hex_label = gtk.Label(label="Hex (#RRGGBB)")
        if hasattr(native_hex_label, "set_xalign"):
            native_hex_label.set_xalign(0.0)
        native_hex_entry = gtk.Entry()
        native_notice_label = gtk.Label(label="")
        self._configure_native_notice_label(native_notice_label)
        if hasattr(native_hex_entry, "set_text"):
            native_hex_entry.set_text(self._color)
        native_hex_box.pack_start(native_hex_label, False, False, 0)
        native_hex_box.pack_start(native_hex_entry, False, False, 0)
        if hasattr(content_area, "pack_start"):
            content_area.pack_start(native_hex_box, False, False, 0)
        self._attach_native_notice_label(dialog, content_area, action_area, native_notice_label)
        if hasattr(native_hex_entry, "connect"):
            native_hex_entry.connect("changed", lambda entry, *_args: self._on_native_hex_entry_changed(dialog, entry))
        if hasattr(dialog, "connect"):
            dialog.connect("notify::rgba", lambda chooser, *_args: self._sync_native_hex_entry_from_dialog(chooser, native_hex_entry))
        setattr(dialog, "_harite_hex_entry", native_hex_entry)
        setattr(dialog, "_harite_notice_label", native_notice_label)

    def _configure_native_notice_label(self, notice_label: Any) -> None:
        gtk = self._gtk
        if hasattr(notice_label, "set_xalign"):
            notice_label.set_xalign(0.0)
        if gtk is not None and hasattr(gtk, "Align") and hasattr(notice_label, "set_halign"):
            notice_label.set_halign(gtk.Align.START)
        if hasattr(notice_label, "set_hexpand"):
            notice_label.set_hexpand(True)

    def _attach_native_notice_label(
        self,
        dialog: Any,
        content_area: Any,
        action_area: Any,
        notice_label: Any,
    ) -> None:
        gtk = self._gtk
        if gtk is not None:
            parent_box = self._prepare_native_notice_parent(gtk, dialog, content_area, action_area)
        else:
            parent_box = None
        if parent_box is None:
            parent_box = content_area
        if hasattr(parent_box, "pack_start"):
            parent_box.pack_start(notice_label, False, True, 0)

    def _prepare_native_notice_parent(self, gtk: Any, dialog: Any, content_area: Any, action_area: Any) -> Any | None:
        parent_box = self._resolve_native_notice_host(gtk, dialog, content_area, action_area)
        if parent_box is not None:
            return parent_box
        if action_area is None or not hasattr(action_area, "pack_start"):
            return None
        if not hasattr(gtk, "Box"):
            return action_area
        if not hasattr(action_area, "get_children") or not hasattr(action_area, "remove"):
            return action_area

        existing_children = list(action_area.get_children())
        if not existing_children:
            return action_area

        action_shell = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=4)
        action_row = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=6)
        if hasattr(action_shell, "set_hexpand"):
            action_shell.set_hexpand(True)
        if hasattr(action_row, "set_hexpand"):
            action_row.set_hexpand(True)
        if hasattr(gtk, "Align"):
            if hasattr(action_shell, "set_halign"):
                action_shell.set_halign(gtk.Align.FILL)
            if hasattr(action_row, "set_halign"):
                action_row.set_halign(gtk.Align.FILL)
        for child in existing_children:
            action_area.remove(child)
            action_row.pack_start(child, False, False, 0)
        action_shell.pack_start(action_row, False, False, 0)
        action_area.pack_start(action_shell, True, True, 0)
        return action_shell

    def _resolve_native_notice_host(self, gtk: Any, dialog: Any, content_area: Any, action_area: Any) -> Any | None:
        candidate = self._get_dialog_internal_vbox(gtk, dialog)
        if self._is_valid_native_notice_host(candidate, dialog, content_area, action_area):
            return candidate

        shared_ancestor = self._find_shared_native_notice_ancestor(content_area, action_area)
        if self._is_valid_native_notice_host(shared_ancestor, dialog, content_area, action_area):
            return shared_ancestor

        for widget in (action_area, content_area):
            candidate = self._get_parent_widget(widget)
            if self._is_valid_native_notice_host(candidate, dialog, content_area, action_area):
                return candidate
        return None

    def _get_dialog_internal_vbox(self, gtk: Any, dialog: Any) -> Any | None:
        buildable = getattr(gtk, "Buildable", None)
        if buildable is not None and hasattr(buildable, "get_internal_child"):
            for builder in (None, dialog):
                try:
                    candidate = buildable.get_internal_child(dialog, builder, "vbox")
                except TypeError:
                    continue
                if candidate is not None:
                    return candidate
        if hasattr(dialog, "get_internal_child"):
            for args in ((None, "vbox"), (dialog, "vbox"), ("vbox",)):
                try:
                    candidate = dialog.get_internal_child(*args)
                except TypeError:
                    continue
                if candidate is not None:
                    return candidate
        return None

    def _find_shared_native_notice_ancestor(self, content_area: Any, action_area: Any) -> Any | None:
        if content_area is None or action_area is None:
            return None
        action_ancestors = self._collect_parent_widgets(action_area)
        for candidate in self._collect_parent_widgets(content_area):
            if candidate in action_ancestors:
                return candidate
        return None

    def _collect_parent_widgets(self, widget: Any) -> list[Any]:
        ancestors: list[Any] = []
        current = self._get_parent_widget(widget)
        while current is not None and current not in ancestors:
            ancestors.append(current)
            current = self._get_parent_widget(current)
        return ancestors

    def _get_parent_widget(self, widget: Any) -> Any | None:
        if widget is None or not hasattr(widget, "get_parent"):
            return None
        try:
            return widget.get_parent()
        except TypeError:
            return None

    def _is_valid_native_notice_host(self, candidate: Any, dialog: Any, content_area: Any, action_area: Any) -> bool:
        if candidate is None or candidate in {dialog, action_area, content_area}:
            return False
        return hasattr(candidate, "pack_start")

    def _set_native_notice(self, dialog: Any, message: str) -> None:
        notice_label = getattr(dialog, "_harite_notice_label", None)
        if notice_label is not None and hasattr(notice_label, "set_text"):
            notice_label.set_text(message)

    def _sync_native_hex_entry_from_dialog(self, dialog: Any, entry: Any) -> None:
        if entry is None or not hasattr(entry, "set_text") or not hasattr(dialog, "get_rgba"):
            return
        try:
            color = self._color_from_rgba(dialog.get_rgba())
        except (TypeError, ValueError):
            return
        current = str(entry.get_text() or "") if hasattr(entry, "get_text") else ""
        if current != color:
            entry.set_text(color)

    def _on_native_hex_entry_changed(self, dialog: Any, entry: Any) -> None:
        if entry is None or not hasattr(entry, "get_text") or not hasattr(dialog, "set_rgba"):
            return
        value = str(entry.get_text() or "").strip()
        self._set_native_notice(dialog, "")
        if not is_background_color_literal(value):
            return
        rgba = self._rgba_from_color(normalize_background_color(value))
        if rgba is None:
            return
        try:
            dialog.set_rgba(rgba)
        except (TypeError, ValueError):
            return

    def _rgba_from_color(self, color: str) -> Any | None:
        gdk = self._load_gdk_module()
        if gdk is None or not hasattr(gdk, "RGBA"):
            return None
        rgba = gdk.RGBA()
        rgba.red = int(color[1:3], 16) / 255.0
        rgba.green = int(color[3:5], 16) / 255.0
        rgba.blue = int(color[5:7], 16) / 255.0
        rgba.alpha = 1.0
        return rgba

    def _color_from_rgba(self, rgba: Any) -> str:
        red = round(float(getattr(rgba, "red", 0.0)) * 255)
        green = round(float(getattr(rgba, "green", 0.0)) * 255)
        blue = round(float(getattr(rgba, "blue", 0.0)) * 255)
        return normalize_background_color((red, green, blue))

    def open_dialog(self) -> None:
        self._set_notice("")
        self.show()

    def pick_color(self) -> None:
        if not self.supports_native_picker():
            return
        self._run_native_picker_dialog()

    def _run_native_picker_dialog(self) -> None:
        gtk = self._gtk
        if gtk is None:
            return

        dialog = self._build_native_dialog()
        try:
            rgba = self._rgba_from_color(self.get_pending_color())
            if rgba is not None and hasattr(dialog, "set_rgba"):
                dialog.set_rgba(rgba)
            if hasattr(dialog, "show_all"):
                dialog.show_all()
            response = dialog.run() if hasattr(dialog, "run") else None
            if response != gtk.ResponseType.OK:
                return

            native_hex_entry = getattr(dialog, "_harite_hex_entry", None)
            if native_hex_entry is not None and hasattr(native_hex_entry, "get_text"):
                native_hex_value = str(native_hex_entry.get_text() or "").strip()
                if native_hex_value and is_background_color_literal(native_hex_value):
                    self.set_color(native_hex_value)
                    return
            if hasattr(dialog, "get_rgba"):
                self.set_color(self._color_from_rgba(dialog.get_rgba()))
        finally:
            if hasattr(dialog, "destroy"):
                dialog.destroy()

    def _run_native_dialog(self) -> None:
        gtk = self._gtk
        if gtk is None:
            self.show()
            return

        dialog = self._build_native_dialog()
        self._visible = True
        try:
            rgba = self._rgba_from_color(self._color)
            if rgba is not None and hasattr(dialog, "set_rgba"):
                dialog.set_rgba(rgba)
            if hasattr(dialog, "show_all"):
                dialog.show_all()
            while True:
                response = dialog.run() if hasattr(dialog, "run") else None
                if response != gtk.ResponseType.OK:
                    self._visible = False
                    if self._on_cancel is not None:
                        self._on_cancel(False)
                    return

                native_hex_entry = getattr(dialog, "_harite_hex_entry", None)
                native_hex_value = None
                submitted_color = self._color
                if native_hex_entry is not None and hasattr(native_hex_entry, "get_text"):
                    native_hex_value = str(native_hex_entry.get_text() or "").strip()
                if native_hex_value:
                    if not is_background_color_literal(native_hex_value):
                        self._set_native_notice(dialog, "Color: invalid background color")
                        continue
                    self.set_color(native_hex_value)
                    submitted_color = self._color
                elif hasattr(dialog, "get_rgba"):
                    self.set_color(self._color_from_rgba(dialog.get_rgba()))
                    submitted_color = self._color
                self._set_native_notice(dialog, "")
                self._visible = False
                if self._on_confirm is not None:
                    self._on_confirm(submitted_color)
                return
        finally:
            if hasattr(dialog, "destroy"):
                dialog.destroy()

    def show(self) -> None:
        self._visible = True
        if self._window is not None:
            if hasattr(self._window, "show_all"):
                self._window.show_all()
                self._configure_pick_button_role()
            elif hasattr(self._window, "show"):
                self._window.show()
            if hasattr(self._window, "present"):
                self._window.present()

    def hide(self) -> None:
        self._visible = False
        if self._window is not None and hasattr(self._window, "hide"):
            self._window.hide()

    def is_visible(self) -> bool:
        return self._visible

    def set_color(self, color: str | None) -> None:
        self._color = normalize_background_color(color)
        if self._entry is not None and hasattr(self._entry, "set_text"):
            self._entry.set_text(self._color)
        if self._embedded_color_chooser is not None and hasattr(self._embedded_color_chooser, "set_rgba"):
            rgba = self._rgba_from_color(self._color)
            if rgba is not None:
                self._syncing_embedded_color_chooser = True
                try:
                    self._embedded_color_chooser.set_rgba(rgba)
                finally:
                    self._syncing_embedded_color_chooser = False
        self._set_current_color_label(self._color)

    def _set_current_color_label(self, color: str) -> None:
        if self._state_label is not None and hasattr(self._state_label, "set_text"):
            self._state_label.set_text(f"Color: {normalize_background_color(color)}")

    def set_notice(self, message: str) -> None:
        self._set_notice(message)

    def clear_notice(self) -> None:
        self._set_notice("")

    def _set_notice(self, message: str) -> None:
        if self._notice_label is not None and hasattr(self._notice_label, "set_text"):
            self._notice_label.set_text(str(message or ""))

    def get_color(self) -> str:
        if self._entry is not None and hasattr(self._entry, "get_text"):
            self._color = normalize_background_color(self._entry.get_text())
        return self._color

    def get_pending_color(self) -> str:
        if self._entry is not None and hasattr(self._entry, "get_text"):
            return str(self._entry.get_text() or "").strip()
        return self._color

    def confirm(self) -> None:
        color = self.get_pending_color()
        if self._on_confirm is not None:
            self._on_confirm(color)

    def cancel(self) -> None:
        if self._on_cancel is not None:
            self._on_cancel(False)

    def destroy(self) -> None:
        if self._on_cancel is not None:
            self._on_cancel(True)


class AboutDialogProxy:
    """Minimal about dialog model used by runtime fallback backend."""

    def __init__(
        self,
        window: Any | None = None,
        title_label: Any | None = None,
        version_label: Any | None = None,
        description_label: Any | None = None,
        credits_label: Any | None = None,
        license_label: Any | None = None,
    ) -> None:
        self._visible = False
        self._window = window
        self._title_label = title_label
        self._version_label = version_label
        self._description_label = description_label
        self._credits_label = credits_label
        self._license_label = license_label

    def show(self) -> None:
        self._visible = True
        if self._window is not None:
            if hasattr(self._window, "show_all"):
                self._window.show_all()
            elif hasattr(self._window, "show"):
                self._window.show()
            if hasattr(self._window, "present"):
                self._window.present()

    def hide(self) -> None:
        self._visible = False
        if self._window is not None and hasattr(self._window, "hide"):
            self._window.hide()

    def is_visible(self) -> bool:
        return self._visible

    def set_content(self, content: dict[str, object]) -> None:
        if self._title_label is not None and hasattr(self._title_label, "set_text"):
            self._title_label.set_text(str(content.get("app_name", "Harite")))
        if self._version_label is not None and hasattr(self._version_label, "set_text"):
            self._version_label.set_text(f"Version: {content.get('version', '-')}")
        if self._description_label is not None and hasattr(self._description_label, "set_text"):
            self._description_label.set_text(str(content.get("description", "")))
        if self._credits_label is not None and hasattr(self._credits_label, "set_text"):
            self._credits_label.set_text(f"Credits: {content.get('credits', '-')}")
        if self._license_label is not None and hasattr(self._license_label, "set_text"):
            license_name = str(content.get("license_name", "LICENSE"))
            self._license_label.set_text(f"License: {license_name}")
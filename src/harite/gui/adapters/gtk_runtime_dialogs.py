from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

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
        default_path = str(Path.home() / "harite-preferences.json")
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
        self._pick_button = pick_button
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._color = DEFAULT_BACKGROUND_COLOR_HEX
        if self._pick_button is not None and hasattr(self._pick_button, "connect"):
            self._pick_button.connect("clicked", lambda *_args: self.pick_color())
        self.set_color(self._color)

    def supports_native_dialog(self) -> bool:
        # Phase10 visual-aid requires the managed dialog so the bottom notice
        # row is consistently available for corrective errors.
        return False

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
        except Exception:
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

        native_hex_box = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=4)
        native_hex_label = gtk.Label(label="Hex (#RRGGBB)")
        if hasattr(native_hex_label, "set_xalign"):
            native_hex_label.set_xalign(0.0)
        native_hex_entry = gtk.Entry()
        if hasattr(native_hex_entry, "set_text"):
            native_hex_entry.set_text(self._color)
        native_hex_box.pack_start(native_hex_label, False, False, 0)
        native_hex_box.pack_start(native_hex_entry, False, False, 0)
        if hasattr(content_area, "pack_start"):
            content_area.pack_start(native_hex_box, False, False, 0)
        if hasattr(native_hex_entry, "connect"):
            native_hex_entry.connect("changed", lambda entry, *_args: self._on_native_hex_entry_changed(dialog, entry))
        if hasattr(dialog, "connect"):
            dialog.connect("notify::rgba", lambda chooser, *_args: self._sync_native_hex_entry_from_dialog(chooser, native_hex_entry))
        setattr(dialog, "_harite_hex_entry", native_hex_entry)

    def _sync_native_hex_entry_from_dialog(self, dialog: Any, entry: Any) -> None:
        if entry is None or not hasattr(entry, "set_text") or not hasattr(dialog, "get_rgba"):
            return
        try:
            color = self._color_from_rgba(dialog.get_rgba())
        except Exception:
            return
        current = str(entry.get_text() or "") if hasattr(entry, "get_text") else ""
        if current != color:
            entry.set_text(color)

    def _on_native_hex_entry_changed(self, dialog: Any, entry: Any) -> None:
        if entry is None or not hasattr(entry, "get_text") or not hasattr(dialog, "set_rgba"):
            return
        value = str(entry.get_text() or "").strip()
        if not is_background_color_literal(value):
            return
        rgba = self._rgba_from_color(normalize_background_color(value))
        if rgba is None:
            return
        try:
            dialog.set_rgba(rgba)
        except Exception:
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
        if self.supports_native_dialog():
            self._run_native_dialog()
            return
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
            response = dialog.run() if hasattr(dialog, "run") else None
            self._visible = False
            if response == gtk.ResponseType.OK:
                native_hex_entry = getattr(dialog, "_harite_hex_entry", None)
                native_hex_value = None
                submitted_color = self._color
                if native_hex_entry is not None and hasattr(native_hex_entry, "get_text"):
                    native_hex_value = str(native_hex_entry.get_text() or "").strip()
                if native_hex_value and is_background_color_literal(native_hex_value):
                    self.set_color(native_hex_value)
                    submitted_color = self._color
                elif hasattr(dialog, "get_rgba"):
                    self.set_color(self._color_from_rgba(dialog.get_rgba()))
                    submitted_color = self._color
                if self._on_confirm is not None:
                    self._on_confirm(submitted_color)
                return
            if self._on_cancel is not None:
                self._on_cancel(False)
        finally:
            if hasattr(dialog, "destroy"):
                dialog.destroy()

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

    def set_color(self, color: str | None) -> None:
        self._color = normalize_background_color(color)
        if self._entry is not None and hasattr(self._entry, "set_text"):
            self._entry.set_text(self._color)
        if self._state_label is not None and hasattr(self._state_label, "set_text"):
            self._state_label.set_text(f"Color: {self._color}")

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
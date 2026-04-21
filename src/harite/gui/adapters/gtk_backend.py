"""GTK backend loader for optional UI signal binding.

This adapter is intentionally optional. It should only be used in environments
where PyGObject/GTK is available.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from harite.positioning import format_position_pair, parse_position_pair
from harite.watch import WatchCycleState, collect_watch_input_images, run_watch_cycle


SAVE_PATH_DIALOG_OBJECT_ALIASES: tuple[str, ...] = (
    "SavePathDialog",
)

SAVE_PATH_STATE_LABEL_ALIASES: tuple[str, ...] = (
    "lblSavePathState",
)

SAVE_PATH_SELECTED_HANDLER_NAMES: tuple[str, ...] = (
    "on_save_path_selected",
)

SAVE_PATH_CANCELED_HANDLER_NAMES: tuple[str, ...] = (
    "on_save_path_selection_canceled",
)

SAVE_PATH_DESTROY_HANDLER_NAMES: tuple[str, ...] = (
    "on_SavePathDialog_destroy",
)

SETTINGS_DIALOG_OBJECT_ALIASES: tuple[str, ...] = (
    "SettingsDialog",
)


def _default_apply_mode() -> str:
    session_markers = (
        os.environ.get("XDG_CURRENT_DESKTOP", ""),
        os.environ.get("XDG_SESSION_DESKTOP", ""),
        os.environ.get("DESKTOP_SESSION", ""),
        os.environ.get("GDMSESSION", ""),
    )
    is_xfce_session = any("xfce" in marker.strip().lower() for marker in session_markers if marker)
    return "per-monitor-auto-split" if is_xfce_session else "single-file"


class _SavePathDialogProxy:
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


class _OpenDialogProxy:
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


class _SrcdirDialogProxy:
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


class _SettingsDialogProxy:
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


class GtkRuntimeSignalBackend:
    """Minimal GTK runtime backend that does not require Glade parsing.

    This fallback keeps present/bind flows usable even when a legacy Glade
    resource cannot be consumed by Gtk.Builder at runtime.
    """

    def __init__(self, gtk_module: Any) -> None:
        self._gtk = gtk_module
        self._signal_handlers: dict[str, Callable[..., Any]] = {}
        self._input_path_l = ""
        self._input_path_r = ""
        self._prefs_apply_mode_preserved: str | None = None
        self._prefs_apply_mode_syncing = False
        self._watch_srcdir_l = ""
        self._watch_srcdir_r = ""
        self._watch_running = False
        self._watch_state_l = WatchCycleState()
        self._watch_state_r = WatchCycleState()
        self._watch_previous_l: Path | None = None
        self._watch_previous_r: Path | None = None
        self._watch_timer_source_id: int | None = None

        window = gtk_module.Window(title="Harite")
        if hasattr(window, "set_resizable"):
            # P5-2 policy: modern desktop UX expects a resizable main window.
            window.set_resizable(True)
        if hasattr(window, "set_default_size"):
            window.set_default_size(1040, 720)

        if hasattr(gtk_module, "Box") and hasattr(gtk_module, "Label"):
            root = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=10)
            root.set_border_width(10)

            header_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            root.pack_start(header_col, False, False, 0)

            title_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            header_col.pack_start(title_row, False, False, 0)

            title = gtk_module.Label(label="")
            if hasattr(title, "set_xalign"):
                title.set_xalign(0.0)
            title_row.pack_start(title, False, False, 0)

            subtitle = gtk_module.Label(label="")
            if hasattr(subtitle, "set_xalign"):
                subtitle.set_xalign(0.0)

            command_bar = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            command_section_label = gtk_module.Label(label="")
            if hasattr(command_section_label, "set_xalign"):
                command_section_label.set_xalign(0.0)

            title_spacer = gtk_module.Label(label="")
            title_row.pack_start(title_spacer, True, True, 0)
            title_row.pack_start(command_bar, False, False, 0)

            btn_setting = gtk_module.Button(label="Prefs")
            btn_help = gtk_module.Button(label="Help")
            btn_about = gtk_module.Button(label="About")
            btn_set_color = gtk_module.Button(label="Color")
            command_bar.pack_start(btn_setting, False, False, 0)
            command_bar.pack_start(btn_help, False, False, 0)
            command_bar.pack_start(btn_about, False, False, 0)

            flow_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            header_col.pack_start(flow_row, False, False, 0)

            flow_legend_label = gtk_module.Label(label="Compose -> Optimize -> Apply")
            if hasattr(flow_legend_label, "set_xalign"):
                flow_legend_label.set_xalign(0.0)
            flow_row.pack_start(flow_legend_label, False, False, 0)

            flow_spacer = gtk_module.Label(label="")
            flow_row.pack_start(flow_spacer, True, True, 0)

            optimize_btn = gtk_module.Button(label="Save As")
            if hasattr(optimize_btn, "set_sensitive"):
                optimize_btn.set_sensitive(False)
            flow_row.pack_start(optimize_btn, False, False, 0)

            # Row 0: top margin row (Glade hbox11 equivalent)
            top_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            root.pack_start(top_row, False, False, 0)

            top_spacer_l = gtk_module.Label(label="")
            top_row.pack_start(top_spacer_l, True, True, 0)

            top_margin_label = gtk_module.Label(label="上マージン(px)")
            if hasattr(top_margin_label, "set_xalign"):
                top_margin_label.set_xalign(0.0)
            top_row.pack_start(top_margin_label, False, False, 0)

            top_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(top_margin_spin, minimum=0, maximum=250, step=1, page=10)
            top_row.pack_start(top_margin_spin, False, False, 0)

            top_spacer_r = gtk_module.Label(label="")
            top_row.pack_start(top_spacer_r, True, True, 0)

            # Row 1: center body (Glade hbox2 equivalent)
            center_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=10)
            root.pack_start(center_row, True, True, 0)

            left_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
            center_row.pack_start(left_margin_shell, False, False, 0)
            left_margin_top_spacer = gtk_module.Label(label="")
            left_margin_shell.pack_start(left_margin_top_spacer, True, True, 0)

            left_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            left_margin_shell.pack_start(left_margin_col, False, False, 0)

            left_margin_label = gtk_module.Label(label="左\nマージン(px)")
            if hasattr(left_margin_label, "set_xalign"):
                left_margin_label.set_xalign(0.5)
            left_margin_col.pack_start(left_margin_label, False, False, 0)

            left_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(left_margin_spin, minimum=0, maximum=500, step=1, page=10)
            left_margin_col.pack_start(left_margin_spin, False, False, 0)
            left_margin_bottom_spacer = gtk_module.Label(label="")
            left_margin_shell.pack_start(left_margin_bottom_spacer, True, True, 0)

            command_tabs = gtk_module.Notebook()
            center_row.pack_start(command_tabs, True, True, 0)

            def _build_centered_page(content: Any) -> Any:
                page_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
                top_spacer = gtk_module.Label(label="")
                page_shell.pack_start(top_spacer, True, True, 0)
                center_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
                page_shell.pack_start(center_shell, False, False, 0)
                left_spacer = gtk_module.Label(label="")
                right_spacer = gtk_module.Label(label="")
                center_shell.pack_start(left_spacer, True, True, 0)
                center_shell.pack_start(content, False, False, 0)
                center_shell.pack_start(right_spacer, True, True, 0)
                bottom_spacer = gtk_module.Label(label="")
                page_shell.pack_start(bottom_spacer, True, True, 0)
                return page_shell

            main_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=12)
            main_section_label = gtk_module.Label(label="Main")
            main_page_shell = _build_centered_page(main_col)

            compose_grid = gtk_module.Grid()
            if hasattr(compose_grid, "set_column_spacing"):
                compose_grid.set_column_spacing(32)
            if hasattr(compose_grid, "set_row_spacing"):
                compose_grid.set_row_spacing(12)
            main_col.pack_start(compose_grid, True, True, 0)

            left_display_grid = gtk_module.Grid()
            right_display_grid = gtk_module.Grid()
            if hasattr(left_display_grid, "set_column_spacing"):
                left_display_grid.set_column_spacing(6)
            if hasattr(left_display_grid, "set_row_spacing"):
                left_display_grid.set_row_spacing(8)
            if hasattr(right_display_grid, "set_column_spacing"):
                right_display_grid.set_column_spacing(6)
            if hasattr(right_display_grid, "set_row_spacing"):
                right_display_grid.set_row_spacing(8)
            tgl_upper_l = gtk_module.ToggleButton(label="Top-L")
            tgl_upper_r = gtk_module.ToggleButton(label="Top-R")
            tgl_lower_l = gtk_module.ToggleButton(label="Bottom-L")
            tgl_lower_r = gtk_module.ToggleButton(label="Bottom-R")
            tgl_push_left_l = gtk_module.ToggleButton(label="Left-L")
            tgl_push_right_l = gtk_module.ToggleButton(label="Right-L")
            btn_get_img_l = gtk_module.Button(label="Open-L")
            tgl_push_left_r = gtk_module.ToggleButton(label="Left-R")
            tgl_push_right_r = gtk_module.ToggleButton(label="Right-R")
            btn_get_img_r = gtk_module.Button(label="Open-R")

            if hasattr(left_display_grid, "attach"):
                left_display_grid.attach(tgl_upper_l, 1, 0, 1, 1)
                left_display_grid.attach(tgl_push_left_l, 0, 1, 1, 1)
                left_display_grid.attach(btn_get_img_l, 1, 1, 1, 1)
                left_display_grid.attach(tgl_push_right_l, 2, 1, 1, 1)
                left_display_grid.attach(tgl_lower_l, 1, 2, 1, 1)

            if hasattr(compose_grid, "attach"):
                compose_grid.attach(left_display_grid, 0, 0, 1, 1)

            input_row_l = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            input_entry_l = gtk_module.Label(label="")
            if hasattr(input_entry_l, "set_xalign"):
                input_entry_l.set_xalign(0.0)
            btn_clr_path_l = gtk_module.Button(label="Clear-L")
            input_row_l.pack_start(input_entry_l, True, True, 0)
            input_row_l.pack_start(btn_clr_path_l, False, False, 0)
            if hasattr(compose_grid, "attach"):
                compose_grid.attach(input_row_l, 0, 1, 1, 1)

            if hasattr(right_display_grid, "attach"):
                right_display_grid.attach(tgl_upper_r, 1, 0, 1, 1)
                right_display_grid.attach(tgl_push_left_r, 0, 1, 1, 1)
                right_display_grid.attach(btn_get_img_r, 1, 1, 1, 1)
                right_display_grid.attach(tgl_push_right_r, 2, 1, 1, 1)
                right_display_grid.attach(tgl_lower_r, 1, 2, 1, 1)

            if hasattr(compose_grid, "attach"):
                compose_grid.attach(right_display_grid, 1, 0, 1, 1)

            input_row_r = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            input_entry_r = gtk_module.Label(label="")
            if hasattr(input_entry_r, "set_xalign"):
                input_entry_r.set_xalign(0.0)
            btn_clr_path_r = gtk_module.Button(label="Clear-R")
            input_row_r.pack_start(input_entry_r, True, True, 0)
            input_row_r.pack_start(btn_clr_path_r, False, False, 0)
            if hasattr(compose_grid, "attach"):
                compose_grid.attach(input_row_r, 1, 1, 1, 1)

            fixed_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            fixed_left_spacer = gtk_module.Label(label="")
            fixed_shell.pack_start(fixed_left_spacer, True, True, 0)
            fixed_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            fixed_shell.pack_start(fixed_row, False, False, 0)
            fixed_right_spacer = gtk_module.Label(label="")
            fixed_shell.pack_start(fixed_right_spacer, True, True, 0)
            rad_fixed = gtk_module.RadioButton.new_with_label(None, "入替不可")
            rad_no_fixed = gtk_module.RadioButton.new_with_label_from_widget(rad_fixed, "入替可")
            if hasattr(rad_no_fixed, "set_active"):
                rad_no_fixed.set_active(True)
            fixed_row.pack_start(rad_fixed, False, False, 0)
            fixed_row.pack_start(rad_no_fixed, False, False, 0)

            pick_state_label = gtk_module.Label(label="")
            if hasattr(pick_state_label, "set_xalign"):
                pick_state_label.set_xalign(0.0)

            action_cluster_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=18)
            action_cluster_spacer = gtk_module.Label(label="")
            action_cluster_row.pack_start(action_cluster_spacer, True, True, 0)
            optimize_group = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            apply_group = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            action_cluster_row.pack_start(optimize_group, False, False, 0)
            action_cluster_row.pack_start(apply_group, False, False, 0)
            if hasattr(compose_grid, "attach"):
                compose_grid.attach(action_cluster_row, 0, 2, 2, 1)

            optimize_section_label = gtk_module.Label(label="Optimize")
            if hasattr(optimize_section_label, "set_xalign"):
                optimize_section_label.set_xalign(0.0)
            optimize_group.pack_start(optimize_section_label, False, False, 0)

            optimize_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            optimize_group.pack_start(optimize_row, False, False, 0)
            optimize_modern_btn = gtk_module.Button(label="Optimize")
            if hasattr(optimize_modern_btn, "set_sensitive"):
                optimize_modern_btn.set_sensitive(False)
            optimize_row.pack_start(optimize_modern_btn, False, False, 0)
            optimize_result = gtk_module.Label(label="Optimize result: not-run")
            if hasattr(optimize_result, "set_xalign"):
                optimize_result.set_xalign(0.0)
            optimize_row.pack_start(optimize_result, True, True, 0)

            apply_section_label = gtk_module.Label(label="Apply")
            if hasattr(apply_section_label, "set_xalign"):
                apply_section_label.set_xalign(0.0)
            apply_group.pack_start(apply_section_label, False, False, 0)

            apply_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            apply_group.pack_start(apply_row, False, False, 0)
            apply_btn = gtk_module.Button(label="Apply")
            if hasattr(apply_btn, "set_sensitive"):
                apply_btn.set_sensitive(False)
            apply_row.pack_start(apply_btn, False, False, 0)
            apply_target = gtk_module.Label(label="Apply target: not-ready")
            if hasattr(apply_target, "set_xalign"):
                apply_target.set_xalign(0.0)
            apply_row.pack_start(apply_target, True, True, 0)

            apply_mode_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            apply_group.pack_start(apply_mode_row, False, False, 0)
            apply_mode_help_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            apply_group.pack_start(apply_mode_help_row, False, False, 0)
            rad_apply_single = gtk_module.RadioButton.new_with_label(None, "No Split")
            rad_apply_per_monitor = gtk_module.RadioButton.new_with_label_from_widget(
                rad_apply_single,
                "Auto-Split",
            )
            default_apply_mode = _default_apply_mode()
            if default_apply_mode == "per-monitor-auto-split":
                if hasattr(rad_apply_per_monitor, "set_active"):
                    rad_apply_per_monitor.set_active(True)
                apply_mode_help_text = "Split the optimized image and apply per display."
            else:
                if hasattr(rad_apply_single, "set_active"):
                    rad_apply_single.set_active(True)
                apply_mode_help_text = "Apply the optimized image as a single file."
            apply_mode_label = gtk_module.Label(label=apply_mode_help_text)
            if hasattr(apply_mode_label, "set_xalign"):
                apply_mode_label.set_xalign(0.0)
            apply_mode_row.pack_start(rad_apply_per_monitor, False, False, 0)
            apply_mode_row.pack_start(rad_apply_single, False, False, 0)
            apply_mode_help_row.pack_start(apply_mode_label, True, True, 0)

            do_it_plan_label = gtk_module.Label(label="Debug: apply is immediate")
            if hasattr(do_it_plan_label, "set_xalign"):
                do_it_plan_label.set_xalign(0.0)

            save_path_state_label = gtk_module.Label(label="Save path: idle")
            if hasattr(save_path_state_label, "set_xalign"):
                save_path_state_label.set_xalign(0.0)

            save_target_label = gtk_module.Label(label="Save target: not-selected")
            if hasattr(save_target_label, "set_xalign"):
                save_target_label.set_xalign(0.0)

            priority_note_label = gtk_module.Label(
                label="Rule: margins define area; align/valign act inside it; fixed binds L/R"
            )
            if hasattr(priority_note_label, "set_xalign"):
                priority_note_label.set_xalign(0.0)

            style_legend_label = gtk_module.Label(label="Reserved slot for future placement")
            if hasattr(style_legend_label, "set_xalign"):
                style_legend_label.set_xalign(0.0)

            current_state_section_label = gtk_module.Label(label="Current state")
            if hasattr(current_state_section_label, "set_xalign"):
                current_state_section_label.set_xalign(0.0)

            current_fixed_label = gtk_module.Label(label="Current fixed: off")
            if hasattr(current_fixed_label, "set_xalign"):
                current_fixed_label.set_xalign(0.0)

            current_margins_label = gtk_module.Label(label="Current margins: 0,0,0,0")
            if hasattr(current_margins_label, "set_xalign"):
                current_margins_label.set_xalign(0.0)

            current_left_label = gtk_module.Label(label="Current L: align=center valign=center")
            if hasattr(current_left_label, "set_xalign"):
                current_left_label.set_xalign(0.0)

            current_right_label = gtk_module.Label(label="Current R: align=center valign=center")
            if hasattr(current_right_label, "set_xalign"):
                current_right_label.set_xalign(0.0)

            command_tabs.append_page(main_page_shell, main_section_label)

            right_margin_shell = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=0)
            center_row.pack_start(right_margin_shell, False, False, 0)
            right_margin_top_spacer = gtk_module.Label(label="")
            right_margin_shell.pack_start(right_margin_top_spacer, True, True, 0)

            right_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            right_margin_shell.pack_start(right_margin_col, False, False, 0)

            right_margin_label = gtk_module.Label(label="右\nマージン(px)")
            if hasattr(right_margin_label, "set_xalign"):
                right_margin_label.set_xalign(0.5)
            right_margin_col.pack_start(right_margin_label, False, False, 0)

            right_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(right_margin_spin, minimum=0, maximum=500, step=1, page=10)
            right_margin_col.pack_start(right_margin_spin, False, False, 0)
            right_margin_bottom_spacer = gtk_module.Label(label="")
            right_margin_shell.pack_start(right_margin_bottom_spacer, True, True, 0)

            # Row 2: bottom margin row (Glade hbox12 equivalent)
            bottom_margin_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            root.pack_start(bottom_margin_row, False, False, 0)
            btm_spacer_l = gtk_module.Label(label="")
            bottom_margin_row.pack_start(btm_spacer_l, True, True, 0)
            bottom_margin_label = gtk_module.Label(label="下マージン(px)")
            if hasattr(bottom_margin_label, "set_xalign"):
                bottom_margin_label.set_xalign(0.0)
            bottom_margin_row.pack_start(bottom_margin_label, False, False, 0)
            bottom_margin_spin = gtk_module.SpinButton()
            self._configure_spin_button(bottom_margin_spin, minimum=0, maximum=250, step=1, page=10)
            bottom_margin_row.pack_start(bottom_margin_spin, False, False, 0)
            btm_spacer_r = gtk_module.Label(label="")
            bottom_margin_row.pack_start(btm_spacer_r, True, True, 0)

            open_dialog_proxy = _OpenDialogProxy(
                gtk_module,
                window,
                self._on_open_dialog_confirmed,
                self._on_open_dialog_canceled,
            )
            save_path_dialog_proxy = _SavePathDialogProxy(
                gtk_module,
                window,
                self._on_save_path_filename_changed,
                self._on_native_save_path_confirmed,
                self._on_native_save_path_canceled,
            )
            prefs_window = gtk_module.Window(title="Preferences")
            if hasattr(prefs_window, "set_default_size"):
                prefs_window.set_default_size(520, 420)
            if hasattr(prefs_window, "set_resizable"):
                prefs_window.set_resizable(True)
            settings_dialog_proxy = _SettingsDialogProxy(prefs_window)
            if hasattr(prefs_window, "connect"):
                prefs_window.connect(
                    "delete-event",
                    lambda *_args: self._on_preferences_window_delete_event(),
                )
            srcdir_dialog_proxy = _SrcdirDialogProxy(
                gtk_module,
                window,
                self._on_srcdir_dialog_confirmed,
                self._on_srcdir_dialog_canceled,
            )

            prefs_apply_btn = gtk_module.Button(label="Prefs Apply")
            prefs_load_btn = gtk_module.Button(label="Prefs Load")
            prefs_save_btn = gtk_module.Button(label="Prefs Save")
            prefs_close_btn = gtk_module.Button(label="Prefs Close")
            prefs_state_label = gtk_module.Label(label="Prefs: idle")
            if hasattr(prefs_state_label, "set_xalign"):
                prefs_state_label.set_xalign(0.0)
            prefs_editor_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            prefs_editor_title = gtk_module.Label(label="Preferences")
            if hasattr(prefs_editor_title, "set_xalign"):
                prefs_editor_title.set_xalign(0.0)
            prefs_editor_box.pack_start(prefs_editor_title, False, False, 0)

            def _prefs_row(label_text: str, *widgets: Any) -> Any:
                row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
                row_label = gtk_module.Label(label=label_text)
                if hasattr(row_label, "set_xalign"):
                    row_label.set_xalign(0.0)
                row.pack_start(row_label, False, False, 0)
                for widget in widgets:
                    row.pack_start(widget, True, True, 0)
                prefs_editor_box.pack_start(row, False, False, 0)
                return row

            prefs_resolution_entry = gtk_module.Entry()
            prefs_layout_entry = gtk_module.Entry()
            prefs_scaling_entry = gtk_module.Entry()
            prefs_two_screen_auto = gtk_module.RadioButton.new_with_label(None, "TwoScreen Auto")
            prefs_two_screen_on = gtk_module.RadioButton.new_with_label_from_widget(prefs_two_screen_auto, "TwoScreen On")
            prefs_two_screen_off = gtk_module.RadioButton.new_with_label_from_widget(prefs_two_screen_auto, "TwoScreen Off")
            if hasattr(prefs_two_screen_off, "set_active"):
                prefs_two_screen_off.set_active(True)
            prefs_l_display_entry = gtk_module.Entry()
            prefs_r_display_entry = gtk_module.Entry()
            prefs_margins_entry = gtk_module.Entry()
            prefs_fixed_toggle = gtk_module.ToggleButton(label="Fixed")
            prefs_align_entry = gtk_module.Entry()
            prefs_valign_entry = gtk_module.Entry()
            prefs_padding_spin = gtk_module.SpinButton()
            self._configure_spin_button(prefs_padding_spin, minimum=0, maximum=10000, step=1, page=10, initial=0)
            prefs_quality_spin = gtk_module.SpinButton()
            self._configure_spin_button(prefs_quality_spin, minimum=1, maximum=100, step=1, page=10, initial=90)
            prefs_embed_info_entry = gtk_module.Entry()
            prefs_embed_text_entry = gtk_module.Entry()
            prefs_embed_position_entry = gtk_module.Entry()
            prefs_embed_max_lines_spin = gtk_module.SpinButton()
            self._configure_spin_button(prefs_embed_max_lines_spin, minimum=1, maximum=20, step=1, page=5, initial=3)
            prefs_plugin_entry = gtk_module.Entry()
            prefs_apply_single = gtk_module.RadioButton.new_with_label(None, "Apply Default")
            prefs_apply_per_monitor = gtk_module.RadioButton.new_with_label_from_widget(prefs_apply_single, "Apply Auto-split")
            if hasattr(prefs_apply_single, "set_active"):
                prefs_apply_single.set_active(True)
            prefs_apply_single.connect(
                "toggled",
                lambda widget, *_args: self._on_preferences_apply_mode_toggled(widget, "single-file"),
            )
            prefs_apply_per_monitor.connect(
                "toggled",
                lambda widget, *_args: self._on_preferences_apply_mode_toggled(widget, "per-monitor-auto-split"),
            )
            prefs_import_path_entry = gtk_module.Entry()
            prefs_export_path_entry = gtk_module.Entry()

            prefs_apply_mode_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            prefs_apply_mode_shell.pack_start(prefs_apply_single, False, False, 0)
            prefs_apply_mode_shell.pack_start(prefs_apply_per_monitor, False, False, 0)

            _prefs_row("Resolution", prefs_resolution_entry)
            _prefs_row("Layout", prefs_layout_entry)
            _prefs_row("Scaling", prefs_scaling_entry)
            _prefs_row("Plugin", prefs_plugin_entry)
            _prefs_row("Apply", prefs_apply_mode_shell)
            _prefs_row("Import path", prefs_import_path_entry)
            _prefs_row("Export path", prefs_export_path_entry)

            prefs_actions = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            prefs_actions.pack_start(prefs_apply_btn, False, False, 0)
            prefs_actions.pack_start(prefs_load_btn, False, False, 0)
            prefs_actions.pack_start(prefs_save_btn, False, False, 0)
            prefs_actions.pack_start(prefs_close_btn, False, False, 0)
            prefs_editor_box.pack_start(prefs_actions, False, False, 0)
            prefs_editor_box.pack_start(prefs_state_label, False, False, 0)

            if hasattr(prefs_window, "add"):
                prefs_window.add(prefs_editor_box)

            watch_tab_box = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=16)
            watch_label = gtk_module.Label(label="Watch")
            if hasattr(watch_label, "set_xalign"):
                watch_label.set_xalign(0.0)
            watch_tab_title = gtk_module.Label(label="Watch (stopped)")
            if hasattr(watch_tab_title, "set_xalign"):
                watch_tab_title.set_xalign(0.0)
            watch_tab_box.pack_start(watch_label, False, False, 0)

            watch_srcdir_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=0)
            watch_tab_box.pack_start(watch_srcdir_shell, False, False, 0)
            watch_srcdir_left_spacer = gtk_module.Label(label="")
            watch_srcdir_shell.pack_start(watch_srcdir_left_spacer, True, True, 0)
            watch_srcdir_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=48)
            watch_srcdir_shell.pack_start(watch_srcdir_row, False, False, 0)
            watch_srcdir_right_spacer = gtk_module.Label(label="")
            watch_srcdir_shell.pack_start(watch_srcdir_right_spacer, True, True, 0)
            btn_open_srcdir_l = gtk_module.Button(label="Srcdir-L")
            btn_open_srcdir_r = gtk_module.Button(label="Srcdir-R")
            watch_srcdir_row.pack_start(btn_open_srcdir_l, False, False, 0)
            watch_srcdir_row.pack_start(btn_open_srcdir_r, False, False, 0)

            watch_controls_shell = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            watch_tab_box.pack_start(watch_controls_shell, False, False, 0)
            watch_controls_left_spacer = gtk_module.Label(label="")
            watch_controls_shell.pack_start(watch_controls_left_spacer, True, True, 0)
            watch_controls_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            watch_controls_shell.pack_start(watch_controls_row, False, False, 0)
            watch_controls_right_spacer = gtk_module.Label(label="")
            watch_controls_shell.pack_start(watch_controls_right_spacer, True, True, 0)

            interval_spin = gtk_module.SpinButton()
            self._configure_spin_button(interval_spin, minimum=1, maximum=86400, step=1, page=10, initial=60)
            interval_label = gtk_module.Label(label="Interval")
            btn_daemonize = gtk_module.Button(label="Watch Start")
            btn_cancel_daemonize = gtk_module.Button(label="Watch Stop")
            watch_controls_row.pack_start(interval_label, False, False, 0)
            watch_controls_row.pack_start(interval_spin, False, False, 0)
            watch_controls_row.pack_start(btn_daemonize, False, False, 0)
            watch_controls_row.pack_start(btn_cancel_daemonize, False, False, 0)

            watch_detail_row = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=2)
            watch_tab_box.pack_start(watch_detail_row, False, False, 0)
            watch_sources_label = gtk_module.Label(label="Watch srcdirs: L=- | R=-")
            if hasattr(watch_sources_label, "set_xalign"):
                watch_sources_label.set_xalign(0.0)
            watch_detail_row.pack_start(watch_sources_label, False, False, 0)
            watch_current_label = gtk_module.Label(label="Watch current: idle")
            if hasattr(watch_current_label, "set_xalign"):
                watch_current_label.set_xalign(0.0)
            watch_detail_row.pack_start(watch_current_label, False, False, 0)
            watch_output_label = gtk_module.Label(label="Watch output: .")
            if hasattr(watch_output_label, "set_xalign"):
                watch_output_label.set_xalign(0.0)
            watch_detail_row.pack_start(watch_output_label, False, False, 0)

            watch_page_shell = _build_centered_page(watch_tab_box)
            command_tabs.append_page(watch_page_shell, watch_tab_title)

            # Row 4: status row (Glade statusbar equivalent)
            footer_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=4)
            root.pack_start(footer_col, False, False, 0)

            status_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=8)
            footer_col.pack_start(status_row, False, False, 0)
            status_label = gtk_module.Label(label="Status: ready")
            if hasattr(status_label, "set_xalign"):
                status_label.set_xalign(0.0)
            status_row.pack_start(status_label, False, False, 0)
            status_spacer = gtk_module.Label(label="")
            status_row.pack_start(status_spacer, True, True, 0)
            watch_summary_label = gtk_module.Label(label="Watch: stopped")
            if hasattr(watch_summary_label, "set_xalign"):
                watch_summary_label.set_xalign(0.0)

            error_label = gtk_module.Label(label="Error: none")
            if hasattr(error_label, "set_xalign"):
                error_label.set_xalign(0.0)

            if hasattr(window, "add"):
                window.add(root)

            self._objects = {
                "WallPosit_MainWindow": window,
                "main_window": window,
                "window1": window,
                "boxRoot": root,
                "hbox11": top_row,
                "lblTopMergin": top_margin_label,
                "spnTopMergin": top_margin_spin,
                "hbox2": center_row,
                "vbox4": left_margin_col,
                "lblLMergin": left_margin_label,
                "spnLMergin": left_margin_spin,
                "lblTitle": title,
                "lblSubtitle": subtitle,
                "lblMainSection": main_section_label,
                "boxMainSection": main_col,
                "composeGrid": compose_grid,
                "leftDisplayCol": left_display_grid,
                "rightDisplayCol": right_display_grid,
                "inputRowL": input_row_l,
                "inputRowR": input_row_r,
                "actionClusterRow": action_cluster_row,
                "actionClusterCol": optimize_group,
                "tglUpperL": tgl_upper_l,
                "tglUpperR": tgl_upper_r,
                "tglPushLeftL": tgl_push_left_l,
                "tglPushRightL": tgl_push_right_l,
                "tglLowerL": tgl_lower_l,
                "tglPushLeftR": tgl_push_left_r,
                "tglPushRightR": tgl_push_right_r,
                "tglLowerR": tgl_lower_r,
                "btnGetImgL": btn_get_img_l,
                "btnGetImgR": btn_get_img_r,
                "lblPickState": pick_state_label,
                "entPathL": input_entry_l,
                "btnClrPathL": btn_clr_path_l,
                "entPathR": input_entry_r,
                "btnClrPathR": btn_clr_path_r,
                "radFixed": rad_fixed,
                "radNoFixed": rad_no_fixed,
                "vbox5": right_margin_col,
                "lblRMergin": right_margin_label,
                "spnRMergin": right_margin_spin,
                "hbox12": bottom_margin_row,
                "lblBtmMergin": bottom_margin_label,
                "spnBtmMergin": bottom_margin_spin,
                "lblOptimizeSection": optimize_section_label,
                "boxOptimizeSection": optimize_row,
                "btnSave": optimize_btn,
                "btnOptimize": optimize_modern_btn,
                "lblOptimizeResult": optimize_result,
                "lblApplySection": apply_section_label,
                "boxApplySection": apply_row,
                "btnSetWall": apply_btn,
                "lblApplyTarget": apply_target,
                "radApplySingle": rad_apply_single,
                "radApplyPerMonitor": rad_apply_per_monitor,
                "lblApplyMode": apply_mode_label,
                "lblDoItPlanned": do_it_plan_label,
                "lblSaveTarget": save_target_label,
                "lblPriorityRule": priority_note_label,
                "lblStyleLegend": style_legend_label,
                "lblCurrentStateSection": current_state_section_label,
                "lblCurrentFixed": current_fixed_label,
                "lblCurrentMargins": current_margins_label,
                "lblCurrentStateL": current_left_label,
                "lblCurrentStateR": current_right_label,
                "lblCommandSection": command_section_label,
                "commandTabs": command_tabs,
                "hbox14": command_bar,
                "btnSetting": btn_setting,
                "btnPrefsApply": prefs_apply_btn,
                "btnPrefsLoad": prefs_load_btn,
                "btnPrefsSave": prefs_save_btn,
                "btnPrefsClose": prefs_close_btn,
                "lblPrefsState": prefs_state_label,
                "boxPrefsEditor": prefs_editor_box,
                "prefsWindow": prefs_window,
                "lblPrefsEditorTitle": prefs_editor_title,
                "entPrefsResolution": prefs_resolution_entry,
                "entPrefsLayout": prefs_layout_entry,
                "entPrefsScaling": prefs_scaling_entry,
                "radPrefsTwoScreenAuto": prefs_two_screen_auto,
                "radPrefsTwoScreenOn": prefs_two_screen_on,
                "radPrefsTwoScreenOff": prefs_two_screen_off,
                "entPrefsLDisplay": prefs_l_display_entry,
                "entPrefsRDisplay": prefs_r_display_entry,
                "entPrefsMargins": prefs_margins_entry,
                "tglPrefsFixed": prefs_fixed_toggle,
                "entPrefsAlign": prefs_align_entry,
                "entPrefsValign": prefs_valign_entry,
                "spnPrefsPadding": prefs_padding_spin,
                "spnPrefsQuality": prefs_quality_spin,
                "entPrefsEmbedInfo": prefs_embed_info_entry,
                "entPrefsEmbedText": prefs_embed_text_entry,
                "entPrefsEmbedPosition": prefs_embed_position_entry,
                "spnPrefsEmbedMaxLines": prefs_embed_max_lines_spin,
                "entPrefsPlugin": prefs_plugin_entry,
                "radPrefsApplySingle": prefs_apply_single,
                "radPrefsApplyPerMonitor": prefs_apply_per_monitor,
                "entPrefsImportPath": prefs_import_path_entry,
                "entPrefsExportPath": prefs_export_path_entry,
                "btnSetColor": btn_set_color,
                "ImgOpenDialog": open_dialog_proxy,
                "SrcdirDialog": srcdir_dialog_proxy,
                **{object_name: settings_dialog_proxy for object_name in SETTINGS_DIALOG_OBJECT_ALIASES},
                "watchTab": watch_tab_box,
                "watchControlsRow": watch_controls_row,
                "watchDetailRow": watch_detail_row,
                "btnOpenSrcdirL": btn_open_srcdir_l,
                "btnOpenSrcdirR": btn_open_srcdir_r,
                "lblWatchSection": watch_label,
                "lblWatchTabTitle": watch_tab_title,
                "spnInterval": interval_spin,
                "lblInterval": interval_label,
                "btnDaemonize": btn_daemonize,
                "btnCancelDaemonize": btn_cancel_daemonize,
                "btnAbout": btn_about,
                "btnHelp": btn_help,
                "statusbar": footer_col,
                "flowRow": flow_row,
                "lblFlowLegend": flow_legend_label,
                "lblStatus": status_label,
                "lblError": error_label,
                "lblWatchSummary": watch_summary_label,
                "lblWatchSources": watch_sources_label,
                "lblWatchCurrent": watch_current_label,
                "lblWatchOutput": watch_output_label,
                **{object_name: save_path_state_label for object_name in SAVE_PATH_STATE_LABEL_ALIASES},
                **{object_name: save_path_dialog_proxy for object_name in SAVE_PATH_DIALOG_OBJECT_ALIASES},
            }

            for object_name, widget in self._objects.items():
                if hasattr(widget, "set_name"):
                    widget.set_name(object_name)
                elif not hasattr(widget, "get_name"):
                    setattr(widget, "name", object_name)

            # Why: fallback window must still exercise MainWindow handlers even when
            # legacy glade cannot be parsed at runtime.
            try:
                input_entry_l.connect("changed", self._on_input_changed)
            except Exception:
                pass
            try:
                input_entry_r.connect("changed", self._on_input_changed)
            except Exception:
                pass
            tgl_upper_l.connect("pressed", lambda *_args: self._on_direction_pressed("tglUpperL"))
            tgl_upper_l.connect("toggled", lambda *_args: self._on_direction_toggled("tglUpperL"))
            tgl_upper_l.connect("released", lambda *_args: self._on_direction_released("tglUpperL"))
            tgl_lower_l.connect("pressed", lambda *_args: self._on_direction_pressed("tglLowerL"))
            tgl_lower_l.connect("toggled", lambda *_args: self._on_direction_toggled("tglLowerL"))
            tgl_lower_l.connect("released", lambda *_args: self._on_direction_released("tglLowerL"))
            tgl_upper_r.connect("pressed", lambda *_args: self._on_direction_pressed("tglUpperR"))
            tgl_upper_r.connect("toggled", lambda *_args: self._on_direction_toggled("tglUpperR"))
            tgl_upper_r.connect("released", lambda *_args: self._on_direction_released("tglUpperR"))
            tgl_lower_r.connect("pressed", lambda *_args: self._on_direction_pressed("tglLowerR"))
            tgl_lower_r.connect("toggled", lambda *_args: self._on_direction_toggled("tglLowerR"))
            tgl_lower_r.connect("released", lambda *_args: self._on_direction_released("tglLowerR"))
            tgl_push_left_l.connect("pressed", lambda *_args: self._on_direction_pressed("tglPushLeftL"))
            tgl_push_left_l.connect("toggled", lambda *_args: self._on_direction_toggled("tglPushLeftL"))
            tgl_push_left_l.connect("released", lambda *_args: self._on_direction_released("tglPushLeftL"))
            tgl_push_right_l.connect("pressed", lambda *_args: self._on_direction_pressed("tglPushRightL"))
            tgl_push_right_l.connect("toggled", lambda *_args: self._on_direction_toggled("tglPushRightL"))
            tgl_push_right_l.connect("released", lambda *_args: self._on_direction_released("tglPushRightL"))
            tgl_push_left_r.connect("pressed", lambda *_args: self._on_direction_pressed("tglPushLeftR"))
            tgl_push_left_r.connect("toggled", lambda *_args: self._on_direction_toggled("tglPushLeftR"))
            tgl_push_left_r.connect("released", lambda *_args: self._on_direction_released("tglPushLeftR"))
            tgl_push_right_r.connect("pressed", lambda *_args: self._on_direction_pressed("tglPushRightR"))
            tgl_push_right_r.connect("toggled", lambda *_args: self._on_direction_toggled("tglPushRightR"))
            tgl_push_right_r.connect("released", lambda *_args: self._on_direction_released("tglPushRightR"))
            btn_get_img_l.connect("clicked", lambda *_args: self._on_pick_input_clicked("L"))
            btn_get_img_r.connect("clicked", lambda *_args: self._on_pick_input_clicked("R"))
            btn_clr_path_l.connect("clicked", lambda *_args: self._on_clear_input_clicked("L"))
            btn_clr_path_r.connect("clicked", lambda *_args: self._on_clear_input_clicked("R"))
            rad_fixed.connect(
                "toggled",
                lambda widget, *_args: self._on_fixed_toggled(widget, True),
            )
            rad_no_fixed.connect(
                "toggled",
                lambda widget, *_args: self._on_fixed_toggled(widget, False),
            )
            top_margin_spin.connect("value-changed", self._on_margin_changed)
            left_margin_spin.connect("value-changed", self._on_margin_changed)
            right_margin_spin.connect("value-changed", self._on_margin_changed)
            bottom_margin_spin.connect("value-changed", self._on_margin_changed)
            optimize_btn.connect("clicked", self._on_save_clicked)
            optimize_modern_btn.connect("clicked", self._on_optimize_clicked)
            apply_btn.connect("clicked", self._on_apply_clicked)
            btn_setting.connect("clicked", self._on_settings_clicked)
            prefs_apply_btn.connect("clicked", self._on_preferences_apply_clicked)
            prefs_load_btn.connect("clicked", self._on_preferences_load_clicked)
            prefs_save_btn.connect("clicked", self._on_preferences_save_clicked)
            prefs_close_btn.connect("clicked", self._on_preferences_close_clicked)
            rad_apply_single.connect(
                "toggled",
                lambda widget, *_args: self._on_apply_mode_toggled(widget, "single-file"),
            )
            rad_apply_per_monitor.connect(
                "toggled",
                lambda widget, *_args: self._on_apply_mode_toggled(widget, "per-monitor-auto-split"),
            )
            btn_set_color.connect("clicked", self._on_color_clicked)
            btn_open_srcdir_l.connect("clicked", lambda *_args: self._on_pick_srcdir_clicked("L"))
            btn_open_srcdir_r.connect("clicked", lambda *_args: self._on_pick_srcdir_clicked("R"))
            interval_spin.connect("value-changed", self._on_watch_interval_changed)
            btn_daemonize.connect("clicked", self._on_watch_start_clicked)
            btn_cancel_daemonize.connect("clicked", self._on_watch_stop_clicked)
            self._refresh_current_state_labels()
        else:
            self._objects = {
                "WallPosit_MainWindow": window,
                "main_window": window,
                "window1": window,
            }

    def connect_signals(self, mapping: dict[str, Callable[..., Any]]) -> None:
        self._signal_handlers.update(mapping)
        owner = self._get_connected_owner()
        if owner is not None:
            self._sync_watch_state_from_owner(owner)

    def connect(self, handler_name: str, callback: Callable[..., Any]) -> None:
        self._signal_handlers[handler_name] = callback
        owner = self._get_connected_owner()
        if owner is not None:
            self._sync_watch_state_from_owner(owner)

    def _configure_spin_button(
        self,
        spin: Any,
        *,
        minimum: int,
        maximum: int,
        step: int,
        page: int,
        initial: int | None = None,
    ) -> None:
        if hasattr(spin, "set_numeric"):
            spin.set_numeric(True)
        if hasattr(spin, "set_range"):
            spin.set_range(minimum, maximum)
        if hasattr(spin, "set_increments"):
            spin.set_increments(step, page)
        if hasattr(spin, "set_value"):
            spin.set_value(minimum if initial is None else initial)

    def get_object(self, name: str) -> Any:
        return self._objects.get(name)

    def get_objects(self) -> list[Any]:
        return list(self._objects.values())

    def _set_status(self, message: str) -> None:
        status = self._objects.get("lblStatus")
        if status is not None and hasattr(status, "set_text"):
            status.set_text(message)

    def _set_error(self, message: str | None) -> None:
        if not message:
            self._set_label_text("lblError", "Error: none")
            return
        self._set_label_text("lblError", f"Error: {message}")

    def _set_feedback(self, *, phase: str, state: str, error: str | None = None) -> None:
        self._set_status(f"{phase}: {state}")
        self._set_error(error)

    def _set_label_text(self, object_name: str, message: str) -> None:
        label = self._objects.get(object_name)
        if label is not None and hasattr(label, "set_text"):
            label.set_text(message)

    def _set_entry_text(self, object_name: str, value: object | None) -> None:
        entry = self._objects.get(object_name)
        if entry is not None and hasattr(entry, "set_text"):
            entry.set_text("" if value is None else str(value))

    def _read_entry_text(self, object_name: str) -> str:
        entry = self._objects.get(object_name)
        if entry is None:
            return ""
        if hasattr(entry, "get_text"):
            return str(entry.get_text() or "").strip()
        return str(getattr(entry, "text", "") or "").strip()

    def _set_spin_value(self, object_name: str, value: int) -> None:
        spin = self._objects.get(object_name)
        if spin is not None and hasattr(spin, "set_value"):
            spin.set_value(int(value))

    def _set_button_enabled(self, object_name: str, enabled: bool) -> None:
        button = self._objects.get(object_name)
        if button is not None and hasattr(button, "set_sensitive"):
            button.set_sensitive(bool(enabled))

    def _get_save_path_dialog(self) -> Any | None:
        for object_name in SAVE_PATH_DIALOG_OBJECT_ALIASES:
            dialog = self._objects.get(object_name)
            if dialog is not None:
                return dialog
        return None

    def _get_save_path_destroy_callback(self) -> Callable[..., Any] | None:
        for handler_name in SAVE_PATH_DESTROY_HANDLER_NAMES:
            callback = self._signal_handlers.get(handler_name)
            if callback is not None:
                return callback
        return None

    def _set_save_path_state_text(self, message: str) -> None:
        for object_name in SAVE_PATH_STATE_LABEL_ALIASES:
            if self._objects.get(object_name) is not None:
                self._set_label_text(object_name, message)
                return

    def _current_save_path_filename(self) -> str:
        dialog = self._get_save_path_dialog()
        if dialog is None or not hasattr(dialog, "get_filename"):
            return ""
        return str(dialog.get_filename() or "").strip()

    def _refresh_save_target_label(self, filename: str | None = None) -> None:
        value = str(filename or "").strip()
        if not value:
            value = self._current_save_path_filename()
        if value:
            self._set_label_text("lblSaveTarget", f"Save target: {value}")
            return
        self._set_label_text("lblSaveTarget", "Save target: not-selected")

    def _refresh_watch_source_labels(self) -> None:
        left = self._watch_srcdir_l or "-"
        right = self._watch_srcdir_r or "-"
        self._set_label_text("lblWatchSources", f"Watch srcdirs: L={left} | R={right}")

    def _refresh_watch_summary_label(self) -> None:
        state = "running" if self._watch_running else "stopped"
        self._set_label_text("lblWatchSummary", f"Watch: {state}")
        self._set_label_text("lblWatchTabTitle", f"Watch ({state})")

    def _refresh_watch_current_label(self, left: str | None = None, right: str | None = None) -> None:
        current_left = left if left is not None else (str(self._watch_previous_l) if self._watch_previous_l else "-")
        current_right = right if right is not None else (str(self._watch_previous_r) if self._watch_previous_r else "-")
        if not self._watch_running and current_left == "-" and current_right == "-":
            self._set_label_text("lblWatchCurrent", "Watch current: idle")
            return
        self._set_label_text("lblWatchCurrent", f"Watch current: L={current_left} | R={current_right}")

    def _refresh_watch_output_label(self, output_dir: str | None = None) -> None:
        value = str(output_dir or "").strip() or "."
        self._set_label_text("lblWatchOutput", f"Watch output: {value}")

    def _get_handler_owner(self, handler_name: str) -> Any | None:
        callback = self._signal_handlers.get(handler_name)
        if callback is None:
            return None
        return getattr(callback, "__self__", None)

    def _get_connected_owner(self) -> Any | None:
        for callback in self._signal_handlers.values():
            owner = getattr(callback, "__self__", None)
            if owner is not None:
                return owner
        return None

    def _sync_watch_state_from_owner(self, owner: Any) -> None:
        self._watch_srcdir_l = str(getattr(owner, "watch_srcdir_l", self._watch_srcdir_l) or "")
        self._watch_srcdir_r = str(getattr(owner, "watch_srcdir_r", self._watch_srcdir_r) or "")
        self._watch_running = bool(getattr(owner, "watch_running", self._watch_running))
        self._watch_state_l = getattr(owner, "_watch_state_l", self._watch_state_l)
        self._watch_state_r = getattr(owner, "_watch_state_r", self._watch_state_r)
        self._watch_previous_l = getattr(owner, "_watch_previous_l", self._watch_previous_l)
        self._watch_previous_r = getattr(owner, "_watch_previous_r", self._watch_previous_r)
        interval_seconds = int(getattr(owner, "watch_interval_seconds", 0) or 0)
        self._set_spin_value("spnInterval", interval_seconds if interval_seconds > 0 else 60)
        self._refresh_watch_source_labels()
        self._refresh_watch_summary_label()
        self._refresh_watch_current_label()
        form_state = getattr(owner, "form_state", None)
        self._refresh_watch_output_label(getattr(form_state, "output_dir", None) if form_state is not None else None)

    def _sync_feedback_from_owner(self, owner: Any) -> None:
        phase = str(getattr(owner, "status_phase", "") or "").strip() or "watch"
        message = str(getattr(owner, "status_message", "") or "").strip() or "state-updated"
        error = str(getattr(owner, "last_error", "") or "").strip() or None
        self._set_feedback(phase=phase.capitalize(), state=message, error=error)

    def _get_glib_module(self) -> Any | None:
        glib = getattr(self._gtk, "GLib", None)
        if glib is not None:
            return glib
        try:
            import gi

            gi.require_version("Gtk", "3.0")
            from gi.repository import GLib

            return GLib
        except Exception:
            return None

    def _stop_watch_timer(self) -> None:
        if self._watch_timer_source_id is None:
            return

        glib = self._get_glib_module()
        if glib is not None and hasattr(glib, "source_remove"):
            glib.source_remove(self._watch_timer_source_id)
        self._watch_timer_source_id = None

    def _on_watch_timer_event(self) -> bool:
        if not self._watch_running:
            self._watch_timer_source_id = None
            return False

        ok = self.run_watch_cycle_once()
        if not ok or not self._watch_running:
            self._watch_timer_source_id = None
            return False
        return True

    def _start_watch_timer(self, interval_seconds: int) -> bool:
        self._stop_watch_timer()

        glib = self._get_glib_module()
        if glib is None or not hasattr(glib, "timeout_add"):
            return False

        interval_ms = max(1, int(interval_seconds)) * 1000
        self._watch_timer_source_id = int(glib.timeout_add(interval_ms, self._on_watch_timer_event))
        return True

    def _run_watch_cycle_for_side(self, side: str, source_dir: Path) -> str:
        images = collect_watch_input_images(source_dir)
        if side == "L":
            selected, state = run_watch_cycle(images, "sequential", self._watch_state_l)
            self._watch_state_l = state
            self._watch_previous_l = selected
            return str(selected)

        selected, state = run_watch_cycle(images, "sequential", self._watch_state_r)
        self._watch_state_r = state
        self._watch_previous_r = selected
        return str(selected)

    def _notify_srcdir_dialog_destroy(self) -> None:
        callback = self._signal_handlers.get("on_close_srcdir_dialog")
        if callback is None:
            return
        try:
            callback()
        except Exception:
            pass

    def _notify_save_path_dialog_destroy(self) -> None:
        callback = self._get_save_path_destroy_callback()
        if callback is None:
            return
        try:
            callback()
        except Exception:
            pass

    def _set_save_path_dialog_open_state(self, opened: bool, *, state_text: str | None = None) -> None:
        dialog = self._get_save_path_dialog()
        if dialog is not None:
            if opened and hasattr(dialog, "show"):
                dialog.show()
            if not opened and hasattr(dialog, "hide"):
                dialog.hide()

        if state_text is not None:
            self._set_save_path_state_text(state_text)

    def _on_save_path_filename_changed(self, filename: str) -> None:
        self._refresh_save_target_label(filename)
        if not self._is_save_path_dialog_open():
            return
        if str(filename or "").strip():
            self._set_save_path_state_text("Save path: ready")
        else:
            self._set_save_path_state_text("Save path: required")

    def _is_save_path_dialog_open(self) -> bool:
        dialog = self._get_save_path_dialog()
        if dialog is None or not hasattr(dialog, "is_visible"):
            return False
        return bool(dialog.is_visible())

    def _on_input_changed(self, entry: Any) -> None:
        callback = self._signal_handlers.get("on_change_input_text")
        text_l = self._input_path_l.strip()
        text_r = self._input_path_r.strip()

        entry_l = self._objects.get("entPathL")
        if not text_l and entry_l is not None and hasattr(entry_l, "get_text"):
            text_l = str(entry_l.get_text() or "").strip()

        entry_r = self._objects.get("entPathR")
        if not text_r and entry_r is not None and hasattr(entry_r, "get_text"):
            text_r = str(entry_r.get_text() or "").strip()

        input_values = [value for value in (text_l, text_r) if value]
        text = ",".join(input_values)
        has_input = bool(input_values)
        # Why: avoid invalid optimize/apply calls when the input field is empty.
        self._set_button_enabled("btnSave", has_input)
        self._set_button_enabled("btnOptimize", has_input)
        self._set_button_enabled("btnSetWall", False)
        if not has_input:
            self._set_save_path_dialog_open_state(False, state_text="Save path: reset")
        self._set_label_text("lblOptimizeResult", "Optimize result: not-run")
        self._set_label_text("lblApplyTarget", "Apply target: not-ready")

        if callback is None:
            return

        try:
            callback(text)
            self._set_feedback(phase="Input", state="updated")
        except Exception as exc:
            self._set_feedback(phase="Input", state="failed", error=str(exc))

    def _on_pick_input_clicked(self, side: str) -> None:
        value = self._input_path_l if side == "L" else self._input_path_r

        dialog = self._objects.get("ImgOpenDialog")
        if dialog is None or not hasattr(dialog, "open_for_side"):
            self._set_label_text("lblPickState", f"Open-{side}: handler-missing")
            self._set_feedback(
                phase=f"Open-{side}",
                state="handler-missing",
                error="open dialog not available",
            )
            return

        dialog.open_for_side(side, value)
        self._set_label_text("lblPickState", f"Open-{side}: dialog-open")
        self._set_feedback(phase=f"Open-{side}", state="dialog-open")

    def _notify_open_dialog_destroy(self) -> None:
        callback = self._signal_handlers.get("on_close_open_image_dialog")
        if callback is None:
            return
        try:
            callback()
        except Exception:
            pass

    def _on_open_dialog_confirmed(self) -> None:
        dialog = self._objects.get("ImgOpenDialog")
        if dialog is None:
            self._set_feedback(phase="Open", state="error", error="open dialog not available")
            return

        side = "L"
        if hasattr(dialog, "get_side"):
            side = str(dialog.get_side() or "L").upper()

        filename = ""
        if hasattr(dialog, "get_filename"):
            filename = str(dialog.get_filename() or "").strip()

        if not filename:
            self._set_label_text("lblPickState", f"Open-{side}: awaiting-selection")
            self._set_feedback(
                phase=f"Open-{side}",
                state="awaiting-selection",
                error="image selection required",
            )
            return

        callback = self._signal_handlers.get("on_pick_input")
        if callback is None:
            self._set_label_text("lblPickState", f"Open-{side}: handler-missing")
            self._set_feedback(
                phase=f"Open-{side}",
                state="handler-missing",
                error="handler not connected",
            )
            return

        try:
            callback(filename, side)
            entry_name = "entPathL" if side == "L" else "entPathR"
            if side == "L":
                self._input_path_l = filename
            else:
                self._input_path_r = filename
            entry = self._objects.get(entry_name)
            if entry is not None and hasattr(entry, "set_text"):
                entry.set_text(self._format_input_display(filename))
                try:
                    if hasattr(entry, "emit"):
                        entry.emit("changed", entry)
                    else:
                        self._on_input_changed(entry)
                except Exception:
                    self._on_input_changed(entry)
            if hasattr(dialog, "hide"):
                dialog.hide()
            self._set_label_text("lblPickState", f"Open-{side}: selected")
            self._set_feedback(phase=f"Open-{side}", state="selected")
            self._notify_open_dialog_destroy()
        except Exception as exc:
            self._set_label_text("lblPickState", f"Open-{side}: error")
            self._set_feedback(phase=f"Open-{side}", state="error", error=str(exc))

    def _on_open_dialog_canceled(self, destroyed: bool = False) -> None:
        dialog = self._objects.get("ImgOpenDialog")
        side = "L"
        if dialog is not None:
            if hasattr(dialog, "get_side"):
                side = str(dialog.get_side() or "L").upper()
            if hasattr(dialog, "hide"):
                dialog.hide()

        state = "closed" if destroyed else "canceled"
        self._set_label_text("lblPickState", f"Open-{side}: {state}")
        self._set_feedback(phase=f"Open-{side}", state=state)
        self._notify_open_dialog_destroy()

    def _format_input_display(self, path: str) -> str:
        value = str(path or "").strip()
        if not value:
            return ""
        try:
            return Path(value).name or value
        except Exception:
            return value

    def _on_clear_input_clicked(self, side: str) -> None:
        entry_name = "entPathL" if side == "L" else "entPathR"
        if side == "L":
            self._input_path_l = ""
        else:
            self._input_path_r = ""

        entry = self._objects.get(entry_name)
        if entry is not None and hasattr(entry, "set_text"):
            entry.set_text("")

        self._on_input_changed(entry)
        self._set_feedback(phase=f"Clear-{side}", state="ok")

    def _current_srcdir_for_side(self, side: str) -> str:
        return self._watch_srcdir_l if side == "L" else self._watch_srcdir_r

    def _on_pick_srcdir_clicked(self, side: str) -> None:
        dialog = self._objects.get("SrcdirDialog")
        if dialog is None or not hasattr(dialog, "open_for_side"):
            self._set_feedback(
                phase=f"Srcdir-{side}",
                state="handler-missing",
                error="srcdir dialog not available",
            )
            return

        dialog.open_for_side(side, self._current_srcdir_for_side(side))
        self._set_feedback(phase=f"Srcdir-{side}", state="dialog-open")

    def _on_srcdir_dialog_confirmed(self) -> None:
        dialog = self._objects.get("SrcdirDialog")
        if dialog is None:
            self._set_feedback(phase="Srcdir", state="error", error="srcdir dialog not available")
            return

        side = "L"
        if hasattr(dialog, "get_side"):
            side = str(dialog.get_side() or "L").upper()

        folder = ""
        if hasattr(dialog, "get_current_folder"):
            folder = str(dialog.get_current_folder() or "").strip()

        if not folder:
            self._set_feedback(
                phase=f"Srcdir-{side}",
                state="awaiting-selection",
                error="source directory is required",
            )
            return

        callback = self._signal_handlers.get("on_pick_watch_srcdir")
        if callback is None:
            self._set_feedback(
                phase=f"Srcdir-{side}",
                state="handler-missing",
                error="handler not connected",
            )
            return

        try:
            ok = callback(folder, side)
            if not ok:
                self._set_feedback(
                    phase=f"Srcdir-{side}",
                    state="select-failed",
                    error="srcdir selection returned false",
                )
                return

            if side == "L":
                self._watch_srcdir_l = folder
            else:
                self._watch_srcdir_r = folder
            self._refresh_watch_source_labels()
            if hasattr(dialog, "hide"):
                dialog.hide()
            self._set_feedback(phase=f"Srcdir-{side}", state="selected")
            self._notify_srcdir_dialog_destroy()
        except Exception as exc:
            self._set_feedback(phase=f"Srcdir-{side}", state="error", error=str(exc))

    def _on_srcdir_dialog_canceled(self, destroyed: bool = False) -> None:
        dialog = self._objects.get("SrcdirDialog")
        side = "L"
        if dialog is not None:
            if hasattr(dialog, "get_side"):
                side = str(dialog.get_side() or "L").upper()
            if hasattr(dialog, "hide"):
                dialog.hide()
        state = "closed" if destroyed else "canceled"
        self._set_feedback(phase=f"Srcdir-{side}", state=state)
        self._notify_srcdir_dialog_destroy()

    def _on_watch_interval_changed(self, widget: Any) -> None:
        callback = self._signal_handlers.get("on_watch_interval_change")
        if callback is None:
            self._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
            return
        try:
            interval = 0
            if hasattr(widget, "get_value_as_int"):
                interval = int(widget.get_value_as_int())
            elif hasattr(widget, "get_value"):
                interval = int(widget.get_value())

            owner = self._get_handler_owner("on_watch_interval_change")
            if owner is not None:
                ok = callback(interval)
            else:
                ok = callback(widget)

            if ok:
                self._set_feedback(phase="Watch", state=f"interval-updated({interval}s)")
            else:
                self._set_feedback(phase="Watch", state="interval-failed", error="interval returned false")
        except Exception as exc:
            self._set_feedback(phase="Watch", state="error", error=str(exc))

    def _on_watch_start_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_watch_start")
        if callback is None:
            self._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
            return
        try:
            owner = self._get_handler_owner("on_watch_start")
            ok = callback()
            if not ok:
                if owner is not None:
                    self._sync_watch_state_from_owner(owner)
                    self._sync_feedback_from_owner(owner)
                else:
                    self._set_feedback(phase="Watch", state="start-failed", error="watch start returned false")
                return

            if owner is not None:
                self._sync_watch_state_from_owner(owner)
                interval_seconds = int(getattr(owner, "watch_interval_seconds", 0) or 0)
                self._start_watch_timer(interval_seconds)
                self._set_feedback(phase="Watch", state="started")
                return

            selected_left = "-"
            selected_right = "-"
            if self._watch_srcdir_l:
                selected_left = self._run_watch_cycle_for_side("L", Path(self._watch_srcdir_l))
            if self._watch_srcdir_r:
                selected_right = self._run_watch_cycle_for_side("R", Path(self._watch_srcdir_r))

            self._watch_running = True
            self._refresh_watch_summary_label()
            self._refresh_watch_source_labels()
            self._refresh_watch_current_label(selected_left, selected_right)
            interval_widget = self._objects.get("spnInterval")
            interval_seconds = 0
            if interval_widget is not None and hasattr(interval_widget, "get_value_as_int"):
                interval_seconds = int(interval_widget.get_value_as_int())
            self._start_watch_timer(interval_seconds)
            self._set_feedback(phase="Watch", state="started")
        except Exception as exc:
            self._set_feedback(phase="Watch", state="error", error=str(exc))

    def _on_watch_stop_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_watch_stop")
        if callback is None:
            self._set_feedback(phase="Watch", state="handler-missing", error="handler not connected")
            return
        try:
            ok = callback()
            if not ok:
                self._set_feedback(phase="Watch", state="stop-ignored")
                return

            owner = self._get_handler_owner("on_watch_stop")
            if owner is not None:
                self._stop_watch_timer()
                self._sync_watch_state_from_owner(owner)
                self._set_feedback(phase="Watch", state="stopped")
                return

            self._watch_running = False
            self._stop_watch_timer()
            self._refresh_watch_summary_label()
            self._refresh_watch_current_label()
            self._set_feedback(phase="Watch", state="stopped")
        except Exception as exc:
            self._set_feedback(phase="Watch", state="error", error=str(exc))

    def run_watch_cycle_once(self) -> bool:
        if not self._watch_running:
            return False

        callback = self._signal_handlers.get("on_watch_tick")
        if callback is not None:
            owner = self._get_handler_owner("on_watch_tick")
            try:
                ok = bool(callback())
            except Exception as exc:
                self._set_feedback(phase="Watch", state="error", error=str(exc))
                return False
            if not ok:
                if owner is not None:
                    self._sync_watch_state_from_owner(owner)
                    self._sync_feedback_from_owner(owner)
                return False

            if owner is not None:
                self._sync_watch_state_from_owner(owner)
                return True

        selected_left = "-"
        selected_right = "-"
        if self._watch_srcdir_l:
            try:
                selected_left = self._run_watch_cycle_for_side("L", Path(self._watch_srcdir_l))
            except ValueError as exc:
                self._set_feedback(phase="Watch", state="error", error=str(exc))
                return False
        if self._watch_srcdir_r:
            try:
                selected_right = self._run_watch_cycle_for_side("R", Path(self._watch_srcdir_r))
            except ValueError as exc:
                self._set_feedback(phase="Watch", state="error", error=str(exc))
                return False

        self._refresh_watch_current_label(selected_left, selected_right)
        return True

    def _set_toggle_active(self, object_name: str, active: bool) -> None:
        toggle = self._objects.get(object_name)
        if toggle is None:
            return
        if hasattr(toggle, "set_active"):
            toggle.set_active(bool(active))
            return
        setattr(toggle, "active", bool(active))

    def _set_preferences_two_screen_mode(self, value: object) -> None:
        raw = str(value).strip().lower() if value is not None else "off"
        is_auto = raw == "auto"
        is_on = raw in {"on", "true", "1"} or value is True
        self._set_toggle_active("radPrefsTwoScreenAuto", is_auto)
        self._set_toggle_active("radPrefsTwoScreenOn", is_on and not is_auto)
        self._set_toggle_active("radPrefsTwoScreenOff", not is_auto and not is_on)

    def _read_preferences_two_screen_mode(self) -> str | bool:
        if self._is_toggle_active("radPrefsTwoScreenAuto"):
            return "auto"
        if self._is_toggle_active("radPrefsTwoScreenOn"):
            return True
        return False

    def _set_preferences_apply_mode(self, value: object | None) -> None:
        mode = str(value or "single-file").strip().lower()
        self._prefs_apply_mode_syncing = True
        try:
            if mode == "per-monitor-auto-split":
                self._prefs_apply_mode_preserved = None
                self._set_toggle_active("radPrefsApplySingle", False)
                self._set_toggle_active("radPrefsApplyPerMonitor", True)
                return
            if mode == "single-file":
                self._prefs_apply_mode_preserved = None
                self._set_toggle_active("radPrefsApplySingle", True)
                self._set_toggle_active("radPrefsApplyPerMonitor", False)
                return

            # Preserve unsupported modes such as per-monitor-explicit without
            # surfacing them as editable GUI choices.
            self._prefs_apply_mode_preserved = mode
            self._set_toggle_active("radPrefsApplySingle", False)
            self._set_toggle_active("radPrefsApplyPerMonitor", False)
        finally:
            self._prefs_apply_mode_syncing = False

    def _read_preferences_apply_mode(self) -> str:
        if self._is_toggle_active("radPrefsApplyPerMonitor"):
            return "per-monitor-auto-split"
        if self._is_toggle_active("radPrefsApplySingle"):
            return "single-file"
        if self._prefs_apply_mode_preserved:
            return self._prefs_apply_mode_preserved
        return "single-file"

    def _on_preferences_apply_mode_toggled(self, widget: Any, mode: str) -> None:
        if self._prefs_apply_mode_syncing:
            return
        is_active = True
        if hasattr(widget, "get_active"):
            is_active = bool(widget.get_active())
        if not is_active:
            return
        self._prefs_apply_mode_preserved = None

    def _sync_preferences_widgets_from_dialog(self) -> dict[str, object]:
        dialog = self._objects.get("SettingsDialog")
        if dialog is None or not hasattr(dialog, "get_preferences_config"):
            return {}
        config = dict(dialog.get_preferences_config())
        self._set_entry_text("entPrefsResolution", config.get("resolution", "1920x1080"))
        self._set_entry_text("entPrefsLayout", config.get("layout", "mosaic"))
        self._set_entry_text("entPrefsScaling", config.get("scaling", "fit"))
        self._set_preferences_two_screen_mode(config.get("two_screen", False))
        self._set_entry_text("entPrefsLDisplay", config.get("l_display"))
        self._set_entry_text("entPrefsRDisplay", config.get("r_display"))
        self._set_entry_text("entPrefsMargins", config.get("margins"))
        self._set_toggle_active("tglPrefsFixed", bool(config.get("fixed", False)))
        self._set_entry_text("entPrefsAlign", format_position_pair(config.get("align", "center"), axis="align"))
        self._set_entry_text("entPrefsValign", format_position_pair(config.get("valign", "center"), axis="valign"))
        self._set_spin_value("spnPrefsPadding", int(config.get("padding", 0)))
        self._set_spin_value("spnPrefsQuality", int(config.get("quality", 90)))
        self._set_entry_text("entPrefsEmbedInfo", config.get("embed_info", "none"))
        self._set_entry_text("entPrefsEmbedText", config.get("embed_text"))
        self._set_entry_text("entPrefsEmbedPosition", config.get("embed_position", "auto"))
        self._set_spin_value("spnPrefsEmbedMaxLines", int(config.get("embed_max_lines", 3)))
        self._set_entry_text("entPrefsPlugin", config.get("plugin", "windows"))
        self._set_preferences_apply_mode(config.get("apply_mode", "single-file"))
        if hasattr(dialog, "get_import_path"):
            self._set_entry_text("entPrefsImportPath", dialog.get_import_path())
        if hasattr(dialog, "get_export_path"):
            self._set_entry_text("entPrefsExportPath", dialog.get_export_path())
        return config

    def _sync_preferences_dialog_from_widgets(self) -> dict[str, object]:
        dialog = self._objects.get("SettingsDialog")
        config: dict[str, object] = {}
        if dialog is not None and hasattr(dialog, "get_preferences_config"):
            config = dict(dialog.get_preferences_config())

        def _empty_to_none(value: str) -> str | None:
            return value if value else None

        config.update(
            {
                "resolution": self._read_entry_text("entPrefsResolution") or "1920x1080",
                "layout": self._read_entry_text("entPrefsLayout") or "mosaic",
                "scaling": self._read_entry_text("entPrefsScaling") or "fit",
                "two_screen": self._read_preferences_two_screen_mode(),
                "l_display": _empty_to_none(self._read_entry_text("entPrefsLDisplay")),
                "r_display": _empty_to_none(self._read_entry_text("entPrefsRDisplay")),
                "margins": _empty_to_none(self._read_entry_text("entPrefsMargins")),
                "fixed": self._is_toggle_active("tglPrefsFixed"),
                "align": list(parse_position_pair(self._read_entry_text("entPrefsAlign") or "center", axis="align")),
                "valign": list(parse_position_pair(self._read_entry_text("entPrefsValign") or "center", axis="valign")),
                "padding": self._read_spin_int("spnPrefsPadding"),
                "quality": self._read_spin_int("spnPrefsQuality"),
                "embed_info": self._read_entry_text("entPrefsEmbedInfo") or "none",
                "embed_text": _empty_to_none(self._read_entry_text("entPrefsEmbedText")),
                "embed_position": self._read_entry_text("entPrefsEmbedPosition") or "auto",
                "embed_max_lines": self._read_spin_int("spnPrefsEmbedMaxLines"),
                "plugin": self._read_entry_text("entPrefsPlugin") or "windows",
                "apply_mode": self._read_preferences_apply_mode(),
            }
        )

        import_path = self._read_entry_text("entPrefsImportPath")
        export_path = self._read_entry_text("entPrefsExportPath")
        if dialog is not None:
            if hasattr(dialog, "set_preferences_config"):
                dialog.set_preferences_config(config)
            if hasattr(dialog, "set_import_path"):
                dialog.set_import_path(import_path)
            if hasattr(dialog, "set_export_path"):
                dialog.set_export_path(export_path)
        return config

    def _refresh_preferences_dialog_config_from_getter(self) -> None:
        dialog = self._objects.get("SettingsDialog")
        getter = self._signal_handlers.get("on_get_preferences_config")
        if getter is None or dialog is None or not hasattr(dialog, "set_preferences_config"):
            return

        current_config: dict[str, object] = {}
        if hasattr(dialog, "get_preferences_config"):
            current_config = dict(dialog.get_preferences_config())

        refreshed = dict(current_config)
        refreshed.update(dict(getter()))
        dialog.set_preferences_config(refreshed)

    def _is_toggle_active(self, object_name: str) -> bool:
        toggle = self._objects.get(object_name)
        if toggle is None:
            return False
        if hasattr(toggle, "get_active"):
            return bool(toggle.get_active())
        return bool(getattr(toggle, "active", False))

    def _current_side_state(self, side: str) -> tuple[str, str]:
        align = "center"
        valign = "center"

        if self._is_toggle_active(f"tglPushLeft{side}"):
            align = "left"
        elif self._is_toggle_active(f"tglPushRight{side}"):
            align = "right"

        if self._is_toggle_active(f"tglUpper{side}"):
            valign = "top"
        elif self._is_toggle_active(f"tglLower{side}"):
            valign = "bottom"

        return align, valign

    def _refresh_current_state_labels(self) -> None:
        fixed_widget = self._objects.get("radFixed")
        fixed_enabled = False
        if fixed_widget is not None and hasattr(fixed_widget, "get_active"):
            fixed_enabled = bool(fixed_widget.get_active())

        left = self._read_spin_int("spnLMergin")
        right = self._read_spin_int("spnRMergin")
        top = self._read_spin_int("spnTopMergin")
        bottom = self._read_spin_int("spnBtmMergin")
        align_l, valign_l = self._current_side_state("L")
        align_r, valign_r = self._current_side_state("R")

        self._set_label_text("lblCurrentFixed", f"Current fixed: {'on' if fixed_enabled else 'off'}")
        self._set_label_text("lblCurrentMargins", f"Current margins: {left},{right},{top},{bottom}")
        self._set_label_text("lblCurrentStateL", f"Current L: align={align_l} valign={valign_l}")
        self._set_label_text("lblCurrentStateR", f"Current R: align={align_r} valign={valign_r}")

    def _on_fixed_toggled(self, widget: Any, fixed_enabled: bool) -> None:
        is_active = True
        if hasattr(widget, "get_active"):
            is_active = bool(widget.get_active())
        if not is_active:
            return

        self._refresh_current_state_labels()

        callback = self._signal_handlers.get("on_toggle_fixed")
        if callback is not None:
            try:
                callback(bool(fixed_enabled))
            except Exception:
                pass

    def _opposite_toggle_name(self, object_name: str) -> str | None:
        opposites = {
            "tglPushLeftL": "tglPushRightL",
            "tglPushRightL": "tglPushLeftL",
            "tglUpperL": "tglLowerL",
            "tglLowerL": "tglUpperL",
            "tglPushLeftR": "tglPushRightR",
            "tglPushRightR": "tglPushLeftR",
            "tglUpperR": "tglLowerR",
            "tglLowerR": "tglUpperR",
        }
        return opposites.get(object_name)

    def _on_direction_pressed(self, object_name: str) -> None:
        opposite_name = self._opposite_toggle_name(object_name)
        if opposite_name is not None:
            opposite_toggle = self._objects.get(opposite_name)
            if opposite_toggle is not None and hasattr(opposite_toggle, "get_active"):
                if bool(opposite_toggle.get_active()):
                    self._set_toggle_active(opposite_name, False)
                    reset_callback = self._signal_handlers.get("on_toggle_position_reset")
                    if reset_callback is not None:
                        try:
                            reset_callback(opposite_name)
                        except Exception:
                            pass
        self._refresh_current_state_labels()

        callback = self._signal_handlers.get("on_toggle_position_pressed")
        if callback is not None:
            try:
                callback(object_name)
            except Exception:
                pass

    def _on_direction_toggled(self, object_name: str) -> None:
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_toggle_position")
        active = self._is_toggle_active(object_name)
        if callback is not None:
            try:
                callback(object_name, active)
            except Exception:
                pass

        if not active:
            reset_callback = self._signal_handlers.get("on_toggle_position_reset")
            if reset_callback is not None:
                try:
                    reset_callback(object_name)
                except Exception:
                    pass

    def _on_direction_released(self, object_name: str) -> None:
        self._refresh_current_state_labels()
        return

    def _read_spin_int(self, object_name: str) -> int:
        spin = self._objects.get(object_name)
        if spin is None:
            return 0
        if hasattr(spin, "get_value_as_int"):
            return int(spin.get_value_as_int())
        if hasattr(spin, "get_value"):
            return int(spin.get_value())
        return 0

    def _on_margin_changed(self, widget: Any) -> None:
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_change_margins")

        if callback is None:
            self._set_feedback(phase="Margins", state="planned")
            return

        try:
            widget_name = widget.get_name() if hasattr(widget, "get_name") else ""
            value = 0
            if hasattr(widget, "get_value_as_int"):
                value = int(widget.get_value_as_int())
            elif hasattr(widget, "get_value"):
                value = int(widget.get_value())
            callback(widget_name, value)
            self._set_feedback(phase="Margins", state="updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="error", error=str(exc))

    def _run_optimize_path(self, callback: Callable[..., Any] | None) -> None:
        if callback is None:
            self._set_feedback(
                phase="Optimize",
                state="handler-missing",
                error="handler not connected",
            )
            self._set_button_enabled("btnSetWall", False)
            self._set_label_text("lblOptimizeResult", "Optimize result: handler-missing")
            self._set_label_text("lblApplyTarget", "Apply target: not-ready")
            return
        try:
            self._set_feedback(phase="Optimize", state="running")
            ok = callback()
            self._set_button_enabled("btnSetWall", bool(ok))
            if ok:
                self._set_feedback(phase="Optimize", state="ok")
                self._set_label_text("lblOptimizeResult", "Optimize result: success")
                self._set_label_text("lblApplyTarget", "Apply target: ready")
            else:
                self._set_feedback(
                    phase="Optimize",
                    state="failed",
                    error="optimize returned false",
                )
                self._set_label_text("lblOptimizeResult", "Optimize result: failed")
                self._set_label_text("lblApplyTarget", "Apply target: not-ready")
        except Exception as exc:
            self._set_button_enabled("btnSetWall", False)
            self._set_feedback(phase="Optimize", state="error", error=str(exc))
            self._set_label_text("lblOptimizeResult", "Optimize result: error")
            self._set_label_text("lblApplyTarget", "Apply target: not-ready")

    def _on_apply_mode_toggled(self, widget: Any, mode: str) -> None:
        is_active = True
        if hasattr(widget, "get_active"):
            is_active = bool(widget.get_active())
        label = "Apply the optimized image as a single file."
        if mode == "per-monitor-auto-split" and is_active:
            label = "Split the optimized image and apply per display."
        self._set_label_text("lblApplyMode", label)

        if not is_active:
            return

        callback = self._signal_handlers.get("on_change_apply_mode")
        if callback is None:
            return
        try:
            callback(mode)
            self._set_feedback(phase="ApplyMode", state="updated")
        except Exception as exc:
            self._set_feedback(phase="ApplyMode", state="error", error=str(exc))

    def _on_save_clicked(self, *_args: Any) -> None:
        # P6 direction: Save As keeps chooser semantics, but fallback should not
        # depend on separate confirm/cancel controls.
        callback = self._signal_handlers.get("on_save")
        if callback is not None:
            try:
                callback()
            except Exception:
                pass

        self._refresh_save_target_label()

        dialog = self._get_save_path_dialog()
        if dialog is not None and hasattr(dialog, "supports_native_dialog") and dialog.supports_native_dialog():
            if hasattr(dialog, "open_dialog"):
                dialog.open_dialog()
            return

        fallback_filename = self._current_save_path_filename()
        if not fallback_filename:
            fallback_filename = str(Path.home() / "harite-output.jpg")
        if dialog is not None and hasattr(dialog, "set_filename"):
            dialog.set_filename(fallback_filename)
        self._handle_save_path_confirm(fallback_filename)

    def _on_optimize_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_optimize")
        self._run_optimize_path(callback)

    def _on_apply_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_apply")
        if callback is None:
            self._set_feedback(
                phase="Apply",
                state="handler-missing",
                error="handler not connected",
            )
            self._set_label_text("lblApplyTarget", "Apply target: handler-missing")
            return
        try:
            self._set_feedback(phase="Apply", state="running")
            ok = callback()
            if ok:
                self._set_feedback(phase="Apply", state="ok")
                self._set_label_text("lblApplyTarget", "Apply target: last applied")
            else:
                self._set_feedback(
                    phase="Apply",
                    state="failed",
                    error="apply returned false",
                )
        except Exception as exc:
            self._set_feedback(phase="Apply", state="error", error=str(exc))

    def _on_settings_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_open_settings_dialog")
        dialog = self._objects.get("SettingsDialog")
        if callback is None:
            self._set_feedback(phase="Prefs", state="planned")
            return
        try:
            ok = callback()
            if ok:
                self._refresh_preferences_dialog_config_from_getter()
                self._sync_preferences_widgets_from_dialog()
                owner = self._get_handler_owner("on_open_settings_dialog")
                if owner is not None:
                    self._sync_watch_state_from_owner(owner)
                if dialog is not None and hasattr(dialog, "show"):
                    dialog.show()
                self._set_label_text("lblPrefsState", "Prefs: opened")
                self._set_feedback(phase="Prefs", state="opened")
            else:
                self._set_feedback(phase="Prefs", state="deferred")
        except Exception as exc:
            self._set_feedback(phase="Prefs", state="error", error=str(exc))

    def _on_preferences_apply_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_apply_preferences")
        dialog = self._objects.get("SettingsDialog")
        if callback is None or dialog is None or not hasattr(dialog, "get_preferences_config"):
            self._set_feedback(phase="PrefsApply", state="handler-missing", error="handler not connected")
            return
        try:
            ok = callback(self._sync_preferences_dialog_from_widgets())
            if ok:
                owner = self._get_handler_owner("on_apply_preferences")
                if owner is not None:
                    self._sync_watch_state_from_owner(owner)
                if hasattr(dialog, "hide"):
                    dialog.hide()
                self._set_label_text("lblPrefsState", "Prefs: applied")
                self._set_feedback(phase="PrefsApply", state="applied")
            else:
                self._set_feedback(phase="PrefsApply", state="failed", error="preferences apply returned false")
        except Exception as exc:
            self._set_feedback(phase="PrefsApply", state="error", error=str(exc))

    def _on_preferences_load_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_load_preferences_file")
        dialog = self._objects.get("SettingsDialog")
        if callback is None or dialog is None or not hasattr(dialog, "get_import_path"):
            self._set_feedback(phase="PrefsLoad", state="handler-missing", error="handler not connected")
            return
        try:
            self._sync_preferences_dialog_from_widgets()
            ok = callback(dialog.get_import_path())
            if ok:
                self._refresh_preferences_dialog_config_from_getter()
                self._sync_preferences_widgets_from_dialog()
                owner = self._get_handler_owner("on_load_preferences_file")
                if owner is not None:
                    self._sync_watch_state_from_owner(owner)
                self._set_label_text("lblPrefsState", "Prefs: loaded")
                self._set_feedback(phase="PrefsLoad", state="loaded")
            else:
                self._set_feedback(phase="PrefsLoad", state="failed", error="preferences load returned false")
        except Exception as exc:
            self._set_feedback(phase="PrefsLoad", state="error", error=str(exc))

    def _on_preferences_save_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_save_preferences_file")
        dialog = self._objects.get("SettingsDialog")
        if callback is None or dialog is None or not hasattr(dialog, "get_export_path"):
            self._set_feedback(phase="PrefsSave", state="handler-missing", error="handler not connected")
            return
        try:
            config = self._sync_preferences_dialog_from_widgets()
            try:
                ok = callback(dialog.get_export_path(), config)
            except TypeError:
                ok = callback(dialog.get_export_path())
            if ok:
                self._set_label_text("lblPrefsState", "Prefs: saved")
                self._set_feedback(phase="PrefsSave", state="saved")
            else:
                self._set_feedback(phase="PrefsSave", state="failed", error="preferences save returned false")
        except Exception as exc:
            self._set_feedback(phase="PrefsSave", state="error", error=str(exc))

    def _on_preferences_close_clicked(self, *_args: Any) -> None:
        dialog = self._objects.get("SettingsDialog")
        if dialog is not None and hasattr(dialog, "hide"):
            dialog.hide()
        callback = self._signal_handlers.get("on_close_settings_dialog")
        if callback is not None:
            try:
                callback()
            except Exception:
                pass
        self._set_label_text("lblPrefsState", "Prefs: closed")
        self._set_feedback(phase="Prefs", state="closed")

    def _on_preferences_window_delete_event(self) -> bool:
        self._on_preferences_close_clicked()
        return True

    def _on_color_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_set_color")
        if callback is None:
            self._set_feedback(phase="Color", state="deferred")
            return
        try:
            callback()
            self._set_feedback(phase="Color", state="deferred")
        except Exception as exc:
            self._set_feedback(phase="Color", state="error", error=str(exc))

    def _handle_save_path_confirm(self, filename: str) -> None:
        callback = self._signal_handlers.get("on_save_path_selected")
        if callback is None:
            self._set_feedback(phase="SavePath", state="handler-missing", error="handler not connected")
            return
        try:
            if not filename:
                self._set_save_path_state_text("Save path: required")
                self._set_feedback(phase="SavePath", state="path-required", error="save path is required")
                return
            self._refresh_save_target_label(filename)
            ok = callback(filename)
            if ok:
                self._set_save_path_dialog_open_state(False, state_text="Save path: saved")
                self._set_feedback(phase="SavePath", state="saved")
                self._notify_save_path_dialog_destroy()
            else:
                self._set_feedback(phase="SavePath", state="failed", error="save path acceptance returned false")
        except Exception as exc:
            self._set_feedback(phase="SavePath", state="error", error=str(exc))

    def _handle_save_path_cancel(self) -> None:
        callback = self._signal_handlers.get("on_save_path_selection_canceled")
        if callback is not None:
            try:
                callback()
            except Exception as exc:
                self._set_feedback(phase="SavePath", state="error", error=str(exc))
                return
        self._set_save_path_dialog_open_state(False, state_text="Save path: canceled")
        self._set_feedback(phase="SavePath", state="canceled")
        self._notify_save_path_dialog_destroy()

    def _on_native_save_path_confirmed(self) -> None:
        self._handle_save_path_confirm(self._current_save_path_filename())

    def _on_native_save_path_canceled(self) -> None:
        self._handle_save_path_cancel()


def load_gtk_builder_signal_backend(ui_file: Path | None = None):
    """Return a GTK Builder object that supports `connect_signals(mapping)`.

    When the UI file is incompatible with Gtk.Builder, a minimal runtime
    backend is returned so present/bind flows can continue without runtime
    Glade dependency.
    """
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except Exception as exc:  # pragma: no cover - depends on host GTK runtime.
        raise RuntimeError(f"GTK backend unavailable: {exc}") from exc

    if ui_file is None:
        return GtkRuntimeSignalBackend(Gtk)

    builder = Gtk.Builder()
    try:
        builder.add_from_file(str(ui_file))
    except Exception as exc:  # pragma: no cover - requires GTK runtime.
        # Why: legacy resources may use old Glade schema (<glade-interface>).
        # Keep runtime path alive by falling back to a minimal GTK window backend.
        return GtkRuntimeSignalBackend(Gtk)

    return builder


def _resolve_window(signal_backend, requested_id: str):
    window = signal_backend.get_object(requested_id)
    if window is not None:
        return window

    # Fallback IDs that may appear in legacy GTK/Glade exports.
    for candidate in ("main_window", "window1"):
        window = signal_backend.get_object(candidate)
        if window is not None:
            return window

    # Last fallback: first top-level GTK Window-like object.
    if hasattr(signal_backend, "get_objects"):
        for obj in signal_backend.get_objects():
            if obj.__class__.__name__.endswith("Window"):
                return obj
    return None


def present_gtk_window(signal_backend, *, window_id: str = "WallPosit_MainWindow") -> bool:
    """Present the real GTK window and enter the main loop.

    Returns True when the target window object is found and shown.
    """
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except Exception as exc:  # pragma: no cover - depends on host GTK runtime.
        raise RuntimeError(f"GTK runtime unavailable: {exc}") from exc

    if not hasattr(signal_backend, "get_object"):
        raise TypeError("signal backend must provide get_object(name)")

    window = _resolve_window(signal_backend, window_id)
    if window is None:
        return False

    # Ensure the minimal prototype flow can exit Gtk.main() by window close.
    if hasattr(window, "connect") and not getattr(window, "_harite_quit_hooked", False):

        def _on_delete_event(*_args):
            Gtk.main_quit()
            return False

        window.connect("delete-event", _on_delete_event)
        setattr(window, "_harite_quit_hooked", True)

    if hasattr(window, "show_all"):
        window.show_all()
    if hasattr(window, "present"):
        window.present()

    Gtk.main()
    return True

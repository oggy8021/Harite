"""GTK backend loader for optional UI signal binding.

This adapter is intentionally optional. It should only be used in environments
where PyGObject/GTK is available.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


class GtkRuntimeSignalBackend:
    """Minimal GTK runtime backend that does not require Glade parsing.

    This fallback keeps present/bind flows usable even when a legacy Glade
    resource cannot be consumed by Gtk.Builder at runtime.
    """

    def __init__(self, gtk_module: Any) -> None:
        self._gtk = gtk_module
        self._signal_handlers: dict[str, Callable[..., Any]] = {}

        window = gtk_module.Window(title="Harite Studio")
        if hasattr(window, "set_resizable"):
            # P5-2 policy: modern desktop UX expects a resizable main window.
            window.set_resizable(True)
        if hasattr(window, "set_default_size"):
            window.set_default_size(960, 640)

        if hasattr(gtk_module, "Box") and hasattr(gtk_module, "Label"):
            root = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=8)
            root.set_border_width(10)

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
            if hasattr(top_margin_spin, "set_numeric"):
                top_margin_spin.set_numeric(True)
            top_row.pack_start(top_margin_spin, False, False, 0)

            top_spacer_r = gtk_module.Label(label="")
            top_row.pack_start(top_spacer_r, True, True, 0)

            # Row 1: center body (Glade hbox2 equivalent)
            center_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=10)
            root.pack_start(center_row, True, True, 0)

            left_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            center_row.pack_start(left_margin_col, False, False, 0)

            left_margin_label = gtk_module.Label(label="左マージン(px)")
            if hasattr(left_margin_label, "set_xalign"):
                left_margin_label.set_xalign(0.0)
            left_margin_col.pack_start(left_margin_label, False, False, 0)

            left_margin_spin = gtk_module.SpinButton()
            if hasattr(left_margin_spin, "set_numeric"):
                left_margin_spin.set_numeric(True)
            left_margin_col.pack_start(left_margin_spin, False, False, 0)

            main_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            center_row.pack_start(main_col, True, True, 0)

            title = gtk_module.Label(label="Wallpaper Optimizer")
            if hasattr(title, "set_xalign"):
                title.set_xalign(0.0)
            main_col.pack_start(title, False, False, 0)

            subtitle = gtk_module.Label(label="Glade-like layout (Phase5 P5-2)")
            if hasattr(subtitle, "set_xalign"):
                subtitle.set_xalign(0.0)
            main_col.pack_start(subtitle, False, False, 0)

            upper_toggle_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(upper_toggle_row, False, False, 0)
            tgl_upper_l = gtk_module.ToggleButton(label="Upper-L")
            tgl_upper_r = gtk_module.ToggleButton(label="Upper-R")
            upper_toggle_row.pack_start(tgl_upper_l, False, False, 0)
            upper_toggle_row.pack_start(tgl_upper_r, False, False, 0)

            file_pick_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(file_pick_row, False, False, 0)
            btn_get_img_l = gtk_module.Button(label="Open-L")
            btn_get_img_r = gtk_module.Button(label="Open-R")
            file_pick_row.pack_start(btn_get_img_l, False, False, 0)
            file_pick_row.pack_start(btn_get_img_r, False, False, 0)

            input_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(input_row, False, False, 0)
            input_entry = gtk_module.Entry()
            input_entry.set_placeholder_text("/path/to/image_or_directory")
            btn_clr_path_l = gtk_module.Button(label="Clear-L")
            btn_clr_path_r = gtk_module.Button(label="Clear-R")
            input_row.pack_start(input_entry, True, True, 0)
            input_row.pack_start(btn_clr_path_l, False, False, 0)
            input_row.pack_start(btn_clr_path_r, False, False, 0)

            fixed_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(fixed_row, False, False, 0)
            rad_fixed = gtk_module.RadioButton.new_with_label(None, "入替不可")
            rad_no_fixed = gtk_module.RadioButton.new_with_label_from_widget(rad_fixed, "入替可")
            fixed_row.pack_start(rad_fixed, False, False, 0)
            fixed_row.pack_start(rad_no_fixed, False, False, 0)

            optimize_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(optimize_row, False, False, 0)
            optimize_section_label = gtk_module.Label(label="Optimize")
            if hasattr(optimize_section_label, "set_xalign"):
                optimize_section_label.set_xalign(0.0)
            optimize_row.pack_start(optimize_section_label, False, False, 0)
            optimize_result = gtk_module.Label(label="Optimize result: not-run")
            if hasattr(optimize_result, "set_xalign"):
                optimize_result.set_xalign(0.0)
            optimize_row.pack_start(optimize_result, True, True, 0)

            apply_row = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            main_col.pack_start(apply_row, False, False, 0)
            apply_section_label = gtk_module.Label(label="Apply")
            if hasattr(apply_section_label, "set_xalign"):
                apply_section_label.set_xalign(0.0)
            apply_row.pack_start(apply_section_label, False, False, 0)
            apply_target = gtk_module.Label(label="Apply target: not-ready")
            if hasattr(apply_target, "set_xalign"):
                apply_target.set_xalign(0.0)
            apply_row.pack_start(apply_target, True, True, 0)

            right_margin_col = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=6)
            center_row.pack_start(right_margin_col, False, False, 0)

            right_margin_label = gtk_module.Label(label="右マージン(px)")
            if hasattr(right_margin_label, "set_xalign"):
                right_margin_label.set_xalign(0.0)
            right_margin_col.pack_start(right_margin_label, False, False, 0)

            right_margin_spin = gtk_module.SpinButton()
            if hasattr(right_margin_spin, "set_numeric"):
                right_margin_spin.set_numeric(True)
            right_margin_col.pack_start(right_margin_spin, False, False, 0)

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
            if hasattr(bottom_margin_spin, "set_numeric"):
                bottom_margin_spin.set_numeric(True)
            bottom_margin_row.pack_start(bottom_margin_spin, False, False, 0)
            btm_spacer_r = gtk_module.Label(label="")
            bottom_margin_row.pack_start(btm_spacer_r, True, True, 0)

            # Row 3: command bar (Glade hbox14 equivalent)
            command_bar = gtk_module.Box(orientation=gtk_module.Orientation.HORIZONTAL, spacing=6)
            root.pack_start(command_bar, False, False, 0)
            btn_setting = gtk_module.Button(label="Prefs")
            btn_set_color = gtk_module.Button(label="Color")
            optimize_btn = gtk_module.Button(label="Save")
            if hasattr(optimize_btn, "set_sensitive"):
                optimize_btn.set_sensitive(False)
            apply_btn = gtk_module.Button(label="Apply")
            if hasattr(apply_btn, "set_sensitive"):
                apply_btn.set_sensitive(False)
            interval_spin = gtk_module.SpinButton()
            if hasattr(interval_spin, "set_numeric"):
                interval_spin.set_numeric(True)
            interval_label = gtk_module.Label(label="秒")
            btn_daemonize = gtk_module.Button(label="Execute")
            btn_cancel_daemonize = gtk_module.Button(label="Stop")
            btn_about = gtk_module.Button(label="About")
            btn_help = gtk_module.Button(label="Help")
            command_bar.pack_start(btn_setting, False, False, 0)
            command_bar.pack_start(btn_set_color, False, False, 0)
            command_bar.pack_start(optimize_btn, False, False, 0)
            command_bar.pack_start(apply_btn, False, False, 0)
            command_bar.pack_start(interval_spin, False, False, 0)
            command_bar.pack_start(interval_label, False, False, 0)
            command_bar.pack_start(btn_daemonize, False, False, 0)
            command_bar.pack_start(btn_cancel_daemonize, False, False, 0)
            command_bar.pack_start(btn_about, False, False, 0)
            command_bar.pack_start(btn_help, False, False, 0)

            # Row 4: status row (Glade statusbar equivalent)
            status_row = gtk_module.Box(orientation=gtk_module.Orientation.VERTICAL, spacing=2)
            root.pack_start(status_row, False, False, 0)
            status_label = gtk_module.Label(label="Status: ready")
            if hasattr(status_label, "set_xalign"):
                status_label.set_xalign(0.0)
            status_row.pack_start(status_label, False, False, 0)
            error_label = gtk_module.Label(label="Error: none")
            if hasattr(error_label, "set_xalign"):
                error_label.set_xalign(0.0)
            status_row.pack_start(error_label, False, False, 0)

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
                "boxMainSection": main_section,
                "btnGetImgL": btn_get_img_l,
                "btnGetImgR": btn_get_img_r,
                "entPathL": input_entry,
                "btnClrPathL": btn_clr_path_l,
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
                "btnSave": optimize_btn,
                "lblOptimizeResult": optimize_result,
                "lblApplySection": apply_section_label,
                "btnSetWall": apply_btn,
                "lblApplyTarget": apply_target,
                "hbox14": command_bar,
                "btnSetting": btn_setting,
                "btnSetColor": btn_set_color,
                "spnInterval": interval_spin,
                "lblInterval": interval_label,
                "btnDaemonize": btn_daemonize,
                "btnCancelDaemonize": btn_cancel_daemonize,
                "btnAbout": btn_about,
                "btnHelp": btn_help,
                "statusbar": status_row,
                "lblStatus": status_label,
                "lblError": error_label,
            }

            # Why: fallback window must still exercise MainWindow handlers even when
            # legacy glade cannot be parsed at runtime.
            input_entry.connect("changed", self._on_input_changed)
            optimize_btn.connect("clicked", self._on_optimize_clicked)
            apply_btn.connect("clicked", self._on_apply_clicked)
        else:
            self._objects = {
                "WallPosit_MainWindow": window,
                "main_window": window,
                "window1": window,
            }

    def connect_signals(self, mapping: dict[str, Callable[..., Any]]) -> None:
        self._signal_handlers.update(mapping)

    def connect(self, handler_name: str, callback: Callable[..., Any]) -> None:
        self._signal_handlers[handler_name] = callback

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

    def _set_button_enabled(self, object_name: str, enabled: bool) -> None:
        button = self._objects.get(object_name)
        if button is not None and hasattr(button, "set_sensitive"):
            button.set_sensitive(bool(enabled))

    def _on_input_changed(self, entry: Any) -> None:
        callback = self._signal_handlers.get("on_entPath_insert_text")
        text = entry.get_text() if hasattr(entry, "get_text") else ""
        has_input = bool(text and str(text).strip())
        # Why: avoid invalid optimize/apply calls when the input field is empty.
        self._set_button_enabled("btnSave", has_input)
        self._set_button_enabled("btnSetWall", False)
        self._set_label_text("lblOptimizeResult", "Optimize result: not-run")
        self._set_label_text("lblApplyTarget", "Apply target: not-ready")

        if callback is None:
            return

        try:
            callback(text)
            self._set_feedback(phase="Input", state="updated")
        except Exception as exc:
            self._set_feedback(phase="Input", state="failed", error=str(exc))

    def _on_optimize_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_btnSave_clicked")
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

    def _on_apply_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_btnSetWall_clicked")
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
                self._set_feedback(phase="Apply", state="dry-run-ok")
                self._set_label_text("lblApplyTarget", "Apply target: consumed")
            else:
                self._set_feedback(
                    phase="Apply",
                    state="dry-run-failed",
                    error="apply returned false",
                )
        except Exception as exc:
            self._set_feedback(phase="Apply", state="error", error=str(exc))


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

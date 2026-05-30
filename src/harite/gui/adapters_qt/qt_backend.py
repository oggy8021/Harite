"""Qt runtime backend for Harite GUI (Phase 8: signal wiring complete)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from harite.gui.views.main_window import MainWindow

_WINDOW_TITLE = "Harite"
_WINDOW_WIDTH = 900
_WINDOW_HEIGHT = 640


class QtSignalBackend:  # noqa: PLR0904 – mirrors GTK backend surface
    """Qt runtime backend wrapping QApplication + QMainWindow.

    Phases 2–8:
    - Builds the 3-layer layout + all tabs (Phases 2–5).
    - Builds all dialogs + file-dialog proxies (Phase 6).
    - Optionally installs QSystemTrayIcon (Phase 7).
    - Provides the full widget-helper interface (_set_*, _read_*, _is_*)
      and signal wiring (Phase 8).
    """

    def __init__(self, qapp: Any, qwindow: Any) -> None:
        self._qapp = qapp
        self._qwindow = qwindow
        self._objects: dict[str, Any] = {"main_window": qwindow}
        self._signal_handlers: dict[str, Callable[..., Any]] = {}
        self._tray_adapter: Any | None = None

        # Runtime state (mirrors gtk_backend initialisation)
        self._slideshow_running: bool = False
        self._slideshow_paused: bool = False
        self._slideshow_srcdir_l: str = ""
        self._slideshow_srcdir_r: str = ""
        self._slideshow_state_l: Any = None
        self._slideshow_state_r: Any = None
        self._slideshow_previous_l: Any = None
        self._slideshow_previous_r: Any = None
        self._input_path_l: str = ""
        self._input_path_r: str = ""
        self.slideshow_mode: str = "random"
        self._slideshow_active_mode: str = "random"
        self._slideshow_timer: Any | None = None

        # Settings dialog helpers
        self._prefs_apply_mode_syncing: bool = False
        self._prefs_apply_mode_preserved: str | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def qapp(self) -> Any:
        return self._qapp

    @property
    def qwindow(self) -> Any:
        return self._qwindow

    @property
    def objects(self) -> dict[str, Any]:
        """Widget registry keyed by both snake_case and camelCase aliases."""
        return self._objects

    @property
    def tray_adapter(self) -> Any | None:
        return self._tray_adapter

    # ------------------------------------------------------------------
    # Layout + dialogs + aliases
    # ------------------------------------------------------------------

    def build_layout(self) -> None:
        """Populate QMainWindow, build all dialogs, and extend with aliases."""
        from harite.gui.adapters_qt.qt_dialogs import build_dialogs
        from harite.gui.adapters_qt.qt_layout_builders import build_main_layout
        from harite.gui.adapters_qt.qt_object_registry import build_qt_object_aliases

        self._objects = build_main_layout(self._qwindow)
        self._objects.update(build_dialogs(self._qwindow))
        self._objects["main_window"] = self._qwindow

        # Extend with GTK-style camelCase aliases used by sync functions
        self._objects.update(build_qt_object_aliases(self._objects))

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def connect_signals(self, dispatch: dict[str, Any]) -> None:
        """Store the signal dispatch table and wire Qt widget signals."""
        from harite.gui.adapters_qt.qt_signal_wiring import connect_qt_widgets

        self._signal_handlers = dict(dispatch)
        connect_qt_widgets(self, self._objects)

    # ------------------------------------------------------------------
    # Tray
    # ------------------------------------------------------------------

    def install_tray(self) -> bool:
        """Install QSystemTrayIcon if available.  Returns True on success."""
        from harite.gui.adapters_qt.qt_tray_adapter import initialize_qt_tasktray

        adapter = initialize_qt_tasktray(self)
        self._tray_adapter = adapter
        return adapter is not None

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def present(self) -> None:
        """Show the window and start the Qt event loop."""
        self._qwindow.show()
        self._qapp.exec()

    # ------------------------------------------------------------------
    # Object access (GTK interface compatibility)
    # ------------------------------------------------------------------

    def get_object(self, name: str) -> Any:
        return self._objects.get(name)

    def get_objects(self) -> list[Any]:
        return list(self._objects.values())

    # ------------------------------------------------------------------
    # Handler owner helpers
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Widget helper methods (call qt_widget_helpers free functions)
    # ------------------------------------------------------------------

    def _set_status(self, message: str) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_status
        set_status(self, message)

    def _set_error(self, message: str | None) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_error
        set_error(self, message)

    def _set_feedback(self, *, phase: str, state: str, error: str | None = None) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_feedback
        set_feedback(self, phase=phase, state=state, error=error)

    def _set_label_text(self, name: str, value: object | None) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_label_text
        set_label_text(self, name, value)

    def _set_entry_text(self, name: str, value: object | None) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_entry_text
        set_entry_text(self, name, value)

    def _read_entry_text(self, name: str) -> str:
        from harite.gui.adapters_qt.qt_widget_helpers import read_entry_text
        return read_entry_text(self, name)

    def _set_spin_value(self, name: str, value: int) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_spin_value
        set_spin_value(self, name, value)

    def _read_spin_int(self, name: str) -> int:
        from harite.gui.adapters_qt.qt_widget_helpers import read_spin_int
        return read_spin_int(self, name)

    def _set_button_enabled(self, name: str, enabled: bool) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_button_enabled
        set_button_enabled(self, name, enabled)

    def _set_widget_enabled(self, name: str, enabled: bool) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_widget_enabled
        set_widget_enabled(self, name, enabled)

    def _set_toggle_active(self, name: str, active: bool) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_toggle_active
        set_toggle_active(self, name, active)

    def _is_toggle_active(self, name: str) -> bool:
        from harite.gui.adapters_qt.qt_widget_helpers import is_toggle_active
        return is_toggle_active(self, name)

    def _set_notebook_page(self, name: str, page_index: int) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_notebook_page
        set_notebook_page(self, name, page_index)

    def _set_save_path_state_text(self, message: str) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_save_path_state_text
        set_save_path_state_text(self, message)

    def _refresh_save_target_label(self, filename: str | None = None) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import refresh_save_target_label
        refresh_save_target_label(self, filename)

    def _refresh_slideshow_source_labels(self) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_source_labels
        refresh_slideshow_source_labels(self)

    def _refresh_slideshow_summary_label(self) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_summary_label
        refresh_slideshow_summary_label(self)

    def _refresh_slideshow_current_label(
        self, left: str | None = None, right: str | None = None
    ) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_current_label
        refresh_slideshow_current_label(self, left, right)

    def _refresh_slideshow_output_label(self, output_dir: str | None = None) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_output_label
        refresh_slideshow_output_label(self, output_dir)

    def _refresh_current_state_labels(self) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import refresh_current_state_labels
        refresh_current_state_labels(self)

    def _format_input_display(self, path: str) -> str:
        from harite.gui.adapters_qt.qt_widget_helpers import format_input_display
        return format_input_display(path)

    # ------------------------------------------------------------------
    # Preview widget
    # ------------------------------------------------------------------

    def _set_preview_widget(
        self,
        name: str,
        source_path: Path | None,
        *,
        crop_box: tuple[int, int, int, int] | None = None,
    ) -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import set_preview_pixmap
        set_preview_pixmap(self, name, source_path)

    def _clear_preview_widget(self, name: str, message: str = "") -> None:
        from harite.gui.adapters_qt.qt_widget_helpers import clear_preview
        clear_preview(self, name, message)

    def _preview_target_size(self) -> tuple[int, int]:
        return (160, 90)

    def _sync_result_preview_from_owner(self, owner: Any) -> None:
        # Best-effort: delegate to GTK free function which calls _set_preview_widget
        try:
            from harite.gui.adapters.gtk_runtime_sync import sync_result_preview_from_owner
            sync_result_preview_from_owner(self, owner)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # State sync methods (delegate to framework-neutral free functions)
    # ------------------------------------------------------------------

    def _sync_slideshow_state_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_sync import sync_slideshow_state_from_owner
        sync_slideshow_state_from_owner(self, owner)

    def _sync_main_state_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_sync import sync_main_state_from_owner
        sync_main_state_from_owner(self, owner)

    def _sync_input_state_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_sync import sync_input_state_from_owner
        sync_input_state_from_owner(self, owner)

    def _sync_margins_state_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_sync import sync_margins_state_from_owner
        sync_margins_state_from_owner(self, owner)

    def _refresh_margins_controls(self, owner: Any | None = None) -> None:
        from harite.gui.adapters.gtk_runtime_sync import refresh_margins_controls
        refresh_margins_controls(self, owner)

    def _sync_feedback_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_sync import sync_feedback_from_owner
        sync_feedback_from_owner(self, owner)

    def _sync_non_preview_state_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_owner_sync import sync_non_preview_state_from_owner
        sync_non_preview_state_from_owner(self, owner)

    def _sync_preview_state_from_owner(
        self,
        owner: Any,
        *,
        include_input: bool = False,
        include_feedback: bool = False,
    ) -> None:
        from harite.gui.adapters.gtk_runtime_owner_sync import sync_preview_state_from_owner
        sync_preview_state_from_owner(
            self, owner, include_input=include_input, include_feedback=include_feedback
        )

    def _sync_input_preview_state_from_owner(
        self, owner: Any, *, include_feedback: bool = False
    ) -> None:
        from harite.gui.adapters.gtk_runtime_owner_sync import sync_input_preview_state_from_owner
        sync_input_preview_state_from_owner(self, owner, include_feedback=include_feedback)

    def _sync_margins_state_with_feedback_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_owner_sync import (
            sync_margins_state_with_feedback_from_owner,
        )
        sync_margins_state_with_feedback_from_owner(self, owner)

    def _sync_slideshow_state_with_feedback_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_owner_sync import (
            sync_slideshow_state_with_feedback_from_owner,
        )
        sync_slideshow_state_with_feedback_from_owner(self, owner)

    def _sync_slideshow_state_only_from_owner(self, owner: Any) -> None:
        from harite.gui.adapters.gtk_runtime_owner_sync import sync_slideshow_state_only_from_owner
        sync_slideshow_state_only_from_owner(self, owner)

    # ------------------------------------------------------------------
    # Settings dialog helpers (delegate to framework-neutral free functions)
    # ------------------------------------------------------------------

    def _set_settings_two_screen_mode(self, value: object) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import set_settings_two_screen_mode
        set_settings_two_screen_mode(self, value)

    def _read_settings_two_screen_mode(self) -> str | bool:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import read_settings_two_screen_mode
        return read_settings_two_screen_mode(self)

    def _set_settings_apply_mode(self, value: object | None) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import set_settings_apply_mode
        set_settings_apply_mode(self, value)

    def _read_settings_apply_mode(self) -> str:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import read_settings_apply_mode
        return read_settings_apply_mode(self)

    def _sync_settings_widgets_from_dialog(self) -> dict[str, object]:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import sync_settings_widgets_from_dialog
        return sync_settings_widgets_from_dialog(self)

    def _sync_settings_dialog_from_widgets(self) -> dict[str, object]:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import sync_settings_dialog_from_widgets
        return sync_settings_dialog_from_widgets(self)

    def _refresh_settings_dialog_from_getter(self) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import refresh_settings_dialog_from_getter
        refresh_settings_dialog_from_getter(self)

    def _refresh_color_dialog_from_getter(self) -> str:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import refresh_color_dialog_from_getter
        return refresh_color_dialog_from_getter(self)

    def _refresh_about_dialog_from_getter(self) -> dict[str, object]:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import refresh_about_dialog_from_getter
        return refresh_about_dialog_from_getter(self)

    def _store_background_color_in_settings_dialog(self, color: str) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import (
            store_background_color_in_settings_dialog,
        )
        store_background_color_in_settings_dialog(self, color)

    def _set_save_path_dialog_open_state(
        self, opened: bool, *, state_text: str | None = None
    ) -> None:
        pass  # Qt: no state machine needed (QFileDialog is a single call)

    # ------------------------------------------------------------------
    # Direction toggle helpers
    # ------------------------------------------------------------------

    def _opposite_toggle_name(self, object_name: str) -> str | None:
        pairs = {
            "tglPushLeftL": "tglPushRightL",
            "tglPushRightL": "tglPushLeftL",
            "tglPushLeftR": "tglPushRightR",
            "tglPushRightR": "tglPushLeftR",
            "tglUpperL": "tglLowerL",
            "tglLowerL": "tglUpperL",
            "tglUpperR": "tglLowerR",
            "tglLowerR": "tglUpperR",
        }
        return pairs.get(object_name)

    def _current_side_state(self, side: str) -> tuple[str, str]:
        """Return (align, valign) for the given side based on toggle states."""
        sfx = side.upper()
        align = (
            "left" if self._is_toggle_active(f"tglPushLeft{sfx}")
            else "right" if self._is_toggle_active(f"tglPushRight{sfx}")
            else "center"
        )
        valign = (
            "top" if self._is_toggle_active(f"tglUpper{sfx}")
            else "bottom" if self._is_toggle_active(f"tglLower{sfx}")
            else "center"
        )
        return align, valign

    def _sanitize_margin_text(self, value: str) -> str:
        try:
            from harite.gui.adapters.gtk_runtime_margin_text import sanitize_margin_text
            return sanitize_margin_text(value)
        except Exception:
            return value

    # ------------------------------------------------------------------
    # Slideshow timer
    # ------------------------------------------------------------------

    def _start_slideshow_timer(self, interval_seconds: int) -> bool:
        try:
            from PyQt6.QtCore import QTimer

            self._stop_slideshow_timer()
            timer = QTimer()
            timer.setInterval(max(1, interval_seconds) * 1000)
            timer.timeout.connect(self._on_slideshow_timer_event)
            timer.start()
            self._slideshow_timer = timer
            return True
        except Exception:
            return False

    def _stop_slideshow_timer(self) -> None:
        if self._slideshow_timer is not None:
            self._slideshow_timer.stop()
            self._slideshow_timer = None

    def _on_slideshow_timer_event(self) -> None:
        callback = self._signal_handlers.get("on_slideshow_tick")
        if callback is None:
            return
        try:
            result = callback()
            if result is False:
                self._stop_slideshow_timer()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Event handlers: direction toggles
    # ------------------------------------------------------------------

    def _on_direction_pressed(self, object_name: str) -> None:
        opposite_name = self._opposite_toggle_name(object_name)
        if opposite_name is not None:
            opposite = self._objects.get(opposite_name)
            if opposite is not None and hasattr(opposite, "isChecked") and opposite.isChecked():
                self._set_toggle_active(opposite_name, False)
                reset_cb = self._signal_handlers.get("on_toggle_position_reset")
                if reset_cb is not None:
                    try:
                        reset_cb(opposite_name)
                    except Exception as exc:
                        self._set_feedback(phase="Position", state="error", error=str(exc))
                        return
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_toggle_position_pressed")
        if callback is not None:
            try:
                callback(object_name)
            except Exception as exc:
                self._set_feedback(phase="Position", state="error", error=str(exc))

    def _on_direction_toggled(self, object_name: str) -> None:
        self._refresh_current_state_labels()
        callback = self._signal_handlers.get("on_toggle_position")
        if callback is not None:
            try:
                callback(object_name)
                owner = self._get_handler_owner("on_toggle_position")
                if owner is not None:
                    self._sync_non_preview_state_from_owner(owner)
            except Exception as exc:
                self._set_feedback(phase="Position", state="error", error=str(exc))

    def _on_direction_released(self, object_name: str) -> None:
        pass

    # ------------------------------------------------------------------
    # Event handlers: margin spin
    # ------------------------------------------------------------------

    def _on_margin_changed(self, _widget: Any) -> None:
        callback = self._signal_handlers.get("on_change_margins")
        if callback is None:
            self._refresh_current_state_labels()
            return
        try:
            left = self._read_spin_int("spnLeftMargin")
            right = self._read_spin_int("spnRightMargin")
            top = self._read_spin_int("spnTopMargin")
            bottom = self._read_spin_int("spnBottomMargin")
            ok = callback(f"{left},{right},{top},{bottom}")
            owner = self._get_handler_owner("on_change_margins")
            if owner is not None:
                self._sync_main_state_from_owner(owner)
                self._sync_feedback_from_owner(owner)
                return
            if ok is False:
                self._set_feedback(phase="Margins", state="rejected")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="error", error=str(exc))
        self._refresh_current_state_labels()

    # ------------------------------------------------------------------
    # Event handlers: input image
    # ------------------------------------------------------------------

    def _on_pick_input_clicked(self, side: str) -> None:
        proxy = self._objects.get("ImgOpenDialog")
        if proxy is None:
            self._set_feedback(phase="Input", state="dialog-unavailable")
            return
        callback = self._signal_handlers.get("on_pick_input")
        if callback is None:
            self._set_feedback(phase="Input", state="planned")
            return

        def _confirmed(path: str) -> None:
            try:
                ok = callback(side, path)
                owner = self._get_handler_owner("on_pick_input")
                if owner is not None:
                    self._sync_input_preview_state_from_owner(owner)
                    self._sync_feedback_from_owner(owner)
                    return
                if ok is False:
                    self._set_feedback(phase="Input", state="rejected")
                else:
                    self._set_feedback(phase="Input", state="updated")
            except Exception as exc:
                self._set_feedback(phase="Input", state="error", error=str(exc))

        try:
            proxy.open(callback=_confirmed)
        except Exception as exc:
            self._set_feedback(phase="Input", state="error", error=str(exc))

    def _on_clear_input_clicked(self, side: str) -> None:
        callback = self._signal_handlers.get("on_clear_input")
        if callback is None:
            self._set_feedback(phase="Input", state="planned")
            return
        try:
            ok = callback(side)
            owner = self._get_handler_owner("on_clear_input")
            if owner is not None:
                self._sync_input_state_from_owner(owner)
                self._sync_feedback_from_owner(owner)
                return
            if ok is False:
                self._set_feedback(phase="Input", state="clear-rejected")
            else:
                self._set_feedback(phase="Input", state="cleared")
        except Exception as exc:
            self._set_feedback(phase="Input", state="error", error=str(exc))

    # ------------------------------------------------------------------
    # Event handlers: optimize / apply / save
    # ------------------------------------------------------------------

    def _on_save_clicked(self, *_args: Any) -> None:
        """Export image: open save-path dialog then call on_save_as."""
        proxy = self._objects.get("SavePathDialog")
        if proxy is None:
            self._set_feedback(phase="Export", state="dialog-unavailable")
            return
        callback = self._signal_handlers.get("on_save_as")
        if callback is None:
            self._set_feedback(phase="Export", state="planned")
            return

        def _confirmed(path: str) -> None:
            try:
                ok = callback(path)
                owner = self._get_handler_owner("on_save_as")
                if owner is not None:
                    self._sync_feedback_from_owner(owner)
                    return
                if ok is False:
                    self._set_feedback(phase="Export", state="failed")
                else:
                    self._set_feedback(phase="Export", state="saved")
            except Exception as exc:
                self._set_feedback(phase="Export", state="error", error=str(exc))

        try:
            proxy.open(callback=_confirmed)
        except Exception as exc:
            self._set_feedback(phase="Export", state="error", error=str(exc))

    def _on_optimize_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_optimize")
        if callback is None:
            self._set_feedback(phase="Optimize", state="planned")
            return
        try:
            ok = callback()
            owner = self._get_handler_owner("on_optimize")
            if owner is not None:
                self._sync_non_preview_state_from_owner(owner)
                return
            if ok is False:
                self._set_feedback(phase="Optimize", state="failed")
            else:
                self._set_feedback(phase="Optimize", state="done")
        except Exception as exc:
            self._set_feedback(phase="Optimize", state="error", error=str(exc))

    def _on_apply_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_apply")
        if callback is None:
            self._set_feedback(phase="Apply", state="planned")
            return
        try:
            ok = callback()
            owner = self._get_handler_owner("on_apply")
            if owner is not None:
                self._sync_non_preview_state_from_owner(owner)
                return
            if ok is False:
                self._set_feedback(phase="Apply", state="failed")
            else:
                self._set_feedback(phase="Apply", state="done")
        except Exception as exc:
            self._set_feedback(phase="Apply", state="error", error=str(exc))

    def _on_apply_mode_toggled(self, widget: Any, mode: str) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_apply_mode_toggled
        on_settings_apply_mode_toggled(self, widget, mode)
        callback = self._signal_handlers.get("on_change_apply_mode")
        if callback is None:
            return
        try:
            ok = callback(mode)
            owner = self._get_handler_owner("on_change_apply_mode")
            if owner is not None:
                self._sync_non_preview_state_from_owner(owner)
                return
            if ok is False:
                self._set_feedback(phase="Apply", state="mode-rejected")
            else:
                self._set_feedback(phase="Apply", state="mode-updated")
        except Exception as exc:
            self._set_feedback(phase="Apply", state="mode-error", error=str(exc))

    # ------------------------------------------------------------------
    # Event handlers: settings dialog
    # ------------------------------------------------------------------

    def _on_settings_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_clicked
        on_settings_clicked(self)

    def _on_settings_apply_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_apply_clicked
        on_settings_apply_clicked(self)

    def _on_settings_save_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_save_clicked
        on_settings_save_clicked(self)

    def _on_settings_close_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_settings_close_clicked
        on_settings_close_clicked(self)

    # ------------------------------------------------------------------
    # Event handlers: color dialog
    # ------------------------------------------------------------------

    def _on_color_pick_clicked(self, *_args: Any) -> None:
        proxy = self._objects.get("ColorDialog")
        if proxy is not None and hasattr(proxy, "open_dialog"):
            proxy.open_dialog()

    def _on_color_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_clicked
        on_color_clicked(self)

    def _on_color_dialog_apply_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_dialog_apply_clicked
        on_color_dialog_apply_clicked(self)

    def _on_color_dialog_cancel_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_dialog_cancel_clicked
        on_color_dialog_cancel_clicked(self)

    def _on_color_dialog_confirmed(self, color: str) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_dialog_confirmed
        on_color_dialog_confirmed(self, color)

    def _on_color_dialog_canceled(self, destroyed: bool = False) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_color_dialog_canceled
        on_color_dialog_canceled(self, destroyed)

    # ------------------------------------------------------------------
    # Event handlers: about dialog
    # ------------------------------------------------------------------

    def _on_about_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_about_clicked
        on_about_clicked(self)

    def _on_about_dialog_close_clicked(self, *_args: Any) -> None:
        from harite.gui.adapters.gtk_runtime_settings_dialogs import on_about_dialog_close_clicked
        on_about_dialog_close_clicked(self)

    # ------------------------------------------------------------------
    # Event handlers: slideshow
    # ------------------------------------------------------------------

    def _on_pick_srcdir_clicked(self, side: str) -> None:
        proxy = self._objects.get("SrcdirDialog")
        if proxy is None:
            self._set_feedback(phase="Slideshow", state="dialog-unavailable")
            return
        callback = self._signal_handlers.get("on_pick_slideshow_srcdir")
        if callback is None:
            self._set_feedback(phase="Slideshow", state="planned")
            return

        def _confirmed(path: str) -> None:
            try:
                ok = callback(side, path)
                owner = self._get_handler_owner("on_pick_slideshow_srcdir")
                if owner is not None:
                    self._sync_slideshow_state_with_feedback_from_owner(owner)
                    return
                if ok is False:
                    self._set_feedback(phase="Slideshow", state="srcdir-rejected")
                else:
                    self._set_feedback(phase="Slideshow", state="srcdir-updated")
            except Exception as exc:
                self._set_feedback(phase="Slideshow", state="error", error=str(exc))

        try:
            proxy.open(callback=_confirmed)
        except Exception as exc:
            self._set_feedback(phase="Slideshow", state="error", error=str(exc))

    def _on_slideshow_interval_changed(self, _widget: Any) -> None:
        callback = self._signal_handlers.get("on_slideshow_interval_change")
        if callback is None:
            return
        try:
            value = self._read_spin_int("spnInterval")
            ok = callback(value)
            owner = self._get_handler_owner("on_slideshow_interval_change")
            if owner is not None:
                self._sync_slideshow_state_only_from_owner(owner)
        except Exception as exc:
            self._set_feedback(phase="Slideshow", state="interval-error", error=str(exc))

    def _on_slideshow_start_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_slideshow_start")
        if callback is None:
            self._set_feedback(phase="Slideshow", state="planned")
            return
        try:
            interval = self._read_spin_int("spnInterval")
            ok = callback()
            owner = self._get_handler_owner("on_slideshow_start")
            if owner is not None:
                self._sync_slideshow_state_with_feedback_from_owner(owner)
                return
            if ok is not False:
                self._slideshow_running = True
                self._start_slideshow_timer(interval)
                self._set_feedback(phase="Slideshow", state="started")
            else:
                self._set_feedback(phase="Slideshow", state="start-failed")
        except Exception as exc:
            self._set_feedback(phase="Slideshow", state="error", error=str(exc))

    def _on_slideshow_stop_clicked(self, *_args: Any) -> None:
        callback = self._signal_handlers.get("on_slideshow_stop")
        self._stop_slideshow_timer()
        if callback is None:
            self._slideshow_running = False
            self._set_feedback(phase="Slideshow", state="planned")
            return
        try:
            ok = callback()
            owner = self._get_handler_owner("on_slideshow_stop")
            if owner is not None:
                self._sync_slideshow_state_with_feedback_from_owner(owner)
                return
            self._slideshow_running = False
            self._set_feedback(phase="Slideshow", state="stopped")
        except Exception as exc:
            self._set_feedback(phase="Slideshow", state="error", error=str(exc))

    def _on_slideshow_mode_toggled(self, widget: Any, mode: str) -> None:
        callback = self._signal_handlers.get("on_change_slideshow_mode")
        if callback is None:
            return
        try:
            ok = callback(mode)
            owner = self._get_handler_owner("on_change_slideshow_mode")
            if owner is not None:
                self._sync_slideshow_state_only_from_owner(owner)
        except Exception as exc:
            self._set_feedback(phase="Slideshow", state="mode-error", error=str(exc))

    # ------------------------------------------------------------------
    # Event handlers: margin text
    # ------------------------------------------------------------------

    def _on_margin_text_mode_toggled(self, widget: Any, value: str) -> None:
        callback = self._signal_handlers.get("on_change_margin_text_mode")
        if callback is None:
            self._set_feedback(phase="Margins", state="planned")
            return
        try:
            ok = callback(value)
            if ok is False:
                self._set_feedback(phase="Margins", state="info-rejected")
                return
            owner = self._get_handler_owner("on_change_margin_text_mode")
            if owner is not None:
                self._sync_margins_state_with_feedback_from_owner(owner)
                return
            self._set_feedback(phase="Margins", state="info-updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="info-error", error=str(exc))

    def _on_margin_text_changed(self, entry: Any) -> None:
        callback = self._signal_handlers.get("on_change_margin_text")
        if callback is None:
            return
        try:
            if hasattr(entry, "toPlainText"):
                value = entry.toPlainText()
            elif hasattr(entry, "text"):
                value = entry.text()
            else:
                value = ""
            value = self._sanitize_margin_text(value)
            ok = callback(value)
            if ok is False:
                self._set_feedback(phase="Margins", state="text-rejected")
                return
            owner = self._get_handler_owner("on_change_margin_text")
            if owner is not None:
                self._sync_margins_state_with_feedback_from_owner(owner)
                return
            self._set_feedback(phase="Margins", state="text-updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="text-error", error=str(exc))

    def _on_margin_position_toggled(self, widget: Any, value: str) -> None:
        callback = self._signal_handlers.get("on_change_margin_text_position")
        if callback is None:
            return
        try:
            ok = callback(value)
            if ok is False:
                self._set_feedback(phase="Margins", state="position-rejected")
                return
            owner = self._get_handler_owner("on_change_margin_text_position")
            if owner is not None:
                self._sync_margins_state_with_feedback_from_owner(owner)
                return
            self._set_feedback(phase="Margins", state="position-updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="position-error", error=str(exc))

    def _on_margin_text_max_lines_changed(self, _spin: Any) -> None:
        callback = self._signal_handlers.get("on_change_margin_text_max_lines")
        if callback is None:
            return
        try:
            value = self._read_spin_int("spnMarginTextMaxLines")
            ok = callback(value)
            if ok is False:
                self._set_feedback(phase="Margins", state="max-lines-rejected")
                return
            owner = self._get_handler_owner("on_change_margin_text_max_lines")
            if owner is not None:
                self._sync_margins_state_with_feedback_from_owner(owner)
                return
            self._set_feedback(phase="Margins", state="max-lines-updated")
        except Exception as exc:
            self._set_feedback(phase="Margins", state="max-lines-error", error=str(exc))

    def _on_margin_text_key_press(self, widget: Any, event: Any) -> bool:
        return False  # Qt: key-press-event not needed; textChanged suffices

    # ------------------------------------------------------------------
    # Stub compatibility: GTK "idle_add" style
    # ------------------------------------------------------------------

    def run_slideshow_cycle_once(self) -> bool:
        """Compatibility stub; real implementation wired in Phase 9+."""
        return False


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def _make_window_icon(qwindow: Any) -> None:
    try:
        from PyQt6.QtGui import QIcon
        from PyQt6.QtSvgWidgets import QSvgWidget  # noqa: F401

        from harite.gui.resource_access import gui_resource_path

        with gui_resource_path("icons", "product", "harite_app.svg") as icon_path:
            qwindow.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        pass


def load_qt_runtime_signal_backend() -> QtSignalBackend:
    """Create QApplication + QMainWindow, build layout, return QtSignalBackend.

    Raises RuntimeError if PyQt6 is not installed.
    """
    try:
        import sys

        from PyQt6.QtWidgets import QApplication, QMainWindow
    except ImportError as exc:
        raise RuntimeError(
            "Harite Qt backend requires PyQt6. "
            "Install it with: pip install 'harite[gui-qt]'"
        ) from exc

    from harite.gui.adapters_qt.qt_stylesheet import apply_qt_stylesheet

    qapp = QApplication.instance() or QApplication(sys.argv)
    apply_qt_stylesheet(qapp)

    qwindow = QMainWindow()
    qwindow.setWindowTitle(_WINDOW_TITLE)
    qwindow.resize(_WINDOW_WIDTH, _WINDOW_HEIGHT)
    _make_window_icon(qwindow)

    backend = QtSignalBackend(qapp, qwindow)
    backend.build_layout()
    return backend

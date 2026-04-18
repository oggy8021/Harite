"""GUI view placeholder.

This file intentionally avoids hard dependency on GTK/PyGObject so the core
package remains importable in environments without GUI libraries.
"""

from __future__ import annotations

from pathlib import Path
import sys

from harite.gui.controllers.optimize_controller import OptimizeController, OptimizeFormState
from harite.gui.services.cli_mapper import OptimizeRequest, to_cli_args
from harite.plugins import registry as plugin_registry
from harite.watch import collect_watch_input_images, select_next_image


class MainWindow:
    """Framework-neutral placeholder for the first standalone GUI window."""

    def __init__(self) -> None:
        self.title = "Harite"
        self.subtitle = "Compose -> Optimize -> Apply"
        self.controller = OptimizeController()
        self.closed = False
        self.can_optimize = False
        self.can_apply = False
        self.last_error = ""
        self.status_level = "idle"
        self.status_phase = "init"
        self.status_message = "ready"
        self.logs: list[str] = []
        self.available_plugins = tuple(plugin_registry.list())
        self.plugin_name = self._default_plugin_name()
        self.last_saved_files: list[Path] = []
        self.save_target_display = "Save target: not-selected"
        self.watch_interval_seconds = 60
        self.watch_srcdir_l = ""
        self.watch_srcdir_r = ""
        self.watch_summary_display = "Watch: stopped"
        self.watch_source_display = "Watch srcdirs: L=- | R=-"
        self.watch_current_display = "Watch current: idle"
        self.watch_running = False
        self._watch_index_l = 0
        self._watch_index_r = 0
        self._watch_previous_l: Path | None = None
        self._watch_previous_r: Path | None = None
        self.open_image_dialog_open = False
        self.open_image_dialog_side: str | None = None
        self._save_path_dialog_open = False
        self.input_path_l = ""
        self.input_path_r = ""
        self.form_state = OptimizeFormState(
            input_value="",
            resolution="1920x1080",
            output_dir=str(Path(".")),
        )
        self.layout_version = "phase6-layout-redefinition"
        self.layout_sections: tuple[tuple[str, tuple[str, ...]], ...] = (
            ("title_menu_flow", ("title", "menu", "flow", "save_as")),
            ("compose_input", ("input_value", "margins", "cross_layout", "fixed", "align", "valign")),
            ("action_cluster", ("optimize", "apply", "saved_files")),
            ("watch_tab", ("watch_summary", "watch_srcdirs", "watch_interval", "watch_controls", "watch_details")),
            ("status_footer", ("status_message", "watch_summary")),
            ("debug_footer", ("save_target", "last_error", "logs", "current_state")),
        )
        self.primary_action_flow: tuple[str, ...] = (
            "save_as",
            "optimize",
            "apply",
        )

    @property
    def save_path_dialog_open(self) -> bool:
        return self._save_path_dialog_open

    @save_path_dialog_open.setter
    def save_path_dialog_open(self, opened: bool) -> None:
        self._save_path_dialog_open = bool(opened)

    def _default_plugin_name(self) -> str:
        platform_map = {
            "win32": "windows",
            "darwin": "macos",
        }
        preferred = platform_map.get(sys.platform, "linux")
        if preferred in self.available_plugins:
            return preferred
        if self.available_plugins:
            return self.available_plugins[0]
        return "windows"

    def on_change_plugin(self, plugin_name: str) -> bool:
        name = (plugin_name or "").strip().lower()
        if not name:
            self.last_error = "plugin is required"
            self._log("Plugin update failed: empty value")
            return False
        if name not in self.available_plugins:
            self.last_error = f"unknown plugin: {name}"
            self._log(f"Plugin update failed: unknown plugin {name}")
            return False

        self.plugin_name = name
        self.last_error = ""
        self._log(f"Plugin updated: {name}")
        return True

    def on_pick_input(self, path: str, side: str | None = None) -> None:
        value = (path or "").strip()
        if not value:
            self.last_error = "input path is empty"
            self._log("Pick input ignored: empty path")
            return

        normalized_side = (side or "").strip().upper()
        if normalized_side == "L":
            self.input_path_l = value
        elif normalized_side == "R":
            self.input_path_r = value
        else:
            current = [p.strip() for p in self.form_state.input_value.split(",") if p.strip()]
            if value not in current:
                current.append(value)
            self.input_path_l = current[0] if len(current) >= 1 else ""
            self.input_path_r = current[1] if len(current) >= 2 else ""

        combined = ",".join(path for path in (self.input_path_l, self.input_path_r) if path)
        self.on_change_input_text(combined)
        if normalized_side in {"L", "R"}:
            self._log(f"Input picked ({normalized_side}): {value}")
        else:
            self._log(f"Input picked: {value}")

    def on_pick_watch_srcdir(self, path: str, side: str | None = None) -> bool:
        value = (path or "").strip()
        normalized_side = (side or "").strip().upper()
        if not value:
            self.last_error = "watch srcdir is empty"
            self._log("Watch srcdir ignored: empty path")
            return False
        if normalized_side == "L":
            self.watch_srcdir_l = value
        elif normalized_side == "R":
            self.watch_srcdir_r = value
        else:
            self.last_error = "watch srcdir side is required"
            self._log("Watch srcdir ignored: missing side")
            return False
        self._update_watch_source_display()
        self._set_status("idle", "watch", f"watch srcdir {normalized_side} selected")
        self._log(f"Watch srcdir selected ({normalized_side}): {value}")
        return True

    def _current_margin_values(self) -> tuple[int, int, int, int]:
        value = (self.form_state.margins or "").strip()
        if not value:
            return (0, 0, 0, 0)

        parts = [part.strip() for part in value.split(",")]
        if len(parts) != 4:
            return (0, 0, 0, 0)

        try:
            return tuple(int(part) for part in parts)
        except ValueError:
            return (0, 0, 0, 0)

    def _margin_index_for_widget(self, widget_name: str) -> int | None:
        if "LMergin" in widget_name:
            return 0
        if "RMergin" in widget_name:
            return 1
        if "TopMergin" in widget_name:
            return 2
        if "BtmMergin" in widget_name:
            return 3
        return None

    def on_change_margins(self, *args: int | str) -> None:
        if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], (int, float)):
            margin_index = self._margin_index_for_widget(args[0])
            if margin_index is None:
                self.last_error = f"unknown margin widget: {args[0]}"
                self._log(f"Margin update failed: unknown widget {args[0]}")
                return

            current = list(self._current_margin_values())
            current[margin_index] = int(args[1])
            self.on_change_margins(*current)
            return

        if len(args) != 4 or not all(isinstance(value, (int, float)) for value in args):
            self.last_error = "invalid margin signal"
            self._log("Margin update failed: invalid signal")
            return

        left, right, top, bottom = (int(args[0]), int(args[1]), int(args[2]), int(args[3]))
        vals = (left, right, top, bottom)
        if any(v < 0 for v in vals):
            self.last_error = "margins must be non-negative"
            self._log("Margin update failed: negative value")
            return

        self.form_state.margins = f"{left},{right},{top},{bottom}"
        self.last_error = ""
        self._log(f"Margins updated: {self.form_state.margins}")

    def on_toggle_fixed(self, enabled: bool) -> None:
        self.form_state.fixed = bool(enabled)
        self._log(f"Fixed mode: {self.form_state.fixed}")

    def on_toggle_position_pressed(self, widget_name: str) -> None:
        self._log(f"Toggle pressed: {widget_name}")

    def on_toggle_position(self, widget_name: str, active: bool) -> None:
        if not active:
            return

        if "PushLeft" in widget_name:
            self.form_state.align = "left"
            self._log(f"Align updated from {widget_name}: left")
            return
        if "PushRight" in widget_name:
            self.form_state.align = "right"
            self._log(f"Align updated from {widget_name}: right")
            return
        if "Upper" in widget_name:
            self.form_state.valign = "top"
            self._log(f"Valign updated from {widget_name}: top")
            return
        if "Lower" in widget_name:
            self.form_state.valign = "bottom"
            self._log(f"Valign updated from {widget_name}: bottom")

    def on_toggle_position_reset(self, widget_name: str) -> None:
        if "Push" in widget_name:
            self.form_state.align = "center"
            self._log(f"Align reset from {widget_name}: center")
            return
        if "Upper" in widget_name or "Lower" in widget_name:
            self.form_state.valign = "center"
            self._log(f"Valign reset from {widget_name}: center")

    def _log(self, message: str) -> None:
        self.logs.append(message)

    def _update_save_target_display(self, save_path: str | None = None) -> None:
        value = (save_path or self.form_state.save_path or "").strip()
        if value:
            self.save_target_display = f"Save target: {value}"
            return
        self.save_target_display = "Save target: not-selected"

    def _update_watch_source_display(self) -> None:
        left = self.watch_srcdir_l or "-"
        right = self.watch_srcdir_r or "-"
        self.watch_source_display = f"Watch srcdirs: L={left} | R={right}"

    def _update_watch_summary_display(self) -> None:
        self.watch_summary_display = "Watch: running" if self.watch_running else "Watch: stopped"

    def _update_watch_current_display(self, left: str | None = None, right: str | None = None) -> None:
        current_left = left if left is not None else (str(self._watch_previous_l) if self._watch_previous_l else "-")
        current_right = right if right is not None else (str(self._watch_previous_r) if self._watch_previous_r else "-")
        if not self.watch_running and current_left == "-" and current_right == "-":
            self.watch_current_display = "Watch current: idle"
            return
        self.watch_current_display = f"Watch current: L={current_left} | R={current_right}"

    def _set_status(self, level: str, phase: str, message: str, *, error: str = "") -> None:
        """Set unified UI status fields and keep last_error in sync."""
        self.status_level = level
        self.status_phase = phase
        self.status_message = message
        self.last_error = error

    def on_change_input_text(self, text: str) -> None:
        normalized = text.strip()
        parts = [part.strip() for part in normalized.split(",") if part.strip()]
        self.input_path_l = parts[0] if len(parts) >= 1 else ""
        self.input_path_r = parts[1] if len(parts) >= 2 else ""
        self.form_state.input_value = ",".join(parts)
        self.can_optimize = bool(text and text.strip())
        if not self.can_optimize:
            # Input changed to empty; reset apply readiness to avoid stale flow.
            self.can_apply = False
            self.last_saved_files = []
            self.input_path_l = ""
            self.input_path_r = ""
            self.save_path_dialog_open = False
            self._set_status("error", "input", "input is required", error="input is required")
            self._log("Save path dialog closed by input reset")
        if self.can_optimize:
            self._set_status("idle", "input", "input ready")
            self._log("Input updated")
        else:
            self._log("Input is empty")

    def on_save(self) -> bool:
        self.save_path_dialog_open = True
        self._update_save_target_display()
        self._set_status("idle", "save_path", "save path dialog opened")
        self._log("Save path dialog opened")
        return True

    def on_optimize(self) -> bool:
        if not self.can_optimize:
            self._set_status("error", "optimize", "input is required", error="input is required")
            self._log("Optimize blocked: input is required")
            return False

        self._set_status("running", "optimize", "optimizing")

        try:
            saved, _placements = self.controller.run_optimize(self.form_state)
            self.last_saved_files = list(saved)
            self.can_apply = bool(self.last_saved_files)
            self._set_status("success", "optimize", "optimize completed")
            self._log(f"Saved {len(saved)} file(s)")
            for path in saved:
                self._log(f"Saved: {path}")
            if self.can_apply:
                self._log("Next action: apply")
            return True
        except Exception as exc:
            self.can_apply = False
            self._set_status("error", "optimize", "optimize failed", error=str(exc))
            self._log(f"Optimize failed: {exc}")
            return False

    def _apply_latest(self) -> bool:
        if not self.last_saved_files:
            self._set_status("error", "apply", "no optimized file to apply", error="no optimized file to apply")
            self._log("Apply blocked: no optimized file")
            return False

        self._set_status("running", "apply", "applying wallpaper")

        target = str(self.last_saved_files[-1])
        try:
            plugin = plugin_registry.get(self.plugin_name)
        except KeyError:
            self._set_status(
                "error",
                "apply",
                "unknown plugin",
                error=f"unknown plugin: {self.plugin_name}",
            )
            self._log(f"Apply failed: unknown plugin {self.plugin_name}")
            return False

        try:
            ok = bool(plugin.apply(target, dry_run=False))
        except Exception as exc:
            self._set_status("error", "apply", "apply failed", error=f"failed to apply wallpaper: {exc}")
            self._log(f"Apply failed via plugin={self.plugin_name}: {exc}")
            return False

        if ok:
            self._set_status("success", "apply", "apply completed")
            self._log(f"Applied wallpaper via plugin={self.plugin_name}: {target}")
            return True

        self._set_status("error", "apply", "apply failed", error="failed to apply wallpaper")
        self._log(f"Apply failed via plugin={self.plugin_name}: {target}")
        return False

    def on_apply(self) -> bool:
        return self._apply_latest()

    def on_clear_input(self) -> bool:
        self.input_path_l = ""
        self.input_path_r = ""
        self.on_change_input_text("")
        self._log("Input cleared")
        return True

    def on_about(self) -> bool:
        self._set_status("planned", "about", "about dialog is planned")
        self._log("About requested: planned")
        return False

    def on_set_color(self) -> bool:
        self._set_status("deferred", "color", "color picker is deferred to phase7")
        self._log("Color picker requested: deferred to phase7")
        return False

    def on_save_path_selected(self, save_path: str | None = None) -> bool:
        value = (save_path or "").strip()
        if not self.save_path_dialog_open and not value:
            self._set_status("idle", "save_path", "save path ignored (closed)")
            self._log("Save path selection ignored: dialog is closed")
            return False
        if not value:
            value = (self.form_state.save_path or "").strip()
        if value:
            self.form_state.save_path = value
            self._update_save_target_display(value)
            self.save_path_dialog_open = False
            self._log(f"Save path selected: {value}")
            if not self.can_optimize:
                self._set_status("error", "save", "input is required", error="input is required")
                self._log("Save As blocked: input is required")
                return False

            self._set_status("running", "save", "saving composite")
            try:
                saved, _placements = self.controller.run_export(self.form_state, value)
            except Exception as exc:
                self._set_status("error", "save", "save failed", error=str(exc))
                self._log(f"Save As failed: {exc}")
                return False

            self._set_status("success", "save", "save completed")
            self._log(f"Save As completed: {saved[-1]}")
            return True
        self._set_status("error", "save_path", "save path is required", error="save path is required")
        self._log("Save path selection rejected: save path is required")
        return False

    def on_save_path_selection_canceled(self) -> bool:
        if not self.save_path_dialog_open:
            self._set_status("idle", "save_path", "save path cancel ignored (closed)")
            self._log("Save path cancel ignored: dialog is closed")
            return False
        self.save_path_dialog_open = False
        self._set_status("idle", "save_path", "save path canceled (path unchanged)")
        self._log("Save path canceled")
        return True

    def on_watch_start(self) -> bool:
        sources: list[tuple[str, Path]] = []
        if self.watch_srcdir_l.strip():
            sources.append(("L", Path(self.watch_srcdir_l.strip())))
        if self.watch_srcdir_r.strip():
            sources.append(("R", Path(self.watch_srcdir_r.strip())))
        if not sources:
            self._set_status("error", "watch", "watch srcdir is required", error="watch srcdir is required")
            self._log("Watch start blocked: watch srcdir is required")
            return False

        selected_left = "-"
        selected_right = "-"
        for side, source_dir in sources:
            try:
                images = collect_watch_input_images(source_dir)
            except ValueError as exc:
                self._set_status("error", "watch", f"watch srcdir {side} invalid", error=str(exc))
                self._log(f"Watch start failed ({side}): {exc}")
                return False

            if side == "L":
                selected, self._watch_index_l = select_next_image(
                    images,
                    "sequential",
                    self._watch_index_l,
                    previous_selected=self._watch_previous_l,
                )
                self._watch_previous_l = selected
                selected_left = str(selected)
            else:
                selected, self._watch_index_r = select_next_image(
                    images,
                    "sequential",
                    self._watch_index_r,
                    previous_selected=self._watch_previous_r,
                )
                self._watch_previous_r = selected
                selected_right = str(selected)

        self.watch_running = True
        self._update_watch_summary_display()
        self._update_watch_source_display()
        self._update_watch_current_display(selected_left, selected_right)
        self._set_status("success", "watch", "watch started")
        self._log(
            f"Watch started: interval={self.watch_interval_seconds}s L={selected_left} R={selected_right}"
        )
        return True

    def on_watch_stop(self) -> bool:
        if not self.watch_running:
            self._set_status("idle", "watch", "watch stop ignored (idle)")
            self._log("Watch stop ignored: watch is idle")
            return False
        self.watch_running = False
        self._update_watch_summary_display()
        self._update_watch_current_display()
        self._set_status("idle", "watch", "watch stopped")
        self._log("Watch stopped")
        return True

    def on_watch_interval_change(self, seconds: int) -> bool:
        value = int(seconds)
        if value <= 0:
            self._set_status("error", "watch", "watch interval must be positive", error="watch interval must be positive")
            self._log(f"Watch interval rejected: {value}")
            return False
        self.watch_interval_seconds = value
        self._set_status("idle", "watch", f"watch interval updated: {value}s")
        self._log(f"Watch interval updated: {value}s")
        return True

    def on_close(self) -> None:
        self.closed = True
        self._log("Window closed")

    def on_close_error_dialog(self) -> None:
        self.last_error = ""
        self._log("Error dialog closed")

    def on_close_open_image_dialog(self) -> None:
        self.open_image_dialog_open = False
        self.open_image_dialog_side = None
        self._log("Open image dialog closed")

    def on_close_save_path_dialog(self) -> None:
        self._update_save_target_display()
        self._log("Save path dialog closed")

    def on_close_settings_dialog(self) -> None:
        self._log("Settings dialog closed")

    def on_close_color_dialog(self) -> None:
        self._log("Color selection dialog closed")

    def on_close_srcdir_dialog(self) -> None:
        self._log("Source directory dialog closed")

    def build_optimize_cli_preview(self) -> str:
        req = OptimizeRequest(
            input_value=self.form_state.input_value,
            resolution=self.form_state.resolution,
            output_dir=Path(self.form_state.output_dir),
            layout=self.form_state.layout,
            scaling=self.form_state.scaling,
            two_screen=self.form_state.two_screen,
            margins=self.form_state.margins,
            l_display=self.form_state.l_display,
            r_display=self.form_state.r_display,
            fixed=self.form_state.fixed,
            align=self.form_state.align,
            valign=self.form_state.valign,
            padding=self.form_state.padding,
            quality=self.form_state.quality,
            embed_info=self.form_state.embed_info,
            embed_text=self.form_state.embed_text,
            embed_position=self.form_state.embed_position,
            embed_max_lines=self.form_state.embed_max_lines,
        )
        args = to_cli_args(req)
        preview = "harite " + " ".join(args)
        self._log(f"CLI preview: {preview}")
        return preview

    def suggest_next_action(self) -> str:
        """Return the recommended next operation in the Optimize/Apply flow."""
        if not self.can_optimize:
            return "input"
        if self.can_optimize and not self.can_apply:
            return "optimize"
        return "apply"

    def run_primary_flow_step(self) -> bool:
        """Execute one safe step of the primary flow.

        Order:
        - input missing -> no-op (False)
        - optimize ready -> optimize
        - apply ready -> apply
        """
        step = self.suggest_next_action()
        if step == "optimize":
            return self.on_optimize()
        if step == "apply":
            return self.on_apply()
        self._set_status("error", "flow", "input is required", error="input is required")
        self._log("Flow step blocked: input is required")
        return False

    def get_layout_blueprint(self) -> dict[str, object]:
        """Return UI grouping metadata used by layout checks and tests."""
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "layout_version": self.layout_version,
            "sections": self.layout_sections,
            "primary_action_flow": self.primary_action_flow,
            "layout_highlights": (
                "menu-bar-header",
                "flow-save-right",
                "center-cross-layout",
                "watch-tab-center-only",
                "actions-right-lower",
                "status-short-footer",
                "debug-bottom-band",
                "color-hidden-slot",
            ),
            "suggested_next_action": self.suggest_next_action(),
            "status": {
                "level": self.status_level,
                "phase": self.status_phase,
                "message": self.status_message,
                "last_error": self.last_error,
                "save_target": self.save_target_display,
                "watch_summary": self.watch_summary_display,
                "watch_sources": self.watch_source_display,
                "watch_current": self.watch_current_display,
            },
        }

    def show(self) -> None:
        print(self.title)
        print(self.subtitle)
        print("GUI skeleton is ready. Next step: bind real GTK widgets.")
        print(f"Can optimize: {self.can_optimize}")
        print(f"Status: {self.status_level}/{self.status_phase} - {self.status_message}")

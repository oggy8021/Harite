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


class MainWindow:
    """Framework-neutral placeholder for the first standalone GUI window."""

    def __init__(self) -> None:
        self.title = "Harite Studio"
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
        self.form_state = OptimizeFormState(
            input_value="",
            resolution="1920x1080",
            output_dir=str(Path(".")),
        )
        self.layout_version = "phase5-radical-mainwindow"
        # P5-2: move to a stronger hero + action-panel layout for clearer first glance.
        self.layout_sections: tuple[tuple[str, tuple[str, ...]], ...] = (
            ("hero", ("input_value", "resolution", "output_dir", "plugin")),
            ("optimize_panel", ("margins", "align", "valign", "padding", "quality", "optimize")),
            ("apply_panel", ("saved_files", "apply_dry_run", "apply_do_it")),
            ("status_panel", ("status_message", "last_error", "logs")),
        )
        self.primary_action_flow: tuple[str, ...] = (
            "hero",
            "optimize",
            "apply_dry_run",
            "apply_do_it",
        )

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

    def on_pick_input(self, path: str) -> None:
        """Legacy signal mapping: on_btnGetImg_clicked."""
        value = (path or "").strip()
        if not value:
            self.last_error = "input path is empty"
            self._log("Pick input ignored: empty path")
            return

        current = [p.strip() for p in self.form_state.input_value.split(",") if p.strip()]
        if value not in current:
            current.append(value)
        self.on_change_input_text(",".join(current))
        self._log(f"Input picked: {value}")

    def on_change_margins(self, left: int, right: int, top: int, bottom: int) -> None:
        """Legacy signal mapping: on_spnMergin_value_changed."""
        vals = (left, right, top, bottom)
        if any(v < 0 for v in vals):
            self.last_error = "margins must be non-negative"
            self._log("Margin update failed: negative value")
            return

        self.form_state.margins = f"{left},{right},{top},{bottom}"
        self.last_error = ""
        self._log(f"Margins updated: {self.form_state.margins}")

    def on_toggle_fixed(self, enabled: bool) -> None:
        """Legacy signal mapping: on_radFixed_toggled."""
        self.form_state.fixed = bool(enabled)
        self._log(f"Fixed mode: {self.form_state.fixed}")

    def _log(self, message: str) -> None:
        self.logs.append(message)

    def _set_status(self, level: str, phase: str, message: str, *, error: str = "") -> None:
        """Set unified UI status fields and keep legacy last_error in sync."""
        self.status_level = level
        self.status_phase = phase
        self.status_message = message
        self.last_error = error

    def on_change_input_text(self, text: str) -> None:
        """Legacy signal mapping: on_entPath_insert_text."""
        self.form_state.input_value = text
        self.can_optimize = bool(text and text.strip())
        if not self.can_optimize:
            # Input changed to empty; reset apply readiness to avoid stale flow.
            self.can_apply = False
            self.last_saved_files = []
            self._set_status("error", "input", "input is required", error="input is required")
        if self.can_optimize:
            self._set_status("idle", "input", "input ready")
            self._log("Input updated")
        else:
            self._log("Input is empty")

    def on_optimize(self) -> bool:
        """Legacy signal mapping: on_btnSave_clicked."""
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
                self._log("Next action: apply dry-run")
            return True
        except Exception as exc:
            self.can_apply = False
            self._set_status("error", "optimize", "optimize failed", error=str(exc))
            self._log(f"Optimize failed: {exc}")
            return False

    def _apply_latest(self, dry_run: bool) -> bool:
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
            ok = bool(plugin.apply(target, dry_run=dry_run))
        except Exception as exc:
            self._set_status("error", "apply", "apply failed", error=f"failed to apply wallpaper: {exc}")
            self._log(f"Apply failed via plugin={self.plugin_name} dry_run={dry_run}: {exc}")
            return False

        if ok:
            self._set_status("success", "apply", "apply completed")
            self._log(f"Applied wallpaper via plugin={self.plugin_name} dry_run={dry_run}: {target}")
            return True

        self._set_status("error", "apply", "apply failed", error="failed to apply wallpaper")
        self._log(f"Apply failed via plugin={self.plugin_name} dry_run={dry_run}: {target}")
        return False

    def on_apply_dry_run(self) -> bool:
        """Legacy signal mapping: on_btnSetWall_clicked (safe mode)."""
        return self._apply_latest(dry_run=True)

    def on_apply_do_it(self) -> bool:
        """Legacy signal mapping: on_btnSetWall_clicked (execute mode)."""
        return self._apply_latest(dry_run=False)

    def on_close(self) -> None:
        """Legacy signal mapping: on_WallPosit_MainWindow_delete_event."""
        self.closed = True
        self._log("Window closed")

    def on_close_error_dialog(self) -> None:
        """Legacy signal mapping: on_ErrorDialog_destroy."""
        self.last_error = ""
        self._log("Error dialog closed")

    def on_close_open_image_dialog(self) -> None:
        """Legacy signal mapping: on_ImgOpenDialog_destroy."""
        self._log("Open image dialog closed")

    def on_close_save_dialog(self) -> None:
        """Legacy signal mapping: on_SaveWallpaperDialog_destroy."""
        self._log("Save dialog closed")

    def on_close_settings_dialog(self) -> None:
        """Legacy signal mapping: on_SettingDialog_destroy."""
        self._log("Settings dialog closed")

    def on_close_color_dialog(self) -> None:
        """Legacy signal mapping: on_ColorSelectionDialog_destroy."""
        self._log("Color selection dialog closed")

    def on_close_srcdir_dialog(self) -> None:
        """Legacy signal mapping: on_SrcdirDialog_destroy."""
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
        return "apply_dry_run"

    def run_primary_flow_step(self) -> bool:
        """Execute one safe step of the primary flow.

        Order:
        - input missing -> no-op (False)
        - optimize ready -> optimize
        - apply ready -> apply dry-run
        """
        step = self.suggest_next_action()
        if step == "optimize":
            return self.on_optimize()
        if step == "apply_dry_run":
            return self.on_apply_dry_run()
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
                "hero-first",
                "optimize-apply-separation",
                "status-persistent-footer",
            ),
            "suggested_next_action": self.suggest_next_action(),
            "status": {
                "level": self.status_level,
                "phase": self.status_phase,
                "message": self.status_message,
                "last_error": self.last_error,
            },
        }

    def show(self) -> None:
        print(self.title)
        print(self.subtitle)
        print("GUI skeleton is ready. Next step: bind real GTK widgets.")
        print(f"Can optimize: {self.can_optimize}")
        print(f"Status: {self.status_level}/{self.status_phase} - {self.status_message}")

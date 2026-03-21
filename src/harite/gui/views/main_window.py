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
        self.title = "Harite GUI (MVP)"
        self.controller = OptimizeController()
        self.closed = False
        self.can_optimize = False
        self.last_error = ""
        self.logs: list[str] = []
        self.available_plugins = tuple(plugin_registry.list())
        self.plugin_name = self._default_plugin_name()
        self.last_saved_files: list[Path] = []
        self.form_state = OptimizeFormState(
            input_value="",
            resolution="1920x1080",
            output_dir=str(Path(".")),
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

    def on_change_input_text(self, text: str) -> None:
        """Legacy signal mapping: on_entPath_insert_text."""
        self.form_state.input_value = text
        self.can_optimize = bool(text and text.strip())
        if self.can_optimize:
            self.last_error = ""
            self._log("Input updated")
        else:
            self.last_error = "input is required"
            self._log("Input is empty")

    def on_optimize(self) -> bool:
        """Legacy signal mapping: on_btnSave_clicked."""
        if not self.can_optimize:
            self.last_error = "input is required"
            self._log("Optimize blocked: input is required")
            return False

        try:
            saved, _placements = self.controller.run_optimize(self.form_state)
            self.last_saved_files = list(saved)
            self.last_error = ""
            self._log(f"Saved {len(saved)} file(s)")
            for path in saved:
                self._log(f"Saved: {path}")
            return True
        except Exception as exc:
            self.last_error = str(exc)
            self._log(f"Optimize failed: {exc}")
            return False

    def _apply_latest(self, dry_run: bool) -> bool:
        if not self.last_saved_files:
            self.last_error = "no optimized file to apply"
            self._log("Apply blocked: no optimized file")
            return False

        target = str(self.last_saved_files[-1])
        try:
            plugin = plugin_registry.get(self.plugin_name)
        except KeyError:
            self.last_error = f"unknown plugin: {self.plugin_name}"
            self._log(f"Apply failed: unknown plugin {self.plugin_name}")
            return False

        ok = bool(plugin.apply(target, dry_run=dry_run))
        if ok:
            self.last_error = ""
            self._log(f"Applied wallpaper via plugin={self.plugin_name} dry_run={dry_run}: {target}")
            return True

        self.last_error = "failed to apply wallpaper"
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

    def show(self) -> None:
        print(self.title)
        print("GUI skeleton is ready. Next step: bind real GTK widgets.")
        print(f"Can optimize: {self.can_optimize}")

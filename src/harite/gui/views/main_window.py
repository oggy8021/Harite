"""GUI view placeholder.

This file intentionally avoids hard dependency on GTK/PyGObject so the core
package remains importable in environments without GUI libraries.
"""

from __future__ import annotations

import ctypes
from dataclasses import replace
import os
from pathlib import Path
import sys

from harite import __version__
from harite.core import DEFAULT_BACKGROUND_COLOR_HEX
from harite.core import describe_embed_position as describe_margin_text_position
from harite.core import is_background_color_literal
from harite.core import normalize_background_color
from harite.core import resolve_embed_margin_region as resolve_margin_text_region
from harite.apply_settings import resolve_apply_settings
from harite.config import load_config, save_config
from harite.display_context import build_two_screen_optimize_context
from harite.gui.controllers.optimize_controller import OptimizeController, OptimizeFormState
from harite.gui.views.main_window_preview import build_optimize_cli_preview
from harite.gui.views.main_window_preview import build_preview_assignments
from harite.gui.views.main_window_preview import build_preview_assist_summary
from harite.gui.views.main_window_preview import build_preview_result_notes
from harite.gui.views.main_window_preview import build_result_preview_state
from harite.gui.views.main_window_preview import format_display_summary
from harite.gui.views.main_window_preview import format_preview_assignment_name
from harite.gui.views.main_window_preview import ResultPreviewState
from harite.positioning import reset_position_pair, update_position_pair
from harite.plugins import registry as plugin_registry
from harite.preferences import AppPreferences
from harite.watch import WatchCycleState, collect_watch_input_images, run_watch_cycle

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
        self.apply_mode = self._default_apply_mode()
        self._pre_two_screen_resolution: str | None = None
        self.watch_interval_seconds = 60
        self.watch_srcdir_l = ""
        self.watch_srcdir_r = ""
        self.watch_summary_display = "Watch: stopped"
        self.watch_source_display = "Watch srcdirs: L=- | R=-"
        self.watch_current_display = "Watch current: idle"
        self.watch_output_display = "Watch output: ."
        self.watch_running = False
        self._watch_state_l = WatchCycleState()
        self._watch_state_r = WatchCycleState()
        self._watch_previous_l: Path | None = None
        self._watch_previous_r: Path | None = None
        self._watch_plugin_impl: object | None = None
        self._watch_dual_auto_split_enabled = False
        self._watch_active_generated_files: tuple[Path, ...] = ()
        self.open_image_dialog_open = False
        self.open_image_dialog_side: str | None = None
        self._save_path_dialog_open = False
        self.settings_dialog_open = False
        self.about_dialog_open = False
        self.input_path_l = ""
        self.input_path_r = ""
        default_output_dir = self._default_output_dir()
        self.form_state = OptimizeFormState(
            input_value="",
            resolution="1920x1080",
            output_dir=default_output_dir,
            background_color=DEFAULT_BACKGROUND_COLOR_HEX,
            embed_position="bottom",
        )
        self.preferences = AppPreferences.defaults(default_plugin=self.plugin_name)
        self.layout_version = "phase6-layout-redefinition"
        self.layout_sections: tuple[tuple[str, tuple[str, ...]], ...] = (
            ("title_menu_flow", ("title", "menu", "flow", "save_as")),
            ("compose_input", ("input_value", "cross_layout", "align", "valign")),
            ("margins_tab", ("margins", "margin_text", "margin_area")),
            ("action_cluster", ("optimize", "apply", "saved_files")),
            ("watch_tab", ("watch_summary", "watch_srcdirs", "watch_interval", "watch_controls", "watch_details")),
            ("status_footer", ("status_message", "watch_summary")),
        )
        self.primary_action_flow: tuple[str, ...] = (
            "save_as",
            "optimize",
            "apply",
        )
        self._update_watch_output_display()

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

    def _default_apply_mode(self) -> str:
        session_markers = (
            os.environ.get("XDG_CURRENT_DESKTOP", ""),
            os.environ.get("XDG_SESSION_DESKTOP", ""),
            os.environ.get("DESKTOP_SESSION", ""),
            os.environ.get("GDMSESSION", ""),
        )
        is_xfce_session = any("xfce" in marker.strip().lower() for marker in session_markers if marker)
        return "per-monitor-auto-split" if is_xfce_session else "single-file"

    def _default_output_dir(self) -> str:
        return str(self._resolve_default_output_dir())

    def _current_resolution_value(self) -> tuple[int, int] | None:
        value = (self.form_state.resolution or "").strip()
        if not value:
            return None
        try:
            width_text, height_text = value.lower().split("x", 1)
            width = int(width_text)
            height = int(height_text)
        except (ValueError, TypeError):
            return None
        if width <= 0 or height <= 0:
            return None
        return width, height

    def _normalize_margin_text_position(self, value: object | None) -> str:
        normalized = str(value or "").strip().lower()
        if normalized == "auto":
            return "bottom"
        if normalized in {"top", "bottom", "left", "right"}:
            return normalized
        return "bottom"

    def _resolve_default_output_dir(self) -> Path:
        if sys.platform == "win32":
            pictures_dir = self._resolve_windows_pictures_dir()
            if pictures_dir is not None:
                return pictures_dir

        pictures_dir = self._resolve_xdg_pictures_dir()
        if pictures_dir is not None:
            return pictures_dir

        return Path.home() / "Pictures"

    def _resolve_windows_pictures_dir(self) -> Path | None:
        try:
            buffer = ctypes.create_unicode_buffer(260)
            result = ctypes.windll.shell32.SHGetFolderPathW(None, 0x27, None, 0, buffer)
        except Exception:
            return None

        if result != 0 or not buffer.value:
            return None
        return Path(buffer.value)

    def _resolve_xdg_pictures_dir(self) -> Path | None:
        env_value = str(os.environ.get("XDG_PICTURES_DIR", "") or "").strip()
        if env_value:
            return self._normalize_pictures_dir(env_value)

        config_home = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
        user_dirs_path = config_home / "user-dirs.dirs"
        if not user_dirs_path.is_file():
            return None

        try:
            for raw_line in user_dirs_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or not line.startswith("XDG_PICTURES_DIR="):
                    continue
                return self._normalize_pictures_dir(line.split("=", 1)[1].strip())
        except OSError:
            return None
        return None

    def _normalize_pictures_dir(self, raw_value: str) -> Path:
        value = raw_value.strip().strip('"').strip("'")
        home = str(Path.home())
        value = value.replace("$HOME", home).replace("${HOME}", home)
        value = os.path.expandvars(value)
        path = Path(value).expanduser()
        if path.is_absolute():
            return path
        return Path.home() / path

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

        self._apply_input_paths()
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

    def _margin_text_area(self, position: str) -> tuple[int, int] | None:
        normalized = (position or "").strip().lower()
        if normalized not in {"top", "bottom", "left", "right"}:
            return None

        resolution = self._current_resolution_value()
        if resolution is None:
            return None

        target_width, target_height = resolution
        left, right, top, bottom = self._current_margin_values()
        region = resolve_margin_text_region(
            (target_width, target_height),
            (left, right, top, bottom),
            normalized,
            two_screen=bool(self.form_state.two_screen),
            l_display=self._parse_resolution_value(self.form_state.l_display),
            r_display=self._parse_resolution_value(self.form_state.r_display),
        )
        if region is None:
            return None
        x0, y0, x1, y1 = region
        return max(0, x1 - x0), max(0, y1 - y0)

    def _update_margin_text_preflight_status(self) -> None:
        margin_text_mode = str(getattr(self.form_state, "embed_info", "none") or "none").lower()
        if margin_text_mode == "none":
            self._set_status("idle", "margins", "margin text off")
            return

        margin_text_position = self._normalize_margin_text_position(self.form_state.embed_position)
        self.form_state.embed_position = margin_text_position
        area = self._margin_text_area(margin_text_position)
        if area is None:
            self._set_status("error", "margins", "margin area unavailable", error="margin area unavailable")
            self._log("Margin text preflight failed: area unavailable")
            return

        area_width, area_height = area
        if area_width < 40 or area_height < 12:
            self._set_status(
                "error",
                "margins",
                "margin text does not fit current margin area",
                error="selected margin area is too small for margin text",
            )
            self._log(f"Margin text preflight failed: {margin_text_position} margin too small ({area_width}x{area_height})")
            return

        self._set_status(
            "idle",
            "margins",
            f"margin text ready in {describe_margin_text_position(margin_text_position)} position ({area_width}x{area_height})",
        )
        self._log(f"Margin text preflight ready: {describe_margin_text_position(margin_text_position)} position ({area_width}x{area_height})")

    def _effective_margin_text_max_lines(self) -> int:
        margin_text_mode = str(getattr(self.form_state, "embed_info", "none") or "none").lower()
        if margin_text_mode == "free":
            return 5
        if margin_text_mode == "combo":
            return 8
        return 3

    def _margin_index_for_widget(self, widget_name: str) -> int | None:
        if "LeftMargin" in widget_name:
            return 0
        if "RightMargin" in widget_name:
            return 1
        if "TopMargin" in widget_name:
            return 2
        if "BottomMargin" in widget_name:
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
        self._update_margin_text_preflight_status()

    def on_toggle_position_pressed(self, widget_name: str) -> None:
        self._log(f"Toggle pressed: {widget_name}")

    def _toggle_side(self, widget_name: str) -> str | None:
        if widget_name.endswith("L"):
            return "L"
        if widget_name.endswith("R"):
            return "R"
        return None

    def on_toggle_position(self, widget_name: str, active: bool) -> None:
        if not active:
            return

        side = self._toggle_side(widget_name)
        if side is None:
            return

        if "PushLeft" in widget_name:
            self.form_state.align = update_position_pair(self.form_state.align, side, "left", axis="align")
            self._log(f"Align updated from {widget_name}: left")
            return
        if "PushRight" in widget_name:
            self.form_state.align = update_position_pair(self.form_state.align, side, "right", axis="align")
            self._log(f"Align updated from {widget_name}: right")
            return
        if "Upper" in widget_name:
            self.form_state.valign = update_position_pair(self.form_state.valign, side, "top", axis="valign")
            self._log(f"Valign updated from {widget_name}: top")
            return
        if "Lower" in widget_name:
            self.form_state.valign = update_position_pair(self.form_state.valign, side, "bottom", axis="valign")
            self._log(f"Valign updated from {widget_name}: bottom")

    def on_toggle_position_reset(self, widget_name: str) -> None:
        side = self._toggle_side(widget_name)
        if side is None:
            return
        if "Push" in widget_name:
            self.form_state.align = reset_position_pair(self.form_state.align, side, axis="align")
            self._log(f"Align reset from {widget_name}: center")
            return
        if "Upper" in widget_name or "Lower" in widget_name:
            self.form_state.valign = reset_position_pair(self.form_state.valign, side, axis="valign")
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

    def _update_watch_output_display(self) -> None:
        output_dir = str(Path(self.form_state.output_dir)) if self.form_state.output_dir else self._default_output_dir()
        self.watch_output_display = f"Watch output: {output_dir}"

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

    def _sync_two_screen_state(self) -> None:
        if not (self.input_path_l and self.input_path_r):
            if self.form_state.two_screen and self._pre_two_screen_resolution:
                self.form_state.resolution = self._pre_two_screen_resolution
                self._pre_two_screen_resolution = None
            self.form_state.two_screen = False
            self.form_state.l_display = None
            self.form_state.r_display = None
            return

        context = build_two_screen_optimize_context()
        if context is None:
            if self.form_state.two_screen and self._pre_two_screen_resolution:
                self.form_state.resolution = self._pre_two_screen_resolution
                self._pre_two_screen_resolution = None
            self.form_state.two_screen = False
            self.form_state.l_display = None
            self.form_state.r_display = None
            self._log("Two-screen unavailable: detected displays < 2")
            return

        if not self.form_state.two_screen:
            self._pre_two_screen_resolution = self.form_state.resolution
        self.form_state.two_screen = True
        self.form_state.l_display = f"{context.l_display[0]}x{context.l_display[1]}"
        self.form_state.r_display = f"{context.r_display[0]}x{context.r_display[1]}"
        self.form_state.resolution = f"{context.resolution[0]}x{context.resolution[1]}"
        self._log(
            "Two-screen auto-configured: "
            f"L={self.form_state.l_display} R={self.form_state.r_display} resolution={self.form_state.resolution}"
        )

    def _parse_resolution_value(self, value: str | None) -> tuple[int, int] | None:
        raw = str(value or "").strip().lower()
        if not raw or "x" not in raw:
            return None
        width_str, height_str = raw.split("x", 1)
        try:
            return int(width_str), int(height_str)
        except ValueError:
            return None

    def _format_display_summary(self, display: tuple[int, int] | None) -> str | None:
        return format_display_summary(display)

    def _build_preview_assist_summary(
        self,
        apply_mode: str,
        l_display: tuple[int, int] | None,
        r_display: tuple[int, int] | None,
    ) -> str:
        return build_preview_assist_summary(apply_mode, l_display, r_display)

    def _format_preview_assignment_name(self, value: str, max_length: int = 36) -> str:
        return format_preview_assignment_name(value, max_length=max_length)

    def _build_preview_assignments(self, input_values: list[str]) -> tuple[str, str]:
        return build_preview_assignments(input_values)

    def _build_preview_result_notes(self, apply_mode: str) -> tuple[str, str]:
        return build_preview_result_notes(apply_mode)

    def build_result_preview_state(self) -> ResultPreviewState:
        return build_result_preview_state(self)

    def on_change_apply_mode(self, mode: str) -> bool:
        value = (mode or "").strip().lower()
        if value not in {"single-file", "per-monitor-auto-split"}:
            self.last_error = f"unknown apply mode: {mode}"
            self._log(f"Apply mode update failed: unknown mode {mode}")
            return False

        self.apply_mode = value
        self.last_error = ""
        self._log(f"Apply mode updated: {value}")
        return True

    def on_change_margin_text_mode(self, value: str) -> bool:
        normalized = (value or "").strip().lower()
        if normalized not in {"none", "params", "free", "combo"}:
            self.last_error = f"unknown margin_text_mode: {value}"
            self._log(f"Margin text mode update failed: unknown value {value}")
            return False

        self.form_state.embed_info = normalized
        self._log(f"Margin text mode updated: {normalized}")
        self._update_margin_text_preflight_status()
        return True

    def on_change_margin_text(self, value: str | None) -> bool:
        text = None if value is None else str(value)
        if text:
            text = "\n".join(text.split("\n")[:5])
        self.form_state.embed_text = None if not text or not text.strip() else text
        self._log("Margin text updated")
        self._update_margin_text_preflight_status()
        return True

    def on_change_margin_text_position(self, value: str) -> bool:
        normalized = (value or "").strip().lower()
        if normalized not in {"top", "bottom", "left", "right"}:
            self.last_error = f"unknown margin_text_position: {value}"
            self._log(f"Margin area update failed: unknown value {value}")
            return False

        self.form_state.embed_position = normalized
        self._log(f"Margin area updated: {normalized}")
        self._update_margin_text_preflight_status()
        return True

    def on_change_margin_text_max_lines(self, value: int) -> bool:
        max_lines = int(value)
        if max_lines <= 0:
            self.last_error = "margin_text_max_lines must be positive"
            self._log("Margin text internal line limit update failed: non-positive value")
            return False

        self.form_state.embed_max_lines = max_lines
        self._log(f"Margin text internal line limit updated: {max_lines}")
        self._update_margin_text_preflight_status()
        return True

    def _apply_input_paths(self) -> None:
        self.form_state.input_value = ",".join(path for path in (self.input_path_l, self.input_path_r) if path)
        self._sync_two_screen_state()
        self.can_optimize = bool(self.form_state.input_value)
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

    def on_change_input_text(self, text: str) -> None:
        normalized = text.strip()
        parts = [part.strip() for part in normalized.split(",") if part.strip()]
        self.input_path_l = parts[0] if len(parts) >= 1 else ""
        self.input_path_r = parts[1] if len(parts) >= 2 else ""
        self._apply_input_paths()

    def on_save_as(self) -> bool:
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
        effective_state = replace(self.form_state, embed_max_lines=self._effective_margin_text_max_lines())

        try:
            saved, _placements = self.controller.run_optimize(effective_state)
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

        composite_path = self.last_saved_files[-1]
        try:
            effective_apply = resolve_apply_settings(
                file=composite_path,
                plugin_name=self.plugin_name,
                apply_mode=self.apply_mode,
                output_dir=composite_path.parent,
            )
        except ValueError as exc:
            self._set_status("error", "apply", str(exc), error=str(exc))
            self._log(f"Apply failed: {exc}")
            return False

        target = effective_apply.target
        if self.apply_mode == "per-monitor-auto-split":
            self._log(f"Apply per-monitor auto-split: {target}")

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

    def on_open_settings_dialog(self) -> bool:
        self.settings_dialog_open = True
        self._set_status("idle", "settings", "settings dialog opened")
        self._log("Settings dialog opened")
        return True

    def on_get_settings_config(self) -> dict[str, object]:
        return self.export_settings_config()

    def on_apply_settings(self, settings: AppPreferences | dict[str, object]) -> bool:
        settings_value = settings
        if isinstance(settings, dict):
            settings_value = AppPreferences.from_config_dict(settings, default_plugin=self.plugin_name)

        self.preferences = settings_value
        optimize = settings_value.optimize
        self.form_state.resolution = optimize.resolution
        self.form_state.scaling = optimize.scaling
        self.form_state.margins = optimize.margins
        self.form_state.align = optimize.align
        self.form_state.valign = optimize.valign
        self.form_state.quality = optimize.quality
        self.form_state.background_color = normalize_background_color(optimize.background_color)
        self.form_state.embed_info = optimize.embed_info
        self.form_state.embed_text = optimize.embed_text
        self.form_state.embed_position = self._normalize_margin_text_position(optimize.embed_position)
        self.form_state.embed_max_lines = optimize.embed_max_lines
        self.form_state.l_display = optimize.l_display
        self.form_state.r_display = optimize.r_display
        if optimize.two_screen_mode == "auto":
            self.form_state.two_screen = None
            if self.input_path_l and self.input_path_r:
                self._sync_two_screen_state()
        elif optimize.two_screen_mode == "on":
            self.form_state.two_screen = True
        else:
            self.form_state.two_screen = False
            self.form_state.l_display = None if optimize.l_display == "auto" else optimize.l_display
            self.form_state.r_display = None if optimize.r_display == "auto" else optimize.r_display

        self.plugin_name = settings_value.apply.plugin_name
        self.apply_mode = settings_value.apply.apply_mode
        self.watch_interval_seconds = settings_value.watch.interval_seconds
        self.watch_srcdir_l = settings_value.watch.srcdir_l or ""
        self.watch_srcdir_r = settings_value.watch.srcdir_r or ""
        self._update_watch_source_display()
        self._update_watch_output_display()
        self.settings_dialog_open = False
        self._set_status("success", "settings", "settings applied")
        self._log("Settings applied")
        return True

    def export_settings_config(self) -> dict[str, object]:
        self.preferences.optimize.resolution = self.form_state.resolution
        self.preferences.optimize.scaling = self.form_state.scaling
        self.preferences.optimize.margins = self.form_state.margins
        self.preferences.optimize.align = self.form_state.align
        self.preferences.optimize.valign = self.form_state.valign
        self.preferences.optimize.quality = self.form_state.quality
        self.preferences.optimize.background_color = normalize_background_color(self.form_state.background_color)
        self.preferences.optimize.embed_info = self.form_state.embed_info
        self.preferences.optimize.embed_text = self.form_state.embed_text
        self.preferences.optimize.embed_position = self.form_state.embed_position
        self.preferences.optimize.embed_max_lines = self.form_state.embed_max_lines
        self.preferences.apply.plugin_name = self.plugin_name
        self.preferences.apply.apply_mode = self.apply_mode
        self.preferences.watch.interval_seconds = self.watch_interval_seconds
        self.preferences.watch.srcdir_l = self.watch_srcdir_l or None
        self.preferences.watch.srcdir_r = self.watch_srcdir_r or None
        if self.form_state.two_screen is None:
            self.preferences.optimize.two_screen_mode = "auto"
        else:
            self.preferences.optimize.two_screen_mode = "on" if self.form_state.two_screen else "off"
        self.preferences.optimize.l_display = self.form_state.l_display
        self.preferences.optimize.r_display = self.form_state.r_display
        return self.preferences.to_config_dict()

    def load_settings_config(self, config: dict[str, object]) -> bool:
        return self.on_apply_settings(AppPreferences.from_config_dict(config, default_plugin=self.plugin_name))

    def on_save_settings_file(
        self,
        path: str | None = None,
        config: dict[str, object] | None = None,
    ) -> bool:
        value = (path or "").strip()
        if not value:
            self._set_status("error", "settings", "settings path is required", error="settings path is required")
            self._log("Settings save failed: path is required")
            return False
        try:
            payload = config if config is not None else self.export_settings_config()
            save_config(Path(value), payload)
        except Exception as exc:
            self._set_status("error", "settings", "settings save failed", error=str(exc))
            self._log(f"Settings save failed: {exc}")
            return False
        self._set_status("success", "settings", "settings saved")
        self._log(f"Settings saved: {value}")
        return True

    def on_load_settings_file(self, path: str | None = None) -> bool:
        value = (path or "").strip()
        if not value:
            self._set_status("error", "settings", "settings path is required", error="settings path is required")
            self._log("Settings load failed: path is required")
            return False
        try:
            config = load_config(Path(value))
        except Exception as exc:
            self._set_status("error", "settings", "settings load failed", error=str(exc))
            self._log(f"Settings load failed: {exc}")
            return False
        ok = self.load_settings_config(config)
        if ok:
            self._log(f"Settings loaded: {value}")
        return ok

    def on_clear_input(self, side: str | None = None) -> bool:
        normalized_side = (side or "").strip().upper()
        if normalized_side == "L":
            self.input_path_l = ""
        elif normalized_side == "R":
            self.input_path_r = ""
        else:
            self.input_path_l = ""
            self.input_path_r = ""

        self._apply_input_paths()
        if normalized_side in {"L", "R"}:
            self._log(f"Input cleared ({normalized_side})")
        else:
            self._log("Input cleared")
        return True

    def on_about(self) -> bool:
        self.about_dialog_open = True
        self._set_status("idle", "about", "about dialog opened")
        self._log("About dialog opened")
        return True

    def on_get_about_dialog_info(self) -> dict[str, str]:
        return {
            "app_name": self.title,
            "version": __version__,
            "description": "壁紙最適化ツール（リファクタリング版）",
            "credits": "Created by oggy8021",
            "license_name": "MIT License",
        }

    def on_close_about_dialog(self) -> None:
        self.about_dialog_open = False
        self._log("About dialog closed")

    def on_set_color(self, color: str | None = None) -> bool:
        if color is None:
            self._set_status("idle", "color", "color dialog opened")
            self._log("Color dialog opened")
            return True

        if not is_background_color_literal(color):
            self._set_status("error", "color", "invalid background color", error="invalid background color")
            self._log(f"Background color rejected: {color}")
            return False

        normalized = normalize_background_color(color)
        self.form_state.background_color = normalized
        self.preferences.optimize.background_color = normalized
        self._set_status("success", "color", f"background color updated: {normalized}")
        self._log(f"Background color updated: {normalized}")
        return True

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

    def _prepare_watch_apply(self, source_count: int) -> bool:
        self._watch_dual_auto_split_enabled = False
        if source_count < 1:
            self._watch_plugin_impl = None
            return True

        if source_count > 1:
            if self.plugin_name != "linux":
                message = "dual-source watch requires linux plugin"
                self._watch_plugin_impl = None
                self._set_status("error", "watch", message, error=message)
                self._log(f"Watch start blocked: {message}")
                return False

            if build_two_screen_optimize_context() is None:
                message = "dual-source watch requires two detected displays"
                self._watch_plugin_impl = None
                self._set_status("error", "watch", message, error=message)
                self._log(f"Watch start blocked: {message}")
                return False

            self._watch_dual_auto_split_enabled = True

        try:
            self._watch_plugin_impl = plugin_registry.get(self.plugin_name)
        except KeyError:
            self._set_status(
                "error",
                "watch",
                "unknown plugin",
                error=f"unknown plugin: {self.plugin_name}",
            )
            self._log(f"Watch start failed: unknown plugin {self.plugin_name}")
            return False
        return True

    def _build_watch_two_screen_state(self, left: str, right: str) -> OptimizeFormState:
        watch_state = replace(self.form_state, input_value=f"{left},{right}")
        context = build_two_screen_optimize_context()
        if context is not None:
            watch_state.two_screen = True
            watch_state.l_display = f"{context.l_display[0]}x{context.l_display[1]}"
            watch_state.r_display = f"{context.r_display[0]}x{context.r_display[1]}"
            watch_state.resolution = f"{context.resolution[0]}x{context.resolution[1]}"
        return watch_state

    def _ensure_watch_output_dir(self) -> None:
        output_dir = str(self.form_state.output_dir or "").strip()
        if not output_dir:
            self.form_state.output_dir = self._default_output_dir()
        self._update_watch_output_display()

    def _cleanup_watch_generated_files(self, paths: tuple[Path, ...]) -> None:
        for path in paths:
            try:
                if path.exists():
                    path.unlink()
                    self._log(f"Watch cleanup removed: {path}")
            except OSError as exc:
                self._log(f"Watch cleanup failed: {path} ({exc})")

    def _set_watch_active_generated_files(self, paths: tuple[Path, ...]) -> None:
        previous_paths = self._watch_active_generated_files
        self._watch_active_generated_files = paths
        if previous_paths and previous_paths != paths:
            self._cleanup_watch_generated_files(previous_paths)

    def _apply_watch_target(self, target: object, *, cycle_phase: str, apply_mode: str) -> bool:
        if self._watch_plugin_impl is None:
            return False

        try:
            ok = bool(self._watch_plugin_impl.apply(target, dry_run=False))
        except Exception as exc:
            self._log(f"Watch {cycle_phase} {apply_mode} apply error: {exc}")
            return False

        if ok:
            self._log(f"Watch {cycle_phase} {apply_mode} apply ok: {target}")
            return True

        self._log(f"Watch {cycle_phase} {apply_mode} apply failed: {target}")
        return False

    def _apply_watch_selection(self, left: str, right: str, *, cycle_phase: str) -> tuple[bool, str | None]:
        selected_paths = [path for path in (left, right) if path != "-"]
        if not selected_paths:
            return True, None
        if self._watch_plugin_impl is None:
            return False, "watch plugin is not ready"

        if len(selected_paths) == 1:
            if self._apply_watch_target(selected_paths[0], cycle_phase=cycle_phase, apply_mode="single-file"):
                self._set_watch_active_generated_files(())
                return True, None
            return False, f"watch {cycle_phase} single-file apply failed"

        if not self._watch_dual_auto_split_enabled:
            return False, "dual-source watch auto-split is not enabled"

        try:
            watch_state = self._build_watch_two_screen_state(selected_paths[0], selected_paths[1])
            saved_files, _placements = self.controller.run_optimize(watch_state)
            composite_path = saved_files[-1]
            effective_apply = resolve_apply_settings(
                file=composite_path,
                plugin_name=self.plugin_name,
                apply_mode="per-monitor-auto-split",
                output_dir=composite_path.parent,
            )
        except Exception as exc:
            self._log(f"Watch {cycle_phase} auto-split prepare failed: {exc}")
            return False, f"watch {cycle_phase} auto-split prepare failed"

        self._log(f"Watch {cycle_phase} per-monitor auto-split: {effective_apply.target}")
        generated_files = [composite_path]
        if isinstance(effective_apply.target, dict):
            generated_files.extend(Path(str(path)) for path in effective_apply.target.values())

        if self._apply_watch_target(
            effective_apply.target,
            cycle_phase=cycle_phase,
            apply_mode="per-monitor-auto-split",
        ):
            deduped = tuple(dict.fromkeys(generated_files))
            self._set_watch_active_generated_files(deduped)
            return True, None
        return False, f"watch {cycle_phase} per-monitor auto-split apply failed"

    def on_watch_start(self) -> bool:
        sources: list[tuple[str, Path]] = []
        self._ensure_watch_output_dir()
        if self.watch_srcdir_l.strip():
            sources.append(("L", Path(self.watch_srcdir_l.strip())))
        if self.watch_srcdir_r.strip():
            sources.append(("R", Path(self.watch_srcdir_r.strip())))
        if not sources:
            self._set_status("error", "watch", "watch srcdir is required", error="watch srcdir is required")
            self._log("Watch start blocked: watch srcdir is required")
            return False

        if not self._prepare_watch_apply(len(sources)):
            return False

        selected_left = "-"
        selected_right = "-"
        for side, source_dir in sources:
            try:
                selected = self._run_watch_cycle_for_side(side, source_dir)
            except ValueError as exc:
                self._set_status("error", "watch", f"watch srcdir {side} invalid", error=str(exc))
                self._log(f"Watch start failed ({side}): {exc}")
                return False

            if side == "L":
                selected_left = selected
            else:
                selected_right = selected

        self.watch_running = True
        self._update_watch_summary_display()
        self._update_watch_source_display()
        self._update_watch_current_display(selected_left, selected_right)
        applied, error_message = self._apply_watch_selection(selected_left, selected_right, cycle_phase="start")
        if not applied:
            self.watch_running = False
            self._update_watch_summary_display()
            self._set_status("error", "watch", error_message or "watch start apply failed", error=error_message or "watch start apply failed")
            self._log(f"Watch start failed: {error_message or 'watch start apply failed'}")
            return False
        self._set_status("success", "watch", "watch started")
        self._log(
            f"Watch started: interval={self.watch_interval_seconds}s L={selected_left} R={selected_right}"
        )
        return True

    def on_watch_tick(self) -> bool:
        if not self.watch_running:
            self._log("Watch tick ignored: watch is idle")
            return False

        selected_left = "-"
        selected_right = "-"
        sources: list[tuple[str, Path]] = []
        if self.watch_srcdir_l.strip():
            sources.append(("L", Path(self.watch_srcdir_l.strip())))
        if self.watch_srcdir_r.strip():
            sources.append(("R", Path(self.watch_srcdir_r.strip())))

        for side, source_dir in sources:
            try:
                selected = self._run_watch_cycle_for_side(side, source_dir)
            except ValueError as exc:
                self._set_status("error", "watch", f"watch srcdir {side} invalid", error=str(exc))
                self._log(f"Watch tick failed ({side}): {exc}")
                return False

            if side == "L":
                selected_left = selected
            else:
                selected_right = selected

        self._update_watch_current_display(selected_left, selected_right)
        applied, error_message = self._apply_watch_selection(selected_left, selected_right, cycle_phase="tick")
        if not applied:
            self.watch_running = False
            self._update_watch_summary_display()
            self._set_status("error", "watch", error_message or "watch tick apply failed", error=error_message or "watch tick apply failed")
            self._log(f"Watch tick stopped: {error_message or 'watch tick apply failed'}")
            return False
        self._log(f"Watch tick: L={selected_left} R={selected_right}")
        return True

    def on_watch_stop(self) -> bool:
        if not self.watch_running:
            self._set_status("idle", "watch", "watch stop ignored (idle)")
            self._log("Watch stop ignored: watch is idle")
            return False
        self.watch_running = False
        self._watch_plugin_impl = None
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
        self.settings_dialog_open = False
        self._log("Settings dialog closed")

    def on_close_color_dialog(self) -> None:
        self._log("Color selection dialog closed")

    def on_close_srcdir_dialog(self) -> None:
        self._log("Source directory dialog closed")

    def build_optimize_cli_preview(self) -> str:
        return build_optimize_cli_preview(self)

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

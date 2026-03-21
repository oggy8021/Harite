"""GUI view placeholder.

This file intentionally avoids hard dependency on GTK/PyGObject so the core
package remains importable in environments without GUI libraries.
"""

from __future__ import annotations

from pathlib import Path

from harite.gui.controllers.optimize_controller import OptimizeController, OptimizeFormState


class MainWindow:
    """Framework-neutral placeholder for the first standalone GUI window."""

    def __init__(self) -> None:
        self.title = "Harite GUI (MVP)"
        self.controller = OptimizeController()
        self.closed = False
        self.can_optimize = False
        self.last_error = ""
        self.logs: list[str] = []
        self.form_state = OptimizeFormState(
            input_value="",
            resolution="1920x1080",
            output_dir=str(Path(".")),
        )

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
            self.last_error = ""
            self._log(f"Saved {len(saved)} file(s)")
            for path in saved:
                self._log(f"Saved: {path}")
            return True
        except Exception as exc:
            self.last_error = str(exc)
            self._log(f"Optimize failed: {exc}")
            return False

    def on_close(self) -> None:
        """Legacy signal mapping: on_WallPosit_MainWindow_delete_event."""
        self.closed = True
        self._log("Window closed")

    def show(self) -> None:
        print(self.title)
        print("GUI skeleton is ready. Next step: bind real GTK widgets.")
        print(f"Can optimize: {self.can_optimize}")

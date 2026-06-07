from __future__ import annotations

from harite.gui.adapters.gtk_runtime_action_handlers import run_apply_clicked, run_optimize_clicked


class _FakeBackend:
    def __init__(self) -> None:
        self.feedback: list[tuple] = []
        self.labels: dict[str, str] = {}
        self.buttons: dict[str, bool] = {"btnSetWall": False}
        self.preview_syncs = 0
        self.availability_syncs = 0
        self.feedback_syncs = 0
        self._owner = None

    def _set_feedback(self, *, phase: str, state: str, error: str | None = None) -> None:
        self.feedback.append((phase, state, error))

    def _set_label_text(self, name: str, text: str) -> None:
        self.labels[name] = text

    def _set_button_enabled(self, name: str, enabled: bool) -> None:
        self.buttons[name] = enabled

    def _get_handler_owner(self, _handler_name: str):
        return self._owner

    def _sync_preview_state_from_owner(self, owner) -> None:
        self.preview_syncs += 1
        self._owner = owner

    def _sync_action_availability_from_owner(self, owner) -> None:
        self.availability_syncs += 1
        self._owner = owner

    def _sync_feedback_from_owner(self, owner) -> None:
        self.feedback_syncs += 1
        phase = str(getattr(owner, "status_phase", "") or "").strip() or "slideshow"
        message = str(getattr(owner, "status_message", "") or "").strip() or "state-updated"
        error = str(getattr(owner, "last_error", "") or "").strip() or None
        self._set_feedback(phase=phase.capitalize(), state=message, error=error)


def test_run_optimize_clicked_success_enables_apply_and_syncs_owner():
    backend = _FakeBackend()

    class _Owner:
        can_optimize = True
        can_apply = True
        status_message = "optimize completed"

    owner = _Owner()
    backend._owner = owner

    run_optimize_clicked(backend, lambda: True)

    assert backend.buttons["btnSetWall"] is True
    assert backend.preview_syncs == 1
    assert backend.availability_syncs == 1
    assert backend.feedback_syncs == 1
    assert backend.feedback[-1] == ("Slideshow", "optimize completed", None)
    assert "lblOptimizeResult" not in backend.labels


def test_run_optimize_clicked_failure_disables_apply_button():
    backend = _FakeBackend()

    run_optimize_clicked(backend, lambda: False)

    assert backend.buttons["btnSetWall"] is False
    assert backend.feedback[-1] == (
        "Optimize",
        "optimize failed",
        "optimize returned false",
    )
    assert "lblApplyTarget" not in backend.labels


def test_run_optimize_clicked_does_not_set_action_cluster_result_labels():
    backend = _FakeBackend()

    run_optimize_clicked(backend, lambda: True)

    assert not any(name.startswith("lblOptimize") or name.startswith("lblApply") for name in backend.labels)


def test_run_apply_clicked_success_syncs_footer_from_owner():
    backend = _FakeBackend()

    class _Owner:
        status_message = "wallpaper applied"

    backend._owner = _Owner()

    run_apply_clicked(backend, lambda: True)

    assert backend.feedback_syncs == 1
    assert backend.feedback[-1] == ("Slideshow", "wallpaper applied", None)
    assert "lblApplyTarget" not in backend.labels

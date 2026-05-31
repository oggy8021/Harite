from __future__ import annotations

from harite.gui.adapters.gtk_runtime_action_handlers import run_apply_clicked, run_optimize_clicked


class _FakeBackend:
    def __init__(self) -> None:
        self.feedback: list[tuple] = []
        self.labels: dict[str, str] = {}
        self.buttons: dict[str, bool] = {"btnSetWall": False}
        self.preview_syncs = 0
        self.availability_syncs = 0
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


def test_run_optimize_clicked_success_updates_labels_and_apply_button():
    backend = _FakeBackend()

    class _Owner:
        can_optimize = True
        can_apply = True

    owner = _Owner()
    backend._owner = owner

    run_optimize_clicked(backend, lambda: True)

    assert backend.buttons["btnSetWall"] is True
    assert backend.labels["lblOptimizeResult"] == "Optimize result: success"
    assert backend.labels["lblApplyTarget"] == "Apply target: ready"
    assert backend.preview_syncs == 1
    assert backend.availability_syncs == 1
    assert backend.feedback[-1] == ("Optimize", "ok", None)


def test_run_optimize_clicked_failure_resets_apply_target():
    backend = _FakeBackend()

    run_optimize_clicked(backend, lambda: False)

    assert backend.buttons["btnSetWall"] is False
    assert backend.labels["lblOptimizeResult"] == "Optimize result: failed"
    assert backend.labels["lblApplyTarget"] == "Apply target: not-ready"


def test_run_optimize_clicked_does_not_use_not_run_label():
    backend = _FakeBackend()

    run_optimize_clicked(backend, lambda: True)

    assert "not-run" not in backend.labels.get("lblOptimizeResult", "")


def test_run_apply_clicked_success_updates_target_label():
    backend = _FakeBackend()

    run_apply_clicked(backend, lambda: True)

    assert backend.labels["lblApplyTarget"] == "Apply target: last applied"
    assert backend.feedback[-1] == ("Apply", "ok", None)

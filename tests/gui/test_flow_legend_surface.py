from __future__ import annotations

from harite.gui.views.flow_legend_surface import (
    flow_legend_active_step,
    format_flow_legend_markup,
    format_flow_legend_plain,
)


class _Owner:
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_flow_legend_active_step_defaults_to_compose():
    assert flow_legend_active_step(None) == "compose"
    assert flow_legend_active_step(_Owner()) == "compose"


def test_flow_legend_active_step_compose_when_input_ready():
    owner = _Owner(can_optimize=True, can_apply=False)
    assert flow_legend_active_step(owner) == "compose"


def test_flow_legend_active_step_optimize_after_optimize():
    owner = _Owner(can_optimize=True, can_apply=True)
    assert flow_legend_active_step(owner) == "optimize"


def test_flow_legend_active_step_apply_after_apply_completed():
    owner = _Owner(
        can_optimize=True,
        can_apply=True,
        status_phase="apply",
        status_level="success",
        status_message="apply completed",
    )
    assert flow_legend_active_step(owner) == "apply"


def test_format_flow_legend_markup_bolds_active_step():
    assert format_flow_legend_markup(active_step="compose") == (
        "<b>Compose</b> -> Optimize -> Apply"
    )
    assert format_flow_legend_markup(active_step="optimize") == (
        "Compose -> <b>Optimize</b> -> Apply"
    )
    assert format_flow_legend_markup(active_step="apply") == (
        "Compose -> Optimize -> <b>Apply</b>"
    )


def test_format_flow_legend_plain_is_unstyled():
    assert format_flow_legend_plain() == "Compose -> Optimize -> Apply"

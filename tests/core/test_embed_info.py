"""Tests for embed_info normalization."""

from __future__ import annotations

import pytest

from harite.embed_info import (
    EMBED_INFO_SETTINGS,
    normalize_embed_info,
    embed_info_includes_settings,
)


def test_normalize_embed_info_empty_is_none():
    assert normalize_embed_info(None) == "none"
    assert normalize_embed_info("") == "none"


def test_normalize_embed_info_maps_params_to_settings():
    assert normalize_embed_info("params") == EMBED_INFO_SETTINGS
    assert normalize_embed_info("PARAMS") == EMBED_INFO_SETTINGS


def test_normalize_embed_info_rejects_unknown():
    with pytest.raises(ValueError, match="embed_info must be one of"):
        normalize_embed_info("bogus")


def test_embed_info_includes_settings_accepts_legacy_alias():
    assert embed_info_includes_settings("params") is True
    assert embed_info_includes_settings("settings") is True


def test_build_embed_lines_appends_scale_tokens():
    from harite.core import _build_embed_lines

    lines = _build_embed_lines(
        "settings",
        target_resolution=(1920, 1080),
        margins=(10, 10, 0, 0),
        align="center",
        valign="center",
        input_count=2,
        two_screen=True,
        l_display=(1920, 1080),
        r_display=(1920, 1080),
        free_text=None,
        l_display_scale=1.25,
        r_display_scale=1.0,
        l_auto_display_scale=False,
        r_auto_display_scale=True,
    )
    assert len(lines) == 2
    assert "inputs=2 L=125% R=auto" in lines[1]

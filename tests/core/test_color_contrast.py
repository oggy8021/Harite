"""Tests for embed text contrast selection."""

from __future__ import annotations

import pytest

from harite.color_contrast import choose_contrasting_embed_text_rgb, relative_luminance


def test_relative_luminance_black_and_white():
    assert relative_luminance((0, 0, 0)) == pytest.approx(0.0, abs=1e-6)
    assert relative_luminance((255, 255, 255)) == pytest.approx(1.0, abs=1e-6)


def test_choose_contrasting_embed_text_on_dark_background():
    assert choose_contrasting_embed_text_rgb((30, 30, 30)) == (235, 235, 235)


def test_choose_contrasting_embed_text_on_light_background():
    assert choose_contrasting_embed_text_rgb((224, 224, 224)) == (35, 35, 35)

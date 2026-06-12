"""Settings embed preview label tracks live input paths."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from harite.gui.adapters.gui_runtime_sync import (
    build_margin_settings_preview,
    refresh_margin_settings_preview_label,
    sync_input_state_from_owner,
)


class _PreviewBackend:
    def __init__(self) -> None:
        self._input_path_l = ""
        self._input_path_r = ""
        self.preview_text = ""

    def _format_input_display(self, path: str) -> str:
        return path

    def _set_entry_text(self, _name: str, _text: str) -> None:
        return None

    def _set_save_path_dialog_open_state(self, _open: bool) -> None:
        return None

    def _set_label_text(self, name: str, text: str) -> None:
        if name == "lblMarginSettingsPreview":
            self.preview_text = text

    def _set_button_enabled(self, _name: str, _enabled: bool) -> None:
        return None


def test_build_margin_settings_preview_uses_owner_input_paths(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.adapters.gui_runtime_sync.resolve_optimize_display_settings",
        lambda **kwargs: SimpleNamespace(
            resolution="1920x1080",
            two_screen=False,
            l_display="1920x1080",
            r_display=None,
            canvas_scale_percent=100,
        ),
    )
    owner = SimpleNamespace(
        form_state=SimpleNamespace(
            input_value="",
            margins="0,0,0,0",
            align="center",
            valign="center",
            canvas_scale_percent=100,
            l_display_scale=1.0,
            r_display_scale=1.0,
            l_auto_display_scale=False,
            r_auto_display_scale=False,
        ),
        input_path_l="/tmp/left.jpg",
        input_path_r="",
        can_optimize=True,
        can_apply=False,
        can_start_slideshow=False,
    )
    backend = _PreviewBackend()

    preview = build_margin_settings_preview(backend, owner)

    assert preview.startswith("canvas=1920x1080@100%")
    assert "input required" not in preview


def test_sync_input_state_refreshes_settings_preview_label(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.adapters.gui_runtime_sync.resolve_optimize_display_settings",
        lambda **kwargs: SimpleNamespace(
            resolution="3840x1080",
            two_screen=True,
            l_display="1920x1080",
            r_display="1920x1080",
            canvas_scale_percent=100,
        ),
    )
    monkeypatch.setattr(
        "harite.gui.adapters.gui_runtime_sync.sync_action_availability_from_owner",
        lambda *_args, **_kwargs: None,
    )
    owner = SimpleNamespace(
        form_state=SimpleNamespace(
            input_value="",
            margins="10,10,0,0",
            align="center",
            valign="center",
            canvas_scale_percent=100,
            l_display_scale=1.0,
            r_display_scale=1.0,
            l_auto_display_scale=False,
            r_auto_display_scale=False,
        ),
        input_path_l="/tmp/left.jpg",
        input_path_r="/tmp/right.jpg",
    )
    backend = _PreviewBackend()
    backend.preview_text = "input required for settings preview"

    sync_input_state_from_owner(backend, owner)

    assert "canvas=3840x1080@100%" in backend.preview_text
    assert "L=1920x1080 R=1920x1080" in backend.preview_text


def test_refresh_margin_settings_preview_label_updates_label(monkeypatch):
    monkeypatch.setattr(
        "harite.gui.adapters.gui_runtime_sync.build_margin_settings_preview",
        lambda _backend, _owner: "canvas=1x1@100%",
    )
    backend = MagicMock()
    refresh_margin_settings_preview_label(backend, None)
    backend._set_label_text.assert_called_once_with("lblMarginSettingsPreview", "canvas=1x1@100%")

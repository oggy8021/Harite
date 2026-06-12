"""Tests for the Qt dialog builders and proxies (Phase 6).

Covers widget existence, initial states, proxy API compliance,
and full-layout integration.
All Qt tests require the ``qapp`` fixture from conftest.py.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Module importability
# ---------------------------------------------------------------------------


def test_qt_dialogs_importable():
    from harite.gui.adapters_qt import qt_dialogs  # noqa: F401

    assert callable(qt_dialogs.build_dialogs)
    assert callable(qt_dialogs.build_settings_dialog)
    assert callable(qt_dialogs.build_color_dialog)
    assert callable(qt_dialogs.build_about_dialog)
    assert callable(qt_dialogs.build_file_dialog_proxies)


# ===========================================================================
# Settings dialog
# ===========================================================================


def test_settings_dialog_required_widgets(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_settings_dialog

    w = build_settings_dialog()

    expected = {
        "prefs_window",
        "prefs_save_btn",
        "prefs_ok_btn",
        "prefs_cancel_btn",
        "prefs_state_label",
        "prefs_notice_label",
        "prefs_canvas_scale_spin",
        "prefs_scaling_entry",
        "prefs_plugin_entry",
        "prefs_apply_single",
        "prefs_apply_per_monitor",
        "prefs_margins_entry",
        "prefs_align_entry",
        "prefs_valign_entry",
        "prefs_quality_spin",
        "prefs_margin_text_mode_entry",
        "prefs_margin_text_entry",
        "prefs_margin_text_position_entry",
        "prefs_margin_text_max_lines_spin",
        "settings_dialog_proxy",
        "SettingsDialog",
    }
    assert expected <= set(w)


def test_settings_dialog_initial_state(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_settings_dialog

    w = build_settings_dialog()

    assert w["prefs_apply_single"].isChecked()
    assert not w["prefs_apply_per_monitor"].isChecked()
    assert w["prefs_canvas_scale_spin"].value() == 100
    assert w["prefs_quality_spin"].value() == 90
    assert w["prefs_margin_text_max_lines_spin"].value() == 3
    assert w["prefs_state_label"].text() == "Settings: current values"
    assert w["prefs_notice_label"].text() == ""


def test_settings_dialog_apply_mode_is_mutually_exclusive(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_settings_dialog

    w = build_settings_dialog()

    w["prefs_apply_per_monitor"].setChecked(True)
    assert w["prefs_apply_per_monitor"].isChecked()
    assert not w["prefs_apply_single"].isChecked()


def test_settings_dialog_windows_span_row_only_on_windows_host(qapp, monkeypatch):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_dialogs import build_settings_dialog

    def _windows_label(editor) -> QLabel | None:
        for label in editor.findChildren(QLabel):
            if label.text() == "Windows":
                return label
        return None

    monkeypatch.setattr("harite.apply_surface.is_windows_host", lambda: False)
    w = build_settings_dialog()
    assert _windows_label(w["prefs_editor_box"]) is None
    assert w["prefs_windows_apply_span"].parent() is None

    monkeypatch.setattr("harite.apply_surface.is_windows_host", lambda: True)
    w_win = build_settings_dialog()
    assert _windows_label(w_win["prefs_editor_box"]) is not None
    assert w_win["prefs_windows_apply_span"].parent() is not None


def test_settings_dialog_canvas_scale_within_bounds(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_settings_dialog

    w = build_settings_dialog()

    w["prefs_canvas_scale_spin"].setValue(50)
    assert w["prefs_canvas_scale_spin"].value() == 50


def test_settings_dialog_proxy_get_set_settings(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_settings_dialog

    w = build_settings_dialog()
    proxy = w["SettingsDialog"]

    assert proxy.get_settings() == {}

    test_settings = {"resolution": "1920x1080", "scaling": "fit"}
    proxy.set_settings(test_settings)
    assert proxy.get_settings() == test_settings

    # Modifying the returned dict does not affect internal state
    returned = proxy.get_settings()
    returned["extra"] = "value"
    assert "extra" not in proxy.get_settings()


def test_settings_dialog_proxy_show_hide(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_settings_dialog

    w = build_settings_dialog()
    proxy = w["SettingsDialog"]

    proxy.show()
    proxy.hide()


def test_settings_dialog_proxy_get_export_path(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_settings_dialog

    w = build_settings_dialog()
    proxy = w["SettingsDialog"]

    # Should return a default settings path string (GTK proxy contract)
    path = proxy.get_export_path()
    assert isinstance(path, str)


# ===========================================================================
# Color dialog
# ===========================================================================


def test_color_dialog_required_widgets(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog()

    expected = {
        "color_window",
        "color_value_entry",
        "color_state_label",
        "color_notice_label",
        "color_pick_btn",
        "color_apply_btn",
        "color_cancel_btn",
        "color_dialog_proxy",
        "ColorDialog",
    }
    assert expected <= set(w)


def test_color_dialog_initial_state(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog(default_color_hex="#AABBCC")

    assert w["color_state_label"].text() == "Color: #AABBCC"
    assert w["color_value_entry"].text() == "#AABBCC"
    assert w["color_notice_label"].text() == ""


def test_color_dialog_proxy_get_color(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog(default_color_hex="#112233")
    proxy = w["ColorDialog"]

    assert proxy.get_color() == "#112233"


def test_color_dialog_proxy_set_color(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog(default_color_hex="#000000")
    proxy = w["ColorDialog"]

    proxy.set_color("#FFFFFF")
    assert proxy.get_color() == "#FFFFFF"


def test_color_dialog_proxy_get_pending_color(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog(default_color_hex="#334455")
    proxy = w["ColorDialog"]

    assert proxy.get_pending_color() == "#334455"


def test_color_dialog_proxy_get_pending_color_reads_entry_text(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog(default_color_hex="#112233")
    w["color_value_entry"].setText("#AABBCC")

    assert w["ColorDialog"].get_pending_color() == "#AABBCC"


def test_color_dialog_open_dialog_shows_manual_editor(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog()
    proxy = w["ColorDialog"]

    proxy.open_dialog()

    assert w["color_window"].isVisible() is True


def test_color_dialog_shows_color_preview_in_picker_host(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog(default_color_hex="#112233")
    proxy = w["ColorDialog"]

    assert proxy._color_preview is not None
    assert w["color_picker_host"].layout().count() >= 2
    assert "background-color: #112233" in proxy._color_preview.styleSheet()
    proxy.open_dialog()
    assert w["color_pick_btn"].isHidden() is False


def test_color_dialog_preview_syncs_with_entry(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog(default_color_hex="#112233")
    proxy = w["ColorDialog"]

    w["color_value_entry"].setText("#AABBCC")

    assert "background-color: #AABBCC" in proxy._color_preview.styleSheet()
    assert proxy.get_pending_color() == "#AABBCC"


def test_color_dialog_pick_color_syncs_entry(qapp, monkeypatch):
    from PyQt6.QtGui import QColor

    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog(default_color_hex="#112233")
    proxy = w["ColorDialog"]

    monkeypatch.setattr(
        "PyQt6.QtWidgets.QColorDialog.getColor",
        lambda *_args, **_kwargs: QColor("#AABBCC"),
    )

    proxy.pick_color()

    assert proxy.get_pending_color() == "#AABBCC"
    assert w["color_value_entry"].text() == "#AABBCC"


def test_color_dialog_proxy_notice(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog()
    proxy = w["ColorDialog"]

    proxy.set_notice("Color: invalid background color")
    assert w["color_notice_label"].text() == "Color: invalid background color"

    proxy.clear_notice()
    assert w["color_notice_label"].text() == ""


def test_color_dialog_proxy_show_hide(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_color_dialog

    w = build_color_dialog()
    w["ColorDialog"].show()
    w["ColorDialog"].hide()


# ===========================================================================
# About dialog
# ===========================================================================


def test_about_dialog_required_widgets(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_about_dialog

    w = build_about_dialog()

    expected = {
        "about_window",
        "about_title_label",
        "about_version_label",
        "about_description_label",
        "about_credits_label",
        "about_license_label",
        "about_close_btn",
        "about_dialog_proxy",
        "AboutDialog",
    }
    assert expected <= set(w)


def test_about_dialog_initial_labels(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_about_dialog

    w = build_about_dialog()

    assert w["about_title_label"].text() == "Harite"
    assert w["about_version_label"].text() == "Version: -"
    assert w["about_credits_label"].text() == "Credits: -"
    assert w["about_license_label"].text() == "License: -"


def test_about_dialog_proxy_set_content(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_about_dialog

    w = build_about_dialog()
    proxy = w["AboutDialog"]

    proxy.set_content({
        "app_name": "Harite Test",
        "version": "1.2.3",
        "description": "A wallpaper tool",
        "credits": "Contributors",
        "license_name": "MIT",
    })

    assert w["about_title_label"].text() == "Harite Test"
    assert w["about_version_label"].text() == "1.2.3"
    assert w["about_description_label"].text() == "A wallpaper tool"
    assert w["about_credits_label"].text() == "Contributors"
    assert w["about_license_label"].text() == "MIT"


def test_about_dialog_proxy_partial_set_content(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_about_dialog

    w = build_about_dialog()
    proxy = w["AboutDialog"]

    proxy.set_content({"version": "2.0.0"})
    assert w["about_version_label"].text() == "2.0.0"
    assert w["about_title_label"].text() == "Harite"  # unchanged


def test_about_dialog_proxy_show_hide(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_about_dialog

    w = build_about_dialog()
    w["AboutDialog"].show()
    w["AboutDialog"].hide()


# ===========================================================================
# File dialog proxies
# ===========================================================================


def test_file_dialog_proxies_required_keys(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_file_dialog_proxies

    w = build_file_dialog_proxies()

    expected = {
        "open_dialog_proxy",
        "ImgOpenDialog",
        "srcdir_dialog_proxy",
        "SrcdirDialog",
        "save_path_dialog_proxy",
        "SavePathDialog",
    }
    assert expected <= set(w)


def test_file_dialog_proxy_aliases_same_objects(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_file_dialog_proxies

    w = build_file_dialog_proxies()

    assert w["ImgOpenDialog"] is w["open_dialog_proxy"]
    assert w["SrcdirDialog"] is w["srcdir_dialog_proxy"]
    assert w["SavePathDialog"] is w["save_path_dialog_proxy"]


def test_file_dialog_proxies_have_open_method(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_file_dialog_proxies

    w = build_file_dialog_proxies()

    assert callable(w["open_dialog_proxy"].open)
    assert callable(w["srcdir_dialog_proxy"].open)
    assert callable(w["save_path_dialog_proxy"].open)


# ===========================================================================
# build_dialogs: all keys merged
# ===========================================================================


def test_build_dialogs_merged_keys(qapp):
    from harite.gui.adapters_qt.qt_dialogs import build_dialogs

    w = build_dialogs()

    assert "SettingsDialog" in w
    assert "ColorDialog" in w
    assert "AboutDialog" in w
    assert "ImgOpenDialog" in w
    assert "SrcdirDialog" in w
    assert "SavePathDialog" in w


# ===========================================================================
# Full layout integration
# ===========================================================================


def test_full_layout_dialogs_integrated(qapp):
    """After full layout build, all dialog proxies are in backend registry."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend

    backend = load_qt_runtime_signal_backend()
    reg = backend.objects

    for key in ("SettingsDialog", "ColorDialog", "AboutDialog",
                "ImgOpenDialog", "SrcdirDialog", "SavePathDialog"):
        assert key in reg, f"Missing key: {key}"

    for key in ("prefs_window", "prefs_save_btn", "prefs_ok_btn",
                "color_window", "about_window", "about_close_btn"):
        assert key in reg, f"Missing widget: {key}"

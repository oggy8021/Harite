"""Qt widget alias registry for Harite GUI (Phase 8).

Maps GTK-style camelCase object names (used throughout gtk_runtime_*.py
sync functions and dialog handlers) to the snake_case keys that Phase 3–7
builders register in the flat widget dict.

``build_qt_object_aliases(widgets)`` should be called after the full layout
and dialogs have been built to extend the registry with all aliases.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Alias builders (same logical sections as gtk_runtime_object_registry.py)
# ---------------------------------------------------------------------------


def build_qt_object_aliases(widgets: dict[str, Any]) -> dict[str, Any]:
    """Return a dict of additional aliases that should be merged into the
    top-level widget registry."""
    result: dict[str, Any] = {}
    result.update(_main_aliases(widgets))
    result.update(_dialog_aliases(widgets))
    result.update(_tab_aliases(widgets))
    result.update(_footer_aliases(widgets))
    return result


def _main_aliases(w: dict[str, Any]) -> dict[str, Any]:
    def _get(key: str) -> Any:
        return w.get(key)

    return {
        "main_window": _get("main_window"),
        "lblTitle": _get("title"),
        "lblSubtitle": _get("subtitle"),
        "lblMainSection": _get("main_section_label"),
        "boxMainSection": _get("main_col"),
        "composeGrid": _get("compose_grid"),
        "leftDisplayCol": _get("left_display_grid"),
        "rightDisplayCol": _get("right_display_grid"),
        "inputRowL": _get("input_row_l"),
        "inputRowR": _get("input_row_r"),
        "actionClusterRow": _get("action_cluster_row"),
        "actionClusterCol": _get("optimize_group"),
        "tglUpperL": _get("tgl_upper_l"),
        "tglUpperR": _get("tgl_upper_r"),
        "tglPushLeftL": _get("tgl_push_left_l"),
        "tglPushRightL": _get("tgl_push_right_l"),
        "tglLowerL": _get("tgl_lower_l"),
        "tglPushLeftR": _get("tgl_push_left_r"),
        "tglPushRightR": _get("tgl_push_right_r"),
        "tglLowerR": _get("tgl_lower_r"),
        "btnGetImgL": _get("btn_get_img_l"),
        "btnGetImgR": _get("btn_get_img_r"),
        "lblPickState": _get("pick_state_label"),
        "entPathL": _get("input_display_l"),
        "btnClrPathL": _get("btn_clr_path_l"),
        "entPathR": _get("input_display_r"),
        "btnClrPathR": _get("btn_clr_path_r"),
        "btnSwapInputPaths": _get("btn_swap_input_paths"),
        "spnTopMargin": _get("top_margin_spin"),
        "lblTopMargin": _get("top_margin_label"),
        "spnLeftMargin": _get("left_margin_spin"),
        "lblLeftMargin": _get("left_margin_label"),
        "spnRightMargin": _get("right_margin_spin"),
        "lblRightMargin": _get("right_margin_label"),
        "spnBottomMargin": _get("bottom_margin_spin"),
        "lblBottomMargin": _get("bottom_margin_label"),
        "lblOptimizeSection": _get("optimize_section_label"),
        "boxOptimizeSection": _get("optimize_row"),
        "btnSave": _get("optimize_btn"),
        "btnOptimize": _get("optimize_modern_btn"),
        "lblOptimizeResult": _get("optimize_result"),
        "lblApplySection": _get("apply_section_label"),
        "boxApplySection": _get("apply_row"),
        "btnSetWall": _get("apply_btn"),
        "lblApplyTarget": _get("apply_target"),
        "lblPreviewSection": _get("preview_section_label"),
        "boxPreviewSection": _get("preview_group"),
        "boxPreviewImagesRow": _get("preview_images_row"),
        "imgPreviewL": _get("preview_left"),
        "imgPreviewR": _get("preview_right"),
        "lblPreviewAssignL": _get("preview_left_assignment"),
        "lblPreviewAssignR": _get("preview_right_assignment"),
        "lblPreviewResultL": _get("preview_left_result"),
        "lblPreviewResultR": _get("preview_right_result"),
        "lblPreviewState": _get("preview_state_label"),
        "lblPreviewSource": _get("preview_source_label"),
        "lblPreviewAssist": _get("preview_assist_label"),
        "radApplySingle": _get("rad_apply_single"),
        "radApplyPerMonitor": _get("rad_apply_per_monitor"),
        "lblApplyMode": _get("apply_mode_label"),
        "lblDoItPlanned": _get("do_it_plan_label"),
        "lblSaveTarget": _get("save_target_label"),
        "lblPriorityRule": _get("priority_note_label"),
        "lblStyleLegend": _get("style_legend_label"),
        "lblCurrentStateSection": _get("current_state_section_label"),
        "lblCurrentMargins": _get("current_margins_label"),
        "lblCurrentStateL": _get("current_left_label"),
        "lblCurrentStateR": _get("current_right_label"),
        "commandTabs": _get("command_tabs"),
        "btnSetting": _get("btn_setting"),
        "btnSettings": _get("btn_setting"),
        "btnSetColor": _get("btn_set_color"),
        "btnAbout": _get("btn_about"),
        "flowRow": _get("flow_row"),
        "lblFlowLegend": _get("flow_legend_label"),
    }


def _dialog_aliases(w: dict[str, Any]) -> dict[str, Any]:
    def _get(key: str) -> Any:
        return w.get(key)

    return {
        "btnSettingsApply": _get("prefs_apply_btn"),
        "btnSettingsOk": _get("prefs_ok_btn"),
        "btnSettingsSave": _get("prefs_save_btn"),
        "btnSettingsClose": _get("prefs_close_btn"),
        "btnSettingsCancel": _get("prefs_cancel_btn"),
        "lblSettingsState": _get("prefs_state_label"),
        "lblSettingsNotice": _get("prefs_notice_label"),
        "boxSettingsEditor": _get("prefs_editor_box"),
        "settingsWindow": _get("prefs_window"),
        "lblSettingsEditorTitle": _get("prefs_editor_title"),
        "entSettingsResolution": _get("prefs_resolution_entry"),
        "entSettingsScaling": _get("prefs_scaling_entry"),
        "radSettingsTwoScreenAuto": _get("prefs_two_screen_auto"),
        "radSettingsTwoScreenOn": _get("prefs_two_screen_on"),
        "radSettingsTwoScreenOff": _get("prefs_two_screen_off"),
        "entSettingsLDisplay": _get("prefs_l_display_entry"),
        "entSettingsRDisplay": _get("prefs_r_display_entry"),
        "entSettingsMargins": _get("prefs_margins_entry"),
        "entSettingsAlign": _get("prefs_align_entry"),
        "entSettingsValign": _get("prefs_valign_entry"),
        "spnSettingsQuality": _get("prefs_quality_spin"),
        "entSettingsMarginTextMode": _get("prefs_margin_text_mode_entry"),
        "entSettingsMarginText": _get("prefs_margin_text_entry"),
        "entSettingsMarginTextPosition": _get("prefs_margin_text_position_entry"),
        "spnSettingsMarginTextMaxLines": _get("prefs_margin_text_max_lines_spin"),
        "entSettingsPlugin": _get("prefs_plugin_entry"),
        "radSettingsApplySingle": _get("prefs_apply_single"),
        "radSettingsApplyPerMonitor": _get("prefs_apply_per_monitor"),
        "chkWindowsApplySpan": _get("prefs_windows_apply_span"),
        "ColorDialog": _get("ColorDialog"),
        "colorWindow": _get("color_window"),
        "entColorValue": _get("color_value_entry"),
        "lblColorState": _get("color_state_label"),
        "lblColorNotice": _get("color_notice_label"),
        "btnColorPick": _get("color_pick_btn"),
        "btnColorApply": _get("color_apply_btn"),
        "btnColorCancel": _get("color_cancel_btn"),
        "AboutDialog": _get("AboutDialog"),
        "aboutWindow": _get("about_window"),
        "lblAboutTitle": _get("about_title_label"),
        "lblAboutVersion": _get("about_version_label"),
        "lblAboutDescription": _get("about_description_label"),
        "lblAboutCredits": _get("about_credits_label"),
        "lblAboutLicense": _get("about_license_label"),
        "btnAboutClose": _get("about_close_btn"),
        "ImgOpenDialog": _get("ImgOpenDialog"),
        "SrcdirDialog": _get("SrcdirDialog"),
        "SettingsDialog": _get("SettingsDialog"),
        "SavePathDialog": _get("SavePathDialog"),
        "lblSavePathState": _get("save_path_state_label"),
    }


def _tab_aliases(w: dict[str, Any]) -> dict[str, Any]:
    def _get(key: str) -> Any:
        return w.get(key)

    return {
        "slideshowTab": _get("slideshow_tab_box"),
        "marginsTab": _get("margins_tab_box"),
        "slideshowControlsRow": _get("slideshow_controls_row"),
        "slideshowDetailRow": _get("slideshow_detail_row"),
        "marginTextTabs": _get("margin_text_tabs"),
        "marginSettingsPage": _get("margin_settings_page"),
        "marginTextPage": _get("margin_text_page"),
        "lblMarginSettingsPreview": _get("margin_settings_preview_label"),
        "lblMarginTextSection": _get("margin_text_section_label"),
        "lblMarginTextMode": _get("margin_text_mode_label"),
        "radMarginTextModeOff": _get("margin_text_mode_off"),
        "radMarginTextModeSettings": _get("margin_text_mode_settings"),
        "radMarginTextModeText": _get("margin_text_mode_text"),
        "radMarginTextModeBoth": _get("margin_text_mode_both"),
        "txtMarginText": _get("margin_text_entry"),
        "radMarginTextPositionLeftTop": _get("margin_position_left_top"),
        "radMarginTextPositionRightBottom": _get("margin_position_right_bottom"),
        "radMarginTextPositionLeftBottom": _get("margin_position_left_bottom"),
        "radMarginTextPositionRightTop": _get("margin_position_right_top"),
        "spnMarginTextMaxLines": _get("margin_text_max_lines_spin"),
        "btnOpenSrcdirL": _get("btn_open_srcdir_l"),
        "btnOpenSrcdirR": _get("btn_open_srcdir_r"),
        "btnClrSrcdirL": _get("btn_clr_srcdir_l"),
        "btnClrSrcdirR": _get("btn_clr_srcdir_r"),
        "btnSwapSlideshowSrcdirs": _get("btn_swap_slideshow_srcdirs"),
        "comboSlideshowSourceL": _get("combo_slideshow_source_l"),
        "comboSlideshowSourceR": _get("combo_slideshow_source_r"),
        "lblSlideshowSection": _get("slideshow_label"),
        "lblSlideshowTabTitle": _get("slideshow_tab_title"),
        "spnInterval": _get("interval_spin"),
        "lblInterval": _get("interval_label"),
        "lblSlideshowMode": _get("slideshow_mode_label"),
        "lblSlideshowModeHelp": _get("slideshow_mode_help_label"),
        "radSlideshowModeSequential": _get("rad_slideshow_mode_sequential"),
        "radSlideshowModeRandom": _get("rad_slideshow_mode_random"),
        "btnDaemonize": _get("btn_daemonize"),
        "btnSlideshowStart": _get("btn_daemonize"),
        "btnCancelDaemonize": _get("btn_cancel_daemonize"),
        "btnSlideshowStop": _get("btn_cancel_daemonize"),
        "lblSlideshowSourceL": _get("slideshow_source_label_l"),
        "lblSlideshowSourceR": _get("slideshow_source_label_r"),
        "lblSlideshowCodhKeyword": _get("slideshow_codh_keyword_chip"),
        "lblSlideshowCurrent": _get("slideshow_current_label"),
        "lblSlideshowOutput": _get("slideshow_output_label"),
    }


def _footer_aliases(w: dict[str, Any]) -> dict[str, Any]:
    def _get(key: str) -> Any:
        return w.get(key)

    return {
        "statusbar": _get("footer_col"),
        "lblStatus": _get("status_label"),
        "lblError": _get("error_label"),
        "lblSlideshowSummary": _get("slideshow_summary_label"),
    }

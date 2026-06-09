from __future__ import annotations

from typing import Any


SAVE_PATH_DIALOG_OBJECT_ALIASES: tuple[str, ...] = (
    "SavePathDialog",
)

SAVE_PATH_STATE_LABEL_ALIASES: tuple[str, ...] = (
    "lblSavePathState",
)

SETTINGS_DIALOG_OBJECT_ALIASES: tuple[str, ...] = (
    "SettingsDialog",
)


def build_runtime_object_aliases(widgets: dict[str, Any]) -> dict[str, Any]:
    return {
        **_build_main_runtime_object_aliases(widgets),
        **_build_dialog_runtime_object_aliases(widgets),
        **_build_tab_runtime_object_aliases(widgets),
        **_build_footer_runtime_object_aliases(widgets),
        **_build_drawer_runtime_object_aliases(widgets),
    }


def _build_drawer_runtime_object_aliases(widgets: dict[str, Any]) -> dict[str, Any]:
    """Snake_case keys used by options-drawer views and drawer_window_resize."""
    aliases: dict[str, Any] = {}
    for key in (
        "btn_margins_options_more",
        "btn_slideshow_options_more",
        "margins_options_drawer",
        "slideshow_options_drawer",
        "margins_options_revealer",
        "slideshow_options_revealer",
        "main_col",
        "slideshow_tab_box",
    ):
        widget = widgets.get(key)
        if widget is not None:
            aliases[key] = widget
    return aliases


def _build_main_runtime_object_aliases(widgets: dict[str, Any]) -> dict[str, Any]:
    return {
        "main_window": widgets["window"],
        "boxRoot": widgets["root"],
        "lblTopMargin": widgets["top_margin_label"],
        "spnTopMargin": widgets["top_margin_spin"],
        "lblLeftMargin": widgets["left_margin_label"],
        "spnLeftMargin": widgets["left_margin_spin"],
        "lblTitle": widgets["title"],
        "lblSubtitle": widgets["subtitle"],
        "lblMainSection": widgets["main_section_label"],
        "boxMainSection": widgets["main_col"],
        "composeGrid": widgets["compose_grid"],
        "leftDisplayCol": widgets["left_display_grid"],
        "rightDisplayCol": widgets["right_display_grid"],
        "inputRowL": widgets["input_row_l"],
        "inputRowR": widgets["input_row_r"],
        "actionClusterRow": widgets["action_cluster_row"],
        "actionClusterCol": widgets["optimize_group"],
        "tglUpperL": widgets["tgl_upper_l"],
        "tglUpperR": widgets["tgl_upper_r"],
        "tglPushLeftL": widgets["tgl_push_left_l"],
        "tglPushRightL": widgets["tgl_push_right_l"],
        "tglLowerL": widgets["tgl_lower_l"],
        "tglPushLeftR": widgets["tgl_push_left_r"],
        "tglPushRightR": widgets["tgl_push_right_r"],
        "tglLowerR": widgets["tgl_lower_r"],
        "btnGetImgL": widgets["btn_get_img_l"],
        "btnGetImgR": widgets["btn_get_img_r"],
        "lblPickState": widgets["pick_state_label"],
        "entPathL": widgets["input_display_l"],
        "btnClrPathL": widgets["btn_clr_path_l"],
        "entPathR": widgets["input_display_r"],
        "btnClrPathR": widgets["btn_clr_path_r"],
        "vbox5": widgets["right_margin_col"],
        "lblRightMargin": widgets["right_margin_label"],
        "spnRightMargin": widgets["right_margin_spin"],
        "hbox12": widgets["bottom_margin_row"],
        "lblBottomMargin": widgets["bottom_margin_label"],
        "spnBottomMargin": widgets["bottom_margin_spin"],
        "lblAllMargins": widgets.get("all_margins_label"),
        "spnAllMargins": widgets.get("all_margins_spin"),
        "boxOptimizeSection": widgets["optimize_group"],
        "btnSave": widgets["optimize_btn"],
        "btnOptimize": widgets["optimize_modern_btn"],
        "boxApplySection": widgets["apply_group"],
        "btnSetWall": widgets["apply_btn"],
        "boxPreviewSection": widgets["preview_group"],
        "boxPreviewImagesRow": widgets["preview_images_row"],
        "imgPreviewL": widgets["preview_left"],
        "imgPreviewR": widgets["preview_right"],
        "radApplySingle": widgets["rad_apply_single"],
        "radApplyPerMonitor": widgets["rad_apply_per_monitor"],
        "lblDoItPlanned": widgets["do_it_plan_label"],
        "lblSaveTarget": widgets["save_target_label"],
        "lblPriorityRule": widgets["priority_note_label"],
        "lblStyleLegend": widgets["style_legend_label"],
        "lblCurrentStateSection": widgets["current_state_section_label"],
        "lblCurrentMargins": widgets["current_margins_label"],
        "lblCurrentStateL": widgets["current_left_label"],
        "lblCurrentStateR": widgets["current_right_label"],
        "lblCommandSection": widgets["command_section_label"],
        "commandTabs": widgets["command_tabs"],
        "hbox14": widgets["command_bar"],
        "btnSetting": widgets["btn_setting"],
        "btnSettings": widgets["btn_setting"],
        "btnSetColor": widgets["btn_set_color"],
        "btnAbout": widgets["btn_about"],
        "flowRow": widgets["flow_row"],
        "lblFlowLegend": widgets["flow_legend_label"],
    }


def _build_dialog_runtime_object_aliases(widgets: dict[str, Any]) -> dict[str, Any]:
    return {
        "btnSettingsApply": widgets["prefs_apply_btn"],
        "btnSettingsOk": widgets["prefs_ok_btn"],
        "btnSettingsSave": widgets["prefs_save_btn"],
        "btnSettingsClose": widgets["prefs_close_btn"],
        "btnSettingsCancel": widgets["prefs_cancel_btn"],
        "lblSettingsState": widgets["prefs_state_label"],
        "lblSettingsNotice": widgets["prefs_notice_label"],
        "boxSettingsEditor": widgets["prefs_editor_box"],
        "settingsWindow": widgets["prefs_window"],
        "lblSettingsEditorTitle": widgets["prefs_editor_title"],
        "entSettingsResolution": widgets["prefs_resolution_entry"],
        "entSettingsScaling": widgets["prefs_scaling_entry"],
        "radSettingsTwoScreenAuto": widgets["prefs_two_screen_auto"],
        "radSettingsTwoScreenOn": widgets["prefs_two_screen_on"],
        "radSettingsTwoScreenOff": widgets["prefs_two_screen_off"],
        "entSettingsLDisplay": widgets["prefs_l_display_entry"],
        "entSettingsRDisplay": widgets["prefs_r_display_entry"],
        "entSettingsMargins": widgets["prefs_margins_entry"],
        "entSettingsAlign": widgets["prefs_align_entry"],
        "entSettingsValign": widgets["prefs_valign_entry"],
        "spnSettingsQuality": widgets["prefs_quality_spin"],
        "entSettingsMarginTextMode": widgets["prefs_margin_text_mode_entry"],
        "entSettingsMarginText": widgets["prefs_margin_text_entry"],
        "entSettingsMarginTextPosition": widgets["prefs_margin_text_position_entry"],
        "spnSettingsMarginTextMaxLines": widgets["prefs_margin_text_max_lines_spin"],
        "entSettingsPlugin": widgets["prefs_plugin_entry"],
        "radSettingsApplySingle": widgets["prefs_apply_single"],
        "radSettingsApplyPerMonitor": widgets["prefs_apply_per_monitor"],
        "chkWindowsApplySpan": widgets["prefs_windows_apply_span"],
        "ColorDialog": widgets["color_dialog_proxy"],
        "colorWindow": widgets["color_window"],
        "entColorValue": widgets["color_value_entry"],
        "lblColorState": widgets["color_state_label"],
        "lblColorNotice": widgets["color_notice_label"],
        "btnColorPick": widgets["color_pick_btn"],
        "btnColorApply": widgets["color_apply_btn"],
        "btnColorCancel": widgets["color_cancel_btn"],
        "AboutDialog": widgets["about_dialog_proxy"],
        "aboutWindow": widgets["about_window"],
        "lblAboutTitle": widgets["about_title_label"],
        "lblAboutVersion": widgets["about_version_label"],
        "lblAboutDescription": widgets["about_description_label"],
        "lblAboutCredits": widgets["about_credits_label"],
        "lblAboutLicense": widgets["about_license_label"],
        "btnAboutClose": widgets["about_close_btn"],
        "ImgOpenDialog": widgets["open_dialog_proxy"],
        "SrcdirDialog": widgets["srcdir_dialog_proxy"],
        **{object_name: widgets["settings_dialog_proxy"] for object_name in SETTINGS_DIALOG_OBJECT_ALIASES},
        **{object_name: widgets["save_path_state_label"] for object_name in SAVE_PATH_STATE_LABEL_ALIASES},
        **{object_name: widgets["save_path_dialog_proxy"] for object_name in SAVE_PATH_DIALOG_OBJECT_ALIASES},
    }


def _build_tab_runtime_object_aliases(widgets: dict[str, Any]) -> dict[str, Any]:
    return {
        "slideshowTab": widgets["slideshow_tab_box"],
        "btnMarginsOptionsMore": widgets["btn_margins_options_more"],
        "marginsOptionsDrawer": widgets["margins_options_drawer"],
        "slideshowControlsRow": widgets["slideshow_controls_row"],
        "slideshowDetailRow": widgets["slideshow_detail_row"],
        "marginTextTabs": widgets["margin_text_tabs"],
        "marginSettingsPage": widgets["margin_settings_page"],
        "marginTextPage": widgets["margin_text_page"],
        "lblMarginSettingsPreview": widgets["margin_settings_preview_label"],
        "lblMarginTextSection": widgets["margin_text_section_label"],
        "lblMarginTextMode": widgets["margin_text_mode_label"],
        "radMarginTextModeOff": widgets["margin_text_mode_off"],
        "radMarginTextModeSettings": widgets["margin_text_mode_settings"],
        "radMarginTextModeText": widgets["margin_text_mode_text"],
        "radMarginTextModeBoth": widgets["margin_text_mode_both"],
        "txtMarginText": widgets["margin_text_entry"],
        "radMarginTextPositionLeftTop": widgets["margin_position_left_top"],
        "radMarginTextPositionRightBottom": widgets["margin_position_right_bottom"],
        "radMarginTextPositionLeftBottom": widgets["margin_position_left_bottom"],
        "radMarginTextPositionRightTop": widgets["margin_position_right_top"],
        "spnMarginTextMaxLines": widgets["margin_text_max_lines_spin"],
        "btnOpenSrcdirL": widgets["btn_open_srcdir_l"],
        "btnOpenSrcdirR": widgets["btn_open_srcdir_r"],
        "lblSlideshowSection": widgets["slideshow_label"],
        "lblSlideshowTabTitle": widgets["slideshow_tab_title"],
        "spnInterval": widgets["interval_spin"],
        "lblInterval": widgets["interval_label"],
        "lblSlideshowMode": widgets["slideshow_mode_label"],
        "lblSlideshowModeHelp": widgets["slideshow_mode_help_label"],
        "radSlideshowModeSequential": widgets["rad_slideshow_mode_sequential"],
        "radSlideshowModeRandom": widgets["rad_slideshow_mode_random"],
        "btnDaemonize": widgets["btn_daemonize"],
        "btnSlideshowStart": widgets["btn_daemonize"],
        "btnCancelDaemonize": widgets["btn_cancel_daemonize"],
        "btnSlideshowStop": widgets["btn_cancel_daemonize"],
        "lblSlideshowSourceL": widgets["slideshow_source_label_l"],
        "lblSlideshowSourceR": widgets["slideshow_source_label_r"],
        "lblSlideshowCurrent": widgets["slideshow_current_label"],
        "lblSlideshowOutput": widgets["slideshow_output_label"],
    }


def _build_footer_runtime_object_aliases(widgets: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusbar": widgets["footer_col"],
        "lblStatus": widgets["status_label"],
        "lblError": widgets["error_label"],
        "lblSlideshowSummary": widgets["slideshow_summary_label"],
    }
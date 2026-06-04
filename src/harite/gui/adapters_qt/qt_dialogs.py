"""Qt dialog builders and proxy classes for Harite GUI (Phase 6).

Three modal dialog windows (Settings / Color / About) plus three file-dialog
proxies (ImgOpen / Srcdir / SavePath).

All proxy classes expose the same duck-typed API that
``gtk_runtime_settings_dialogs.py`` and friends call through
``backend._objects.get("SettingsDialog")`` etc.
"""

from __future__ import annotations

from typing import Any


from harite.gui.resource_access import set_qt_button_icon as _set_button_icon


# ===========================================================================
# Settings dialog
# ===========================================================================


class QtSettingsDialogProxy:
    """Wraps a QDialog and provides the SettingsDialog duck-type API.

    ``get_settings()`` / ``set_settings()`` maintain an internal dict that
    ``sync_settings_widgets_from_dialog`` and friends read/write via the
    backend's ``_set_entry_text`` helpers.  The form widgets themselves hold
    the user-editable view; the internal dict is the serialised snapshot.
    """

    def __init__(self, dialog: Any) -> None:
        self._dialog = dialog
        self._settings: dict[str, object] = {}

    # --- Protocol API (called by gtk_runtime_settings_dialogs) ---

    def get_settings(self) -> dict[str, object]:
        return dict(self._settings)

    def set_settings(self, settings: dict[str, object]) -> None:
        self._settings = dict(settings)

    def get_export_path(self) -> str:
        try:
            from harite.settings_file import resolve_default_settings_path

            return str(resolve_default_settings_path())
        except Exception:
            return ""

    # --- Visibility helpers ---

    def show(self) -> None:
        self._dialog.show()

    def hide(self) -> None:
        self._dialog.hide()


def build_settings_dialog(parent: Any = None) -> dict[str, Any]:
    """Build the Settings QDialog and return the widget registry."""
    from PyQt6.QtWidgets import (
        QButtonGroup,
        QCheckBox,
        QDialog,
        QDialogButtonBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QRadioButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

    prefs_window = QDialog(parent)
    prefs_window.setWindowTitle("Settings")
    prefs_window.resize(520, 420)
    prefs_window.setModal(False)

    outer = QVBoxLayout(prefs_window)
    outer.setSpacing(6)

    # -- header row --
    header_row = QWidget()
    header_layout = QHBoxLayout(header_row)
    header_layout.setContentsMargins(0, 0, 0, 0)
    prefs_editor_title = QLabel("Settings")
    prefs_save_btn = QPushButton("Save Settings")
    _set_button_icon(prefs_save_btn, "icons", "lucide", "save.svg")
    header_layout.addWidget(prefs_editor_title)
    header_layout.addStretch()
    header_layout.addWidget(prefs_save_btn)
    outer.addWidget(header_row)

    prefs_editor_box = QWidget()
    editor_layout = QVBoxLayout(prefs_editor_box)
    editor_layout.setContentsMargins(0, 0, 0, 0)
    editor_layout.setSpacing(6)
    outer.addWidget(prefs_editor_box, stretch=1)

    # -- form rows (visible) --
    def _add_row(label_text: str, *widgets: Any) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        row_layout.addWidget(QLabel(label_text))
        for w in widgets:
            row_layout.addWidget(w, stretch=1)
        editor_layout.addWidget(row)

    prefs_resolution_entry = QLineEdit()
    prefs_scaling_entry = QLineEdit()
    prefs_plugin_entry = QLineEdit()

    prefs_apply_single = QRadioButton("Apply Default")
    prefs_apply_per_monitor = QRadioButton("Apply Auto-split")
    prefs_apply_single.setChecked(True)
    apply_mode_group = QButtonGroup(prefs_window)
    apply_mode_group.addButton(prefs_apply_single)
    apply_mode_group.addButton(prefs_apply_per_monitor)
    apply_mode_shell = QWidget()
    apply_mode_layout = QHBoxLayout(apply_mode_shell)
    apply_mode_layout.setContentsMargins(0, 0, 0, 0)
    apply_mode_layout.addWidget(prefs_apply_single)
    apply_mode_layout.addWidget(prefs_apply_per_monitor)
    apply_mode_layout.addStretch()

    _add_row("Resolution", prefs_resolution_entry)
    _add_row("Scaling", prefs_scaling_entry)
    _add_row("Plugin", prefs_plugin_entry)
    _add_row("Apply", apply_mode_shell)

    from harite.apply_surface import is_windows_host

    prefs_windows_apply_span = QCheckBox("Apply with Span when using Span mode")
    if is_windows_host():
        _add_row("Windows", prefs_windows_apply_span)
    else:
        prefs_windows_apply_span.setVisible(False)

    # -- action buttons --
    prefs_ok_btn = QPushButton("OK")
    prefs_cancel_btn = QPushButton("Cancel")
    actions = QWidget()
    actions_layout = QHBoxLayout(actions)
    actions_layout.setContentsMargins(0, 0, 0, 0)
    actions_layout.addWidget(prefs_cancel_btn)
    actions_layout.addWidget(prefs_ok_btn)
    editor_layout.addWidget(actions)

    # -- separator + state labels --
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    prefs_state_label = QLabel("Settings: current values")
    prefs_notice_label = QLabel("")

    editor_layout.addWidget(sep)
    editor_layout.addWidget(prefs_state_label)
    editor_layout.addWidget(prefs_notice_label)
    editor_layout.addStretch()

    # -- hidden extra widgets (registered for signal wiring, not visible) --
    prefs_two_screen_auto = QRadioButton("TwoScreen Auto")
    prefs_two_screen_on = QRadioButton("TwoScreen On")
    prefs_two_screen_off = QRadioButton("TwoScreen Off")
    prefs_two_screen_off.setChecked(True)
    two_screen_group = QButtonGroup(prefs_window)
    two_screen_group.addButton(prefs_two_screen_auto)
    two_screen_group.addButton(prefs_two_screen_on)
    two_screen_group.addButton(prefs_two_screen_off)
    for w in (prefs_two_screen_auto, prefs_two_screen_on, prefs_two_screen_off):
        w.setVisible(False)

    prefs_l_display_entry = QLineEdit()
    prefs_r_display_entry = QLineEdit()
    prefs_margins_entry = QLineEdit()
    prefs_align_entry = QLineEdit()
    prefs_valign_entry = QLineEdit()
    prefs_margin_text_mode_entry = QLineEdit()
    prefs_margin_text_entry = QLineEdit()
    prefs_margin_text_position_entry = QLineEdit()

    for w in (
        prefs_l_display_entry,
        prefs_r_display_entry,
        prefs_margins_entry,
        prefs_align_entry,
        prefs_valign_entry,
        prefs_margin_text_mode_entry,
        prefs_margin_text_entry,
        prefs_margin_text_position_entry,
    ):
        w.setVisible(False)

    prefs_quality_spin = QSpinBox()
    prefs_quality_spin.setMinimum(1)
    prefs_quality_spin.setMaximum(100)
    prefs_quality_spin.setSingleStep(1)
    prefs_quality_spin.setValue(90)
    prefs_quality_spin.setVisible(False)

    prefs_margin_text_max_lines_spin = QSpinBox()
    prefs_margin_text_max_lines_spin.setMinimum(1)
    prefs_margin_text_max_lines_spin.setMaximum(20)
    prefs_margin_text_max_lines_spin.setSingleStep(1)
    prefs_margin_text_max_lines_spin.setValue(3)
    prefs_margin_text_max_lines_spin.setVisible(False)

    proxy = QtSettingsDialogProxy(prefs_window)

    return {
        "prefs_window": prefs_window,
        "prefs_apply_btn": prefs_ok_btn,
        "prefs_load_btn": None,
        "prefs_save_btn": prefs_save_btn,
        "prefs_close_btn": prefs_cancel_btn,
        "prefs_ok_btn": prefs_ok_btn,
        "prefs_cancel_btn": prefs_cancel_btn,
        "prefs_state_label": prefs_state_label,
        "prefs_notice_label": prefs_notice_label,
        "prefs_notice_separator": sep,
        "prefs_editor_box": prefs_editor_box,
        "prefs_header_row": header_row,
        "prefs_editor_title": prefs_editor_title,
        "prefs_resolution_entry": prefs_resolution_entry,
        "prefs_scaling_entry": prefs_scaling_entry,
        "prefs_two_screen_auto": prefs_two_screen_auto,
        "prefs_two_screen_on": prefs_two_screen_on,
        "prefs_two_screen_off": prefs_two_screen_off,
        "prefs_l_display_entry": prefs_l_display_entry,
        "prefs_r_display_entry": prefs_r_display_entry,
        "prefs_margins_entry": prefs_margins_entry,
        "prefs_align_entry": prefs_align_entry,
        "prefs_valign_entry": prefs_valign_entry,
        "prefs_quality_spin": prefs_quality_spin,
        "prefs_margin_text_mode_entry": prefs_margin_text_mode_entry,
        "prefs_margin_text_entry": prefs_margin_text_entry,
        "prefs_margin_text_position_entry": prefs_margin_text_position_entry,
        "prefs_margin_text_max_lines_spin": prefs_margin_text_max_lines_spin,
        "prefs_plugin_entry": prefs_plugin_entry,
        "prefs_apply_single": prefs_apply_single,
        "prefs_apply_per_monitor": prefs_apply_per_monitor,
        "prefs_windows_apply_span": prefs_windows_apply_span,
        "prefs_import_path_entry": None,
        "prefs_export_path_entry": None,
        "settings_dialog_proxy": proxy,
        "SettingsDialog": proxy,
    }


# ===========================================================================
# Color dialog
# ===========================================================================


class QtColorDialogProxy:
    """Wraps a QDialog (manual color picker) and provides the ColorDialog API.

    ``open_dialog()`` opens a native ``QColorDialog`` for color selection and
    stores the picked color as ``pending_color``.  The caller must then call
    ``get_pending_color()`` and apply it via the signal handler.
    """

    def __init__(self, dialog: Any, *, default_color: str = "#000000") -> None:
        self._dialog = dialog
        self._color = default_color
        self._pending_color = default_color
        self._notice_label: Any = None

    def attach_notice_label(self, label: Any) -> None:
        self._notice_label = label

    # --- Protocol API ---

    def get_color(self) -> str:
        return self._color

    def set_color(self, hex_color: str) -> None:
        self._color = hex_color
        self._pending_color = hex_color
        try:
            entry = self._dialog.findChild(
                __import__("PyQt6.QtWidgets", fromlist=["QLineEdit"]).QLineEdit
            )
            if entry is not None:
                entry.setText(hex_color)
        except Exception:
            pass

    def get_pending_color(self) -> str:
        return self._pending_color

    def open_dialog(self) -> None:
        """Open native QColorDialog; sets pending_color on accept."""
        try:
            from PyQt6.QtGui import QColor
            from PyQt6.QtWidgets import QColorDialog

            initial = QColor(self._color)
            parent = getattr(self._dialog, "parent", lambda: None)()
            color = QColorDialog.getColor(initial, parent, "Background Color")
            if color.isValid():
                self._pending_color = color.name().upper()
                try:
                    from PyQt6.QtWidgets import QLineEdit

                    entry = self._dialog.findChild(QLineEdit)
                    if entry is not None:
                        entry.setText(self._pending_color)
                except Exception:
                    pass
        except Exception:
            pass

    def clear_notice(self) -> None:
        if self._notice_label is not None:
            self._notice_label.setText("")

    def set_notice(self, message: str) -> None:
        if self._notice_label is not None:
            self._notice_label.setText(message)

    def show(self) -> None:
        self._dialog.show()

    def hide(self) -> None:
        self._dialog.hide()


def build_color_dialog(parent: Any = None, *, default_color_hex: str = "#000000") -> dict[str, Any]:
    """Build the Color QDialog and return the widget registry."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QVBoxLayout,
    )

    color_window = QDialog(parent)
    color_window.setWindowTitle("Background Color")
    color_window.resize(420, 360)
    color_window.setModal(False)

    editor_box = QVBoxLayout(color_window)
    editor_box.setSpacing(6)

    color_editor_title = QLabel("Background color (#RRGGBB)")
    color_editor_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
    editor_box.addWidget(color_editor_title)

    color_picker_host = QFrame()
    color_picker_host.setFrameShape(QFrame.Shape.StyledPanel)
    color_picker_host.setMinimumHeight(120)
    editor_box.addWidget(color_picker_host, stretch=1)

    color_value_entry = QLineEdit(default_color_hex)
    editor_box.addWidget(color_value_entry)

    color_pick_btn = QPushButton("Pick Color")
    color_apply_btn = QPushButton("Color Apply")
    color_cancel_btn = QPushButton("Color Cancel")
    actions = QFrame()
    actions_layout = QHBoxLayout(actions)
    actions_layout.setContentsMargins(0, 0, 0, 0)
    actions_layout.addWidget(color_pick_btn)
    actions_layout.addWidget(color_apply_btn)
    actions_layout.addWidget(color_cancel_btn)
    editor_box.addWidget(actions)

    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    color_state_label = QLabel(f"Color: {default_color_hex}")
    color_notice_label = QLabel("")
    editor_box.addWidget(sep)
    editor_box.addWidget(color_state_label)
    editor_box.addWidget(color_notice_label)

    proxy = QtColorDialogProxy(color_window, default_color=default_color_hex)
    proxy.attach_notice_label(color_notice_label)

    return {
        "color_window": color_window,
        "color_value_entry": color_value_entry,
        "color_state_label": color_state_label,
        "color_notice_label": color_notice_label,
        "color_notice_separator": sep,
        "color_picker_host": color_picker_host,
        "color_pick_btn": color_pick_btn,
        "color_apply_btn": color_apply_btn,
        "color_cancel_btn": color_cancel_btn,
        "color_dialog_proxy": proxy,
        "ColorDialog": proxy,
    }


# ===========================================================================
# About dialog
# ===========================================================================


class QtAboutDialogProxy:
    """Wraps the About QDialog and exposes ``set_content`` / show / hide."""

    def __init__(
        self,
        dialog: Any,
        labels: dict[str, Any],
    ) -> None:
        self._dialog = dialog
        self._labels = labels  # {field_name: QLabel}

    def set_content(self, content: dict[str, object]) -> None:
        mapping = {
            "app_name": "about_title_label",
            "version": "about_version_label",
            "description": "about_description_label",
            "credits": "about_credits_label",
            "license_name": "about_license_label",
        }
        for field, widget_key in mapping.items():
            value = content.get(field)
            lbl = self._labels.get(widget_key)
            if lbl is not None and value is not None:
                lbl.setText(str(value))

    def show(self) -> None:
        self._dialog.show()

    def hide(self) -> None:
        self._dialog.hide()


def build_about_dialog(parent: Any = None) -> dict[str, Any]:
    """Build the About QDialog and return the widget registry."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
    )

    about_window = QDialog(parent)
    about_window.setWindowTitle("About Harite")
    about_window.resize(420, 320)
    about_window.setModal(False)

    shell_layout = QVBoxLayout(about_window)
    shell_layout.setSpacing(6)
    shell_layout.addStretch()

    content_box = QVBoxLayout()
    content_box.setSpacing(6)

    # App icon (best-effort)
    try:
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtWidgets import QLabel as _QLabel

        from harite.gui.resource_access import gui_resource_path

        with gui_resource_path("icons", "product", "harite_app.svg") as p:
            pm = QPixmap(str(p)).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
            icon_lbl = _QLabel()
            icon_lbl.setPixmap(pm)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            content_box.addWidget(icon_lbl)
    except Exception:
        pass

    def _centered(text: str) -> Any:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        return lbl

    about_title_label = _centered("Harite")
    about_version_label = _centered("Version: -")
    about_description_label = _centered("")
    about_credits_label = _centered("Credits: -")
    about_license_label = _centered("License: -")

    for lbl in (
        about_title_label,
        about_version_label,
        about_description_label,
        about_credits_label,
        about_license_label,
    ):
        content_box.addWidget(lbl)

    about_close_btn = QPushButton("About Close")
    close_row = QHBoxLayout()
    close_row.addStretch()
    close_row.addWidget(about_close_btn)
    close_row.addStretch()
    content_box.addLayout(close_row)

    shell_layout.addLayout(content_box)
    shell_layout.addStretch()

    labels = {
        "about_title_label": about_title_label,
        "about_version_label": about_version_label,
        "about_description_label": about_description_label,
        "about_credits_label": about_credits_label,
        "about_license_label": about_license_label,
    }
    proxy = QtAboutDialogProxy(about_window, labels)

    return {
        "about_window": about_window,
        "about_title_label": about_title_label,
        "about_version_label": about_version_label,
        "about_description_label": about_description_label,
        "about_credits_label": about_credits_label,
        "about_license_label": about_license_label,
        "about_close_btn": about_close_btn,
        "about_dialog_proxy": proxy,
        "AboutDialog": proxy,
    }


# ===========================================================================
# File dialog proxies
# ===========================================================================


class QtFileOpenDialogProxy:
    """Single-call QFileDialog.getOpenFileName wrapper for image files."""

    def __init__(self, parent: Any = None) -> None:
        self._parent = parent

    def open(self, *, title: str = "Open Image", callback: Any = None) -> str | None:
        try:
            from PyQt6.QtWidgets import QFileDialog

            path, _ = QFileDialog.getOpenFileName(
                self._parent,
                title,
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.webp);;All files (*)",
            )
            if path and callback is not None:
                callback(path)
            return path or None
        except Exception:
            return None


class QtSrcdirDialogProxy:
    """Single-call QFileDialog.getExistingDirectory wrapper for source dirs."""

    def __init__(self, parent: Any = None) -> None:
        self._parent = parent

    def open(self, *, title: str = "Select Source Directory", callback: Any = None) -> str | None:
        try:
            from PyQt6.QtWidgets import QFileDialog

            path = QFileDialog.getExistingDirectory(self._parent, title, "")
            if path and callback is not None:
                callback(path)
            return path or None
        except Exception:
            return None


class QtSavePathDialogProxy:
    """Single-call QFileDialog.getSaveFileName wrapper for export destination."""

    def __init__(self, parent: Any = None) -> None:
        self._parent = parent

    def open(self, *, title: str = "Export Image", callback: Any = None) -> str | None:
        try:
            from PyQt6.QtWidgets import QFileDialog

            path, _ = QFileDialog.getSaveFileName(
                self._parent,
                title,
                "",
                "JPEG (*.jpg);;PNG (*.png);;All files (*)",
            )
            if path and callback is not None:
                callback(path)
            return path or None
        except Exception:
            return None


def build_file_dialog_proxies(parent: Any = None) -> dict[str, Any]:
    """Build the three file-dialog proxy objects."""
    open_proxy = QtFileOpenDialogProxy(parent)
    srcdir_proxy = QtSrcdirDialogProxy(parent)
    save_proxy = QtSavePathDialogProxy(parent)
    return {
        "open_dialog_proxy": open_proxy,
        "ImgOpenDialog": open_proxy,
        "srcdir_dialog_proxy": srcdir_proxy,
        "SrcdirDialog": srcdir_proxy,
        "save_path_dialog_proxy": save_proxy,
        "SavePathDialog": save_proxy,
    }


# ===========================================================================
# Top-level builder
# ===========================================================================


def build_dialogs(parent: Any = None) -> dict[str, Any]:
    """Build all dialogs and return a merged widget registry.

    ``parent`` should be the main QMainWindow so dialogs are positioned
    relative to it.
    """
    from harite.core import DEFAULT_BACKGROUND_COLOR_HEX

    result: dict[str, Any] = {}
    result.update(build_settings_dialog(parent))
    result.update(build_color_dialog(parent, default_color_hex=DEFAULT_BACKGROUND_COLOR_HEX))
    result.update(build_about_dialog(parent))
    result.update(build_file_dialog_proxies(parent))
    return result

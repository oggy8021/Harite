"""Tests for qt_widget_helpers.py (Phase 8)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PyQt6.QtWidgets")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _FakeBackend:
    """Minimal backend stub with a widget registry."""

    def __init__(self) -> None:
        self._objects: dict = {}


@pytest.fixture
def backend(qapp):
    return _FakeBackend()


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------


def test_qt_widget_helpers_importable():
    from harite.gui.adapters_qt import qt_widget_helpers  # noqa: F401


# ---------------------------------------------------------------------------
# set_label_text / set_status / set_error / set_feedback
# ---------------------------------------------------------------------------


def test_set_label_text_updates_qlabel(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_label_text

    lbl = QLabel("")
    backend._objects["myLabel"] = lbl
    set_label_text(backend, "myLabel", "hello")
    assert lbl.text() == "hello"


def test_set_label_text_noop_on_missing(qapp, backend):
    from harite.gui.adapters_qt.qt_widget_helpers import set_label_text

    set_label_text(backend, "nonexistent", "hi")  # must not raise


def test_set_status_updates_lblStatus(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_status

    lbl = QLabel("")
    backend._objects["lblStatus"] = lbl
    set_status(backend, "state-ok")
    assert lbl.text() == "state-ok"


def test_set_error_updates_lblError(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_error
    from harite.gui.views.footer_feedback import FOOTER_ERROR_ACTIVE_COLOR

    lbl = QLabel("")
    lbl.setObjectName("errorLabel")
    backend._objects["lblError"] = lbl
    set_error(backend, "Error: boom")
    assert lbl.text() == "Error: boom"
    assert lbl.property("hasError") == "true"
    assert FOOTER_ERROR_ACTIVE_COLOR in lbl.styleSheet()
    assert "font-weight: bold" in lbl.styleSheet()


def test_set_error_sync_feedback_input_required_style(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_feedback
    from harite.gui.views.footer_feedback import FOOTER_ERROR_ACTIVE_COLOR

    status = QLabel()
    error = QLabel()
    error.setObjectName("errorLabel")
    backend._objects["lblStatus"] = status
    backend._objects["lblError"] = error

    set_feedback(
        backend,
        phase="Input",
        state="input is required",
        error="input is required",
        status_level="error",
    )

    assert error.text() == "Error: input is required"
    assert error.property("hasError") == "true"
    assert FOOTER_ERROR_ACTIVE_COLOR in error.styleSheet()


def test_set_error_clears_has_error_property(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_error

    lbl = QLabel("")
    lbl.setObjectName("errorLabel")
    backend._objects["lblError"] = lbl
    set_error(backend, "Error: boom")
    set_error(backend, None)
    assert lbl.property("hasError") == "false"


def test_set_error_clears_on_none(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_error

    lbl = QLabel("previous")
    backend._objects["lblError"] = lbl
    set_error(backend, None)
    assert lbl.text() == "Error: none"


def test_set_feedback_sets_status_and_error(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import set_feedback

    status = QLabel()
    error = QLabel()
    backend._objects["lblStatus"] = status
    backend._objects["lblError"] = error
    set_feedback(backend, phase="Test", state="done", error="oops")
    assert status.text() == "Status: ready"
    assert error.text() == "Error: oops"


# ---------------------------------------------------------------------------
# set_entry_text / read_entry_text
# ---------------------------------------------------------------------------


def test_set_entry_text_qlineedit(qapp, backend):
    from PyQt6.QtWidgets import QLineEdit

    from harite.gui.adapters_qt.qt_widget_helpers import set_entry_text

    entry = QLineEdit()
    backend._objects["ent"] = entry
    set_entry_text(backend, "ent", "path/to/file")
    assert entry.text() == "path/to/file"


def test_set_entry_text_qplaintextedit(qapp, backend):
    from PyQt6.QtWidgets import QPlainTextEdit

    from harite.gui.adapters_qt.qt_widget_helpers import set_entry_text

    pte = QPlainTextEdit()
    backend._objects["txt"] = pte
    set_entry_text(backend, "txt", "hello\nworld")
    assert pte.toPlainText() == "hello\nworld"


def test_read_entry_text_qlineedit(qapp, backend):
    from PyQt6.QtWidgets import QLineEdit

    from harite.gui.adapters_qt.qt_widget_helpers import read_entry_text

    entry = QLineEdit()
    entry.setText("abc")
    backend._objects["e"] = entry
    assert read_entry_text(backend, "e") == "abc"


def test_read_entry_text_missing_returns_empty(qapp, backend):
    from harite.gui.adapters_qt.qt_widget_helpers import read_entry_text

    assert read_entry_text(backend, "nope") == ""


# ---------------------------------------------------------------------------
# set_spin_value / read_spin_int
# ---------------------------------------------------------------------------


def test_set_spin_value_and_read(qapp, backend):
    from PyQt6.QtWidgets import QSpinBox

    from harite.gui.adapters_qt.qt_widget_helpers import read_spin_int, set_spin_value

    spin = QSpinBox()
    spin.setRange(0, 9999)
    backend._objects["spn"] = spin
    set_spin_value(backend, "spn", 42)
    assert read_spin_int(backend, "spn") == 42


def test_read_spin_int_missing_returns_zero(qapp, backend):
    from harite.gui.adapters_qt.qt_widget_helpers import read_spin_int

    assert read_spin_int(backend, "missing") == 0


# ---------------------------------------------------------------------------
# set_button_enabled / set_widget_enabled
# ---------------------------------------------------------------------------


def test_set_button_enabled(qapp, backend):
    from PyQt6.QtWidgets import QPushButton

    from harite.gui.adapters_qt.qt_widget_helpers import set_button_enabled

    btn = QPushButton("x")
    backend._objects["btn"] = btn
    set_button_enabled(backend, "btn", False)
    assert not btn.isEnabled()
    set_button_enabled(backend, "btn", True)
    assert btn.isEnabled()


# ---------------------------------------------------------------------------
# set_toggle_active / is_toggle_active
# ---------------------------------------------------------------------------


def test_set_toggle_active_qcheckbox(qapp, backend):
    from PyQt6.QtWidgets import QCheckBox

    from harite.gui.adapters_qt.qt_widget_helpers import is_toggle_active, set_toggle_active

    cb = QCheckBox()
    backend._objects["chk"] = cb
    assert not is_toggle_active(backend, "chk")
    set_toggle_active(backend, "chk", True)
    assert is_toggle_active(backend, "chk")


def test_is_toggle_active_missing_returns_false(qapp, backend):
    from harite.gui.adapters_qt.qt_widget_helpers import is_toggle_active

    assert is_toggle_active(backend, "gone") is False


# ---------------------------------------------------------------------------
# set_notebook_page
# ---------------------------------------------------------------------------


def test_set_notebook_page(qapp, backend):
    from PyQt6.QtWidgets import QTabWidget, QWidget

    from harite.gui.adapters_qt.qt_widget_helpers import set_notebook_page

    tabs = QTabWidget()
    tabs.addTab(QWidget(), "A")
    tabs.addTab(QWidget(), "B")
    tabs.addTab(QWidget(), "C")
    backend._objects["tabs"] = tabs
    set_notebook_page(backend, "tabs", 2)
    assert tabs.currentIndex() == 2


# ---------------------------------------------------------------------------
# format_input_display
# ---------------------------------------------------------------------------


def test_format_input_display_short():
    from harite.gui.adapters_qt.qt_widget_helpers import format_input_display

    assert format_input_display("abc") == "abc"


def test_format_input_display_long():
    from harite.gui.adapters_qt.qt_widget_helpers import format_input_display

    long_path = "/a/" + "b" * 80
    result = format_input_display(long_path)
    assert result.startswith("…")
    assert len(result) <= 61


def test_format_input_display_empty():
    from harite.gui.adapters_qt.qt_widget_helpers import format_input_display

    assert format_input_display("") == ""


# ---------------------------------------------------------------------------
# refresh_slideshow_source_labels
# ---------------------------------------------------------------------------


def test_format_slideshow_output_label_text_truncates_long_paths() -> None:
    from harite.gui.adapters_qt.qt_widget_helpers import format_slideshow_output_label_text

    long_path = "C:/Users/example/画像/" + ("work/" * 20) + "Harite/slideshow"
    label, tooltip = format_slideshow_output_label_text(long_path)
    assert label.startswith("Slideshow output:")
    assert "Harite" in label and "slideshow" in label
    assert tooltip == long_path
    assert len(label) < len(long_path)


def test_slideshow_output_sync_uses_work_dir_not_pictures_root(qapp, monkeypatch, tmp_path: Path) -> None:
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters.gui_runtime_sync import sync_slideshow_state_from_owner
    from harite.gui.views.main_window import MainWindow

    home = tmp_path / "home"
    pictures = home / "Pictures"
    pictures.mkdir(parents=True)
    xdg_config = tmp_path / "xdg-config"
    xdg_config.mkdir()
    (xdg_config / "user-dirs.dirs").write_text('XDG_PICTURES_DIR="$HOME/Pictures"\n', encoding="utf-8")
    monkeypatch.setattr("harite.gui.views.main_window.Path.home", lambda: home)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config))
    monkeypatch.setattr("harite.gui.views.main_window.sys.platform", "linux")

    work_dir = pictures / "Harite" / "slideshow"
    window = MainWindow()
    window.form_state.output_dir = str(pictures)

    class _SyncBackend:
        def __init__(self) -> None:
            self._objects: dict = {}
            self._slideshow_srcdir_l = ""
            self._slideshow_srcdir_r = ""
            self.slideshow_mode = "random"
            self._slideshow_active_mode = "random"
            self._slideshow_running = False
            self._slideshow_paused = False
            self._slideshow_state_l = None
            self._slideshow_state_r = None
            self._slideshow_previous_l = None
            self._slideshow_previous_r = None

        def _set_spin_value(self, *_args: object) -> None:
            pass

        def _set_toggle_active(self, *_args: object) -> None:
            pass

        def _set_label_text(self, name: str, value: object) -> None:
            from harite.gui.adapters_qt.qt_widget_helpers import set_label_text

            set_label_text(self, name, value)

        def _set_button_enabled(self, *_args: object) -> None:
            pass

        def _refresh_slideshow_source_labels(self, owner: object) -> None:
            pass

        def _refresh_slideshow_mode_controls(self, owner: object) -> None:
            pass

        def _refresh_slideshow_registry_combos(self, owner: object) -> None:
            pass

        def _refresh_slideshow_summary_label(self) -> None:
            pass

        def _refresh_slideshow_current_label(self) -> None:
            pass

        def _refresh_slideshow_output_label(self, output_dir: str | None) -> None:
            from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_output_label

            refresh_slideshow_output_label(self, output_dir)

    backend = _SyncBackend()
    lbl = QLabel()
    backend._objects["lblSlideshowOutput"] = lbl

    sync_slideshow_state_from_owner(backend, window)

    assert "Harite" in lbl.text() and "slideshow" in lbl.text()
    assert lbl.toolTip() == str(work_dir)


def test_refresh_slideshow_output_label_sets_tooltip(qapp, backend) -> None:
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_output_label

    lbl = QLabel()
    backend._objects["lblSlideshowOutput"] = lbl
    full = "C:/Users/example/画像/" + ("nested/" * 12) + "Harite/slideshow"
    refresh_slideshow_output_label(backend, full)
    assert "…" in lbl.text()
    assert lbl.toolTip() == full


def test_refresh_slideshow_summary_label_syncs_footer_and_tab_title(qapp, backend):
    """MAT-02: Qt tab title must follow running/stopped like GTK."""
    from PyQt6.QtWidgets import QLabel, QTabWidget, QWidget

    from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_summary_label

    summary = QLabel()
    tab_title = QLabel()
    backend._objects["lblSlideshowSummary"] = summary
    backend._objects["lblSlideshowTabTitle"] = tab_title
    tabs = QTabWidget()
    slideshow_page = QWidget()
    tabs.addTab(QWidget(), "Main")
    tabs.addTab(slideshow_page, "Slideshow (stopped)")
    backend._objects["command_tabs"] = tabs
    backend._objects["slideshow_tab_box"] = slideshow_page
    backend._slideshow_running = False
    backend._slideshow_paused = False

    refresh_slideshow_summary_label(backend)
    assert summary.text() == "Slideshow: stopped"
    assert tab_title.text() == "Slideshow (stopped)"
    assert tabs.tabText(1) == "Slideshow (stopped)"

    backend._slideshow_running = True
    refresh_slideshow_summary_label(backend)
    assert summary.text() == "Slideshow: running"
    assert tab_title.text() == "Slideshow (running)"
    assert tabs.tabText(1) == "Slideshow (running)"

    backend._slideshow_paused = True
    refresh_slideshow_summary_label(backend)
    assert summary.text() == "Slideshow: paused"
    assert tabs.tabText(1) == "Slideshow (paused)"


def test_refresh_slideshow_source_labels_truncates_long_paths(qapp, backend):
    from PyQt6.QtWidgets import QLabel

    from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_source_labels

    lbl_l = QLabel()
    lbl_r = QLabel()
    backend._objects["lblSlideshowSourceL"] = lbl_l
    backend._objects["lblSlideshowSourceR"] = lbl_r
    backend._slideshow_srcdir_l = "C:/cache/" + ("x" * 80)
    backend._slideshow_srcdir_r = ""
    refresh_slideshow_source_labels(backend)
    assert lbl_l.text().startswith("L:")
    assert "…" in lbl_l.text()
    assert "R: -" in lbl_r.text()


# ---------------------------------------------------------------------------
# Programmatic widget updates must not emit change signals
# ---------------------------------------------------------------------------


def test_set_entry_text_blocks_text_changed(qapp, backend):
    from PyQt6.QtWidgets import QPlainTextEdit

    from harite.gui.adapters_qt.qt_widget_helpers import set_entry_text

    entry = QPlainTextEdit()
    backend._objects["txtMarginText"] = entry
    fired: list[int] = []
    entry.textChanged.connect(lambda: fired.append(1))
    set_entry_text(backend, "txtMarginText", "line one")
    assert entry.toPlainText() == "line one"
    assert fired == []


def test_on_margin_text_sync_does_not_recurse(qapp):
    """sync_margins after margin-text handler must not re-enter the handler."""
    from harite.gui.adapters_qt.qt_backend import load_qt_runtime_signal_backend
    from harite.gui.views.main_window import MainWindow

    backend = load_qt_runtime_signal_backend()
    window = MainWindow()
    backend._signal_handlers["on_change_margin_text"] = window.on_change_margin_text

    entry = backend._objects["txtMarginText"]
    assert entry is not None
    backend._on_margin_text_changed(entry)


# ---------------------------------------------------------------------------
# Slideshow registry combos (C-02)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Slideshow registry combos (C-02)
# ---------------------------------------------------------------------------


def _normalize_combo_data(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _write_catalog_for_refresh(left: Path, right: Path, catalog_path: Path) -> tuple[str, str, str]:
    from harite.sources import add_profile, add_source, empty_catalog, save_catalog

    catalog = empty_catalog()
    left_entry = add_source(catalog, name="Left NAS", path=left)
    right_entry = add_source(catalog, name="Right Cloud", path=right)
    profile = add_profile(
        catalog,
        name="Dual",
        members={"L": left_entry.id, "R": right_entry.id},
    )
    save_catalog(catalog, catalog_path)
    return left_entry.id, right_entry.id, profile.id


def test_refresh_slideshow_registry_combos_restores_owner_selection(qapp, backend, tmp_path):
    from PyQt6.QtWidgets import QComboBox

    from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_registry_combos
    from harite.gui.views.main_window import MainWindow, REGISTRY_NONE_LABEL

    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    catalog_path = tmp_path / "harite-sources.json"
    left_id, _right_id, profile_id = _write_catalog_for_refresh(left_dir, right_dir, catalog_path)

    owner = MainWindow()
    owner._source_catalog_path = catalog_path
    owner.slideshow_profile_id = profile_id
    owner.slideshow_source_id_l = left_id
    owner.slideshow_source_id_r = ""

    profile_combo = QComboBox()
    source_l = QComboBox()
    source_r = QComboBox()
    backend._objects["combo_slideshow_profile"] = profile_combo
    backend._objects["combo_slideshow_source_l"] = source_l
    backend._objects["combo_slideshow_source_r"] = source_r

    refresh_slideshow_registry_combos(backend, owner)

    assert _normalize_combo_data(profile_combo.currentData()) == profile_id
    assert profile_combo.currentText() == "Dual"
    assert _normalize_combo_data(source_l.currentData()) == left_id
    assert _normalize_combo_data(source_r.currentData()) == ""
    assert source_r.currentText() == REGISTRY_NONE_LABEL


def test_refresh_slideshow_registry_combos_clears_profile_after_clear(qapp, backend, tmp_path):
    from PyQt6.QtWidgets import QComboBox

    from harite.gui.adapters_qt.qt_widget_helpers import refresh_slideshow_registry_combos
    from harite.gui.views.main_window import MainWindow, REGISTRY_NONE_LABEL

    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    catalog_path = tmp_path / "harite-sources.json"
    _left_id, right_id, profile_id = _write_catalog_for_refresh(left_dir, right_dir, catalog_path)

    window = MainWindow()
    window._source_catalog_path = catalog_path
    window.on_select_slideshow_profile(profile_id)

    profile_combo = QComboBox()
    source_l = QComboBox()
    source_r = QComboBox()
    backend._objects["combo_slideshow_profile"] = profile_combo
    backend._objects["combo_slideshow_source_l"] = source_l
    backend._objects["combo_slideshow_source_r"] = source_r

    window.on_clear_slideshow_srcdir("L")
    refresh_slideshow_registry_combos(backend, window)

    assert window.slideshow_profile_id == ""
    assert profile_combo.currentText() == REGISTRY_NONE_LABEL
    assert _normalize_combo_data(source_l.currentData()) == ""
    assert _normalize_combo_data(source_r.currentData()) == right_id

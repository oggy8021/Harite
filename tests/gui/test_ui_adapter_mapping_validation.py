from harite.gui.adapters.ui_adapter import validate_mainwindow_signal_mapping
from harite.gui.adapters.ui_loader import load_glade_prototype
from harite.gui.views.main_window import MainWindow


def test_validate_mainwindow_signal_mapping_ok_for_default_glade():
    result = load_glade_prototype()
    win = MainWindow()

    validation = validate_mainwindow_signal_mapping(win, result.signal_handlers)

    assert validation["ok"] is True
    assert validation["missing_methods"] == []


def test_validate_mainwindow_signal_mapping_detects_missing_methods():
    class DummyWindow:
        pass

    validation = validate_mainwindow_signal_mapping(
        DummyWindow(),
        ("on_btnSave_clicked", "on_btnSetWall_clicked"),
    )

    assert validation["ok"] is False
    assert "on_save_legacy" in validation["missing_methods"]
    assert "on_apply_dry_run" in validation["missing_methods"]

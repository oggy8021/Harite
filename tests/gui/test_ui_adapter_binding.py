from pathlib import Path

from harite.gui.adapters.ui_loader import UiLoadResult
from harite.gui.adapters.ui_adapter import bind_mainwindow


def test_bind_mainwindow_records_metadata():
    dummy = type("DummyWindow", (), {})()

    result = UiLoadResult(
        file_path=Path("/tmp/fake.glade"),
        root_tag="interface",
        widget_count=7,
        signal_count=3,
    )

    bind_mainwindow(dummy, result)

    assert hasattr(dummy, "_adapter_bindings")
    md = dummy._adapter_bindings
    assert md["widget_count"] == 7
    assert md["signal_count"] == 3
    assert Path(md["file"]).name == "fake.glade"

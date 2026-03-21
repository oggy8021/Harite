from pathlib import Path

import pytest

from harite.gui.adapters.ui_loader import load_glade_prototype


def test_load_glade_prototype_reads_default_resource():
    result = load_glade_prototype()

    assert result.file_path.exists()
    assert result.root_tag == "glade-interface"
    assert result.widget_count > 0
    assert result.signal_count > 0


def test_load_glade_prototype_raises_when_file_missing(tmp_path):
    missing = tmp_path / "missing.glade"

    with pytest.raises(FileNotFoundError, match="ui resource not found"):
        load_glade_prototype(missing)

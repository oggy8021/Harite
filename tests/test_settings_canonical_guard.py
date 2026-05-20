from pathlib import Path

from harite import settings_file
from harite.gui.adapters.gtk_runtime_dialogs import SettingsDialogProxy
from harite.settings import AppSettings, ApplySettings, OptimizeSettings, SlideshowSettings


def test_settings_model_exposes_only_canonical_settings_methods():
    assert hasattr(AppSettings, "from_settings_dict")
    assert hasattr(AppSettings, "to_settings_dict")

    for cls in (AppSettings, ApplySettings, OptimizeSettings, SlideshowSettings):
        assert hasattr(cls, "to_settings_dict")
        assert not hasattr(cls, "from_config_dict")
        assert not hasattr(cls, "to_config_dict")


def test_settings_file_module_exposes_only_canonical_settings_helpers():
    assert callable(settings_file.resolve_default_settings_path)
    assert callable(settings_file.load_settings)
    assert callable(settings_file.save_settings)
    assert not hasattr(settings_file, "load_config")
    assert not hasattr(settings_file, "save_config")


def test_legacy_settings_modules_are_removed_from_src_tree():
    src_dir = Path(__file__).resolve().parents[1] / "src" / "harite"

    assert not (src_dir / "config.py").exists()
    assert not (src_dir / "preferences.py").exists()


def test_settings_dialog_proxy_exposes_only_canonical_settings_methods():
    dialog = SettingsDialogProxy()

    assert hasattr(dialog, "set_settings")
    assert hasattr(dialog, "get_settings")
    assert hasattr(dialog, "update_setting")
    assert not hasattr(dialog, "set_settings_config")
    assert not hasattr(dialog, "get_settings_config")
    assert not hasattr(dialog, "set_preferences_config")
    assert not hasattr(dialog, "get_preferences_config")
    assert not hasattr(dialog, "update_preference")

from __future__ import annotations

from pathlib import Path

import pytest

from harite.settings_file import merge_patch_only_settings_keys, resolve_default_settings_path


def test_resolve_default_settings_path_linux_with_xdg_config_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    xdg = tmp_path / "xdg"
    monkeypatch.setattr("harite.settings_file.sys.platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))

    assert resolve_default_settings_path() == xdg / "harite" / "harite-settings.json"


def test_resolve_default_settings_path_linux_default_config_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("harite.settings_file.sys.platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr("harite.settings_file.Path.home", lambda: tmp_path)

    assert resolve_default_settings_path() == tmp_path / ".config" / "harite" / "harite-settings.json"


def test_resolve_default_settings_path_windows_uses_appdata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    appdata = tmp_path / "Roaming"
    appdata.mkdir()
    monkeypatch.setattr("harite.settings_file.sys.platform", "win32")
    monkeypatch.setenv("APPDATA", str(appdata))

    assert resolve_default_settings_path() == appdata / "harite" / "harite-settings.json"


def test_resolve_default_settings_path_windows_falls_back_when_appdata_unset(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    home = tmp_path / "user"
    home.mkdir()
    monkeypatch.setattr("harite.settings_file.sys.platform", "win32")
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr("harite.settings_file.Path.home", lambda: home)

    assert resolve_default_settings_path() == home / "AppData" / "Roaming" / "harite" / "harite-settings.json"


def test_merge_patch_only_settings_keys_preserves_missing_keywords() -> None:
    payload = {"plugin": "linux", "apply_mode": "per-monitor-auto-split"}
    existing = {"plugin": "windows", "codh_keyword": "富士", "ndl_keyword": "浮世絵"}

    merged = merge_patch_only_settings_keys(payload, existing)

    assert merged == {
        "plugin": "linux",
        "apply_mode": "per-monitor-auto-split",
        "codh_keyword": "富士",
        "ndl_keyword": "浮世絵",
    }


def test_merge_patch_only_settings_keys_keeps_payload_keywords() -> None:
    payload = {"codh_keyword": "桜", "ndl_keyword": "妖怪"}
    existing = {"codh_keyword": "富士", "ndl_keyword": "浮世絵"}

    merged = merge_patch_only_settings_keys(payload, existing)

    assert merged == {"codh_keyword": "桜", "ndl_keyword": "妖怪"}


def test_merge_patch_only_settings_keys_preserves_slideshow_was_running_at_exit() -> None:
    payload = {"plugin": "linux"}
    existing = {"slideshow_was_running_at_exit": True, "plugin": "windows"}

    merged = merge_patch_only_settings_keys(payload, existing)

    assert merged["slideshow_was_running_at_exit"] is True
    assert merged["plugin"] == "linux"


def test_persist_slideshow_was_running_at_exit_writes_key(tmp_path: Path) -> None:
    from harite.settings_file import load_settings, persist_slideshow_was_running_at_exit

    target = tmp_path / "harite-settings.json"
    path = persist_slideshow_was_running_at_exit(True, target)
    assert path == target
    assert load_settings(target) == {"slideshow_was_running_at_exit": True}

    persist_slideshow_was_running_at_exit(False, target)
    assert load_settings(target) == {"slideshow_was_running_at_exit": False}


def test_load_settings_empty_file_returns_empty_dict(tmp_path: Path) -> None:
    from harite.settings_file import load_settings

    target = tmp_path / "harite-settings.json"
    target.write_bytes(b"")
    assert load_settings(target) == {}


def test_load_settings_whitespace_only_returns_empty_dict(tmp_path: Path) -> None:
    from harite.settings_file import load_settings

    target = tmp_path / "harite-settings.json"
    target.write_text("  \n", encoding="utf-8")
    assert load_settings(target) == {}


def test_load_settings_invalid_non_empty_still_raises(tmp_path: Path) -> None:
    from harite.settings_file import load_settings

    target = tmp_path / "harite-settings.json"
    target.write_text("{bad", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON config"):
        load_settings(target)


def test_patch_settings_value_on_empty_file_writes_key(tmp_path: Path) -> None:
    from harite.settings_file import load_settings, patch_settings_value

    target = tmp_path / "harite-settings.json"
    target.write_bytes(b"")
    patch_settings_value(target, "codh_keyword", "桜")
    assert load_settings(target) == {"codh_keyword": "桜"}

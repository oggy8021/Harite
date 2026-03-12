from harite import plugins
from pathlib import Path


def test_registry_contains_windows():
    names = plugins.registry.list()
    assert "windows" in names


def test_windows_plugin_dry_run_success():
    plugin = plugins.registry.get("windows")
    # use existing test asset
    p = Path("tests/data/left.jpg")
    assert p.exists()
    assert plugin.apply(str(p), dry_run=True) is True


def test_windows_plugin_missing_file():
    plugin = plugins.registry.get("windows")
    assert plugin.apply("nonexistent-file.jpg", dry_run=True) is False

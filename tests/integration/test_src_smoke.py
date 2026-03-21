def test_package_imports():
    import importlib

    modules = [
        'harite',
        'harite.cli',
        'harite.core',
        'harite.plugins',
        'harite.workspace',
    ]

    for m in modules:
        mod = importlib.import_module(m)
        assert mod is not None


def test_core_and_workspace_api():
    from harite.core import split_composite_for_displays
    from harite.workspace import detect_displays

    assert callable(split_composite_for_displays)
    assert callable(detect_displays)

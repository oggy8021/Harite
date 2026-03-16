import pytest

from harite import workspace


@pytest.mark.parametrize("sample_xfconf,expected", [
    ("XFCONF_SAMPLE_PLACEHOLDER", True),
])
def test_detect_displays_repro(monkeypatch, sample_xfconf, expected):
    """Skeleton test to reproduce XFCE/xfconf detection issues.

    - Patch `workspace.detect_displays` to return deterministic Display objects.
    - Provide representative `xfconf-query` outputs as fixtures and assert
      that plugin matching logic selects the expected display.
    """

    # Example: monkeypatch.detect_displays to a simple layout
    monkeypatch.setattr(workspace, "detect_displays", lambda: [
        workspace.Display("eDP-1", 1920, 1080, 0),
        workspace.Display("DP-1", 1920, 1080, 1920),
    ])

    # Placeholder assertion; concrete assertions will be added while reproducing
    displays = workspace.detect_displays()
    assert displays and isinstance(displays[0], workspace.Display)

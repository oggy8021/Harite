"""Unit tests for session startup slideshow resume (#518)."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from harite.gui.startup_slideshow import (
    resolve_startup_launch,
    should_auto_start_from_owner,
    should_auto_start_slideshow,
)


@pytest.mark.parametrize(
    ("startup_slideshow", "was_running_at_exit", "is_startup_launch", "slideshow_running", "expected"),
    [
        (True, True, True, False, True),
        (False, True, True, False, False),
        (True, False, True, False, False),
        (True, True, False, False, False),
        (True, True, True, True, False),
    ],
)
def test_should_auto_start_slideshow(
    startup_slideshow: bool,
    was_running_at_exit: bool,
    is_startup_launch: bool,
    slideshow_running: bool,
    expected: bool,
) -> None:
    assert should_auto_start_slideshow(
        startup_slideshow=startup_slideshow,
        was_running_at_exit=was_running_at_exit,
        is_startup_launch=is_startup_launch,
        slideshow_running=slideshow_running,
    ) is expected


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [
        ("1", True),
        ("true", True),
        ("yes", True),
        ("on", True),
        ("0", False),
        ("", False),
    ],
)
def test_resolve_startup_launch_from_env(
    monkeypatch: pytest.MonkeyPatch,
    env_value: str,
    expected: bool,
) -> None:
    monkeypatch.setenv("HARITE_STARTUP_LAUNCH", env_value)
    assert resolve_startup_launch(cli_flag=None) is expected


def test_resolve_startup_launch_cli_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HARITE_STARTUP_LAUNCH", "1")
    assert resolve_startup_launch(cli_flag=False) is False
    assert resolve_startup_launch(cli_flag=True) is True


@dataclass
class _SlideshowPrefs:
    was_running_at_exit: bool = False


@dataclass
class _Prefs:
    slideshow: _SlideshowPrefs = field(default_factory=_SlideshowPrefs)


class _Owner:
    def __init__(
        self,
        *,
        startup_slideshow: bool = False,
        was_running_at_exit: bool = False,
        slideshow_running: bool = False,
    ) -> None:
        self.startup_slideshow = startup_slideshow
        self.slideshow_running = slideshow_running
        self.preferences = _Prefs(_SlideshowPrefs(was_running_at_exit=was_running_at_exit))


def test_should_auto_start_from_owner() -> None:
    owner = _Owner(startup_slideshow=True, was_running_at_exit=True, slideshow_running=False)
    assert should_auto_start_from_owner(owner, is_startup_launch=True) is True
    assert should_auto_start_from_owner(owner, is_startup_launch=False) is False

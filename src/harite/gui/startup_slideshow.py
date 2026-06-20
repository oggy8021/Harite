"""Session startup slideshow resume helpers (#518)."""

from __future__ import annotations

import os
from typing import Any

STARTUP_SLIDESHOW_SETTINGS_KEY = "startup_slideshow"
SLIDESHOW_WAS_RUNNING_AT_EXIT_KEY = "slideshow_was_running_at_exit"
STARTUP_LAUNCH_ENV = "HARITE_STARTUP_LAUNCH"

_TRUTHY_ENV_VALUES = frozenset({"1", "true", "yes", "on"})


def resolve_startup_launch(*, cli_flag: bool | None = None) -> bool:
    if cli_flag is not None:
        return bool(cli_flag)
    raw = os.getenv(STARTUP_LAUNCH_ENV, "").strip().lower()
    return raw in _TRUTHY_ENV_VALUES


def should_auto_start_slideshow(
    *,
    startup_slideshow: bool,
    was_running_at_exit: bool,
    is_startup_launch: bool,
    slideshow_running: bool,
) -> bool:
    return (
        bool(startup_slideshow)
        and bool(is_startup_launch)
        and bool(was_running_at_exit)
        and not bool(slideshow_running)
    )


def should_auto_start_from_owner(owner: Any, *, is_startup_launch: bool) -> bool:
    slideshow = getattr(getattr(owner, "preferences", None), "slideshow", None)
    startup_slideshow = bool(getattr(owner, "startup_slideshow", False))
    was_running_at_exit = bool(getattr(slideshow, "was_running_at_exit", False))
    return should_auto_start_slideshow(
        startup_slideshow=startup_slideshow,
        was_running_at_exit=was_running_at_exit,
        is_startup_launch=is_startup_launch,
        slideshow_running=bool(getattr(owner, "slideshow_running", False)),
    )

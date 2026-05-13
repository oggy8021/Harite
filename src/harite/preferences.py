from __future__ import annotations

from dataclasses import asdict, dataclass, field
import os
from typing import Any

from .core import DEFAULT_BACKGROUND_COLOR_HEX, normalize_background_color
from .optimize_settings import AUTO
from .positioning import parse_position_pair


def _decode_optional_auto_string(value: object | None, *, default: str | None = None) -> str | None:
    if value is None:
        return default
    raw = str(value).strip()
    if not raw:
        return default
    if raw.lower() == AUTO:
        return AUTO
    return raw


def _decode_two_screen_mode(value: object) -> str:
    if value is None:
        return "off"
    if isinstance(value, bool):
        return "on" if value else "off"
    raw = str(value).strip().lower()
    if raw in {"on", "off", AUTO}:
        return raw
    if raw in {"1", "true", "yes"}:
        return "on"
    if raw in {"0", "false", "no"}:
        return "off"
    raise ValueError(f"invalid two_screen preference: {value}")


@dataclass
class OptimizePreferences:
    resolution: str = "1920x1080"
    scaling: str = "fit"
    two_screen_mode: str = "off"
    l_display: str | None = None
    r_display: str | None = None
    margins: str | None = None
    align: tuple[str, str] = ("center", "center")
    valign: tuple[str, str] = ("center", "center")
    quality: int = 90
    background_color: str = DEFAULT_BACKGROUND_COLOR_HEX
    embed_info: str = "none"
    embed_text: str | None = None
    embed_position: str = AUTO
    embed_max_lines: int = 3

    @classmethod
    def from_config_dict(cls, config: dict[str, Any]) -> "OptimizePreferences":
        return cls(
            resolution=_decode_optional_auto_string(config.get("resolution"), default=AUTO) or AUTO,
            scaling=str(config.get("scaling", "fit")),
            two_screen_mode=_decode_two_screen_mode(config.get("two_screen", False)),
            l_display=_decode_optional_auto_string(config.get("l_display")),
            r_display=_decode_optional_auto_string(config.get("r_display")),
            margins=None if config.get("margins") is None else str(config.get("margins")),
            align=parse_position_pair(config.get("align", "center"), axis="align"),
            valign=parse_position_pair(config.get("valign", "center"), axis="valign"),
            quality=int(config.get("quality", 90)),
            background_color=normalize_background_color(config.get("background_color", DEFAULT_BACKGROUND_COLOR_HEX)),
            embed_info=str(config.get("embed_info", "none")),
            embed_text=None if config.get("embed_text") is None else str(config.get("embed_text")),
            embed_position=str(config.get("embed_position", AUTO)),
            embed_max_lines=int(config.get("embed_max_lines", 3)),
        )

    def to_config_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["two_screen"] = AUTO if self.two_screen_mode == AUTO else (self.two_screen_mode == "on")
        del data["two_screen_mode"]
        data["align"] = list(self.align)
        data["valign"] = list(self.valign)
        return data


@dataclass
class ApplyPreferences:
    plugin_name: str = "windows"
    apply_mode: str = "per-monitor-auto-split"

    @classmethod
    def from_config_dict(cls, config: dict[str, Any], *, default_plugin: str) -> "ApplyPreferences":
        return cls(
            plugin_name=str(config.get("plugin", default_plugin)),
            apply_mode=str(config.get("apply_mode", "per-monitor-auto-split")),
        )

    def to_config_dict(self) -> dict[str, Any]:
        return {
            "plugin": self.plugin_name,
            "apply_mode": self.apply_mode,
        }


@dataclass
class WatchPreferences:
    interval_seconds: int = 60
    srcdir_l: str | None = None
    srcdir_r: str | None = None

    @classmethod
    def from_config_dict(cls, config: dict[str, Any]) -> "WatchPreferences":
        return cls(
            interval_seconds=int(config.get("watch_interval_seconds", 60)),
            srcdir_l=None if config.get("watch_srcdir_l") is None else str(config.get("watch_srcdir_l")),
            srcdir_r=None if config.get("watch_srcdir_r") is None else str(config.get("watch_srcdir_r")),
        )

    def to_config_dict(self) -> dict[str, Any]:
        return {
            "watch_interval_seconds": self.interval_seconds,
            "watch_srcdir_l": self.srcdir_l,
            "watch_srcdir_r": self.srcdir_r,
        }


@dataclass
class AppPreferences:
    optimize: OptimizePreferences = field(default_factory=OptimizePreferences)
    apply: ApplyPreferences = field(default_factory=ApplyPreferences)
    watch: WatchPreferences = field(default_factory=WatchPreferences)

    @staticmethod
    def _default_apply_mode(default_plugin: str) -> str:
        session_markers = (
            os.environ.get("XDG_CURRENT_DESKTOP", ""),
            os.environ.get("XDG_SESSION_DESKTOP", ""),
            os.environ.get("DESKTOP_SESSION", ""),
            os.environ.get("GDMSESSION", ""),
        )
        is_xfce_session = any("xfce" in marker.strip().lower() for marker in session_markers if marker)
        return "per-monitor-auto-split" if is_xfce_session else "single-file"

    @classmethod
    def defaults(cls, *, default_plugin: str) -> "AppPreferences":
        return cls(
            apply=ApplyPreferences(
                plugin_name=default_plugin,
                apply_mode=cls._default_apply_mode(default_plugin),
            )
        )

    @classmethod
    def from_config_dict(cls, config: dict[str, Any], *, default_plugin: str) -> "AppPreferences":
        raw_apply_mode = config.get("apply_mode")
        apply_mode = str(raw_apply_mode) if raw_apply_mode is not None else cls._default_apply_mode(default_plugin)
        return cls(
            optimize=OptimizePreferences.from_config_dict(config),
            apply=ApplyPreferences(
                plugin_name=str(config.get("plugin", default_plugin)),
                apply_mode=apply_mode,
            ),
            watch=WatchPreferences.from_config_dict(config),
        )

    def to_config_dict(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        merged.update(self.optimize.to_config_dict())
        merged.update(self.apply.to_config_dict())
        merged.update(self.watch.to_config_dict())
        return merged
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import os
from typing import Any

from harite.core import DEFAULT_BACKGROUND_COLOR_HEX, normalize_background_color
from harite.display_scale import normalize_display_scale
from harite.optimize_settings import normalize_canvas_scale_percent
from harite.positioning import parse_position_pair


def _decode_bool_setting(value: object, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raw = str(value).strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default


@dataclass
class OptimizeSettings:
    canvas_scale_percent: int = 100
    scaling: str = "fit"
    l_display_scale: float = 1.0
    r_display_scale: float = 1.0
    l_auto_display_scale: bool = False
    r_auto_display_scale: bool = False
    margins: str | None = None
    align: tuple[str, str] = ("center", "center")
    valign: tuple[str, str] = ("center", "center")
    quality: int = 90
    background_color: str = DEFAULT_BACKGROUND_COLOR_HEX
    embed_info: str = "none"
    embed_text: str | None = None
    embed_position: str = "right-bottom"
    embed_max_lines: int = 3

    @classmethod
    def from_settings_dict(cls, settings: dict[str, Any]) -> "OptimizeSettings":
        raw_scale = settings.get("canvas_scale_percent", settings.get("canvas_scale", 100))
        return cls(
            canvas_scale_percent=normalize_canvas_scale_percent(raw_scale),
            scaling=str(settings.get("scaling", "fit")),
            l_display_scale=normalize_display_scale(settings.get("l_display_scale", 1)),
            r_display_scale=normalize_display_scale(settings.get("r_display_scale", 1)),
            l_auto_display_scale=_decode_bool_setting(settings.get("l_auto_display_scale"), default=False),
            r_auto_display_scale=_decode_bool_setting(settings.get("r_auto_display_scale"), default=False),
            margins=None if settings.get("margins") is None else str(settings.get("margins")),
            align=parse_position_pair(settings.get("align", "center"), axis="align"),
            valign=parse_position_pair(settings.get("valign", "center"), axis="valign"),
            quality=int(settings.get("quality", 90)),
            background_color=normalize_background_color(settings.get("background_color", DEFAULT_BACKGROUND_COLOR_HEX)),
            embed_info=str(settings.get("embed_info", "none")),
            embed_text=None if settings.get("embed_text") is None else str(settings.get("embed_text")),
            embed_position=str(settings.get("embed_position", "right-bottom")),
            embed_max_lines=int(settings.get("embed_max_lines", 3)),
        )

    def to_settings_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["align"] = list(self.align)
        data["valign"] = list(self.valign)
        return data


@dataclass
class ApplySettings:
    plugin_name: str = "windows"
    apply_mode: str = "per-monitor-auto-split"
    windows_apply_span: bool = False

    @classmethod
    def from_settings_dict(cls, settings: dict[str, Any], *, default_plugin: str) -> "ApplySettings":
        raw_apply_mode = settings.get("apply_mode")
        apply_mode = (
            str(raw_apply_mode)
            if raw_apply_mode is not None
            else AppSettings._default_apply_mode(default_plugin)
        )
        raw_span = settings.get("windows_apply_span", False)
        windows_apply_span = raw_span is True or str(raw_span).strip().lower() in {"1", "true", "yes", "on"}
        return cls(
            plugin_name=str(settings.get("plugin", default_plugin)),
            apply_mode=apply_mode,
            windows_apply_span=windows_apply_span,
        )

    def to_settings_dict(self) -> dict[str, Any]:
        return {
            "plugin": self.plugin_name,
            "apply_mode": self.apply_mode,
            "windows_apply_span": bool(self.windows_apply_span),
        }


@dataclass
class SlideshowSettings:
    interval_seconds: int = 60
    mode: str = "random"
    srcdir_l: str | None = None
    srcdir_r: str | None = None
    source_id_l: str | None = None
    source_id_r: str | None = None
    profile_id: str | None = None
    l_auto_display_scale: bool = False
    r_auto_display_scale: bool = False

    @classmethod
    def from_settings_dict(cls, settings: dict[str, Any]) -> "SlideshowSettings":
        return cls(
            interval_seconds=int(settings.get("slideshow_interval_seconds", 60)),
            mode=str(settings.get("slideshow_mode", "random")),
            srcdir_l=None if settings.get("slideshow_srcdir_l") is None else str(settings.get("slideshow_srcdir_l")),
            srcdir_r=None if settings.get("slideshow_srcdir_r") is None else str(settings.get("slideshow_srcdir_r")),
            source_id_l=_optional_str(settings.get("slideshow_source_id_l")),
            source_id_r=_optional_str(settings.get("slideshow_source_id_r")),
            profile_id=_optional_str(settings.get("slideshow_profile_id")),
            l_auto_display_scale=_decode_bool_setting(
                settings.get("slideshow_l_auto_display_scale"),
                default=False,
            ),
            r_auto_display_scale=_decode_bool_setting(
                settings.get("slideshow_r_auto_display_scale"),
                default=False,
            ),
        )

    def to_settings_dict(self) -> dict[str, Any]:
        payload = {
            "slideshow_interval_seconds": self.interval_seconds,
            "slideshow_mode": self.mode,
            "slideshow_srcdir_l": self.srcdir_l,
            "slideshow_srcdir_r": self.srcdir_r,
            "slideshow_l_auto_display_scale": bool(self.l_auto_display_scale),
            "slideshow_r_auto_display_scale": bool(self.r_auto_display_scale),
        }
        if self.source_id_l:
            payload["slideshow_source_id_l"] = self.source_id_l
        if self.source_id_r:
            payload["slideshow_source_id_r"] = self.source_id_r
        if self.profile_id:
            payload["slideshow_profile_id"] = self.profile_id
        return payload


def _optional_str(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


@dataclass
class AppSettings:
    optimize: OptimizeSettings = field(default_factory=OptimizeSettings)
    apply: ApplySettings = field(default_factory=ApplySettings)
    slideshow: SlideshowSettings = field(default_factory=SlideshowSettings)

    @staticmethod
    def _default_apply_mode(default_plugin: str) -> str:
        if default_plugin == "windows":
            try:
                from harite.workspace import detect_displays

                if len(detect_displays()) >= 2:
                    return "per-monitor-auto-split"
            except Exception:
                pass
        session_markers = (
            os.environ.get("XDG_CURRENT_DESKTOP", ""),
            os.environ.get("XDG_SESSION_DESKTOP", ""),
            os.environ.get("DESKTOP_SESSION", ""),
            os.environ.get("GDMSESSION", ""),
        )
        is_xfce_session = any("xfce" in marker.strip().lower() for marker in session_markers if marker)
        return "per-monitor-auto-split" if is_xfce_session else "single-file"

    @classmethod
    def defaults(cls, *, default_plugin: str) -> "AppSettings":
        return cls(
            apply=ApplySettings(
                plugin_name=default_plugin,
                apply_mode=cls._default_apply_mode(default_plugin),
            )
        )

    @classmethod
    def from_settings_dict(cls, settings: dict[str, Any], *, default_plugin: str) -> "AppSettings":
        return cls(
            optimize=OptimizeSettings.from_settings_dict(settings),
            apply=ApplySettings.from_settings_dict(settings, default_plugin=default_plugin),
            slideshow=SlideshowSettings.from_settings_dict(settings),
        )

    def to_settings_dict(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        merged.update(self.optimize.to_settings_dict())
        merged.update(self.apply.to_settings_dict())
        merged.update(self.slideshow.to_settings_dict())
        return merged

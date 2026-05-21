from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .display_context import build_auto_split_display_map, get_ordered_displays
from .workspace import Display


@dataclass(frozen=True)
class EffectiveApplySettings:
    apply_mode: str
    target: str | dict


def resolve_apply_settings(
    *,
    file: Path,
    apply_mode: str,
    left_file: Path | None = None,
    right_file: Path | None = None,
    displays: Sequence[Display] | None = None,
    output_dir: Path | None = None,
) -> EffectiveApplySettings:
    mode = str(apply_mode or "single-file").strip().lower()
    if mode == "single-file":
        return EffectiveApplySettings(apply_mode=mode, target=str(file))

    ordered_displays = get_ordered_displays(displays)

    if mode == "per-monitor-explicit":
        if len(ordered_displays) < 2:
            raise ValueError("Need at least two displays to use --left-file/--right-file")
        mapping = {}
        if left_file is not None:
            mapping[ordered_displays[0].name] = str(left_file)
        if right_file is not None:
            mapping[ordered_displays[1].name] = str(right_file)
        if not mapping:
            raise ValueError("--per-monitor requires --left-file/--right-file or --auto-split")
        return EffectiveApplySettings(apply_mode=mode, target=mapping)

    if mode == "per-monitor-auto-split":
        if len(ordered_displays) < 2:
            raise ValueError("per-monitor apply requires at least two detected displays")
        target = build_auto_split_display_map(file, ordered_displays[:2], output_dir or file.parent)
        if not target:
            raise ValueError("per-monitor split failed")
        return EffectiveApplySettings(apply_mode=mode, target=target)

    raise ValueError(f"unknown apply mode: {apply_mode}")
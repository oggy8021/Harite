from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from harite.settings_file import resolve_default_settings_path

LAST_OPTIMIZE_RUN_FILENAME = ".harite-last-optimize.json"


@dataclass(frozen=True)
class LastOptimizeRun:
    composite_path: Path
    output_dir: Path


def _tracking_path(directory: Path) -> Path:
    return Path(directory) / LAST_OPTIMIZE_RUN_FILENAME


def _serialize_run(*, output_dir: Path, composite_path: Path) -> dict[str, str]:
    resolved_output = Path(output_dir).resolve()
    resolved_composite = Path(composite_path).resolve()
    return {
        "composite_path": str(resolved_composite),
        "output_dir": str(resolved_output),
    }


def _parse_run_payload(payload: object) -> LastOptimizeRun:
    if not isinstance(payload, dict):
        raise ValueError("last optimize run file must contain a JSON object")
    raw_composite = payload.get("composite_path")
    raw_output = payload.get("output_dir")
    if not raw_composite or not raw_output:
        raise ValueError("last optimize run file is missing composite_path or output_dir")
    composite_path = Path(str(raw_composite)).expanduser()
    output_dir = Path(str(raw_output)).expanduser()
    if not composite_path.is_file():
        raise ValueError(f"last optimize composite file not found: {composite_path}")
    return LastOptimizeRun(composite_path=composite_path, output_dir=output_dir)


def write_last_optimize_run(*, output_dir: Path, composite_path: Path) -> Path:
    """Persist the latest optimize result for a follow-up ``apply`` command."""
    payload = _serialize_run(output_dir=output_dir, composite_path=composite_path)
    primary = _tracking_path(output_dir)
    primary.parent.mkdir(parents=True, exist_ok=True)
    _write_json(primary, payload)

    config_dir = resolve_default_settings_path().parent
    config_dir.mkdir(parents=True, exist_ok=True)
    _write_json(_tracking_path(config_dir), payload)
    return primary


def read_last_optimize_run(*, search_dirs: Sequence[Path]) -> LastOptimizeRun:
    errors: list[str] = []
    seen: set[Path] = set()
    for raw_dir in search_dirs:
        directory = Path(raw_dir).expanduser()
        try:
            resolved = directory.resolve()
        except OSError:
            resolved = directory
        if resolved in seen:
            continue
        seen.add(resolved)
        tracking = _tracking_path(resolved)
        if not tracking.exists():
            continue
        try:
            return _load_run(tracking)
        except ValueError as exc:
            errors.append(f"{tracking}: {exc}")
    if errors:
        raise ValueError(errors[-1])
    raise ValueError(
        "No last optimize run found. Run `harite optimize` first or pass --file."
    )


def default_last_optimize_search_dirs(*, output_hint: Path | None = None) -> list[Path]:
    dirs: list[Path] = []
    if output_hint is not None:
        dirs.append(Path(output_hint))
    dirs.append(resolve_default_settings_path().parent)
    dirs.append(Path.cwd())
    return dirs


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _load_run(path: Path) -> LastOptimizeRun:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return _parse_run_payload(payload)

from __future__ import annotations

from pathlib import Path
from typing import Any
import json


def load_config(path: Path) -> dict[str, Any]:
    """Load a JSON config file and return as dict.

    The config file is expected to be a JSON object containing keys
    matching CLI option names (e.g. "resolution": "3840x2160").
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    try:
        with p.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON config: {e}") from e

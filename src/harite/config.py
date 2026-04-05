from __future__ import annotations

from pathlib import Path
from typing import Any
import json


def load_config(path: Path) -> dict[str, Any]:
    """JSON 設定ファイルを読み込み辞書で返す。

    Summary:
        指定したパスの JSON ファイルを読み込み、CLI のデフォルト設定を表す
        辞書を返す。ファイルが見つからない場合や JSON が不正な場合は例外を投げる。

    Args:
        path: 読み込む設定ファイルのパス。

    Returns:
        設定を格納した辞書。

    Raises:
        FileNotFoundError: ファイルが存在しない場合。
        ValueError: JSON が不正な場合。
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    try:
        with p.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON config: {e}") from e

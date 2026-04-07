# Core I/O 仕様（草案）

作成日: 2026-03-12
作成者: Copilot（草案）

## 目的

母体プログラムのコア計算ロジックの入出力（I/O）を定義し、Harite の実装で必ず保持すべき外部インターフェースを明確にする。

## スコープ

- 「壁紙を最適化し、美しく配置する」という最終挙動を維持する。内部実装は再構築する。
- CLI とプログラム的 API（ライブラリ呼び出し）の両方を対象とする。
- 表示レイアウトの最終的なピクセル配置（矩形配置）を出力できることを必須とする。

## 高レベル動作

入力となる画像群とターゲット画面情報を受け取り、各画像のトリミング/スケーリング/位置決めを行い、最終的に出力画像（最適化済み）およびレイアウトメタデータを生成する。

## 入力（パラメータ）

- inputs: `list[str | Path]` — 入力画像ファイルのパス一覧、もしくは画像を列挙するディレクトリパス
- target_resolution: `tuple[int, int]` — 出力画面解像度（幅、高さ）
- layout: `str` — レイアウトモード（例: `single`、`grid`、`mosaic`、`cover`）
- scaling: `str` — リサイズモード（例: `fit`、`fill`、`crop`）
- padding: `int` — 画像間の余白（ピクセル）
- output_dir: `Path` — 出力先ディレクトリ
- quality: `int` (0-100) — 出力画像の圧縮品質
- random_seed: `Optional[int]` — 再現性のための乱数シード

## 出力

- optimized_files: `list[Path]` — 出力された最適化画像のパス一覧
- layout_metadata: `List[PlacementResult]` — 各画像の最終配置情報
- summary: `Dict[str, Any]` — 実行サマリ（処理時間、スコア等）
- exit_code / status: 成功/失敗の状態

### PlacementResult（データモデル案）

```py
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

@dataclass
class PlacementResult:
    image_path: Path
    x: int
    y: int
    width: int
    height: int
    rotation: float  # degrees
    scale: float
    score: float  # 最適化の良さを表す指標
```

## プログラム API（候補シグネチャ）

```py
from pathlib import Path
from typing import Sequence, Tuple, List

def optimize_wallpapers(
    inputs: Sequence[Path | str],
    target_resolution: Tuple[int, int],
    output_dir: Path,
    layout: str = "mosaic",
    scaling: str = "fit",
    padding: int = 0,
    quality: int = 90,
    random_seed: int | None = None,
) -> Tuple[List[Path], List[PlacementResult]]:
    """最適化画像と配置メタデータを返す。"""
```

```py
def compute_placement(
    image_path: Path,
    target_resolution: Tuple[int, int],
    layout: str = "mosaic",
    scaling: str = "fit",
    padding: int = 0,
) -> PlacementResult:
    """単一画像のターゲット画面内における配置を計算して返す。"""
```

## CLI 例

- 基本実行例:

```
harite optimize --input ./imgs --resolution 3840x2160 --layout mosaic --output ./out --quality 90
```

- 単一画像で配置のみ確認する例:

```
harite compute-placement --input img.jpg --resolution 1920x1080 --layout cover
```

決定: CLI 名は `harite` を正式に採用します。母体プログラムの旧コマンド名である `walloptimiz` は、現時点ではエイリアスを提供しません。旧コマンド名の互換が必要になった場合は、`pyproject.toml` の `console_scripts` にエイリアスを追加する案を別途検討・実装します。

## 受け入れ基準（互換性）

- 定量比較: 母体プログラムの代表入力セットに対して、`PlacementResult` の `x,y,width,height,scale` が許容差内に収まること。許容差は初期値として `±2` ピクセル、スケールは `±0.02` を提案。
- 出力ファイル名やメタデータフォーマットは後続仕様で固定するが、JSON 形式で保存すること。
- 再現性: `random_seed` を固定した場合に同じ `layout_metadata` が得られること。

## テスト方針（コア）

- `compute_placement` の単体テストを充実させる。母体プログラムのテストケースを1〜3件サンプルとして取り込み、数値比較で互換性を担保する。
- 入出力のフォーマットテスト（JSON）を用意する。

## 次のアクション

1.母体プログラムの該当ソース（`wallpaperoptimizer`）を解析し、代表的な入力/出力例を収集する。
2.本ファイルを基に `tests/core/test_core.py` のサンプルケースを作成する。
3.オーナーに本草案のレビューを依頼し、許容差やレイアウトモードの細部を決定する。

---

この草案を確認いただき、修正や追加要望があれば指示ください。

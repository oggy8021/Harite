# Core I/O — 代表入力例と期待出力（草案）

作成日: 2026-03-12

以下は `docs/specs/core-io.md` を補足する代表的な入力例とテストケース案です。自動化テスト作成時のベースにしてください。

## 例1: 単一モニタ（フルスクリーン）

- 入力: `inputs = ['samples/img_wide.jpg']`
- target_resolution: `(1920, 1080)`
- scaling: `fill`
- 期待出力（メタデータ）:
  - 1つの `PlacementResult` を返す
  - `width >= 1920 or height >= 1080`（少なくとも画面を覆う）
  - `x <= 0 <= x+width`（中心位置が画面内にある）

## 例2: デュアルモニタ（左右分割）

- 入力: `inputs = ['samples/left.jpg', 'samples/right.jpg']`
- target_resolution: `(3840, 1080)`  # 左:1920x1080、右:1920x1080
- scaling: `fit`
- 期待出力:
  - 2つの `PlacementResult`（left/right）
  - 左画像は `posit == 'left'`、右画像は `posit == 'right'`
  - 各画像がそれぞれのスクリーン領域に収まる（許容差 ±2ピクセル）

## 例3: マージン指定と再現性

- 入力: `inputs = ['samples/a.jpg', 'samples/b.jpg']`
- オプション: `random_seed=42`
- 期待出力:
  - `random_seed=42` による `layout_metadata` は再現可能
  - 同じ入力順と設定から同じ配置結果が得られる

## メタデータ JSON 例

{
  "optimized_files": ["/home/user/.local/share/harite/wallopt20260312-120101.jpg"]、"layout_metadata": [
    {
      "image_path": "samples/left.jpg"、"x": 0、"y": 0、"width": 1920、"height": 1080、"rotation": 0.0、"scale": 1.0、"score": 0.95、"posit": "left"
    }
  ]、"summary": {"processing_time_s": 0.42}
}

---

次のステップ案:

- 母体プログラムの `test/` ディレクトリから代表ケースやサンプル画像を収集して `tests/data/` に置く。
- 実装ができ次第、`tests/core/test_core.py` のスキップを解除して実行する。

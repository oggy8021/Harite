## Tests overview (日本語)

目的

- リポジトリにおける現在のテスト状況を整理し、未カバー領域と優先度を明確にする。

対象範囲

- CLI コマンド（`scripts/` の主要スクリプト）
- ドキュメント変換ロジック（`scripts/apply_docs_replacements.py`、`scripts/fix_enumerators.py`）
- CI ワークフローで実行可能な最小セット

現状（要点）

- 単体テスト: 一部ユニットテストはあるがカバレッジは限定的。特にテキスト置換のエッジケースが不足。
- インテグレーション: ドキュメント変換の dry-run → レポート を手動で検証している。

未カバー / 優先順位（提案）

1. 置換ロジックのエッジケース（数字・コードブロック・表・diff行の除外） — 高
2. 列挙子修正の一覧形式依存ケース — 高
3. CLI 引数の境界値（`--dry-run`、`--report`） — 中
4. CI の差分閾値に対するリグレッションテスト — 中

推奨アクション

1. 小さなユニットテストを追加（`tests/test_replacements.py` 等）で最初の2項目をカバー。
2. 代表的な markdown サンプルを fixtures として用意し、parametrize テストで複数ケースを回す。
3. 必要最小限の CI ジョブを追加し、重要ケースのみ自動で実行する。

次のステップ（短期）

1. この草案を確認 → 修正指示を頂く。
2. `feature/tests-coverage-001` ブランチで `tests/` を追加し、`pytest` の基本テストを 1~2 件追加。

---
作成日: 2026-03-15

検証の詳細（追記）

以下は本リポジトリでの検証を確実にするために `docs/tests-overview.md` に明示的に残しておきたい項目です。テスト実装時の合意点として約束してください。

- パラメータ行列: CLI の主要オプションと引数の組合せ表を作成する（例: `--dry-run`、`--report`、入力パス、出力パス、フィルタフラグ 等）。優先度の高い組合せをまず自動化する。
- 環境バリエーション: OS（Windows/Unix）、Python バージョン、locale/encoding、PowerShell/シェルの違いを表記し、再現可能な最小セットを定義する。
- 出力アーティファクト検証: 生成されるレポートや画像について「ゴールデンファイル」との比較を行う。画像比較は PSNR/SSIM 等を用い、閾値を明記する（例: SSIM >= 0.99 または PSNR >= 40dB）。
- 乱数・決定性: 生成に乱数が絡む場合はシード固定の方法を用意し、テストで再現可能にする（環境変数や `--seed` フラグを標準化する）。
- テスト手法: `pytest.mark.parametrize` を用いたパラメタライズ、fixtures によるサンプル入力配置、CI 用のスモークケースとローカル拡張ケースを分離する。
- 許容差分ポリシー: 画像差分の閾値や許容範囲、差分超過時の再現手順と報告フォーマットを規定する。

簡単な `pytest` サンプル（例）:

```python
import subprocess
import pytest
from pathlib import Path

@pytest.mark.parametrize("args, golden", [
 (("--input", "tests/fixtures/sample1.md", "--report", "out.md"), "tests/golden/sample1.png"),
])
def test_cli_image_output(tmp_path, args, golden):
 out_dir = tmp_path / "out"
 out_dir.mkdir()
 cmd = ["python", "-m", "scripts.apply_docs_replacements"] + list(args) + ["--out-dir", str(out_dir)]
 subprocess.check_call(cmd)
 # ここで出力画像と golden を比較し、SSIM/PSNR の閾値を満たすことを assert する

```

画像差分の検証例（概念）:

- 使用ライブラリ: `Pillow` と `scikit-image` (`skimage.metrics.structural_similarity`) を利用して SSIM を算出する。
- 閾値例: `SSIM >= 0.99` を合格ラインとし、これを超えない場合は差分画像を `tests/artifacts/` に保存して人が確認する。

備考: 上記はサンプルのため、具体的な CLI 呼び出しや出力パスは実装時に合わせて調整してください。

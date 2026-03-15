# 最初の開発タスク（提案）

目的: 母体プログラムの仕様をリバースエンジニアリングし、Harite のコア設計（I/Oシグネチャ）を確定する。

ステップ:
1.母体プログラム `wallpaperoptimizer` をクローン/参照し、主要な計算フローを抽出する。
2.コアの入力/出力（シグネチャ）を洗い出し、`docs/specs/core-io.md` を作成する。
3.`pyproject.toml` とパッケージ骨格 (`src/harite/__init__.py`) を作成する。
4.最小の CLI スケルトン（`typer` 推奨）を作成し、`harite --version` を実装する。
5.単体テストの雛形を作成（`tests/test_core.py`）と GitHub Actions の最小CIを設定。
6.仕様書（`docs/specs/core-io.md`）をオーナーに提出して承認を得る。

推定所要時間: 1~3日（解析量による）。

成果物:
- `docs/specs/core-io.md`（オーナー承認が必要）
- 初期プロジェクト構造（`pyproject.toml`、`src/harite/`、`tests/`）
- 最小CLIとCI設定

次のアクションの提案:
- 私がステップ1の解析を行い、`docs/specs/core-io.md` の草案を作成します。実施してよいですか？
# XFCE フォローアップ検証ログ（#6）

最終更新: 2026-03-20

## 目的

- #6 `Improve XFCE heuristics` の運用検証結果を、リリース準備チェックリストに沿って記録する。
- 実機で確認済みの事項と、継続観測が必要な事項を分離して管理する。

## 実施環境

- OS: Linux Mint (XFCE)
- Python: 3.12
- 関連コマンド: `xfconf-query`, `xrandr`
- 検証スクリプト: `scripts/xfce_smoke_runner.py`

## 実施ログ（要約）

### Step 1: dry-run（短時間）

- 結果: 成功
- 主要ログ: `finish failures=0`
- 判定: 問題なし

### Step 2: dry-run（長時間）

- 結果: 成功
- 主要ログ: `finish failures=0`
- 判定: 問題なし

### Step 3: 実適用（--do-it）

- 初回観測: 壁紙が切り替わらず黒背景化するケースを確認
- 調査結果: `xfconf` に相対パスが書き込まれるケースがあり、環境によって適用失敗
- 対応:
  - `scripts/xfce_smoke_runner.py` で入力パスを絶対パス化
  - Linux plugin の `apply` 経路でも絶対パス化
  - 回帰テストを追加
- 対応後観測: 実機で壁紙が切り替わることを確認
- 判定: 主要ブロッカーは解消

## リリース準備チェックリストとの対応

- 項目 3: 実行確認（CLI）
  - `harite optimize --help`: 実施済み
  - `harite apply --help`: 実施済み
- 項目 4: Linux/XFCE 向け最終確認
  - dry-run 再実行: 実施済み（Step1/Step2）
  - 実適用で切り替え確認: 実施済み（対応後）
  - 絶対パス適用確認: 実施済み（コード修正 + テスト）
  - 切り戻し手順確認: 実施済み（2026-03-20 の実行ログあり）

## 追加実行結果（2026-03-20）

- 実行コマンド: `scripts/run_xfce_followup.sh`（known-good + smoke 5回）
- 出力ディレクトリ: `xfce-followup-20260320-131829`
- known-good 画像: `/home/katsu/Develop/Repos/Harite/tests/data/img_wide.jpg`
- 主要ログ:
  - `xfce-followup-20260320-131829/apply-dry-run.log`
  - `xfce-followup-20260320-131829/apply-do-it.log`
  - `xfce-followup-20260320-131829/smoke.log`
  - `xfce-followup-20260320-131829/last-image-after.txt`
- 目視結果: 壁紙復帰を確認（成功）
- 未確認:
  - `last-image` が絶対パスのみかの厳密確認
  - 黒背景が完全に再発しないことの継続観測

## 残タスク

1. `xfce-followup-20260320-131829/last-image-after.txt` を確認し、絶対パス適用の確認結果を追記する。
2. 可能であれば別解像度構成（例: 異解像度デュアル）でも 5 回程度の短時間 smoke を取得する。

補助:

- `scripts/run_xfce_followup.sh` を使うと、切り戻し確認と短時間 smoke のログをまとめて取得できる。

## 参照

- `docs/release-readiness-checklist.md`
- `docs/misc/xfce-testing.md`
- `docs/misc/xfce-rollback-playbook.md`
- `docs/specs/xfce-heuristics.md`
- `scripts/run_xfce_followup.sh`

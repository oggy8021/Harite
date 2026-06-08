# CI ワークフロー解説（概要）

目的

- リポジトリに設定されている GitHub Actions ワークフローの役割を日本語で明示し、どのジョブが何を検証しているか、重いジョブと軽いジョブの区分、そして日常的な PR で期待される通過条件を分かりやすくまとめます。

対象ファイル

- `.github/workflows/ci.yml`
- `.github/workflows/pr-checks.yml`
- `.github/workflows/docs-diff-check.yml`

---

## 1. `ci.yml` — CI（lint + テスト行列）

目的

- プルリクエストや main への push 時の基本的な静的チェックとユニットテストを実行し、主要プラットフォームでの動作確認を行います。

含まれるジョブ

- `lint`（Ruff）
  - 実行環境: `ubuntu-latest`
  - 役割: コード整形・スタイルチェック（早期の軽量フィードバック）。
  - 備考: ここでの失敗はコード品質指摘だが必須修正対象とするかは運用次第。

- `changes`（コード変更検出、PR のみ）
  - 役割: `dorny/paths-filter` で `src/`, `tests/`, 依存定義, `.github/`, `scripts/` 等の変更を検出する。
  - `docs/**` のみの PR では後段の pytest を省略し、同名の `Test matrix` ジョブを即時成功させる（branch protection の必須チェック名を維持）。

- `test`（テストマトリクス）
  - 実行環境: `ubuntu-latest`（matrix、Python 3.12）
  - 役割: ユニットテスト（`pytest -q`、`QT_QPA_PLATFORM=offscreen`）。
  - 備考: PR でコード変更がある場合、または `main` への push 時に実行。`pip` キャッシュ（`setup-python` `cache: pip`）で依存インストールを短縮。

- `test-skipped`（docs-only PR 用）
  - 役割: コード変更なし PR 向けの pytest 省略パス。チェック名は `Test matrix (ubuntu-latest, 3.12)` と同一。

- `build-dist`
  - 役割: sdist / wheel ビルドと artifact 保存。
  - 備考: branch protection の必須チェックには含めない（`test` 成功後に実行）。

運用上の方針

- テストマトリクスは **ubuntu のみ**（`.github/branch-protection.json` と整合）。
- `docs/**` のみの PR は pytest を省略（lint / pr-checks / docs-diff-check は従来どおり）。
- Windows / macOS マトリクスは PR 毎必須から外す。将来のリリース企画がある場合に別ジョブで検討。

---

## 2. `pr-checks.yml` — PR メタチェック（ブランチ名／PR本文など）

目的

- PR の運用ルール（ブランチ命名規約、PR 本文の有無など）を自動で検証し、レビュー運用の品質を担保します。

含まれるジョブ

- `validate-branch-name`
  - 役割: `feature/`,`fix/`,`docs/`,`chore/` プレフィックスなどの命名規約をチェック。`save/*` のようなバックアップブランチはチェックをスキップ。
- `validate-pr-body`
  - 役割: PR の本文が空でないことを検査（簡易テンプレート遵守の促し）。

運用上のポイント

- これらは軽量で PR の質を保つため重要です。命名規約違反は早期に弾くことでレビューワークの無駄を減らします。

---

## 3. `docs-diff-check.yml` — ドキュメント差分サイズチェック

目的

- `docs/` 以下で大量の自動置換が発生する PR を検出し、誤った大規模差分が混入しないようにするための安全網を提供します。

含まれるジョブ

- `check_diff`
  - 役割: `scripts/apply_docs_replacements.py` のドライラン結果をレポートし、ファイルごとの差分行数が所定の閾値（例: 100行）を超えると失敗させる。

運用上のポイント

- ドキュメント置換等の自動処理が意図せず単一ファイルへ大規模差分を作るのを防ぎます。
- repo 全体の backlog が残っていても、単一ファイルの急激な膨張を優先して検知する運用です。必要に応じて閾値の調整や例外運用を検討してください。

---

## 全体運用の提案（短期決定事項）

- PR の必須チェックは「早く通ること」と「最低限の品質保証」の両立を目標にする。
  - 最低必須: `pr-checks`（命名／本文） + `lint` + 縮約した `unit-tests`（一つの代表環境）。
  - 重め: OS マトリクスや拡張統合テストは夜間バッチ・手動トリガーへ移行。
- ユーザ誤操作や狭い環境向けのエッジケースは "仕様として明文化" してユーザ責任に切り分けることで、CI 側の過剰な検証負荷を減らす選択肢がある。

---

## 次のアクション案

- この文書をレビュー → 必要なら `docs/ci-workflows.md` を微修正して PR 化します。
- 必須ジョブと拡張ジョブの明確化（実際にワークフローを分割する作業）を行う。

作成日: 2026-03-16

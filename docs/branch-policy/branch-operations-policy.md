# ブランチ運用ポリシー（統合版）

最終更新: 2026-04-12

## 目的

- `main` の安定運用と誤操作防止を両立する。
- ブランチ保護、PR運用、クリーンアップ、Agent利用の責任境界を一本化する。

## 適用範囲

- 対象ブランチ: `main`, `feature/*`, `fix/*`, `docs/*`, `chore/*`
- 例外運用: `save/*`（退避/バックアップ）, `discuss/*`（検討用）
- 運用責任者: オーナー

## ブランチ命名

- 機能追加: `feature/<short-desc>-<YYYYMMDD>`
- バグ修正: `fix/<short-desc>-<YYYYMMDD>`
- ドキュメント: `docs/<short-desc>-<YYYYMMDD>`
- 雑務: `chore/<short-desc>-<YYYYMMDD>`

## PR とマージ

- `main` への直接 push は行わない。
- PR本文に概要/変更点/テスト手順を記載する。
- CI が green のときのみマージする。
- マージ方式は原則 `squash merge`。

## Branch Protection（main）

推奨設定:

- 必須ステータスチェック
  - `Lint (ruff)`
  - `Test matrix (ubuntu-latest, 3.12)`
  - `Test matrix (macos-latest, 3.12)`
  - `Test matrix (windows-latest, 3.12)`
- `Include administrators`: 有効
- `Require branches to be up to date before merging`: 有効
- PRレビュー必須数: 当面 0（将来 1 以上へ引き上げ可）
- ブランチ名/PR本文チェック: `.github/workflows/pr-checks.yml` で実施（`save/*` はスキップ）

注意:

- Branch protection は GitHub Settings で管理者が適用する。
- 本文書は設定の参照用であり、文書更新のみでは有効化されない。

## ブランチクリーンアップ運用

- 原則: `main` マージ済みの不要ブランチを削除する。
- PRマージ時は `--delete-branch` を優先する。
- 週次ジョブで残存ブランチを再確認する。

除外ルール:

- `main`
- `master`
- `save/*`
- `discuss/*`

自動クリーンアップ:

- ワークフロー: `.github/workflows/branch-cleanup.yml`
- トリガー:
  - 毎週日曜 03:15 UTC（JST 12:15）
  - `workflow_dispatch`
- 安全策:
  - オープンPRの head ブランチは削除しない
  - マージ後 2 日未満のブランチは削除しない
  - 1回の実行で最大 20 ブランチ
  - `dry_run` で事前確認可能

## Agent運用ルール

責任分離:

- Agent: 提案、テンプレ作成、テスト設計、dry-run差分提示
- Owner: 明示承認、ローカル実行、最終判断

基本ポリシー:

- 提案と実行を分離する。
- 破壊的操作（ブランチ削除、強制push、main直マージ）を自動実行しない。
- 影響が大きい操作は必ず dry-run と承認テンプレを使う。

承認テンプレ例:

```text
Propose: squash-merge PR #123 into main
Changes: src/foo.py, tests/test_foo.py
Require approval: yes

Owner reply to approve: "Approve: squash-merge PR #123 — approve-by: <name>"
```

## 障害時の復旧

- 原則: `git revert` を優先し履歴を保持する。
- 必要時: `save/main-backup-<timestamp>` を作成する。
- 参照: `git reflog`

## 関連資料

- `docs/branch-policy/branch-policy.md`
- `docs/branch-policy/branching-charter.md`
- `docs/pr-flow.md`
- `.github/workflows/pr-checks.yml`
- `.github/workflows/branch-cleanup.yml`

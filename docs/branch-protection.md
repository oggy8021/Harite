# Branch Protection（提案）

- 目的: `main` を安定運用し、誤マージや運用漏れを減らす。
- 適用対象: `main` ブランチ

## 主要ルール（提案）

- 必須ステータスチェック:
  - `Lint (ruff)`
  - `Test matrix (ubuntu-latest, 3.12)`
  - `Test matrix (macos-latest, 3.12)`
  - `Test matrix (windows-latest, 3.12)`
- `Include administrators`: 有効
- `Require branches to be up to date before merging`（strict）: 有効
- PR レビュー必須数: 当面は 0（将来 1 以上に引き上げ可）
- ブランチ名／PR本文チェック: `.github/workflows/pr-checks.yml` で実施（`save/*` はスキップ）

## 重要事項

- GitHub の Branch protection はリポジトリ管理者が **UI/Settings** で適用する。
- この文書と `.github/branch-protection.json` は「設定の参照・共有用」であり、これだけでは保護は有効化されない。

## 設定手順（管理者）

1. GitHub の対象リポジトリで `Settings` → `Branches` を開く。
2. `main` 向けの branch protection rule を新規作成または編集する。
3. 本文書の「主要ルール（提案）」に沿って項目を設定する。
4. 必要に応じて `.github/branch-protection.json` を見て差分を確認する。

## リスクと復旧

- 誤変更の取り消しは `git revert` を優先し、履歴を保持する。
- 緊急退避が必要な場合は `save/main-backup-<timestamp>` ブランチを作成して保全する。

## 変更履歴

- 2026-03-18: 提案文書として再整理し、管理者UIでの適用が必要である点を明記。

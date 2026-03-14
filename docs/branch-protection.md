**Branch Protection（簡素化版）**

- 目的: 単一メンテナ向けにプロセスを簡素化し、日常開発の摩擦を減らす。

- 適用対象: `main` ブランチ

- 主要ルール（簡略）:
 - 主要ルール（簡略）:
  - 必須ステータスチェック: `Lint (ruff)` と `Test matrix (ubuntu-latest, 3.12)`, `Test matrix (macos-latest, 3.12)`, `Test matrix (windows-latest, 3.12)`（CI の各チェック名に正確に合わせること）
   - `Include administrators`: 有効（管理者も保護対象）
   - `strict` モード: 有効（マージ前にブランチを最新に合わせることを要求）
   - PR レビュー: 必須ではない（プロジェクト運用に応じて後で追加可）
   - ブランチ名／PR本文の自動検証: 無効

- リスクと復旧:
  - 誤った変更を取り消す必要がある場合は、まず `save/main-backup-<timestamp>` ブランチからリストア可能。
  - 小さな試案（仕様メモ等）は削除しても問題ない場合は `git revert` で取り消し、履歴を残すことを推奨。

- 設定手順（管理者が行う）:
  1. GitHub → Settings → Branches → Branch protection rules を開く
  2. `main` のルールを編集し、上記の内容になるよう調整
  3. 必要ならこのファイル（`.github/branch-protection.json`）を参照して設定を確認

- 変更履歴:
  - 2026-03-14: 簡素化ルールを適用（作成者: repo maintainer）
  - 2026-03-14: 必須チェックを CI の実際のチェック名に合わせて微調整（linter + OS 別テストマトリクス）

# PRフロー運用ガイド

## 目的

- PRの作成からマージまでを短時間で再現できる手順として統一する。
- ブランチ命名の衝突や、本文不足によるCI失敗を未然に防ぐ。

## ブランチ命名ルール

- 形式: `feature|fix|docs|chore/<name>`
- `<name>` は英小文字・数字・`._-` を使用する。
- `001` のような連番のみは避け、`YYYYMMDD` や目的語を含める。

例:

- `docs/pr-flow-20260318`
- `chore/branch-cleanup-20260318`
- `fix/xfce-detect-timeout-20260318`

## 推奨ワークフロー

1. `main` から作業ブランチを作成する。
2. 小さくコミットし、PRを作成する。
3. PR本文テンプレート（概要/変更内容/テスト手順）を記入する。
4. CI通過を確認し、必要なら修正コミットを追加する。
5. `squash merge` で `main` に取り込む。
6. マージ後はブランチを削除する。

## レビュー手順（軽量）

- 変更量が小さいPRを優先し、1PRあたりの責務を絞る。
- レビュー時は次を確認する。
  - 命名規約に一致しているか。
  - PR本文が空でないか。
  - テスト/ドキュメント更新が必要な変更か。

## マージポリシー

- 基本方針: `squash merge`
- 理由: `main` の履歴を読みやすく保ち、revert単位を明確にするため。
- 例外: リリースや履歴保存の意図がある場合のみ `merge commit` を検討する。

## ペアセッション（TODO #9）

- 目的: Branch protection設定とPR運用を同時に確認し、設定漏れをなくす。
- 実施内容:
  - GitHub Settings上の `main` 保護設定確認
  - 必須チェック名とワークフローの整合確認
  - サンプルPRで命名・本文チェックの動作確認

## 関連資料

- `docs/branch-protection.md`
- `.github/workflows/pr-checks.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`

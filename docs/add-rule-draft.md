# Agent運用ルール（草案）

## 1. 目的

- AI支援（Copilot）による提案と、人（Owner）による実行の責任境界を明確化する。
- 破壊的操作の誤実行を防ぎ、安全な承認フローを定義する。

## 2. 適用範囲

- ローカル開発ワークフロー（ブランチ作成、PR作成、テスト設計、マージ、クリーンアップ等）。
- CIやリモート操作を含む変更は、Owner の明示承認を必須とする。

## 3. モデルに応じた制約

- `GPT4.1 以下`：簡易な補助のみ。設計や詳細なタスク分解は行わない。
- `GPT5-mini`：高文脈理解が必要なロードマップや詳細なタスク分解、不確実な自動化は避ける（提案は可）。
- `GPT5.3-Codex` 等の高能力モデル：Owner が許可すれば、より詳細な分解や代行提案が可能。ただし自動実行は不可。

> 注: 実際に利用可能なモデル名は運用環境に依存するため、使用前に確認すること。

## 4. 役割と責任

- Agent (Copilot): 提案、テンプレ作成、テスト設計、差分・コマンドの dry-run 出力、承認テンプレの提示。
- Owner: 明示的承認、ローカルでのコマンド実行、最終レビュー、障害発生時の判断・ロールバック実行。

## 5. 基本ポリシー

- 提案と実行は常に分離する。Agent は実行コマンドを提示するのみ。Owner が承認したら実行手順を提示する。
- 破壊的操作（例: ブランチ削除、強制プッシュ、main へのマージ）は自動実行しない。
- 自動化を行う場合は必ず `dry-run`（差分一覧）を提示し、Owner の承認を得る。

## 6. Git 操作ガイド（要約）

### ブランチ作成

- Agent: ブランチ名候補と実行コマンドを提示（例: `feature/issue-123-add-login`）。
- Owner: コマンドをコピーしてローカルで実行。

例（PowerShell）:

```powershell
git checkout -b feature/issue-123-add-login
```

### PR 作成

- Agent: PR本文テンプレ、レビューチェックリスト、関連チケットの一覧を生成。
- Owner: PR を作成し、CI 通過を待つ。

### マージ（squash）

- Agent: 実行前に `dry-run`（差分、コミット要約、コマンド一覧）を提示。
- Owner: 下記の承認テンプレで承認後、マージを実行。

承認テンプレ（例）:

```
Propose: squash-merge PR #123 into main
Changes: src/foo.py, tests/test_foo.py
Require approval: yes

Owner reply to approve: "Approve: squash-merge PR #123 — approve-by: <name>"
```

## 7. テストの分担

- Agent: テストケース設計、pytest 用コードの生成、実行コマンド（PowerShell/Bash 両対応）の提示。
- Owner: ローカルでテストを実行し、結果（成功/失敗ログ）を Agent に共有する。

例（PowerShell）:

```powershell
python -m pytest tests/test_example.py -q
```

例（Bash）:

```bash
python -m pytest tests/test_example.py -q
```

## 8. モデル切替のルール（提案）

- Agent は自動でモデルを切り替えない。代わりに以下のトリガーで「切替提案」を出す。
  - 入力が2回以上あいまいで追加確認が必要になったとき。
  - セキュリティ、認証、アクセス権に関わる操作を扱うと判断されたとき。
  - 影響範囲が大きい（例: 3 ファイル以上、主要モジュールの変更）と判定されたとき。

提案テンプレ（例）:

```
このタスクは高度な文脈理解が必要です。続行前に高性能モデルへの切替を検討してください。
```

## 9. 監査・ログ・フォールバック

- Agent が提示した提案・コマンド・承認履歴はログとして保存することを推奨（例: `logs/agent-actions.log`）。
- 簡易ログフォーマット例（1 行 JSON）:

```json
{"time":"2026-03-24T10:00:00Z","actor":"agent","action":"propose","command":"git checkout -b feature/...","details":"PR #123"}
```

- 失敗時の基本的なロールバック手順を明記する（例: `git revert`、`git reflog` の利用）。

簡易フォールバック例:

```powershell
# 直近コミットを取り消す（必要に応じて調整）
git revert <commit-hash>

# 参照が壊れた場合の確認
git reflog
```

## 10. 実現上の注意点

- 多くのプラットフォームでは Agent がモデルを自動で切り替える機能は制限されているため、切替は提案ベースにするのが現実的。
- 自動で PR やマージを行う場合は、dry-run の提示と Owner の明示承認を必須とする。

## 11. 次のアクション案

- この草案をレビューして、承認テンプレやログフォーマットのサンプルをさらに追加しますか？
- または `docs/git-operation-help/safe-squash-merge.md` に承認フローへのリンクを追加します（どちらを優先しますか）。

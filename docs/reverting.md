**戻し（revert）手順ガイド**

目的: 誤った変更や試験的な仕様メモを安全に取り消すための手順。

前提: 既に `save/main-backup-<timestamp>` のようなバックアップブランチが存在すること。

1) 変更を部分的に取り消す（推奨: `git revert`）

- 特定コミットだけを取り消したい場合（履歴を残す）:

```bash
# main にいることを確認
git checkout main
# 対象コミットのハッシュを確認
git log --oneline --decorate -n 20
# 例: commit-hash を指定して revert
git revert <commit-hash>
# push
git push origin main
```

- リモートに直接 push したくない場合は、revert 用ブランチを作って PR で取り込む:

```bash
git checkout -b revert/<short-hash>
git revert <commit-hash>
git push -u origin HEAD
# その後 GitHub 上で PR を作成してマージ
```

2) 大きく巻き戻したい（履歴書き換えを許容する場合）

- 注意: 履歴が書き換わるため、他の共同作業者がいる場合は注意が必要。バックアップブランチがあることを確認。

```bash
git checkout main
# target-commit-hash は残したい最新のコミット
git reset --hard <target-commit-hash>
git push --force origin main
```

3) バックアップから復元する

```bash
git fetch origin
git checkout -b restore-from-backup origin/save/main-backup-<timestamp>
# 必要に応じて変更を取得して main にマージするか、直接上書きする
```

4) 補助スクリプト

- `scripts/revert-commit.ps1` を使うと、履歴一覧を見て選んだコミットを revert して PR を作成する補助を行えます。

5) 運用ルール（提案）

- 小さな草案やメモのコミットは、`git commit --amend` や `git revert` で取り消し、履歴をきれいに保つ。
- 重要な履歴は `save/main-backup-<timestamp>` ブランチで保護する。

作業に迷ったら私に指示をください。
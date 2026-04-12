# squash merge後の整合確認チェック（追補）

**目的**

- squash merge 後に「コミットハッシュが変わった」ことと「内容が異なる」ことを混同しないよう、確認手順と判定ルールを明確にする。

**適用範囲**

- 対象: squash でマージされた PR の確認、または squash 前後で "浮いて見えるコミット" を判定する場面

---

## 判定（速攻チェック）

1. リモートとブランチの差分を確認

```bash
git fetch origin
git diff --name-status origin/main..HEAD
```

2. コミット存在の整合（ハッシュ差を見る）

```bash
git log --oneline origin/main..HEAD
git cherry -v origin/main HEAD
```

判定の要点:
- `git diff origin/main..branch` が空であれば内容は同一（ハッシュだけ違う可能性あり）
- `git cherry` は内容ベースでコミットが既に存在するかどうかを示す（+/- 記号）

---

## 実行（確認手順と判断ルール）

1. まず内容差を優先して確認する

```bash
git fetch origin
git diff origin/main..branch   # 内容ベースの差分
```

判断:
- 差分が無ければ → 内容は同一、ハッシュ差は squash 等の結果。運用上は問題なし。
- 差分があれば → 内容が異なるので修正または再確認が必要。

2. `git cherry` で既存コミット判定

```bash
git cherry -v origin/main branch
```

解釈:
- 出力に `+` があれば branch 上のコミットは origin に未反映（内容差あり）
- 出力に `-` があれば origin に同等のコミットが既に存在（ハッシュ差のみ）

---

## 修正案（差分がある場合）

- 差分がある場合は、まず作業ブランチにて修正を行い、再度 PR を作成するか、必要なら revert を実行する。
- squash 後に「同一内容だがハッシュが違う」だけなら通常は放置で良い（コミット履歴の見た目のみの問題）。

---

## 確認（操作後）

```bash
git fetch origin
git diff origin/main..branch || echo "no content diff"
git cherry -v origin/main branch
```

期待結果:
- 内容差が無ければ `git diff` が空、`git cherry` に `-` が多く出る場合があるが運用上問題なし

---

## クイックチェックリスト（PR/Issue 用短文）

- 判定: `git diff origin/main..branch` で内容差確認
- 実行: 差分あり→修正ブランチで対応、差分無→ハッシュ差のみで運用問題なし
- 確認: `git cherry -v origin/main branch` で同等コミットの有無を判断

# main に安全に戻る手順

以下は安全に main に戻るための一連のコマンド例（Windows PowerShell 推奨）。状況に合わせて実行してください。

事前チェック（未コミット変更がないか確認）

```powershell
git status --short
```

1) PR が未マージなら GitHub 上でマージ（Squash + 削除の例）

```powershell
gh pr merge <PR-number-or-branch> --squash --delete-branch
# 例: gh pr merge 123 --squash --delete-branch
```

1) リモートを取得して main に切替、最新を取り込む（安全な fast-forward）

```powershell
git fetch origin
git switch main
git pull --ff-only origin main
```

1) ローカルの feature ブランチを削除（マージ済の場合）

```powershell
git branch -d `ブランチ名`
# 強制削除（未マージの変更がある場合）:
# git branch -D `ブランチ名`
```

1) リモートブランチを削除（もし自動削除されていなければ）

```powershell
git push origin --delete `ブランチ名`
```

1) リモート参照を整理・確認

```powershell
git remote prune origin
git branch --merged main
git branch --list
```

1) ローカルでテストを実行（任意）

```powershell
.\.venv\Scripts\python -m pytest -q
# または対象テストだけ:
.\.venv\Scripts\python -m pytest -q tests/scripts/test_gui_layout_smoke.py
```

1) 最後の状態確認

```powershell
git status
git log --oneline -n 5
```

UNIX / macOS の場合の同等コマンド（参考）

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git branch -d `ブランチ名`
git push origin --delete `ブランチ名`
git remote prune origin
python -m pytest -q
```

補足注意事項

- `gh pr merge` を実行する前に PR の説明・CI 結果を確認してください。  
- `git branch -d` はマージ済みでないと失敗します。未マージで削除したければ `-D` を使います（注意）。  
- リモート削除は PR 作成時に `--delete-branch` を使っていれば自動で削除済みの場合があります（その場合は harmless になります）。

続けて私が実行（代行）することもできます。実行する場合は「代行して」と指示してください。


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

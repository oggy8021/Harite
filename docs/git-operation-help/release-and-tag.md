# リリースとタグ付けの手順

目的
- 安全にリリースタグを作成し、GitHub Release を発行するための手順を示します。

事前チェック
- CI が通っていること（必須）。
- main ブランチが最新であること。

手順（PowerShell）

```powershell
# 1. main に切替・最新取得
git switch main
git pull --ff-only origin main

# 2. 必要なテスト/ビルドを実行
python -m pytest -q

# 3. 注釈付きタグを作成
git tag -a v1.2.3 -m "Release v1.2.3: short notes"

# 4. タグをリモートに push
git push origin v1.2.3

# 5. （任意）gh CLI で Release を作成
gh release create v1.2.3 --title "v1.2.3" --notes-file RELEASE_NOTES.md
```

手順（Bash）

```bash
git switch main
git pull --ff-only origin main
python -m pytest -q
git tag -a v1.2.3 -m "Release v1.2.3: short notes"
git push origin v1.2.3
gh release create v1.2.3 --title "v1.2.3" --notes-file RELEASE_NOTES.md
```

補足とオプション
- 簡易リリースノート: `--notes "Short notes..."` を使用するとファイル不要。
- バイナリやビルドアーティファクトを添付する場合は `gh release upload` を利用。
- 署名付きタグ（GPG）を使用する場合は `git tag -s` を検討。

ロールバック（簡易）
- 既に push したタグを取り消す場合（注意: 共有リポジトリに影響あり）:

```powershell
git tag -d v1.2.3
git push origin --delete v1.2.3
```

チェックリスト（リリース前）
- [ ] CI が green
- [ ] リリースノート準備済み
- [ ] バイナリ/アセットが揃っている（必要な場合）
- [ ] チームにリリース予定を告知済み

注意事項
- 公開済みのタグを削除／上書きする操作は協業に影響するため、事前に合意を取りましょう。

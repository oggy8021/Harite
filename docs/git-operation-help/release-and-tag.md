# リリースとタグ付けの手順

目的

- 安全にリリースタグを作成し、GitHub Release を発行するための手順を示します。
- current `v1.0.0` release では、GitHub Releases に `dist/harite-1.0.0-py3-none-any.whl` と `dist/harite-1.0.0.tar.gz` を添付して公開します。

事前チェック

- CI が通っていること（必須）。
- main ブランチが最新であること。
- [docs/release-readiness-checklist.md](docs/release-readiness-checklist.md) の未完了項目が release 判断上許容できる状態であること。
- [docs/release-notes-draft.md](docs/release-notes-draft.md) を GitHub Release 本文の原稿として使えること。

手順（PowerShell）

```powershell
# 1. main に切替・最新取得
git switch main
git pull --ff-only origin main

# 2. 必要なテスト/ビルドを確認
python -m pytest -q tests
python -m build --sdist --wheel

# 3. 注釈付きタグを作成
git tag -a v1.0.0 -m "Release v1.0.0"

# 4. タグをリモートに push
git push origin v1.0.0

# 5. gh CLI で Release を作成し、artifact を添付
gh release create v1.0.0 `
  --title "v1.0.0" `
  --notes-file docs/release-notes-draft.md `
  dist/harite-1.0.0-py3-none-any.whl `
  dist/harite-1.0.0.tar.gz
```

手順（Bash）

```bash
git switch main
git pull --ff-only origin main
python -m pytest -q tests
python -m build --sdist --wheel
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
gh release create v1.0.0 \
  --title "v1.0.0" \
  --notes-file docs/release-notes-draft.md \
  dist/harite-1.0.0-py3-none-any.whl \
  dist/harite-1.0.0.tar.gz
```

補足とオプション

- 簡易リリースノート: `--notes "Short notes..."` を使用するとファイル不要。
- 既に Release を作成済みで artifact だけ後から添付する場合は `gh release upload v1.0.0 dist/harite-1.0.0-py3-none-any.whl dist/harite-1.0.0.tar.gz` を利用。
- 署名付きタグ（GPG）を使用する場合は `git tag -s` を検討。

ロールバック（簡易）

- 既に push したタグを取り消す場合（注意: 共有リポジトリに影響あり）:

```powershell
git tag -d v1.0.0
git push origin --delete v1.0.0
```

チェックリスト（リリース前）

- [ ] CI が green
- [ ] リリースノート準備済み
- [ ] `dist/harite-1.0.0-py3-none-any.whl` と `dist/harite-1.0.0.tar.gz` が揃っている
- [ ] チームにリリース予定を告知済み

注意事項

- 公開済みのタグを削除／上書きする操作は協業に影響するため、事前に合意を取りましょう。

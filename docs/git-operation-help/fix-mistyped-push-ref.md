# 誤push参照の修正ガイド

**目的**

- リモートに誤った参照（例: `origin/feature/...` を誤って `git push origin origin/feature/...` などで作成）を作ってしまった場合の安全な修正手順を示す。

**適用範囲**

- 対象: リモートに不要なリファレンス（ブランチ参照）が作成されたケース
- 前提: リモートの不要参照削除は影響範囲を確認した上で実施する。

---

## 判定（速攻チェック）

```bash
git fetch origin --prune
git ls-remote --refs origin | sed -n '1,20p'
git branch -r --sort=authordate | sed -n '1,40p'
```

判定ポイント:

- 削除対象のリファレンス名を正確に特定する（例: `refs/heads/origin/feature/foo` や `origin/origin/feature/foo` のような重複参照）

---

## 実行（最短手順）

注: リモート参照の削除は取り消しが困難なため、対象名を二重に確認すること。

1) 正しいブランチへ再push（もしローカルに正しいブランチがある場合）

```bash
git push origin feature/your-topic:feature/your-topic
```

1) 不要なリファレンスを削除する（安全な方法）

```bash
git push origin --delete "origin/feature/foo"   # リモートでの不要参照削除
# あるいは
git push origin :refs/heads/origin/feature/foo
```

1) 削除後の確認

```bash
git fetch origin --prune
git ls-remote --heads origin | grep feature/foo || echo "deleted"
```

---

## 代替（リモート参照の巻き戻しが必要な場合）

- 参照名が誤っているだけで中身は正しいブランチがある場合は、不要参照を削除して正しい参照へ再pushするだけで十分です。
- 誤ってプッシュした内容自体を取り消す必要がある場合は、まず退避ブランチを作成してから `git revert` または合意の上で `--force-with-lease` を使用してください。

---

## 確認（操作後）

```bash
git fetch origin --prune
git branch -r | grep feature/your-topic || echo "ok"
```

確認ポイント:

- 不要参照がリモートから消えていること
- 正しいブランチがリモートに存在すること

---

## クイックチェックリスト（PR/Issue 用短文）

- 判定: `git ls-remote --refs origin` で不要参照名を特定
- 実行: 正しいブランチへ `git push` → 不要参照を `git push origin --delete <ref>` で削除
- 確認: `git fetch --prune` 後に `git ls-remote` で削除を確認

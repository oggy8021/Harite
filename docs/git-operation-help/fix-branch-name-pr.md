# ブランチ命名エラー対応（PR再発行まで）

**目的**

- ブランチ命名規約に違反した場合の復旧手順（rename で済むケース、PR 再発行が必要なケース）を定型化する。

**適用範囲**

- 対象: 命名規約違反で PR が開かれている、あるいはローカル/リモートのブランチ名が誤っているケース。

---

## 判定（速攻チェック）

```bash
git branch --show-current
git remote show origin | sed -n '1,120p'
git ls-remote --heads origin | grep "your-branch-name\|feature"
```

判定ポイント:
- ローカルのみの誤名か（まだ push していない）
- 既に origin に同名ブランチや PR が存在するか

---

## 実行（ケース分岐）

### A: ローカルのみ / rename で済む場合

1. ブランチ名を変更

```bash
git branch -m old-name new-name
git push -u origin new-name
# 必要なら古いリモート参照を削除
git push origin --delete old-name || true
```

2. 既存の PR がないか確認。PR がない場合は通常通り新しいブランチ名で PR を作成。

---

### B: 既に PR が作成されている / rename で対応できない場合（PR 再発行）

1. 既存 PR の状態を確認し、必要ならコメントで事情を説明してクローズする。テンプレ例は下記。

2. ローカルで新しいブランチを作成して変更を移す（cherry-pick など）

```bash
git switch -c feature/new-name
git cherry-pick <コミット範囲>   # 必要に応じて
git push -u origin feature/new-name
```

3. 新しいブランチで PR を再発行し、旧 PR は閉じる。

---

## 旧 PR close 時の定型コメント例

```
Closing this PR because branch name did not follow project naming rules.
Changes have been moved to `feature/new-name` and a new PR has been opened: <PR link>.
```

---

## 確認（操作後）

```bash
git fetch origin --prune
git branch -r | grep new-name
```

確認ポイント:
- 新しいブランチが origin に存在すること
- 旧ブランチ／PR がクローズ済みであること

---

## クイックチェックリスト（PR/Issue 用短文）

- 判定: 影響はローカルのみか、既に PR があるか？
- 実行: ローカルのみ→`git branch -m` + `git push -u origin` / PR がある→変更移行して新PRを作る
- 確認: `git fetch --prune` と `git branch -r` で新ブランチの存在を確認

# Draft → Branch ワークフロー

目的
- main 上で作成したドラフト（未整理のコミット／ワーキングツリー）を安全に新しいブランチに移し、PR を作成する手順を示します。

前提
- 可能であれば「ブランチ作成 → ドラフト作成 → コミット」の順に作業するのが最も安全です。

ケース A: ドラフトがワーキングツリー（未コミット）の場合（推奨）

```powershell
# main にいる状態で新ブランチを作成してドラフトを含める
git switch -c feature/ISSUE-123-draft
git add path/to/draft.md
git commit -m "chore: add draft for ISSUE-123"
git push -u origin feature/ISSUE-123-draft

# 必要ならPRを作成（gh CLIを例）
gh pr create --fill
```

ケース B: ドラフトが main にコミット済みで既に push されている場合

手順（安全な移動）

```powershell
# 1) 新ブランチを作成してコミットを取り込む
git switch -c feature/ISSUE-123-draft

# 2) 新ブランチを push
git push -u origin feature/ISSUE-123-draft

# 3) main に戻ってドラフトを取り除く（公開済みなら revert を推奨）
git switch main
git revert <commit-hash-that-added-draft> --no-edit
git push origin main
```

補足: ドラフト追加コミットが他の変更と混ざっている場合は、`git cherry-pick` や `git rebase -i` で必要なコミットのみ抽出する方法もある。

ケース C: ドラフトが main にコミット済だがまだ push していない（ローカルのみ）

```powershell
# 新しいブランチを作成すればドラフトコミットはそのブランチに残る
git switch -c feature/ISSUE-123-draft
git push -u origin feature/ISSUE-123-draft

# main に戻す場合は必要に応じて reset を利用（ローカル未共有の時のみ推奨）
git switch main
git reset --hard origin/main
```

注意点
- 可能なら main 上でレビューに出さない（未整理の）コミットは避ける。
- main から履歴を書き換える（force push）操作は協業者に影響するため、原則使わない。どうしても必要な場合は事前合意とバックアップを必須とする。
- PR 作成時は PR テンプレに「このブランチは main で作成したドラフトを移したものです」など注記しておくと親切。

チェックリスト（ドラフト→ブランチ）
- [ ] 新ブランチにドラフトが含まれていることを確認
- [ ] main の不要コミットを revert した（公開済なら revert）
- [ ] PR を作成し、CI を回す

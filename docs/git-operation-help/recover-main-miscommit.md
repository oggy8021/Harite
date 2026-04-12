# main誤コミット復旧ガイド

**目的**

- `main` に誤ってコミット/プッシュした際に、迅速かつ安全に復旧経路を選び実行できるようにする。

**適用範囲**

- 対象: `main` ブランチ上の誤コミット
- 前提: 共有リポジトリでは履歴改変は最終手段とし、チーム合意を必須とする。

---

## 判定（速攻チェック — 判定→実行→確認 の順で実施）

1. 現在の状態確認

```bash
git status -sb
git log --oneline --decorate -n 5
```

判定目安:

- 出力に `main...origin/main` があり `ahead` が付く → ローカルに差分（未push）
- `origin/main` 側に進んでいる（origin 上に反映済み）→ push 済み

---

## 実行（プロジェクトのブランチ運用に合わせた推奨手順）

注意: 破壊的操作は最終手段。まずは作業ブランチを作って退避する方針を優先する。

---

### 修正手順 A — `main` へ未 push の場合（推奨）

1. 誤コミットを退避するブランチを作成

```bash
git switch -c feature/your-topic-$(date +%Y%m%d)
```

1. `main` に戻す

```bash
git switch main
```

1. `main` を `origin/main` に一致させる

```bash
git fetch origin --prune
git reset --keep origin/main
```

1. 退避ブランチを push

```bash
git switch feature/your-topic-$(date +%Y%m%d)
git push -u origin feature/your-topic-$(date +%Y%m%d)
```

この手順はローカルの誤コミットを安全に退避し、`main` を origin と一致させるための一般的で安全な方法です。

---

### 修正手順 B — `main` へ push 済みの場合（推奨フロー）

1. 誤コミットを作業ブランチとして残す

```bash
git switch -c feature/your-topic-$(date +%Y%m%d)
```

1. そのブランチを push

```bash
git push -u origin feature/your-topic-$(date +%Y%m%d)
```

1. `main` に戻る

```bash
git switch main
```

1. `main` 上の誤コミットを打ち消す（取り消しコミットを作成）

```bash
git revert <誤コミットSHA>
git push origin main
```

この方法は履歴を書き換えず、他の開発者への影響を最小化します。

---

### 履歴書き換えが本当に必要な場合（最終手段）

履歴書き換えを行う前に、必ず関係者の合意を得てください。影響範囲の通知と記録を必須とします。

```bash
git switch main
git reset --hard <修正したい親SHA>
git push --force-with-lease origin main
```

`--force-with-lease` を使い、他者の変更を上書きしないよう注意してください。

---

## 確認（操作後のチェック）

```bash
git fetch origin
git log --oneline -n 5
git status -sb
git log --oneline origin/main -n 5
```

確認ポイント:

- 期待した退避ブランチが存在し、必要なら push されていること
- `main` が `origin/main` と一致していること（または取り消しコミットが反映されていること）
- 他の開発者の作業を上書きしていないこと

---

## 事後対応・記録

- 操作手順と理由を短く Issue または PR に記録する（影響、実施者、日時）。
- 強制 push を行った場合は、影響を受ける開発者へ必ず直接通知する。

---

## 備考（環境差）

- Windows (Git for Windows): 上記コマンドは Git Bash / PowerShell で実行可能。GUI クライアントを使う場合は「reset」「revert」「push」の操作がどのように行われるかを併記することを推奨する。
- CI が `main` の更新をトリガーする場合は、CI 側の挙動（自動デプロイ等）を確認してから操作する。

---

## クイックチェックリスト（PR/Issue に貼れる短文）

- 判定: コミットは未push / push済み のどちらか？
- 実行: 未push→`git reset --hard HEAD~1`（例） / push済み→`git revert <SHA>` を実行
- 確認: `git log` と `git status` で状態を確認

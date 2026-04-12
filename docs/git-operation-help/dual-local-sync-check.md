# 2ローカル環境同期チェック手順（Windows / XFCE）

**目的**

- 複数端末（例: Windows と XFCE デスクトップ）で同一リポジトリの HEAD が一致しているかを簡単かつ確実に判定する手順を提供する。

**適用範囲**

- 対象: ローカル2台以上で同一コミットを参照しているか即座に確認したいケース
- 前提: 両端末で `git fetch origin` が実行できるネットワーク環境

---

## 判定（3コマンドで迅速確認）

1. 現在の HEAD を確認

```bash
git rev-parse HEAD
```

1. ワークツリーの状態（差分/ブランチ）を確認

```bash
git status -sb
```

1. 直近コミット履歴を簡潔に確認

```bash
git log --oneline -n 3
```

判定基準（短く）:

- 両端末で `git rev-parse HEAD` の出力が同一 → 同一 HEAD
- `git status -sb` で一方に `ahead`/`behind` 表示がある → 差分あり
- `git log` の先頭が異なる場合は、コミット不一致

---

## 実行（同期が取れていない場合の対処）

- 端末Aで `git fetch origin`、端末Bでも `git fetch origin` を実行してリモートとの差を確認する。差分がローカルだけのケースは退避ブランチを作成して push することを推奨する。

例: 端末で差分がある場合の安全な退避

```bash
# 退避ブランチ作成
git switch -c feature/save-work-YYYYMMDD
git push -u origin feature/save-work-YYYYMMDD
# main 等に戻し、origin と一致させる
git switch main
git fetch origin --prune
git reset --keep origin/main
```

---

## 環境差の注意点

- Windows (Git for Windows / PowerShell): `git status -sb` の表示は同等。改行コードや改行表示差に注意。
- XFCE 等の Linux 環境: 標準の Git コマンドで差分確認可能。ファイルモード差（executable bit）があると差分に出る場合がある。

---

## 確認（操作後）

```bash
git fetch origin
git rev-parse HEAD
git status -sb
```

期待結果:

- 両端末で `git rev-parse HEAD` が同一、`git status -sb` がクリーンまたは同一表示であること

---

## クイックチェックリスト（PR/Issue 用短文）

- 判定: `git rev-parse HEAD` / `git status -sb` / `git log --oneline -n 3` を両端末で実行
- 実行: 差分がある場合は退避ブランチを作成して push し、`main` を `origin/main` に合わせる
- 確認: 両端末で `git rev-parse HEAD` が一致することを確認

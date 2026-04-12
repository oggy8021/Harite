# Git運用リカバリ 作業指示バックログ

最終更新: 2026-04-12

## 目的

- 過去に複数回発生した Git 運用トラブルを、低コストで再発防止できる文書に分解する。
- mini モデルでも処理しやすい粒度（1タスク=1PR）で、継続的に整備する。

## 運用ルール

- 1タスク = 1PR。
- 変更対象は原則 `docs/git-operation-help/` のみ。
- 各PRで追加する手順は「判定 -> 実行 -> 確認」の順に固定する。
- コマンド例は 10 行以内を目安にする。

## タスク一覧（1-7）

### 1. main誤コミット復旧ガイド（未push / push済み分岐）

- 目的:
  - `main` に誤ってコミットした時の復旧判断を高速化する。
- 成果物:
  - `docs/git-operation-help/recover-main-miscommit.md`
- 必須内容:
  - 判定フロー（未push / push済み）
  - 分岐ごとの最短コマンド
  - 最終整合確認コマンド
- 完了条件:
  - 5分以内で復旧経路を選べる。

### 2. 誤push参照の修正ガイド

- 目的:
  - `git push origin origin/feature/...` のような誤指定 push の復旧を定型化する。
- 成果物:
  - `docs/git-operation-help/fix-mistyped-push-ref.md`
- 必須内容:
  - 正規ブランチへの再push
  - 不要参照の削除
  - `ls-remote` での確認例
- 完了条件:
  - 削除対象と残す対象を誤らない。

### 3. ブランチ命名エラー対応（PR再発行まで）

- 目的:
  - 命名規約違反時の復旧（rename可能/不可）を迷わず実施する。
- 成果物:
  - `docs/git-operation-help/fix-branch-name-pr.md`
- 必須内容:
  - renameで済むケース
  - PR再発行が必要なケース
  - 旧PR close時の定型コメント
- 完了条件:
  - `rerun` で直らない理由が明記されている。

### 4. 2ローカル環境同期チェック手順（Windows/XFCE）

- 目的:
  - 複数端末で同一 HEAD を即確認できるようにする。
- 成果物:
  - `docs/git-operation-help/dual-local-sync-check.md`
- 必須内容:
  - `git rev-parse HEAD`
  - `git status -sb`
  - `git log --oneline -n 3`
  - 判定基準（同一/不一致）
- 完了条件:
  - 3コマンドで同期状態を判定できる。

### 5. squash merge後の整合確認チェック追補

- 目的:
  - 「コミットハッシュ差」と「内容差」を混同しないようにする。
- 成果物:
  - 既存更新: `docs/git-operation-help/safe-squash-merge.md`
- 必須内容:
  - `git diff origin/main..branch` の見方
  - `git cherry` の見方と注意
  - 内容同一時の判断ルール
- 完了条件:
  - “浮いて見えるコミット” の誤判定が減る。

### 6. draft資材のブランチ退避手順の強化

- 目的:
  - main上作業を未然に減らす。
- 成果物:
  - 既存更新: `docs/git-operation-help/draft-to-branch.md`
- 必須内容:
  - 作業前プリフライト（現在ブランチ確認）を先頭化
  - 誤配置時の復旧導線リンク
- 完了条件:
  - 予防手順が復旧手順より先に提示される。

### 7. リリース系操作の「やってはいけない」短冊追記

- 目的:
  - タグ/リリース運用での誤操作リスクを下げる。
- 成果物:
  - 既存更新: `docs/git-operation-help/release-and-tag.md`
- 必須内容:
  - 禁止操作リスト
  - 実行前チェック
  - 失敗時のロールバック入口
- 完了条件:
  - 失敗時に次の1手が明示される。

## 優先度（推奨）

1. Task 1
2. Task 2
3. Task 4
4. Task 5
5. Task 3
6. Task 6
7. Task 7

## 備考

- すべて docs-only で進行可能。
- 進捗は本ファイルに追記せず、各PR本文で管理する。

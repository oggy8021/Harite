# Harite 作業予定（日本語）

最終更新: 2026-03-20

## 先にここだけ見る（30秒版）

- 現在の進行中:
  - `Improve XFCE heuristics`（タスク #6）
- 直近で完了した運用整備:
  - タスク #9: ブランチ保護・PRフロー整理（反映済み）
  - タスク #10: 定期ブランチクリーンアップ運用化（反映済み）
  - タスク #12: CI に sdist/wheel ビルド job 追加（反映済み）
- 次に着手する候補:
  - タスク #6: `Improve XFCE heuristics` の運用検証継続

## 現在の優先タスク

1. 進行中: `Improve XFCE heuristics`（#6）
2. フォローアップ: リリース準備チェックリストに沿った検証ログ整理

## タスク一覧（状態つき）

1. ✅ 完了: ドキュメント整理（Docs consolidation）
2. ✅ 完了: `docs` 統合用 PR の作成（レビュー用）
3. ✅ 完了: バックアップとブランチ運用ポリシーのドキュメント化
4. ✅ 完了: ワーキングツリー中心のチャットレビュー運用導入
5. ✅ 完了: `docs` 配下ファイルの整理
6. 🟡 進行中: `Improve XFCE heuristics`
7. ✅ 完了: テスト強化（Docs 作成→優先ケース追加→CI 組合せ）
8. ✅ 完了: CI 戦略の見直し
9. ✅ 完了: ブランチ保護・PR フローのペアセッション（スケジュール）
10. ✅ 完了: 定期的なブランチクリーンアップ（運用ルール化）
11. ✅ 完了: リリース準備チェックリスト作成
12. ✅ 完了: CI: sdist/wheel ビルド job の追加

## #6 Improve XFCE heuristics のメモ

- ブランチ案: `feature/xfce-heuristics-001`
- 主要テーマ:
  - 正規化／別名対応
  - 複合トークン照合
  - インデックス照合
  - 解像度照合
  - 位置ヒューリスティック
  - 表示検出の堅牢化
  - XFCE 候補選択とフォールバック
  - テスト／CI 再現性（`xfconf-query` 模擬テスト）
- フォローアップ記録:
  - `docs/misc/xfce-followup-log.md`

## 新しい運用ルール（短縮版）

- ブランチ命名: `feature|fix|docs|chore/<task>-<YYYYMMDD>`
- `main` への直接 push はしない。PR 経由で `squash merge` を使う。
- コンフリクトはローカルで解消してから push/PR する。
- `save/*` はバックアップ用途（PRチェックのスキップ対象）。

## 参照ドキュメント

- `docs/branch-protection.md`
- `docs/pr-flow.md`
- `docs/branch-cleanup.md`
- `docs/release-readiness-checklist.md`
- `docs/misc/xfce-followup-log.md`
- `docs/misc/xfce-rollback-playbook.md`
- `.github/workflows/ci.yml`
- `.github/workflows/pr-checks.yml`
- `.github/workflows/branch-cleanup.yml`

## 次セッション開始テンプレ

以下をそのままチャットに貼れば再開しやすくなります。

```text
本日の再開: #6 / #11 / #12 のどれから着手するか決めたいです。
現状は docs 側の運用整備（#9/#10）は完了済みです。
まず最小PR単位を3つ提案してください。
```

## 履歴（要約）

- 作成日: 2026-03-14
- 2026-03-18 時点で #9/#10 は完了に更新
- 2026-03-20 時点で #11 は完了に更新
- 2026-03-20 時点で #12 は完了に更新
- 過去の詳細ログは Git 履歴と PR を参照

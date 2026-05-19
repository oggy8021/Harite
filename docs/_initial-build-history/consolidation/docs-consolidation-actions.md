# Docs Consolidation — 次バッチ作業（ローカルドラフト）

目的: 句読点・全角/半角スペース・コマンド表記の正規化を行い、日本語ドキュメントの可読性と一貫性を高める。

作業（ローカルで実行、未コミット）:
1.主要ファイル順に句読点と不要スペースの正規化（`docs/` 下の README 相当ファイルを優先）。
2.コマンド例の表記確認と統一（`git`/`gh` の使用例を検証）。
3.用語統一の最終スイープ（`main`、`feature/`、`タイプミス` 等）。
4.`docs/docs-consolidation-scan.md` と `docs/docs-consolidation-progress.md` を更新して作業ログを残す。

ワークフロー:

- 全てワーキングツリーでドラフト編集 → あなたがローカルで確認 → 承認を受けて commit→push→PR を実行。

備考: このファイルはローカルドラフトです。不要なら削除してください。

作成日: 2026-03-15

次の小タスク（優先順）:

- 作業を完了したファイルの一覧を `docs/docs-consolidation-progress.md` に追記する（差分サンプル付き）。
- ポリシー整合性草案を `docs/docs-consolidation-actions.md` に簡潔にまとめ、`docs/branch-policy.md` と `docs/agent-rules.md` の矛盾点を明示する。
- 全角/半角の最終スイープを終えたら、ワーキングツリーの変更点をまとめた短いレビューノートを作成する（レビュア向けチェックリスト付き）。

注意（作業ルール）:

- ここで行う変更は全て `feature/docs-consolidate-001` 上のローカルドラフトとする。`src/` には触れない。
- 先に push/PR は行わない。私（あなた）がローカルで確認し「commit and PR」と指示した時点でコミット→push→PR を実行する。
- 重要なポリシー変更や方針の明確化は別ファイル（`docs/docs-consolidation-policy.md`）として切り出し、レビューを求める。

次に行う作業: 全角/半角スペースと句読点の最終スイープ（現在進行中）。完了次第 `docs/docs-consolidation-progress.md` を更新します。

# Docs branch-policy follow-up TODO

目的: `feature/docs-branch-policy-followup` 上で残した作業の整理と優先付け

優先タスク（短い）

1. `docs/branch-policy.md` の最終レビューと細部調整
2. `docs/TODOs_jp.md` と `docs/docs-consolidation-plan.md` のタイプミス修正
3. CI の docs-diff チェックが通るようテストケースを確認
4. 不要なレポートファイルのクリーンアップ（`.gitignore` 既設定）
5. 小さな PR に分割するためのタスク分解

運用メモ:

- すべての編集は feature ブランチ上で `--dry-run` を実行し、レポートを確認してからコミット
- 大きな一括変換は CI の diff-size チェックで弾かれる可能性があるため、小さく切る

次のアクション候補:

- 今すぐ (A) 小PR用の最小差分を作る（私が作業します）
- (B) まず `docs/branch-policy.md` のレビューを行う（あなたが確認）

# docs スクリプト集

このディレクトリにはドキュメント整備を支援する簡易スクリプトが含まれます。

目的

- 大量の表記ゆれや置換の自動適用を支援する（事前に差分を確認してから適用すること）
- 誤った全角句読点や連番記号の修正を行う

主要スクリプト

- `apply_docs_replacements.py` — 文字列置換をバッチで適用（`--dry-run` と `--report` をサポート）
- `fix_enumerators.py` — 日本語文書の連番末尾の全角句点（例: `1。`）を半角`.` に戻す（`--dry-run` と `--report` をサポート）

推奨ワークフロー

1. 新しい feature ブランチを作る: `git switch -c feature/add-docs-scripts-README-001`
2. スクリプトをドライランで実行してレポートを確認する（破壊的変更はまだ行われない）

例: `fix_enumerators.py` のドライラン

```bash
python scripts/fix_enumerators.py --dry-run --report docs/enumerator-report.md
```

例: `apply_docs_replacements.py` のドライラン

```bash
python scripts/apply_docs_replacements.py --dry-run --report docs/replacements-report.md
```

1. レポート（`docs/enumerator-report.md` など）を確認して問題なければ実行（`--dry-run` を外す）
2. 変更をコミットして PR を作成する（`main` への直接 push は避ける）

注意事項

- スクリプトはコードブロックやインラインコードを扱うファイルでは置換をスキップするよう設計されていますが、完全自動化は危険です。必ずレポートを確認してからコミットしてください。
- 大きなレポート（多くのdiff）が出た場合は手動でレビューブランチを作り、ファイル単位で分割して PR を小さくすることを推奨します。

問題報告

- 問題や改善案はリポジトリの Issues にお願いします。

ライセンス

- リポジトリのライセンスに従います。

---
（この README は自動生成テンプレートです。必要に応じて編集してください。）

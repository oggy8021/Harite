
docstring-plan

## 依頼

- docstring 生成の基本ルール
  - Google Style で、各関数の `Summary`、`Args`、`Returns` を作成してください。
  - 説明文は 「日本語」 で、極力 「ショート（簡潔）」 に記述してください。
  - 4/9 の上位モデル（5.3-Codex）復帰時に設計意図が伝わる、最小限かつ的確な表現を優先してください。
- 型ヒント（Type Hints）の同期
  - コードに型ヒントがない場合は、推論して `(path: str) -> bool` のようにコード自体も補完してください。
  - docstring 内の型表記と、コード上の型ヒントを完全に一致させてください。
- 「Why（なぜ）」の抽出
  - 複雑な条件分岐や Linux/XFCE 固有の処理には、ソースコードから意図を汲み取り、「なぜこの処理が必要か」を 1 行でコメント `# ...` 追記してください

## スコープ

### 第1フェーズ

- src/harite/cli.py
- src/harite/config.py
- src/harite/core.py
- src/harite/plugins.py
- src/harite/workspace.py

### 第2フェーズ

- tests/*.py
- tests/cli/*.py
- tests/core/*.py
- tests/integration/*.py
- tests/workspace/*.py

### 対象外

scripts/

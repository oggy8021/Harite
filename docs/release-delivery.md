# Harite 配布と .venv 非依存実行手順

最終更新: 2026-03-20

## 目的

- 開発用 `.venv` を使わずに Harite を実行できる状態を再現可能にする。
- リリース時の配布物（`sdist` / `wheel`）と配布経路を固定化する。

## 配布物（Deliverables）

- `dist/harite-<version>-py3-none-any.whl`
- `dist/harite-<version>.tar.gz`

上記 2 つを GitHub Releases に添付して配布する。

## ビルド手順（作成側）

```bash
python -m build --sdist --wheel
```

成功時に `dist/` 配下へ `whl` と `tar.gz` が生成される。

## .venv 非依存のインストール手順（利用側）

### A。pipx 推奨（CLI ツール用途）

```bash
pipx install /abs/path/to/dist/harite-<version>-py3-none-any.whl
harite optimize --help
harite apply --help
```

### B。pip --user（pipx がない場合）

```bash
python -m pip install --user /abs/path/to/dist/harite-<version>-py3-none-any.whl
harite optimize --help
harite apply --help
```

## アンインストール手順

### A。pipx の場合

```bash
pipx uninstall harite
```

### B。pip --user の場合

```bash
python -m pip uninstall -y harite
```

## ロールバック手順

1. 現行版をアンインストールする。
2. 直前安定版の wheel を指定して再インストールする。
3. `harite optimize --help` が表示できることを確認する。

```bash
pipx install --force /abs/path/to/harite-<previous-version>-py3-none-any.whl
```

## 実測ログ（2026-03-20, Windows）

- `python -m build --sdist --wheel`: 成功
- クリーン venv で `pip install dist/*.whl`: 成功
- `.venv` 非依存で `harite optimize --help` / `harite apply --help`: 成功
- `pip uninstall -y harite`: 成功

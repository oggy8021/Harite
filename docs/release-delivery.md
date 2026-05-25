# Harite 配布と .venv 非依存実行手順

最終更新: 2026-05-26

## 目的

- 開発用 `.venv` を使わずに Harite を実行できる状態を再現可能にする。
- リリース時の配布物（`sdist` / `wheel`）と配布経路を固定化する。

## 現在の状態

- 対象リリースは `v1.0.0` 想定。
- [pyproject.toml](pyproject.toml) の version は `1.0.0` へ更新済み。
- current release 候補に対する `python -m build --sdist --wheel` は実施済み。
- clean install と uninstall の再確認は XFCE 実機で取得済み。
- rollback は今回の release では省略する。
- 本書は current release 用の実施手順と証跡置き場を兼ねる。

## 配布物（Deliverables）

- `dist/harite-<version>-py3-none-any.whl`
- `dist/harite-<version>.tar.gz`

上記 2 つを GitHub Releases に添付して配布する。

current release の配布経路

- 公開先: GitHub Releases
- 添付対象: `dist/harite-1.0.0-py3-none-any.whl`, `dist/harite-1.0.0.tar.gz`
- リリース本文の原稿: [docs/release-notes-draft.md](docs/release-notes-draft.md)

## ビルド手順（作成側）

```bash
python -m build --sdist --wheel
```

成功時に `dist/` 配下へ `whl` と `tar.gz` が生成される。current release では実行日時と対象コミットも併記する。

## .venv 非依存のインストール手順（利用側）

推奨取得環境

- release 向けの clean install / uninstall 証跡は、可能であれば XFCE 実機で取得する。
- その際は `.venv` を有効化しない状態で CLI help と `harite-gui` 起動導線も併せて確認する。
- `harite-gui` は host 環境側の GTK 3 / PyGObject runtime を前提にするため、XFCE 実機では `python3-gi` と GTK 3 系ライブラリの利用可否も併せて確認する。

### A。pipx 推奨（CLI ツール用途）

```bash
pipx install /abs/path/to/dist/harite-<version>-py3-none-any.whl
harite optimize --help
harite apply --help
harite slideshow --help
```

補足:

- `pipx` の既定は分離 venv のため、distro 提供の `python3-gi` をそのままは見られない。
- `harite-gui` の起動確認まで取りたい場合は、`pipx install --system-site-packages` を使って host 側の `python3-gi` を参照させる。

GUI 起動確認を含む実機検証コマンド例

```bash
pipx install --force --system-site-packages /abs/path/to/dist/harite-<version>-py3-none-any.whl
harite optimize --help
harite apply --help
harite slideshow --help
harite-gui
```

### B。pip --user（pipx がない場合）

```bash
python -m pip install --user /abs/path/to/dist/harite-<version>-py3-none-any.whl
harite optimize --help
harite apply --help
harite slideshow --help
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

今回の `v1.0.0` release では rollback 実証は省略する。以下は必要時の参考手順。

1. 現行版をアンインストールする。
2. 直前安定版の wheel を指定して再インストールする。
3. `harite optimize --help` と `harite apply --help` が表示できることを確認する。

```bash
pipx install --force --system-site-packages /abs/path/to/harite-<previous-version>-py3-none-any.whl
```

## current release 証跡

- [x] `python -m build --sdist --wheel` 実行結果を記録した。
- [x] XFCE 実機で `pipx install --system-site-packages` による clean install 結果を記録した。
- [x] XFCE 実機で `.venv` 非依存の `harite optimize --help` / `harite apply --help` / `harite slideshow --help` / `harite-gui` 起動導線を確認した。
- [x] XFCE 実機で uninstall の結果を記録した。
- [ ] XFCE 実機で rollback の結果を記録した。（今回の release では省略）

実施メモ

- 日時: 2026-05-26
- 対象コミット: current working tree on `chore/release-v1.0.0`
- 実施環境: Windows / Python 3.12.10 virtual environment
- build:
  - コマンド: `c:/Users/oggy_/Develop/Repos/Harite/.venv/Scripts/python.exe -m build --sdist --wheel`
  - 結果: 成功
  - 生成物: `dist/harite-1.0.0-py3-none-any.whl`, `dist/harite-1.0.0.tar.gz`
  - 補足: setuptools から `project.license` と `tool.setuptools.license-files` に関する deprecation warning が出るが、build 自体は成功した。
- clean install:
  - 状態: XFCE 実機で一部取得済み
  - 実施結果: `pipx install --force --system-site-packages ./dist/harite-1.0.0-py3-none-any.whl` で install 成功
  - 実施結果: `.venv` 非依存の `harite optimize --help`、`harite apply --help`、`harite slideshow --help`、`harite-gui` 起動確認に成功
  - 補足: `pipx` の既定インストールでは分離 venv から `python3-gi` を見られず、`harite-gui` が `No module named 'gi'` で失敗した。`--system-site-packages` 付き install では起動できた。
  - 補足: この Windows 作業環境では `pipx` は利用不可だった。release 証跡は XFCE 実機の取得結果を優先する。
- uninstall:
  - 実施結果: XFCE 実機で uninstall 確認済み
  - 補足: clean install 確認の流れの中で `pipx uninstall harite` を実施し、削除導線を確認した。
- rollback:
  - 状態: 省略
  - 補足: 直前安定版 wheel を使った再インストール確認は今回の release では実施しない。
- 補足: 旧 2026-03-20 の実測ログは current release の証跡としては扱わない。

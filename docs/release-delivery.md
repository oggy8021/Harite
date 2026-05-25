# Harite 配布と .venv 非依存実行手順

最終更新: 2026-05-25

## 目的

- 開発用 `.venv` を使わずに Harite を実行できる状態を再現可能にする。
- リリース時の配布物（`sdist` / `wheel`）と配布経路を固定化する。

## 現在の状態

- 対象リリースは `v1.0.0` 想定。
- [pyproject.toml](pyproject.toml) の version は `1.0.0` へ更新済み。
- current release 候補に対する `python -m build --sdist --wheel` は実施済み。
- clean install、uninstall、rollback の再確認は XFCE 実機で取得予定。
- 本書は current release 用の実施手順と証跡置き場を兼ねる。

## 配布物（Deliverables）

- `dist/harite-<version>-py3-none-any.whl`
- `dist/harite-<version>.tar.gz`

上記 2 つを GitHub Releases に添付して配布する想定とする。

## ビルド手順（作成側）

```bash
python -m build --sdist --wheel
```

成功時に `dist/` 配下へ `whl` と `tar.gz` が生成される。current release では実行日時と対象コミットも併記する。

## .venv 非依存のインストール手順（利用側）

推奨取得環境

- release 向けの clean install / uninstall / rollback 証跡は、可能であれば XFCE 実機で取得する。
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
- `harite-gui` の起動確認まで取りたい場合は、`pipx` 側で system site packages を見せるか、次の `pip --user` 手順を使う。

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

1. 現行版をアンインストールする。
2. 直前安定版の wheel を指定して再インストールする。
3. `harite optimize --help` と `harite apply --help` が表示できることを確認する。

```bash
pipx install --force /abs/path/to/harite-<previous-version>-py3-none-any.whl
```

## current release 証跡

- [x] `python -m build --sdist --wheel` 実行結果を記録した。
- [ ] XFCE 実機で `pipx install` または `pip install --user` による clean install 結果を記録した。
- [ ] XFCE 実機で `.venv` 非依存の `harite optimize --help` / `harite apply --help` / `harite slideshow --help` / `harite-gui` 起動導線を確認した。
- [ ] XFCE 実機で uninstall / rollback の結果を記録した。

実施メモ

- 日時: 2026-05-25
- 対象コミット: current working tree on `chore/release-v1.0.0`
- 実施環境: Windows / Python 3.12.10 virtual environment
- build:
  - コマンド: `c:/Users/oggy_/Develop/Repos/Harite/.venv/Scripts/python.exe -m build --sdist --wheel`
  - 結果: 成功
  - 生成物: `dist/harite-1.0.0-py3-none-any.whl`, `dist/harite-1.0.0.tar.gz`
  - 補足: setuptools から `project.license` と `tool.setuptools.license-files` に関する deprecation warning が出るが、build 自体は成功した。
- clean install:
  - 状態: XFCE 実機で取得予定
  - 推奨確認項目: wheel install、`harite optimize --help`、`harite apply --help`、`harite slideshow --help`、`harite-gui` 起動導線、uninstall、rollback
  - 補足: `pipx` の既定インストールでは分離 venv から `python3-gi` を見られず、`harite-gui` が `No module named 'gi'` で失敗しうる。GUI 起動確認は `pipx` 側で system site packages を見せるか、`pip install --user` のような non-isolated install を優先する。
  - 補足: この Windows 作業環境では `pipx` は利用不可だった。release 証跡は XFCE 実機の取得結果を優先する。
- 補足: 旧 2026-03-20 の実測ログは current release の証跡としては扱わない。

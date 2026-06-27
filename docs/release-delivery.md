# Harite 配布と .venv 非依存実行手順

最終更新: 2026-06-21

## 目的

- 開発用 `.venv` を使わずに Harite を実行できる状態を再現可能にする。
- リリース時の配布物と配布経路を固定化する。

## 現在の状態（v2.0.2）

- 対象リリースは **`v2.0.2`**。
- [pyproject.toml](pyproject.toml) の version は **`2.0.2`**。
- Linux: `python -m build --sdist --wheel` で wheel / sdist を生成（CI `build-dist` も同手順）。
- Windows: PyInstaller **onedir**（[packaging/windows/README.md](packaging/windows/README.md)）。
- PyPI 公開は **未決**。配布は GitHub Release 添付・git clone を想定。

## 配布物（Deliverables）

### 全プラットフォーム（Python パッケージ）

- `dist/harite-<version>-py3-none-any.whl`
- `dist/harite-<version>.tar.gz`

### Windows（バイナリ、任意添付）

- `dist/windows/harite/` — `harite.exe`（CLI）
- `dist/windows/harite-qt/` — `harite-qt.exe`（Qt GUI）

各 onedir フォルダを zip して GitHub Releases に添付する。

## ビルド手順（作成側）

### sdist / wheel

```bash
python -m build --sdist --wheel
```

### Windows onedir

```powershell
pip install -e ".[gui-qt]"
pip install pyinstaller
python scripts/build_windows_pyinstaller.py
```

## .venv 非依存のインストール手順（利用側）

### A。pipx 推奨（CLI ツール用途）

```bash
pipx install /abs/path/to/dist/harite-<version>-py3-none-any.whl
harite optimize --help
harite apply --help
harite slideshow --help
```

### B。pip --user（pipx がない場合）

```bash
python -m pip install --user /abs/path/to/dist/harite-<version>-py3-none-any.whl
harite optimize --help
```

### GUI（Linux / Qt）

```bash
pip install /abs/path/to/dist/harite-<version>-py3-none-any.whl
pip install PyQt6   # または distro の python3-pyqt6 + --system-site-packages venv
harite-qt
# または harite-gui（同じ Qt 入口）
```

Linux / XFCE でメニュー起動:

```bash
harite install-desktop-entry
```

GTK / `python3-gi` は **v2 では不要**。

## 既存利用者向けアップデート

**対象:** v2.0.1 → v2.0.2 など、同一 major の patch 更新。Breaking change は [CHANGELOG.md](CHANGELOG.md) を参照。

**原則:** 設定 JSON（`harite-settings.json` / `harite-sources.json`）と remote cache は **そのまま**。本体だけ差し替え、GUI / CLI を再起動する。

| プラットフォーム | 保存場所（既定） |
| --- | --- |
| Linux / XFCE | `~/.config/harite/`（settings / sources）、`~/.cache/harite/remote-cache` 等 |
| Windows | `%APPDATA%\harite\`（settings / sources / remote-cache） |

### Linux / XFCE — wheel

```bash
# 1. harite-qt / harite-gui を終了
# 2. 新 wheel で上書き（初回と同じ install 経路）

pipx install --force /abs/path/to/dist/harite-2.0.2-py3-none-any.whl
# distro PyQt6 利用時（初回と同型）:
# pipx install --system-site-packages --force /abs/path/to/dist/harite-2.0.2-py3-none-any.whl

# pip --user の場合:
python3 -m pip install --user --upgrade /abs/path/to/dist/harite-2.0.2-py3-none-any.whl

harite --version   # → 2.0.2
harite-qt
```

- `harite install-desktop-entry` の再実行は不要（`.desktop` は維持）。
- slideshow 実行中に更新した場合は、更新後に Start し直す。

### Windows — onedir zip

```powershell
# 1. harite-qt.exe / harite.exe を終了
# 2. GitHub Release の zip を既存展開先へ上書き（harite/ と harite-qt/）
dist\windows\harite\harite.exe --version   # → 2.0.2
dist\windows\harite-qt\harite-qt.exe
```

- 展開先パスを変えなければ、ショートカット・`Path` は変更不要。
- インストーラはないため、アンインストール相当は旧フォルダ削除のみ（設定 JSON は `%APPDATA%\harite\` に残る）。

## アンインストール手順

### pipx

```bash
pipx uninstall harite
```

### pip --user

```bash
python -m pip uninstall -y harite
```

## 参照

- リリース本文原稿: [docs/release-notes-draft.md](docs/release-notes-draft.md)
- Windows ビルド詳細: [packaging/windows/README.md](packaging/windows/README.md)
- [CHANGELOG.md](CHANGELOG.md)

---

## 履歴（v1.0.0 以前の記録）

以下は v1.0.0 時点の証跡。v2 では GUI が Qt のみになった点に注意。

- 対象リリースは `v1.0.0` 想定。
- `harite-gui` は host 環境側の GTK 3 / PyGObject runtime を前提にした。
- XFCE 実機で `pipx install --system-site-packages` による clean install を実施済み（2026-05-26）。

# Harite 配布と .venv 非依存実行手順

最終更新: 2026-06-13

## 目的

- 開発用 `.venv` を使わずに Harite を実行できる状態を再現可能にする。
- リリース時の配布物と配布経路を固定化する。

## 現在の状態（v2.0.0）

- 対象リリースは **`v2.0.0`**。
- [pyproject.toml](pyproject.toml) の version は **`2.0.0`**。
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

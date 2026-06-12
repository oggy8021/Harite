# Windows 配布（PyInstaller onedir）

Harite v2 以降の Windows 向けバイナリは **PyInstaller `onedir`** でビルドする。onefile は使わない（起動・デバッグ・同梱のバランス）。

## 成果物

| フォルダ | EXE | 用途 |
| --- | --- | --- |
| `dist/windows/harite/` | `harite.exe` | CLI（console） |
| `dist/windows/harite-qt/` | `harite-qt.exe` | Qt GUI（windowed） |

各フォルダを zip して GitHub Release に添付する。

## 前提

- Windows 10/11
- Python 3.12+（開発用 `.venv` 推奨）
- リポジトリルートで editable install + Qt extra:

```powershell
pip install -e ".[gui-qt]"
pip install pyinstaller
```

## ビルド手順

```powershell
python scripts/build_windows_pyinstaller.py
```

スクリプトは次を行う:

1. `harite_app.svg` から `packaging/windows/harite_app.ico` を生成（未作成時のみ）
2. `harite` / `harite-qt` をそれぞれ onedir でビルド
3. `src/harite/gui/resources/` を datas として同梱

## アイコン

- **ウィンドウ / タスクバー / EXE:** `harite_app.svg` → `.ico`（`scripts/build_windows_icon.py`）
- **システムトレイ:** 実行時に package resources の `harite.svg` / `harite_light_bg.svg` を使用（#483）

Python ロゴ（`python.ico`）は使わない。

## 動作確認（例）

```powershell
dist\windows\harite\harite.exe --version
dist\windows\harite\harite.exe optimize --help
dist\windows\harite-qt\harite-qt.exe
```

## 利用者向け：スタートメニュー・PATH

Harite の Windows 配布物は **zip 展開のみ** で、インストーラやスタートメニュー登録は **行いません**。

| やりたいこと | 方法 |
| --- | --- |
| GUI をスタートメニューから起動 | `harite-qt.exe` をピン留め、または `.lnk` ショートカットを手動作成 |
| CLI を `harite` コマンドで呼ぶ | 展開した `harite` フォルダをユーザー環境変数 **Path** に追加（任意） |
| そのまま使う | `harite.exe` / `harite-qt.exe` をフルパスで実行 |

`harite install-desktop-entry` は Linux/XDG 専用で、Windows では使えません。

## 補足

- `harite-gtk` / GTK バックエンドは v2 で提供しない。
- `harite-gui` コンソール script は wheel 向け。Windows zip では `harite-qt.exe` を GUI 入口とする。

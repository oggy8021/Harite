# Harite リリースノート草案

最終更新: 2026-06-13  
対象バージョン: **v2.0.0**

## 概要

Harite v2 は **CLI v2** と **Qt 6 一本化** を軸とするメジャー版です。マルチディスプレイ壁紙の合成・適用・スライドショーを、検出ベースの幾何と settings JSON 中心の apply に整理しました。

## 今回の要点（Breaking）

- **`optimize`:** `--resolution` / `--two-screen` / display 手動指定を廃止。出力縮小は **`--canvas-scale`** のみ（配置は常に 100% 幾何）。
- **`apply`:** `--plugin` 等の CLI フラグを廃止。`harite-settings.json`（`-c`）で `plugin` / `apply_mode` を指定。
- **`embed-info`:** `params` → `settings`。`none` はオプション省略。
- **GUI:** GTK 廃止。`harite-gui` / `harite-qt` は Qt のみ。Windows 配布は `harite.exe` + `harite-qt.exe`（PyInstaller onedir）。

## 主な内容

### CLI

- ワークスペース検出と入力枚数から作業解像度を自動決定。
- 2 枚入力時はデュアル配置（検出失敗時はエラー、半分ずつフォールバック廃止）。
- `Placement:` 行出力、slideshow / install-desktop-entry 継続。

### GUI / トレイ

- Qt 6 メインウィンドウ、`harite_app.svg` ウィンドウアイコン。
- Windows タスクバー配色検出、XFCE ステータストレイ（ラスター pixmap）。

### 配布

| プラットフォーム | 成果物 |
| --- | --- |
| **全般** | `harite-2.0.0-py3-none-any.whl`, `harite-2.0.0.tar.gz` |
| **Windows** | `harite/` + `harite-qt/` onedir フォルダ（zip 添付） |

PyPI 公開は v2.0.0 時点では **未決**（旧 `wallpaperoptimizer` は登録削除済み）。GitHub Release 添付・git clone を想定。

## 移行メモ（1.x 利用者向け）

| 旧 | 新 |
| --- | --- |
| `harite optimize -r 3840x1080 ...` | 解像度指定なし（自動検出）。ファイル縮小は `--canvas-scale 50` 等 |
| `harite optimize --two-screen ...` | 2 枚入力で自動。Settings の Off も縮小/廃止 |
| `harite apply --plugin xfce ...` | `-c settings.json` の `plugin` キー |
| `harite-gui`（GTK 前提） | Qt + `python3-pyqt6`（Linux）または `harite-qt.exe`（Windows） |

## 検証サマリー

- `python -m pytest -q tests`
- `python -m build --sdist --wheel`
- オーナー実機: CLI / GUI / Windows / XFCE 回帰（housekeeping §4）

## 参照

- [CHANGELOG.md](CHANGELOG.md)
- [docs/release-delivery.md](docs/release-delivery.md)
- [packaging/windows/README.md](packaging/windows/README.md)
- [docs/working/20260612-pre-release-housekeeping.md](docs/working/20260612-pre-release-housekeeping.md)

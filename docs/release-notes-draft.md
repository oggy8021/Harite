# Harite リリースノート草案

最終更新: 2026-06-19  
対象バージョン: **v2.0.1**

## 概要

Harite v2.0.1 は **v2.0.0 直後の安定化パッチ**です。slideshow tick の継続性（JMA / display pause / pending apply）、トレイ導線の回帰修正、settings keyword 保持、list source の cursor 表示を中心に改善しました。

Breaking change はありません（CLI v2 / Qt 一本化は v2.0.0 のまま）。

## 今回の要点

### Slideshow 安定化（#492–#497, #503）

- JMA 更新なし tick は apply を skip（不要 optimize 回避）。
- display 一時失敗は **pause**（hard stop 回避）。復帰後に **pending remote apply** を回収。
- 縦長画像 + auto display scale の fit 失敗時は down-only フォールバック。
- tick 失敗時に tray / main / footer を同期し、footer に赤文字エラーを表示。

### GUI / トレイ

- トレイ → Settings / Color / About で main window を raise しない（#492）。
- Slideshow タブに list 型ソースの **cursor position chip**（#507）。
- pause 状態 UI sync、JMA chip コンパクト化（#512–#514）。

### Settings / 耐障害性

- Settings Save で keyword キーを保持（#496）。
- 0 バイト `harite-sources.json` / `harite-settings.json` を空として load（#505）。

### UX 改善

- running 中の interval / auto scale 変更を **次 tick へ延期**（#495）。

### リモートソース

- CODH kiriezu: 利用不可 manifest を retry 内で skip（#516）。

## 配布

| プラットフォーム | 成果物 |
| --- | --- |
| **全般** | `harite-2.0.1-py3-none-any.whl`, `harite-2.0.1.tar.gz` |
| **Windows** | `harite/` + `harite-qt/` onedir フォルダ（zip 添付） |

PyPI 公開は **未決**（v2.0.0 同様）。GitHub Release 添付・git clone を想定。

## 既存利用者向けアップデート

v2.0.0 から v2.0.1 へは **設定・CLI の移行作業は不要**です。配布物を差し替え、Harite を再起動してください。

| 環境 | 手順の要約 | 詳細 |
| --- | --- | --- |
| **Linux / XFCE** | `harite-2.0.1-py3-none-any.whl` で pipx / pip 上書き → `harite --version` 確認 → `harite-qt` 再起動 | [release-delivery.md §既存利用者向けアップデート](docs/release-delivery.md) |
| **Windows** | onedir zip で `harite/` / `harite-qt/` を上書き → `harite.exe --version` 確認 → EXE 再起動 | 同上、[README.md §アップデート](README.md) |

**保持されるもの:** `harite-settings.json`, `harite-sources.json`, remote cache, ピクチャ配下の slideshow 作業ディレクトリ。

**不要な作業:** `install-desktop-entry` の再実行（Linux）、Windows ショートカット / `Path` の作り直し（展開先パス不変時）。

## 検証サマリー

- `python -m pytest -q tests` — 2026-06-19 OK
- `python -m build --sdist --wheel` — 2.0.1 成果物
- オーナー実機: v2.0.1 候補マージ後の JMA / slideshow / tray 回帰 — **現動作 OK**

## 参照

- [CHANGELOG.md](CHANGELOG.md)
- [docs/release-delivery.md](docs/release-delivery.md)
- [docs/working/20260619-v2.0.1-release-housekeeping.md](docs/working/20260619-v2.0.1-release-housekeeping.md)
- [docs/working/finished/20260613-v2-post-release-fix-planning.md](docs/working/finished/20260613-v2-post-release-fix-planning.md)

# Harite リリースノート草案

最終更新: 2026-06-21  
対象バージョン: **v2.0.2**

## 概要

Harite v2.0.2 は **常駐運用 UX** のパッチです。OS ログイン autostart から Slideshow を条件付きで再開し、main window の × を tray 格納に変更します。console script が CLI フラグを無視していた不具合も修正しています。

Breaking change はありません（CLI v2 / Qt 一本化は v2.0.0 のまま）。

## 今回の要点

### セッション autostart — Slideshow 再開（#518）

- Slideshow タブ **「Resume slideshow on session startup」**（`startup_slideshow`）。
- 前回 **tray Quit 時に running** だった場合のみ、`harite-qt --no-present-ui-window --startup-launch` で自動 Start。
- `slideshow_was_running_at_exit` を settings に永続化（Stop / 意図的終了時は再開しない）。
- README に Windows Startup / XFCE autostart `.desktop` 手順（Harite 側の登録 CLI は提供しない）。

### tray 常駐 UX（#518）

- main window **×** → **hide**（終了しない）。完全終了は tray **Quit** のみ。
- `QApplication.setQuitOnLastWindowClosed(False)` — 非表示でもプロセス存続。

### 修正（#521）

- `harite-qt` / `harite-gui` console script と Windows PyInstaller 入口が `app_qt.run()` を直接呼び、`--startup-launch` / `--no-present-ui-window` が無視されていた問題。

## 配布

| プラットフォーム | 成果物 |
| --- | --- |
| **全般** | `harite-2.0.2-py3-none-any.whl`, `harite-2.0.2.tar.gz` |
| **Windows** | `harite-2.0.2-windows-cli.zip`, `harite-2.0.2-windows-gui.zip`（onedir） |

PyPI 公開は **未決**（v2.0.0 同様）。GitHub Release 添付・git clone を想定。

## 既存利用者向けアップデート

v2.0.1 から v2.0.2 へは **設定・CLI の移行作業は不要**です（新キー `startup_slideshow` は既定 `false`）。配布物を差し替え、Harite を再起動してください。

**autostart を使う場合:** OS 側の起動コマンドに `--no-present-ui-window --startup-launch` を付け、Slideshow タブで checkbox を ON にしてください（[README.md §セッション自動起動](README.md)）。

**× ボタン:** v2.0.2 以降、× は終了ではなく tray へ格納します。終了は tray **Quit** から行ってください。

| 環境 | 手順の要約 | 詳細 |
| --- | --- | --- |
| **Linux / XFCE** | `harite-2.0.2-py3-none-any.whl` で pipx / pip 上書き → `pip install -e` 後 `harite-qt --help` で flags 確認 → 再起動 | [release-delivery.md §既存利用者向けアップデート](docs/release-delivery.md) |
| **Windows** | onedir zip で `harite/` / `harite-qt/` を上書き → 版確認 → EXE 再起動 | 同上、[README.md §アップデート](README.md) |

**保持されるもの:** `harite-settings.json`, `harite-sources.json`, remote cache、slideshow 作業ディレクトリ。

## 検証サマリー

- `python -m pytest -q tests` — 2026-06-21 OK
- `python -m build --sdist --wheel` — 2.0.2 成果物
- オーナー実機: Windows / XFCE — tray-only 起動 + 条件付き auto-start — **OK**

## 参照

- [CHANGELOG.md](CHANGELOG.md)
- [docs/release-delivery.md](docs/release-delivery.md)
- [docs/working/20260621-v2.0.2-release-housekeeping.md](docs/working/20260621-v2.0.2-release-housekeeping.md)
- [docs/working/20260619-1430-startup-slideshow-resume-planning.md](docs/working/20260619-1430-startup-slideshow-resume-planning.md)

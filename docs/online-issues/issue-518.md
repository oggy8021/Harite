# Issue #518

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/518>
- opened: 2026-06-19
- title: `スタートアップで起動した場合に、Slideshowを停止時より再開する`
- labels: `enhancement`
- 報告: オーナー構想（web-ui 採用）
- 対象版: **v2.0.2**

## 事象

- 現状: GUI 起動時は **常に slideshow stopped**。OS ログイン後 autostart でも手動 Start が必要。
- 現状: main window **×** ボタンで **アプリ終了** → slideshow 停止（母体は × ≒ Invisible / hide）。

## 期待

- settings に **スタートアップフラグ**（`startup_slideshow`）を設ける。
- **解釈 B（確定）:** 前回 exit 時に slideshow **running だった場合のみ**、`--startup-launch` 付き autostart で再開。
- **Windows / XFCE:** OS スタートアップ登録は **ユーザー手動**（Harite は README 手順のみ。登録 CLI は提供しない）。
- **他 Linux:** 今回パス。

## 分類

- `enhancement` — GUI runtime / settings / tray 常駐 UX

## 関連

- planning: [20260619-1430-startup-slideshow-resume-planning.md](../working/20260619-1430-startup-slideshow-resume-planning.md)
- 正本（改定候補）: core-spec §6.3、gui-spec §5–§7
- 実装: `MainWindow.on_slideshow_start/stop`、`app_qt.run`、`settings.py`
- 関連 UX（判断待ち）: main window × → hide vs quit（§5 planning）

## 取り込み方針

- **planning 確定（2026-06-19）** → design slice → spec → テスト → impl
- v2.0.2 スコープ:
  - `startup_slideshow` + `slideshow_was_running_at_exit`（永続化）
  - `--startup-launch` + deferred auto-start
  - Slideshow タブ checkbox
  - README autostart 手順（Windows / XFCE）
  - （**確定**）× ボタン → hide（S1）。Quit のみ終了

## 調査メモ

### 現状（コード）

| 項目 | 状態 |
| --- | --- |
| `slideshow_running` | メモリのみ |
| × ボタン | `QMainWindow` クローズ → `QApplication` 終了（`QuitOnLastWindowClosed` 既定 true） |
| tray Invisible | `hide()` — slideshow 継続 |
| tray Quit | `qapp.quit()` |

### autostart Exec 例

```ini
Exec=harite-qt --no-present-ui-window --startup-launch
```

## オーナー判断（2026-06-19）

| # | 決定 |
| --- | --- |
| 1 | 解釈 **B**（前回 running 時のみ autostart 再開） |
| 2 | Slideshow タブ checkbox |
| 3–4 | Startup / autostart **登録 CLI なし**（README のみ） |
| 5 | **v2.0.2** |
| 6 | × ボタン **S1** — × = hide、終了は tray Quit のみ |

## resolution

**根本原因（2026-06-19 追記）:** `harite-qt` / `harite-gui` の console script および Windows `entry_qt.py` が `app_qt.run()` を直接呼んでおり、`--startup-launch` / `--no-present-ui-window` が **argparse を経由しない**ため無視されていた。対処: 入口を `app_qt.main()` に統一（#519 フォローアップ）。

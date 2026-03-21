# GUI Signal 対応表（旧 Glade -> 新 Controller）

最終更新: 2026-03-21

## 目的

- 旧 glade/ui の signal 名と、Harite GUI の controller メソッド対応を固定化する。
- 移植時に「どのイベントをどこへ移すか」を追跡可能にする。

## 前提

- 旧資産原本: `docs/legacy-ui/` 配下
- 新実装: `src/harite/gui/` 配下
- MVP は常駐機能（tray/indicator/daemon）を対象外とする。

## 対応表テンプレート

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| example.glade | btn_optimize | clicked | on_btn_optimize_clicked | OptimizeController.run_optimize | todo | |

## 抽出結果（wallpositapplet.glade）

外部 clone から取り込んだ `wallpositapplet.glade` の signal を分類した。

### MVP で扱う候補

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| wallpositapplet.glade | btnGetImgL / btnGetImgR | clicked | on_btnGetImg_clicked | MainWindow.on_pick_input | implemented | 左右個別入力はMVPで1入力欄へ統合も可 |
| wallpositapplet.glade | spnTopMergin/spnLMergin/spnRMergin/spnBtmMergin | value_changed | on_spnMergin_value_changed | MainWindow.on_change_margins | implemented | `--margins` へ集約 |
| wallpositapplet.glade | radFixed / radNoFixed | toggled | on_radFixed_toggled | MainWindow.on_toggle_fixed | implemented | `--fixed` へ反映 |
| wallpositapplet.glade | btnSave | clicked | on_btnSave_clicked | MainWindow.on_optimize | implemented | `optimize` 実行に対応 |
| wallpositapplet.glade | btnSetWall | clicked | on_btnSetWall_clicked | MainWindow.on_apply_dry_run / on_apply_do_it | implemented | `apply` の安全導線に分離 |
| wallpositapplet.glade | entPathL / entPathR | insert_text | on_entPath_insert_text | MainWindow.on_change_input_text | implemented | Phase 1 優先 |
| wallpositapplet.glade | WallPosit_MainWindow | delete_event | on_WallPosit_MainWindow_delete_event | MainWindow.on_close | implemented | Phase 1 優先 |

## Phase 1 優先実装（3 signal）

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| wallpositapplet.glade | entPathL / entPathR | insert_text | on_entPath_insert_text | MainWindow.on_change_input_text | implemented | 入力バリデーション |
| wallpositapplet.glade | btnSave | clicked | on_btnSave_clicked | MainWindow.on_optimize | implemented | optimize 実行導線 |
| wallpositapplet.glade | WallPosit_MainWindow | delete_event | on_WallPosit_MainWindow_delete_event | MainWindow.on_close | implemented | 常駐なし終了 |

### MVP では非対象（dropped）

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| wallpositapplet.glade | btnDaemonize | clicked | on_btnDaemonize_clicked | N/A | dropped | 常駐機能のためMVP非対象 |
| wallpositapplet.glade | btnCancelDaemonize | clicked | on_btnCancelDaemonize_clicked | N/A | dropped | 常駐機能のためMVP非対象 |
| wallpositapplet.glade | spnInterval | value_changed | on_spnInterval_value_changed | N/A | dropped | 定期実行非対象 |
| wallpositapplet.glade | btnAbout | clicked | on_btnAbout_clicked | N/A | dropped | MVP後回し |
| wallpositapplet.glade | btnHelp | clicked | (未指定) | N/A | dropped | MVP後回し |

### ダイアログ系（後続）

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| wallpositapplet.glade | ColorSelectionDialog | destroy | on_ColorSelectionDialog_destroy | MainWindow.on_close_color_dialog | implemented | プレースホルダでクローズイベントを記録 |
| wallpositapplet.glade | SrcdirDialog | destroy | on_SrcdirDialog_destroy | MainWindow.on_close_srcdir_dialog | implemented | プレースホルダでクローズイベントを記録 |
| wallpositapplet.glade | SaveWallpaperDialog | destroy | on_SaveWallpaperDialog_destroy | MainWindow.on_close_save_dialog | implemented | プレースホルダでクローズイベントを記録 |
| wallpositapplet.glade | SettingDialog | destroy | on_SettingDialog_destroy | MainWindow.on_close_settings_dialog | implemented | プレースホルダでクローズイベントを記録 |
| wallpositapplet.glade | ImgOpenDialog | destroy | on_ImgOpenDialog_destroy | MainWindow.on_close_open_image_dialog | implemented | プレースホルダでクローズイベントを記録 |
| wallpositapplet.glade | ErrorDialog | destroy | on_ErrorDialog_destroy | MainWindow.on_close_error_dialog | implemented | プレースホルダでクローズ時にエラー状態をクリア |

Status 値:
- todo
- mapped
- implemented
- dropped

## 非対象（MVP）

- indicator/tray 関連 signal
- daemon/timer 常駐関連 signal

## 作業手順

1. 原本 glade/ui を `docs/legacy-ui/` へ保管
2. signal 一覧をこの表へ転記
3. 新 controller 側の受け口を定義
4. dropped の理由を Notes に明記

## 受け入れ基準

- MVP 対象 signal がすべて `implemented` になっている
- `dropped` は理由が記録されている
- MainWindow 初期表示から optimize 実行までの signal が追跡できる

## 現在ステータス

- 2026-03-21 時点で、MVP 対象 signal はすべて `implemented`。

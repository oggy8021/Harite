# GUI Signal 対応表（旧 Glade -> 新 Controller / 履歴資料）

最終更新: 2026-04-18

## 位置づけ

- この文書は Phase 5 以前に作成・更新された旧 glade signal 対応の履歴資料である。
- current runtime の正本仕様を定義する文書ではない。
- Phase6 以降は、旧 signal 名と widget ID の証跡確認に限定して参照する。
- current runtime の構造判断は `gui-phase6-planning.md` と `gui-phase6-glade-adapter-judgement.md` を正本とする。

## 目的

- Phase 5 以前の移植検討で使っていた、旧 glade/ui の signal 名と controller 対応の記録を保持する。
- 後続フェーズで、旧 signal / widget の由来を追跡できるようにする。

## 前提

- 旧資産原本: `docs/legacy-ui/` 配下
- 新実装: `src/harite/gui/` 配下
- MVP は常駐機能（tray/indicator/daemon）を対象外とする。
- `src/harite/gui/resources/wallpositapplet.glade` は Phase6 で削除済みであり、本書は `docs/legacy-ui/wallpositapplet.glade` を参照する履歴文書として扱う。

## 対応表テンプレート

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| example.glade | btn_optimize | clicked | on_btn_optimize_clicked | OptimizeController.run_optimize | todo | |

## 抽出結果（wallpositapplet.glade）

外部 clone から取り込んだ `wallpositapplet.glade` の signal を、当時の移植判断用に分類した。

### 2026-04-13 全ボタン追跡（btn/tgl/rad）

- 目的: signal 対応だけでなく、ボタンフェイス（label/use_stock/relief）と旧実装ハンドラ根拠を一体で追跡する。
- 追跡対象: `docs/legacy-ui/wallpositapplet.glade` 内の `btn*` / `tgl*` / `rad*` 全件。
- 追跡証跡: `out/manual-validation/glade-button-face-trace-20260413.csv`

追跡サマリ:

- 総件数: 36
- `use_stock=True`: 31
- signal 定義あり: 34
- 旧実装ハンドラ解決済み: 30
- 未解決: 4

未解決4件の扱い:

- `btnClrPathL`, `btnClrPathR`
  - glade signal は `on_btnClrPath_clicked`。
  - 旧実装では `WindowBase._initializeWindow()` の `signal_autoconnect` 辞書で `on_btnClrPath_clicked -> btnGetImg_clicked` に束ねており、共有ハンドラ方式。
- `btnCancelSave`, `btnOpenSave`
  - 現行取り込み glade は `on_btnCancelSave_clicked` / `on_btnOpenSave_clicked`。
  	- 旧 `SaveWallpaperDialog.py` は `on_btnCancel_clicked` / `on_btnOpen_clicked` を接続しており、命名差分がある。
  	- 現行側は意味正規化として `on_btnCancelSave_clicked -> MainWindow.on_save_path_selection_canceled`、`on_btnOpenSave_clicked -> MainWindow.on_save_path_selected` を採用している。
  	- ただしこれは glade 資産側の話であり、current runtime の adapter / backend はすでに `on_save_path_selection_canceled` / `on_save_path_selected` / `on_SavePathDialog_destroy` へ移行済みである。

確度ラベル（本ファイルでの運用）:

- A: glade の face 定義 + 旧実装ハンドラの意味まで一致
- B: glade face は確認済みだが、ハンドラ名/接続で差分があり追加確認が必要
- C: 現行互換層で代替表現を用いるため意味同等性で担保

現時点判定:

- MainWindow の `tgl*`, `btnSave`, `btnSetWall` は A。
- `btnClrPath*`, `btnCancelSave`, `btnOpenSave` は B（命名・接続差分の追跡継続）。
- `btnClrPath*` は B（共有ハンドラ方式の継続可否を追跡）。
- `btnCancelSave`, `btnOpenSave` は A-（命名差分はあるが意味正規化で解消済み）。

### MVP で扱う候補

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| wallpositapplet.glade | btnGetImgL / btnGetImgR | clicked | on_btnGetImg_clicked | MainWindow.on_pick_input | implemented | 左右個別入力はMVPで1入力欄へ統合も可 |
| wallpositapplet.glade | spnTopMergin/spnLMergin/spnRMergin/spnBtmMergin | value_changed | on_spnMergin_value_changed | MainWindow.on_change_margins | implemented | `--margins` へ集約 |
| wallpositapplet.glade | radFixed / radNoFixed | toggled | on_radFixed_toggled | MainWindow.on_toggle_fixed | implemented | `--fixed` へ反映 |
| wallpositapplet.glade | btnSave | clicked | on_btnSave_clicked | MainWindow.on_save | implemented | 旧MainWindowの Save 導線。Optimize ボタン同義として扱わない |
| wallpositapplet.glade | btnSetWall | clicked | on_btnSetWall_clicked | MainWindow.on_apply | implemented | Phase6 では `Apply` 即時実行を正本とする |
| wallpositapplet.glade | btnSetColor | clicked | on_btnSetColor_clicked | MainWindow.on_set_color | implemented | 現時点は `planned` 明示（非透過化のため状態表示のみ先行） |
| wallpositapplet.glade | entPathL / entPathR | insert_text | on_entPath_insert_text | MainWindow.on_change_input_text | implemented | Phase 1 優先 |
| wallpositapplet.glade | WallPosit_MainWindow | delete_event | on_WallPosit_MainWindow_delete_event | MainWindow.on_close | implemented | Phase 1 優先 |

## Phase 1 優先実装（3 signal）

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| wallpositapplet.glade | entPathL / entPathR | insert_text | on_entPath_insert_text | MainWindow.on_change_input_text | implemented | 入力バリデーション |
| wallpositapplet.glade | btnSave | clicked | on_btnSave_clicked | MainWindow.on_save | implemented | Save（保存先選択+生成）導線 |
| wallpositapplet.glade | WallPosit_MainWindow | delete_event | on_WallPosit_MainWindow_delete_event | MainWindow.on_close | implemented | 常駐なし終了 |

### MVP では非対象（dropped）

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| wallpositapplet.glade | btnDaemonize | clicked | on_btnDaemonize_clicked | MainWindow.on_watch_start（planned） | dropped | watch 導線へ統合予定（MVPでは未実装） |
| wallpositapplet.glade | btnCancelDaemonize | clicked | on_btnCancelDaemonize_clicked | MainWindow.on_watch_stop（planned） | dropped | watch 導線へ統合予定（MVPでは未実装） |
| wallpositapplet.glade | spnInterval | value_changed | on_spnInterval_value_changed | MainWindow.on_watch_interval_change（planned） | dropped | watch 間隔設定へ統合予定（MVPでは未実装） |
| wallpositapplet.glade | btnAbout | clicked | on_btnAbout_clicked | N/A | dropped | MVP後回し |
| wallpositapplet.glade | btnHelp | clicked | (未指定) | N/A | dropped | 作るか含めて保留（最低優先） |

### Phase 3 での再分類（dropped 項目）

| Legacy file | Widget ID | Legacy signal | Phase 3 判定 | 理由 |
|---|---|---|---|---|
| wallpositapplet.glade | btnDaemonize | clicked | 対象（watch） | watch start アクションとして導線を再定義 |
| wallpositapplet.glade | btnCancelDaemonize | clicked | 対象（watch） | watch stop アクションとして導線を再定義 |
| wallpositapplet.glade | spnInterval | value_changed | 対象（watch） | watch interval 設定として導線を再定義 |
| wallpositapplet.glade | btnAbout | clicked | 対象 | 非常駐の情報ダイアログとして安全に追加可能 |
| wallpositapplet.glade | btnHelp | clicked | 保留（最低優先） | 作るかどうか自体を後続で再判定 |

### ダイアログ系（後続）

| Legacy file | Widget ID | Legacy signal | Legacy handler | New controller method | Status | Notes |
|---|---|---|---|---|---|---|
| wallpositapplet.glade | ColorSelectionDialog | destroy | on_ColorSelectionDialog_destroy | MainWindow.on_close_color_dialog | implemented | プレースホルダでクローズイベントを記録 |
| wallpositapplet.glade | SrcdirDialog | destroy | on_SrcdirDialog_destroy | MainWindow.on_close_srcdir_dialog | implemented | プレースホルダでクローズイベントを記録 |
| wallpositapplet.glade | SaveWallpaperDialog | destroy | on_SaveWallpaperDialog_destroy | MainWindow.on_close_save_path_dialog | implemented | glade 資産上の legacy handler。current runtime は `on_SavePathDialog_destroy` を正本とする |
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

## 履歴ステータス

- 2026-03-21 時点で、当時の MVP 対象 signal はすべて `implemented` と整理されていた。
- 2026-04-18 時点では、本書は current runtime の設計書ではなく旧 glade signal 対応の履歴証跡として扱う。

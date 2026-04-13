# Glade レイアウト再現ガイド（WallPosit_MainWindow）

最終更新: 2026-04-13
参照元: `src/harite/gui/resources/wallpositapplet.glade`

## 結論

- 既存 `docs/specs/gui/` には、Glade の実ウィジェット配置を画面内構造として固定した文書はなかった。
- 本書は `WallPosit_MainWindow` の配置を再現するための基準ドキュメント。

## 画面全体の骨格

`GtkWindow(WallPosit_MainWindow)`
- title: `Wallpaper Optimizer`
- resizable: `False`
- root container: `GtkVBox(vbox1)`

Phase5 方針メモ:

- 旧Gladeでは `resizable=False` だが、現代的UXと作業導線（複数ペイン比較、長文ログ確認）を優先し、P5-2 では `resizable=True` を採用する。

`vbox1` の縦方向スタック（上から順）
1. `hbox11`: 上マージン行（Top margin）
2. `hbox2`: 中央本体（左マージン / 中央操作群 / 右マージン）
3. `hbox12`: 下マージン行（Bottom margin）
4. `hbox14`: 下部アクションバー（設定・保存・適用・常駐操作）
5. `statusbar`: `GtkStatusbar`

## 再現用レイアウト図（MainWindow）

```text
+--------------------------------------------------------------------------------+
| Window: Wallpaper Optimizer                                                    |
+--------------------------------------------------------------------------------+
| [blank] [上マージン(px) lblTopMergin] [spnTopMergin] [blank]                    |
+---------------------------+--------------------------------+-------------------+
| 左マージン(px)             |                                | 右マージン(px)    |
| lblLMergin                |  [tglUpperL] [tglUpperR]      | lblRMergin        |
| [spnLMergin]              |  [tglPushLeftL][openL][...]   | [spnRMergin]      |
|                           |  [tglPushLeftR][openR][...]   |                   |
|                           |  [tglLowerL] [tglLowerR]      |                   |
|                           |  [entPathL][clrL][entPathR][clrR]                |
|                           |  (radFixed) (radNoFixed)      |                   |
+---------------------------+--------------------------------+-------------------+
| [blank] [下マージン(px) lblBtmMergin] [spnBtmMergin] [blank]                    |
+--------------------------------------------------------------------------------+
| [prefs] [color] [save] [apply] [spnInterval][秒] [execute] [stop] [about] [help]|
+--------------------------------------------------------------------------------+
| statusbar                                                                       |
+--------------------------------------------------------------------------------+
```

## 主要コンテナと役割

- `hbox11`: 上マージン調整
- `hbox2`: 中央レイアウト本体
  - `vbox4`: 左マージン列（`lblLMergin`, `spnLMergin`）
  - `hbox5`: 中央 + 右マージン列
    - `vbox3`: 中央操作群
      - 位置トグル群（上/左右/下）
      - 画像選択ボタン（左右）
      - パス表示 + クリア
      - 固定/非固定ラジオ
    - `vbox5`: 右マージン列（`lblRMergin`, `spnRMergin`）
- `hbox12`: 下マージン調整
- `hbox14`: 主要コマンドバー
- `statusbar`: 実行状態表示

## 主要ウィジェットID（再現優先）

### マージン
- `spnTopMergin`, `spnLMergin`, `spnRMergin`, `spnBtmMergin`

### 画像入力・配置
- パス: `entPathL`, `entPathR`
- 取得: `btnGetImgL`, `btnGetImgR`
- クリア: `btnClrPathL`, `btnClrPathR`
- 位置トグル:
  - 上下: `tglUpperL`, `tglUpperR`, `tglLowerL`, `tglLowerR`
  - 左右: `tglPushLeftL`, `tglPushRightL`, `tglPushLeftR`, `tglPushRightR`
- 固定モード: `radFixed`, `radNoFixed`

### 下部バー
- `btnSetting`, `btnSetColor`, `btnSave`, `btnSetWall`
- `spnInterval`, `lblInterval`
- `btnDaemonize`, `btnCancelDaemonize`
- `btnAbout`, `btnHelp`

## シグナル導線（MainWindow 主要分）

- window close: `on_WallPosit_MainWindow_delete_event`
- margin change: `on_spnMergin_value_changed`
- toggle buttons: `on_tglBtn_pressed`, `on_tglBtn_released`, `on_tglBtn_toggled`
- image pick: `on_btnGetImg_clicked`
- path update: `on_entPath_insert_text`
- path clear: `on_btnClrPath_clicked`
- fixed mode: `on_radFixed_toggled`
- save/optimize: `on_btnSave_clicked`
- apply: `on_btnSetWall_clicked`

## Glade再現時の配置ルール（Phase5向け）

- ルール1: 縦5段（上マージン行 / 中央本体 / 下マージン行 / コマンドバー / statusbar）を維持する。
- ルール2: 中央本体は「左マージン列 + 中央操作群 + 右マージン列」の3列を維持する。
- ルール3: 下部コマンドは1行バーに集約し、`save` と `apply` は中央寄りの主要ボタンとして視認可能にする。
- ルール4: 旧IDに紐づく操作意図（取得、クリア、固定、適用）を欠落させない。

## Phase5との接続

- P5-2（MainWindow 大胆再構成）で、本書の骨格を「どこまで残し、どこを刷新するか」を明示する。
- P5-2 で Window 方針を `resizable=True` に確定し、旧制約の採否理由を記録する。
- P5-3（Optimize/Apply 分離強化）では、下部 `btnSave` / `btnSetWall` の導線を新UIへ再割り当てる。
- P5-4（スタイル統一）では、旧Gladeの情報密度を保ちつつ可読性を上げる。

## このPRでの実施可否（P5-2）

このPRで実施できること:

- MainWindow の骨格（縦5段 + 中央3列）を Glade 近似へ寄せる。
- 主要ウィジェットIDの互換導線（`btnSave`, `btnSetWall`, `entPathL` など）を維持する。
- `resizable=True` を採用し、旧制約との差分理由を記録する。

このPRでは実施しないこと（後続PR推奨）:

- 旧Gladeの全ボタン配置・全シグナルの完全1:1再現。
- Optimize/Apply の詳細な情報階層分離（P5-3で実施）。
- タイポグラフィ/色/余白トークンの最終統一（P5-4で実施）。

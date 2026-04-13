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
| lblLMergin                |  [tglUpperL]         [tglUpperR]      | lblRMergin        |
| [spnLMergin]              |  [tglPushLeftL][openL][tglPushRightL] | [spnRMergin]      |
|                           |  [tglLowerL]         [tglLowerR]      |                   |
|                           |  [tglPushLeftR][openR][tglPushRightR] |                   |
|                           |  [entPathL][clrL][entPathR][clrR]     |                   |
|                           |  (radFixed) (radNoFixed)      |                   |
+---------------------------+--------------------------------+-------------------+
| [blank] [下マージン(px) lblBtmMergin] [spnBtmMergin] [blank]                    |
+--------------------------------------------------------------------------------+
| [prefs] [color] [save] [apply] [spnInterval][秒] [execute] [stop] [about] [help]|
+--------------------------------------------------------------------------------+
| statusbar                                                                       |
+--------------------------------------------------------------------------------+
```

図中注記:

- `tgl*L` と `tgl*R` は、左右それぞれの画像に対する独立指示ボタン。
- `openL` / `openR` はファイル/ディレクトリ選択ダイアログで入力を受けるボタン。
- `entPathL` / `entPathR` は現在パス表示（入力フォーム）で、`clrL` / `clrR` は個別クリア。
- 以前の図で使っていた `...` は省略記号だった。未知要素を断定する意図ではなく、ASCII図の簡略化を示すための表記。

### 中央プレビューの扱い（2026-04-13確定）

- 旧 `WallPosit_MainWindow` には、中央の常設画像プレビュー用ウィジェットは確認されない。
- `GtkImage` は `ErrorDialog`（`image1`）でのみ使用され、MainWindow中央のプレビュー用途ではない。
- 旧実装 `WindowBase.btnGetImg_clicked` は、画像表示ではなく `entPathL/R` へのパス反映を行う。
- よって本書では「中央プレビューは現状無し」を確定とし、preview は将来機能（P5-4以降）として扱う。

先に解いておくべきボタン類（優先順）:

1. `btnCancelSave` / `btnOpenSave`（SaveWallpaperDialog）: `on_btnCancelSave_clicked` / `on_btnOpenSave_clicked` と旧 `on_btnCancel_clicked` / `on_btnOpen_clicked` の命名差分を解消。
2. `btnClrPathL` / `btnClrPathR`（MainWindow）: 共有ハンドラ方式（`on_btnClrPath_clicked -> btnGetImg_clicked`）を現行側でも意図的に残すか、専用ハンドラへ分離するかを決定。
3. `btnAbout`（MainWindow）: planned から実体導線へ昇格するかを後続で判断。
4. `btnHelp`（MainWindow）: 作るかどうか自体を保留。優先度は最低として後続で再判定。

## 主要コンテナと役割

- `hbox11`: 上マージン調整
- `hbox2`: 中央レイアウト本体
  - `vbox4`: 左マージン列（`lblLMergin`, `spnLMergin`）
  - `hbox5`: 中央 + 右マージン列
    - `vbox3`: 中央操作群
      - 左画像ブロック: `tglUpperL` / `tglPushLeftL` / `btnGetImgL` / `tglPushRightL` / `tglLowerL`
      - 右画像ブロック: `tglUpperR` / `tglPushLeftR` / `btnGetImgR` / `tglPushRightR` / `tglLowerR`
      - 左右は独立指示系で、各画像を囲むように配置される
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
- save（旧MainWindow）: `on_btnSave_clicked`
- apply: `on_btnSetWall_clicked`

## ボタンフェイス再現ポリシー（Stock意図の読み取り）

本節は「どこで」「どう反映するか」を固定するための運用ルール。

### 1) 意思の読み取り（仕様解釈）

- `tgl*` / `btn*` の多くは `use_stock=True` で定義され、ラベルは文言ではなく操作意味を示す stock 名（例: `gtk-justify-right`）になっている。
- したがって、旧UIの主眼は「文字列の一致」ではなく「一目で方向・操作種別が分かるボタンフェイス」にある。
- 特に `tglPushRight*` / `tglPushLeft*` は、右寄せ/左寄せを視覚的に即判別できることを必須要件とする。

### 1-2) Explain による確証強化（旧実装ハンドラ根拠）

以下は `wallpaperoptimizer/WallpaperOptimizer/WindowBase.py` のハンドラ実装を Explain 観点で読んだ結果。

- `tglBtn_toggled` は、ボタン名を `left/right/top/bottom` へ直接マップして `option.opts.align/valign` に設定する。
  - `tglPushLeft*` -> `align=left`
  - `tglPushRight*` -> `align=right`
  - `tglUpper*` -> `valign=top`
  - `tglLower*` -> `valign=bottom`
- `tglBtn_pressed` は対向トグルを落とし、`tglBtn_released` は両方OFF時に `center/middle` へ戻す。
  - つまりトグルフェイスは「装飾」ではなく、配置決定ロジックの入力そのもの。
- `btnSave_clicked` は「保存先選択 + 生成」の Save 導線であり、旧MainWindowに独立した Optimize ボタンは存在しない。
- `btnSetWall_clicked` は即時 apply 実行。
- 現行P5-3では安全策として `Optimize (provisional)` を Save 近傍に仮置きし、旧Save導線を壊さない形で分離を進める。

確証レベル定義:

- A（高）: Glade の stock 指定 + WindowBase ハンドラで意味値が確定するもの。
- B（中）: Glade 上の stock 指定はあるが、ハンドラで意味値が直接は確定しないもの。
- C（低）: 現行実装都合で置換が必要で、同等表現で意味維持を狙うもの。

本書の `tgl*`, `btnSave`, `btnSetWall` は A 扱いとする。

### 2) MainWindow のフェイス基準（優先再現）

- 位置トグル（`tglUpper*`, `tglLower*`, `tglPush*`）
  - 要件: 方向性（上/下/左/右）がアイコンまたは同等表現で判別できること。
- 画像取得/クリア（`btnGetImg*`, `btnClrPath*`）
  - 要件: open/clear の操作種別が一目で分かること。
  - 補足: `btnClrPath*` は旧Gladeで `relief=none`。補助操作として主操作より弱い見え方を維持する。
- 下部コマンド（`btnSave`, `btnSetWall`, `btnDaemonize`, `btnCancelDaemonize` 等）
  - 要件: save/apply/execute/stop の意味差がボタンフェイスで区別できること。

### 3) 反映箇所（実装・文書・テスト）

- 実装: `src/harite/gui/adapters/gtk_backend.py`
  - Stock API が使える環境では stock 相当の見え方を採用。
  - Stock API が使えない環境では、意味等価なアイコン名/記号/短文ラベルで代替し、方向・操作種別の判別性を維持。
  - `tgl*` は A 根拠に従い、左右/上下の判別性を最優先（見た目の美しさより誤認防止を優先）。
- 文書: `docs/specs/gui/gui-phase5-p5-3-flow-policy.md`
  - Optimize/Apply 分離だけでなく、主要アクションのフェイス差（意味判別性）を受け入れ観点に含める。
- テスト: `tests/gui/test_gtk_runtime_backend.py`
  - 少なくとも「右寄せ/左寄せ、適用/保存、実行/停止」の区別がUI要素上で検出できることを回帰観点として固定する。
  - 可能なら `tglPushRight*` 選択時に最終オプションが `align=right` になることを挙動観点で確認する。

### 4) 判定基準（P5レビュー用）

- 文字を読まなくても、方向ボタンの意味（上/下/左/右）を判定できる。
- apply/save/execute/stop を誤認しない。
- 互換層都合でフェイスを置換した場合でも、置換表（旧stock -> 新表現）をPR記録に残す。

## Glade再現時の配置ルール（Phase5向け）

- ルール1: 縦5段（上マージン行 / 中央本体 / 下マージン行 / コマンドバー / statusbar）を維持する。
- ルール2: 中央本体は「左マージン列 + 中央操作群 + 右マージン列」の3列を維持する。
- ルール3: 下部コマンドは1行バーに集約し、`save` と `apply` は中央寄りの主要ボタンとして視認可能にする。
- ルール4: 旧IDに紐づく操作意図（取得、クリア、固定、適用）を欠落させない。

## Phase5との接続

- P5-2（MainWindow 大胆再構成）で、本書の骨格を「どこまで残し、どこを刷新するか」を明示する。
- P5-2 で Window 方針を `resizable=True` に確定し、旧制約の採否理由を記録する。
- P5-3（Optimize/Apply 分離強化）では、旧 `btnSave` の意味（Save導線）を維持しつつ、`Optimize (provisional)` を Save 近傍に仮置きして分離を段階導入する。
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

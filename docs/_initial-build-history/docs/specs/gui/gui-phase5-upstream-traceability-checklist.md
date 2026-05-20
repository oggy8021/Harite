# GUI Phase5 Upstream Traceability Checklist

最終更新: 2026-04-16
対象: P5-8 以降の各PR（必須）

## 目的

- 母体プログラム（wallpaperoptimizer）との対応関係を先に明示し、実装前レビューで合意する。
- MainWindowへの暫定ロジック蓄積を避け、Dialog/責務分割の整合を維持する。
- 「元プログラムからの移行」を中盤以降でも継続担保し、場当たり実装を防ぐ。

## 実施タイミング

- 実装前: 本チェックリストを作成してレビュー依頼する。
- 実装後: 差分・未対応項目を更新し、実機結果と突合する。

## PR/merge 停止ポリシー（本書の最上位ルール）

- 本書の必須項目が未充足のPRは、`Draft` でのみ扱う。
- 未充足PRは `merge禁止` とする。
- 次を満たすまで、P5-8以降の merge を全面停止する。
  - 上流読解ソースの明記
  - 対応関係マトリクスの記入
  - 非対応差分の合意
  - 実装前レビュー承認（Approve）
  - Owner実行の回帰結果記録
  - 実機確認結果（PRごと）の記録

## 運用原則（上流移行）

- 原則1: 先に上流挙動を読む。実装は後。
- 原則2: 不明点は、母体プログラムまたは Owner に求める。Ownerもソース解析まで行う。
- 原則3: 既存MainWindowへ詰め込みすぎない。Dialog/責務分割を優先する。
- 原則4: 回帰（regression）兆候がある場合、次機能へ進まず原因PRを先に修正する。

## ステータス定義（統一）

- `pass`: 上流対応と実機挙動が一致
- `warn`: 差分はあるが、理由と後続タスクが合意済み
- `fail`: 上流逸脱、回帰、または証跡不足
- `blocked`: 前段failにより検証不能（理由必須）

## 1. 対象PR情報

- PR番号:
- タスク番号: P5-8 / P5-9 / P5-10 / P5-11
- ブランチ名:
- 担当:
- レビュー担当:
- 予定実機環境: XFCE / OS名 / バージョン
- 判定対象導線:

## 2. 上流読解ソース

- 参照ファイル1:
- 参照ファイル2:
- 参照ファイル3:
- 備考:

推奨（タスク別）:

- P5-8: `WindowBase.py`（トグル押下/復帰とmargin優先）
- P5-9: `Widget/ImgOpenDialog.py` + 呼び出し元
- P5-10: `SettingDialog.py` / `SrcdirDialog.py`
- P5-11: `Widget/SaveWallpaperDialog.py`

## 3. 対応関係マトリクス

| 機能項目 | 上流挙動（要約） | 現行挙動（実装前） | 実装方針 | 受け入れ条件 |
| --- | --- | --- | --- | --- |
| 例: Open-L | | | | |
| 例: Open-R | | | | |
| 例: Save cancel | | | | |
| 例: Toggle exclusion | | | | |
| 例: Margin reflect | | | | |

記入ルール:

- `上流挙動` はファイル名+関数名を必ず併記する。
- `実装方針` は「どこを変更するか（file/symbol）」を必ず書く。
- `受け入れ条件` はテスト項目 + 実機確認項目の両方を書く。

## 4. 非対応・差分の合意

- 非対応項目1:
  - 理由:
  - 代替挙動:
  - 後続タスク:
- 非対応項目2:
  - 理由:
  - 代替挙動:
  - 後続タスク:

差分分類（必須）:

- `仕様差分（意図的）`
- `暫定差分（期限付き）`
- `不具合差分（要修正）`

## 5. 実装前レビュー合意（必須）

- [ ] 上流読解ソースが明記されている
- [ ] 対応関係マトリクスが埋まっている
- [ ] 非対応・差分の理由と後続タスクが明記されている
- [ ] レビュー承認（Approve）を得た
- [ ] PRは `Draft` で開始し、承認後に `Ready for review` へ変更した

レビューコメントURL:

## 6. 実装後突合

- 回帰テスト結果（owner実行）:
- 実機判定（pass/warn/fail）:
- 上流差分の再確認:
- PRコメント反映:

### 実機確認チェック（PRごと必須）

- [ ] MainWindow 観点を確認（pass/warn/fail）
- [ ] Optimize 観点を確認（pass/warn/fail/blocked）
- [ ] Apply 観点を確認（pass/warn/fail/blocked）
- [ ] Style 観点を確認（pass/warn/fail）
- [ ] スクリーンショット3点を保存
- [ ] `out/manual-validation/` の json/md/pr-comment を更新

### Go/No-Go 判定

- Go条件:
  - 必須チェック完了
  - `fail` なし（`warn` は合意済みのみ）
- No-Go条件:
  - 必須チェック未完了
  - `fail` あり
  - `blocked` 理由が未解消

最終判定:

- [ ] Go（merge可）
- [ ] No-Go（merge停止継続）

判定者:
判定日:

## 7. 実施順（必須フロー）

1. 上流読解ソースを確定する
2. 対応関係マトリクスを埋める
3. 非対応・差分を分類し、後続タスクへ割り当てる
4. Draft PRを作成し、本書を添付する
5. レビュー承認（Approve）を得る
6. 承認済み項目のみ実装する
7. Owner実行の回帰と実機確認を記録する
8. Go/No-Go を判定し、Go のときだけ merge 可とする

## 8. PR本文テンプレート（貼り付け用）

```md
### Upstream Traceability Gate
- Task: P5-x
- Source read: [file/function list]
- Mapping doc: docs/specs/gui/gui-phase5-upstream-traceability-checklist.md
- Review status: approved / pending

### Intentional Diffs
- [仕様差分（意図的）]
- [暫定差分（期限付き）]
- [不具合差分（要修正）]

### Validation
- Fixed regression (owner): pass/fail
- XFCE manual: pass/warn/fail/blocked
- Overall Go/No-Go: Go / No-Go
```

## 9. レビュー承認ログ（必須）

- 承認者:
- 承認日時:
- 承認対象コミット:
- 保留事項:
- 次回確認ポイント:

## 10. タスク別 最低確認項目

- P5-8（トグル排他 + margin）
  - トグルの対向復帰が発生する
  - margin反映がUI表示と内部状態で一致する
- P5-9（Open Dialog）
  - Open-L/Open-R で選択ダイアログが開く
  - 選択/キャンセルが `entPathL/R` と状態表示に反映される
  - `entPathL/R` の事前入力を要求せず、dialog の選択結果を左右別に反映する
- P5-10（watch）
  - `srcdirL/srcdirR` 指定あり/なしの双方が意図どおり動く
  - MainWindow通常入力導線と責務が混在しない
- P5-11（Save）
  - 保存先・保存名が追跡できる
  - confirm/cancel の状態遷移が破綻しない

## 11. 逸脱時の扱い

- 上流挙動と不一致を見つけた場合は、即時 `No-Go` とする
- 逸脱修正PRを優先し、次機能へ進まない
- 逸脱理由が仕様差分として妥当な場合のみ、合意の上で `warn` へ格下げ可

## 12. P5-8 最低記入（初版）

本節は P5-8（トグル上下左右 + margin）着手のための最低限記入済みブロック。
未確定項目は Owner ソース解析で更新する。

### 12-1. 対象PR情報（P5-8）

- PR番号: TBD
- タスク番号: P5-8
- ブランチ名: `feature/gui-phase5-p5-8-toggle-exclusion-margin-sync-20260414`
- 担当: owner
- レビュー担当: TBD
- 予定実機環境: XFCE
- 判定対象導線: `tglUpper/Lower*`、`tglPushLeft/Right*`、`spn*Mergin`

### 12-2. 上流読解ソース（P5-8）

- 参照ファイル1: `wallpaperoptimizer/WallpaperOptimizer/WindowBase.py`
- 参照観点1: `tglBtn_pressed`（対向トグル復帰）
- 参照観点2: `tglBtn_released`（両方OFF時の復帰ルール）
- 参照観点3: `tglBtn_toggled`（align/valign 反映）
- 備考: ローカル正本は `..\wallpaperoptimizer` を参照する
- 読解メモ1: `tglBtn_pressed` は同一side内の対向トグルが active のときだけ `set_active(False)` を行う
- 読解メモ2: `tglBtn_toggled` は active になったトグル名から `align/valign` を `left/right/top/bottom` へ設定する
- 読解メモ3: `tglBtn_released` は「自分も対向もOFF」のときだけ `align=center` または `valign=middle` へ戻す
- 読解メモ4: `spnMergin_value_changed` は changed された単一 widget 名から index を決め、`option.opts.mergin[idx]` だけを更新する
- 読解メモ5: margin の `- / +` は独立 button ではなく `GtkSpinButton` 自身のステッパで、Glade 上は `adjustment="0 0 250 1 10 0"` / `"0 0 500 1 10 0"` により step/range が与えられている
- 備考: 母体 `Core.py` では margin は表示可能領域を縮め、その後に `align/valign` で配置を決める。`fixed` は左右画像の割当方針であり、margin/align を打ち消す優先順位ルールは見当たらない

### 12-3. 対応関係マトリクス（P5-8）

| 機能項目 | 上流挙動（要約） | 現行挙動（実装前） | 実装方針 | 受け入れ条件 |
| --- | --- | --- | --- | --- |
| Toggle exclusion（vertical） | `pressed` で対向を落とし、`released` で両方OFF時は `valign=middle` に戻す | 同時有効が起こり得る | 同一side内の対向トグルだけを排他制御しつつ、母体の `both-off -> middle` を再現できるか確認する | `tglUpperL` と `tglLowerL`、`tglUpperR` と `tglLowerR` が各side内で同時にONにならず、両方OFF時の復帰先が母体と一致する |
| Toggle exclusion（horizontal） | `pressed` で対向を落とし、`released` で両方OFF時は `align=center` に戻す | 同時有効が起こり得る | 同一side内の対向トグルだけを排他制御しつつ、母体の `both-off -> center` を再現できるか確認する | `tglPushLeftL` と `tglPushRightL`、`tglPushLeftR` と `tglPushRightR` が各side内で同時にONにならず、両方OFF時の復帰先が母体と一致する |
| Margin reflect | changed された1 widget に応じて `mergin[idx]` を単独更新する | 反映経路が不明瞭 | 現行の4値集約伝播を維持するか、母体同様の単項目更新へ寄せるかをレビューで確定する | left/right/top/bottom の内部状態更新が母体意図と矛盾しない |

例示:

- `tglUpperL` がONのとき、`tglLowerL` を押すと `tglUpperL` が落ちて `tglLowerL` へ切り替わる
- `tglUpperL` がONでも、`tglUpperR` は押せるままにする
- `tglPushLeftR` がONのとき、`tglPushRightR` を押すと `tglPushLeftR` が落ちて切り替わる

### 12-4. 非対応・差分（P5-8初版）

- 非対応項目1: 実GTK環境の最終配置結果可視化
  - 理由: P5-8は導線と内部反映の確定を優先
  - 代替挙動: 状態表示とテストで確認
  - 後続タスク: P5-9/P5-10で実機表示を再検証

### 12-5. 実装前レビュー合意（P5-8）

- [ ] 12-2 と 12-3 の内容をレビュー
- [ ] 不明点を Owner ソース解析で補完
- [ ] Approve 後に実装開始

### 12-6. 実装スコープ境界（P5-8）

- In scope:
  - `tglUpper*/tglLower*` の排他制御
  - `tglPushLeft*/tglPushRight*` の排他制御
  - `spn*Mergin` 変更時の4値集約伝播
- Out of scope:
  - 実GTK描画での最終配置アルゴリズムの再現
  - Open/Save/watch 導線の仕様追加（P5-9以降で扱う）
- 逸脱禁止:
  - 上記Out of scopeへ影響する変更は本PRで行わない

### 12-7. 未解決点（Ownerソース解析で補完）

- [x] `tglBtn_released` の「両方OFF時の復帰先」優先順位
  - vertical は `middle`、horizontal は `center`
- [x] `fixed > margin > toggles` の厳密適用条件（左右/上下の個別差）
  - 母体にはそのような強度ルールは見当たらない。`fixed` は L/R 割当、margin は有効領域、toggle はその内側の寄せ位置として同時成立する
- [x] 排他制御と `align/valign` 更新順序の依存有無
  - 母体は `pressed -> toggled(active時のみ) -> released(両方OFFならcenter/middle)` の責務分離になっている
- [x] 例外導線（初期状態/未選択状態）での上流既定値
  - `Options.py` の既定値は `align=center`、`valign=middle`、`mergin=0,0,0,0`、`fixed=False`、`interval=60`。Harite 側では vertical の `middle` を `center` 表現へ正規化している
- [x] 現行 fallback 実装の「対向ボタン無効化」は母体差分として維持するか、`pressed/released` ベースへ寄せ直すか
  - 母体寄せへ変更済み。無効化UXは廃止した
- [x] 現行 fallback 実装は `on_radFixed_toggled(False)` を呼んでいるが、母体のトグル処理は `align/valign` 更新であり、責務が一致していない
  - `align/valign` 更新へ置き換え済み
- [x] margin の `- / +` が機能しない直接原因は何か
  - 母体は `GtkSpinButton` の adjustment で step/range を持つが、fallback は `set_value(0)` だけで range/increment 未設定だった。母体値へ合わせて補完する
- [x] 現行 margin 実装の「4値一括 callback」が、母体の単項目更新と比べて仕様差分として許容されるか
  - UI adapter / fallback は母体どおり changed widget 起点で更新している。MainWindow 内部で最終的に `l,r,t,b` 文字列へ再集約して保持するのは Harite の状態表現であり、母体の単項目更新導線とは矛盾しない

### 12-8. 実装後エビデンス記録（P5-8）

#### 12-8-1. 回帰（Owner実行）

- 実行日: 2026-04-15
- 実行者: owner
- コマンド: `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py`
- 結果: pass（100%）

#### 12-8-2. 実機（XFCE）

| 観点 | 判定 | 根拠（スクリーンショット/ログ） |
| --- | --- | --- |
| Vertical toggle exclusion（same-side only） | pass | 母体寄せの切替挙動を確認 |
| Horizontal toggle exclusion（same-side only） | pass | 母体寄せの切替挙動を確認 |
| Margin reflect（UI表示） | pass | `Current state` で現在値を確認可能。Top + Top Margin の同時成立も母体 `Core.py` と整合 |
| Margin reflect（内部状態） | pass | GUI回帰 100% pass |

#### 12-8-3. 最終合意

- [x] P5-8 の受け入れ条件を満たした
- [x] 非対応差分は `warn` として合意済み
- [x] 次タスク（P5-9）へ進行可

## 13. P5-9 最低記入（Open Dialog）

本節は P5-9（Open-L/Open-R の Dialog 主体導線復元）のための最低限記入済みブロック。
母体 `ImgOpenDialog` の return semantics と、Harite 側の意図差分を同時に固定する。

### 13-1. 対象PR情報（P5-9）

- PR番号: TBD
- タスク番号: P5-9
- ブランチ名: `feature/gui-phase5-p5-9-open-dialog-restore-20260414`
- 担当: owner
- レビュー担当: TBD
- 予定実機環境: XFCE
- 判定対象導線: `btnGetImgL`、`btnGetImgR`、`ImgOpenDialog`、`entPathL`、`entPathR`

### 13-2. 上流読解ソース（P5-9）

- 参照ファイル1: `wallpaperoptimizer/WallpaperOptimizer/Widget/ImgOpenDialog.py`
- 参照観点1: `openDialog(path, addlr)` の初期ディレクトリ、タイトル、戻り値
- 参照観点2: `__init__` の image filter / all files filter
- 参照ファイル2: `wallpaperoptimizer/WallpaperOptimizer/Widget/DialogBase.py`
- 参照観点3: `btnCancel_clicked` の `gtk.RESPONSE_CANCEL`
- 参照ファイル3: `wallpaperoptimizer/WallpaperOptimizer/WindowBase.py`
- 参照観点4: `btnGetImg_clicked` の `ImgOpenDialog.openDialog(...)` 呼び出しと `entPath.set_text(os.path.basename(path))`
- 読解メモ1: upstream は `btnOpen_clicked -> RESPONSE_OK`、cancel/destroy は `RESPONSE_CANCEL` として扱い、`openDialog` は OK 時だけ filename を返し、それ以外は `False` を返す
- 読解メモ2: 初期 path が空なら home directory、非空なら `abspath(path)` を初期位置に使う
- 読解メモ3: title は既定タイトルへ `(<L/R>)` を付けて side を区別する
- 読解メモ4: filter は `image/png`、`image/jpeg`、`image/bmp`、`image/gif` と `*.png`、`*.jpeg`、`*.jpg`、`*.bmp`、`*.gif`、および all files で構成される
- 読解メモ5: caller は選択 path を内部 args に保持し、entry には basename のみを表示する

### 13-3. 対応関係マトリクス（P5-9）

| 機能項目 | 上流挙動（要約） | 現行挙動（実装前） | 実装方針 | 受け入れ条件 |
| --- | --- | --- | --- | --- |
| Open-L/Open-R 起動 | `WindowBase.btnGetImg_clicked` が side ごとに `ImgOpenDialog.openDialog(current_path, Caps)` を呼ぶ | entry に値がないと `planned(path-required)` で停止 | `src/harite/gui/adapters/gtk_backend.py` に `ImgOpenDialog` proxy を追加し、button 押下で side-aware に dialog-open へ遷移させる | Open-L/Open-R 押下で dialog が開き、owner 回帰で `dialog-open` 状態が固定される |
| 選択確定 | `ImgOpenDialog.btnOpen_clicked` は `RESPONSE_OK`、`openDialog` は `get_filename()` を返す | entry の文字列をそのまま handler へ渡していた | `src/harite/gui/adapters/ui_adapter.py` と `src/harite/gui/views/main_window.py` で `path, side` を受け、左右別 path を保持しつつ `input_value` を再構成する | 選択確定で selected へ遷移し、左右の path が上書き更新され、owner 回帰が pass する |
| cancel / destroy | `DialogBase.btnCancel_clicked` は `RESPONSE_CANCEL`、`openDialog` は `False` を返して caller 側 path を更新しない | close semantics が未定義で、MainWindow は destroy をログするだけ | fallback proxy では cancel/close を `canceled` / `closed` 状態へ明示し、既存 path を保持したまま `on_ImgOpenDialog_destroy` を通知する | cancel/close 後に path が変化せず、状態表示が `canceled` または `closed` になる |
| title / 初期位置 | upstream は title に side suffix を付け、空 path 時は home、非空 path 時は absolute path 起点 | title/初期位置ともに未整理 | `src/harite/gui/adapters/gtk_backend.py` の runtime fallback で native `Gtk.FileChooserDialog` を起動し、side suffix、home 初期位置、既存 path の absolute path 再利用を再現する | 実機で dialog title に side が表示され、空 path でも dialog が開く |
| filter 制御 | upstream は image filter と all files filter を dialog へ追加する | filter 制御なし | runtime fallback の native chooser に `png/jpeg/jpg/bmp/gif` と all files filter を追加する | 実機で filter 選択肢が表示され、対象集合が upstream と一致する |
| entry 表示内容 | caller は `os.path.basename(path)` のみ表示する | path-required 前提で entry を入力欄として扱っていた | Harite では user 合意に従い、`entPathL/R` を表示欄として full path を保持する | GUI 上で選択元 path が判読でき、仕様差分として合意済みである |

### 13-4. 非対応・差分（P5-9）

- 非対応項目1: `entPathL/R` への basename-only 表示
  - 理由: user 合意は「選択されたソース path を表示する」ことであり、basename のみでは情報量が足りない
  - 代替挙動: full path を表示し、左右別 path を MainWindow 側でも保持する
  - 後続タスク: 必要なら preview 導入時に path 表示の縮退方針を再設計する
  - 差分分類: `仕様差分（意図的）`

### 13-5. 実装前レビュー合意（P5-9）

- [x] 13-2 と 13-3 の内容をレビュー可能な形で記入した
- [x] 差分分類と後続タスクを明記した
- [ ] Approve を得た

### 13-6. 実装スコープ境界（P5-9）

- In scope:
  - Open-L/Open-R 押下で dialog-open へ遷移すること
  - confirm/cancel/close の状態遷移
  - 左右別 path の保持と `input_value` 再構成
- Out of scope:
  - 実 chooser widget による filter UI の完全再現
  - home directory 初期化の実 UI 再現
  - save dialog の挙動整理
- 逸脱禁止:
  - Save/watch の仕様変更を本タスクへ混入させない

### 13-7. 未解決点（P5-9）

- [x] cancel と destroy を同一の「未選択」意味として扱えるか
  - upstream はどちらも `RESPONSE_CANCEL` 経由で `False` を返す。Harite では状態表示だけ `canceled` / `closed` に分け、path 非更新という本質は一致させる
- [x] `entPathL/R` を basename 表示へ寄せるか、source path 表示へ寄せるか
  - user 合意に従い source path 表示へ寄せる。upstream caller の basename-only は意図差分として扱う
- [x] filter 対象の最小集合は何か
  - upstream 定義どおり `png/jpeg/jpg/bmp/gif` と all files を最小集合として固定する
- [x] title 側の L/R 区別はどの強度で再現するか
  - fallback proxy でも `Open image (L/R)` として side を明示する

### 13-8. 実装後エビデンス記録（P5-9）

#### 13-8-1. 回帰（Owner実行）

- 実行日: 2026-04-16
- 実行者: owner
- コマンド: `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py`
- 結果: pass

#### 13-8-2. 実機（XFCE）

| 観点 | 判定 | 根拠（スクリーンショット/ログ） |
| --- | --- | --- |
| Open dialog 起動 | pass | owner が XFCE 実機で chooser 起動を確認 |
| confirm/cancel 状態遷移 | pass | owner が XFCE 実機で confirm/cancel の双方を確認 |
| path 表示 | pass | owner が XFCE 実機で選択 path 表示を確認 |
| filter UI | pass | owner が XFCE 実機で image/all-files filter を確認 |

#### 13-8-3. 最終合意

- [x] P5-9 の上流対応表を記入した
- [x] 回帰 pass を記録した
- [x] 実機確認を完了した
- [x] P5-9 を Go 判定できる

## 14. P5-11 最低記入（Save Dialog）

本節は P5-11（Save 体験改善）のための事前整理ブロック。
upstream の save path 確定責務は維持しつつ、dialog 実体は modern GTK chooser へ置換可能とする。

### 14-1. 対象PR情報（P5-11）

- PR番号: TBD
- タスク番号: P5-11
- ブランチ名: `feature/gui-phase5-p5-11-save-ux-improvement-20260416`
- 担当: owner
- レビュー担当: TBD
- 予定実機環境: XFCE
- 判定対象導線: `btnSave`、`SaveWallpaperDialog`、`btnOpenSave`、`btnCancelSave`、save path 表示

### 14-2. 上流読解ソース（P5-11）

- 参照ファイル1: `wallpaperoptimizer/WallpaperOptimizer/Widget/SaveWallpaperDialog.py`
- 参照観点1: `openDialog()` の戻り値と dialog lifecycle
- 参照ファイル2: `wallpaperoptimizer/WallpaperOptimizer/Widget/DialogBase.py`
- 参照観点2: `btnCancel_clicked` の `gtk.RESPONSE_CANCEL`
- 参照ファイル3: `wallpaperoptimizer/WallpaperOptimizer/WindowBase.py`
- 参照観点3: `btnSave_clicked` が `SaveWallpaperDialog.openDialog()` の戻り値を `option.opts.save` へ入れ、その後 `core.option.getSavePath()` を見て `singlerun()` する流れ
- 読解メモ1: upstream save dialog は openDialog 一発で完了し、OK 時は `get_filename()`、cancel/destroy 時は `None` を返す
- 読解メモ2: save path の確定後に本体処理を続行する責務は caller 側にある
- 読解メモ3: upstream には Harite 現行のような confirm/cancel ボタン別の状態機械や `path-required` ラベル管理は見当たらない

### 14-3. 対応関係マトリクス（P5-11）

| 機能項目 | 上流挙動（要約） | 現行挙動（実装前） | 実装方針 | 受け入れ条件 |
| --- | --- | --- | --- | --- |
| Save 起動 | `WindowBase.btnSave_clicked` が `SaveWallpaperDialog.openDialog()` を呼ぶ | fallback backend が内部 proxy を開き、MainWindow 側にも `save_dialog_open` 状態を持つ | Save 押下で native save chooser または同等の modal dialog を開き、状態機械を単純化する | Save 押下で chooser が開き、閉じた後の状態が一意に定まる |
| confirm | upstream は `openDialog()` が save filename を返し、caller が `singlerun()` を続行する | `on_save_dialog_confirm(save_path)` が path を設定し、`can_optimize` なら `on_optimize()` を呼ぶ | 「save path を返す」と「caller が optimize 続行」の責務は維持しつつ、dialog 確定経路を1本化する | confirm 後に save path が保持され、保存処理が一度だけ続行する |
| cancel / destroy | upstream は `None` を返し、保存処理を継続しない | cancel が dialog open state に依存し、条件次第で `cancel-failed` になり得る | cancel/destroy は常に non-destructive に閉じ、保存処理を継続しない経路へ寄せる | cancel 後に save path が不用意に変化せず、`cancel-failed` が発生しない |
| path 表示 | upstream caller は path を内部 option に保持するが、MainWindow 上の見せ方は強く規定されない | `lblSaveDialogState` など複数ラベルへ状態が分散 | 保存先 path と保存名を MainWindow 側で追跡し、1箇所で確認できる表示へ寄せる | 実機で「どこに何という名前で保存されるか」が判読できる |
| dialog 実体 | upstream は legacy Glade の `GtkFileChooserDialog` | Harite fallback は独自 `_SaveDialogProxy` と補助ボタン群 | dialog 実体は native save chooser へ modernize 可。戻り値 semantics を優先し widget 再現は要求しない | 実 GTK 環境で save chooser が開き、古い Glade 依存なしに成立する |
| overwrite / 既定保存先 UX | upstream 実装詳細は薄い | 現行 Harite は path-required 表示中心で、保存先 UX が不明瞭 | modern GTK chooser の overwrite confirmation や current folder UX を活用してよい | 行き先不明が解消され、overwrite 時の事故を減らせる |

- 実装中メモ1: runtime fallback の `_SaveDialogProxy` は native `Gtk.FileChooserDialog(SAVE)` を優先し、Save 押下で `on_save` 通知後に modal chooser を開く形へ着手済み。confirm は save path を callback へ返し、cancel は保存継続なしで閉じる（2026-04-16）
- 実装中メモ2: modern chooser では overwrite confirmation と既定ファイル名 `harite-output.jpg` を補完し、upstream の modal-return semantics を損なわない範囲で UX を改善する（2026-04-16）
- 実装中メモ3: MainWindow / runtime fallback の双方に `Save target:` 表示を追加し、保存先 path は 1 箇所で読める形へ整理した。`lblApplyTarget` は apply 導線専用のまま維持する（2026-04-16）

### 14-4. 非対応・差分（P5-11 事前整理）

- 非対応項目1: upstream の dialog 実体そのものの再現
  - 理由: 旧 Glade/legacy chooser への依存は現環境で不安定であり、P5-9 と同様に fallback/native chooser 併用が現実的
  - 代替挙動: native save chooser を採用し、戻り値 semantics と caller 責務を維持する
  - 後続タスク: P5-11 実装時に chooser abstraction を save/open で共通化できるか検討する
  - 差分分類: `仕様差分（意図的）`
- 非対応項目2: 現行の SaveDialog 状態ラベル群の完全維持
  - 理由: upstream は modal-return 型であり、現在の多段ラベルは Harite 独自複雑化の可能性が高い
  - 代替挙動: 保存先表示と保存結果表示を整理し、不要な `path-required` / `cancel-failed` 状態を縮退させる
  - 後続タスク: P5-11 実装時に最低限必要な status vocabulary を再定義する
  - 差分分類: `仕様差分（意図的）`

### 14-5. 実装前レビュー合意（P5-11）

- [x] 14-2 と 14-3 の事前整理を記入した
- [x] 維持点と modernize 点を分離した
- [x] Approve を得た

### 14-6. 実装スコープ境界（P5-11）

- In scope:
  - save path の confirm/cancel semantics
  - native save chooser への modernize
  - 保存先の可視化
- Out of scope:
  - optimize 本体アルゴリズムの変更
  - apply/watch 導線の変更
  - Open dialog の追加差分修正
- 逸脱禁止:
  - save chooser 導入に乗じて unrelated な MainWindow state を増やしすぎない

### 14-7. 未解決点（P5-11）

- [x] 何を modernize してよいか
  - dialog 実体、overwrite confirmation、current folder UX、保存先表示 UI は modern GTK chooser に寄せてよい
- [x] 何を削ってよいか
  - upstream に根拠の薄い独自の SaveDialog 状態機械や `cancel-failed` 語彙は整理対象とする
- [x] 何を upstream 互換として最優先で守るか
  - save path の戻り値 semantics と caller 側続行責務を最優先とする

### 14-8. 実装後エビデンス記録（P5-11）

#### 回帰（Owner実行）

- 実行日: 2026-04-16
- 実行者: owner
- コマンド: `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py`
- 結果: pass

#### 実機（XFCE）

| 観点 | 判定 | 根拠（スクリーンショット/ログ） |
| --- | --- | --- |
| Save chooser 起動 | pass | owner が XFCE 実機で Save 押下直後の native chooser 起動を確認 |
| confirm/cancel 状態遷移 | pass | owner が XFCE 実機で confirm と cancel の双方を確認 |
| 保存先表示 | pass | owner が `Save target:` 表示と実際の保存先一致を確認 |
| overwrite UX | pass | owner が chooser 側の overwrite confirmation を確認 |

- owner 確認メモ1: Save 押下直後に native save chooser が起動すること
- owner 確認メモ2: chooser 上で path/filename を選ぶと MainWindow の `Save target:` 表示に同じ path が見えること
- owner 確認メモ3: cancel では保存処理が継続せず、既存 save path が不要に壊れないこと
- owner 確認メモ4: overwrite confirmation が chooser 側で機能すること
- 実機メモ1: Left-L / Bottom-R を試しながら保存し、期待どおりの save 画像を取得できた（2026-04-16, owner確認）
- 実機メモ2: `Save target:` 表示は owner 実機で期待どおりに読めることを確認した（2026-04-16, owner確認）
- 実機メモ3: cancel と overwrite confirmation の双方が期待どおりに機能することを確認した（2026-04-16, owner確認）

#### 最終合意

- [x] P5-11 の事前対応表を記入した
- [x] 実装方針の Approve を得た
- [x] P5-11 着手可と判定した
- [x] P5-11 を Go 判定できる

## 15. P5-10 最低記入（watch / srcdir）

本節は P5-10（watch 導線実処理）のための事前整理ブロック。
watch 用 `srcdirL/srcdirR` は通常入力 `entPathL/R` と責務分離しつつ、upstream の dialog-led semantics と interval 更新責務を優先する。

### 15-1. 対象PR情報（P5-10）

- PR番号: TBD
- タスク番号: P5-10
- ブランチ名: `feature/gui-phase5-p5-10-watch-flow-srcdir-20260414`
- 担当: owner
- レビュー担当: TBD
- 予定実機環境: XFCE
- 判定対象導線: `btnSetting`、`btnOpenSrcdirL/R`、`SrcdirDialog`、`spnInterval`、`btnDaemonize`、`btnCancelDaemonize`

### 15-2. 上流読解ソース（P5-10）

- 参照ファイル1: `wallpaperoptimizer/WallpaperOptimizer/Widget/SettingDialog.py`
- 参照観点1: `btnOpenSrcdir_clicked` が `SrcdirDialog.openDialog(current_srcdir, side)` を呼び、OK 時だけ `srcdirs[idx]` と entry を更新すること
- 参照ファイル2: `wallpaperoptimizer/WallpaperOptimizer/Widget/SrcdirDialog.py`
- 参照観点2: side suffix 付き title、current folder 初期化、OK で folder path を返し cancel で `False` を返すこと
- 参照ファイル3: `wallpaperoptimizer/WallpaperOptimizer/WindowBase.py`
- 参照観点3: `spnInterval_value_changed` が option interval と statusbar を更新し、watch start/stop は caller 側責務であること
- 読解メモ1: upstream watch 用 source dir は通常入力 path とは別管理で、dialog 選択結果が設定 state へ反映される
- 読解メモ2: `spnInterval` は `GtkSpinButton` adjustment (`60 1 86400 1 10 0`) 前提で扱う
- 読解メモ3: `btnDaemonize_clicked` / `btnCancelDaemonize_clicked` 自体は base class では空実装だが、watch 導線の入口として独立している

### 15-3. 対応関係マトリクス（P5-10）

| 機能項目 | 上流挙動（要約） | Harite 実装方針 | 受け入れ条件 |
| --- | --- | --- | --- |
| watch source 選択 | `SettingDialog` から `SrcdirDialog` を開き、OK 時だけ `srcdirs[idx]` を更新 | MainWindow に `watch_srcdir_l/r` を追加し、fallback backend でも `SrcdirDialog` proxy と `Srcdir-L/R` 導線を持つ | `srcdirL/srcdirR` が通常入力と混線せず保持される |
| interval 更新 | `spnInterval_value_changed` が interval を即時更新 | MainWindow / fallback backend ともに spin の更新を actual 化する | 正の秒数で interval が更新され、0 以下は reject される |
| watch start | caller が watch 用 source dir をもとに実処理を開始 | `collect_watch_input_images` / `select_next_image` を使って初回選択を確定し、status へ反映する | source dir 指定あり/なしの分岐がテストで固定される |
| watch stop | caller が watch 状態を停止へ遷移 | running/idle を分けて停止状態を返す | idle stop は無害、running stop は stopped へ遷移する |

- 実装メモ1: MainWindow は `watch_srcdir_l/r`、`watch_source_display`、`watch_current_display`、`watch_running` を保持し、watch 専用 state を通常入力から分離した（2026-04-16）
- 実装メモ2: fallback backend は `SrcdirDialog` proxy と `btnOpenSrcdirL/R`、`lblWatchSources`、`lblWatchCurrent` を追加し、実 GTK では native folder chooser を優先、fallback では proxy state で回せる形にした（2026-04-16）
- 実装メモ3: 回帰テストでは `srcdirL/srcdirR` 指定あり/なし、watch interval 更新、fallback watch labels を固定し始めた。owner 実行は未実施（2026-04-16）
- 実装メモ4: 現実装の watch start は source dir 検証と初回選択結果の可視化までで、壁紙 plugin apply や interval ごとの継続切替はまだ接続していない（2026-04-16）

### 15-4. 非対応・差分（P5-10 事前整理）

- 非対応項目1: upstream `SettingDialog` 全体の legacy Glade 再現
  - 理由: 現段階で必要なのは watch source 選択 semantics であり、設定 dialog 全面復元はスコープ過大
  - 代替挙動: watch source 選択に必要な `SrcdirDialog` semantics を fallback/backend へ先行導入する
  - 差分分類: `仕様差分（意図的）`
- 非対応項目2: watch の長時間 daemon 実行ループそのもの
  - 理由: P5-10 の主眼は導線 actual 化と source dir 分岐固定であり、持続実行 orchestration は別責務
  - 代替挙動: start 時点の source dir 検証と初回選択結果の可視化までを今回の確定範囲とする
  - 差分分類: `段階実装`

### 15-5. 実装前レビュー合意（P5-10）

- [x] 15-2 と 15-3 の事前整理を記入した
- [x] `srcdirL/srcdirR` を通常入力と分離する方針を明記した
- [x] Approve を得た

### 15-6. 実装スコープ境界（P5-10）

- In scope:
  - `srcdirL/srcdirR` 選択導線
  - watch interval 更新
  - watch start/stop の status と初回選択可視化
- Out of scope:
  - 長時間 daemon 実行 orchestration
  - 壁紙 plugin apply を伴う実切替処理
  - apply/save 導線の追加変更
  - `SettingDialog` 全体の完全復元

### 15-7. 実装後エビデンス記録（P5-10）

#### 回帰（Owner実行）

- 実行日: 2026-04-16
- 実行者: owner
- コマンド: `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py`
- 結果: pass

- 回帰メモ1: MainWindow の `srcdirL/srcdirR` 分離、watch start/stop、interval 更新が green
- 回帰メモ2: ui_adapter の `on_btnOpenSrcdir_clicked` dispatch と fallback backend の watch labels / srcdir chooser proxy が green

#### 実機（XFCE）

| 観点 | 判定 | 根拠（スクリーンショット/ログ） |
| --- | --- | --- |
| Srcdir chooser 起動 | pass | owner が XFCE 実機で Srcdir chooser 起動を確認 |
| `srcdirL/srcdirR` 反映 | pass | owner が左右 srcdir 選択結果の反映を確認 |
| watch start/stop 表示 | pass | owner が watch start/stop の状態表示を確認 |
| interval 更新 | pass | owner が interval 更新の反映を確認 |

- 実機メモ1: P5-10 の実機確認項目 1,2,3,4 はいずれも OK（2026-04-16, owner確認）
- 実機メモ2: `do-it` は現時点で planned のため、本タスクの実機確認対象外とした。P5-10 完了後に別相談へ回す
- 実機メモ3: watch で壁紙が実際に切り替わる様子は観測できず、「たぶん動いている」段階に留まった。これは現実装が apply / 継続切替未接続であることと整合する（2026-04-16, owner確認）

#### 最終合意

- [x] P5-10 の事前対応表を記入した
- [x] 実装方針の Approve を得た
- [x] P5-10 着手可と判定した
- [x] P5-10 を Go 判定できる

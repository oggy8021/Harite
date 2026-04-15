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
- 判定対象導線: `tglUpper/Lower*`, `tglPushLeft/Right*`, `spn*Mergin`

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
  - `Options.py` の既定値は `align=center`, `valign=middle`, `mergin=0,0,0,0`, `fixed=False`, `interval=60`。Harite 側では vertical の `middle` を `center` 表現へ正規化している
- [x] 現行 fallback 実装の「対向ボタン無効化」は母体差分として維持するか、`pressed/released` ベースへ寄せ直すか
  - 母体寄せへ変更済み。無効化UXは廃止した
- [x] 現行 fallback 実装は `on_radFixed_toggled(False)` を呼んでいるが、母体のトグル処理は `align/valign` 更新であり、責務が一致していない
  - `align/valign` 更新へ置き換え済み
- [x] margin の `- / +` が機能しない直接原因は何か
  - 母体は `GtkSpinButton` の adjustment で step/range を持つが、fallback は `set_value(0)` だけで range/increment 未設定だった。母体値へ合わせて補完する
- [x] 現行 margin 実装の「4値一括 callback」が、母体の単項目更新と比べて仕様差分として許容されるか
  - UI adapter / fallback は母体どおり changed widget 起点で更新している。MainWindow 内部で最終的に `l,r,t,b` 文字列へ再集約して保持するのは Harite の状態表現であり、母体の単項目更新導線とは矛盾しない

### 12-8. 実装後エビデンス記録（P5-8）

#### 回帰（Owner実行）

- 実行日: 2026-04-15
- 実行者: owner
- コマンド: `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py`
- 結果: pass（100%）

#### 実機（XFCE）

| 観点 | 判定 | 根拠（スクリーンショット/ログ） |
| --- | --- | --- |
| Vertical toggle exclusion（same-side only） | pass | 母体寄せの切替挙動を確認 |
| Horizontal toggle exclusion（same-side only） | pass | 母体寄せの切替挙動を確認 |
| Margin reflect（UI表示） | pass | `Current state` で現在値を確認可能。Top + Top Margin の同時成立も母体 `Core.py` と整合 |
| Margin reflect（内部状態） | pass | GUI回帰 100% pass |

#### 最終合意

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
- 判定対象導線: `btnGetImgL`, `btnGetImgR`, `ImgOpenDialog`, `entPathL`, `entPathR`

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
- 読解メモ4: filter は `image/png`, `image/jpeg`, `image/bmp`, `image/gif` と `*.png`, `*.jpeg`, `*.jpg`, `*.bmp`, `*.gif`、および all files で構成される
- 読解メモ5: caller は選択 path を内部 args に保持し、entry には basename のみを表示する

### 13-3. 対応関係マトリクス（P5-9）

| 機能項目 | 上流挙動（要約） | 現行挙動（実装前） | 実装方針 | 受け入れ条件 |
| --- | --- | --- | --- | --- |
| Open-L/Open-R 起動 | `WindowBase.btnGetImg_clicked` が side ごとに `ImgOpenDialog.openDialog(current_path, Caps)` を呼ぶ | entry に値がないと `planned(path-required)` で停止 | `src/harite/gui/adapters/gtk_backend.py` に `ImgOpenDialog` proxy を追加し、button 押下で side-aware に dialog-open へ遷移させる | Open-L/Open-R 押下で dialog が開き、owner 回帰で `dialog-open` 状態が固定される |
| 選択確定 | `ImgOpenDialog.btnOpen_clicked` は `RESPONSE_OK`、`openDialog` は `get_filename()` を返す | entry の文字列をそのまま handler へ渡していた | `src/harite/gui/adapters/ui_adapter.py` と `src/harite/gui/views/main_window.py` で `path, side` を受け、左右別 path を保持しつつ `input_value` を再構成する | 選択確定で selected へ遷移し、左右の path が上書き更新され、owner 回帰が pass する |
| cancel / destroy | `DialogBase.btnCancel_clicked` は `RESPONSE_CANCEL`、`openDialog` は `False` を返して caller 側 path を更新しない | close semantics が未定義で、MainWindow は destroy をログするだけ | fallback proxy では cancel/close を `canceled` / `closed` 状態へ明示し、既存 path を保持したまま `on_ImgOpenDialog_destroy` を通知する | cancel/close 後に path が変化せず、状態表示が `canceled` または `closed` になる |
| title / 初期位置 | upstream は title に side suffix を付け、空 path 時は home、非空 path 時は absolute path 起点 | title/初期位置ともに未整理 | title suffix は fallback proxy で再現し、初期位置の home fallback は後続差分として記録する | title に side が表示される。home fallback 未実装は warn として明記される |
| filter 制御 | upstream は image filter と all files filter を dialog へ追加する | filter 制御なし | filter 種別は traceability に固定し、fallback proxy では metadata 再現から段階導入する | filter 差分が文書化され、後続実装の対象集合が固定される |
| entry 表示内容 | caller は `os.path.basename(path)` のみ表示する | path-required 前提で entry を入力欄として扱っていた | Harite では user 合意に従い、`entPathL/R` を表示欄として full path を保持する | GUI 上で選択元 path が判読でき、仕様差分として合意済みである |

### 13-4. 非対応・差分（P5-9）

- 非対応項目1: `entPathL/R` への basename-only 表示
  - 理由: user 合意は「選択されたソース path を表示する」ことであり、basename のみでは情報量が足りない
  - 代替挙動: full path を表示し、左右別 path を MainWindow 側でも保持する
  - 後続タスク: 必要なら preview 導入時に path 表示の縮退方針を再設計する
  - 差分分類: `仕様差分（意図的）`
- 非対応項目2: empty path 時の home directory 初期化
  - 理由: fallback proxy は実 chooser を持たず、ディレクトリ初期化の UI 意味がまだ薄い
  - 代替挙動: 既存 path があればそれを再利用し、空なら空のまま dialog-open とする
  - 後続タスク: 実 chooser 導入時に home 初期化を再現する
  - 差分分類: `暫定差分（期限付き）`
- 非対応項目3: image/all-files filter の UI 再現
  - 理由: 現行 fallback proxy は選択状態機械の復旧を優先し、chooser widget 自体は未導入
  - 代替挙動: 対応対象の MIME/pattern 集合だけ先に本書へ固定する
  - 後続タスク: P5-9 follow-up または実 chooser 導入時に filter UI を反映する
  - 差分分類: `暫定差分（期限付き）`

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

#### 回帰（Owner実行）

- 実行日: 2026-04-16
- 実行者: owner
- コマンド: `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_ui_adapter_dispatch.py tests/gui/test_ui_adapter_mapping_validation.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py`
- 結果: pass

#### 実機（XFCE）

| 観点 | 判定 | 根拠（スクリーンショット/ログ） |
| --- | --- | --- |
| Open dialog 起動 | blocked | 実機確認未記入 |
| confirm/cancel 状態遷移 | blocked | 実機確認未記入 |
| path 表示 | blocked | 実機確認未記入 |
| filter UI | warn | fallback proxy では未実装、traceability へ差分記録済み |

#### 最終合意

- [x] P5-9 の上流対応表を記入した
- [x] 回帰 pass を記録した
- [ ] 実機確認を完了した
- [ ] P5-9 を Go 判定できる

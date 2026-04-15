# GUI Phase5 Upstream Traceability Checklist

最終更新: 2026-04-15
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
- 備考: margin優先（`fixed > margin > toggles`）は現行仕様との整合を確認する

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
- [ ] `fixed > margin > toggles` の厳密適用条件（左右/上下の個別差）
- [x] 排他制御と `align/valign` 更新順序の依存有無
  - 母体は `pressed -> toggled(active時のみ) -> released(両方OFFならcenter/middle)` の責務分離になっている
- [ ] 例外導線（初期状態/未選択状態）での上流既定値
- [ ] 現行 fallback 実装の「対向ボタン無効化」は母体差分として維持するか、`pressed/released` ベースへ寄せ直すか
- [ ] 現行 fallback 実装は `on_radFixed_toggled(False)` を呼んでいるが、母体のトグル処理は `align/valign` 更新であり、責務が一致していない
- [ ] 現行 margin 実装の「4値一括 callback」が、母体の単項目更新と比べて仕様差分として許容されるか

### 12-8. 実装後エビデンス記録（P5-8）

#### 回帰（Owner実行）

- 実行日:
- 実行者:
- コマンド:
- 結果:

#### 実機（XFCE）

| 観点 | 判定 | 根拠（スクリーンショット/ログ） |
| --- | --- | --- |
| Vertical toggle exclusion（same-side only） | pass/warn/fail/blocked | |
| Horizontal toggle exclusion（same-side only） | pass/warn/fail/blocked | |
| Margin reflect（UI表示） | pass/warn/fail/blocked | |
| Margin reflect（内部状態） | pass/warn/fail/blocked | |

#### 最終合意

- [ ] P5-8 の受け入れ条件を満たした
- [ ] 非対応差分は `warn` として合意済み
- [ ] 次タスク（P5-9）へ進行可

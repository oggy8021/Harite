# GUI Phase5 P5-7 XFCE Rejudge Template (P5-x)

最終更新: 2026-04-14
対象: P5-x 再判定（前回結果を保持したまま追記）

## 目的

- 既存の P5-7 判定結果を削除せずに、P5-x 修正後の再判定を後方へ追記する。
- PR ごとの判定履歴を残し、改善差分を比較可能にする。

## 運用ルール

- 既存ファイルを上書きしない。前回結果はそのまま保持する。
- 再判定はこのテンプレートを複製して `out/manual-validation/` に保存する。
- `評価日` と `対象PR` は毎回更新する。

## 申し送り事項（方針転換）

- 「MainWindow単体でフローを先に成立」は暫定方針として扱い、今後の基準は「端から使える導線を優先」へ切り替える。
- 旧 `WallpaperOptimizer` の操作体験に倣い、MainWindow に連なる Dialog（特に `ImgOpenDialog` / `SaveWallpaperDialog`）を先に成立させる。
- MainWindow 単体への暫定ロジックの過密化は抑止し、導線責務を Dialog 側へ分配する。
- 主要導線（Save/Optimize/Apply/Open）は体験劣化が出た時点で回帰扱いとし、見た目調整より先に修正する。

## 保存先（P5-x 追記用）

- JSON: `out/manual-validation/pr-<PR番号>-xfce-rejudge.json`
- Report: `out/manual-validation/pr-<PR番号>-xfce-rejudge.md`
- PR Comment: `out/manual-validation/pr-<PR番号>-xfce-rejudge-pr-comment.md`
- Screenshot: `out/manual-validation/pr-<PR番号>-xfce-rejudge-mainwindow.png`
- Screenshot: `out/manual-validation/pr-<PR番号>-xfce-rejudge-optimize.png`
- Screenshot: `out/manual-validation/pr-<PR番号>-xfce-rejudge-apply.png`

## 再判定テンプレート（追記ブロック）

- 対象PR: <PR番号>
- 評価日: 2026/04/14
- 評価者: owner
- 前回判定参照: `docs/specs/gui/gui-phase5-p5-7-xfce-validation-template.md`

### 判定結果（P5-x）

- MainWindow: fail
- Optimize: regression
- Apply: regression
- Style consistency: fail
- Overall: fail

### 詳細メモ（P5-x）

- MainWindow:
  - OpenLは押下すると、ファイル選択ダイアログをオープンします。Thunarなどに同じくファイラー相当を使って、左画像として使いたい画像を辿り、指定します。指定したら、同パスが entPathLに挿入されます。
  - 今は  OpenL を押すと planned となるので、この実装はこれからの計画ということですよね。PhaseX として計画に載せて下さい。
  - パスを入力させるのと、結果的に選択した結果がパスになるのは真逆です
  - 拡張子を限定させてファイルをしているなどの機能が、 wallpaperoptimizer:WallpaperOptimizer>Widget>ImgOpenDialog.py にあります。
  - 現状は、入力させたパスの承認機能でしょうか？
  - OpenRは、省略します
  - Top、Bottom、Left、Right と対象にある tgl系操作は片方を有効にすると、もう片方は押下前に復帰するのが本来です。両方同時押しは矛盾があるため、受け入れないとの仕様が WallpaperOptimizerにはあります。 `gui-phase5-p5-4-retrofit-modernize.md` としても予定は決まっていないですね。これも実装を計画してください。
  - Saveの体験がよくないですね。どこになんというファイル名で保存されたかが分からないです。wallpaperoptimizer:WallpaperOptimizer>Widget>SaveWallpaperDialog.py 保存場所を指定する機能となっています。
  - Save Cancel
    - SaveDialog: cancel-failed Error:cancel returned false とあります。
  - Margin -+ の機能実装はいつでしょう
- Optimize:
  - MainWindow回帰により実施見送り（blocked）
- Apply:
  - MainWindow回帰により実施見送り（blocked）
- Style consistency:
  - 現状以下が左寄せで並びます。暫定許容でしょうか。
    - Top-L、Top-R
    - Left-L、Open-L、RightL、Left-R、Open-R、RightR
    - Bottom-L、Bottom-R
- Notes:

### WallpaperOptimizerにおける Dialog の呼び出し関係

gladeをベースに兄妹関係であると explain していましたが、プログラムとしては次の呼び出し関係にあります。

- MainWindow
  - ImgOpenDialog
  - SettingDialog
    - SrcdirDialog
  - ColorSelectionDialog
  - SaveWallpaperDialog

## PR コメント貼り付けテンプレート（P5-x）

```md
### Phase5 visual/manual gate (XFCE rejudge, P5-x)
- MainWindow: pass/warn/fail
- Optimize: pass/warn/fail
- Apply: pass/warn/fail
- Style consistency: pass/warn/fail
- Overall: pass/fail
- Notes: [delta from previous result and next action]

### Evidence
- Previous result: docs/specs/gui/gui-phase5-p5-7-xfce-validation-template.md
- Rejudge report: out/manual-validation/pr-<PR番号>-xfce-rejudge.md
- MainWindow: attached (pr-<PR番号>-xfce-rejudge-mainwindow.png)
- Optimize: attached (pr-<PR番号>-xfce-rejudge-optimize.png)
- Apply: attached (pr-<PR番号>-xfce-rejudge-apply.png)
```

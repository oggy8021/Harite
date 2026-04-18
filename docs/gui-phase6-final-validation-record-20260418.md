# GUI Phase6 Final Validation Record (2026-04-18)

最終更新: 2026-04-18
対象: Phase6 closeout validate

## 位置づけ

- 本書は 2026-04-18 時点の Phase6 実機確認記録である。
- [docs/manual-validation-gate.md](docs/manual-validation-gate.md) の運用ルールに従い、XFCE 実機確認時点の判定を記録する。
- 現時点では close 判定ではなく、Phase6 継続の根拠として扱う。

## 判定サマリ

- 判定: deferred
- 理由: MainWindow の全景、中央 2 列目、タイトル、メニュー、`Save As` 位置、watch タブ化対象、debug 情報配置について未払拭論点が残っている。加えて `Apply` を含む主要操作は未検証であり、Phase6 を閉じる条件を満たさない。
- 対象環境: XFCE
- 対象PRまたはブランチ: `feature/watch-tab-split`

## 前提（Phase6 完了確認）

- [docs/specs/gui/gui-phase6-planning.md](docs/specs/gui/gui-phase6-planning.md) の出口条件を確認した。
- [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md) を次フェーズ準備成果物として確認した。
- current runtime は glade prototype 前提を撤去済みである。
- `Save` は `Save As` chooser 主体、`Apply` は即時実行、`Save confirm` / `Save cancel` は常設しない前提である。

固定 GUI 回帰:

- コマンド:
  - `python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py tests/gui/test_phase5_visual_regression.py tests/gui/test_ui_adapter_backend_connect.py tests/gui/test_app_entrypoint.py`
- 結果: not-available
- 補足: 本記録時点では実行結果をまだ記録していない。

## 最終受け入れ基準（Phase6）

以下を満たした時点で Phase6 を close とする。

1. XFCE 実機で current GUI を起動し、MainWindow / Save As or Optimize / Apply immediate の主要導線を確認している。
2. 固定 GUI 回帰が pass している。
3. MainWindow / Optimize / Apply の 3 画面スクリーンショットが揃っている。
4. MainWindow の初見印象と、Phase6 を閉じてよいかの判断理由が記録されている。
5. Phase7 を product alignment フェーズとして開始してよい前提が確認されている。

## 実施記録（Phase6 closeout）

| Step | 内容 | 結果 | Notes |
| --- | --- | --- | --- |
| 1 | 固定 GUI 回帰実行 | not-available | 本記録時点では未記録 |
| 2 | `python -m harite.gui.app --bind-ui-backend --present-ui-window` で実ウィンドウ表示 | pass | MainWindow を開いて全景確認を実施 |
| 3 | MainWindow 入力欄編集と状態更新 | not-available | 今回の主眼は全景と配置確認 |
| 4 | `Save As` または `Optimize` 導線 | not-available | 主要操作は未検証 |
| 5 | `Apply` 即時実行導線 | not-available | 主要操作は未検証 |
| 6 | watch 導線確認（変更時のみ） | not-available | タブ対象の読み替えが必要と判明 |
| 7 | MainWindow / Optimize / Apply スクリーンショット取得 | not-available | 本記録時点では未記録 |

## MainWindow 初見印象

- 第一印象: 現時点の MainWindow には暫定感が残る。アプリケーションタイトル `Harite Studio` は要求していない名称であり、全景の第一印象からずれる。中央 2 列目も、左右ディスプレイイメージと十字配置を読ませる構造より、左寄せの仮配置として見える。
- 操作感: `Save As` が下方に沈んで見え、flow の一部として認識しにくい。`Apply` を含む主要操作については今回未検証であり、現時点では操作体験の良否を判定できない。
- 「間に合わせではない」判断: fail
- 理由: Phase6 で払拭すべき UI 上の違和感が残っている。具体的には、タイトル、中央 2 列目の構図、中央列の不要ラベル、watch タブ化対象、最下部 debug 情報の扱い、`Prefs` `Help` `About` の標準的な置き方が未整理である。よって Phase6 の出口品質には未達である。

## 未払拭論点

- アプリケーションタイトルは `Harite` とし、`Harite Studio` は採用しない。
- 上下左右の tgl ボタン系は操作意味をボタン配置そのもので示すため、[docs/specs/gui/gui-phase5-p5-7-xfce-validation-template.md](docs/specs/gui/gui-phase5-p5-7-xfce-validation-template.md) の `中央2列目イメージ` から外してはならない。
- `Save As` は flow として認識できる位置に置く。下方へ沈める配置は採用しない。
- 中央 2 列目に `Wallpaper Optimizer`、`Glade-like layout (Phase5 P5-2)`、`Compose / Input` のような不要ラベルを残さない。
- Compose エリアは左右ディスプレイイメージと十字配置を再現できる構造へ戻す。
- watch のタブ化対象は `Compose / Input` から `Apply` までの中央 2 列目であり、マージン類は入れ替え対象にしない。
- `Apply mode` など製作途中向けの情報はステータスエリアより下の最下部へ退避する。
- `Secondary / Meta` という命名は避け、`Prefs` `Help` `About` を標準的な文字メニューとして扱う読みを優先する。
- `Color` はまだ場所検討の余地があり、Colorとのボタン配置だけは開いたエリアに用意すること。

## 相談ポイント

- glade 由来の中央 2 列目配置をそのまま再現できない箇所があるなら、不可能と明言したうえで代替案を示して相談へ戻す。
- watch tab は中央 2 列目差し替え型で読む。margin 系まで切り替える案は採用しない。
- `Prefs` `Help` `About` は左下の余白へ置くより、タイトル直下の文字メニューへ寄せる方が標準的である。

## 関連仕様メモ

- [docs/specs/gui/gui-phase6-layout-redefinition.md](docs/specs/gui/gui-phase6-layout-redefinition.md) に、上記の不通過理由と再定義要求を反映済みである。

## クローズ条件

- [ ] 固定 GUI 回帰を記録した
- [x] 実ウィンドウ起動結果を記録した
- [x] MainWindow 初見印象を記録した
- [ ] 3 画面スクリーンショットを確認した
- [x] 本ファイルの「判定サマリ」を更新した
- [ ] Phase7 開始可否の判断を追記した

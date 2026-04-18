# GUI Phase6 Final Validation Record (2026-04-18)

最終更新: 2026-04-18
対象: Phase6 closeout validate

## 位置づけ

- 本書は 2026-04-18 時点の Phase6 実機確認記録である。
- [docs/manual-validation-gate.md](docs/manual-validation-gate.md) の運用ルールに従い、XFCE 実機確認時点の判定を記録する。
- 現時点では close 判定ではなく、Phase6 継続の根拠として扱う。

## 判定サマリ

- 判定: pass
- 理由: Phase6 は見た目とレイアウトの受領ライン到達を主目的とし、その観点では十字配置、watch タブ化、`Prefs` 入口復旧、resize 耐性、左右マージン compact 化まで揃い、了承ラインに達した。`Apply` 結果の疑義や周辺整合性は Phase7 のテーマとして切り分け、Phase6 close 判定からは分離する。
- 対象環境: XFCE
- 対象PRまたはブランチ: `feature/watch-tab-split`

## 前提（Phase6 完了確認）

- [docs/specs/gui/gui-phase6-planning.md](docs/specs/gui/gui-phase6-planning.md) の出口条件を確認した。
- [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md) を次フェーズ準備成果物として確認した。
- current runtime は glade prototype 前提を撤去済みである。
- `Save` は `Save As` chooser 主体、`Apply` は即時実行、`Save confirm` / `Save cancel` は常設しない前提である。

固定 GUI 回帰:

- コマンド:
  - `python.exe -m pytest -q tests/gui`
- 結果: pass
- 補足: オーナー実行で 100% pass を確認済み。

## 最終受け入れ基準（Phase6）

以下を満たした時点で Phase6 を close とする。

1. XFCE 実機で current GUI を起動し、MainWindow の見た目と主要導線の存在を確認している。
2. 固定 GUI 回帰が pass している。
3. MainWindow / Optimize / Apply の 3 画面スクリーンショットが揃っている。
4. MainWindow の初見印象と、Phase6 を閉じてよいかの判断理由が記録されている。
5. Phase7 を product alignment フェーズとして開始してよい前提が確認されている。

## 実施記録（Phase6 closeout）

| Step | 内容 | 結果 | Notes |
| --- | --- | --- | --- |
| 1 | 固定 GUI 回帰実行 | pass | オーナー実行の `python.exe -m pytest -q tests/gui` が 100% pass |
| 2 | `python -m harite.gui.app --bind-ui-backend --present-ui-window` で実ウィンドウ表示 | pass | MainWindow を開いて全景確認を実施 |
| 3 | MainWindow 入力欄編集と状態更新 | pass | `Open-L/R` による path 表示更新と十字配置の読みを確認 |
| 4 | `Save As` または `Optimize` 導線 | deferred | Phase6 では主要導線の存在確認までを対象とし、結果整合性の細部は Phase7 へ送る |
| 5 | `Apply` 即時実行導線 | deferred | XFCE 2 画面（2048x1280 x 2、連続 4096x1280）で、`700x1244.jpg` と `700x394.jpg` から生成した `out/manual-validation/harite_output_0003.jpg` を `Default` 適用すると、各 2048x1280 画面に同一 4096x1280 結果を当てに行くような圧縮表示に見えた。ただし XFCE で同じ画像を手動選択し、日本語 UI 上の「縦横比を維持せず全画面化」として表示した場合も同じ見た目となったため、desktop/plugin の通常貼り付け意味と一致している可能性が高い。`Auto-split` は想定どおり。整合性確認は Phase7 へ送る |
| 6 | watch 導線確認（変更時のみ） | pass | watch タブの配置整理と resize 耐性を確認。機能深掘りは Phase7 へ送る |
| 7 | MainWindow / Optimize / Apply スクリーンショット取得 | pass | MainWindow に加え、`out/manual-validation/pr-xxx-xfce-optimize.png` と `out/manual-validation/pr-xxx-xfce-apply.png` を配置済み |

## MainWindow 初見印象

- 第一印象: `Harite` タイトル、`Prefs / Help / About` の header 配置、中央 2 列目の十字配置、watch タブ分離、Prefs 最小可視化、resize 時の中央寄せが揃い、以前の暫定感は大きく薄れた。最大化時も中央 block が崩れず、Phase6 のレイアウト目標にはかなり近い。
- 操作感: `Main` / `Watch` の切り替え、十字配置の意味、左右マージンの外周 control としての読みは改善した。`Apply` 結果の整合性や周辺組み合わせの疑義は残るが、それらは Phase7 で扱う product alignment 論点として切り分ける。
- 「間に合わせではない」判断: pass
- 理由: Phase6 の目的を見た目とレイアウトの受領ライン到達と捉えるなら、主要違和感は十分に払拭された。残る疑義は見た目の未達ではなく、Phase7 で詰めるべき整合性論点である。

## 払拭済み論点

- アプリケーションタイトルは `Harite` へ戻した。
- Compose エリアは左右ディスプレイイメージと十字配置を読める構造へ戻した。
- `Prefs` `Help` `About` は header 側の文字メニューとして整理した。
- watch は中央 2 列目差し替え型の tab として読みやすくなった。
- `Prefs` は必要部品として押下可能な入口と最小限の可視化が復旧した。
- resize 時も tab 内コンテンツが左上へ崩れず、中央 block として読めるようになった。
- 左右マージンは compact な外周 control として読みやすくなった。

## 未払拭論点

- `Save As` は flow として認識できる位置に置く。下方へ沈める配置は採用しない。
- `Apply` 結果には、XFCE 2 画面（2048x1280 x 2）で 4096x1280 の optimize 結果を `Default` 適用した際、各画面へ同一ワイド画像をそのまま適用し、左右方向に圧縮されて潰れるように見える組み合わせがある。ただし XFCE の手動設定で「縦横比を維持せず全画面化」を選んだ見た目とは一致しており、`Default` が plugin 実装部の通常 apply 経路を素直に呼んでいるだけの可能性がある。`Auto-split` は想定どおりであり、この差分は Phase7 の整合性テーマとして切り分けて扱う。
- `Color` は依然として Phase7 候補であり、Phase6 close 条件には含めない整理を維持する。

## 残チェックリスト（close 前の最小確認）

本節は close 前の保留確認として使っていたが、2026-04-18 時点で Phase6 は見た目受領ラインに達したと判断したため、残件は Phase7 側の整合性テーマへ移した。

## 相談ポイント

- glade 由来の中央 2 列目配置をそのまま再現できない箇所があるなら、不可能と明言したうえで代替案を示して相談へ戻す。
- watch tab は中央 2 列目差し替え型で読む。margin 系まで切り替える案は採用しない。
- `Prefs` `Help` `About` は左下の余白へ置くより、タイトル直下の文字メニューへ寄せる方が標準的である。

## 関連仕様メモ

- [docs/specs/gui/gui-phase6-layout-redefinition.md](docs/specs/gui/gui-phase6-layout-redefinition.md) に、上記の不通過理由と再定義要求を反映済みである。

## Phase7 開始可否

- 現時点の判断: pass
- 理由: Phase6 は見た目とレイアウトの了承ラインに到達した。今後の主論点は `Apply` 結果の疑義、watch の本格責務、`Prefs` の内容 grouping、auto-detect の露出、`Color` の扱いなど、product alignment の整合性テーマである。
- したがって、Phase7 は準備段階ではなく、次に着手すべき正規フェーズとして開始してよい。

## クローズ条件

- [x] 固定 GUI 回帰を記録した
- [x] 実ウィンドウ起動結果を記録した
- [x] MainWindow 初見印象を記録した
- [x] 3 画面スクリーンショットを確認した
- [x] 本ファイルの「判定サマリ」を更新した
- [x] Phase7 開始可否の判断を追記した

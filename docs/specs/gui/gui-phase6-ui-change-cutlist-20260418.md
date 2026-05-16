# GUI Phase6 UI Change Cutlist (2026-04-18)

最終更新: 2026-04-18
対象: Phase6 layout-first implementation

## 位置づけ

- 本書は、Phase6 継続のために実装へ落とす UI 変更項目を切り出した作業チェックリストである。
- 順序は「1. UI 変更項目を切り出す -> 2. 調整項目を事前相談 -> 3. レイアウト類だけ先に実装 -> 4. ボタン/イベント/機能結線を再実施」に従う。
- 機能結線は本書の後段に分離し、まずはレイアウトだけでレビュー可能な粒度へ落とす。

## 入力元

- [docs/gui-phase6-final-validation-record-20260418.md](docs/gui-phase6-final-validation-record-20260418.md)
- [docs/specs/gui/gui-phase6-layout-redefinition.md](docs/specs/gui/gui-phase6-layout-redefinition.md)
- [docs/specs/gui/gui-phase6-owner-layout-consultation-20260418.md](docs/specs/gui/gui-phase6-owner-layout-consultation-20260418.md)
- [docs/specs/gui/gui-phase5-p5-7-xfce-validation-template.md](docs/specs/gui/gui-phase5-p5-7-xfce-validation-template.md)

## Phase6 実装順序

1. 本書で UI 変更項目を固定する。
2. [docs/specs/gui/gui-phase6-ui-preconsultation-20260418.md](docs/specs/gui/gui-phase6-ui-preconsultation-20260418.md) の推薦実装を採用済み前提として反映する。
3. レイアウト類だけを先に実装し、実機確認レビューへ掛ける。
4. レビュー結果を踏まえて、ボタン、イベントハンドラ、機能結線を再実施する。

## 2026-04-18 採用済み前提

- `Prefs` `Help` `About` は、独立ボタン列ではなく、タイトル直下の軽いメニューバーとして実装する。
- `Save As` は title/menu 行ではなく、flow 行右端へ置く。
- 中央 2 列目は、座標の完全一致ではなく意味配置の厳密一致を優先して再構成する。
- watch タブは中央 2 列目のみを差し替え、main 側の watch 要約は `running / stopped` の最小表示に留める。
- `Optimize` / `Apply` は強い枠線ではなく、軽いグルーピングで右下主操作領域として読ませる。
- `Status` は短い状態要約だけに留め、debug は最下部の控えめな別帯へ分離する。
- `Color` 機能そのものは今回見せず、非表示のまま将来用の配置余地だけを残す。

## A。レイアウト先行で実装する項目

### A-1. タイトルと上部帯

- [ ] ウィンドウタイトルを `Harite` に変更する。
- [ ] `Harite Studio` 表記を UI 上から除去する。
- [ ] 上部帯に `Prefs` `Help` `About` をメニューバーとして配置する。
- [ ] メニューバーは重い native 再現ではなく、軽い横並びテキスト + 余白 + hover 反応程度で構成する。
- [ ] `Flow: Compose -> Optimize -> Apply` を上部帯へ置く。
- [ ] `Save As` を flow から認識できる右側位置へ移す。
- [ ] `Save As` を title/menu 行ではなく flow 行右端へ置く。
- [ ] `Save As` を下方の埋もれた位置から外す。

### A-2. 中央 2 列目の再配置

- [ ] 中央 2 列目を左右ディスプレイイメージとして読める構図へ戻す。
- [ ] `tglUpper*` / `tglLower*` を中央列センターへ置く。
- [ ] `tglPushLeft*` / `btnGetImg*` / `tglPushRight*` を `中央2列目イメージ` に沿ってセンタリングする。
- [ ] 左右画像パス欄と clear 操作を中央構図に沿って再配置する。
- [ ] 中央 2 列目の左寄せ仮配置を除去する。
- [ ] 余白や widget サイズは調整してよいが、意味配置の軸は崩さない。
- [ ] `Wallpaper Optimizer` 表示を除去する。
- [ ] `Glade-like layout (Phase5 P5-2)` 表示を除去する。
- [ ] `Compose / Input` 表示を中央列から除去する。

### A-3. マージン帯の固定

- [ ] 上マージン、左マージン、右マージン、下マージンを main 側へ維持する。
- [ ] マージン帯は watch タブ切り替え対象に含めない。
- [ ] 中央 2 列目とマージン帯の視覚的な関係を崩さない。

### A-4. Optimize / Apply エリア

- [ ] `Optimize` と `Apply` を右下寄せで近接配置する。
- [ ] 右下エリアを主操作領域として視覚的に読めるようにする。
- [ ] 強い枠線や重いパネル化は避け、余白・整列・小見出し程度の軽いグルーピングで読ませる。
- [ ] まだ未結線の状態でも、将来の主操作位置としてレビュー可能な見た目にする。

### A-5. watch タブの枠組み

- [ ] watch は独立下部帯ではなく、中央 2 列目差し替え型のタブとして構成する。
- [ ] main tab のレイアウトを壊さないまま watch tab へ切り替えられる見た目にする。
- [ ] main 側には watch 要約を残す前提で、詳細 controls は watch 側に寄せる。
- [ ] main 側の watch 要約は `running / stopped` の最小表示に留める。

### A-6. Status / Debug の分離

- [ ] `Status` は main 末尾の通常状態表示帯として維持する。
- [ ] `Status` には短い状態要約だけを残す。
- [ ] `Apply mode` 由来の開発中表示は `Status` より下へ移す。
- [ ] debug 情報をアプリケーション最下部へ退避する。
- [ ] debug 帯は細い境界線または背景差だけの控えめな見た目にする。
- [ ] debug 情報が中央 UI の構図を壊さないようにする。

### A-7. `Color` の後置き余地

- [ ] `Color` 機能そのものは今回のレイアウト先行実装では表示しない。
- [ ] ただし将来の `Color` ボタン配置を吸収できる開いたエリアは確保する。
- [ ] `Color` を見せないことで全景レビューを乱さないようにする。

## B。レビュー後に結線する項目

### B-1. ボタン結線

- [ ] `Prefs` `Help` `About` のメニューバー項目操作を結線する。
- [ ] `Save As` の表示位置変更後に chooser 導線を再結線する。
- [ ] `Optimize` / `Apply` ボタンの配置変更後に handler 結線を再確認する。
- [ ] watch tab の start/stop / srcdir / interval 結線を再確認する。

### B-2. 状態表示結線

- [ ] `Status` に残す情報と debug 側へ落とす情報を再分離する。
- [ ] watch の main 側要約表示を最小粒度で結線する。
- [ ] `Apply mode` 系の開発中表示が残る場合は、最下部表示へ結線し直す。

### B-3. 機能確認

- [ ] `Save As or Optimize` 導線を再確認する。
- [ ] `Apply` 即時実行導線を再確認する。
- [ ] watch 導線を tab 切り替え後の UI に合わせて再確認する。
- [ ] 必要なら fixed regression と実機確認を再度回す。

## 実装ブロック

### Block 1. 上部帯とタイトル

- 範囲: title / menu / flow / `Save As`
- 目的: 第一印象のずれを先に除去する
- 実装後レビュー観点: `Harite`、メニューバー、`Save As` の位置

### Block 2. 中央 2 列目とマージン帯

- 範囲: tgl 群 / open / clear / path / fixed / margins
- 目的: 十字配置と左右ディスプレイイメージの回復
- 実装後レビュー観点: `中央2列目イメージ` との整合

### Block 3. 右下主操作領域

- 範囲: `Optimize` / `Apply`
- 目的: 主操作の視線導線を固定する
- 実装後レビュー観点: 右下近接配置の妥当性

### Block 4. watch タブと最下部 debug 帯

- 範囲: watch tab 枠 / status / debug
- 目的: main 側構図を保ったまま watch と debug を退避する
- 実装後レビュー観点: タブ差し替え範囲、status と debug の分離

## 完了条件

- [ ] レイアウト先行実装の対象が UI 部品単位で分解されている。
- [ ] 事前相談が必要な項目が別紙へ切り出されている。
- [ ] レイアウトだけでレビュー可能な実装ブロックに分かれている。
- [ ] 結線の後戻りを前提に、レイアウトと機能結線が分離されている。

# Harite — 破棄候補 / 保留延長（pending）

最終更新: 2026-06-09  
起点: 2026-06-08（[20260518 feature-overview](finished/20260518-2047-feature-overview.md) 分割時に切り出し）

## 位置づけ

- 本書は feature inventory の **破棄候補 / 保留延長** 棚である。
- 現行 planning 入口は [20260609-1200-feature-overview.md](20260609-1200-feature-overview.md)。
- いっさい触れないことを機械的に固定する棚ではなく、reformation 残件や懐かしさで安易に復活させないためのガード。

再度候補へ戻す場合は、「なぜ今それを戻すのか」を改めて説明できることを前提にする。

## 破棄候補 / 保留延長

| ID | 項目 | 概要 | 現時点の判断 |
| --- | --- | --- | --- |
| H-01 | 内部 issue の延長での feature 化 | reformation 中に出た surface 不整合を、そのまま新 feature として抱え続ける。 | 本 inventory の対象外。現行 surface の整合修正は spec / 実装側で閉じる |
| H-02 | 旧 UI / 旧 surface 互換の長期維持 | 旧 CLI option や旧 GUI 前提を将来 feature の制約として保持し続ける。 | reformation 後の負債持ち越しになりやすく、基本は縮小方向 |
| H-03 | 早期の多機能化 | source / plugin / GUI を一度に拡張する大規模 feature を最初の planning でまとめて始める。 | planning 粒度が粗すぎるため、入口では採らない |
| H-04 | K-02 source metadata / cache | 画像 source ごとのタグ・取得元・評価・利用履歴。 | **オーナー棚卸: 不要**（2026-06-03）。C-02/C-05/C-01 の source モデルで足りる |
| H-05 | K-03 favorites / history | 過去の生成・適用壁紙や source の振り返り・再利用。 | **オーナー棚卸: 不要**（2026-06-03）。保存スコープと product 焦点がずれる |
| H-06 | K-06 import / export profiles | optimize / apply / slideshow 設定の profile 単位の持ち運び。 | **オーナー棚卸: 不要・やめる**（2026-06-03）。registry + preset で運用し、別途 export は負債になりやすい |
| H-07 | K-05 scheduler / timed automation | 時刻・曜日・条件で optimize / apply / slideshow を起動。 | **オーナー棚卸: 不要に近い**（2026-06-03）。下記 §K-05 参照。明示ニーズが出るまで採らない |
| H-08 | K-01 ~~watch~~ slideshow 再構成 | 旧 inventory「Watch」= 現 **Slideshow** タブ。slideshow 再構成は **C-02 / C-05 で充足**。 | **オーナー棚卸: 破棄**（2026-06-04）。monitor / 単 display の操作整理は **P-03 完了**（[#359](../online-issues/closed/issue-359.md)）。Phase10 mock 等の「Watch」表記は legacy 掃除対象 |

## planning 入口カテゴリ（参照 — 打ち消し線は破棄・保留）

### 1. 外部ソース連携

- 外部壁紙サイト連携 — **第1期完了**（C-01）
- 取得結果キャッシュ — C-01 に包含
- ~~source metadata~~ — H-04

### 2. source / slideshow

- source registry / source profiles — **完了**（C-02）
- slideshow source 強化 — **完了**（C-05）
- ~~K-01 watch 再構成~~ — H-08
- ~~scheduler / timed automation~~ — H-07

### 3. plugin / apply 拡張

- plugin capability 可視化 — 構想保持 [C-03](20260609-1200-feature-overview.md#2-構想保持)
- plugin 拡張パック — 構想保持 [K-04](20260609-1200-feature-overview.md#2-構想保持)
- per-monitor apply policy の強化 — issue 駆動

### 4. GUI / UX 導線改善

- GUI 利用導線の再設計 — **完了**（C-04）
- ~~import / export profiles~~ — H-06
- ~~favorites / history~~ — H-05

## K-05（scheduler）— 残しうるストーリーと見送り理由

オーナー判断どおり **当面は採らない**（H-07）。


| ストーリー | なぜ弱い / 代替 |
| --- | --- |
| 勤務時間だけ slideshow を回したい | Interval + 手動 Start/Stop で足りる。常駐 scheduler は tray/サービス設計が要る |
| 朝 9 時に気象図を取り直して apply | C-01 は start 前 sync + slideshow interval。OS のログイン時起動は Harite 外 |
| 夜は個人写真・昼は JMA preset に自動切替 | profile / srcdir の時刻連動切替は未実装だが、scheduler 全体より限定 feature の方が筋がよい（それでも今は不要寄り） |
| 曜日ごとに別 source profile | GUI 複雑化・テスト・スリープ復帰とセット。明示要望なし |


**結論:** 時刻駆動の**汎用 automation 基盤**（K-05）は Harite の core 価値から外す。将来ニーズが出たら K-05 復活ではなく**限定スコープ**で再検討する。

# Harite Project Initial Build Reformation WS10 Feature Overview

最終更新: 2026-05-30

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 10 を具体化する子文書である。
- 主題は、`1.0.0` 後の新運用で扱う後続機能の棚卸しと feature overview の作成である。
- 本書は `1.0.0` gate ではなく、その後に開く backlog / planning 入口として扱う。

## この stream で固定すること

- 断片的な feature アイデアを inventory 化する。
- 実装候補、構想保持、破棄候補を粗く切り分ける。
- post-`1.0.0` の feature planning 入口文書として、次期 planning の土台を作る。

## 対象

- 外部壁紙サイト連携
- watch / sources / plugins の将来拡張案
- GUI / CLI の新導線案
- 将来の product improvement 候補

## 非対象

- `1.0.0` 前に実装を始めること
- release / packaging 整理
- docs 再編そのもの
- 現行 surface の内部 issue 解決

## 現在ステータス

- WS10 は、reformation 本体の不整合修正 stream ではなく、post-`1.0.0` planning の入口整備 stream として扱う。
- 現時点では feature の優先順位確定や issue 分解までは行わず、まず overview 上で inventory を受ける。
- 本書の今回の役割は、断片案を「着手候補 / 構想保持 / 破棄候補」に粗く並べ、次の planning で掘る対象を見える化することにある。

## 一次 inventory

### 1. 着手候補

ここでの並び順は、現時点の product 価値の大きさそのものではなく、先に入れやすい順・前提を作りやすい順を優先する。

**前提**: Qt 移行（`harite-gtk` / `harite-qt` 二本立て化）を先行させ、完了後に以下を順次着手する。

| ID | 項目 | 概要 | planning で最初に詰めること |
| --- | --- | --- | --- |
| C-02 | source registry / source profiles | watch directory や外部 source を単発入力ではなく、名前付き source 群として保存・再利用できるようにする。 | source モデル、GUI/CLI surface、設定保存形式 |
| C-05 | slideshow source 強化 | slideshow の source を単発 directory から、複数 source・source profile・将来の外部 source へ広げる。初期スコープは local directory、同期済み cloud folder、ローカル mount 済み NAS/SMB/WebDAV directory までとし、それ以上の直接連携は将来余裕がある場合に限る。 | source 正規化、順序規則、GUI owner state との整合 |
| C-01 | 外部壁紙サイト連携 | 外部サイトや API から壁紙候補を取得し、Harite の source として扱えるようにする。C-05 の local/mounted source 扱いを一種の先行試行とみなせる。オーナー発案の本丸 feature。 | 対象サイト、取得方法、利用規約、キャッシュ方針 |

### 2. 構想保持

ここは、方向性自体は有力だが、着手候補より先に掘ると設計順が逆転しやすい項目、または採用条件が未整理の項目を置く棚である。
永久保留ではなく、着手候補側の planning 結果で前提が揃えば、次の段階で着手候補へ再分類しうる。

| ID | 項目 | 概要 | 保持理由 / 採用条件 |
| --- | --- | --- | --- |
| C-03 | plugin capability 可視化 | plugin ごとに受理 target や OS 制約を可視化し、apply / slideshow / GUI での分岐を分かりやすくする。 | **採用条件**: 仕様書に根拠を持ち、UIUX として明確に改善される論拠（spec 改訂案 + 表示面のストーリー）が示せたとき |
| C-04 | GUI 利用導線の再設計 | optimize / apply / slideshow を単なる tab 群ではなく、利用目的ベースで再構成する。 | **採用条件**: 既存レイアウトの骨格を維持しつつ、世の標準傾向や UX トレンドを引用した「主要導線がより良くなる」ストーリーが組めたとき。「利用目的ベース」の具体が未整理のため現時点では積極採用しない |
| K-01 | watch 機能の再構成 | 現行 slideshow / source / monitor 変化監視を含め、watch を独立機能として設計し直す。 | 現時点では source / slideshow / plugin の基礎設計が先。現行 GUI に Watch tab が存在するが実装は未完であり、Qt 移行後に方向性を整理する |
| K-02 | source metadata / cache | 画像 source ごとにタグ、取得元、評価、最終利用履歴などを持てるようにする。 | 外部 source 連携や history 導線と一緒に詰めたほうがよい |
| K-03 | favorites / history | 過去に生成・適用した壁紙や source を振り返り、再利用できるようにする。 | 保存スコープと UX を先に整理したい |
| K-04 | plugin 拡張パック | Linux 以外や追加 desktop 向け plugin を外付け拡張として扱えるようにする。 | capability model と packaging 方針が先に必要 |
| K-05 | scheduler / timed automation | 時刻・曜日・条件に応じて optimize / apply / slideshow を起動する。 | watch / source / profile 面が固まってからのほうが設計しやすい |
| K-06 | import / export profiles | optimize / apply / slideshow の運用設定を profile 単位で持ち運べるようにする。 | source / settings / GUI 導線との責務分担を整理してからでよい |

#### C-04 rough ideas（参考保持）

- task ベース: 「作る」「適用する」「回す」の 3 系統から入る。
- scenario ベース: 「単画面で 1 枚作る」「2 画面向けに合成する」「すぐ適用する」「slideshow を始める」のような利用目的から入る。
- progressive disclosure: 最初から全 widget を見せず、基本面と詳細面を分ける。
- Wallpaperoptimizer 的な強みは残しつつ、最初の入口は「やりたいこと」から入り、細かい調整は後で開く。

### 3. 破棄候補 / 保留延長

ここは、今後いっさい触れないことを機械的に固定する棚ではなく、reformation 中の残件や懐かしさで安易に復活させないためのガードとして置く。
再度候補へ戻す場合は、「なぜ今それを戻すのか」を改めて説明できることを前提にする。

| ID | 項目 | 概要 | 現時点の判断 |
| --- | --- | --- | --- |
| H-01 | 内部 issue の延長での feature 化 | reformation 中に出た surface 不整合を、そのまま新 feature として抱え続ける。 | WS10 の対象外。現行 surface の整合修正は WS1-WS9 側で閉じる |
| H-02 | 旧 UI / 旧 surface 互換の長期維持 | 旧 CLI option や旧 GUI 前提を将来 feature の制約として保持し続ける。 | reformation 後の負債持ち越しになりやすく、基本は縮小方向 |
| H-03 | 早期の多機能化 | source / plugin / GUI を一度に拡張する大規模 feature を最初の planning でまとめて始める。 | planning 粒度が粗すぎるため、入口では採らない |

## planning 入口カテゴリ

### 1. 外部ソース連携

- 外部壁紙サイト連携
- 取得結果キャッシュ
- source metadata

### 2. source / watch / slideshow

- source registry / source profiles
- slideshow source 強化
- watch 機能の再構成
- scheduler / timed automation

### 3. plugin / apply 拡張

- plugin capability 可視化
- plugin 拡張パック
- per-monitor apply policy の強化

### 4. GUI / UX 導線改善

- GUI 利用導線の再設計
- import / export profiles
- favorites / history

## 次期 planning への渡し方

- overview では実装順をまだ固定せず、まず候補群の置き場所を作る。
- 次の planning では、着手候補から 1 つか 2 つを選び、個別の spec / plan / tasks へ落とす。
- 構想保持に置いた項目は、着手候補の設計結果を受けて再分類する。
- 破棄候補 / 保留延長は、reformation 残件や懐かしさで復活させず、再度の明示理由がある場合だけ戻す。

## 現時点の論点

### 1. 構想の棚卸し方

- 断片メモのまま残すのではなく、一覧として集約する必要がある。
- ただし、いまは優先順位の精密化より inventory 化を優先する。

### 2. 分類の粒度

- すぐ着手候補
- 中期の構想保持
- 破棄または保留延長

### 3. 次期 planning への渡し方

- overview から次の親 planning へどう送るか。
- 単発メモを増やしすぎず、入口文書で受ける必要がある。

### 4. 入口カテゴリの初期案

- 外部ソース連携や取得導線の拡張
- watch / sources / plugins の機能拡張
- GUI / CLI の新しい利用導線
- product improvement と UX 強化

## 近中期の優先順序（2026-05-30 確定）

```
[先行] Qt 移行（harite-gtk / harite-qt 二本立て化）
         ↓ 完了後
[次段] C-02 source registry  ←── C-01 の器を作る
       C-05 slideshow source 強化  ←── local/mounted まで
         ↓ 揃ったら
[本丸] C-01 外部壁紙サイト連携  ←── オーナー発案
```

- Qt 移行の詳細は [docs/working/20260530-2201-pyqt6-migration-plan.md](20260530-2201-pyqt6-migration-plan.md) を参照する。
- C-03 / C-04 は採用条件が揃った時点で着手候補へ再分類する。条件が揃わなければ構想保持のまま維持する。

## Qt 移行後 Windows 検証 backlog（W-xx）

C-xx（新機能 inventory）とは別軸。`harite-qt` 実機検証で表面化した polish / プラットフォームギャップ。

| ID | 項目 | Issue | 詳細 |
| --- | --- | --- | --- |
| W-01 | action cluster レイアウト | #342 | **完了**（#346, 2026-05-31） |
| W-02 | Windows slideshow 方針 | #341 | spec-as-designed → planning |
| W-03 | Apply / 壁紙 / 解像度 | #343 | **C 先行** → A/B は C 後 |

統合文書: [docs/working/20260531-1200-windows-qt-validation-backlog.md](20260531-1200-windows-qt-validation-backlog.md)  
観測ログ: [docs/online-issues/README.md](../online-issues/README.md)

## 初動タスク

1. 現在頭にある後続機能案を列挙する。
2. それぞれを「着手候補 / 構想保持 / 破棄候補」に粗く分類する。
3. 外部壁紙サイト連携のような大きめ構想を、単発案ではなく overview 項目として受ける。
4. post-`1.0.0` planning の入口となる最小構造を定める。

進捗メモ:

- 一次 inventory を本書へ反映した。
- 2026-05-30: オーナーとの議論を経て、C-03/C-04 を構想保持へ移動（採用条件付き）。Qt 移行を全 feature に先行させる方針を確定した。
- 次段では Qt 移行計画を進め、完了後に C-02/C-05/C-01 の順で個別 planning 文書へ分離する。
- 2026-05-31: Windows 実機検証由来の W-01〜W-03 を [20260531-1200-windows-qt-validation-backlog.md](20260531-1200-windows-qt-validation-backlog.md) に集約。

## 完了条件

- 後続機能 inventory の枠組みが説明可能になっている。
- `1.0.0` gate の外に置く理由が説明可能になっている。
- 構想の受け皿として overview を置く理由が説明可能になっている。
- Workstream 1・3・4・5 と混線せずに次段へ送れる状態になっている。
- 少なくとも一次 inventory が overview 上で参照可能になっている。

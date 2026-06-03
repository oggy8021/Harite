# Harite Project Initial Build Reformation WS10 Feature Overview

最終更新: 2026-06-03（v1.0.0 リリース済み・第4波 **C-01 planning 着手**）

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 10 を具体化する子文書である。
- 主題は **v1.0.0 以降**の後続機能の棚卸しと planning 入口である。
- **`1.0.0` はリリース済み**（2026-06）。当初の「gate 前は着手しない」等のガードは **適用しない**。本書は現行 backlog / planning 正本として随時更新する。

## この stream で固定すること

- 断片的な feature アイデアを inventory 化する。
- 実装候補、構想保持、破棄候補を粗く切り分ける。
- post-`1.0.0` feature の planning 入口として、次期 planning の土台を更新し続ける。

## 対象

- 外部壁紙サイト連携
- slideshow / sources / plugins の将来拡張案
- GUI / CLI の新導線案
- 将来の product improvement 候補

## 非対象

- release / packaging 整理（別 stream）
- docs 再編そのもの
- 現行 surface の内部 issue 解決（online-issues / polish 波で扱う）

## 現在ステータス

- **v1.0.0 リリース済み。** WS10 は post-1.0.x の **継続 planning / backlog 入口**として運用する。
- **2026-06-01:** Qt 移行・W-xx 完了後、online-issues #353–359 を受けて **着手候補を再評価** した（下記 §近端 backlog / §近中期の優先順序）。
- C-xx（大 feature）の順序は **C-02 → C-05 → C-01 を維持**。近端 **F-01 / P-01–02 は完了**（2026-06-01）。

## 一次 inventory

### 1. 着手候補

ここでの並び順は、現時点の product 価値の大きさそのものではなく、先に入れやすい順・前提を作りやすい順を優先する。

**前提**: Qt 移行（`harite-gtk` / `harite-qt` 二本立て化）を先行させ、完了後に以下を順次着手する。

| ID | 項目 | 概要 | planning で最初に詰めること |
| --- | --- | --- | --- |
| C-02 | source registry / source profiles | slideshow 用 directory 等を単発入力ではなく、名前付き source 群として保存・再利用できるようにする。 | **完了**（#373–378, audit: [20260601-c02-3layer-audit.md](finished/20260601-c02-3layer-audit.md)） — [harite-source-spec.md](../specs/source/harite-source-spec.md) |
| C-05 | slideshow source 強化 | slideshow の source を単発 directory から、複数 source・source profile・将来の外部 source へ広げる。初期スコープは local directory、同期済み cloud folder、ローカル mount 済み NAS/SMB/WebDAV directory までとし、それ以上の直接連携は将来余裕がある場合に限る。 | **完了**（#382–384, audit: [20260602-c05-3layer-audit.md](finished/20260602-c05-3layer-audit.md)） |
| C-01 | 外部壁紙サイト連携 | 外部 API から **都度取得** し remote cache（ステージング）経由で slideshow に載せる。第1 provider=気象庁。 | **spec 1b** PR — [§12–15](../specs/source/harite-source-spec.md)（#388 済） |
| C-01-J | JMA 天気図 list.json カタログ | list.json 全種の日本語整理と **preset 選定ストーリー**（公式 schema なし）。 | **別フェーズ** — [inventory](20260603-jma-weather-map-list-inventory.md) |
| C-01-E | 外部 source 探索拡張 | NDL / CODH 等の調査・preset 追加。 | **別フェーズ**（C-01 第1 impl 後） |

### 1b. 近端 backlog（Qt 完了後・2026-06-01）

online-issues 由来。**着手順序（2026-06-01 確定）:** F-01 → P-01/P-02 → issue 整理 → C-02。詳細は各 issue と [online-issues/README.md](../online-issues/README.md)。

| ID | 項目 | Issue | 分類 | 現判断 |
| --- | --- | --- | --- | --- |
| F-01 | Windows 設定ファイル path | [#354](../online-issues/closed/issue-354.md) | foundation | **完了**（#365–367, 2026-06-01 Windows 実機確認） |
| P-01 | 左右 path / srcdir の swap | [#353](../online-issues/closed/issue-353.md) | GUI polish | **完了**（#369–371, 2026-06-01 オーナー確認） |
| P-02 | Slideshow srcdir クリア | [#358](../online-issues/closed/issue-358.md) | GUI polish | **完了**（#369–371, 個別 clear 採用） |
| P-03 | 単 display 時の -R 側無効化 | [#359](../online-issues/issue-359.md) | edge case UX | **構想保持（着手順序外）** — 急がない |

### 2. 構想保持

ここは、方向性自体は有力だが、着手候補より先に掘ると設計順が逆転しやすい項目、または採用条件が未整理の項目を置く棚である。
永久保留ではなく、着手候補側の planning 結果で前提が揃えば、次の段階で着手候補へ再分類しうる。

| ID | 項目 | 概要 | 保持理由 / 採用条件 |
| --- | --- | --- | --- |
| C-03 | plugin capability 可視化 | plugin ごとに受理 target や OS 制約を可視化し、apply / slideshow / GUI での分岐を分かりやすくする。 | **採用条件**: 仕様書に根拠を持ち、UIUX として明確に改善される論拠（spec 改訂案 + 表示面のストーリー）が示せたとき |
| C-04 | GUI 利用導線の再設計 | optimize / apply / slideshow を単なる tab 群ではなく、利用目的ベースで再構成する。 | **採用条件**: 既存レイアウトの骨格を維持しつつ、世の標準傾向や UX トレンドを引用した「主要導線がより良くなる」ストーリーが組めたとき。「利用目的ベース」の具体が未整理のため現時点では積極採用しない |
| K-01 | ~~watch~~ slideshow 再構成（**旧語整理待ち**） | 旧 inventory「Watch」= 現 **Slideshow**。monitor 変化監視等を別 feature に切り出すなら K-01 を再定義。 | **構想保持・要再分類** — C-02/C-05 後。Phase10 mock の Watch 表記は legacy。 |
| K-02 | source metadata / cache | 画像 source ごとにタグ、取得元、評価、最終利用履歴などを持てるようにする。 | 外部 source 連携や history 導線と一緒に詰めたほうがよい |
| K-03 | favorites / history | 過去に生成・適用した壁紙や source を振り返り、再利用できるようにする。 | 保存スコープと UX を先に整理したい |
| K-04 | plugin 拡張パック | Linux 以外や追加 desktop 向け plugin を外付け拡張として扱えるようにする。 | capability model と packaging 方針が先に必要 |
| K-05 | scheduler / timed automation | 時刻・曜日・条件に応じて optimize / apply / slideshow を起動する。 | source / profile / slideshow 面が固まってからのほうが設計しやすい |
| K-06 | import / export profiles | optimize / apply / slideshow の運用設定を profile 単位で持ち運べるようにする。 | source / settings / GUI 導線との責務分担を整理してからでよい |
| P-03 | 単 display 時の -R 側無効化 | 検出 1 枚のとき右パネル操作を disabled にする案。 | **採用条件**: 単 display 再現手順、disabled 範囲の spec、GTK/Qt テスト方針が揃ったとき（[#359](../online-issues/issue-359.md)） |

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

### 2. source / slideshow

- source registry / source profiles
- slideshow source 強化
- scheduler / timed automation（[K-05](#2-構想保持)）
- （旧語 Watch = slideshow — 2026-06-01 用語整理）

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
- slideshow / sources / plugins の機能拡張
- GUI / CLI の新しい利用導線
- product improvement と UX 強化

## 近中期の優先順序（2026-06-01 確定）

```
[完了] Qt 移行 + W-01〜W-03 + F-01 + P-01/P-02 + #353/#358 closed
         ↓
[完了] C-02  source registry     ← #373–378, audit: [20260601-c02-3layer-audit.md](finished/20260601-c02-3layer-audit.md)
         ↓
[完了] C-05  slideshow source 強化   ← #382–384, audit: [20260602-c05-3layer-audit.md](finished/20260602-c05-3layer-audit.md)
         ↓
        C-01  外部壁紙サイト連携   ← 1b spec（気象庁・オンデマンド cache）
        C-01-J / C-01-E  … 別フェーズ（list カタログ / 他 source 探索）

[着手順序外・構想保持] P-03 #359（単 display / -R 無効化 — 急がない）
```

- Qt 移行の詳細は [docs/working/finished/20260530-2201-pyqt6-migration-plan.md](finished/20260530-2201-pyqt6-migration-plan.md) を参照する。
- C-03 / C-04 は採用条件が揃った時点で着手候補へ再分類する。
- F-01 は Windows **`%APPDATA%\harite\harite-settings.json`**（Roaming）。**旧 path 互換・移行なし**。
- P-01–02 は §9 GUI 合意工程の最初の実践。**2026-06-01 完了**（3 層 audit は [closed/issue-353](../online-issues/closed/issue-353.md) / [issue-358](../online-issues/closed/issue-358.md)）。

## Qt 移行後 Windows 検証 backlog（W-xx）

C-xx（新機能 inventory）とは別軸。`harite-qt` 実機検証で表面化した polish / プラットフォームギャップ。

| ID | 項目 | Issue | 詳細 |
| --- | --- | --- | --- |
| W-01 | action cluster レイアウト | #342 | **完了**（#346, 2026-05-31） |
| W-02 | Windows slideshow 方針 | #341 | **完了**（W-02-A #355 + #356, 2026-05-31） |
| W-03 | Apply / 壁紙 / 解像度 | #343 | **完了**（#349 + #352、背景色不問で #343 クローズ, 2026-05-31） |

統合文書: [docs/working/finished/20260531-1200-windows-qt-validation-backlog.md](finished/20260531-1200-windows-qt-validation-backlog.md)  
観測ログ: [docs/online-issues/README.md](../online-issues/README.md)

## 初動タスク（WS10 立ち上げ — **完了**）

1. ~~後続機能案を列挙する。~~ → 一次 inventory 反映済み
2. ~~着手候補 / 構想保持 / 破棄候補に分類する。~~ → 本書 §1–3
3. ~~大きめ構想を overview 項目として受ける。~~ → C-01 等
4. ~~planning 入口の最小構造を定める。~~ → 本書 + `docs/working/` / online-issues 連携

以降の更新は **inventory 追加・優先順序・完了記録**のみ（初動タスクの再実施は不要）。

進捗メモ:

- 一次 inventory を本書へ反映した。
- 2026-05-30: オーナーとの議論を経て、C-03/C-04 を構想保持へ移動（採用条件付き）。Qt 移行を全 feature に先行させる方針を確定した。
- 次段では Qt 移行計画を進め、完了後に C-02/C-05/C-01 の順で個別 planning 文書へ分離する。
- 2026-05-31: Windows 実機検証由来の W-01〜W-03 を [finished/20260531-1200-windows-qt-validation-backlog.md](finished/20260531-1200-windows-qt-validation-backlog.md) に集約。
- 2026-06-01: online-issues #353–359 を inventory 化。F-01 / P-01–02 を近端着手候補、P-03 を構想保持へ。C-02→C-05→C-01 は維持。
- 2026-06-01: **v1.0.0 リリース済み** — gate 前ガードは obsolete。本書を post-1.0.x backlog 入口として継続更新。
- 2026-06-01: 第4波 **C-02 planning 着手** — [20260601-1400-c02-source-registry-planning.md](20260601-1400-c02-source-registry-planning.md)
- 2026-06-01: 第4波 **C-02 完了**（#373–378）— 3-layer audit: [20260601-c02-3layer-audit.md](finished/20260601-c02-3layer-audit.md)。次は C-05 planning。
- 2026-06-02: 第4波 **C-05 planning 着手** — [20260602-1400-c05-slideshow-source-enhancement-planning.md](20260602-1400-c05-slideshow-source-enhancement-planning.md)
- 2026-06-02: 第4波 **C-05 完了**（#382–384）— audit: [20260602-c05-3layer-audit.md](finished/20260602-c05-3layer-audit.md)。次は **C-01** planning。
- 2026-06-03: 第4波 **C-01 spec 1a 完了**（#388）— 1b: 気象庁・オンデマンド cache / Start 前 Sync / Interval 下限 600s
- 2026-06-03: **C-01-J**（list.json カタログ）・**C-01-E**（他 source 探索）を overview 別フェーズとして追加

## 完了条件（WS10 立ち上げ — **達成済み**）

- 後続機能 inventory の枠組みが説明可能になっている。
- 構想の受け皿として overview を置く理由が説明可能になっている。
- Workstream 1・3・4・5 と混線せずに次段へ送れる状態になっている。
- 少なくとも一次 inventory が overview 上で参照可能になっている。

※ 当初の「`1.0.0` gate の外に置く」完了条件は、**v1.0.0 リリースにより obsolete**。以降は上記 4 点 + 各 feature 完了記録の更新で十分。

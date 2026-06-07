# Harite Project Initial Build Reformation WS10 Feature Overview

最終更新: 2026-06-08（P-08 Main+Margins Drawer planning 着手）

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 10 を具体化する子文書である。
- 主題は **v1.0.0 以降**の後続機能の棚卸しと planning 入口である。
- `**1.0.0` はリリース済み**（2026-06）。当初の「gate 前は着手しない」等のガードは **適用しない**。本書は現行 backlog / planning 正本として随時更新する。

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


| ID        | 項目                                | 概要                                                                              | planning で最初に詰めること                                                                                                                                                                  |
| --------- | --------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C-02      | source registry / source profiles | slideshow 用 directory 等を単発入力ではなく、名前付き source 群として保存・再利用できるようにする。                | **完了** — [planning](finished/20260601-1400-c02-source-registry-planning.md) / [audit](finished/20260601-c02-3layer-audit.md) / [source-spec](../specs/source/harite-source-spec.md) |
| C-05      | slideshow source 強化               | slideshow の source を単発 directory から、複数 source・source profile・将来の外部 source へ広げる。 | **完了** — [planning](finished/20260602-1400-c05-slideshow-source-enhancement-planning.md) / [audit](finished/20260602-c05-3layer-audit.md)                                           |
| C-01      | 外部壁紙サイト連携                         | 外部 API から **都度取得** し remote cache 経由で slideshow に載せる。第1 provider=気象庁。           | **完了** — [planning](finished/20260603-1400-c01-external-wallpaper-source-planning.md) / [audit](finished/20260603-c01-3layer-audit.md)                                              |
| C-01-J    | JMA 天気図 list.json カタログ            | list.json 棚卸・preset 選定（カラー 2 + モノクロ実況 2）。全 12 葉のギャラリー UI は **スコープ外**。           | **完了**（2026-06-03 実機確認）— [調査・完了記録](finished/20260603-jma-weather-map-list-inventory.md)                                                                                             |
| C-01-E    | 外部 source 探索拡張                    | NDL / CODH preset + provider（実現性検証スコープ）。                                        | **完了**（#400）— [統合索引](finished/20260603-c01-e-merged-inventory.md) / [軽量 audit](finished/20260603-c01-e-3layer-audit.md)                                                             |
| C-01-E-KW | CODH キーワード検索のユーザー指定               | `harite-settings.json` の `codh_keyword`、Manage `keyword(CODH)`。                 | **完了**（#413）— [planning](finished/20260605-c01-e-kw-codh-keyword-planning.md)                                                                                                       |
| C-01-F    | remote live sync on slideshow tick | CODH index+cursor、JMA interval sync。provider 別 tick sync。                         | **完了**（#425–426, spec #427）— [planning](finished/20260604-c01-f-remote-sync-on-tick-planning-draft.md)                                                                                  |
| P-05      | Manage sources リスト整理              | local / preset 二面板、自動ソート、keyword 行移設。                                           | **完了**（Qt）— [planning](finished/20260606-p05-manage-sources-panel-planning.md)                                                                                                         |
| P-03      | 単 display / monitor まわり UX        | 1 枚検出時の -R 無効化等。                                                                | **完了**（#420）— [planning](finished/20260606-p03-single-display-ux-planning.md) / [audit](finished/20260606-p03-3layer-audit.md)（[#359](../online-issues/closed/issue-359.md)）        |


### 1b. 近端 backlog（Qt 完了後・2026-06-01）

online-issues 由来。**着手順序（2026-06-01 確定）:** F-01 → P-01/P-02 → issue 整理 → C-02。詳細は各 issue と [online-issues/README.md](../online-issues/README.md)。


| ID   | 項目                         | Issue                                        | 分類                                                       | 現判断                                                                                                                            |
| ---- | -------------------------- | -------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| F-01 | Windows 設定ファイル path        | [#354](../online-issues/closed/issue-354.md) | foundation                                               | **完了**（#365–367, 2026-06-01 Windows 実機確認）                                                                                      |
| P-01 | 左右 path / srcdir の swap    | [#353](../online-issues/closed/issue-353.md) | GUI polish                                               | **完了**（#369–371, 2026-06-01 オーナー確認）                                                                                            |
| P-02 | Slideshow srcdir クリア       | [#358](../online-issues/closed/issue-358.md) | GUI polish                                               | **完了**（#369–371, 個別 clear 採用）                                                                                                  |
| P-03 | 単 display / monitor まわり UX | [#359](../online-issues/closed/issue-359.md) | edge case UX                                             | **完了**（#420）— [planning](finished/20260606-p03-single-display-ux-planning.md) / [audit](finished/20260606-p03-3layer-audit.md) |
| P-06 | Slideshow CODH キーワード chip  | --                                           | Slideshow タブ右上角 read-only（`codh_keyword` 確認）。編集は Manage。 | **完了**（Qt）— [planning](finished/20260606-p06-slideshow-codh-keyword-chip-planning.md)                                             |
| P-07 | Slideshow Drawer 開閉視認性     | --                                           | 背景ずらし・上辺線・chevron 回転。palette 優先（#412）。                   | **完了**（#417）— [planning](finished/20260606-p07-slideshow-drawer-open-state-planning.md)                                                                                                         |
| P-04 | Main action cluster 整理        | --                                           | Preview/Optimize/Apply の常設 label 削減。C-04 後続 polish。              | **完了**（#429）— [planning](finished/20260607-p04-main-action-cluster-planning-draft.md)                                                                                  |
| P-08 | Main + Margins Drawer（案 B）   | --                                           | Margins 専用 tab 廃止。4 spin 常設 + embed/text/position は Drawer。C-04 §7.2。 | **gate 通過** — [planning draft](20260608-p08-main-margins-drawer-planning-draft.md) / [slice-memo](design/20260608-p08-main-margins-drawer-slice-memo.md)（gui-spec §3 改訂中） |


### 2. 構想保持

ここは、方向性自体は有力だが、着手候補より先に掘ると設計順が逆転しやすい項目、または採用条件が未整理の項目を置く棚である。
永久保留ではなく、着手候補側の planning 結果で前提が揃えば、次の段階で着手候補へ再分類しうる。


| ID     | 項目                                 | 概要                                                                      | 保持理由 / 採用条件                                                                                                                                |
| ------ | ---------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| C-03   | plugin capability 可視化              | plugin ごとに受理 target や OS 制約を可視化し、apply / slideshow / GUI での分岐を分かりやすくする。 | **保留・縮小** — 詳細は [C-04 計画正本](finished/20260604-c04-gui-surface-planning-draft.md) §6（独立パネルは出さず help 整理に吸収可）                                          |
| C-04   | GUI surface / 利用導線                 | 3 tab 骨格は維持。Slideshow/Margins の密度整理、feedback・Error 視覚、Drawer、preset 余地。 | **完了**（#406–409, spec #427）— [planning](finished/20260604-c04-gui-surface-planning-draft.md)            |
| K-04   | plugin 拡張パック                       | Linux 以外や追加 desktop 向け plugin を外付け拡張として扱えるようにする。                        | capability model と packaging 方針が先に必要                                                                                                       |


C-04 の rough ideas・採択表・widget 切り分けは [finished/20260604-c04-gui-surface-planning-draft.md](finished/20260604-c04-gui-surface-planning-draft.md) を参照（本 overview では重複しない）。

### 3. 破棄候補 / 保留延長

ここは、今後いっさい触れないことを機械的に固定する棚ではなく、reformation 中の残件や懐かしさで安易に復活させないためのガードとして置く。
再度候補へ戻す場合は、「なぜ今それを戻すのか」を改めて説明できることを前提にする。


| ID   | 項目                                | 概要                                                                         | 現時点の判断                                                                                                                                                               |
| ---- | --------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H-01 | 内部 issue の延長での feature 化          | reformation 中に出た surface 不整合を、そのまま新 feature として抱え続ける。                      | WS10 の対象外。現行 surface の整合修正は WS1-WS9 側で閉じる                                                                                                                            |
| H-02 | 旧 UI / 旧 surface 互換の長期維持          | 旧 CLI option や旧 GUI 前提を将来 feature の制約として保持し続ける。                            | reformation 後の負債持ち越しになりやすく、基本は縮小方向                                                                                                                                   |
| H-03 | 早期の多機能化                           | source / plugin / GUI を一度に拡張する大規模 feature を最初の planning でまとめて始める。          | planning 粒度が粗すぎるため、入口では採らない                                                                                                                                          |
| H-04 | K-02 source metadata / cache      | 画像 source ごとのタグ・取得元・評価・利用履歴。                                               | **オーナー棚卸: 不要**（2026-06-03）。C-02/C-05/C-01 の source モデルで足りる                                                                                                           |
| H-05 | K-03 favorites / history          | 過去の生成・適用壁紙や source の振り返り・再利用。                                              | **オーナー棚卸: 不要**（2026-06-03）。保存スコープと product 焦点がずれる                                                                                                                    |
| H-06 | K-06 import / export profiles     | optimize / apply / slideshow 設定の profile 単位の持ち運び。                          | **オーナー棚卸: 不要・やめる**（2026-06-03）。registry + preset で運用し、別途 export は負債になりやすい                                                                                            |
| H-07 | K-05 scheduler / timed automation | 時刻・曜日・条件で optimize / apply / slideshow を起動。                                | **オーナー棚卸: 不要に近い**（2026-06-03）。下記 §K-05 残ストーリー参照。明示ニーズが出るまで採らない                                                                                                       |
| H-08 | K-01 ~~watch~~ slideshow 再構成      | 旧 inventory「Watch」= 現 **Slideshow** タブ。slideshow 再構成は **C-02 / C-05 で充足**。 | **オーナー棚卸: 破棄**（2026-06-04）。monitor / 単 display の操作整理は **P-03 完了**（[#359](../online-issues/closed/issue-359.md)）。Phase10 mock 等の「Watch」表記は legacy 掃除対象（product 名ではない） |


## planning 入口カテゴリ

### 1. 外部ソース連携

- 外部壁紙サイト連携
- 取得結果キャッシュ
- source metadata

### 2. source / slideshow

- source registry / source profiles
- slideshow source 強化
- ~~K-01 watch 再構成~~ — [H-08](#3-破棄候補--保留延長)（C-02/C-05 充足。monitor 縁は P-03）
- ~~scheduler / timed automation~~ — [H-07](#3-破棄候補--保留延長)（オーナー: 不要に近い）

### 3. plugin / apply 拡張

- plugin capability 可視化
- plugin 拡張パック
- per-monitor apply policy の強化

### 4. GUI / UX 導線改善

- GUI 利用導線の再設計
- ~~import / export profiles~~ — [H-06](#3-破棄候補--保留延長)
- ~~favorites / history~~ — [H-05](#3-破棄候補--保留延長)

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
        C-01  外部壁紙サイト連携   ← 完了 #392–393 + audit
        C-01-J  JMA list / preset 選定   ← 完了（調査 + モノクロ 2 preset、実機確認）
        C-01-E  他 source 探索   ← 完了（#400）
        C-04   GUI surface      ← 完了（#406–409）
         ↓
[完了] C-01-E-KW（CODH キーワード UI）← #413
         ↓
[完了] P-05 Manage 面板分割（Qt）← [planning](finished/20260606-p05-manage-sources-panel-planning.md)
         ↓
[完了] P-03 単 display UX（#420）    ← [planning](finished/20260606-p03-single-display-ux-planning.md)
[完了] P-06 CODH keyword chip（Qt）← [planning](finished/20260606-p06-slideshow-codh-keyword-chip-planning.md)

[完了] P-07 Drawer 開閉視認性（#417）← [planning](finished/20260606-p07-slideshow-drawer-open-state-planning.md)

[完了] C-01-F remote tick sync  ← #425–426 + spec #427。[planning](finished/20260604-c01-f-remote-sync-on-tick-planning-draft.md)

[完了] P-04 Main action cluster  ← #429。[planning](finished/20260607-p04-main-action-cluster-planning-draft.md)

[planning] P-08 Main + Margins Drawer（C-04 案 B）  ← [draft](20260608-p08-main-margins-drawer-planning-draft.md)
```

- Qt 移行の詳細は [docs/working/finished/20260530-2201-pyqt6-migration-plan.md](finished/20260530-2201-pyqt6-migration-plan.md) を参照する。
- C-04 は [planning](finished/20260604-c04-gui-surface-planning-draft.md) — waves 0/b/a/c + spec #427 完了。
- **完了:** C-01-E-KW（#413）— [planning](finished/20260605-c01-e-kw-codh-keyword-planning.md)。
- **完了:** P-05 Manage Local/Presets タブ — [planning](finished/20260606-p05-manage-sources-panel-planning.md)。P-06 Slideshow CODH chip（Qt）— [planning](finished/20260606-p06-slideshow-codh-keyword-chip-planning.md)。
- **完了:** P-07 Drawer 開閉視認性（#417、#412 close）— [planning](finished/20260606-p07-slideshow-drawer-open-state-planning.md)。
- **完了:** P-03 単 display UX（#420、#359 close）— [planning](finished/20260606-p03-single-display-ux-planning.md) / [audit](finished/20260606-p03-3layer-audit.md)。
- **完了:** C-01-F（#425–426 CODH/JMA tick sync、spec #427）— [planning](finished/20260604-c01-f-remote-sync-on-tick-planning-draft.md)。
- **完了:** P-04 Main action cluster（#429）— [planning](finished/20260607-p04-main-action-cluster-planning-draft.md)。
- F-01 は Windows `**%APPDATA%\harite\harite-settings.json`**（Roaming）。**旧 path 互換・移行なし**。
- P-01–02 は §9 GUI 合意工程の最初の実践。**2026-06-01 完了**（3 層 audit は [closed/issue-353](../online-issues/closed/issue-353.md) / [issue-358](../online-issues/closed/issue-358.md)）。

## Qt 移行後 Windows 検証 backlog（W-xx）

C-xx（新機能 inventory）とは別軸。`harite-qt` 実機検証で表面化した polish / プラットフォームギャップ。


| ID   | 項目                   | Issue | 詳細                                               |
| ---- | -------------------- | ----- | ------------------------------------------------ |
| W-01 | action cluster レイアウト | #342  | **完了**（#346, 2026-05-31）                         |
| W-02 | Windows slideshow 方針 | #341  | **完了**（W-02-A #355 + #356, 2026-05-31）           |
| W-03 | Apply / 壁紙 / 解像度     | #343  | **完了**（#349 + #352、背景色不問で #343 クローズ, 2026-05-31） |


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
- 2026-06-01: 第4波 **C-02 planning 着手** — [20260601-1400-c02-source-registry-planning.md](finished/20260601-1400-c02-source-registry-planning.md)
- 2026-06-01: 第4波 **C-02 完了**（#373–378）— 3-layer audit: [20260601-c02-3layer-audit.md](finished/20260601-c02-3layer-audit.md)。次は C-05 planning。
- 2026-06-02: 第4波 **C-05 planning 着手** — [20260602-1400-c05-slideshow-source-enhancement-planning.md](finished/20260602-1400-c05-slideshow-source-enhancement-planning.md)
- 2026-06-02: 第4波 **C-05 完了**（#382–384）— audit: [20260602-c05-3layer-audit.md](finished/20260602-c05-3layer-audit.md)。次は **C-01** planning。
- 2026-06-03: 第4波 **C-01 spec 1b 完了**（#390）— 気象庁 §15、preset JSON、オンデマンド cache、Interval 下限は preset 駆動
- 2026-06-03: **C-01-J**（list.json カタログ）・**C-01-E**（他 source 探索）を overview 別フェーズとして追加
- 2026-06-03: 第4波 **C-01 完了**（#392 core、#393 GUI）— audit: [20260603-c01-3layer-audit.md](finished/20260603-c01-3layer-audit.md)
- 2026-06-03: オーナー棚卸 — **K-02 / K-03 / K-06 破棄**（H-04–H-06）、**K-05 不要に近い**（H-07）
- 2026-06-03: **C-01-J 調査完了** — live list.json 全 12 葉棚卸 → [20260603-jma-weather-map-list-inventory.md](finished/20260603-jma-weather-map-list-inventory.md)
- 2026-06-03: **C-01-J 完了** — モノクロ実況 preset 2 種 + オーナー実機確認。ft24/48・カタログ UI は見送り確定
- 2026-06-03: **C-01-E 追補** — remote-cache 孤児 directory の materialize 時自動削除（`prune_orphan_remote_cache_dirs`）。**C-01-E-KW**（CODH キーワードユーザー指定）は §2 構想保持へ先送り
- 2026-06-03: **C-01-E 完了** — 実現性検証 + #400 merge。[統合索引](finished/20260603-c01-e-merged-inventory.md) / [軽量 audit](finished/20260603-c01-e-3layer-audit.md)
- 2026-06-04: **第4波 C-02/C-05/C-01/C-01-J/C-01-E** の planning・inventory を `working/finished/` へ移動（本 overview のみ `working/` に残す）
- 2026-06-04: **K-01 破棄（H-08）** — slideshow 再構成は C-02/C-05 済み。display / monitor 縁は P-03 に集約。legacy「Watch」表記の docs 掃除を開始
- 2026-06-04: **C-04 計画正本** — [finished/20260604-c04-gui-surface-planning-draft.md](finished/20260604-c04-gui-surface-planning-draft.md)（GUI surface / オーナー観測・採択表・Slideshow/Margins 切り分け）
- 2026-06-04: **C-04 impl 完了** — #406–409（footer / Slideshow drawer / Margins slim / icon tooltips）
- 2026-06-04: **C-01-F planning draft** — remote をライブ feed 化（tick 毎 sync・provider 別）。[finished/20260604-c01-f-remote-sync-on-tick-planning-draft.md](finished/20260604-c01-f-remote-sync-on-tick-planning-draft.md)
- 2026-06-05: **C-01-E-KW planning draft** — CODH キーワード UI 起票
- 2026-06-06: **C-01-E-KW 完了** — #413。[planning](finished/20260605-c01-e-kw-codh-keyword-planning.md)
- 2026-06-06: **C-01-F 据え置き** — CODH 負荷懸念。gate F1–F3 未記入のまま保留
- 2026-06-07: **C-01-F planning 合意** — CODH §3.1 index+cursor（B 案）、cursor 永続化。§7 F1–F4 pass。impl 着手可
- 2026-06-06: **P-05 / P-03 planning draft** 起票 — 次着手候補
- 2026-06-06: **P-06 planning draft** — Slideshow 右上角 CODH keyword read-only（Footer 不採用、P-05 と分離）
- 2026-06-06: **P-05 完了**（Qt）— Manage dialog Local/Presets タブ、preset グループ見出し、keyword 移設
- 2026-06-06: **P-06 完了**（Qt）— Slideshow 右上角 `CODH: {keyword}` read-only chip
- 2026-06-06: **P-07 planning draft** — Slideshow Drawer 開閉視認性（背景+縁取り+chevron、palette 優先）— [#412](https://github.com/oggy8021/Harite/issues/412)
- 2026-06-06: **P-07 完了** — #417 merge、#412 close。Drawer 開閉スタイル（Qt/GTK）、planning を [finished/](finished/20260606-p07-slideshow-drawer-open-state-planning.md) へ
- 2026-06-06: **P-03 完了** — #420 merge、#359 close。第二スロット disabled + L-only slideshow。planning / audit を [finished/](finished/20260606-p03-single-display-ux-planning.md) へ
- 2026-06-07: **P-05 / P-06 棚卸し** — 完了済み planning を [finished/](finished/20260606-p05-manage-sources-panel-planning.md) / [finished/](finished/20260606-p06-slideshow-codh-keyword-chip-planning.md) へ（overview リンク整合）
- 2026-06-07: **C-01-F / C-04 棚卸し** — impl + spec 改訂完了。planning を [finished/](finished/20260604-c01-f-remote-sync-on-tick-planning-draft.md) / [finished/](finished/20260604-c04-gui-surface-planning-draft.md) へ。`working/` 直下は overview のみ active
- 2026-06-08: **P-04 完了** — #429 merge。Main Preview/Optimize/Apply の label 削減（result/target→footer、mode help→tooltip、見出し廃止、idle 文言廃止）。planning を [finished/](finished/20260607-p04-main-action-cluster-planning-draft.md) へ。
- 2026-06-08: **remote-cache pytest 隔離** — #430 merge。`HARITE_REMOTE_CACHE_ROOT`・materialize の catalog 由来 cache root・全テスト autouse 隔離（本番 APPDATA 汚染防止）。
- 2026-06-08: **P-08 planning 着手** — C-04 案 B（Main + Margins Drawer、2 tab）。 [planning draft](20260608-p08-main-margins-drawer-planning-draft.md) / [slice-memo](design/20260608-p08-main-margins-drawer-slice-memo.md)。
- 2026-06-07: **P-04 planning 合意** — [planning draft](finished/20260607-p04-main-action-cluster-planning-draft.md)

### K-05（scheduler）— 残しうるストーリーと見送り理由

オーナー判断どおり **当面は採らない**。次のような話は成立しうるが、現行 product では代替で足りる、または別製品寄りの責務になりやすい。


| ストーリー                      | なぜ弱い / 代替                                                                                    |
| -------------------------- | -------------------------------------------------------------------------------------------- |
| 勤務時間だけ slideshow を回したい     | Interval + 手動 Start/Stop で足りる。常駐 scheduler は tray/サービス設計が要る                                  |
| 朝 9 時に気象図を取り直して apply      | C-01 は start 前 sync + slideshow interval。OS のログイン時起動は Harite 外                               |
| 夜は個人写真・昼は JMA preset に自動切替 | profile / srcdir の**時刻連動切替**は未実装だが、scheduler 全体より「preset 切替ルール」小 feature の方が筋がよい（それでも今は不要寄り） |
| 曜日ごとに別 source profile      | 運用ニーズはあるが、GUI 複雑化・テスト・スリープ復帰とセット。明示要望なし                                                      |


**結論:** 時刻駆動の**汎用 automation 基盤**（K-05）は Harite の core 価値（optimize / apply / slideshow + source）から外す。将来「時刻で profile だけ切替」程度のニーズが出たら、K-05 復活ではなく**限定スコープ**で再検討する。

## 完了条件（WS10 立ち上げ — **達成済み**）

- 後続機能 inventory の枠組みが説明可能になっている。
- 構想の受け皿として overview を置く理由が説明可能になっている。
- Workstream 1・3・4・5 と混線せずに次段へ送れる状態になっている。
- 少なくとも一次 inventory が overview 上で参照可能になっている。

※ 当初の「`1.0.0` gate の外に置く」完了条件は、**v1.0.0 リリースにより obsolete**。以降は上記 4 点 + 各 feature 完了記録の更新で十分。
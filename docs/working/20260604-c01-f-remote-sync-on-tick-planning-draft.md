# C-01-F — Remote live sync on slideshow tick（計画 draft）

最終更新: 2026-06-06  
ステータス: **据え置き**（2026-06-06 オーナー判断 — CODH 負荷懸念・gate F1–F3 未記入。impl しない）

## 位置づけ


| 文書                                                                                | 役割                                                        |
| --------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [feature-overview](20260518-2047-feature-overview.md) §C-01-F                     | inventory 入口（1 行）                                         |
| **本書**                                                                            | C-01 第 2 段の **計画正本** — remote を「ライブ壁紙 feed」として tick と結線する |
| [C-01 planning](finished/20260603-1400-c01-external-wallpaper-source-planning.md) | 第 1 段（cache-first staging + Start/Refresh sync）— **完了**   |
| [C-01-E 統合索引](finished/20260603-c01-e-merged-inventory.md)                        | NDL/CODH 実現性検証 — **完了**（本書の素材）                            |
| [harite-source-spec §12.4](../specs/source/harite-source-spec.md)                 | 現行正本（tick は network しない）— **改訂対象**                        |


**前提（完了済み）:** C-02 / C-05 / C-01 / C-01-E / C-04（Slideshow Drawer 等）。

**後続（完了済み）:** [C-01-E-KW](finished/20260605-c01-e-kw-codh-keyword-planning.md)（#413）— tick sync なしでも Refresh / Start 前 sync で運用。

**据え置き理由（2026-06-06）:** CODH への tick 毎リクエストは負荷・迷惑になりうる。gate §7 の F1–F3 が未記入のまま保留。再開時は overview §2 から着手候補へ再分類する。

**着手前:** [§7 着手 gate checklist](#7-着手-gate-checklist) の 3 項目をオーナーが pass するまで impl しない。

### 目次


| §                             | 内容                            |
| ----------------------------- | ----------------------------- |
| [1](#1-問題オーナー実機2026-06)       | 問題（期待 vs 現行）                  |
| [2](#2-目標)                    | 目標                            |
| [3](#3-provider-別-sync-方針)    | provider 別 sync 方針            |
| [4](#4-spec-改訂タッチポイント)        | spec 改訂タッチポイント                |
| [5](#5-実装フェーズ案)               | 実装フェーズ案                       |
| [6](#6-スコープ外)                 | スコープ外                         |
| **[7](#7-着手-gate-checklist)** | **着手 gate checklist（オーナー記入）** |
| [8](#8-関連-backlog本書とは別-id)    | 関連 backlog                    |


---

## 1. 問題（オーナー実機・2026-06）

### 1.1 期待と実装のズレ


| 期待（ライブ壁紙 / slideshow）           | 現行 C-01                            |
| ------------------------------- | ---------------------------------- |
| Interval ごとにソースを見に行く            | tick は **cache の 1 枚**だけを再 apply   |
| 新しい絵が来たら壁紙が変わる                  | Start/Refresh 時の 1 枚が **回し続け中は固定** |
| `min_interval: 600` ＝ 10 分周期の更新 | 600 は **tick 下限のみ**。sync とは未配線     |


現行の remote は **「1 枚入り virtual local-dir」** であり、C-05 slideshow（フォルダ内画像の cycle）に載せただけ。JMA / NDL / CODH すべて **Stop→Start や Refresh を繰り返さないと絵が変わらない**。

### 1.2 なぜこうなったか（要約）

C-01 第 1 段の決定（[planning §Open questions](finished/20260603-1400-c01-external-wallpaper-source-planning.md)）:

- cache は **最新 1 枚 staging**（#3b）
- **K-05 定期 auto-sync は対象外**
- tick で network しない（UI ブロック回避・tick 短時間化・slideshow コアの単純化）
- 後から **Start 直前 sync** のみ追加

NDL/CODH（C-01-E）は **同じ枠** に載ったが、ランダム源には **tick 毎 fetch** が本体。Interval 下限だけでは「ライブ感」は出ない。

**教訓:** 霞んでいた中心論点は cache の硬さではなく、**remote が slideshow tick と一体か否か**。

### 1.3 C-01-E 実験の価値（維持）

- NDL / CODH API 棚卸し・preset 5 種・`sources_remote.py` provider 実装
- Manage / Drawer 導線（C-04 後）
- 「取れる絵」と「回す体験」は **別問題** と分離できた

手戻りは **§12.4 の契約と tick 経路** が中心。inventory / preset JSON は活かす。

---

## 2. 目標（C-01-F）

**remote `slideshow` を「ライブ feed」として再定義する。**


| 方針                       | 内容                                                           |
| ------------------------ | ------------------------------------------------------------ |
| **provider 別 sync ポリシー** | 全 provider 共通の「tick は fetch しない」を **廃止**し、kind / preset で分岐  |
| **cache staging は維持可**   | 基本は **最新 1 枚上書き**のままでよい（ギャラリー蓄積は本波の必須ではない）                   |
| **Interval の意味**         | remote 実行中は **Interval ＝ sync + apply の周期**（少なくとも random 系）  |
| **K-05 とは別**             | OS 常駐 scheduler ではなく、**slideshow running 中の on-demand sync** |


---

## 3. Provider 別 sync ポリシー（draft）


| Provider / preset 型                      | tick 毎の sync                             | 備考                                                                                        |
| ---------------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------- |
| **JMA** `remote-jma-weather-map`         | **推奨: Interval 境界で sync**                | list.json で filename 変化時のみ GET してよい（同一なら skip）。公式更新周期と `min_interval 600` を **意味ある配線**にする |
| **CODH random** `*-random`               | **毎 tick sync**                          | `total` → random `start` → 新 canvas（現 `_codh_pick_thumbnail_url`）                         |
| **CODH 固定 KW** `codh-edo-spots-sakura` 等 | **毎 tick sync または start+周期**             | 固定検索でも **別 canvas を取る**なら random `start` 相当が必要。要 spec 細部                                  |
| **NDL** `ndl-random-*`（facet 6 preset）     | **採用後に検討** — tick sync で価値が出やすい | `ndl-random` 廃止。同梱は [inventory §3.4](finished/20260603-c01-e-ndl-tsugidigi-inventory.md) の 6 facet preset |
| **local-dir**                            | **変更なし**                                 | 従来どおりフォルダ内 cycle のみ                                                                       |


**実行中の Refresh（Manage）** — 現行どおり実行中 run との競合に注意（§12.3）。

---

## 4. 仕様・実装タッチポイント（案）

### 4.1 正本の改訂


| 文書                                                                 | 変更                                                     |
| ------------------------------------------------------------------ | ------------------------------------------------------ |
| [source-spec §12.4](../specs/source/harite-source-spec.md)         | `slideshow tick` 行を **provider 別**に書き換え                |
| [source-spec §15.5](../specs/source/harite-source-spec.md)         | JMA: tick/interval sync 契約                             |
| [source-spec §15.6–15.7](../specs/source/harite-source-spec.md)    | NDL/CODH tick 方針                                       |
| [slideshow-spec §6.6](../specs/slideshow/harite-slideshow-spec.md) | tick 前 remote sync の順序（sync → collect → cycle → apply） |


### 4.2 コード（想定）


| 層                               | 内容                                                                    |
| ------------------------------- | --------------------------------------------------------------------- |
| `main_window.on_slideshow_tick` | remote side について **tick 前に** `sync_remote_source`（policy 経由）          |
| `sources_remote`                | provider メタデータ: `sync_on_slideshow_tick: always | interval | never` 等 |
| JMA                             | オプション: 前回 filename と比較して skip                                         |
| 失敗時                             | tick 失敗 → stop / pause / 前回画像維持 — **planning で確定**                    |


### 4.3 cache 手戻りの見込み

- **ディレクトリ layout**（`{cache_root}/{uuid}/latest.`*）は **維持可能**
- 変わるのは **「いつ `_write_latest_cache` するか」**（Start だけ → tick でも）
- 複数世代 cache は **本波スコープ外**（将来オプション）

---

## 5. フェーズ分割（提案）


| 段     | 内容                                                  | 停止点         |
| ----- | --------------------------------------------------- | ----------- |
| **0** | 本 planning 合意                                       | 本書          |
| **1** | spec PR — §12.4 / §6.6 / §15 差分                     | spec merge  |
| **2** | tests — tick 前 sync モック、JMA skip、CODH random 毎 tick | tests merge |
| **3** | impl — CODH random tick sync（体感最大）                  | PR          |
| **4** | impl — JMA interval sync + filename 比較              | PR          |
| **5** | 軽量 audit + 実機                                       | クローズ        |


**NDL** は段 3–4 に含めない（オーナー判断まで保留）。

---

## 6. スコープ外（本波）


| 項目                    | 理由                                         |
| --------------------- | ------------------------------------------ |
| C-01-E-KW（ユーザー KW UI） | **C-01-F 後** — KW だけ足しても tick で取りに行かないと無意味 |
| cache 複数枚ギャラリー        | random は API 側で毎回別 ID で足りる                 |
| K-05 scheduler        | 常駐 poll は引き続き非採択                           |
| CLI remote slideshow  | C-01 継続方針どおり GUI 主                         |


---

## 7. 着手 gate checklist

impl 着手前にオーナーが下表に **pass** / **revise** / **reject** を記入する（[C-04 slice-memo](design/20260604-c04-slideshow-margins-surface-slice-memo.md) と同形式）。


| #   | 論点                                                   | 現状 / 提案                                                                     | オーナー |
| --- | ---------------------------------------------------- | --------------------------------------------------------------------------- | ---- |
| F1  | §3 provider 表（CODH random / JMA interval / NDL 据え置き） | 表どおりで着手してよいか                                                                |      |
| F2  | tick 中 sync **失敗時**の挙動                               | **案 A:** slideshow を stop + footer エラー。**案 B:** 前回 `latest.`* を維持して tick 継続 |      |
| F3  | JMA **同一 filename skip**                             | **案 A:** skip（無駄な再 decode 回避）。**案 B:** 毎 tick 再 decode（実装単純）                |      |


**gate 通過条件:** F1–F3 がすべて **pass**（revise は本文へ反映後に再記入）。

---

## 8. 関連 backlog（本書とは別 ID）


| ID                    | 関係            |
| --------------------- | ------------- |
| C-01-E-KW             | **後続**（本書完了後） |
| P-04（Preview idle 整理） | 独立。並行可        |
| P-03                  | 独立。着手順序外      |


---

## 変更履歴


| 日付         | 内容                                                 |
| ---------- | -------------------------------------------------- |
| 2026-06-04 | 初版 — C-01 第 2 段 draft。オーナー実機フィードバックと §12.4 振り返りを反映 |
| 2026-06-04 | §7 を「着手 gate checklist」表形式に拡張。目次と着手前リンクを追加         |



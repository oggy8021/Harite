# C-01-F — Remote live sync on slideshow tick（計画 draft）

最終更新: 2026-06-07  
ステータス: **planning 合意**（§3 CODH index+cursor、§7 gate 記入済み。**impl は gate 通過後**）

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

**据え置き経緯（2026-06-06）:** 初版は CODH への tick 毎 **search probe**（`total` + random `start`）が負荷懸念で gate 未記入のまま保留。

**2026-06-07 合意:** CODH は **軽量 index cache + cursor**（§3.1）で層 B（slideshow Mode）を復活させ、tick では **画像 GET のみ**。JMA は interval 境界 sync + filename skip（§3 表）。

**着手前:** [§7 着手 gate checklist](#7-着手-gate-checklist) の **F1–F4** がすべて **pass**（revise 反映済み）してから impl する。

### 目次


| §                             | 内容                            |
| ----------------------------- | ----------------------------- |
| [1](#1-問題オーナー実機2026-06)       | 問題（期待 vs 現行）                  |
| [2](#2-目標)                    | 目標                            |
| [3](#3-provider-別-sync-方針)    | provider 別 sync 方針            |
| [3.1](#31-codh--index--cursorb-案確定) | CODH — index + cursor（確定）   |
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

## 3. Provider 別 sync ポリシー（合意）


| Provider / preset 型 | tick 毎の動作 | 備考 |
| --- | --- | --- |
| **JMA** `remote-jma-weather-map` | **Interval 境界で sync** | `list.json` → filename 変化時のみ画像 GET（同一なら **skip** — F3 案 A）。`min_interval 600` と公式更新周期を配線 |
| **CODH**（random / keyword 含む全 preset） | **index + cursor で 1 件選び → 画像 GET → `latest.*`** | 詳細は [§3.1](#31-codh--index--cursorb-案確定）。tick 毎の search probe は **しない** |
| **NDL** `ndl-random-*` | **本波は据え置き** | tick sync で価値は出やすいがオーナー判断まで保留。[inventory §3.4](finished/20260603-c01-e-ndl-tsugidigi-inventory.md) 参照 |
| **local-dir** | **変更なし** | 従来どおりフォルダ内 cycle のみ |

**実行中の Refresh（Manage）** — 現行どおり実行中 run との競合に注意（§12.3）。CODH は Refresh で **index 再構築**（§3.1）。

---

### 3.1 CODH — index + cursor（B 案・確定）

現行 §15.7.3（毎 sync: `total` probe → random `start` → 1 件）は **Refresh 専用のリスト構築**に移し、slideshow **Mode（sequential / random）を remote 側でも有効**にする。v1 で `results[]` 全文を実キャッシュした案は **重い**ため採用しない。

#### UX 前提

- コーパス ~2000 件 × `min_interval` 600s では **1 日（~144 tick）では見切れない**（全件 sequential で **~14 日**）。
- **cursor**（リスト上の巡回位置）は **アプリ再起動をまたいで継続**する（§3.1.3）。

#### 3.1.1 候補リスト（`codh-index.json`）

| 項目 | 契約 |
| --- | --- |
| **構築タイミング** | **Manage Refresh**、初回（index 無し）、**query 変更後**（keyword 等）。起動時は **disk から読むだけ**（全件ページングしない） |
| **構築手順** | `probe`（`start=0&limit=1` → `total`）→ `start` を増やしながら `limit=L`（例 50–100）で **ページング** → 各 `results[].canvasThumbnail` を `/200,/` → `/max/` に正規化 |
| **保存先** | `{cache_root}/{source_id}/codh-index.json` |
| **中身（最小）** | `version`, `query_key`（indexer + 検索条件 + keyword の fingerprint）, `total`, `built_at`, `entries[]`（各 `{image_url}`） |
| **サイズ感** | 全件でも URL のみなら **~1 MB 未満**（[inventory](finished/20260603-c01-e-codh-icp-inventory.md) の全件 JSON ≈3MB より軽い） |
| **書き込み** | `codh-index.json.tmp` → rename（途中失敗で壊れた index を読まない） |

`limit` 省略は **禁止**（inventory 既知 — UI フリーズ）。

#### 3.1.2 tick 手順（slideshow running 中）

1. `codh-index.json` を読み、**cursor**（§3.1.3）と整合する `query_key` を確認。
2. Mode に従い **次の `image_url`** を選ぶ（sequential: `index++`、random: リストから乱択・直前 URL 回避は cursor で）。
3. `image_url` を GET → §12.3 の共通ヘルパで **`latest.*` 上書き**。
4. **cursor を更新**し `codh-cycle.json` へ保存（tick 後。クラッシュ耐性）。

tick 毎の Canvas Indexer **search API は呼ばない**（画像ホストへの GET のみ）。

#### 3.1.3 巡回位置（`codh-cycle.json`）

API ページングの `start=` ではなく、**候補リスト上の cursor**。

| 項目 | 契約 |
| --- | --- |
| **保存先** | `{cache_root}/{source_id}/codh-cycle.json`（index と **別ファイル** — Refresh で index 全再構築しても cursor を独立管理） |
| **中身（最小）** | `query_key`, `mode`, `index`（sequential）, `previous_image_url`（random 用）, `updated_at` |
| **run 中** | メモリの `SlideshowCycleState` と同期 |
| **再起動後** | disk から cursor を復元 → 続きから（600s × 2000 件の sequential UX） |
| **query_key 不一致** | cursor を **0 / 空にリセット**（keyword 変更等） |
| **index 再構築で `total` 変化** | `index %= new_total` またはリセット — **F4 で確定** |

#### 3.1.4 現行 §12.5 との関係

| 層 | C-01-F 後 |
| --- | --- |
| **A. Sync 時候補選択** | Refresh 時に **index 一括構築** + tick 時に **1 件画像化** |
| **B. Slideshow Mode** | CODH side でも **sequential / random が有効**（仮想 `local-dir` 相当。画像バイナリは tick で 1 枚ずつ） |

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


| 層 | 内容 |
| --- | --- |
| `main_window.on_slideshow_tick` | remote side について policy 経由で tick 前処理（CODH: cursor 進行 + 画像 GET、JMA: interval sync） |
| `sources_remote` | provider メタデータ: `sync_on_slideshow_tick`（`never` / `interval` / `codh-index-cycle` 等） |
| CODH | `build_codh_index`（Refresh）、`advance_codh_cursor` + `fetch_codh_tick_image`（tick）、`codh-index.json` / `codh-cycle.json` IO |
| JMA | 前回 filename と比較して skip（F3 案 A） |
| 失敗時 | tick 画像 GET 失敗 → **前回 `latest.*` 維持して tick 継続**（F2 案 B）。リトライ上限は impl で調整可 |


### 4.3 cache 手戻りの見込み

- **ディレクトリ layout** — `{cache_root}/{uuid}/latest.*` は **維持**
- **追加** — `codh-index.json`（候補 URL リスト）、`codh-cycle.json`（cursor）
- 変わるのは **「いつ `_write_latest_cache` するか」**（Start だけ → **tick でも**）
- 複数世代 **画像** cache は **本波スコープ外**（index は URL メタのみ）

---

## 5. フェーズ分割（提案）


| 段     | 内容                                                  | 停止点         |
| ----- | --------------------------------------------------- | ----------- |
| **0** | 本 planning 合意（§3.1 index+cursor） | 本書 |
| **1** | spec PR — §12.4 / §12.5 / §15.7 / §6.6 差分 | spec merge |
| **2** | tests — CODH index ページング・cursor 永続化・tick 画像 GET モック、JMA filename skip | tests merge |
| **3** | impl — CODH index+cursor + tick 画像取得 | PR |
| **4** | impl — JMA interval sync + filename 比較 | PR |
| **5** | 軽量 audit + 実機 | クローズ |


**NDL** は段 3–4 に含めない（オーナー判断まで保留）。

---

## 6. スコープ外（本波）


| 項目                    | 理由                                         |
| --------------------- | ------------------------------------------ |
| C-01-E-KW（ユーザー KW UI） | **C-01-F 後** — KW だけ足しても tick で取りに行かないと無意味 |
| cache 複数枚ギャラリー（画像バイナリ） | CODH は **URL index** のみ。画像は引き続き `latest.*` 1 枚上書き |
| K-05 scheduler        | 常駐 poll は引き続き非採択                           |
| CLI remote slideshow  | C-01 継続方針どおり GUI 主                         |


---

## 7. 着手 gate checklist

impl 着手前にオーナーが下表に **pass** / **revise** / **reject** を記入する（[C-04 slice-memo](design/20260604-c04-slideshow-margins-surface-slice-memo.md) と同形式）。


| # | 論点 | 現状 / 提案 | オーナー |
| --- | --- | --- | --- |
| F1 | §3 provider 表（JMA interval / CODH §3.1 / NDL 据え置き） | JMA: interval 境界 sync + filename skip。CODH: **index + cursor**（tick は画像 GET のみ）。NDL: 本波対象外 | **pass** — JMA 同意。CODH は §3.1（B 案） |
| F2 | tick 中 **画像 GET 失敗時** | **案 A:** stop + エラー。**案 B:** 前回 `latest.*` 維持して tick 継続 | **pass** — 案 B（リトライは impl 詳細） |
| F3 | JMA **同一 filename skip** | **案 A:** skip。**案 B:** 毎 tick 再 decode | **pass** — 案 A skip |
| F4 | CODH **cursor** 永続化・wrap | **案 A:** `codh-cycle.json`、tick 後保存、再起動で復元。sequential 末尾は **先頭 wrap**。**案 B:** メモリのみ（再起動で先頭） | **pass** — 案 A（§3.1.3） |


**gate 通過条件:** F1–F4 がすべて **pass**（revise は本文へ反映後に再記入）。**2026-06-07: 通過** — impl 着手可。

---

## 8. 関連 backlog（本書とは別 ID）


| ID                    | 関係            |
| --------------------- | ------------- |
| C-01-E-KW             | **後続**（本書完了後） |
| P-04（Preview idle 整理） | 独立。並行可        |
| P-03                  | **完了**（#420）。並行可 |


---

## 変更履歴


| 日付         | 内容                                                 |
| ---------- | -------------------------------------------------- |
| 2026-06-04 | 初版 — C-01 第 2 段 draft。オーナー実機フィードバックと §12.4 振り返りを反映 |
| 2026-06-04 | §7 を「着手 gate checklist」表形式に拡張。目次と着手前リンクを追加 |
| 2026-06-07 | §3.1 CODH **index + cursor**（B 案）確定。§7 F1–F4 pass。ステータスを planning 合意へ |



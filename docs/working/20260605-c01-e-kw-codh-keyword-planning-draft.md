# C-01-E-KW — CODH キーワード検索のユーザー指定（計画 draft）

最終更新: 2026-06-05  
ステータス: **planning draft**（spec / GUI 合意前。impl は本書合意後）

## 位置づけ


| 文書                                                                      | 役割                                                              |
| ----------------------------------------------------------------------- | --------------------------------------------------------------- |
| [feature-overview §C-01-E-KW](20260518-2047-feature-overview.md)        | inventory 入口（1 行）                                               |
| **本書**                                                                  | CODH 江戸観光 **キーワード**のユーザー指定 — 計画正本                               |
| [CODH inventory](finished/20260603-c01-e-codh-icp-inventory.md)         | API・メタデータ・`where_metadata_`* 契約                                 |
| [C-01-F planning](20260604-c01-f-remote-sync-on-tick-planning-draft.md) | **関連** — tick sync で KW の product 価値が出る（本書と並行可だが tick なしでは体感薄い） |
| [C-04 surface](20260604-c04-gui-surface-planning-draft.md) §4.3         | KW 入力は **Manage dialog 内**（Drawer 経由）— slice S6 **pass**        |
| [harite-source-spec §15.7](../specs/source/harite-source-spec.md)       | provider 正本（改訂対象）                                               |
| [harite-gui-spec §4.2](../specs/gui/harite-gui-spec.md)                 | Manage dialog 契約（改訂対象）                                          |


**前提（完了済み）:** C-01-E provider + `codh-edo-spots-sakura`（コード固定 `桜`）、C-04 Drawer / Manage 導線。

**並行:** C-01-F は **未 impl**（planning draft）。KW UI だけ先に載せても **Refresh / Start 直前 sync** では従来どおり。tick 毎の新絵は C-01-F 後。

### 目次


| §                         | 内容                 |
| ------------------------- | ------------------ |
| [1](#1-問題)                | 問題                 |
| [2](#2-目標)                | 目標                 |
| [3](#3-notes-契約案)         | `notes` 機械行契約      |
| [4](#4-gui-案)             | GUI（Manage dialog） |
| [5](#5-sync-挙動)           | sync 挙動            |
| [6](#6-スコープ)              | スコープ / スコープ外       |
| [7](#7-着手-gate-checklist) | 着手 gate checklist  |
| [8](#8-実装フェーズ案)           | 実装フェーズ案            |


---

## 1. 問題

- `codh-edo-spots-sakura` の **「桜」は `_CODH_PRESET_SEARCH` にハードコード** — ユーザーが梅・花火・雪などに変えられない。
- 同梱 preset を増やすだけでも代替は可能だが、**104 ファセット**を preset 列挙するのは非現実的。
- C-04 後、KW 入力の置き場は **Manage sources and profiles…** 内に合意済み（専用 tab は作らない）。

---

## 2. 目標

**CODH 江戸観光・江戸買物の両 indexer で、ユーザーが 1 語指定して slideshow remote source として使えるようにする。**


| 方針 | 内容（オーナー §7 確定） |
| --- | --- |
| **indexer** | **`edo-spots` + `edo-shops`** — 同一のユーザー入力 KW を両方で使う（API の metadata label は indexer 別にマップ — §5） |
| **preset** | **案 B:** 新 `codh-edo-spots-keyword`（＋買物側は `codh-edo-shops-keyword` 等）。`codh-edo-spots-sakura` は **同梱廃止** |
| **検索 API** | `where_metadata_label` + `where_metadata_value`（観光=`キーワード`、買物=`備考` — [inventory §4](finished/20260603-c01-e-codh-icp-inventory.md)） |
| **保存** | `harite-settings.json` の `codh_keyword`（観光・買物共通）。`notes` には書かない（§3） |
| **UI** | Manage dialog — 上記 keyword 系 preset の source 選択時のみ入力行を表示 |
| **多様性** | **疑似ランダム**（`total` → `start`）— `codh-edo-spots-random` と同型 |


---

## 3. `codh_keyword` 契約（確定 — 2026-06 impl 改訂）

**保存先:** `harite-settings.json` トップレベル `codh_keyword`（**観光・買物で共通** — K1）。

| 項目 | 契約 |
| --- | --- |
| キー | `codh_keyword`（`sources_remote.CODH_KEYWORD_SETTINGS_KEY`） |
| 値 | UTF-8 文字列。前後空白は strip。**空は無効**（sync 時は default `桜`） |
| 長さ上限 | **16 文字**（`len()` 基準） |
| preset JSON / source `notes` | **書かない**（出典・`harite-preset` / `harite-min-interval` のみ） |
| 初期値 | **`桜`**（settings 未設定時） |
| 廃止 | `codh-edo-spots-sakura`、notes 内 `harite-codh-keyword:`（migrate で settings へ移行後 strip） |

---

## 4. GUI（確定 — §7 K6）

**場所:** `source_registry_dialog`（Qt 先行、GTK parity）  
**slice:** [20260605-c01-e-kw-manage-keyword-slice.html](design/20260605-c01-e-kw-manage-keyword-slice.html) + [memo](design/20260605-c01-e-kw-manage-keyword-slice-memo.md)

### 4.1 暫定配置（現フェーズ）

| 項目 | 合意 |
| --- | --- |
| 位置 | **Refresh / Delete 行の直上**（source リスト直下）。空きが少ないため **暫定** |
| ラベル | **`keyword(CODH)`** — CODH 側もメタデータ名は「キーワード」だが UI ラベルはこれで統一 |
| 控件 | `QLineEdit`、**初期値 `桜`**、`maxLength=16` |
| 表示 | **常設**（選択 source に関わらず行は表示。非対応 source 時は **disabled** 推奨 — spec で固定） |
| 保存 | **Refresh 前** および **Close 時** — `harite-settings.json` の `codh_keyword` を read/write（source 共通） |

### 4.2 理想配置（P-05 — 本波では触らない）

Sources を **ALL なし**で二面板に分ける（[P-05](20260518-2047-feature-overview.md) ストック）:

| 面板 | 操作 |
| --- | --- |
| **local** | Delete、name、path、Browse、Add local |
| **preset** | Refresh、**keyword(CODH)**（暫定行がここへ移設） |

**0 件ヒット時:** Refresh / Start sync は `ValueError` → footer / QMessageBox（§7 K4）。

---

## 5. sync 挙動

```
_codh_sync (keyword preset)
  1. settings から codh_keyword を読む（default 桜）
  2. preset の indexer に応じて label を選択:
       edo-spots → where_metadata_label=キーワード
       edo-shops → where_metadata_label=備考
     where_metadata_value={kw}
  3. total 取得 → random start（codh-edo-*-random 同型）→ limit=1
  4. canvasThumbnail → /max/ → latest.*
```


| 論点 | 確定 |
| --- | --- |
| indexer 別 label | 同一ユーザー KW、観光=`キーワード` / 買物=`備考` |
| pick | **疑似ランダム**（§7 K3） |
| 既存 `codh-edo-spots-sakura` | 廃止（§7 K2） |
| C-01-F 後 | tick sync で同一 KW の別 canvas が回る |


---

## 6. スコープ / スコープ外


| 含む（v1） | 含まない |
| --- | --- |
| `edo-spots` + `edo-shops`（同一 KW UI、label は indexer 別） | 職種・商人名など **別軸** の検索 UI |
| Manage dialog 1 フィールド | Slideshow tab 正面への KW 露出 |
| notes 機械行             | catalog schema version 変更 |
| urlencode + 長さ検証      | ファセット一覧 UI / オートコンプリート    |
| 疑似ランダム（keyword 時）     | `where=` 部分一致フォールバック      |


---

## 7. 着手 gate checklist


| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| K1 | v1 indexer | 観光 `edo-spots` のみ（draft 初版） | **revise** — `edo-shops` も同一 KW を用いる |
| K2 | preset | 案 A: `sakura` 維持 + 上書き / 案 B: `codh-edo-spots-keyword` 新設 | **pass 案 B** — `sakura` 廃止。入力の初期値 `桜` でサンプル役を移す |
| K3 | keyword 時の pick | 疑似ランダム vs 先頭固定 | **pass** — 現行 random 系と同じ |
| K4 | 0 件時 | エラーのみ vs フォールバック | **pass** — エラー表示のみ |
| K5 | 長さ上限 | 32 文字 | **revise** — **16 文字**（マルチバイトも 1 文字） |
| K6 | widget slice | 暫定: Refresh 直上・`keyword(CODH)`・初期値 `桜`・常設 | **pass** — [slice-memo](design/20260605-c01-e-kw-manage-keyword-slice-memo.md) |


**gate 通過条件:** K1–K6 がすべて **pass** — **達成**（2026-06-05）。次: spec 改訂 PR。

### 7.1 K6 とは何か（補足）

C-04 の **S6**（「KW は Manage 内でよい」）は **大枠の置き場**だけの合意。**K6** はその **中身 1 行**を impl する前に決める工程である。

| K6 で決めること | K6 で決めないこと |
| --- | --- |
| Manage dialog の **どこに** keyword 行を足すか（source リスト下 / Refresh 上 等） | Slideshow tab・Drawer の再配置（C-04 済み） |
| ラベル文案（例: `Keyword:` / `キーワード`） | CODH API の検索ロジック（計画書 §5） |
| placeholder・初期値 `桜` の見せ方 | キーワードの最大長（K5 で確定） |
| 非対象 source 選択時は **行ごと非表示** でよいか | GTK/Qt の parity 実装詳細 |

**成果物の形（§9 工程）:** [design/](design/) に **widget slice** 1 組 — 例: `20260605-c01-e-kw-manage-keyword-slice.html` + 短い memo（P-01 / C-04 slice と同型）。ブラウザで「現行 Manage 面板 + keyword 1 行案」を見比べ、memo に pass/revise を 1 行書く。**HTML が無くても** 実機スクショに赤枠注釈 + memo でも可。

**K6 pass 後:** gui-spec §4.2 / source-spec §15.7 の **spec 改訂 PR** に進む（.cursorrules §9）。

---

## 8. 実装フェーズ案


| 段     | 内容                                                       | 成果物              |
| ----- | -------------------------------------------------------- | ---------------- |
| **0** | 本書 + §7 gate + widget slice 合意                           | working / design |
| **1** | source-spec §15.7 + gui-spec §4.2 改訂 PR                  | specs            |
| **2** | core — `harite-codh-keyword` parse、`_codh_sync` 分岐、tests | PR               |
| **3** | GUI — Manage dialog keyword 行（Qt）、tests                  | PR               |
| **4** | GTK parity（必要最小）                                         | PR               |
| **5** | 実機 + 軽量 audit                                            | 完了               |


C-01-F tick sync は **別トラック**（本書完了と並行または後追い可）。

---

## 変更履歴


| 日付         | 内容                                                        |
| ---------- | --------------------------------------------------------- |
| 2026-06-05 | 初版 — C-01-E-KW 計画 draft。notes 機械行・Manage UI・random pick 案 |
| 2026-06-05 | §7 — オーナー K1–K5 確定。K6 補足 §7.1 追加 |
| 2026-06-05 | §4 / §7 K6 — 暫定配置合意。widget slice + memo。gate 通過 |



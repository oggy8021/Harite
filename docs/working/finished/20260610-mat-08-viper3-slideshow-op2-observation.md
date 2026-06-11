# MAT-08 観測 — viper3 slideshow-op2.jsonl（#462 以降）

実施日: 2026-06-10（ログ収集） / 記録: 2026-05-31  
親: [maturation §MAT-08](../online-issues/maturation-20260609-qt-common.md#mat-08--preset-系-slideshow-の動作ログcodh--ndl-観測用)  
前提: [op1 観測](20260609-mat-08-viper3-slideshow-op-observation.md)、MAT-02b #462（`SLIDESHOW_TICK` / `SLIDESHOW_APPLY`）  
環境: **viper3**（Linux、`/home/katsu`）、`harite-qt`、Post #462 main  
ログ: オーナー提供 `slideshow-op2.jsonl`（114 行、JST `+09:00`）

## 観測条件

| 項目 | 値 |
| --- | --- |
| 有効化 | `HARITE_SLIDESHOW_OP_LOG` → `slideshow-op2.jsonl`（リポジトリ外想定） |
| 期間 | `2026-06-10T00:05:57` 〜 `2026-06-10T09:25:23`（約 9h20m） |
| 記録数 | 114 JSONL 行 |
| 失敗（`ok: false`） | **0**（HTTP 層） |

## 結論（オーナー確定 + コード照合）

| 区分 | 実機 / JSONL | 判定 |
| --- | --- | --- |
| **CODH** | 00:41 / 00:51 tick — `CODH_TICK` + GET + `SLIDESHOW_APPLY` OK | **安定** |
| **JMA** | 03:06 / 05:06 / 07:06 — `JMA_TICK` OK。`latest.png` mtime + `jma-cycle.json` `updated_at` = 7:06 確認済 | **安定**（apply 行は tick ログに無いが、次回観測で確認） |
| **NDL** | Start sync は OK。tick は **同一 `latest.jpg` の再 apply のみ**（`NDL_META_URL` 等なし） | **設計ギャップ** → `ndl_slideshow_tick` で改修（本 PR） |
| **NDL 00:53 セッション** | Start apply 後、次ログは 01:06 JMA Start まで tick 無し | **観測継続**（安定化フェーズ。本改修のブロッカーではない） |

→ op2 は **MAT-02b の tick/apply ログが効いている**一方、NDL は **product 要件（tick 毎 randomwithfacet）未実装**が主因。CODH は op1 の「GET OK だが未反映」から改善傾向。

## セッション別メモ

### 1. NDL イラスト + ランドマーク（00:05–00:26）

- Start: L/R とも `NDL_META_URL` → IIIF GET → CACHE 成功。
- tick 00:16 / 00:26: `SLIDESHOW_TICK` → `SLIDESHOW_APPLY` OK。`selected_*` は **Start 時と同一 path**（`latest.jpg` 再選択のみ）。
- **期待:** tick 毎 `randomwithfacet`。**実装:** 未配線（source-spec §15.3.3 L681 旧文）。

### 2. CODH 江戸観光 dual（00:31–00:51）

- Start + tick 00:41 / 00:51: `CODH_TICK` + `CODH_IMAGE_GET` + apply まで一連で記録。
- op1 の 20:37「GET OK だが壁紙未更新」と比べ、**apply 層までログで追える**状態。

### 3. NDL 地図 + 着色挿絵（00:52–00:53）— 00:53 打ち切り

- Start 00:53:07 apply OK。
- **以降 tick ログなし**（次は 01:06 JMA Start）。間隔 10 分なら 01:03 頃の tick が期待される。
- オーナー判断: **安定化観測で継続追跡**（timer 停止・手動 Stop 等の可能性。NDL tick 未実装とは独立）。

### 4. JMA アジア + 日本付近（01:06–07:06）

- interval **7200s**（2h）。03:06 / 05:06 / 07:06 に `JMA_TICK` ×2（L/R）。
- オーナー: `latest.png` mtime と `jma-cycle.json` `updated_at` が 7:06 と一致 → **tick sync 成功**。
- op2 には 03:06 以降の `SLIDESHOW_APPLY` 行が無い → **次観測:** filename 未変化時は optimize/apply skip か、ログ欠落かを切り分け。

### 5. NDL 屋外 + 着色挿絵（08:42–09:25）

- Start 08:42 / 08:45（再 Start）後、tick 08:55 / 09:05 / 09:15 / 09:25 で apply OK。
- いずれも **同一 `latest.jpg` path** — NDL tick 改修前の再現。

## JSONL サマリ

| step | 回数 | 補足 |
| --- | --- | --- |
| `REMOTE_SYNC_BEGIN` | 10 セッション | すべて `ok: true` で END |
| `CODH_TICK` | 4 | L/R 各 2（00:41, 00:51） |
| `JMA_TICK` | 6 | 3 tick × L/R |
| `NDL_*` (META/IIIF/CACHE) | Start のみ | **tick では 0** |
| `SLIDESHOW_TICK` | 14+ | phase=tick |
| `SLIDESHOW_APPLY` | 14+ | phase=start/tick |

## op log 強化（outcome フィールド）

provider 共通で tick / cache 要約行に次を付与（op2 以前のログには無い）:

| フィールド | 意味 |
| --- | --- |
| `image_fetched` | network から画像 bytes を取得できたか |
| `cache_written` | `latest.*` を disk に書いたか |
| `had_previous` | 書込前に `latest.*` が存在したか |
| `overwritten` | 既存 `latest.*` を置換したか |
| `content_changed` | 前回 bytes と異なるか |
| `skip_reason` | 取得/書込スキップ理由（例: JMA `filename_unchanged`） |

## 本改修との対応

| 項目 | 対応 |
| --- | --- |
| NDL tick で `randomwithfacet` | `ndl_slideshow_tick` + `NDL_TICK` op log |
| 取得/上書きの可視化 | `NDL_CACHE_WRITE` / `JMA_TICK` / `CODH_TICK` 等に outcome フィールド |
| source-spec §15.3.4 | tick sync 契約を正本化 |
| slideshow-spec §6.2.1 | NDL 行を `ndl_slideshow_tick` に更新 |
| 00:53 無 tick | 観測継続（本 PR スコープ外） |
| JMA tick 後 apply 欠落 | 次回 op3 で `SLIDESHOW_APPLY` の有無を確認 |

## 次の観測（op3 想定）

1. 本 PR マージ後、NDL dual で 10 分間隔 → tick 毎 `NDL_TICK` + `NDL_META_URL` が出ること。
2. `selected_*` path は固定でも **mtime / bytes** が tick 毎変わること（実機 + JSONL）。
3. JMA 2h interval で filename 変化 tick の `SLIDESHOW_APPLY` 有無。
4. 00:53 型の「Start 後無 tick」再発時は `SLIDESHOW_TICK` の有無で timer 層を切り分け。

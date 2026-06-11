# MAT-08 観測 — viper3 slideshow-op3.jsonl（#464 以降）

実施日: 2026-06-10（ログ収集） / 記録: 2026-05-31  
親: [maturation §MAT-08](../online-issues/maturation-20260609-qt-common.md#mat-08--preset-系-slideshow-の動作ログcodh--ndl-観測用)  
前提: [op2 観測](20260610-mat-08-viper3-slideshow-op2-observation.md)、#464（`ndl_slideshow_tick` + outcome op log）、#465（Profile `— none —` → L/R clear）  
環境: **viper3**（Linux、`/home/katsu`）、`harite-qt`、Post #464 main（観測中 #465 マージ）  
ログ: オーナー提供 `slideshow-op3.jsonl`（110 行、JST `+09:00`）

## 観測条件

| 項目 | 値 |
| --- | --- |
| 有効化 | `HARITE_SLIDESHOW_OP_LOG` → `slideshow-op3.jsonl` |
| 期間 | `2026-06-10T10:22:48` 〜 `2026-06-10T11:36:49`（約 1h14m） |
| 記録数 | 110 JSONL 行 |
| 失敗（`ok: false`） | **3**（いずれも NDL IIIF 404/400、再試行で回復） |

## 結論（オーナー確定）

**勝ち筋が取れた。** #464 の NDL tick 改修と outcome op log が、観測で意図どおり機能している。

| 区分 | 実機 / JSONL | 判定 |
| --- | --- | --- |
| **JMA** | Start + 10 分 tick。`filename_unchanged` で GET skip、**apply は継続** | **安定・説明可能** |
| **NDL** | tick 毎 `NDL_META_URL` → IIIF → `NDL_TICK`（`content_changed=true`）→ `SLIDESHOW_APPLY` | **#464 改修 成功** |
| **NDL IIIF 404** | 11:22 L / 11:36 L で attempt 1–2 失敗 → 3/2 で成功 | **再試行契約どおり** |
| **CODH** | 本ログにセッション無し | op2 までの安定を継承（本回は未再検証） |

→ op1/op2 の「NDL tick で新規取得しない」「JMA tick 後 apply が見えない」は **op3 で解消**。残る MAT-02b 論点は **長時間運用・観測汚染防止（#465）** と **apply 失敗時 timer 方針**。

## セッション別

### 1. JMA dual（アジア + 日本付近）— 10:22–10:32

- **Start:** `JMA_CACHE_WRITE` — L は `content_changed=false`（同一 bytes 上書き）、R は `content_changed=true`。
- **tick 10:32:** `JMA_TICK` ×2 — `skip_reason=filename_unchanged`、`image_fetched=false`、`cache_written=false`。**op2 以降の outcome フィールドが期待どおり。**
- **apply:** `SLIDESHOW_APPLY` phase=tick が直後に記録 — **JMA 短 interval でも tick→apply 一連がログで追える**（op2 の JMA apply 欠落懸念を解消）。

### 2. NDL 屋内 + 屋外 — 10:42–11:22

- **Start 10:42:** L/R sync + outcome（`content_changed=true`）。
- **tick 10:52 / 11:02 / 11:12 / 11:22:** 各 tick で L/R 独立に `NDL_META_URL` → `NDL_TICK`（`image_fetched=true`, `overwritten=true`, `content_changed=true`）→ `SLIDESHOW_APPLY`。
- **11:22 L:** IIIF 404 ×2 → attempt 3 で GET 成功。tick 全体は `NDL_TICK ok=true`。**失敗と回復がログで切り分け可能。**
- op2 との差: tick 毎 **bytes が変化**（例: L 3003199 → 920309 → 50308 → …）。同一 path 再 apply 問題は解消。

### 3. NDL イラスト + ランドマーク — 11:26–11:36

- **Start 11:26** + **tick 11:36**（10 分間隔どおり）。
- L: IIIF 404 attempt 1 → attempt 2 成功。R: 一発成功。
- op1 で問題だった「イラスト + ランドマーク dual」構成でも **tick 発火・取得・apply が一連で記録**。

## JSONL サマリ

| step | 回数 | 補足 |
| --- | --- | --- |
| `JMA_TICK` | 2 | いずれも `filename_unchanged` |
| `JMA_CACHE_WRITE` | 2 | Start のみ。outcome 付き |
| `NDL_TICK` | 10 | L/R 各 5。すべて `image_fetched=true` |
| `NDL_IIIF_GET` `ok:false` | 3 | すべて後続 attempt で回復 |
| `SLIDESHOW_APPLY` | 8 | start 3 + tick 5 |
| `SLIDESHOW_TICK` | 8 | すべて `ok:true`（完了行） |

## op1 / op2 / op3 の位置づけ

| 回 | main 相当 | 主な学び |
| --- | --- | --- |
| op1 | pre-#462 | JMA のみ安定。NDL/CODH 不安定。観測ログ不足 |
| op2 | #462 | tick/apply ログ追加。NDL は設計ギャップ（tick 再取得なし）を確定 |
| **op3** | **#464** | NDL tick + outcome で **product パイプライン成立**。JMA skip/apply も説明可能 |

## 残課題（MAT-02b / 熟成）

| 項目 | 状態 |
| --- | --- |
| NDL sync-on-tick | **op3 で確認済**（#464） |
| outcome op log | **op3 で確認済** |
| Profile `— none —` → L/R clear | **#465 マージ済**（本観測は主に #464 ビルド） |
| 00:53 型無 tick | 本ログに該当セッション無し — 長時間運用で再監視 |
| tick apply 失敗時 timer | 未着手 |
| CODH 長時間 + apply 乖離 | op2 以降未再検証 — 必要なら op4 |

## PMI

- #464: run `27246414065` — success
- #465: run `27249496072` — success（観測終了後マージ）

## ロードマップへの接続（オーナー 2026-06-10）

- [v2 ロードマップ固め](20260610-v2-roadmap-op3-planning.md) — MAT-10 実施載せ、**MAT-18**（NDL searchbytext）、**MAT-14b**（auto 倍率）

# MAT-08 観測 — viper3 slideshow-op.jsonl（途中結果）

実施日: 2026-06-09（ログ収集） / 記録: 2026-05-31  
親: [maturation §MAT-08](../online-issues/maturation-20260609-qt-common.md#mat-08--preset-系-slideshow-の動作ログcodh--ndl-観測用)  
環境: **viper3**（Linux、`/home/katsu`）、`harite-qt`、Post #461 main  
ログ: オーナー提供 `slideshow-op.jsonl`（90 行、JST `+09:00`）

## 観測条件

| 項目 | 値 |
| --- | --- |
| 有効化 | `HARITE_SLIDESHOW_OP_LOG` → `~/.cache/harite/slideshow-op.jsonl`（想定） |
| 期間 | `2026-06-09T18:56:13` 〜 `2026-06-09T20:39:46`（約 1h44m） |
| 記録数 | 90 JSONL 行 |
| 失敗（`ok: false`） | **1** / 10 sync セッション |

## 結論（オーナー確定）

**JMA 以外は不安定。** JSONL 上は remote GET が成功していても、実機では **期待した時刻の tick / 壁紙更新が起きない** ケースが多い。

| 区分 | 実機体感 | JSONL との関係 |
| --- | --- | --- |
| **JMA** | **問題なし** | `JMA_TICK` が約 10 分間隔で記録され体感と一致 |
| **NDL おまかせ** | 手編集 catalog 残存 — **問題なし**（廃止 preset の期待どおり失敗） | `ndl-random` sync NG のみ |
| **NDL イラスト** | **20:04 の回が来ず打ち切り** | Start sync（19:44）は OK。以降の tick ログなし |
| **NDL 写真・ランドマーク / 屋内** | **20:20 の回が来ず** | Start sync（20:10）は OK |
| **CODH 江戸観光** | 途中まで良好。**20:37 以降 壁紙更新なし** で打ち切り | `CODH_TICK` + `CODH_IMAGE_GET` は 20:37 に `ok: true` だが **体感は未更新** |
| **NDL 写真・屋外 / 図版（地図）** | **20:49 の回が来ず** で打ち切り | Start sync（20:39）は OK |

→ **op log の GET 成功 ≠ 壁紙更新成功**。MAT-02b の切り分けは **slideshow tick 発火** と **apply 層** が主戦場。

## オーナー補足（セッション別）

### JMA（L/R dual）

- 特に問題なし。ログの `JMA_TICK` とも整合。

### NDL おまかせ（`ndl-random`）

- catalog に残っていた手編集エントリ。同梱廃止済み preset のため sync 失敗は **想定内**（手編集漏れとしての product 問題ではない）。

### NDL イラスト（`ndl-random-illust`）— 打ち切り

- **20:04** に来るはずの回が発生せず観測終了。
- **L のみ**で動かしたが、本来その構成では動かないはず。
- R を `--none--` にしたのに **画像パスが残存**（`Clear-R` と同様に消えるのが本来）。
- 残っていた R 側パスがあることで **動いているように見えた**可能性 — 観測条件が汚染されている。

### NDL 写真・ランドマーク / NDL 写真・屋内

- Start（20:10 頃）は問題なし。
- **20:20** の回が来ない。

### CODH 江戸観光（おまかせ）+ keyword=浅草寺

- Start〜初回までは良好（index build + 初回 GET はログでも確認）。
- **20:37** を最後に壁紙更新なし — 打ち切り。
- ログ上は 20:37 に `CODH_TICK` / `CODH_IMAGE_GET` 成功。**取得と反映の乖離**。

### NDL 写真・屋外 / NDL 図版（地図）

- Start（20:39 頃）は問題なし。
- **20:49** の回が来ず — 打ち切り。

## JSONL サマリ（HTTP 層のみ）

| 区分 | JSONL | 補足 |
| --- | --- | --- |
| **JMA** | `JMA_TICK` ×9 すべて `ok: true` | 実機と一致 |
| **NDL facet** | Start sync 5 種すべて META→IIIF→GET→CACHE 成功 | **tick ログは無し**（NDL は Start 直前 sync のみが設計） |
| **CODH** | index 1309 件 build + sync/tick GET 成功 | tick GET 成功でも **壁紙未更新** の例あり |
| **旧 `ndl-random`** | sync NG（期待どおり） | — |

## 期待 tick とログの対応

slideshow 間隔 **10 分** 想定でのメモ（オーナー体感ベース）:

| 時刻（目安） | 観測セッション | 期待 | 実機 | JSONL |
| --- | --- | --- | --- | --- |
| 19:44 | NDL イラスト Start | 初回表示 | （要確認） | sync OK |
| **20:04** | NDL イラスト継続 | 次の回 | **来ず・打ち切り** | 該当 tick 無し |
| 20:10 | NDL landmark + indoor Start | 初回表示 | Start OK | sync OK |
| **20:20** | 同上継続 | 次の回 | **来ず** | 該当 tick 無し |
| 20:27 | CODH Start | 初回表示 | 良好 | sync OK |
| **20:37** | CODH 継続 | tick + 壁紙更新 | **更新なし・打ち切り** | `CODH_TICK` OK（乖離） |
| 20:39 | NDL outdoor + map Start | 初回表示 | Start OK | sync OK |
| **20:49** | 同上継続 | 次の回 | **来ず・打ち切り** | 該当 tick 無し |

## 副次 finding（状態 UI）

| 事象 | 期待 | 観測 |
| --- | --- | --- |
| L/R を `--none--` に変更 | 当該 side の画像パスが消える（`Clear-L/R` 同等） | viper3 では **R で残存**（L も同型の潜在バグ） |

→ slideshow 観測の前提を壊す。**L-only テストの妥当性に影響**。

## ログで見えないもの（v0 限界）

- slideshow **tick 発火**そのもの（NDL 向け）
- slideshow **apply**（desktop への反映）
- JMA の `filename` / list.json 解決結果
- Optimize 経路（MAT-11）の有無・作業ディレクトリ

## フォローアップ（MAT-02b / MAT-08 継続）

| ID | 内容 | 優先 |
| --- | --- | --- |
| **MAT-02b** | NDL/CODH — tick 不発・GET 成功でも未反映。apply / tick scheduler を主戦場に | **高** |
| UI | R `--none--` 時の path 残存（Clear-R 不整合） | **MAT-02b で修正** |
| MAT-08 v1+ | tick 発火・apply 成否を op log に足す | 高（切り分けに直結） |
| catalog | 残存 `ndl-random` を facet 版へ差し替え | 低 |

## 参照

- [harite-source-spec §12.4.3](../specs/source/harite-source-spec.md)（op log 契約）
- [C-01-E merged inventory](finished/20260603-c01-e-merged-inventory.md)（`ndl-random` 廃止）
- MAT-16 #461 — cache `updated_at` はローカル TZ（本ログの `ts_jst` とは別フィールド）

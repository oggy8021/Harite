# Issue #503

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/503>
- opened: 2026-06-14
- title: `JMA Slideshowにおいて画像更新があったにもかかわらず、Optimize + Apply していない`
- labels: （未付与）
- 報告: v2.0.1 候補マージ後の実機・XFCE（オーナー夜間 JMA デュアル実行）
- OP_LOG: `out/slideshow-op-v2-jma-002.jsonl`（`HARITE_SLIDESHOW_OP_LOG`）
- 前提: 寝る前に **左右ディスプレイ電源 OFF**

## 事象

### 観測セッション（2026-06-14）

- JMA デュアル（L: `jma-near-color` / R: `jma-asia-color`）、interval 60 分相当で夜間実行。
- **04:51** tick: L/R とも `filename_unchanged` → `SLIDESHOW_TICK skip_reason=no_remote_update`（#493 どおり）。
- **05:51** tick:
  - L/R とも `JMA_TICK` で `content_changed: true` / `cache_written: true` — `latest.png` と `jma-cycle.json` は **05:51** に更新（オーナー `remote-cache` 確認と一致）。
  - **`SLIDESHOW_APPLY` なし**。`SLIDESHOW_TICK` の締め行（`ok: true` / `ok: false`）も **なし**。
- **06:51 / 07:51** tick: 再び `filename_unchanged` → `no_remote_update` skip。05:51 に取得した新 PNG が **壁紙に一度も載らない** まま継続。

### ログ要点（05:51）

| step | 要点 |
| --- | --- |
| `SLIDESHOW_TICK` | phase=tick のみ（先頭行） |
| `JMA_CACHE_WRITE` / `JMA_TICK` L/R | 新 filename、bytes 変化、`overwritten: true` |
| （欠落） | `SLIDESHOW_APPLY`、`SLIDESHOW_TICK ok=...` の締め |

### remote-cache（05:51 時点）

- `jma-cycle.json` の `filename` / `updated_at` は 05:51 の新図。
- `latest.png` も 05:51 タイムスタンプ。

## 期待

- JMA で **cache が更新された tick** では、可能なら optimize+apply で壁紙を更新したい。
- ディスプレイ OFF 等で apply できない場合でも、**復帰後の tick で未 apply の cache を載せる**（05:51 の図が 06:51 以降も永遠に skip されない）。

## 分類

- `bug` — remote cache 更新と apply skip の **不整合**（#493 skip + display pause の組み合わせ）
- `investigation` — OP_LOG が pause 経路を締めていない（観測の困難さ）

## 関連

- 正本: [harite-source-spec.md §15.1.3](../specs/source/harite-source-spec.md) — JMA tick は filename 変化時のみ PNG GET
- 先行修正:
  - [#493](issue-493.md) — `no_remote_update` skip（**解決済** PR #500）
  - [#493](issue-493.md) — display 失敗時 **pause**（`DUAL_INPUT_REQUIRES_TWO_DISPLAYS`）
- 実装:
  - `src/harite/sources_remote_jma.py` — `jma_slideshow_tick`（更新時 `save_jma_cycle`）
  - `src/harite/gui/views/main_window.py` — `_should_skip_slideshow_apply_for_remote_ticks`, `_pause_slideshow_for_display_loss`, `on_slideshow_tick`
- OP_LOG 先例: [issue-493](issue-493.md) `slideshow-op-v2-jma-001.jsonl`

## 取り込み方針

- 現時点の判断: **近端着手候補**（v2.0.1 パッチ or v2.0.2 — オーナー判断待ち）
- 原因はほぼ確定（下記調査メモ）。修正は **「cache だけ進んだ未 apply 状態」** の回収設計が中心。
- 修正候補（いずれかまたは併用）:
  1. **pending apply** — remote が `no_update=False` なのに apply が pause / 失敗したら、次 tick は `filename_unchanged` でも apply する
  2. **pause 時 OP_LOG** — `SLIDESHOW_TICK ok=true skip_reason=display_paused` + `detected_display_count`（未 apply であることをログで可視化）
  3. **jma-cycle の更新タイミング** — apply 成功後にだけ cycle を進める（副作用大・要 spec 検討）
- 次: ~~本メモ確定~~ → impl + テスト（v2.0.1）

### オーナー判断（2026-06-14）

- 外の世界（JMA API / cache 更新）が正 — **cache だけ進むのは当然**。
- XFCE `234bc04` 系: ディスプレイ電源 OFF でも検知できるまで動く → **いつ pause したか OP_LOG で欲しい**（#493 で pause 挙動は入ったが **締め OP_LOG は未だった** → 本修正で `display_paused` 追加）。
- **07:51** はディスプレイ ON — 05:51 に取った `latest.png` を載せたい → **pending apply 回収**で対応。
- **v2.0.1 圏内**で改修。

## 調査メモ

### 原因（コード上ほぼ確定）

**#493 の二つの改善が組み合わさった隙間。**

```text
05:51 on_slideshow_tick
  → jma_slideshow_tick L/R: filename 変化 → latest.png 上書き + jma-cycle 更新
  → _should_skip_slideshow_apply → False（更新あり）
  → _apply_slideshow_selection
       → optimize: build_two_screen_optimize_context() が None（ディスプレイ OFF）
       → _is_transient_slideshow_cycle_error → pause（slideshow_running は維持）
  → return True（**SLIDESHOW_TICK 締め OP_LOG なし**、SLIDESHOW_APPLY なし）

06:51 on_slideshow_tick
  → jma_slideshow_tick: filename == jma-cycle → no_update=True
  → _should_skip_slideshow_apply → True（L/R とも no_update）
  → apply 省略（no_remote_update）
  → 05:51 の latest.png は未 apply のまま
```

**ポイント:**

1. **05:51** — cache は進んだが、display pause で apply だけ落ちた。
2. **06:51 以降** — `jma-cycle.json` は既に 05:51 の filename を記録しているため、JMA API 上は「未更新」→ #493 skip が毎 tick 発動。
3. オーナーがディスプレイを ON に戻していても、**filename 不変の間は apply されない**。

### 04:51 / 06:51 が「期待どおり」な理由

- 04:51 / 06:51 / 07:51: 天気図 filename 不変 → cache 不変 → `no_remote_update` skip は #493 設計どおり。

### 05:51 だけが「期待外」な理由

- **cache 層は更新済み**（OP_LOG + `remote-cache` で確認）。
- **apply 層だけ未実行**（pause + OP_LOG 欠落）。
- その **未 apply 状態が回収されない**（次 tick が filename ベース skip）。

### オーナー前提との整合

「寝る前に左右ディスプレイ電源 OFF」は、05:51 の optimize 失敗 → pause と整合。**問題は pause 後の回収不在**。

### テストギャップ

- `test_post_release_wave2_slideshow.py` は dual JMA **skip** と **display pause** を別テストでカバー。
- **「remote 更新 → pause → 次 tick filename_unchanged でも apply」** は未カバー。

### 実装方針（#503 fix）

1. `pending_remote_apply` — remote tick が `no_update=False` なのに apply 未完なら立てる。次 tick は `filename_unchanged` でも optimize+apply。
2. apply 成功で下ろす。
3. pause 時 `SLIDESHOW_TICK skip_reason=display_paused` + `detected_display_count` + `pending_remote_apply`。
4. 成功回収時 `recovered_pending_remote_apply=true`（任意 OP_LOG）。

### memo（オーナー）

- 05:51 の挙動が期待通りではない（cache は新しいのに壁紙未更新、その後も skip 続行）。

## resolution

（未解決）

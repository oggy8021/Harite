# Issue #493

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/493>
- opened: 2026-06-13
- title: `JMAデータによる Slideshow において、データ更新がない段のTICK動作がおかしい`
- labels: `help wanted`
- 報告: v2.0.0 リリース直後（オーナー実機・XFCE）
- OP_LOG: `out/slideshow-op-v2-jma-001.jsonl`（`HARITE_SLIDESHOW_OP_LOG` 指定）

## 事象

### 観測セッション（2026-06-13）

- JMA preset デュアル（L: 気象庁日本付近 / R: アジア域）で slideshow 実行。
- **09:31** start 系: remote sync → `SLIDESHOW_APPLY` OK（`HDMI-1` / `DP-1` per-monitor auto-split）。
- **10:31** tick: L/R とも `JMA_TICK` は `skip_reason: filename_unchanged`（更新なし）— ここまでは妥当。
- 直後の `SLIDESHOW_TICK` が **`ok: false`** で slideshow 停止:

  ```text
  slideshow cycle auto-split prepare failed: Two input images require two detected displays. Use one input only.
  ```

- 朝 6 時相当の天気図以降、JMA 側に実更新が無かった（**11:30 頃まで監視後、手動打ち切り**）。

### ログ抜粋（要点）

| 時刻 (JST) | step | 要点 |
| --- | --- | --- |
| 09:31:07 | JMA_CACHE_WRITE (R) | `content_changed: true` — 初回取得 |
| 09:31:08 | SLIDESHOW_APPLY | start OK |
| 09:31:28–30 | JMA + APPLY | start 再同期（L/R `content_changed: false` も overwrite） |
| 10:31:29 | JMA_TICK L/R | `filename_unchanged`, fetch/cache スキップ |
| 10:31:29 | SLIDESHOW_TICK | **error**（上記メッセージ） |

## 期待

1. **更新がない tick では Skip が妥当** — JMA が `filename_unchanged` なら optimize / apply を走らせず、slideshow を継続したい。
2. 左右ソースを指定しているのに「two detected displays」エラーが出る理由を切り分けたい（**モニター信号検出由来か** → OP_LOG に記録したい）。
3. **start / stop 時刻**も OP_LOG に残したい（現状 `SLIDESHOW_START` / `SLIDESHOW_STOP` ステップなし）。

## 分類

- `bug` — tick 時の skip 未実装 + エラー時の過剰停止
- `investigation` — 表示検出の瞬間失敗か、skip 設計漏れかの切り分け
- `enhancement` — OP_LOG 拡張（display 診断、start/stop）

## 関連

- 正本: [harite-source-spec.md §op log](../specs/source/harite-source-spec.md) — `JMA_TICK`, `SLIDESHOW_TICK`, `SLIDESHOW_APPLY`
- 観測先例:
  - [op2](../working/finished/20260610-mat-08-viper3-slideshow-op2-observation.md) — filename 未変化時の apply 欠落を「skip かログ欠落か」と記載
  - [op3](../working/finished/20260610-mat-08-viper3-slideshow-op3-observation.md) — `filename_unchanged` + tick 後 `SLIDESHOW_APPLY` は「outcome どおり」と記載（**本 Issue は apply 前に optimize で失敗し停止** — op3 と異なる）
- 実装:
  - `src/harite/sources_remote_jma.py` — `jma_slideshow_tick`, `skip_reason=filename_unchanged`
  - `src/harite/gui/views/main_window.py` — `on_slideshow_tick`, `_apply_slideshow_selection`, `_is_transient_slideshow_cycle_error`
  - `src/harite/optimize_settings.py` — `DUAL_INPUT_REQUIRES_TWO_DISPLAYS`
  - `src/harite/display_context.py` — `build_two_screen_optimize_context` → `detect_displays()`
  - `src/harite/slideshow_op_log.py` — `HARITE_SLIDESHOW_OP_LOG`
- 他 Issue: [#494](issue-494.md)（tray / main 状態ずれ — 本 tick 失敗がトリガー）

## 取り込み方針

- 現時点の判断: **保留**（修正タイミングは別途。調査・OP_LOG 拡張方針を先に固める）
- スコープ候補:
  1. **tick skip:** L/R とも remote tick が「更新なし」なら `_apply_slideshow_selection` を省略し `SLIDESHOW_TICK ok=true skip_reason=...` を記録
  2. **表示検出失敗:** tick 時の `DUAL_INPUT_REQUIRES_TWO_DISPLAYS` を `_is_transient_slideshow_cycle_error` に含め pause 扱い（現状は **slideshow 完全停止**）
  3. **OP_LOG:** エラー時に `detected_display_count` / display 名一覧；`SLIDESHOW_START` / `SLIDESHOW_STOP` ステップ追加
- 次: オーナー追加観測 → spec / gui-spec に tick skip 期待を1段落 → impl
- **判断確定（2026-06-13）:** モニター検知由来の display 失敗は **pause** — [planning Wave 2](../working/20260613-v2-post-release-fix-planning.md)

## 調査メモ

### コード経路（10:31 tick）

```text
on_slideshow_tick
  → log SLIDESHOW_TICK (phase=tick, 先頭・ok 未設定)
  → _remote_slideshow_tick_for_side → jma_slideshow_tick
       → filename 同一 → JMA_TICK ok, skip_reason=filename_unchanged
  → _run_slideshow_cycle_for_side（キャッシュから画像 path 再選択）
  → _apply_slideshow_selection(left, right, cycle_phase="tick")
       → run_slideshow_optimize（2 入力）
            → resolve_optimize_display_settings
                 → build_two_screen_optimize_context()
                      → detect_displays() が 2 未満 → ValueError
       → except → SLIDESHOW_TICK ok=false, slideshow_running=false（停止）
```

**JMA の skip は fetch 層のみ。** optimize / apply 層は「更新なし」でも毎 tick 実行される。

### エラーメッセージの意味

`Two input images require two detected displays. Use one input only.`

- 定義: `optimize_settings.DUAL_INPUT_REQUIRES_TWO_DISPLAYS`
- 2 枚入力の optimize 時、`build_two_screen_optimize_context()` が `None` のときに送出（`detect_displays()` で **2 台未満**）。
- **左右ソース指定とは別問題** — ソースは L/R キャッシュ dir として揃っているが、**tick 時点のワークスペース検出**が 2 ディスプレイを返せなかった、と読める。

### モニター信号検出由来か？

- **有力。** `build_two_screen_optimize_context()` は毎回 `detect_displays()`（Linux では `xrandr` 等）を呼ぶ。09:31 start 時は 2 台検出できていた（`HDMI-1` / `DP-1` apply 成功）が、10:31 tick の optimize 直前に検出が 1 台以下になった可能性がある。
- ただし **更新なしでも optimize を走らせた**ため、表示検出が正常でも「不要な optimize」が走る設計問題は残る。

### transient pause とのギャップ

`_is_transient_slideshow_cycle_error` が pause にするのは **別メッセージのみ**:

```703:706:src/harite/gui/views/main_window.py
    def _is_transient_slideshow_cycle_error(self, exc: ValueError, *, cycle_phase: str) -> bool:
        if cycle_phase != "tick":
            return False
        return str(exc) == "per-monitor apply requires at least two detected displays"
```

今回の `DUAL_INPUT_REQUIRES_TWO_DISPLAYS` は **pause 対象外** → tick 失敗で `slideshow_running = False`（打ち切り相当）。

### OP_LOG ギャップ（オーナー要望）

| 要望 | 現状 |
| --- | --- |
| 表示検出失敗の診断を OP_LOG に | 未実装（`error` 文字列のみ） |
| start / stop 時刻 | `on_slideshow_start` / `on_slideshow_stop` に `log_slideshow_op` なし。`SLIDESHOW_APPLY phase=start` はあるが **セッション開始マーカーではない** |

### 修正の当たり（実装時メモ・未着手）

1. **短期:** `filename_unchanged` が L/R ともなら tick を short-circuit（`SLIDESHOW_TICK ok=true`, `skip_reason=no_remote_update` 等）。
2. **中期:** optimize 前の display 失敗を apply 層と同様 pause 化、または start 時の display スナップショットを tick でも参照。
3. **観測:** OP_LOG に `SLIDESHOW_START` / `SLIDESHOW_STOP`、エラー時 `detected_displays` フィールド。

### memo（オーナー）

- 更新がないなら Skip が妥当では。
- 左右ソース指定なのに two displays エラー — モニター信号検出由来か → OP_LOG に記録したい。
- 朝 6 時以降 JMA 更新なし。11:30 頃まで見て打ち切り。
- start/stop 時刻も OP_LOG に記録したい。

## resolution

（未解決）

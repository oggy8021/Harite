# Issue #497

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/497>
- opened: 2026-06-13
- title: `Preset Slideshow において、縦長画像が取得できたとき設定との組み合わせで tick errorとなる場面が見られた`
- labels: `bug`
- 報告: v2.0.0 リリース直後（オーナー実機・viper3）
- 観測ログ: `out/slideshow-op-v2-002.jsonl`（MAT-08 系）

## 事象

Preset Slideshow 実行中、**remote 取得（NDL / CODH）は成功**するが、**optimize 準備（auto-split）で tick が失敗**し slideshow が停止する。

### 再現セッション（OP_LOG）

| 項目 | 値 |
| --- | --- |
| Start | 2026-06-13 **19:47** |
| L | NDL図版（イラスト）`ndl-random-illust` |
| R | 江戸観光（キーワード: **増上寺**）`codh-edo-spots-keyword` |
| interval | 600s（10分） |
| 成功 tick | 19:57 / 20:07 / 20:17（各 apply OK） |
| 失敗 tick | **20:27:58** — 以降ログなし |

### 失敗ログ（末尾 1 件）

```json
{
  "step": "SLIDESHOW_TICK",
  "ok": false,
  "error": "slideshow cycle auto-split prepare failed: scaled source image exceeds L area: 878x3048 does not fit in 2048x1280 (display 2048x1280 with margins L0,R0,U0,B0)"
}
```

直前の remote 層はすべて成功:

- `NDL_TICK` ok — IIIF `804587/241` pct 切り出し（縦長）、68,824 bytes
- `CODH_TICK` ok — 増上寺 index から random 1 件、3,257,297 bytes
- **`SLIDESHOW_APPLY` 未到達**（prepare で落ちた）

### UX 上の見え方（オーナー所感）

- slideshow が **止まっていることが分かりにくい**
- footer に **赤文字エラーが出ない**（MAT-13 完了後も本経路では未反映と見える）
- Tray / Main の状態ずれは [#494](issue-494.md) と同型の可能性

## 期待

- 縦長・小さい NDL 切り出し + display scale 設定の組み合わせでも、**tick を継続**するか、少なくとも **停止理由を赤文字で明示**する。
- tick 失敗時は Tray / タブ / footer が **stopped + error** で一致する（#494 整合）。

## 分類

- `bug` — optimize 層の intentional upscale 上限（MAT-14/14b）と NDL facet 縦長 crop の衝突
- `investigation` — tick 失敗時の feedback 同期漏れ（#494 とセットで継続調査が難しい）

## 関連

- [#494](issue-494.md) — tick 失敗後の Tray vs Main desync（**先に直すと調査しやすい**）
- [#493](issue-493.md) — 別経路の tick 失敗（JMA / ディスプレイ検出）— エラーメッセージは異なる
- [MAT-14](../online-issues/maturation-20260609-qt-common.md#mat-14--2x--4x-display-scale意図的拡大) — intentional display scale
- [MAT-14b](../online-issues/maturation-20260609-qt-common.md) — auto upscale（短辺閾値 1.5x / 2x）
- [MAT-13](../online-issues/maturation-20260609-qt-common.md) — footer 赤文字（#458 完了だが **timer tick 失敗経路は未同期**）
- [MAT-08](../online-issues/maturation-20260609-qt-common.md#mat-08--preset-系-slideshow-の動作ログcodh--ndl-観測用) — 本ログ採取
- 正本:
  - [harite-source-spec.md §15.3](../specs/source/harite-source-spec.md) — NDL facet tick
  - [harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md) — tick → optimize → apply
- 実装:
  - `src/harite/core.py` — `_resolve_intentional_image_dimensions`（`scaled source image exceeds`）
  - `src/harite/auto_display_scale.py` — `compute_auto_display_scale_factor`
  - `src/harite/gui/views/main_window.py` — `on_slideshow_tick`, `_apply_slideshow_selection`, `_is_transient_slideshow_cycle_error`
  - `src/harite/gui/adapters_qt/qt_backend.py` — `_on_slideshow_timer_event`（**sync なし**）
  - `src/harite/gui/adapters/gui_runtime_sync.py` — `sync_feedback_from_owner`（MAT-13 赤文字）
- 他 Issue: [#496](issue-496.md)（keyword 保存 — 別件）

## 取り込み方針

### 優先順（オーナー判断メモ）

継続調査・再現確認のしやすさのため、**#494（状態同期 + エラー表示）を先**にした方がよい。

1. **#494** — `_on_slideshow_timer_event` で `result is False` のとき `sync_slideshow_state_with_feedback_from_owner` → footer 赤文字・Tray 一致
2. **本件（optimize）** — **確定: 案 A（down-only フォールバック）** — [planning](../working/20260613-v2-post-release-fix-planning.md)
3. 回帰テスト: 縦長 NDL mock + L auto display scale on → tick が止まらない／エラーが footer に出る

## 調査メモ

### 原因（コード上）

**L 側 NDL イラスト**の縦長 IIIF 切り出しに **Slideshow L auto display scale（MAT-14b）** が 1.5x 等を適用し、拡大後サイズが display slot（2048×1280）を超える。

```212:238:src/harite/core.py
def _resolve_intentional_image_dimensions(..., intentional_factor: int = 1, *, side_label: str = "display"):
    factor = normalize_display_scale(intentional_factor)
    if factor == 1.0:
        return _resolve_native_dimensions(img, screen_w, screen_h, margins)  # down-only で fit
    ...
    if not _image_fits_with_margins(nw, nh, screen_w, screen_h, margins):
        raise ValueError(
            f"scaled source image exceeds {side_label} area: {nw}x{nh} does not fit in {max_w}x{max_h} ..."
        )
```

- `factor == 1.0` なら縦長でも **縮小して fit** するため、今回の 3 tick は通過しうる
- `auto_display_scale` が 1.5x / 2x を選ぶと **拡大のみ**で、高さ超過時に `ValueError`
- 推定: 元画像短辺が display 短辺の 1/2 以下 → **1.5x** → 878×3048 → 高さ 3048 > 1280

### なぜ NDL/CODH 取得は無関係に見えるか

remote tick は **cache への `latest.*` 上書きまで成功**。失敗はその後の **slideshow optimize（dual auto-split 合成）** 層。OP_LOG 上は `NDL_TICK` / `CODH_TICK` がすべて `ok: true` で、最後だけ `SLIDESHOW_TICK ok: false`。

### tick 停止経路

```1986:1999:src/harite/gui/views/main_window.py
        if not applied:
            self.slideshow_running = False
            ...
            self._set_status("error", "slideshow", error_message or "slideshow cycle apply failed", error=...)
            log_slideshow_op("SLIDESHOW_TICK", ok=False, ...)
            return False
```

`_is_transient_slideshow_cycle_error` は **ディスプレイ 2 枚未満**のみ pause 対象。本エラーは **hard stop**。

### エラーが赤文字にならない理由（#494 と同根）

```488:497:src/harite/gui/adapters_qt/qt_backend.py
    def _on_slideshow_timer_event(self) -> None:
        ...
            result = callback()
            if result is False:
                self._stop_slideshow_timer()
                # sync_slideshow_state_with_feedback_from_owner なし
```

owner は `_set_status("error", ...)` + `last_error` を設定するが、**Qt backend へ `sync_feedback_from_owner` が走らない**ため `lblError` が更新されない（MAT-13 の赤文字経路に到達しない）。

### OP_LOG 補足（正常に見えた部分）

| 項目 | 判定 |
| --- | --- |
| interval 10分 | OK |
| NDL facet random | 各 tick 別図版・取得成功 |
| CODH 増上寺 index | 11 件・tick 取得成功 |
| CODH random mode | `cursor_index: 0` は random のログ仕様どおり |
| 停止 | optimize prepare の L 側 fit 失敗のみ |

### 回避（調査継続までの暫定）

- Slideshow **L Auto display scale をオフ**、または manual scale 100% → factor 1.0 で down-only fit
- ただし NDL facet は図版アスペクト比がランダムなため、設定次第で再発しうる

### memo（オーナー）

- display scale + 縦長 NDL で tick error。
- 止まっていることがアプリとして分からないのは #494 問題。
- 赤文字エラーが出ないのが特に分かりづらい。いくつか直さないと継続調査が難しい。

## resolution

（未解決）

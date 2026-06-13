# Issue #495

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/495>
- opened: 2026-06-13
- title: `Slideshow実行中の main window等からの設定変更を次のtickに適用する`
- labels: `enhancement`
- 報告: v2.0.0 リリース直後の slideshow 検証からの気づき（**#492–#494 とは独立した新規要素**）

## 事象（現状の不便）

Slideshow **実行中**に Main Window や Settings 等でパラメータを変えても、多くは **次の tick に載らない**、または **即時 re-apply**（stop/start なしでも負荷がかかる）に留まる。運用上 **Stop → 変更 → Start** を毎回挟むのが面倒。

特に変えたい例（オーナー）:

- **Interval**（spin）
- **Auto display scale**（Slideshow タブ L/R）
- 可能であればその他の slideshow / optimize 関連（margins、srcdir 変更等は別判断）

## 期待

- 実行中に UI で変更した値は、**可能なら次の tick から** 有効化する（いちいち stop/start しない）。
- interval 変更 → 次 tick 以降のタイマー間隔に反映、など。

## 分類

- `enhancement` / `planning` — 製品 UX（#492–#494 の bug 回帰経路とは別）

## 関連

- 正本: [harite-gui-spec.md §6.2](../specs/gui/harite-gui-spec.md) — 実行中の interval 変更は **owner のみ更新、timer 再起動なし、次回 Start 以降で有効**（現行仕様）
- 実装:
  - `src/harite/gui/views/main_window.py` — `on_slideshow_interval_change`, `on_change_slideshow_auto_display_scale`, `_reapply_slideshow_if_running`
  - `src/harite/gui/adapters_qt/qt_backend.py` — `_on_slideshow_interval_changed`, `_start_slideshow_timer` / `_stop_slideshow_timer`
  - `src/harite/gui/adapters/gui_runtime_slideshow_ui.py` — `commit_slideshow_interval_from_spin`
- 他 Issue: [#493](issue-493.md) / [#494](issue-494.md)（tick 失敗・状態 desync — 本件修正時に **deferred apply** 設計と整合させる）

## 取り込み方針

- 現時点の判断: **v2.0.1 同梱** — 現仕様の延長（enhancement だが大規模機能ではない）— [planning](../working/20260613-v2-post-release-fix-planning.md)
- スコープ案:
  1. **Deferred tick queue** — running 中の変更を「次 tick 用 pending」に積み、tick 開始時に commit + timer 再設定
  2. **対象の段階導入** — まず interval + slideshow auto scale。srcdir / profile 変更は副作用大のため後回し
  3. **即時 re-apply の見直し** — `on_change_slideshow_auto_display_scale` は現状 `_reapply_slideshow_if_running()` で **即 tick 相当の apply**（次 tick 待ちではない）
- 次: gui-spec §6 に「running 中の変更 → 次 tick 適用」表を追記 → 実装 → テスト

## 調査メモ

### 現行挙動（コード + 正本）

| 変更 | running 中の挙動 | 次 tick で有効？ |
| --- | --- | --- |
| **Interval spin** | `on_slideshow_interval_change` で owner 更新のみ。Qt timer **再起動なし** | **No** — 次回 **Start** まで（gui-spec §6.2 明記） |
| **Slideshow auto scale L/R** | `_reapply_slideshow_if_running()` → 即 `_apply_slideshow_selection(..., cycle_phase="tick")` | **即時**（次 tick 待ちではない） |
| **Main auto scale** | owner / form_state 更新のみ。reapply **なし** | **No**（slideshow 経路に未反映） |
| **Settings Apply** | `on_apply_settings` — running 中は `_slideshow_active_mode` 等の扱いに注意（要個別確認） | 混在 |

### `_reapply_slideshow_if_running`（参考）

```512:519:src/harite/gui/views/main_window.py
    def _reapply_slideshow_if_running(self) -> None:
        if not self.slideshow_running:
            return
        ...
        self._apply_slideshow_selection(left, right, cycle_phase="tick")
```

auto scale 変更は **次 tick ではなくその場で optimize+apply** する。ユーザー要望（次 tick に載せたい）とは **逆方向** の箇所もある。

### interval の timer

`qt_backend._start_slideshow_timer` は Start 成功時のみ呼ばれる。実行中 spin 変更は `_on_slideshow_interval_changed` → owner 更新 → `sync_slideshow_state_only_from_owner` のみ。

### 設計メモ（実装時の当たり・未確定）

- **Pending changes フラグ**（例: `_slideshow_pending_interval`, `_slideshow_pending_auto_scale`）を tick 入口で消化。
- interval: 次 tick **前** に `QTimer.setInterval` または one-shot 再スケジュール（経過中の tick を乱さない）。
- auto scale: 即時 `_reapply_slideshow_if_running` をやめ、pending に積んで次 tick の optimize へ渡す（#493 の skip 設計と両立要検討）。
- OP_LOG: `SLIDESHOW_DEFERRED_APPLY` 等で何が次 tick に載ったか記録すると検証しやすい（#493 要望と共通）。

### memo（オーナー）

- Slideshow 検証での気づき。他 Issue（#492–#494）とは経路が異なる純粋な新規要素。
- interval や auto 等を、可能なら **変えた後の tick** に載せたい。stop/start を挟むのが面倒。

## resolution

（未解決）

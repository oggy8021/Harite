# Issue #341

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/341>
- opened: 2026-05-31
- **closed: 2026-05-31**（W-02-A 完了 — PR #356）
- title: `Windows) スライドショーを実行しようとLRパス指定し、Startすると dual-source slideshow requires linux plugin となる`

## 事象

- Srcdir-L / Srcdir-R を指定して Start すると `dual-source slideshow requires linux plugin` となる
- **2026-05-31 以前:** spec-as-designed（dual-source slideshow は Linux plugin 前提）
- Srcdir-L のみの指定では Start できない（**引き続き仕様どおり** — GUI は両 srcdir 必須）

## 分類

- ~~spec-as-designed~~ → **resolved**（W-02-A, 2026-05-31）

## 現状到達点（2026-05-31 post #356）

| 層 | 状態 |
| --- | --- |
| 手動 Apply Span | **動作**（B-lite #352） |
| slideshow tick 内 Span 経路 | **動作**（#352 + #356） |
| dual-source **start** | **許可** — Windows + display 2+（`_prepare_slideshow_apply`） |
| 正本 | slideshow-spec §9 / gui-spec §6 Windows dual-source 反映（#355） |
| 手元確認 | dual srcdir → Start（ウィンドウ / tray）→ Interval / Span / current 表示 — **OK** |

精査: [working/20260531-1530-windows-post-w03-status-and-w02-slideshow.md](../working/20260531-1530-windows-post-w03-status-and-w02-slideshow.md)

## 関連

- backlog: [docs/working/20260531-1200-windows-qt-validation-backlog.md](../working/20260531-1200-windows-qt-validation-backlog.md)（W-02 **完了**）
- 横断: [#343](issue-343.md)（Apply / 壁紙 / 解像度）、two-screen、auto-split
- 正本: [harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md)、[harite-gui-spec.md](../specs/gui/harite-gui-spec.md) §6、[harite-plugin-spec.md](../specs/plugins/harite-plugin-spec.md) §4.1
- PR: #355（spec / status docs）、#356（impl + Interval / current path UX + spec 追記）

## 取り込み方針

| 項目 | 判断 |
| --- | --- |
| 即時 bugfix | **完了**（#356） |
| 設計判断 | **W-02-A 採択・実装済** — dual-source on Windows = wide composite + Span |
| 次アクション | **なし**（本 Issue クローズ） |
| オプション | W-02-B: GUI で single-srcdir Start 許可（CLI は既に可）— 未着手、別 Issue 化可 |

## 論点メモ

- Linux 向け dual-source / per-monitor 経路を Windows に **Span 経路として** 持ち込む案 — **W-02-A で採用済**。
- registry 自動復元は引き続き **非実装**（#343）。slideshow 中は opt-in Span 維持。

## resolution

**W-02-A（完了 2026-05-31）:** Windows + display 2+ で dual-source slideshow を許可。各 tick は B-lite と同型（two-screen optimize → composite → `resolve_apply_settings` → single-file apply + optional `ensure_span_style`）。per-monitor map / linux plugin は不要。

**旧事象（#352 以前）:** `dual-source slideshow requires linux plugin` — start ゲートによる拒否。**#356 で解消。**

**副次（#356）:** Start 直前 Interval spin commit（settings より spin 優先）、`Slideshow current` basename 省略（GTK/Qt）。正本: gui-spec §6.1–6.2。

**GitHub:** Issue #341 クローズ。正本・backlog・online-issues へ反映済。

# Issue #341

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/341>
- opened: 2026-05-31
- title: `Windows) スライドショーを実行しようとLRパス指定し、Startすると dual-source slideshow requires linux plugin となる`

## 事象

- Srcdir-L / Srcdir-R を指定して Start すると `dual-source slideshow requires linux plugin` となる
- **仕様として問題なし**（想定どおり）。dual-source slideshow は Linux plugin 前提
- Srcdir-L のみの指定では Start できない（これも仕様どおり）

## 分類

- **spec-as-designed**（2026-05-31 時点）→ **planning**（W-03 B-lite 完了後、spec 化可能）

## 現状到達点（2026-05-31 post #352）

| 層 | 状態 |
| --- | --- |
| 手動 Apply Span | **動作**（B-lite #352） |
| slideshow tick 内 Span 経路 | **コードあり**（`_apply_slideshow_selection`） |
| dual-source **start** | **拒否** — `_prepare_slideshow_apply` が `linux plugin` 必須 |
| 正本 | slideshow-spec §9 は linux 必須のまま |

精査: [working/20260531-1530-windows-post-w03-status-and-w02-slideshow.md](../working/20260531-1530-windows-post-w03-status-and-w02-slideshow.md)

## 関連

- backlog: [docs/working/20260531-1200-windows-qt-validation-backlog.md](../working/20260531-1200-windows-qt-validation-backlog.md)（W-02）
- 横断: [#343](issue-343.md)（Apply / 壁紙 / 解像度）、two-screen、auto-split
- 正本: [harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md)、[harite-plugin-spec.md](../specs/plugins/harite-plugin-spec.md) §4.1

## 取り込み方針

| 項目 | 判断 |
| --- | --- |
| 即時 bugfix | **不要**（2026-05-31 時点の start 拒否は旧 spec 通り） |
| 設計判断 | **W-02-A 推奨** — dual-source on Windows = wide composite + Span（#343 resolution 整合） |
| 次アクション | spec PR（slideshow-spec §9, gui-spec §6）→ test → `_prepare_slideshow_apply` 解除 |
| オプション | W-02-B: GUI で single-srcdir Start 許可（CLI は既に可） |

## 論点メモ

- Linux 向け dual-source / per-monitor 経路を Windows に **Span 経路として** 持ち込む案が B-lite 後に具体化（tick 実装済み、start のみ未接続）。
- Qt 移行の副産物として「できない」が目に付く — W-02 spec で **許可する範囲** を明文化する。
- registry 自動復元は引き続き **非実装**（#343）。slideshow 中は opt-in Span 維持。

## resolution（draft — spec PR 待ち）

**W-02-A（採択案）:** Windows + display 2+ で dual-source slideshow を許可。各 tick は B-lite と同型（two-screen optimize → composite → `resolve_apply_settings` → single-file apply + optional `ensure_span_style`）。per-monitor map / linux plugin は不要。

# Harite Project Initial Build Reformation WS10 Feature Overview（完了アーカイブ）

最終更新: 2026-06-09  
ステータス: **一次 inventory 完了記録**（本書は `finished/` へ移動。active 入口 → [20260609-1200-feature-overview.md](../20260609-1200-feature-overview.md)）

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](../../reformation/harite-project-initial-build-reformation.md) の Workstream 10 を具体化した **第1期 inventory** の完了記録である。
- **2026-06-09:** 構想保持・破棄候補を切り出し、本書は完了項目の参照用アーカイブとした。

## 一次 inventory（完了）

### 1. 着手候補（すべて完了）

| ID | 項目 | 完了記録 |
| --- | --- | --- |
| C-02 | source registry / source profiles | [planning](20260601-1400-c02-source-registry-planning.md) / [audit](20260601-c02-3layer-audit.md) |
| C-05 | slideshow source 強化 | [planning](20260602-1400-c05-slideshow-source-enhancement-planning.md) / [audit](20260602-c05-3layer-audit.md) |
| C-01 | 外部壁紙サイト連携 | [planning](20260603-1400-c01-external-wallpaper-source-planning.md) / [audit](20260603-c01-3layer-audit.md) |
| C-01-J | JMA 天気図 list.json カタログ | [調査](20260603-jma-weather-map-list-inventory.md) |
| C-01-E | 外部 source 探索拡張 | [統合索引](20260603-c01-e-merged-inventory.md) / [audit](20260603-c01-e-3layer-audit.md) |
| C-01-E-KW | CODH キーワード検索のユーザー指定 | [planning](20260605-c01-e-kw-codh-keyword-planning.md)（#413） |
| C-01-F | remote live sync on slideshow tick | [planning](20260604-c01-f-remote-sync-on-tick-planning-draft.md)（#425–426, spec #427） |
| P-05 | Manage sources リスト整理 | [planning](20260606-p05-manage-sources-panel-planning.md)（Qt） |
| P-03 | 単 display / monitor まわり UX | [planning](20260606-p03-single-display-ux-planning.md) / [audit](20260606-p03-3layer-audit.md)（#420） |

### 1b. 近端 backlog（すべて完了）

| ID | 項目 | 完了記録 |
| --- | --- | --- |
| F-01 | Windows 設定ファイル path | #365–367（[#354](../../online-issues/closed/issue-354.md)） |
| P-01 | 左右 path / srcdir の swap | #369–371（[#353](../../online-issues/closed/issue-353.md)） |
| P-02 | Slideshow srcdir クリア | #369–371（[#358](../../online-issues/closed/issue-358.md)） |
| P-06 | Slideshow CODH キーワード chip | [planning](20260606-p06-slideshow-codh-keyword-chip-planning.md)（Qt） |
| P-07 | Slideshow Drawer 開閉視認性 | [planning](20260606-p07-slideshow-drawer-open-state-planning.md)（#417） |
| P-04 | Main action cluster 整理 | [planning](20260607-p04-main-action-cluster-planning-draft.md)（#429） |
| P-08 | Main + Margins Drawer（案 B） | [planning](20260608-p08-main-margins-drawer-planning-draft.md) / [audit](../../specs/gui/audit/p08-3layer-audit.md)（#436） |

### 構想保持から完了へ移った項目

| ID | 項目 | 完了記録 |
| --- | --- | --- |
| C-04 | GUI surface / 利用導線 | [planning](20260604-c04-gui-surface-planning-draft.md)（#406–409, spec #427） |

## Qt 移行後 Windows 検証 backlog（W-xx — 完了）

| ID | 項目 | 完了記録 |
| --- | --- | --- |
| W-01 | action cluster レイアウト | #346（[#342](../../online-issues/closed/issue-342.md)） |
| W-02 | Windows slideshow 方針 | #355–356（[#341](../../online-issues/closed/issue-341.md)） |
| W-03 | Apply / 壁紙 / 解像度 | #349–352（[#343](../../online-issues/closed/issue-343.md)） |

統合: [20260531-1200-windows-qt-validation-backlog.md](20260531-1200-windows-qt-validation-backlog.md)

## 近中期の優先順序（確定・完了）

```
[完了] Qt 移行 + W-01〜W-03 + F-01 + P-01/P-02
[完了] C-02 → C-05 → C-01 系 → C-01-E-KW → C-01-F
[完了] C-04 → P-05 → P-03 → P-06 → P-07 → P-04 → P-08
```

Qt 移行: [20260530-2201-pyqt6-migration-plan.md](20260530-2201-pyqt6-migration-plan.md)

## 進捗メモ（抜粋）

- 2026-05-30〜06-01: Qt 移行完了、F-01 / P-01–02 完了、v1.0.0 リリース。
- 2026-06-02〜06-03: 第4波 C-02 / C-05 / C-01 / C-01-J / C-01-E 完了。K-02/K-03/K-06 破棄（→ [pending](../20260608-1200-feature-pending.md)）。
- 2026-06-04〜06-08: C-04 / C-01-F / P-05〜P-08 完了。
- 2026-06-09: 本 overview を完了アーカイブ化。active 入口を [20260609-1200-feature-overview.md](../20260609-1200-feature-overview.md) へ。

## 完了条件（WS10 立ち上げ — 達成済み）

- 後続機能 inventory の枠組みが説明可能になっている。
- 構想の受け皿として overview を置く理由が説明可能になっている。
- Workstream 1・3・4・5 と混線せずに次段へ送れる状態になっている。
- 少なくとも一次 inventory が overview 上で参照可能になっている。

# design

GUI の見た目合意形成用 artifact を置く（spec 正本の前段）。

## 位置づけ

| 種別 | 用途 | 例 |
| --- | --- | --- |
| **icon board** | Lucide 選定・icon+label・tone 比較 | [gui-phase10-icon-mock.html](gui-phase10-icon-mock.html) |
| **widget slice** | 新 widget 1 塊の配置・ラベル合意 | [20260601-p01-p02-lr-swap-clear-slice.html](20260601-p01-p02-lr-swap-clear-slice.html) |
| **評価メモ** | mock の pass/warn/fail 記録 | [gui-phase10-icon-mock-memo.md](gui-phase10-icon-mock-memo.md) |

- HTML mock はブラウザで開いて比較する。CI 対象外。
- 振る舞いの正本は [docs/specs/gui/](../../specs/gui/)。mock は合意用の補助資料。
- icon board は **icon 専用**。ウィンドウ全体のレイアウト正本にはしない。

## 現在のファイル

| ファイル | 内容 |
| --- | --- |
| [gui-phase10-icon-mock.html](gui-phase10-icon-mock.html) | Main / Slideshow icon 合意 board（Phase10 由来。旧ラベル Watch は legacy） |
| [gui-phase10-icon-mock-memo.md](gui-phase10-icon-mock-memo.md) | 上記 mock の目的・評価観点・手順 |
| [20260601-p01-p02-lr-swap-clear-slice.html](20260601-p01-p02-lr-swap-clear-slice.html) | 第2波 P-01/P-02 — Main swap + Slideshow swap/clear |
| [20260601-p01-p02-lr-swap-clear-slice-memo.md](20260601-p01-p02-lr-swap-clear-slice-memo.md) | 上記 slice の配置案・handler 草案・評価 checklist |
| [20260604-glade2-legacy-interpretation-memo.md](20260604-glade2-legacy-interpretation-memo.md) | 母体 `wallpositapplet.glade` 読解・A12/A13 推奨（C-04） |
| [20260604-c04-slideshow-margins-surface-slice.html](20260604-c04-slideshow-margins-surface-slice.html) | C-04 §4 Slideshow + §5 Margins 将来像（現行 vs 提案 / Drawer） |
| [20260604-c04-slideshow-margins-surface-slice-memo.md](20260604-c04-slideshow-margins-surface-slice-memo.md) | 上記 slice の合意 checklist |
| [20260605-c01-e-kw-manage-keyword-slice.html](20260605-c01-e-kw-manage-keyword-slice.html) | C-01-E-KW — Manage dialog keyword 行（暫定: Refresh 直上） |
| [20260605-c01-e-kw-manage-keyword-slice-memo.md](20260605-c01-e-kw-manage-keyword-slice-memo.md) | 上記 slice の K6 checklist + P-05 理想像 |

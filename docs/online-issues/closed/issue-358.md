# Issue #358

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/358>
- opened: 2026-05-31
- **closed: 2026-06-01**（P-02 完了 — 第2波）
- title: `スライドショーについて、Srcdir-L,R をクリアする仕組みがない`

## 事象

- Slideshow タブで Srcdir-L / Srcdir-R を空にする UI がない。
- Qt 版テスト時、左右 srcdir を揃えた state からやり直すのが手間。

## 分類

- polish / UX improvement → **resolved**

## 関連

- feature-overview: [P-02](../../working/20260518-2047-feature-overview.md)
- [#353](issue-353.md)（同第2波 — L/R swap）
- design: [20260601-p01-p02-lr-swap-clear-slice.html](../../working/design/20260601-p01-p02-lr-swap-clear-slice.html)
- 正本: [harite-gui-spec.md §3 Slideshow / §4.1](../../specs/gui/harite-gui-spec.md)

## 取り込み方針

- **完了（P-02 / 第2波）。** P-01 とまとめて design slice 合意。
- **採用:** **個別 clear**（Clear-L / Clear-R）。Main Clear-L/R と同配置（各 side panel 右下）。
- **不採用:** Clear both（間違えた side だけ空にしたい — オーナー判断）。
- 両 srcdir 必須ガードは維持 — 片方または両方空 → Start 不可。実行中 slideshow の自動 stop なし。

## 調査メモ

- memo（オーナー）: 個別 clear を design 段階で採用。Clear both は UX が悪い。
- design: [20260601-p01-p02-lr-swap-clear-slice-memo.md](../../working/design/20260601-p01-p02-lr-swap-clear-slice-memo.md)

## 3 層 audit（事後・2026-06-01）

| 層 | 内容 | PR / 根拠 |
| --- | --- | --- |
| **design** | Slideshow Main 同型 3 列 + 各 side 右下 Clear-L/R | #369（Clear both 却下 → 個別 clear 採用） |
| **spec** | §3 srcdir row、§4.1 `on_clear_slideshow_srcdir(side)` | #370 |
| **tests** | 個別 clear、start 可用性、実行中 stop なし、invalid side | #371 — `tests/gui/test_p01_p02_lr_swap_clear.py` |
| **impl（Qt）** | `MainWindow.on_clear_slideshow_srcdir`、`btn_clr_srcdir_l/r`、wiring | #371 |
| **impl（GTK）** | spec 上 parity 対象だが **未着手** | — |

**共有 PR:** P-01 と同一 (#369–371)。handler / widget は issue ごとに上表の行で切り分け。

## resolution

- **closed:** 2026-06-01
- **正本:** [gui-spec §4.1](../../specs/gui/harite-gui-spec.md)
- **PR:** #369（design）、#370（spec）、#371（tests + Qt impl）、本 PR（close）
- **手元確認:** Slideshow Clear-L/R + Start ガード（第2波 Qt impl 内、#353 と同 PR）

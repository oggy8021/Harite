# Harite - Feature Overview（active）

最終更新: 2026-06-09  
ステータス: **現行 planning 入口**（熟成運転期間 — Windows / Xfce 実使用、issue 蓄積）

## 位置づけ

- 本書は post-`1.0.0` の **第2期 feature inventory** 入口である（第1期の文脈: [reformation](../reformation/harite-project-initial-build-reformation.md)）。
- 第1期（C-xx / P-xx 一次波）の完了記録: [finished/20260518-2047-feature-overview.md](finished/20260518-2047-feature-overview.md)
- 破棄候補 / 保留延長: [20260608-1200-feature-pending.md](20260608-1200-feature-pending.md)

## この stream で固定すること

- 断片的な feature アイデアを inventory 化する。
- 実装候補、構想保持、破棄候補を粗く切り分ける（破棄・保留は pending ファイルへ）。
- post-`1.0.0` feature の planning 入口として、次期 planning の土台を更新し続ける。

## 現在ステータス

- **熟成運転期間** — 実機で使い込み、違和感は [online-issues](../online-issues/README.md) に蓄積する。
- 第1期 inventory は完了（上記 finished 参照）。
- **次に確実に言える inventory:** GTK を辞める（Qt 一本化）。

## 1. 着手候補

並び順は product 価値の精密評価より、前提の整理と着手しやすさを優先する。


| ID   | 項目       | 概要                                              | planning で最初に詰めること                                                      | 現判断                                    |
| ---- | -------- | ----------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------- |
| Q-01 | GTK を辞める | `harite-gtk` / GTK adapter 層を廃止し **Qt 一本化** する。 | 削除範囲（entrypoint / CI / packaging / docs）、GTK 専用 parity の未移植分の扱い、移行期間の有無 | **inventory 確定** — planning 未着手（熟成運転後） |


## 2. 構想保持

方向性は有力だが、着手候補より先に掘ると設計順が逆転しやすい項目。永久保留ではなく、前提が揃えば §1 へ再分類しうる。


| ID   | 項目                    | 概要                                         | 保持理由 / 採用条件                                                                                            |
| ---- | --------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| C-03 | plugin capability 可視化 | plugin ごとに受理 target や OS 制約を可視化する。         | **保留・縮小** — [C-04 計画正本](finished/20260604-c04-gui-surface-planning-draft.md) §6（独立パネルは出さず help 整理に吸収可） |
| K-04 | plugin 拡張パック          | Linux 以外や追加 desktop 向け plugin を外付け拡張として扱う。 | capability model と packaging 方針が先に必要。**Q-01（GTK 廃止）後**の packaging 議論と接続                                |


## planning 入口カテゴリ（active）


| カテゴリ                       | 現状                                             |
| -------------------------- | ---------------------------------------------- |
| GUI / runtime              | **Q-01** GTK 廃止 → Qt 一本化                       |
| plugin / apply             | C-03 capability 可視化（縮小保留）、K-04 拡張パック           |
| 外部ソース / slideshow / source | 第1期完了。拡張は issue 駆動                             |
| 破棄・保留                      | [pending](20260608-1200-feature-pending.md) 参照 |


## 次期 planning への渡し方

- overview では実装順をまだ固定せず、まず候補群の置き場所を作る。
- 着手候補から 1 つを選び、個別の spec / plan / tasks へ落とす（次は **Q-01** が自然）。
- 構想保持は、Q-01 や issue 蓄積の結果を受けて再分類する。
- 破棄候補 / 保留延長は [pending](20260608-1200-feature-pending.md) に置き、懐かしさで復活させない。


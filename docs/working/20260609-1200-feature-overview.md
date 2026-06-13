# Harite - Feature Overview（active）

最終更新: 2026-06-13  
ステータス: **現行 planning 入口**（`v2.0.0` リリース済み → **post-release #492–#497** 修正波）

## 位置づけ

- 本書は post-`1.0.0` の **第2期 feature inventory** 入口である（第1期の文脈: [reformation](../reformation/harite-project-initial-build-reformation.md)）。
- 第1期（C-xx / P-xx 一次波）の完了記録: [finished/20260518-2047-feature-overview.md](finished/20260518-2047-feature-overview.md)
- 破棄候補 / 保留延長: [20260608-1200-feature-pending.md](20260608-1200-feature-pending.md)

## この stream で固定すること

- 断片的な feature アイデアを inventory 化する。
- 実装候補、構想保持、破棄候補を粗く切り分ける（破棄・保留は pending ファイルへ）。
- post-`1.0.0` feature の planning 入口として、次期 planning の土台を更新し続ける。

## 現在ステータス

- **熟成運転:** 2026-06-09 宣言 → 同日 **打ち切り**（未改修のままでは継続不可のため）。
- **製品線:** `pyproject.toml` の `1.9.0` は熟成運転の中間マイルストーン。**本 stream の営みは `v2.0.0` を目指す**（Qt 一本化・remote source の確かさ）。
- **現フェーズ:** v2.0.0 リリース済み（#491）。**次:** post-release 6件 — [fix planning](20260613-v2-post-release-fix-planning.md)（#492–#497）。
- 第1期 inventory は完了（上記 finished 参照）。
- **再棚卸の入口:** [maturation §v2.0.0 への再整理](../online-issues/maturation-20260609-qt-common.md#v200-への再整理オーナー方針-2026-06-09)。

### 熟成運転メモ（Xfce 実機）

| 事象 | 観測 | 原因（調査） | 対応 |
| --- | --- | --- | --- |
| Main `More margin options…` が開かない | Drawer が見えない | `Gtk.Revealer` は組み立て済みだが `backend._objects` に revealer / snake_case キーが未登録。toggle が no-op | `gtk_runtime_object_registry` へ登録（修正済・要 Xfce 再確認） |
| Slideshow `More slideshow options…` が開かない | 同上 | 同上 | 同上 |
| Slideshow タブが Notebook 内で上寄せ | 起動直後から余白が下に溜まる | Main は `build_centered_page_shell` 経由、Slideshow は `slideshow_tab_box` を直 append していた | Slideshow も centered page shell へ（#439・確認済） |
| Slideshow Srcdir-L/R が横に伸びる | Notebook を左右 2 分割するように見える | 長い path label が panel 幅を押し広げ、同一列の icon button まで横伸び | button を centered row に入れ、label は `format_input_display` + ellipsize（#439 追記・要 Xfce 再確認） |
| Slideshow path label 省略なし | 長い path がそのまま表示 | GTK `refresh_slideshow_source_labels` が full path 固定 | basename 省略 + tooltip（#439 追記・要 Xfce 再確認） |
| GTK に Preset/Profile UI がないのに設定が部分展開 | Slideshow で NDL 図版など preset 由来の表示に見える | **認識済み:** GTK 版は Slideshow の Preset / Profile **提供面がない**。一方 settings 読み込みは Qt 版と同型のため、`slideshow_source_id_*` / `slideshow_profile_id` 等が防ぎきれず **部分的に展開**する | **記載のみ・削除しない** — GTK はメンテ対象外へ（Q-01）。parity 拡張はしない |

**Qt / 共通（v1.9.0 → v2.0.0）:** [maturation-20260609-qt-common.md](../online-issues/maturation-20260609-qt-common.md)。**完了（#442〜#472）:** MAT-01〜18, 10, 14b, Q-01 コード。[Q-01 計画](finished/20260610-q01-gtk-deprecation-planning.md) は finished へ移動済み。

## 1. 着手候補

並び順は product 価値の精密評価より、前提の整理と着手しやすさを優先する。


| ID   | 項目       | 概要                                              | planning で最初に詰めること                                                      | 現判断                                    |
| ---- | -------- | ----------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------- |
| MAT-13 | エラー表示を赤色に | footer / feedback の error がメッセージ性弱い | Status 面の色・コントラスト | **完了** #458 |
| MAT-14 | source image scale（% プリセット） | 100/125/150/200%、L/R 各1、拡大後が display に収まらなければエラー | MAT-01b 原寸回帰とは別軸。Compose 周辺の配置 | **完了** #459 |
| MAT-15 | core 幾何総点検 | align / margin 優先、ストレッチ誤解の是正、MAT-14 接続 | MAT-12→11 延長。GUI 注釈 + spec + テスト | **完了** #460 |
| MAT-16 | 時刻をローカル TZ（JST） | `jma-cycle.json` / `updated_at` 等の解析しづらさ | MAT-08 op log と方針統一 | **完了** #461 |
| MAT-17 | CLI slideshow + settings | CLI でも `harite-settings.json` を読む | settings + MAT-11 optimize 経路（single/dual）。catalog / remote tick は GUI 専用 | **完了** #463 |
| Q-01 | GTK をメンテ対象外に落とす | 回収コスト観点で GTK 削除 + 共有層 rename。**v2.0.0 = Qt 一本化。** | 付録 C レビュー済。GTK 熟成メモは **残す** | **コード完了** #472 — [計画](finished/20260610-q01-gtk-deprecation-planning.md) |
| MAT-02b | NDL / CODH slideshow 不安定 | tick / apply / none クリア。MAT-02 表示整合とは別枠。 | op3 で勝ち筋確定 | **完了** #462–#465 — [メモ](finished/20260609-mat-02b-slideshow-remote-stability.md) |
| MAT-08 | Preset slideshow 操作ログ（viper3） | op1 → op2 → op3 実機切り分け | [op3](finished/20260610-mat-08-viper3-slideshow-op3-observation.md) | **完了** |
| MAT-10 | 江戸切絵図 source（新規） | edo-maps / IIIF を雰囲気 slideshow source に | ライセンス・indexer | **完了** #470 |
| MAT-18 | NDL searchbytext | キーワードで図版検索（CODH 同型 UI） | op3: facet は書簡偏重 | **完了** #467–#468 |
| MAT-14b | auto 倍率 | 短辺閾値で 1.25–2x 自動拡大（Main+Slideshow） | MAT-14 手動 % とは別軸 | **完了** #469 |
| MAT-19〜24 | v2 前 CLI / 幾何一本化 | spec/help・embed・四重露出・Apply 経路・plugin 縮小・v2 bump | [roadmap](20260611-1200-cli-v2-roadmap.md)。従属: [gatereview](20260611-pre-bump-cli-gatereview.md)、[two-screen](20260611-two-screen-display-params-clarification.md) | **進行中**（MAT-19/21/22/23 完了、残: MAT-20/24） |


## 2. 構想保持

方向性は有力だが、着手候補より先に掘ると設計順が逆転しやすい項目。永久保留ではなく、前提が揃えば §1 へ再分類しうる。


| ID   | 項目                    | 概要                                         | 保持理由 / 採用条件                                                                                            |
| ---- | --------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| C-03 | plugin capability 可視化 | plugin ごとに受理 target や OS 制約を可視化する。         | **保留・縮小** — [C-04 計画正本](finished/20260604-c04-gui-surface-planning-draft.md) §6（独立パネルは出さず help 整理に吸収可） |
| K-04 | plugin 拡張パック          | Linux 以外や追加 desktop 向け plugin を外付け拡張として扱う。 | capability model と packaging 方針が先に必要。**Q-01（GTK 廃止）後**の packaging 議論と接続                                |


## planning 入口カテゴリ（active）


| カテゴリ                       | 現状                                             |
| -------------------------- | ---------------------------------------------- |
| GUI / runtime              | **Q-01** 完了 #472 → Qt 一本化                       |
| CLI / 幾何 / v2 bump         | **MAT-19〜24** [roadmap](20260611-1200-cli-v2-roadmap.md) |
| plugin / apply             | C-03 capability 可視化（縮小保留）、K-04 拡張パック           |
| 外部ソース / slideshow / source | 第1期完了。拡張は issue 駆動                             |
| 破棄・保留                      | [pending](20260608-1200-feature-pending.md) 参照 |


## 次期 planning への渡し方

- overview では実装順をまだ固定せず、まず候補群の置き場所を作る。
- 着手候補から 1 つを選び、個別の spec / plan / tasks へ落とす（次は **MAT-19** から [CLI v2 roadmap](20260611-1200-cli-v2-roadmap.md) の順序どおり）。
- 構想保持は、Q-01 や issue 蓄積の結果を受けて再分類する。
- 破棄候補 / 保留延長は [pending](20260608-1200-feature-pending.md) に置き、懐かしさで復活させない。


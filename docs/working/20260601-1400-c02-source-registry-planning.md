# C-02 — source registry / source profiles  planning

最終更新: 2026-06-01（段 0 完了 → 段 1 spec 昇格済み）

## 位置づけ

- 親 inventory: [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) §C-02
- 第4波（大 feature）の **planning 入口**（段 0 完了）。spec 正本: [harite-source-spec.md](../specs/source/harite-source-spec.md)。
- 後続: **C-05**（slideshow source 強化）→ **C-01**（外部壁紙サイト）の前提づくり。

## 用語（2026-06-01 オーナー確認）

| 語 | 意味 |
| --- | --- |
| **Slideshow** | 現行 product 語。GUI の `Slideshow` タブ、interval/tick による壁紙ローテーション（[gui-spec §6](../../specs/gui/harite-gui-spec.md)）。 |
| **Watch** | **slideshow の旧語**。新規 spec / planning / UI では使わない。 |
| **Watch（design artifact）** | [gui-phase10-icon-mock.html](design/gui-phase10-icon-mock.html) 等の **legacy ラベル** — Slideshow 面の icon 比較用として残るが、別タブ・別機能ではない。 |
| **K-01（feature-overview）** | 旧 inventory「watch 再構成」— 実体は slideshow 系の話と重複。**C-05 / C-02 整理後に再分類**（monitor 監視だけ残すなら別 ID）。 |

以降、本書では **slideshow srcdir / directory source** と書き、Watch は legacy 注記に限る。

## ゴール（C-02 で言う「source registry」）

slideshow 用 directory や将来の外部 source を **単発 path 入力**ではなく、**名前付き source** として登録・一覧・再利用できる基盤を作る。

| 現状 | C-02 後（目標イメージ） |
| --- | --- |
| Slideshow: `slideshow_srcdir_l/r` を settings に直書き | 登録済み source を **名前で参照**できる（path 直書きと共存可） |
| Main: `input_path_l/r` はセッション中心 | **C-02 対象外** — ファイラーお気に入りで賄う |
| 永続化: `harite-settings.json` の flat key のみ | catalog は **`sources.json`（案 B）**；実行 path は settings に残す |
| 外部 API / cloud 直結なし | **local directory**（+ mount 済み path）のみ第1段階 |

## 現状 inventory（2026-06-01）

### データ

| 場所 | 内容 |
| --- | --- |
| `SlideshowSettings.srcdir_l/r` | settings JSON の `slideshow_srcdir_l/r` |
| `MainWindow.input_path_l/r` | 実行時 path。settings load で復元されるが **registry 概念なし** |
| `AppSettings` | optimize / apply / slideshow の 3 分割（[settings.py](../../src/harite/settings.py)） |
| 設定ファイル | [core-spec §6.1](../../specs/core/harite-core-spec.md) — OS 別既定 path（F-01 済） |

### コード

- `source registry` / `SourceProfile` 等の **モジュール未存在**。
- slideshow 画像収集: `collect_slideshow_input_images` / `SlideshowCycleState`（directory path を直接受け取る）。
- plugin registry（`plugins.py`）とは **別概念** — OS apply plugin の登録であり、壁紙 **入力 source** ではない。

### GUI / CLI

- GUI: **Slideshow** タブの Srcdir-L/R picker（第2波 P-01/P-02 済）。**registry UI なし**。
- CLI: `--input` directory 等の **都度指定**（[cli-spec §6](../../specs/cli/harite-cli-spec.md)）。
- legacy design の「Watch mock」: Phase10 icon board 上の旧ラベル（= Slideshow 面の icon 比較）。**独立タブではない**。

## C-02 と隣接 feature の境界

```text
C-02  registry + profiles     … 名前付き source の CRUD・永続化・参照 API（L/R profile のみ）
C-05  slideshow 強化          … source type 拡張・実行面強化（**ordered list profile は持たない**）
C-01  外部サイト              … source type = remote / API（C-02 type 拡張）
（旧 K-01）                   … Watch=slideshow 旧語のため inventory 再整理待ち
```

**原則:** C-02 は「**箱と索引**」まで。slideshow の tick ロジック変更は **C-05** へ送る。

**スコープ外（オーナー 2026-06-01）:** profile 内の **ordered list**（入れ子のお気に入りを差し替え・ローテするプレイリスト型）は **採用しない・データモデルにも持たない**。壁紙収集向けの過剰ストーリーであり、現時点でユーザー訴求もない。registry は **フラットな名前付き source** + **L/R 2 スロット profile** に限定する。

## planning で詰める論点（feature-overview より）

### 1. source モデル（案）

第1段階は **local directory のみ**。

| フィールド | 必須 | 説明 |
| --- | --- | --- |
| `id` | ✓ | **UUID**（ユーザー非表示。settings / profile 参照用） |
| `name` | ✓ | ユーザー向け表示名 |
| `kind` | ✓ | 第1段階は `"local-dir"` 固定 |
| `path` | ✓ | ディレクトリ絶対 path（正規化規則は spec で定義） |
| `notes` | — | 任意メモ |

**source profile（確定）:** 名前付きの **L/R 固定 2 スロット**。

| フィールド | 説明 |
| --- | --- |
| `id` / `name` | profile 識別 |
| `members` | `{ "L": "<source_id>", "R": "<source_id>" }` — **L/R 固定のみ**（list 型なし） |

**オーナー決定（2026-06-01）:** L/R 固定。変更管理・変更機能の提供が単純になる。

**オーナー決定（2026-06-01）:** **ordered list は採用しない。** profile は L/R 2 スロット以外の形状を持たない。入れ子お気に入りの差し替え・ローテは想定外。

### 2. 永続化（確定: 案 B）

| 案 | メリット | デメリット |
| --- | --- | --- |
| **A.** `harite-settings.json` 内に `sources` / `source_profiles` 配列 | 1 ファイル、backup 簡単 | settings 肥大、load/save 全体が連動 |
| **B.** `%APPDATA%/harite/sources.json`（Linux: XDG config 配下） | settings と分離、diff しやすい | path 解決を foundation に追加 |
| ~~**C.**~~ | ~~catalog / state 分離~~ | ~~ファイル間分断で管理が重い。削りやすい過剰設計~~ |

**オーナー決定（2026-06-01）:** **案 B**。

| 保存先 | 内容 |
| --- | --- |
| **`sources.json`** | source catalog + profile catalog（CRUD 対象） |
| **`harite-settings.json`** | 従来どおり `slideshow_srcdir_l/r`（**実行 path**）。registry 選択を追跡する field（例: `slideshow_source_id_l/r`）が必要なら **こちらに追加** — catalog 本体は分離したまま |

profile / registry 選択時は `srcdir_l/r` へ **path を展開**（参照解決）。案 C のような catalog ↔ settings 間の二重管理は採用しない。

### 3. GUI / CLI surface（第1段階案）

| surface | 第1段階 | 送る |
| --- | --- | --- |
| **core API** | list / get / add / update / delete source；resolve profile → paths | — |
| **CLI** | **打ち止め** — 現行 4 command（optimize / apply / slideshow / install-desktop-entry）維持 | `harite source` サブコマンドは C-02 外 |
| **GUI** | **Slideshow のみ** — Srcdir 行に「登録済みから選ぶ」**最小**（combo または小 dialog） | Main input registry、専用 Sources 管理タブ |
| **settings dialog** | 触らない（または registry path 表示のみ） | 一括 editor |

**オーナー決定（2026-06-01）:** CLI は **打ち止め**。registry CRUD は **GUI + core API** のみ。既存 CLI は `--input` 等の都度指定のまま（[cli-spec §6](../../specs/cli/harite-cli-spec.md)）。

**オーナー決定（2026-06-01）:** GUI は **Slideshow のみ**。Main の input path は **ファイラーのお気に入り**で賄う（最近のファイラーは標準装備）。最終運用は Slideshow 主体という想定。

GUI 変更があるため、具体 widget は **design slice 合意後**に gui-spec へ（§9）。planning では **導線の有無**だけ固定する。

### 4. 後方互換

- 既存 `slideshow_srcdir_l/r` **そのまま動作**（registry 未使用でも可）。
- registry 導入時も **path 文字列を settings に残す**（案 B: catalog は `sources.json`、実行値は settings）。
- 旧 settings の **自動 migration は最小** — F-01 と同様、無理な推測 migration は避ける。

### 5. 削除・参照解決ポリシー（確定）

slideshow-spec に **registry エントリ削除**の直接先例はない。参考にする既存ルール:

| 状況 | slideshow / core の既存扱い |
| --- | --- |
| 入力 directory **不存在・空** | **起動前停止**（[core-spec §7](../../specs/core/harite-core-spec.md)、[slideshow-spec §9](../../specs/slideshow/harite-slideshow-spec.md)） |
| tick 中の一時的条件不足 | display 喪失のみ **pause**（slideshow-spec §5） |

**オーナー決定（2026-06-01）:** 上記に倣い、**参照先 file object にアクセス不能になる操作は中断（拒否）** とする。

| 操作 | ポリシー |
| --- | --- |
| **source delete**（profile が `members.L/R` で参照中） | **delete を拒否** — warn のみで続行しない |
| **実行時**（参照 path が消失・ inaccessible） | slideshow **中断** — start 前なら start failure、実行中なら stop / failure（既存 directory 検証と同型） |
| **source ID** | **UUID** — ユーザー非表示。rename は `name` フィールドのみ |

### 6. 上限・検証（確定）

**オーナー決定（2026-06-01）:** 安全側の初期上限。超過時は **追加を拒否**（`ValueError` 等、spec で具体化）。

| 対象 | 上限 |
| --- | --- |
| **source 数**（catalog 全体） | **64** |
| **profile 数**（catalog 全体） | **32** |
| **name**（source / profile 共通） | **64 文字** |
| **notes**（source のみ・任意） | **512 文字** |

path 長・存在確認は OS / 既存 slideshow 検証に従う。同名 source / profile の許容は **spec 段階**（未決なら拒否寄りで定義）。

## 提案フェーズ分割（第4波内）

| 段 | 内容 | 正本 | 停止点 |
| --- | --- | --- | --- |
| **0** | 本 planning + オーナー決定（open questions） | working（本書） | マージ許可 |
| **1** | core/foundation spec — モデル・path・API・保存形式 | core-spec または新 `source-spec` 分冊 | spec PR マージ |
| **2** | tests — registry CRUD / resolve / 互換 | tests | tests PR マージ |
| **3** | impl — `harite.sources`（名 TBD）+ persistence | src | impl PR マージ |
| **4** | GUI 最小（Slideshow から registry 選択） | gui-spec + design slice | 第2波と同型の段階停止 |
| ~~**5**~~ | ~~CLI サブコマンド~~ | — | **C-02 外**（オーナー: CLI 打ち止め） |

C-05 は **段 3 完了後**に別 planning を切る（source type 拡張・slideshow 実行面。profile 形状の list 化は対象外）。

## Open questions — 全決定済み（2026-06-01）

| # | 論点 | 決定 |
| --- | --- | --- |
| **1** | profile 形状 | **L/R 2 スロット固定のみ** — ordered list **非採用**（持たない） |
| **2** | 永続化 | **案 B** — `sources.json` に catalog。settings は実行 path + 必要なら選択 ID field |
| **3** | 第1 GUI | **Slideshow のみ** — Main はファイラーお気に入り。Slideshow 主体運用 |
| **4** | CLI | **打ち止め** — 現行 4 command 維持 |
| **5** | ID 規則 | **UUID**（ユーザー非表示） |
| **6** | 削除ポリシー | slideshow に直接先例なし → **アクセス不能時点で中断**。参照中 source の delete は **拒否** |
| **7** | 上限 | source **64** / profile **32** / name **64 文字** / notes **512 文字** — 超過は追加拒否 |

## 3 層比較（planning 時点 — 未実装）

| 層 | 現状 | C-02 完了時の期待 |
| --- | --- | --- |
| **spec** | ~~source registry 記述なし~~ | [harite-source-spec.md](../specs/source/harite-source-spec.md)（段 1 完了） |
| **tests** | なし | CRUD + resolve + settings 共存 |
| **impl** | なし | core モジュール +（段4で）Qt picker |

## 次アクション

1. ~~planning マージ~~（#373 済）
2. ~~**spec PR**（段 1）~~ → [harite-source-spec.md](../specs/source/harite-source-spec.md)
3. spec マージ後: **tests PR**（段 2）→ impl（段 3）→ GUI design slice（段 4）

## 参照

- [feature-overview §C-02](20260518-2047-feature-overview.md)
- [foundation-spec](../../specs/harite-foundation-spec.md) — 責務境界
- [core-spec §2 データモデル](../../specs/core/harite-core-spec.md)
- [gui-spec §6 slideshow](../../specs/gui/harite-gui-spec.md)
- 第2波プロセス例: [closed/issue-353.md](../online-issues/closed/issue-353.md)（design → spec → tests → impl）

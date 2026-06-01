# C-02 — source registry / source profiles  planning

最終更新: 2026-06-01（第4波着手）

## 位置づけ

- 親 inventory: [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) §C-02
- 第4波（大 feature）の **planning 入口**。本書は spec 正本の前段（`.cursorrules` §6 — working → specs 昇格）。
- 後続: **C-05**（slideshow source 強化）→ **C-01**（外部壁紙サイト）の前提づくり。
- **K-01**（Watch タブ再構成）は本波のスコープ外。Watch 向け icon mock は [design/gui-phase10-icon-mock.html](design/gui-phase10-icon-mock.html) のみ存在。

## ゴール（C-02 で言う「source registry」）

watch directory や外部 source を **単発 path 入力**ではなく、**名前付き source** として登録・一覧・再利用できる基盤を作る。

| 現状 | C-02 後（目標イメージ） |
| --- | --- |
| Slideshow: `slideshow_srcdir_l/r` を settings に直書き | 登録済み source を **名前で参照**できる（path 直書きと共存可） |
| Main: `input_path_l/r` はセッション中心 | 第1段階では **必須にしない**（registry は slideshow / 将来 watch 優先） |
| 永続化: `harite-settings.json` の flat key のみ | **registry 用のデータモデル + 保存先**を core/foundation に定義 |
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

- GUI: Slideshow タブの Srcdir-L/R picker（第2波 P-01/P-02 済）。**registry UI なし**。
- CLI: `--input` directory 等の **都度指定**（[cli-spec §6](../../specs/cli/harite-cli-spec.md)）。
- Watch タブ: **未実装**（release notes に名称のみ）。

## C-02 と隣接 feature の境界

```text
C-02  registry + profiles     … 名前付き source の CRUD・永続化・参照 API
C-05  slideshow 強化          … 複数 source 順序・profile を slideshow 実行に載せる
C-01  外部サイト              … source type = remote / API（C-02 type 拡張）
K-01  Watch 再構成            … 監視トリガー UI（C-02 registry を **消費** する側）
```

**原則:** C-02 は「**箱と索引**」まで。slideshow の tick ロジック変更や Watch 自動化は C-05 / K-01 へ送る。

## planning で詰める論点（feature-overview より）

### 1. source モデル（案）

第1段階は **local directory のみ**。

| フィールド | 必須 | 説明 |
| --- | --- | --- |
| `id` | ✓ | 安定 ID（UUID または slug）。settings 参照用 |
| `name` | ✓ | ユーザー向け表示名 |
| `kind` | ✓ | 第1段階は `"local-dir"` 固定 |
| `path` | ✓ | ディレクトリ絶対 path（正規化規則は spec で定義） |
| `notes` | — | 任意メモ |

**source profile（案）:** 名前付きの **source 参照の束**。

| フィールド | 説明 |
| --- | --- |
| `id` / `name` | profile 識別 |
| `members` | `{ "L": "<source_id>", "R": "<source_id>" }` または ordered list |

→ **要決定:** dual L/R 固定か、将来 C-05 向けに ordered list か。

### 2. 永続化（案）

| 案 | メリット | デメリット |
| --- | --- | --- |
| **A.** `harite-settings.json` 内に `sources` / `source_profiles` 配列 | 1 ファイル、backup 簡単 | settings 肥大、load/save 全体が連動 |
| **B.** `%APPDATA%/harite/sources.json`（Linux: XDG config 配下） | settings と分離、diff しやすい | path 解決を foundation に追加 |
| **C.** 両方（registry 本体 + settings に「現在選択 profile id」のみ） | 実行 state と catalog 分離 | 実装・spec やや重い |

**推奨（planning 時点）:** **C** — catalog は B、現在の slideshow 実行値は従来どおり settings / owner state。profile 選択時に `srcdir_l/r` へ **展開**（参照解決）。

### 3. GUI / CLI surface（第1段階案）

| surface | 第1段階 | 送る |
| --- | --- | --- |
| **core API** | list / get / add / update / delete source；resolve profile → paths | — |
| **CLI** | `harite source list|add|remove`（サブコマンド） | profile CRUD は第2子段階可 |
| **GUI** | Slideshow Srcdir 行に「登録済みから選ぶ」**最小**（combo または小 dialog） | 専用 Sources タブ・Watch 面 |
| **settings dialog** | 触らない（または registry path 表示のみ） | 一括 editor |

GUI 変更があるため、具体 widget は **design slice 合意後**に gui-spec へ（§9）。planning では **導線の有無**だけ固定する。

### 4. 後方互換

- 既存 `slideshow_srcdir_l/r` **そのまま動作**（registry 未使用でも可）。
- registry 導入時も **path 文字列を settings に残す**運用を第1段階では許容（profile id 参照は任意拡張）。
- 旧 settings の **自動 migration は最小** — F-01 と同様、無理な推測 migration は避ける。

## 提案フェーズ分割（第4波内）

| 段 | 内容 | 正本 | 停止点 |
| --- | --- | --- | --- |
| **0** | 本 planning + オーナー決定（open questions） | working（本書） | マージ許可 |
| **1** | core/foundation spec — モデル・path・API・保存形式 | core-spec または新 `source-spec` 分冊 | spec PR マージ |
| **2** | tests — registry CRUD / resolve / 互換 | tests | tests PR マージ |
| **3** | impl — `harite.sources`（名 TBD）+ persistence | src | impl PR マージ |
| **4** | GUI 最小（Slideshow から registry 選択） | gui-spec + design slice | 第2波と同型の段階停止 |
| **5** | CLI サブコマンド（任意・C-02 内 or 直後） | cli-spec | 同上 |

C-05 は **段 3 完了後**に別 planning を切る（slideshow が複数 source をどう回すか）。

## Open questions（オーナー決定待ち）

1. **profile 形状:** L/R 2 スロット固定 vs 名前付きリスト（C-05 見込みで list 寄り？）
2. **永続化:** 案 A / B / C のどれで開始するか
3. **第1 GUI:** Slideshow のみで足りるか、Main input path の registry 参照も同波に含めるか
4. **CLI:** C-02 必須か、GUI 先行か
5. **ID 規則:** UUID vs ユーザー指定 slug（rename 時の参照更新）
6. **削除ポリシー:** profile が参照中の source を delete したとき warn / block

## 3 層比較（planning 時点 — 未実装）

| 層 | 現状 | C-02 完了時の期待 |
| --- | --- | --- |
| **spec** | source registry 記述なし（plugin registry のみ） | モデル・永続化・resolve・GUI/CLI 最小 surface |
| **tests** | なし | CRUD + resolve + settings 共存 |
| **impl** | なし | core モジュール +（段4で）Qt picker |

## 次アクション

1. 本 PR をレビュー → **マージ許可**
2. Open questions 1–6 をオーナーが回答
3. 回答を反映した **spec PR**（段 1）を起票 — **ここで初めて正本改定**

## 参照

- [feature-overview §C-02](20260518-2047-feature-overview.md)
- [foundation-spec](../../specs/harite-foundation-spec.md) — 責務境界
- [core-spec §2 データモデル](../../specs/core/harite-core-spec.md)
- [gui-spec §6 slideshow](../../specs/gui/harite-gui-spec.md)
- 第2波プロセス例: [closed/issue-353.md](../online-issues/closed/issue-353.md)（design → spec → tests → impl）

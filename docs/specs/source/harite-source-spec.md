# Harite source registry 仕様 (Source Spec)

最終更新: 2026-06-01 (C-02 段 1 — planning #373 昇格)

## 1. 責務

- slideshow 用 **local directory** を、単発 path ではなく **名前付き source** として登録・一覧・再利用する catalog を定義する。
- **source profile** は L/R 固定 2 スロットに source を割り当てた名前付きプリセットである。
- catalog の永続化、CRUD、参照解決（profile / source id → directory path）を core 層の契約として定義する。

本書が扱わないもの:

- slideshow の tick / cycle ロジック変更（[slideshow-spec](../slideshow/harite-slideshow-spec.md) — C-05）
- Main タブ input path の registry（ファイラーお気に入りで賄う）
- CLI `harite source` サブコマンド（CLI 打ち止め — [cli-spec](../cli/harite-cli-spec.md)）
- plugin registry（[plugin-spec](../plugins/harite-plugin-spec.md)）— OS apply plugin 登録であり、入力 source ではない
- profile / source の **ordered list** 形状、profile 間の周回ローテ

planning 正本: [20260601-1400-c02-source-registry-planning.md](../../working/20260601-1400-c02-source-registry-planning.md)

## 2. 用語

| 語 | 意味 |
| --- | --- |
| **source** | 1 件の local directory を指す catalog エントリ（`id`, `name`, `kind`, `path`） |
| **source profile** | L/R 2 スロットに source id を割り当てた名前付きプリセット |
| **catalog** | `sources.json` に保存される source 列 + profile 列の全体 |
| **resolve** | source id または profile id から **実行用 directory path** を得る操作 |

## 3. データモデル

### 3.1 Source

第 1 段階の `kind` は **`local-dir` のみ**。

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `id` | string (UUID) | ✓ | 安定 ID。ユーザー非表示。生成は実装側 |
| `name` | string | ✓ | ユーザー向け表示名。catalog 内で **一意**（§5.2） |
| `kind` | string | ✓ | 第 1 段階は `"local-dir"` 固定 |
| `path` | string | ✓ | directory **絶対 path**（§4 正規化後） |
| `notes` | string | — | 任意メモ |

### 3.2 Source profile

profile は **L/R 固定 2 スロットのみ**を持つ。list 型 `members` は **採用しない**。

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `id` | string (UUID) | ✓ | 安定 ID |
| `name` | string | ✓ | ユーザー向け表示名。profile catalog 内で **一意**（§5.2） |
| `members` | object | ✓ | `{ "L": "<source_id> \| null>", "R": "<source_id> \| null>" }` |

- `members` は **`L` と `R` キーを常に持つ**。
- 未割当スロットは JSON `null` とする（キー省略は load 時に `null` へ正規化してよい）。
- profile **間の周回**や **profile 内 source の順序ローテ**は行わない。

### 3.3 Catalog（ファイル全体）

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `schema_version` | integer | ✓ | 現行は **1** |
| `sources` | array | ✓ | Source の列（最大 64） |
| `profiles` | array | ✓ | Source profile の列（最大 32） |

## 4. path 正規化

`local-dir` の `path` は add / update 時に次を満たすこと。

1. `Path(path)` で解釈し、**絶対 path** に正規化する（`resolve()` 相当。存在しない path は §7 の検証で拒否）。
2. 末尾の path セパレータは除去する。
3. 正規化後の path が **既存 directory** であること（ファイルのみ・不存在は拒否）。
4. directory 内に slideshow 採用可能な画像が 1 件以上あることは **registry CRUD 時には要求しない**（実行時検証は [slideshow-spec §2](../slideshow/harite-slideshow-spec.md) / [core-spec §7](../core/harite-core-spec.md) に従う）。

## 5. 上限と一意性

### 5.1 件数・文字数上限

超過時は **追加を拒否**し `ValueError` とする（§8）。

| 対象 | 上限 |
| --- | --- |
| source 数 | 64 |
| profile 数 | 32 |
| `name`（source / profile） | 64 文字 |
| `notes` | 512 文字 |

空文字 `name` は拒否する。

### 5.2 名前の一意性

- source の `name` は **sources 配列内**で一意（大小区別・完全一致）。
- profile の `name` は **profiles 配列内**で一意（同上）。
- source と profile の `name` が偶然同一でも **許容**する（別 namespace）。

### 5.3 ID の一意性

- `id` は catalog 全体（sources + profiles）で一意であること。
- 重複 `id` を含む JSON を load した場合は `ValueError` とする。

## 6. 永続化

### 6.1 ファイル path

`resolve_default_sources_path()` が返す既定 path は、設定ファイルと **同一の `harite/` ディレクトリ**配下とする（[core-spec §6.1](../core/harite-core-spec.md) と同型）。

| プラットフォーム | 既定 path |
| --- | --- |
| Linux（`XDG_CONFIG_HOME` 設定時） | `$XDG_CONFIG_HOME/harite/sources.json` |
| Linux（未設定） | `~/.config/harite/sources.json` |
| Windows | `%APPDATA%\harite\sources.json` |

- 初回 save 時に親ディレクトリを作成する（`mkdir(parents=True)`）。
- ファイル不存在時の load は **空 catalog**（`schema_version: 1`, `sources: []`, `profiles: []`）として扱ってよい。

### 6.2 物理形式

- UTF-8 JSON
- 保存時は 2-space indent と末尾改行
- `schema_version` 未対応の将来版を load した場合は `ValueError` とする（第 1 段階）

### 6.3 設定ファイルとの関係

[core-spec §6](../core/harite-core-spec.md) の `harite-settings.json` とは **ファイルを分離**する。

| 保存先 | 内容 |
| --- | --- |
| **`sources.json`** | source / profile catalog（本書） |
| **`harite-settings.json`** | 実行 state。従来どおり `slideshow_srcdir_l` / `slideshow_srcdir_r` に **展開済み path** を保持 |

registry 選択時の流れ:

1. GUI または core API が source / profile を resolve する。
2. 得られた path を owner / settings の `slideshow_srcdir_l/r` へ書く。
3. 任意で、どの registry エントリを選んだかを settings に記録する（§6.4）。

**自動 migration は行わない** — 既存 `slideshow_srcdir_*` から catalog へ推測 import しない（F-01 / C-02 planning と同型）。

### 6.4 settings 上の任意 tracking key（第 1 段階）

catalog 本体は `sources.json` のみ。settings には次の **任意 key** を追加してよい（未実装時は無視）。

| key | 意味 |
| --- | --- |
| `slideshow_source_id_l` | 最後に L 側で選んだ source `id` |
| `slideshow_source_id_r` | 最後に R 側で選んだ source `id` |
| `slideshow_profile_id` | 最後に適用した profile `id`（L/R 両方を profile から展開した場合） |

これらは **実行 path の代替ではない**。slideshow 実行は引き続き `slideshow_srcdir_l/r` の path 文字列を参照する。

## 7. core API（契約）

実装 module 名は **`harite.sources`**（ファイル分割は `sources_file.py` 等でよい）。GUI / CLI はこの API 経由で catalog を扱う。

### 7.1 Catalog I/O

| 操作 | 契約 |
| --- | --- |
| `load_catalog(path?)` | JSON → catalog model。不存在は空 catalog |
| `save_catalog(catalog, path?)` | catalog → JSON。検証済み catalog のみ |

### 7.2 Source CRUD

| 操作 | 契約 |
| --- | --- |
| `list_sources(catalog)` | 全 source |
| `get_source(catalog, source_id)` | 1 件。無ければ `KeyError` または `ValueError` |
| `add_source(catalog, *, name, path, notes?)` | UUID 採番、上限・一意性・path 検証 |
| `update_source(catalog, source_id, **fields)` | 部分更新。`id` 変更不可 |
| `delete_source(catalog, source_id)` | §7.4 参照整合を満たす場合のみ |

### 7.3 Profile CRUD

| 操作 | 契約 |
| --- | --- |
| `list_profiles(catalog)` | 全 profile |
| `get_profile(catalog, profile_id)` | 1 件 |
| `add_profile(catalog, *, name, members)` | UUID 採番。`members.L/R` の source id は存在する id または `null` |
| `update_profile(catalog, profile_id, **fields)` | 部分更新 |
| `delete_profile(catalog, profile_id)` | 参照中 settings key があっても **delete 可**（settings 側 id は次回 load で無効扱い／クリアは GUI 責務） |

### 7.4 Resolve

| 操作 | 戻り値 |
| --- | --- |
| `resolve_source(catalog, source_id)` | 正規化済み directory `Path` |
| `resolve_profile_members(catalog, profile_id)` | `{ "L": Path \| None, "R": Path \| None }` |

- 参照先 source が catalog に無い場合は `ValueError`。
- resolve 時点で path が **inaccessible**（不存在等）の場合も `ValueError`（実行前失敗と同型）。

### 7.5 削除ポリシー

[slideshow-spec](../slideshow/harite-slideshow-spec.md) に registry 削除の直接先例はない。次を採用する。

| 操作 | ポリシー |
| --- | --- |
| **source delete** | いずれかの profile の `members.L` または `members.R` が当該 `source_id` を参照している場合 **拒否**（`ValueError`） |
| **実行時** | 参照 directory にアクセス不能 → slideshow **中断**（start 前: start failure、実行中: stop / failure。[core-spec §7](../core/harite-core-spec.md) / slideshow-spec §9 と同型） |

## 8. エラー

- 検証失敗・上限超過・参照整合違反は **`ValueError`** とする（メッセージは user-facing 改修可能だが、契約として例外種別を固定）。
- catalog JSON 不正は load 時に `ValueError`。
- 明示 path 指定 load でファイル不存在は、呼び出し文脈により `FileNotFoundError` または空 catalog（§6.1）。

## 9. GUI / CLI surface（第 1 段階）

| surface | C-02 段 1（本書） | 後続 |
| --- | --- | --- |
| **core API** | §7 全文 | impl 段 |
| **CLI** | 変更なし | — |
| **GUI** | Slideshow から registry 選択する **導線あり**（widget 詳細は gui-spec + design slice、段 4） | [gui-spec §6](../gui/harite-gui-spec.md) |

## 10. 他分冊との境界

- 設定ファイル path 規則の親: [core-spec §6.1](../core/harite-core-spec.md)
- slideshow 実行・directory 検証: [slideshow-spec](../slideshow/harite-slideshow-spec.md)
- GUI Slideshow タブ widget: [gui-spec](../gui/harite-gui-spec.md)（段 4 で追記）
- 全体導線: [foundation-spec](../harite-foundation-spec.md)

## 11. 実装状態

| 層 | 状態 |
| --- | --- |
| **spec** | 本書（段 1） |
| **tests** | [tests/test_sources.py](../../tests/test_sources.py), [tests/test_sources_file.py](../../tests/test_sources_file.py)（段 2） |
| **impl** | `harite.sources`, `harite.sources_file`（段 2 — tests と同 PR） |

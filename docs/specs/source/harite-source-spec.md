# Harite source registry 仕様 (Source Spec)

最終更新: 2026-06-06（remote provider 契約の正本集約 — §12.4.1 Refresh、§12.5、§15.6–15.7）

## 1. 責務

- slideshow 用 **local directory** を、単発 path ではなく **名前付き source** として登録・一覧・再利用する catalog を定義する。
- **source profile** は L/R 固定 2 スロットに source を割り当てた名前付きプリセットである。
- catalog の永続化、CRUD、参照解決（profile / source id → directory path）を core 層の契約として定義する。

本書が扱わないもの:

- slideshow の tick / cycle **算法**の変更（選択モード・L/R 独立 state 等は [slideshow-spec](../slideshow/harite-slideshow-spec.md)）
- Main タブ input path の registry（ファイラーお気に入りで賄う）
- CLI `harite source` サブコマンド（CLI 打ち止め — [cli-spec](../cli/harite-cli-spec.md)）
- plugin registry（[plugin-spec](../plugins/harite-plugin-spec.md)）— OS apply plugin 登録であり、入力 source ではない
- profile / source の **ordered list** 形状、profile 間の周回ローテ

planning 正本: [20260601-1400-c02-source-registry-planning.md](../../working/finished/20260601-1400-c02-source-registry-planning.md)（C-02）、[20260602-1400-c05-slideshow-source-enhancement-planning.md](../../working/finished/20260602-1400-c05-slideshow-source-enhancement-planning.md)（C-05）、[20260603-1400-c01-external-wallpaper-source-planning.md](../../working/finished/20260603-1400-c01-external-wallpaper-source-planning.md)（C-01）

## 2. 用語

| 語 | 意味 |
| --- | --- |
| **source** | slideshow 用 directory を指す catalog エントリ（`id`, `name`, `kind`, `path`） |
| **source profile** | L/R 2 スロットに source id を割り当てた名前付きプリセット |
| **catalog** | `harite-sources.json` に保存される source 列 + profile 列の全体 |
| **resolve** | source id または profile id から **実行用 directory path** を得る操作 |
| **remote source** | `kind` が `remote-*` の source。`path` は **sync 済み cache directory**（§12） |
| **source preset** | 製品同梱の読み取り専用テンプレート（§13）。user catalog へは **import のみ** |
| **provider** | remote source の **手動 Sync** で cache を更新するサイト別実装（§14） |
| **sync** | provider が外部から画像を取得し cache を更新する操作（**手動のみ**、§12.4） |

## 3. データモデル

### 3.1 Source

`kind` は **`local-dir`** または **`remote-{provider略称}`**（§12.1）。user catalog の `schema_version` は **1 のまま**（新 field は追加しない）。

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `id` | string (UUID) | ✓ | 安定 ID。ユーザー非表示。生成は実装側 |
| `name` | string | ✓ | ユーザー向け表示名。catalog 内で **一意**（§5.2） |
| `kind` | string | ✓ | `"local-dir"` または `remote-*`（§12.1） |
| `path` | string | ✓ | **local-dir:** ユーザー指定 directory の絶対 path（§4）。**remote:** §12.3 の cache directory（import / add 時に自動設定） |
| `notes` | string | — | 任意メモ。remote の帰属・preset 由来マーカー等に使用してよい（§15 は 1b） |

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

### 4.1 `local-dir` path のプラットフォーム注記（C-05）

マウント済み NAS / 同期 cloud folder は **OS が通常の directory path として見せるもの**を `local-dir` の `path` として登録する。専用 `kind` や SMB クライアント（`smbprotocol` 等）は **採用しない**。

| 環境 | 推奨 path 例 | 契約 |
| --- | --- | --- |
| Windows | `G:\Pictures`、`\\server\share\Photo`（UNC） | Win32 / Pillow が directory として読める path を **そのまま**保存・resolve する |
| Linux | `/mnt/nas/photos` 等の **fstab / mount 済み** path | 通常の `local-dir` として扱う |
| Linux（GVFS） | `/run/user/.../gvfs/smb-share:...`（Thunar picker 等） | **CRUD 拒否はしない**（現状許容）。slideshow 実行の成功は **保証しない**。product 文書では `/mnt` 直指定を **推奨**（[実機観測](../../working/finished/20260602-c02-real-device-observations.md)） |

- PyGObject / GIO による GVFS 専用読み取りは **採用しない**（Qt 寄せ方針）。
- path 正規化（§4 1–3）は GVFS path に対しても適用する。存在チェックを通過しても、実行時の画像列挙が失敗しうる（[slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md)）。

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
| Linux（`XDG_CONFIG_HOME` 設定時） | `$XDG_CONFIG_HOME/harite/harite-sources.json` |
| Linux（未設定） | `~/.config/harite/harite-sources.json` |
| Windows | `%APPDATA%\harite\harite-sources.json` |

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
| **`harite-sources.json`** | source / profile catalog（本書） |
| **`harite-settings.json`** | 実行 state。従来どおり `slideshow_srcdir_l` / `slideshow_srcdir_r` に **展開済み path** を保持 |

registry 選択時の流れ:

1. GUI または core API が source / profile を resolve する。
2. 得られた path を owner / settings の `slideshow_srcdir_l/r` へ書く。
3. どの registry エントリを選んだかを settings の tracking key に記録する（§6.4）。

**slideshow start 前**（C-05）の流れは [slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md) を参照。tracking key がある side は **start 直前に再 resolve** し、得られた path で `slideshow_srcdir_*` を上書きする。

**自動 migration は行わない** — 既存 `slideshow_srcdir_*` から catalog へ推測 import しない（F-01 / C-02 planning と同型）。

### 6.4 settings 上の任意 tracking key（第 1 段階）

settings には次の **任意 key** を追加してよい（未設定時は無視）。

| key | 意味 |
| --- | --- |
| `slideshow_source_id_l` | 最後に L 側で選んだ source `id` |
| `slideshow_source_id_r` | 最後に R 側で選んだ source `id` |
| `slideshow_profile_id` | 最後に適用した profile `id`（L/R 両方を profile から展開した場合） |

**手動 Srcdir-L/R**（path picker / 直接入力）では、当該 side の tracking key は **空にする**（source UUID を付与しない）。**許容**する。

**実行時の path 正本（C-05）:**

| 経路 | start 前 | tick 中 |
| --- | --- | --- |
| tracking key **あり** | `resolve_source` / `resolve_profile_members` で `slideshow_srcdir_*` を更新してから画像収集 | **再 resolve しない**。start 時点の path を使用 |
| tracking key **なし**（手動 path のみ） | 既存 `slideshow_srcdir_*` をそのまま検証 | 同上 |
| CLI | 本書の tracking key は **使わない**（都度 `--input`） | — |

tick 毎の catalog 再 load は **行わない**。catalog の読み込みはアプリ起動時および Manage dialog 等の明示操作（C-02 現状維持）。

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
| **実行時** | 参照 directory にアクセス不能 → slideshow **中断**（start 前: start failure、実行中: stop / failure。[core-spec §7](../core/harite-core-spec.md) / [slideshow-spec §9](../slideshow/harite-slideshow-spec.md) と同型） |

### 7.6 実行中の catalog 変更（C-05 — GUI）

slideshow **running** 中に `harite-sources.json` が保存されたとき、GUI は **安全側**に倒す。

| 変更 | 動作 |
| --- | --- |
| 実行中 L/R が参照する `source_id` の **path 変更**・**source 削除** | **slideshow stop**（failure 扱い） |
| 実行中に適用した `slideshow_profile_id` の **members 変更**（L/R の source id 割当変更） | **slideshow stop** |
| 実行中 side の tracking `source_id` が catalog に **存在しなくなった** | **slideshow stop** |
| **無関係** source の `notes` / `name` のみ変更 | **続行**（次 tick からも start 時 path を維持） |
| 無関係 profile の変更 | **続行** |

- start 時に、実行に使う L/R の `source_id`（あれば）と `slideshow_profile_id`（あれば）を **実行スナップショット**として保持してよい。
- tick 毎の catalog 再 load は行わない（§6.4）。Manage dialog Close 後、上表に該当する変更があれば **即 stop** してよい（次 tick 待ちでもよい — 実装は stop を遅らせない方を推奨）。

## 8. エラー

- 検証失敗・上限超過・参照整合違反は **`ValueError`** とする（メッセージは user-facing 改修可能だが、契約として例外種別を固定）。
- catalog JSON 不正は load 時に `ValueError`。
- 明示 path 指定 load でファイル不存在は、呼び出し文脈により `FileNotFoundError` または空 catalog（§6.1）。

## 9. GUI / CLI surface

| surface | C-02 | C-05（本書） |
| --- | --- | --- |
| **core API** | §7 CRUD / resolve | §6.4 実行時 path、§7.6 catalog 変更 |
| **CLI** | 変更なし | 変更なし |
| **GUI** | registry 選択（[gui-spec §4.2 / §6.3](../gui/harite-gui-spec.md)） | start 前 resolve（§6.3 / [slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md)）。GTK parity は follow-up |

## 10. 他分冊との境界

- 設定ファイル path 規則の親: [core-spec §6.1](../core/harite-core-spec.md)
- slideshow 実行・directory 検証: [slideshow-spec](../slideshow/harite-slideshow-spec.md)
- GUI Slideshow タブ widget: [gui-spec](../gui/harite-gui-spec.md)（C-01 GUI は §6.5）
- 全体導線: [foundation-spec](../harite-foundation-spec.md)

## 12. Remote source（C-01 段 1a）

外部サイトから取得した壁紙候補を **cache-first** で扱う。fetch → ローカル cache directory → 既存 `resolve` → C-05 slideshow（実行面は `local-dir` と同型の directory 列挙）。

```text
[同梱 preset §13] → 起動時 bootstrap (§13.4) → harite-sources.json (schema v1, kind=remote-*)
       → Refresh / Start 直前 Sync (§12.4) → cache/{source_id}/
       → combo に *{name} 表示 (gui-spec §6.5) → 選択 → resolve → slideshow (C-05)
```

### 12.1 `kind` 命名

| 規則 | 内容 |
| --- | --- |
| 接頭辞 | `remote-` で始まる |
| 略称 | 小文字英数字と `-` のみ（例: `remote-jma-weather-map`）。正規表現 `^remote-[a-z0-9]+(?:-[a-z0-9]+)*$` |
| 登録 | 各 `kind` は **1 つの provider 実装**に対応（§14）。未登録 `kind` の Sync は `ValueError` |
| API key | **採用しない**（ユーザー管理・実装埋め込みを含む） |

`local-dir` 以外で `remote-` 接頭辞を持たない `kind` は **拒否**する。

### 12.2 Cache 根 directory

設定・catalog と **別ディレクトリ**に置く。`resolve_default_remote_cache_root()` が返す path。

| プラットフォーム | 第 1 候補 | 契約 |
| --- | --- | --- |
| Linux（`XDG_CACHE_HOME` 設定時） | `$XDG_CACHE_HOME/harite/remote-cache` | 親を `mkdir(parents=True)` してよい |
| Linux（未設定） | `~/.cache/harite/remote-cache` | 同上 |
| Windows | `%APPDATA%\harite\remote-cache` | §6.1 と同系の `harite/` 配下（`APPDATA` 未設定時は `Path.home() / "AppData" / "Roaming"`） |

**Windows フォールバック（第 1 候補が作成不能な場合のみ）:**

1. `%USERPROFILE%\Pictures\harite_cache_dir\remote-cache` を試す。
2. いずれも作成不能なら `ValueError`（user-facing メッセージ可）。

フォールバック採用時も、当該 run のあいだ **一貫した root** を使う（起動毎に候補を再評価してよい）。

### 12.3 Cache レイアウト

| path | 意味 |
| --- | --- |
| `{cache_root}/{source_id}/` | 1 remote source あたり 1 ディレクトリ。catalog の `path` はこの **絶対 path** と一致させる |
| 配下ファイル | provider が **その時点で必要な画像のみ** 配置する（アーカイブではない） |

**保持（オンデマンド）:**

- 1 回の `sync_remote_source` は **必要な画像 1 枚を都度 GET** し、cache へ **上書き** する。世代蓄積・所蔵リストのローカル複製は **しない**（§12.5）。
- 採用ファイル名は provider 共通ヘルパで **`latest.jpg`**（JPEG）または **`latest.png`**（PNG）。Sync 成功時、当該 directory の他 `*.png` / `*.jpg` / `*.jpeg` は削除してよい。
- 気象庁（§15.1–15.2）は常に **`latest.png` 1 件**。NDL / CODH は URL に応じて §上記のいずれか 1 件。
- slideshow **実行中**の Sync は、当該 run が参照中の `latest.*` を置き換えない（実行中は Sync を拒否、または stop 後に Refresh）。

**初回 import 時:** cache directory は **未作成でもよい**。`path` は `{cache_root}/{source_id}` を **予約**として catalog に書く。初回 Sync 成功で directory と画像が出現する。

**孤児 directory の掃除（C-01）:** `prune_orphan_remote_cache_dirs` は `{cache_root}` 直下の subdirectory のうち、**現在の catalog に存在する `remote-*` source の `id` と一致しない名前**の directory を削除する。GUI の **catalog materialize**（起動・combo 更新・Manage 保存後の再読込）のたびに best-effort で実行する。専用の「キャッシュ掃除」ボタンは置かない。

**ユーザーによる手動削除:**

- `{cache_root}` 自体、またはその中の **一部 / 全部の UUID subdirectory** を削除してよい（設定・catalog は別ファイルのため壊れない）。
- 削除後、Saved source で remote を選ぶと `resolve` が当該 `{source_id}/` を **空 directory として再作成**する（画像ファイルはまだ無い）。
- 画像の再取得は **Manage の Refresh** または slideshow **Start 直前の sync** で行う。起動時 materialize だけではネットワーク取得しない（§12.4）。

### 12.4 Sync と resolve

| タイミング | 契約 |
| --- | --- |
| **Catalog materialize** | GUI 起動・combo 更新時 — preset 追加・修復、**孤児 cache directory 削除**（§12.3）。**ネットワーク sync は行わない**（UI ブロック防止） |
| **Refresh** | Manage dialog の Refresh — 選択中 remote に `sync_remote_source` |
| **slideshow Start 直前** | 実行予定の L/R が参照する **すべての `remote-*`** source に `sync_remote_source`（[gui-spec §6.5](../gui/harite-gui-spec.md)） |
| **slideshow tick** | network fetch しない。各 tick は cache directory を `local-dir` と同型に再スキャンし、§12.5 の `latest.*` 1 枚を apply 対象とする |
| **resolve** | `remote-*` は cache directory が無ければ **作成してから** §4 と同型の `normalize_directory_path` を満たす。`local-dir` は既存 directory 必須。空 directory や画像 0 件は **resolve 時には成功しうる**が、slideshow start の画像収集は [slideshow-spec](../slideshow/harite-slideshow-spec.md) で失敗しうる |
| **実行中** | cache 削除・Sync による参照不能 → §7.5 / §7.6 と同型（stop / start failure） |

network エラー・HTTP 4xx/5xx は Sync 時に `ValueError`（またはラップした `OSError` を `ValueError` に変換してよい）。

**tick 毎の再 Sync（C-01-F）:** 現行 product では **採用しない**（据え置き）。interval ごとに別候補へ切り替えたい場合は、現行では Stop → Start または Manage **Refresh** で sync を走らせる。

#### 12.4.1 再起動・Refresh・Start — cache が変わる条件（正本）

ユーザーが「毎日アプリを開き直せば絵が変わるか」と読むときの契約。**sync が走らない操作では `latest.*` は前回のまま**残る。

| 操作の組み合わせ | network sync | `latest.*` の中身 |
| --- | --- | --- |
| **アプリ再起動のみ** | **しない**（materialize は `bootstrap_preset_sources(..., sync=False)`） | **変わらない** — 前セッションの cache をそのまま読む |
| 再起動 → **Slideshow Start** | **する**（実行 L/R の全 `remote-*`） | **変わりうる** — 層 A で候補を引き直す（§12.5） |
| 再起動 → Manage **Refresh** → Close | **する**（選択中 remote **1 件**） | 当該 source だけ変わりうる。Slideshow はまだ Start していなければ壁紙 apply は起きない |
| 実行中の **tick** のみ | しない | 変わらない |
| **Stop** → **Start**（再起動なし） | Start 直前で sync | 変わりうる（再起動 + Start と同型の sync 入口） |

**日常運用の読み方:** 「日々違う絵にしたい」なら **その日の最初の Slideshow Start**（前日 Stop 済み、または起動直後）が自然な入口。**再起動だけでは足りない**。前日と同じ cache を載せたまま Start すれば、sync 後に別候補へ変わりうる（NDL/CODH はランダム再抽選、JMA は list の最新 filename）。

#### 12.4.2 Manage Refresh の product 意味（provider 別）

Refresh はいずれも `sync_remote_source` 1 回だが、**ユーザーにとっての意味は provider で異なる**。

| provider 群 | Refresh が意味すること | 必須か |
| --- | --- | --- |
| **JMA**（`remote-jma-weather-map`） | 気象庁 `list.json` から **最新の実況天気図**を取り直す（コンテンツ自体が時系列で更新される） | 鮮度が要るなら **Start 直前 sync でも足りる**。Refresh は Start 前の明示的プレビュー／手動更新 |
| **NDL / CODH**（所蔵アーカイブ系） | 母集合（所蔵コーパス）は **滅多に変わらない**前提のまま、**「どの 1 枚を見せるか」だけ**を引き直す（NDL=サーバー random、CODH=`total`+random `start`） | **必須ではない**。同じことは **Slideshow Start 直前 sync** でも起きる（L/R 全 remote） |
| **CODH keyword preset** | Refresh 前に Manage の `keyword(CODH)` を `harite-settings.json` へ flush してから sync — **keyword 変更後の再抽選** | keyword を変えた直後は Refresh または次回 Start で反映 |

**Refresh が Start と重複しうる理由（NDL/CODH）:** Start は slideshow 実行の副作用として sync する。Refresh は **slideshow を開始せず**、または **選択中の 1 source だけ** cache を更新したいときの入口。所蔵更新ではなく **表示候補の再抽選**である点は §12.5 層 A と同じ。

**取りづらさの整理:** 所蔵ライブラリの更新を追うための Refresh ではない。アーカイブ系では「もう一度ランダムに引く」操作に近く、**毎日の変化は再起動 + Start** で足りる設計（Start で必ず sync するため）。

### 12.5 Remote cache と slideshow Mode（正本）

NDL / CODH を含む **すべての `remote-*`** に共通する契約。実装・product 説明の **一次参照は本節と §15** とする（`docs/working/finished/*inventory*` は API 調査の背景資料）。

#### 設計前提

| 前提 | 契約 |
| --- | --- |
| 所蔵の更新頻度 | 国立機関コレクションは **滅多に変わらない**前提でよい |
| ローカルコーパス | Harite は **所蔵リスト全体を cache に持たない**。sync ごとに **画像 1 枚**を取得し `latest.*` で上書き |
| 鮮度 | **Start 直前 Sync** と **Refresh** が画像入れ替えの入口。tick 毎の network fetch は §12.4 のとおり **しない** |

#### cache の slideshow 入力としての意味

- `resolve` 後の remote `path`（`{cache_root}/{source_id}/`）は **`local-dir` と同型**の slideshow 入力 directory（[slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md)）。
- 各 tick で `collect_slideshow_input_images` が directory を再スキャンするが、正常運用では **画像は 1 枚**（`latest.jpg` または `latest.png`）のみ。
- **ローカル所蔵リストの中を sequential / random で回す**方式ではない。

#### 2 層の「選び方」（混同しない）

| 層 | いつ | 何を決めるか | 正本 |
| --- | --- | --- | --- |
| **A. Sync 時の候補選択** | Start 直前・Refresh | リモートコーパス（または keyword 絞り込み後）から **どの 1 キャンバス／図版**を画像化するか | §15.6（NDL）、§15.7（CODH）、§15.2（JMA） |
| **B. Slideshow Mode** | 各 tick | **すでに cache にあるファイル列**から次に apply する path（`sequential` / `random`） | [slideshow-spec](../slideshow/harite-slideshow-spec.md) |

層 A と層 B は **直列につながらない**。remote のみの side では cache が 1 枚のため、**層 B（Mode）は実質ノーオペ** — `sequential` も `random` も毎 tick 同一ファイルを選ぶ。

#### L/R と Mode

- L / R は **独立**に `collect_slideshow_input_images` → cycle する（L/R 別 `SlideshowCycleState`）。
- Mode 設定は run 全体で 1 つだが、**各 side の `images` リスト長**に対して適用される。
- 例: L = CODH（1 枚）・R = `local-dir`（多数）→ **R 側だけ** Mode が効く。L/R 両方 remote なら **両方とも Mode 無効**（各 1 枚）。

#### 絵が変わるタイミング（現行）

| 操作 | 層 A（新しい候補の取得） | 層 B（Mode による切替） |
| --- | --- | --- |
| アプリ **再起動のみ** | **しない**（§12.4.1） | — |
| 再起動 → Slideshow **Start** | 実行 L/R の全 `remote-*` で sync → 候補が変わりうる | 開始 |
| Slideshow **Start**（再起動なし） | 同上 | 開始 |
| Manage **Refresh** | 選択中 remote で sync（Start せず再抽選） | — |
| Slideshow **tick** | **しない** | cache 1 枚なら変化なし |
| Mode を sequential ↔ random に変更 | — | remote 1 枚 side では見た目変化なし |

## 13. Source preset（C-01 段 1a）

製品同梱の **読み取り専用**テンプレート正本。user `harite-sources.json` への反映は **起動時 bootstrap**（§13.4）で行う。ユーザーが catalog から削除しても、次回起動で **再 materialize してよい**。

### 13.1 配置と読み込み

| 項目 | 契約 |
| --- | --- |
| package path | `harite.gui` の `resources/source_presets/harite-source-presets.json`（[resource_access.py](../../src/harite/gui/resource_access.py) と同型の `importlib.resources`） |
| 改変 | site-packages 内ファイルのユーザー改変・削除は **製品責任外** |
| 版 | アプリ版とともに更新。実行時の preset **再 fetch はしない** |

### 13.2 Preset ファイル schema

user catalog とは **別ファイル**。ルート object:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `preset_schema_version` | integer | ✓ | 現行は **1** |
| `sources` | array | ✓ | テンプレート source の列 |
| `profiles` | array | — | テンプレート profile の列（任意） |

**テンプレート source 要素:**

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `preset_id` | string | ✓ | 安定 ID（import 追跡用）。`[a-z0-9]+(?:-[a-z0-9]+)*` |
| `name` | string | ✓ | import 後の source `name` 初期値（§5.1 上限に従う） |
| `kind` | string | ✓ | `remote-*`（§12.1） |
| `notes` | string | — | import 後の `notes` 初期値 |
| `path` | string | — | **無視**（import 時に cache path を再計算） |
| `min_slideshow_interval_seconds` | integer | — | 当該 source 選択時の slideshow Interval **下限**（秒）。未指定時は下限なし |

**テンプレート profile 要素（任意）:**

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `preset_id` | string | ✓ | profile テンプレート ID |
| `name` | string | ✓ | import 後の profile `name` |
| `members` | object | ✓ | `{ "L": "<source_preset_id> \| null>", "R": "..." }` — 値は **source の `preset_id`**（UUID ではない） |
| `min_slideshow_interval_seconds` | integer | — | profile 選択時の Interval **下限**（秒）。未指定時は members の source preset の下限の **最大値** |

profile import は、参照する source `preset_id` が **同一操作または既存 catalog に存在**することを要求する。

### 13.3 Import API（core）

| 操作 | 契約 |
| --- | --- |
| `load_source_presets()` | preset ファイル → in-memory preset catalog。`preset_schema_version` 未対応は `ValueError` |
| `import_preset_source(user_catalog, preset_id)` | 新 UUID、`path` = `remote_cache_dir(source_id)`、§5 上限・名前一意性を検証。Interval 下限は **preset テンプレート**（`min_slideshow_interval_seconds`）から `harite-preset:` 経由で解決 — `notes` には **書かない** |
| `preset_min_slideshow_interval(preset_catalog, preset_id)` | source / profile テンプレートの下限秒。未定義は `None` |
| `catalog_slideshow_interval_floor(catalog, *, source_id_l, source_id_r, profile_id)` | 現在の combo 選択から適用する Interval 下限秒（`None` は下限なし） |
| `import_preset_profile(user_catalog, preset_id)` | 新 UUID。`members` の preset_id を **新規 import した source id** へ解決（同一 import バッチ内の対応表） |

- GUI は §13.4 `bootstrap_preset_sources` を用いる。
- CLI から `import_preset_*` は **呼び出さない**。

### 13.4 Preset bootstrap（GUI 起動時）

| 操作 | 契約 |
| --- | --- |
| `bootstrap_preset_sources(catalog)` | 同梱 preset の各 `preset_id` について、catalog に **対応 source が無ければ** `import_preset_source` 相当で追加。対応 profile が無ければ `import_preset_profile` 相当で追加（任意 preset） |
| マーカー | preset 由来 source の `notes` に `harite-preset:{preset_id}` と出典のみ。Interval 下限は同梱 preset JSON の `min_slideshow_interval_seconds` を参照（`notes` に `harite-min-interval:` は **書かない**；旧行は repair で除去）。表示名の `*` 接頭辞は **GUI のみ** |
| 永続化 | 変更があれば `save_catalog` してよい |
| Sync | **起動時は行わない**（§12.4）。`bootstrap_preset_sources(..., sync=False)`。画像は Refresh / Start 直前 |

- 同名 `local-dir` が既にあり preset マーカー行が無い場合、`name` にサフィックスを付けて追加してよい。
- preset 由来 source を delete した場合、次回 bootstrap で **再作成してよい**（profile 参照中は §7.5 により delete 拒否）。

## 14. Provider 契約（C-01 段 1a）

実装 module は **`harite.sources.remote`**（ファイル分割可）とする。`harite.sources` から re-export してよい。

### 14.1 登録

| 操作 | 契約 |
| --- | --- |
| `register_remote_provider(kind: str, provider)` | 起動時または module import 時に 1 回。`kind` は §12.1 |
| `get_remote_provider(kind: str)` | 未登録は `KeyError` または `ValueError` |

### 14.2 Provider インタフェース

各 provider は次を実装する。

| メソッド / 属性 | 契約 |
| --- | --- |
| `kind` | 担当 `remote-*` 文字列（登録 key と一致） |
| `sync(catalog, source_id)` | 当該 source に必要な画像を API から取得し cache を **上書き**（§12.3） |
| （任意）`default_notes` | import 時に `notes` が空なら埋める帰属プレースホルダ（文言確定は §15） |

Sync は **idempotent** でよい（同一内容の再取得可）。

### 14.3 Core API 拡張（remote）

| 操作 | 契約 |
| --- | --- |
| `is_remote_kind(kind)` | `kind.startswith("remote-")` かつ §12.1 正規表現 |
| `remote_cache_dir_for_source(source_id)` | `resolve_default_remote_cache_root() / source_id` |
| `add_remote_source(catalog, *, name, kind, notes?)` | UUID 採番、`path` 自動。`kind` 検証・provider 登録確認 |
| `sync_remote_source(catalog, source_id)` | provider に委譲。完了後 catalog の `path` が cache root と一致していること |
| `resolve_source` | **remote も local-dir も** 最終的に `normalize_directory_path(entry.path)`（§7.4 維持） |

`add_source`（既存・`local-dir` 専用）は **`kind` を変更しない**。remote の新規追加は `add_remote_source` または `import_preset_source` のみ。

`update_source` で remote の `kind` 変更は **拒否**。`path` の手動変更は **拒否**（cache 整合のため）。`name` / `notes` のみ更新可。

load / save 時の catalog 検証では、`remote-*` の `path` は **存在しなくても load 可**（resolve / Sync / start 時に失敗）。

## 15. Provider 実装 — 気象庁（C-01 段 1b）

`kind`: **`remote-jma-weather-map`**。API key は用いない。

### 15.1 データ源

| 項目 | URL |
| --- | --- |
| 一覧 | `https://www.jma.go.jp/bosai/weather_map/data/list.json` |
| 画像 | `https://www.jma.go.jp/bosai/weather_map/data/png/{filename}` — `{filename}` は list 要素の文字列 |

`list.json` ルートの category key と preset の対応:

| `preset_id` | list.json パス | ファイル名タグ | 内容 |
| --- | --- | --- | --- |
| `jma-near-color` | `near.now` | `JRcolor` | 日本付近・カラー実況天気図 |
| `jma-asia-color` | `asia.now` | `JRcolor` | アジア域・カラー実況天気図 |
| `jma-near-monochrome` | `near_monochrome.now` | `JRjmahp` | 日本付近・モノクロ実況天気図 |
| `jma-asia-monochrome` | `asia_monochrome.now` | `JRjmahp` | アジア域・モノクロ実況天気図 |

`ft24` / `ft48` および上表以外の list パスは **Sync 対象外**。

### 15.2 Sync 手順

`sync_remote_source`（`harite-preset:{preset_id}` で分岐）:

1. `list.json` を GET（UTF-8 JSON）。
2. 上表の配列から、当該 preset の **ファイル名タグ**（`JRcolor` または `JRjmahp`）を含む要素のみ対象とする。
3. 配列の **最終要素**を `{filename}` とする。空配列は `ValueError`。
4. `https://www.jma.go.jp/bosai/weather_map/data/png/{filename}` を GET（PNG）。
5. cache directory へ **`latest.png` として上書き保存**。当該 directory の他 `*.png` は削除してよい。
6. `default_notes` が未設定で catalog `notes` が空のとき、§15.4 の帰属 1 行目を `notes` に追記してよい。

`list.json` の公式 schema 文書は気象庁から公開されていない。カテゴリ一覧は [JMA weather map list inventory](../../working/finished/20260603-jma-weather-map-list-inventory.md)（別フェーズの選定参考）。

### 15.3 同梱 preset

package: `harite.gui` / `resources/source_presets/harite-source-presets.json`（§13.2）。

| `preset_id` | `name` | `kind` | profile |
| --- | --- | --- | --- |
| `jma-near-color` | `気象庁（日本付近）` | `remote-jma-weather-map` | — |
| `jma-asia-color` | `気象庁（アジア域）` | `remote-jma-weather-map` | — |
| `jma-near-monochrome` | `気象庁（日本付近・モノクロ）` | `remote-jma-weather-map` | — |
| `jma-asia-monochrome` | `気象庁（アジア域・モノクロ）` | `remote-jma-weather-map` | — |
| `jma-dual-lr` | `気象庁 L/R` | — | `members.L` = `jma-near-color`, `members.R` = `jma-asia-color` |

GUI combo 表示は `*{name}`（例: `*気象庁（日本付近）` — [gui-spec §6.5](../gui/harite-gui-spec.md)）。

### 15.4 帰属

**正本の置き場所:** 出典・`harite-preset` マーカーは **`harite-sources.json` の source `notes`** に記載する。Interval 下限は **同梱 preset JSON** の `min_slideshow_interval_seconds`（`harite-preset:` から解決）。Manage 画面でも同内容を表示する。Optimize / Export 画像への EXIF 等の埋め込みは **行わない**（壁紙実体は cache の PNG をそのまま apply する）。

preset `notes` および Manage で表示する出典（公共データ利用規約 第 1.0 版）:

```text
harite-preset:{preset_id}
出典：気象庁ホームページ（https://www.jma.go.jp/）
```

### 15.5 Remote source と slideshow L/R（共通）

すべての `remote-*`（JMA / NDL / CODH 含む）に共通:

| 項目 | 契約 |
| --- | --- |
| 入力形状 | 各 source の cache は **画像 1 枚**（`latest.*`）。§12.5 |
| start 前 | [slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md) — 実行 L/R の全 `remote-*` で sync → resolve → `slideshow_srcdir_*` |
| tick | network 再取得 **しない**。Mode は cache 1 枚の side では **実質無効**（§12.5） |
| 鮮度 | Start 直前 Sync / Manage Refresh のみ |

**気象庁デュアル profile 例:**

| 項目 | 契約 |
| --- | --- |
| 既定 profile | 同梱 `jma-dual-lr` — L = `jma-near-color`、R = `jma-asia-color` |
| Interval 下限 | 同梱 preset の `min_slideshow_interval_seconds`（気象庁: **600**）— [gui-spec §6.5](../gui/harite-gui-spec.md) |

## 15.6 Provider 実装 — NDL 次世代デジタルライブラリー（C-01-E）

`kind`: **`remote-ndl-tsugidigi`**。API key は用いない。

**実装契約の正本は本節。** OpenAPI 調査の背景は [NDL inventory](../../working/finished/20260603-c01-e-ndl-tsugidigi-inventory.md)（**任意** — 本節と矛盾したら本節を優先）。

### 15.6.1 データ源

| 層 | URL / 役割 |
| --- | --- |
| Illustration API | `https://lab.ndl.go.jp/dl/api/illustration/randomwithfacet` — **サーバー側ランダム**（`size=1` 必須） |
| IIIF 画像 | `https://dl.ndl.go.jp/api/iiif/{pid}/{page}/pct:{x},{y},{w},{h}/max/0/default.jpg` |

### 15.6.2 同梱 preset

| `preset_id` | facet タグ（`f-graphictags.tagname`） |
| --- | --- |
| `ndl-random-map` | `graphic_map` |
| `ndl-random-illust` | `graphic_illust` |
| `ndl-random-illustcolor` | `graphic_illustcolor` |
| `ndl-random-indoor` | `picture_indoor` |
| `ndl-random-landmark` | `picture_landmark` |
| `ndl-random-outdoor` | `picture_outdoor` |

plain `/illustration/random`（旧 `ndl-random`）は **同梱しない**。

### 15.6.3 Sync 手順

`harite-preset:{preset_id}` で facet を解決し、次を行う。

1. `GET randomwithfacet?size=1&f-graphictags.tagname={facet}` → JSON 配列 1 件（`Illustration`）。
2. 返却から `pid`, `page`, `x`, `y`, `w`, `h` を読み IIIF URL を組み立てる。
3. IIIF URL を GET し画像 bytes を取得する。
4. §12.3 の共通ヘルパで **`latest.jpg`**（または URL に応じた `latest.png`）として cache へ上書き保存する。

**IIIF 404:** 同一 IIIF URL は **再試行しない**。手順 1 から Illustration API を **再呼び出し**して別候補を試す（最大 **5** 回、試行間の待ち時間なし）。5 回とも失敗なら `ValueError`。

### 15.6.4 候補選択と保持しないもの

| 項目 | 契約 |
| --- | --- |
| ランダムの主体 | **NDL サーバー**（`randomwithfacet`）。Harite はローカルコーパスを持たず、sync ごとに API を 1 回（404 時は再呼び出し） |
| ローカルリスト巡回 | **しない** — cache は常に **1 枚**（§12.5） |
| Illustration メタデータ | IIIF URL 生成に使ったら **永続化しない**（`pid` / 切り出し矩形 / 書誌情報等は cache に残さない） |
| Slideshow Mode | §12.5 — remote のみの side では **実質無効** |

### 15.6.5 帰属

preset `notes` および Manage 表示（`harite-preset:` 行の次行）:

```text
出典：国立国会図書館デジタルコレクション・次世代デジタルライブラリー（https://dl.ndl.go.jp/）
```

## 15.7 Provider 実装 — CODH 江戸 ICP（C-01-E）

`kind`: **`remote-codh-edo`**。Canvas Indexer search API（`https://mp.ex.nii.ac.jp/api/{indexer}/search`）。

**実装契約の正本は本節。** API フィールド調査の背景は [CODH inventory](../../working/finished/20260603-c01-e-codh-icp-inventory.md)（**任意**）。

### 15.7.1 データ源

| indexer | データセット | 用途 |
| --- | --- | --- |
| `edo-spots` | 江戸観光案内 | 観光 preset |
| `edo-shops` | 江戸買物案内 | 買物 preset |

Harite は **Curation JSON 全体や所蔵リストのローカル複製を取得しない**。search API で **1 件ずつ** `canvasThumbnail`（IIIF Image API URL）を取得する。

### 15.7.2 同梱 preset

| `preset_id` | indexer | 検索条件 |
| --- | --- | --- |
| `codh-edo-spots-keyword` | `edo-spots` | `where={codh_keyword}`（部分一致）+ §15.7.3 の random `start` |
| `codh-edo-shops-keyword` | `edo-shops` | 同上 |
| `codh-edo-spots-random` | `edo-spots` | 絞り込みなし + random `start` |
| `codh-edo-shops-random` | `edo-shops` | 同上 |

plain `codh-edo-spots-sakura`（固定 `桜`）は **同梱しない**。

**`codh_keyword`（C-01-E-KW）:** `harite-settings.json` トップレベル。観光・買物 keyword preset **共通**。最大 **16** 文字（`len` 基準）。初期値 **`桜`**。source `notes` / 同梱 preset JSON には **書かない**（旧 `harite-codh-keyword:` 行は起動時 migrate で settings へ移し notes から除去）。

### 15.7.3 Sync 手順（random `start`）

共通クエリ: `select=canvas`, `from=canvas,curation`, `limit=1`。keyword preset は `where={codh_keyword}` を追加。

1. **probe:** `start=0&limit=1` で search を GET → 応答の `total`（件数）を読む。`total < 1` は `ValueError`。
2. **pick:** `start = uniform_random(0 .. total-1)` を生成し、同一条件で再 GET → `results[0]` を 1 件得る。
3. `results[0].canvasThumbnail`（文字列）の `/200,/` を `/max/` に置換した URL を GET する。
4. §12.3 の共通ヘルパで **`latest.jpg`** または **`latest.png`** として cache へ上書き保存する。

**注意:** `limit` 省略は **禁止**（全コーパス JSON を返しうる）。常に `limit=1`。

### 15.7.4 候補選択と保持しないもの

| 項目 | 契約 |
| --- | --- |
| ランダムの主体 | **Harite クライアント**（`total` 取得後の `start` 乱数）。CODH 側の dedicated random API には依存しない |
| ローカルリスト巡回 | **しない** — コーパス全体は download せず、sync ごとに **1 件**だけ取得して `latest.*` に上書き |
| 捨てる応答フィールド | `manifestLabel`, `manifestUrl`, `canvasId`, `fragment`（`xywh`）等 — **画像 URL 生成以外は永続化しない** |
| 帰属の正本 | API 応答ではなく **preset `notes` の固定 URL**（同梱 `harite-source-presets.json`） |
| Slideshow Mode | §12.5 — `start` 乱数は **sync 時（層 A）** のみ。Mode（層 B）は cache 1 枚のため **実質無効** |

### 15.7.5 帰属

江戸観光案内 / 江戸買物案内の各 URL — 同梱 preset JSON の `notes` を正とする。

### 15.7.6 スコープ外

江戸マップ ID・緯度経度・GIS・Curation JSON の自前パース。

## 16. GUI / CLI（C-01）

| surface | 契約 |
| --- | --- |
| **CLI** | 変更なし |
| **GUI** | [gui-spec §6.5](../gui/harite-gui-spec.md) |

## 11. 実装状態

| 層 | C-02 | C-05 | C-01 |
| --- | --- | --- | --- |
| **spec** | #374 | #383 | #388–390 §12–15 |
| **tests (core)** | #375 | — | #392 |
| **impl (core)** | #375 | — | #392 |
| **tests (GUI)** | #378 | #384 | #393 |
| **impl (GUI)** | #378 | #384 | #393 |
| **audit** | [20260601-c02-3layer-audit.md](../../working/finished/20260601-c02-3layer-audit.md) | [20260602-c05-3layer-audit.md](../../working/finished/20260602-c05-3layer-audit.md) | [20260603-c01-3layer-audit.md](../../working/finished/20260603-c01-3layer-audit.md) |

C-01 planning 段 0: #386 / #387。

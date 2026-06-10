# Harite source registry 仕様 (Source Spec)

最終更新: 2026-06-07

## 1. 責務

- slideshow 用 **local directory** を、単発 path ではなく **名前付き source** として登録・一覧・再利用する catalog を定義する。
- **source profile** は L/R 固定 2 スロットに source を割り当てた名前付きプリセットである。
- catalog の永続化、CRUD、参照解決（profile / source id → directory path）を core 層の契約として定義する。
- 外部サイト由来の壁紙候補（remote source）の cache・sync・provider 契約を定義する。

本書が扱わないもの:

- slideshow の tick / cycle **算法**（選択モード・L/R 独立 state 等は [slideshow-spec](../slideshow/harite-slideshow-spec.md)）
- Main タブ input path の registry（ファイラーお気に入りで賄う）
- CLI `harite source` サブコマンド（[cli-spec](../cli/harite-cli-spec.md)）
- plugin registry（[plugin-spec](../plugins/harite-plugin-spec.md)）— OS apply plugin 登録であり、入力 source ではない
- profile / source の **ordered list** 形状、profile 間の周回ローテ

### 1.1 本書の読み方

| 層 | 節 | 内容 |
| --- | --- | --- |
| **本編** | §2–11 | catalog データモデル・path・永続化・core API |
| **本編** | §12–14 | remote source 共通（cache レイアウト・sync タイミング・provider 登録） |
| **付録** | §15 | サイト別の取得手順（本編 §12 から参照する詳細） |
| **付録** | §16 | GUI との接続 |

本書単体で実装・product 判断が完結する。§15 は API 手順の詳細に留め、本編 §12 の契約を補う。

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
| **sync** | provider が外部から画像を取得し cache を更新する操作（§12.4） |

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

### 4.1 `local-dir` path のプラットフォーム注記

マウント済み NAS / 同期 cloud folder は **OS が通常の directory path として見せるもの**を `local-dir` の `path` として登録する。専用 `kind` や SMB クライアント（`smbprotocol` 等）は **採用しない**。

| 環境 | 推奨 path 例 | 契約 |
| --- | --- | --- |
| Windows | `G:\Pictures`、`\\server\share\Photo`（UNC） | Win32 / Pillow が directory として読める path を **そのまま**保存・resolve する |
| Linux | `/mnt/nas/photos` 等の **fstab / mount 済み** path | 通常の `local-dir` として扱う |
| Linux（GVFS） | `/run/user/.../gvfs/smb-share:...`（Thunar picker 等） | **CRUD 拒否はしない**（現状許容）。slideshow 実行の成功は **保証しない**。`/mnt` 等の mount 済み path を **推奨** |

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
- `schema_version` 未対応の将来版を load した場合は `ValueError` とする

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

**slideshow start 前**の流れは [slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md) を参照。tracking key がある side は **start 直前に再 resolve** し、得られた path で `slideshow_srcdir_*` を上書きする。

**自動 migration は行わない** — 既存 `slideshow_srcdir_*` から catalog へ推測 import しない。

### 6.4 settings 上の任意 tracking key

settings には次の **任意 key** を追加してよい（未設定時は無視）。

| key | 意味 |
| --- | --- |
| `slideshow_source_id_l` | 最後に L 側で選んだ source `id` |
| `slideshow_source_id_r` | 最後に R 側で選んだ source `id` |
| `slideshow_profile_id` | 最後に適用した profile `id`（L/R 両方を profile から展開した場合） |

**手動 Srcdir-L/R**（path picker / 直接入力）では、当該 side の tracking key は **空にする**（source UUID を付与しない）。**許容**する。

**実行時の path 正本:**

| 経路 | start 前 | tick 中 |
| --- | --- | --- |
| tracking key **あり** | `resolve_source` / `resolve_profile_members` で `slideshow_srcdir_*` を更新してから画像収集 | **再 resolve しない**。start 時点の path を使用 |
| tracking key **なし**（手動 path のみ） | 既存 `slideshow_srcdir_*` をそのまま検証 | 同上 |
| CLI | 本書の tracking key は **使わない**（都度 `--input`） | — |

tick 毎の catalog 再 load は **行わない**。catalog の読み込みはアプリ起動時および Manage dialog 等の明示操作時のみ。

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

### 7.6 実行中の catalog 変更（GUI）

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

| surface | 契約 |
| --- | --- |
| **core API** | §7 CRUD / resolve、§6.4 実行時 path、§7.6 実行中 catalog 変更 |
| **CLI** | catalog API を直接露出しない（従来どおり `--input` path） |
| **GUI** | registry 選択（[gui-spec §4.2 / §6.3](../gui/harite-gui-spec.md)）、start 前 resolve（[slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md)） |

## 10. 他分冊との境界

- 設定ファイル path 規則の親: [core-spec §6.1](../core/harite-core-spec.md)
- slideshow 実行・directory 検証: [slideshow-spec](../slideshow/harite-slideshow-spec.md)
- GUI Slideshow タブ・remote 操作: [gui-spec §6.5](../gui/harite-gui-spec.md)
- 全体導線: [foundation-spec](../harite-foundation-spec.md)

## 12. Remote source

外部サイトから取得した壁紙候補を **cache-first** で扱う。fetch → ローカル cache directory → `resolve` → slideshow（実行面は `local-dir` と同型の directory 列挙）。

```text
[同梱 preset §13] → 起動時 bootstrap (§13.4) → harite-sources.json (kind=remote-*)
       → Refresh / Start 直前 Sync (§12.4) → cache/{source_id}/
       → 選択 → resolve → slideshow
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

**開発・テスト用 override:** 環境変数 `HARITE_REMOTE_CACHE_ROOT` が非空なら、その path を root として `mkdir(parents=True)` したうえで一貫利用する（pytest は `tests/conftest.py` で `tmp_path` へ向ける）。

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

**Refresh等操作前の directory の掃除:** `prune_orphan_remote_cache_dirs` は `{cache_root}` 直下の subdirectory のうち、**現在の catalog に存在する `remote-*` source の `id` と一致しない名前**の directory を削除する。`cache_root` は（明示引数が無いとき）**catalog 内の remote `path` が単一の親 directory に揃う場合はそれを推定**し、そうでなければ `resolve_default_remote_cache_root()` を用いる。GUI の **catalog materialize**（起動・combo 更新・Manage 保存後の再読込）では、bootstrap 等で catalog が更新された場合は **保存後に** best-effort で prune する。専用の「キャッシュ掃除」ボタンは置かない。

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
| **slideshow tick** | **provider 別**。**JMA**: §15.1.3（`list.json` で filename 比較、変化時のみ PNG GET）。**CODH**: §15.4.5（index + cursor、画像 GET のみ）。**NDL**: §15.3.4（毎 tick `randomwithfacet` → IIIF GET → `latest.jpg` 上書き）。各 tick は cache を再スキャンし `latest.*` を apply |
| **resolve** | `remote-*` は cache directory が無ければ **作成してから** §4 と同型の `normalize_directory_path` を満たす。`local-dir` は既存 directory 必須。空 directory や画像 0 件は **resolve 時には成功しうる**が、slideshow start の画像収集は [slideshow-spec](../slideshow/harite-slideshow-spec.md) で失敗しうる |
| **実行中** | cache 削除・Sync による参照不能 → §7.5 / §7.6 と同型（stop / start failure） |

network エラー・HTTP 4xx/5xx は Sync 時に `ValueError`（またはラップした `OSError` を `ValueError` に変換してよい）。

**tick 毎の network 取得:** **JMA** は §15.1.3。**CODH** は §15.4.5。**NDL** は §15.3.4。

#### 12.4.1 再起動・Refresh・Start — cache が変わる条件（正本）

ユーザーが「毎日アプリを開き直せば絵が変わるか」と読むときの契約。**sync が走らない操作では `latest.*` は前回のまま**残る。

| 操作の組み合わせ | network sync | `latest.*` の中身 |
| --- | --- | --- |
| **アプリ再起動のみ** | **しない**（materialize は `bootstrap_preset_sources(..., sync=False)`） | **変わらない** — 前セッションの cache をそのまま読む |
| 再起動 → **Slideshow Start** | **する**（実行 L/R の全 `remote-*`） | **変わりうる** — 層 A で候補を引き直す（§12.5） |
| 再起動 → Manage **Refresh** → Close | **する**（選択中 remote **1 件**） | 当該 source だけ変わりうる。Slideshow はまだ Start していなければ壁紙 apply は起きない |
| 実行中の **tick** のみ | **JMA**: §15.1.3。**CODH**: §15.4.5。**NDL**: §15.3.4 | **JMA**: filename 更新時に変わりうる。**CODH**: cursor 進行で変わりうる。**NDL**: 毎 tick で変わりうる |
| **Stop** → **Start**（再起動なし） | Start 直前で sync | 変わりうる（再起動 + Start と同型の sync 入口） |

**日常運用の読み方:** 「日々違う絵にしたい」なら **その日の最初の Slideshow Start**（前日 Stop 済み、または起動直後）が自然な入口。**再起動だけでは足りない**。前日と同じ cache を載せたまま Start すれば、sync 後に別候補へ変わりうる（NDL/CODH はランダム再抽選、JMA は list の最新 filename）。

#### 12.4.2 Manage Refresh の product 意味（provider 別）

Refresh はいずれも `sync_remote_source` 1 回だが、**ユーザーにとっての意味は provider で異なる**。

| provider 群 | Refresh が意味すること | 必須か |
| --- | --- | --- |
| **JMA**（`remote-jma-weather-map`） | 気象庁 `list.json` から **最新の実況天気図**を取り直す（コンテンツ自体が時系列で更新される） | 鮮度が要るなら **Start 直前 sync でも足りる**。Refresh は Start 前の明示的プレビュー／手動更新 |
| **NDL** | 母集合は滅多に変わらない前提のまま、サーバー random で **別候補 1 枚**を取得 | 必須ではない。Start 直前 sync でも可 |
| **CODH** | **index 全再構築** + ランダム 1 件の画像化。keyword 変更後は index 無効化に相当 | keyword 変更直後は Refresh または次回 Start |

**Refresh が Start と重複しうる理由（NDL/CODH）:** Start は slideshow 実行の副作用として sync する。Refresh は **slideshow を開始せず**、または **選択中の 1 source だけ** cache を更新したいときの入口。所蔵更新ではなく **表示候補の再抽選**である点は §12.5 層 A と同じ。

**取りづらさの整理:** 所蔵ライブラリの更新を追うための Refresh ではない。アーカイブ系では「もう一度ランダムに引く」操作に近く、**毎日の変化は再起動 + Start** で足りる設計（Start で必ず sync するため）。

#### 12.4.3 Preset remote 操作ログ（開発者向け・MAT-08）

CODH / NDL の実機切り分け用に、Preset `remote-*` の **sync / tick** について JSONL 形式の操作ログを出せる。

| 項目 | 契約 |
| --- | --- |
| 有効化 | 環境変数 `HARITE_SLIDESHOW_OP_LOG` が非空のときのみ記録。未設定時は **no-op**（通常利用への影響なし） |
| 出力先 | ファイル path（追記 JSONL）、または `stderr` / `1` / `true`（logger `harite.slideshow.remote` へ INFO） |
| タイムスタンプ | 各レコードの `ts_jst` は JST（`+09:00` 固定オフセット） |
| 対象 | slideshow **Start 直前 sync**、Manage **Refresh**、**CODH / JMA / NDL tick**、**slideshow tick/apply**（MAT-02b）。手動 `local-dir` のみは対象外 |
| 内容 | `step`（例: `REMOTE_SYNC_BEGIN`, `NDL_META_URL`, `NDL_CACHE_WRITE`, `NDL_TICK`, `CODH_IMAGE_GET`, `CODH_TICK`, `JMA_CACHE_WRITE`, `JMA_TICK`, `SLIDESHOW_TICK`, `SLIDESHOW_APPLY`）、`url`、`preset_id`、`ok`、`error` 等 |
| 画像 outcome（provider 共通） | 要約 tick / cache 行に **`image_fetched`**（network GET 成功）、**`cache_written`**（`latest.*` 書込）、**`had_previous`**（書込前に cache あり）、**`overwritten`**（既存 `latest.*` を置換）、**`content_changed`**（bytes 変化）、**`skip_reason`**（例: `filename_unchanged`） |

実装: `harite.slideshow_op_log.log_slideshow_op`。viper3 観測例: `export HARITE_SLIDESHOW_OP_LOG=~/.cache/harite/slideshow-op.jsonl`。

### 12.5 Remote cache と slideshow Mode（正本）

すべての `remote-*` に共通する契約。サイト別手順は §15。

#### タイムスタンプ（MAT-16）

| 対象 | フィールド | 形式 |
| --- | --- | --- |
| JMA `jma-cycle.json` | `updated_at` | ホスト **ローカル TZ** の ISO8601（オフセット付き、マイクロ秒なし） |
| CODH `codh-cycle.json` | `updated_at` | 同上 |
| CODH `codh-index.json` | `built_at` | 同上 |
| Preset remote 操作ログ（§12.4.3） | `ts_jst` | **JST**（`+09:00` 固定オフセット）— MAT-08 互換 |

実装: cache メタデータは `harite.local_time.local_now_iso`。操作ログは `jst_now_iso`。日本環境ではいずれも JST 表記になる。

#### 設計前提

| 前提 | 契約 |
| --- | --- |
| 所蔵の更新頻度 | 国立機関コレクションは滅多に変わらない想定とする |
| ローカルコーパス | 所蔵リスト全体は cache に持たない。画像バイナリは常に `latest.*` 1 枚 |
| 鮮度 | Start 直前 Sync と Refresh が入口。**JMA / CODH / NDL** は slideshow tick でも §12.4 のとおり更新しうる |

#### cache の slideshow 入力としての意味

- `resolve` 後の remote `path`（`{cache_root}/{source_id}/`）は **`local-dir` と同型**の slideshow 入力 directory（[slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md)）。
- 各 tick で `collect_slideshow_input_images` が directory を再スキャンするが、正常運用では **画像は 1 枚**（`latest.jpg` または `latest.png`）のみ。
- **ローカル所蔵リストの中を sequential / random で回す**方式ではない。

#### 2 層の「選び方」（混同しない）

| 層 | いつ | 何を決めるか | 正本 |
| --- | --- | --- | --- |
| **A. Sync 時の候補選択** | Start 直前・Refresh | リモートコーパス（または keyword 絞り込み後）から **どの 1 キャンバス／図版**を画像化するか | §15.3（NDL）、§15.4（CODH）、§15.1（JMA） |
| **B. Slideshow Mode** | 各 tick | **すでに cache にあるファイル列**から次に apply する path（`sequential` / `random`） | [slideshow-spec](../slideshow/harite-slideshow-spec.md) |

**CODH** は tick 前に層 A（cursor 進行 + 画像 GET）が動くため、cache は 1 枚でも **Slideshow Mode が有効**（仮想 feed）。**NDL** は tick 毎に層 A（`randomwithfacet`）で候補が変わりうるが cache は 1 枚のため **Slideshow Mode は作用しない**。**JMA** は filename 変化時のみ層 A が動き、Mode も作用しない。

#### L/R と Mode

- L / R は独立に `collect_slideshow_input_images` → cycle する。
- Mode は run 全体で 1 つだが、各 side の `images` リスト長に適用される。
- L = CODH・R = `local-dir`（多数）なら R 側だけ従来型 Mode（複数枚 cycle）。L = CODH・R = NDL なら L 側だけ CODH cursor Mode が効く。

#### 絵が変わるタイミング（現行）

| 操作 | 層 A（新しい候補の取得） | 層 B（Mode による切替） |
| --- | --- | --- |
| アプリ **再起動のみ** | **しない**（§12.4.1） | — |
| 再起動 → Slideshow **Start** | 実行 L/R の全 `remote-*` で sync → 候補が変わりうる | 開始 |
| Slideshow **Start**（再起動なし） | 同上 | 開始 |
| Manage **Refresh** | 選択中 remote で sync（Start せず再抽選） | — |
| Slideshow **tick** | **JMA**: §15.1.3。**CODH**: §15.4.5。**NDL**: §15.3.4 | **JMA**: filename 更新時に変化。**CODH**: cursor 進行で変化。**NDL**: 毎 tick で変化しうる |
| Mode を sequential ↔ random に変更 | — | CODH side では **有効**（cursor 進行）。NDL/JMA 1 枚 side では **作用しない** |

## 13. Source preset

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

## 14. Provider 契約

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

## 15. Provider 実装

サイト別の取得手順。本編 §12 の契約を具体化する付録。

### 15.1 気象庁

`kind`: **`remote-jma-weather-map`**。API key は用いない。

#### 15.1.1 データ源

| 項目 | URL |
| --- | --- |
| 一覧 | `https://www.jma.go.jp/bosai/weather_map/data/list.json` |
| 画像 | `https://www.jma.go.jp/bosai/weather_map/data/png/{filename}` — `{filename}` は list 要素の文字列 |

`list.json` の category key と preset の対応:

| `preset_id` | list.json パス | ファイル名タグ | 内容 |
| --- | --- | --- | --- |
| `jma-near-color` | `near.now` | `JRcolor` | 日本付近・カラー実況天気図 |
| `jma-asia-color` | `asia.now` | `JRcolor` | アジア域・カラー実況天気図 |
| `jma-near-monochrome` | `near_monochrome.now` | `JRjmahp` | 日本付近・モノクロ実況天気図 |
| `jma-asia-monochrome` | `asia_monochrome.now` | `JRjmahp` | アジア域・モノクロ実況天気図 |

`ft24` / `ft48` および上表以外の list パスは **Sync 対象外**。

#### 15.1.2 Sync 手順

`sync_remote_source`（`harite-preset:{preset_id}` で分岐）:

1. `list.json` を GET（UTF-8 JSON）。
2. 上表の配列から、当該 preset の **ファイル名タグ**（`JRcolor` または `JRjmahp`）を含む要素のみ対象とする。
3. 配列の **最終要素**を `{filename}` とする。空配列は `ValueError`。
4. `https://www.jma.go.jp/bosai/weather_map/data/png/{filename}` を GET（PNG）。
5. cache directory へ **`latest.png` として上書き保存**。当該 directory の他 `*.png` は削除してよい。
6. `default_notes` が未設定で catalog `notes` が空のとき、§15.4 の帰属 1 行目を `notes` に追記してよい。

Sync 完了後、`{cache_root}/{source_id}/jma-cycle.json` に `preset_id` と選んだ `filename` を保存する。

#### 15.1.3 Slideshow tick sync

slideshow running 中、当該 side が `remote-jma-weather-map` を参照するとき、各 tick 前に次を行う（[slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md)）。

1. §15.1.2 手順 1–3 と同型で `list.json` から現行 `{filename}` を得る。
2. `jma-cycle.json` の `filename` と同一なら PNG GET を **skip** する。
3. 異なるときのみ §15.1.2 手順 4–5 で `latest.png` を上書きし、`jma-cycle.json` を更新する。
4. PNG GET 失敗時は前回 `latest.png` を維持して tick を継続する。

`jma-cycle.json`（最小）: `preset_id`, `filename`, `updated_at`。

#### 15.1.4 同梱 preset

package: `harite.gui` / `resources/source_presets/harite-source-presets.json`（§13.2）。

| `preset_id` | `name` | `kind` | profile |
| --- | --- | --- | --- |
| `jma-near-color` | `気象庁（日本付近）` | `remote-jma-weather-map` | — |
| `jma-asia-color` | `気象庁（アジア域）` | `remote-jma-weather-map` | — |
| `jma-near-monochrome` | `気象庁（日本付近・モノクロ）` | `remote-jma-weather-map` | — |
| `jma-asia-monochrome` | `気象庁（アジア域・モノクロ）` | `remote-jma-weather-map` | — |
| `jma-dual-lr` | `気象庁 L/R` | — | `members.L` = `jma-near-color`, `members.R` = `jma-asia-color` |

GUI combo 表示は `*{name}`（例: `*気象庁（日本付近）` — [gui-spec §6.5](../gui/harite-gui-spec.md)）。

#### 15.1.5 帰属

**正本の置き場所:** 出典・`harite-preset` マーカーは **`harite-sources.json` の source `notes`** に記載する。Interval 下限は **同梱 preset JSON** の `min_slideshow_interval_seconds`（`harite-preset:` から解決）。Manage 画面でも同内容を表示する。Optimize / Export 画像への EXIF 等の埋め込みは **行わない**（壁紙実体は cache の PNG をそのまま apply する）。

preset `notes` および Manage で表示する出典（公共データ利用規約 第 1.0 版）:

```text
harite-preset:{preset_id}
出典：気象庁ホームページ（https://www.jma.go.jp/）
```

### 15.2 Remote source と slideshow L/R（共通）

| 項目 | 契約 |
| --- | --- |
| 入力形状 | 各 source の cache は画像 1 枚（`latest.*`）。§12.5 |
| start 前 | [slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md) — 実行 L/R の全 `remote-*` で sync |
| tick | **JMA**: §15.1.3。**CODH**: §15.4.5。**NDL**: §15.3.4 |
| 鮮度 | Start 直前 Sync / Manage Refresh。JMA は tick 中の filename 更新、NDL は毎 tick で `latest.jpg` が変わりうる |

気象庁デュアル profile: 同梱 `jma-dual-lr`（L = `jma-near-color`、R = `jma-asia-color`）。Interval 下限 **600** 秒 — [gui-spec §6.5](../gui/harite-gui-spec.md)。

### 15.3 NDL 次世代デジタルライブラリー

`kind`: **`remote-ndl-tsugidigi`**。API key は用いない。

#### 15.3.1 データ源

| 層 | URL / 役割 |
| --- | --- |
| Illustration API（facet） | `https://lab.ndl.go.jp/dl/api/illustration/randomwithfacet` — **サーバー側ランダム**（`size=1` 必須） |
| Illustration API（keyword） | `https://lab.ndl.go.jp/dl/api/illustration/searchbytext` — **テキスト類似検索**（`keyword2vec` 必須、`size=1`） |
| IIIF 画像 | `https://dl.ndl.go.jp/api/iiif/{pid}/{page}/pct:{x},{y},{w},{h}/max/0/default.jpg` |

#### 15.3.2 同梱 preset

| `preset_id` | facet タグ（`f-graphictags.tagname`） |
| --- | --- |
| `ndl-random-map` | `graphic_map` |
| `ndl-random-illust` | `graphic_illust` |
| `ndl-random-illustcolor` | `graphic_illustcolor` |
| `ndl-random-indoor` | `picture_indoor` |
| `ndl-random-landmark` | `picture_landmark` |
| `ndl-random-outdoor` | `picture_outdoor` |
| `ndl-search-keyword` | `searchbytext`（`keyword2vec` は settings `ndl_keyword`、既定 `妖怪`） |

plain `/illustration/random`（旧 `ndl-random`）は **同梱しない**。

#### 15.3.3 Sync 手順

`harite-preset:{preset_id}` で入口 API を解決し、次を行う。

1. **facet preset:** `GET randomwithfacet?size=1&f-graphictags.tagname={facet}` → JSON 配列 1 件（`Illustration`）。**keyword preset (`ndl-search-keyword`):** `GET searchbytext?keyword2vec={ndl_keyword}&size=20&from={offset}` → JSON オブジェクトの `list`（`hit` / `from` 付き）。cache に `ndl-search-batch.json`（現バッチ）と `ndl-search-cycle.json`（`from` + `cursor_index`）を保持し、CODH `codh-cycle.json` と同型に **リストを順次巡回**する（MAT-18b）。
2. 返却から `pid`, `page`, `x`, `y`, `w`, `h` を読み IIIF URL を組み立てる。
3. IIIF URL を GET し画像 bytes を取得する。
4. §12.3 の共通ヘルパで **`latest.jpg`**（または URL に応じた `latest.png`）として cache へ上書き保存する。

**IIIF 404 / 400:** 同一 IIIF URL は再試行しない。手順 1 から Illustration API を再呼び出しして別候補を試す（最大 5 回、試行間の待ち時間なし）。5 回とも失敗なら `ValueError`。

Start / Refresh では上記手順を 1 回実行する。

#### 15.3.4 Slideshow tick sync

slideshow running 中、当該 side が `remote-ndl-tsugidigi` を参照するとき、各 tick 前に §15.3.3 の手順 1–4 と同型で **毎回** 入口 API（`randomwithfacet` または `searchbytext`）から新しい図版を取得し `latest.jpg` を上書きする（[slideshow-spec §6.2.1](../slideshow/harite-slideshow-spec.md)）。

1. facet: `GET randomwithfacet?...` → JSON 配列 1 件。keyword: 現バッチの `list[cursor_index]` を IIIF 化。tick 毎に cursor 進行。バッチ末尾で `from` を進めて再取得（`from >= hit` で 0 に wrap）。
2. IIIF URL を組み立てて GET し画像 bytes を取得する。
3. §12.3 の共通ヘルパで `latest.jpg` を上書き保存する。
4. IIIF 404 / 400 時の再試行は §15.3.3 と同型（最大 5 回）。全試行失敗時は前回 `latest.jpg` を維持して tick を継続する（`ndl_slideshow_tick` は `False`）。

op log: 要約 `NDL_TICK`（MAT-08）。詳細は `NDL_META_URL` / `NDL_IIIF_*` / `NDL_CACHE_WRITE`。

#### 15.3.5 候補選択と保持しないもの

| 項目 | 契約 |
| --- | --- |
| 候補の主体 | **facet:** サーバー側ランダム（毎 API 呼び出し）。**keyword:** `searchbytext` の **検索結果リスト**（バッチ取得 + cursor） |
| キーワード設定 | `ndl_keyword`（settings、Manage Presets `keyword(NDL)`、最大 16 文字）— CODH `codh_keyword` と並列 |
| ローカルリスト巡回 | **keyword のみ** — `ndl-search-batch.json` + `ndl-search-cycle.json` で現バッチを順次巡回（画像は常に `latest.*` 1 枚） |
| Manage Refresh | `codh_sync_pick=refresh` と同型 — keyword の `from` / cursor を 0 に戻しバッチ再取得 |
| Illustration メタデータ | IIIF URL 生成に使ったら **永続化しない**（`pid` / 切り出し矩形 / 書誌情報等は cache に残さない） |
| Slideshow Mode | **作用しない** — cache は常に `latest.*` 1 枚のため、`sequential` / `random` 切替で見た目は変わらない（§12.5） |

#### 15.3.6 帰属

preset `notes` および Manage 表示（`harite-preset:` 行の次行）:

```text
出典：国立国会図書館デジタルコレクション・次世代デジタルライブラリー（https://dl.ndl.go.jp/）
```

### 15.4 CODH 江戸 ICP

`kind`: **`remote-codh-edo`**。Canvas Indexer search API（`https://mp.ex.nii.ac.jp/api/{indexer}/search`）。

#### 15.4.1 データ源

| indexer | データセット |
| --- | --- |
| `edo-spots` | 江戸観光案内 |
| `edo-shops` | 江戸買物案内（**同梱 preset なし** — MAT-04。文字図版中心のため product 見送り） |

Curation JSON 全体のローカル複製は持たない。候補 URL は `codh-index.json`（§15.4.3）に集約する。

#### 15.4.2 同梱 preset

| `preset_id` | indexer | 検索条件 |
| --- | --- | --- |
| `codh-edo-spots-keyword` | `edo-spots` | `where={codh_keyword}`（部分一致） |
| `codh-edo-spots-random` | `edo-spots` | 絞り込みなし |

**MAT-04:** `codh-edo-shops-keyword` / `codh-edo-shops-random` は同梱から削除。既存 catalog に残った江戸買物由来 source は sync 非対応（`unsupported CODH preset`）— 手動削除を想定。

固定 keyword preset（例: 固定 `桜`）は同梱しない。

**`codh_keyword`:** `harite-settings.json` トップレベル。`codh-edo-spots-keyword` 用。最大 16 文字。初期値 `桜`。source `notes` / preset JSON には書かない。

#### 15.4.3 候補リスト（`codh-index.json`）

| 項目 | 契約 |
| --- | --- |
| 構築タイミング | Manage Refresh、初回（index 無し）、query 変更後。起動時は disk から読むだけ |
| 手順 | `probe`（`limit=1` → `total`）→ `limit=50` でページング → 各 `canvasThumbnail` を `/200,/` → `/max/` 正規化 |
| 保存先 | `{cache_root}/{source_id}/codh-index.json`（`.tmp` → rename） |
| 中身 | `version`, `query_key`, `total`, `built_at`, `entries[]`（各 `{image_url}`） |

search API 呼び出しで `limit` 省略は禁止。

#### 15.4.4 Start / Refresh sync

| 入口 | 契約 |
| --- | --- |
| Refresh | index 再構築 → リストからランダム 1 件を選び画像 GET → `codh-cycle.json` 更新 |
| Start 直前 | index 無し / `query_key` 不一致時のみ index 構築。cursor 位置の URL を進めずに GET（resume） |

画像 GET 失敗時は `ValueError`（Start / Refresh は失敗）。§12.3 で `latest.*` 上書き。

#### 15.4.5 Slideshow tick sync

running 中、各 tick 前（[slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md)）:

1. `codh-index.json` を読み、`query_key` を確認。
2. Slideshow Mode に従い `codh-cycle.json` の cursor で次の `image_url` を選ぶ。
3. 画像 GET → `latest.*` 上書き。cursor 保存。
4. tick 毎の search API は呼ばない。

画像 GET 失敗時は前回 `latest.*` 維持、tick 継続。

**`codh-cycle.json`（最小）:** `query_key`, `mode`, `index`, `previous_image_url`, `updated_at`。再起動後も cursor 復元。sequential 末尾は先頭へ wrap。`query_key` 不一致時は cursor をリセット。index 再構築で `total` が変わったときは `index %= new_total`。

#### 15.4.6 保持と Mode

| 項目 | 契約 |
| --- | --- |
| ローカル状態 | index（URL のみ）+ cursor。画像バイナリは常に `latest.*` 1 枚 |
| Slideshow Mode | 有効 — CODH side は仮想 feed として cursor 進行（§12.5） |
| 永続化しない応答 | `manifestLabel`, `manifestUrl`, `canvasId`, `fragment` 等 |

#### 15.4.7 帰属

江戸観光案内 / 江戸買物案内の各 URL — 同梱 preset JSON の `notes` を正とする。

#### 15.4.8 スコープ外

江戸マップ ID・緯度経度・GIS・Curation JSON の自前パース。

### 15.8 NDL 江戸切絵図（尾張屋版・MAT-10）

`kind`: **`remote-ndl-kiriezu`**。NDL デジタルコレクション IIIF の **地図1枚全体**（`dl.ndl.go.jp/api/iiif/{pid}/...`）。edo-maps は **pid 索引**のみ（Canvas Indexer 経由ではない）。

#### 15.8.1 同梱 preset（A / B / C）

正本: [CODH 尾張屋版一覧](https://codh.rois.ac.jp/edo-maps/owariya/)（**29 pid**）。キーワード UI なし。interval はユーザー設定（preset floor 600s）。

**A — 全区:** `ndl-kiriezu-all`（29 枚 cursor 巡回）

**B — 大グループ:**

| `preset_id` | 枚数 | 概要 |
| --- | ---: | --- |
| `ndl-kiriezu-group-shitamachi` | 7 | 浅草・深川・本所・向島・下谷・根岸 等 |
| `ndl-kiriezu-group-yamanote` | 10 | 芝・赤坂・麻布・四谷・駒込・巣鴨・新宿 等 |
| `ndl-kiriezu-group-nihonbashi` | 4 | 日本橋・大名小路・番町 |
| `ndl-kiriezu-group-north` | 5 | 外桜田・駿河台・本郷湯島・小石川・音羽 |
| `ndl-kiriezu-group-south` | 3 | 大久保・目黒・小日向 |

**C — 単エリア:** `ndl-kiriezu-asakusa` / `nihonbashi` / `shiba` / `ueno` / `fukagawa` / `honjo` / `yamanote`（各 1〜3 枚。雰囲気固定向け）

カタログ詳細は `sources_remote_ndl_kiriezu.py` の `_KIRIEZU_ALL_MAPS`。

#### 15.8.2 画像 URL

1. `GET .../api/iiif/{pid}/manifest.json` → canvas id（例 `R0000001`）を `ndl-kiriezu-manifest-cache.json` に cache。
2. `GET .../api/iiif/{pid}/{canvas}/full/1200,/0/default.jpg`（幅 **1200px** 固定）。

#### 15.8.3 sync / tick

| 操作 | 契約 |
| --- | --- |
| Manage Refresh | `ndl-kiriezu-cycle.json` を preset 先頭（`cursor_index=0`）へ |
| Start 直前 | cursor 維持（resume）— 現位置の地図を再 GET |
| tick | cursor 進行（preset 内 wrap）→ 次地図を GET |

op log: `NDL_KIRIEZU_PICK` / `NDL_KIRIEZU_TICK`（`pid`, `map_label`, `cursor_index`）。

#### 15.8.4 帰属

preset `notes` 正本: 国立国会図書館デジタルコレクション「江戸切絵図」（尾張屋版）+ CODH 江戸マップ索引 URL。

## 16. GUI / CLI

| surface | 契約 |
| --- | --- |
| **CLI** | remote catalog を直接露出しない |
| **GUI** | [gui-spec §6.5](../gui/harite-gui-spec.md) |

# C-01 — 外部壁紙サイト連携 planning

最終更新: 2026-06-03（**段 0** — open questions **オーナー決定済**）

## 位置づけ

- 親 inventory: [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) §C-01
- 第4波の **本丸**（オーナー発案）。前提: **C-02** + **C-05** **完了**
- ユーザーの `harite-sources.json` の **schema は変更しない**（v1 維持）。remote 用の設定は **同じ source 形状** + 新 `kind` 値で表現

## 用語

| 語 | 意味 |
| --- | --- |
| **user catalog** | ユーザー設定配下の `harite-sources.json`（C-02） |
| **source preset** | 製品同梱の **候補定義**（§11）。user catalog には **自動では書かない** |
| **`local-dir`** | 既存 kind |
| **remote source** | `kind` が `remote-{provider略称}` の source。fetch 後は **cache directory** を `path` に持つ |
| **provider** | サイト別 fetch 実装（NASA APOD 等） |
| **resolve** | C-05 継承 — start 前に id → 実行用 directory `Path`（remote は cache 済み path） |

## ゴール（C-01）

外部 API から壁紙候補を取得し、**既存 registry / profile / slideshow** で使えるようにする。

| 方針 | 内容 |
| --- | --- |
| **cache-first** | fetch → ローカル cache → `resolve` → C-05 slideshow（実行面はほぼ流用） |
| **preset 配布** | サイト定義は **package 内 JSON**（§11）。ユーザーが **自分の catalog に取り込む** |
| **schema 不変** | `harite-sources.json` の `schema_version: 1` とフィールド集合は **そのまま** |
| **第 1 impl** | オーナー選定: **NASA 今日の天文写真（APOD）** — 他サイトは preset 追加で拡張 |

## §11 — Source preset（オーナー決定・本 feature の柱）

製品に **事前登録した source 候補** を同梱する。ユーザーの `harite-sources.json` には **最初から書かない**（削除されやすいため）。

| 項目 | 決定 |
| --- | --- |
| **置き場** | `src/harite/gui/resources/` 配下（[resources README](../../src/harite/gui/resources/README.md) 方針: `importlib.resources` 参照）。例: `source-presets/harite-source-presets.json` または provider 別 JSON |
| **形式** | `harite-sources.json` **近似**（同じ `sources` / `profiles` 構造を **参考にした preset 用ファイル**）。user catalog とは **別ファイル** |
| **Profiles** | preset 内に profile 例を載せてもよいが、**ユーザーの profile に入れるかはユーザ判断** |
| **改変責任** | ユーザーが site-packages 内の同梱ファイルを **書き換え・削除**した場合は **製品責任外** |
| **拡張** | 新サイトは **preset ファイルへエントリ追加** + provider 実装（#10）。user catalog schema 変更は **不要** |

**UX（案）:**

1. Slideshow / Manage から **Preset 一覧**を表示（読み取り専用）
2. ユーザーが **「Add to my sources」** → エントリを **user catalog にコピー**（新 UUID 採番）
3. 以降は通常の C-02 source として Manage / profile / slideshow 連携
4. **Sync** で cache 更新（手動。§4）

```text
[同梱] resources/source-presets/*.json   … 読み取り専用テンプレート
         ↓ ユーザー操作（import）
[user]   harite-sources.json             … schema v1 不変、kind=remote-* を追加
         ↓ Sync
[cache]  OS 別 cache 根（§3）/ {source_id}/
         ↓ resolve（C-05 start 前）
[run]    slideshow / optimize
```

## 現状 inventory（post C-05）

| 層 | 内容 |
| --- | --- |
| **user catalog** | `harite.sources` + Qt Manage（C-02） |
| **slideshow** | start 前 resolve（C-05 #384） |
| **同梱 preset** | **未存在** |
| **remote fetch** | **未存在** |

## C-01 と隣接 feature の境界

```text
C-02 / C-05  … 完了
C-01         … preset 配布 + remote kind + cache + provider（NASA 第1弾）+ GUI import/sync
K-02         … metadata 本格化は対象外
K-05         … 定期 auto-sync は対象外
```

**C-01 に含める:**

- 同梱 preset ファイル + loader（`importlib.resources`）
- `kind` 命名 `remote-{略称}`（#2）
- cache 根の OS 別規則（#3）
- provider: **NASA APOD**（第 1 実装）
- GUI: preset 一覧・import・Sync・既存 combo 連携
- 帰属・ToS 文言（#9、サイトごと）
- Slideshow 用 **アイコン**（#12、Lucide 追加）

**C-01 に含めない（初期）:**

- ユーザー管理 **API key** が必要なサイト（#5）
- **CLI** 拡張（#8）
- **catalog schema_version 2**（#6）
- リッチな **検索ギャラリー**（#7 → 不要寄り）
- **embed 強制マージン**へのライセンス焼き込み（面白いが **議論分かれ・defer**）
- GTK registry / preset UI parity（follow-up）

## オーナー選定 — 第 1 ターゲット候補（#1）

**第 1 実装:** **NASA 今日の天文写真（APOD）** — https://api.nasa.gov/

| 候補（preset / 後続 provider） | メモ |
| --- | --- |
| **NASA APOD** | 第 1 impl |
| **気象庁** 天気図等 | https://www.jma.go.jp/ … [list.json](https://www.jma.go.jp/bosai/weather_map/data/list.json) 等。CC BY 4.0 互換。出典「気象庁ホームページより引用」等。**細かい画像取得・API 組み立ては別途** |
| **NDL** デジタルコレクション API | https://dl.ndl.go.jp/ — 出典メタデータ推奨。別途 |
| **CODH** 江戸マップ API | https://codh.rois.ac.jp/ — CC BY-SA、出展明記・同一ライセンス配布。別途 |

NASA 以外は **preset 定義 + provider 実装**を段階追加（#10）。一括実装はしない。

**API key（#5 との関係）:** オーナー決定は **ユーザーが登録・管理する API key を要するサイトは採用しない**。NASA の公開 DEMO_KEY 等、**実装に固定で埋め込む非秘密パラメータ**がある場合は spec 段で明示（要否は APOD 仕様確認）。

## Open questions — オーナー決定（2026-06-03）

| # | 論点 | 決定 |
| --- | --- | --- |
| **1** | 第 1 ターゲット | **NASA APOD**。他は上表のとおり preset / 後続 provider |
| **2** | `kind` 命名 | **`remote-{provider略称}`**（例: `remote-nasa-apod`） |
| **3** | cache 場所 | **Linux:** `XDG_CACHE_HOME` 配下。**Windows:** Roaming の `harite/` 配下（settings と同系）。不可なら `%USERPROFILE%\Pictures` 等に `harite_cache_dir` — **spec 段で技術確認** |
| **3b** | cache 保持 | fetch 済み・貼り付け中画像を **最小世代分** 保持（初案） |
| **4** | start 前 auto-sync | preset 同梱ファイルは **アプリ版とともに不変**（版アップまで考慮不要）。**user source の sync** は手動（Sync 操作）— stale 自動 poll は初期外 |
| **5** | API key | **ユーザー管理 API key を要するサイトは使わない** |
| **6** | catalog schema | **変更なし**（v1）。preset は **別ファイル**（§11） |
| **7** | GUI 深度 | **説明:** 当初は「Manage 最小 vs 検索プレビュー付きギャラリー」の二択。**結論:** ギャラリーは **初期不要**。preset 一覧 + import + Sync で足りる |
| **8** | CLI | **打ち止め・対象外**（C-02 継続） |
| **9** | 帰属・ToS | **各ターゲットサイトの規約に従う**（出典明記等は provider / GUI 文言で） |
| **10** | 追加サイト | **§11 preset に定義を足す** + provider 追加。user schema 変更なし |
| **11** | Source preset | **上記 §11 確定** |
| **12** | アイコン（Lucide） | **Profile 行:** `bookmark` / `star` / `folder-heart` から選定（spec 段）。**Manage:** `archive`。既存 [resources/icons/lucide/](../../src/harite/gui/resources/icons/lucide/) に SVG 追加 |

## planning で詰める論点（確定済み要約）

### アーキテクチャ — cache-first（維持）

```text
preset（同梱）→ ユーザーが import → user catalog（schema v1）
         → 手動 Sync → cache/{source_id}/
         → resolve → slideshow（C-05）
```

### sync / refresh

| タイミング | 決定 |
| --- | --- |
| **手動 Sync** | 第 1 段階の正本 |
| **start 前 auto-sync** | **しない**（#4） |
| **定期** | K-05 — 対象外 |

### エラー

- sync 失敗 → `ValueError` / status
- cache 空で start → start failure（C-05 同型）
- 実行中 cache 削除 → stop（§7.5）

## 提案フェーズ分割（第4波内・C-01）

| 段 | 内容 | 停止点 |
| --- | --- | --- |
| **0** | 本 planning（本書） | マージ許可 |
| **1** | spec — preset ファイル契約、remote kind、cache 根、NASA APOD provider、帰属 | spec PR |
| **2** | tests — preset load、fetch モック、resolve + slideshow 連携 | tests PR |
| **3** | impl — preset loader、NASA provider、cache、resolve 拡張 | impl PR |
| **4** | GUI — preset import、Sync、icons（#12）、gui-spec | 段階停止 |
| **5** | 3-layer audit | close |

**第 1 完了定義（案）:** NASA APOD preset から import した source で Sync → Slideshow start が Linux/Windows で動作し、帰属文言が spec 通り。

## 3 層比較（段 0 — 未着手）

| 層 | 状態 |
| --- | --- |
| **spec** | 未記載（段 1） |
| **tests** | なし |
| **impl** | なし |

## 次アクション

1. ~~open questions #1–12~~ — **2026-06-03 決定済**
2. **本 planning PR マージ**
3. **spec PR** — preset パス、remote kind、cache、NASA APOD、帰属（JMA/NDL/CODH は preset スタブのみ可）
4. tests + impl → GUI → audit

## 参照

- [C-02](../20260601-1400-c02-source-registry-planning.md) / [C-05](../20260602-1400-c05-slideshow-source-enhancement-planning.md) planning
- [harite-source-spec.md](../specs/source/harite-source-spec.md)
- [gui resources README](../../src/harite/gui/resources/README.md)
- [feature-overview §C-01](20260518-2047-feature-overview.md)

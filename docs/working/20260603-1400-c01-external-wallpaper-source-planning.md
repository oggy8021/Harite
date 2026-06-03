# C-01 — 外部壁紙サイト連携 planning

最終更新: 2026-05-31（**段 2 tests 着手** — core preset/remote + tests PR）

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
| **provider** | サイト別 fetch 実装（気象庁・NDL 等） |
| **resolve** | C-05 継承 — start 前に id → 実行用 directory `Path`（remote は cache 済み path） |

## ゴール（C-01）

外部 API から壁紙候補を取得し、**既存 registry / profile / slideshow** で使えるようにする。

| 方針 | 内容 |
| --- | --- |
| **cache-first** | **都度 API 取得** → cache は **最新 1 枚のステージング**（世代蓄積しない）→ `resolve` → slideshow |
| **preset 配布** | サイト定義は **package 内 JSON**（§11）。ユーザーが **自分の catalog に取り込む** |
| **schema 不変** | `harite-sources.json` の `schema_version: 1` とフィールド集合は **そのまま** |
| **第 1 impl** | **気象庁**（天気図等）。どの画像を取得するか・**左右ディスプレイへの割当**は **段 1b（spec）** でサイト調査のうえ確定 |

## §11 — Source preset（オーナー決定・本 feature の柱）

製品に **事前登録した source 候補** を同梱する。ユーザーの `harite-sources.json` には **最初から書かない**（削除されやすいため）。

| 項目 | 決定 |
| --- | --- |
| **置き場** | `src/harite/gui/resources/` 配下（[resources README](../../src/harite/gui/resources/README.md) 方針: `importlib.resources` 参照）。例: `source-presets/harite-source-presets.json` または provider 別 JSON |
| **形式** | `harite-sources.json` **近似**（同じ `sources` / `profiles` 構造を **参考にした preset 用ファイル**）。user catalog とは **別ファイル** |
| **Profiles** | preset 内に profile 例を載せてもよいが、**ユーザーの profile に入れるかはユーザ判断** |
| **改変責任** | ユーザーが site-packages 内の同梱ファイルを **書き換え・削除**した場合は **製品責任外** |
| **拡張** | 新サイトは **preset ファイルへエントリ追加** + provider 実装（#10）。user catalog schema 変更は **不要** |

**UX:**

1. 起動時 `bootstrap_preset_sources` + preset 由来 `sync_remote_source`（best-effort）
2. Slideshow combo に `*気象庁（日本付近）` 等（[gui-spec §6.5](../specs/gui/harite-gui-spec.md)）
3. 既定 profile `気象庁 L/R` — L=日本付近、R=アジア域（[source-spec §15](../specs/source/harite-source-spec.md)）

```text
[preset] → bootstrap → harite-sources.json
         → Sync（起動 / Refresh / Start 直前）→ cache/{id}/latest.png のみ
         → resolve → slideshow（tick は再 fetch しない）
```

**別フェーズ:** [list.json カタログ](20260603-jma-weather-map-list-inventory.md)（C-01-J）、[他 source 探索](20260518-2047-feature-overview.md)（C-01-E）

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
C-01         … preset 配布 + remote kind + cache + provider（気象庁）+ GUI import/sync
K-02         … metadata 本格化は対象外
K-05         … 定期 auto-sync は対象外
```

**C-01 に含める:**

- 同梱 preset ファイル + loader（`importlib.resources`）
- `kind` 命名 `remote-{略称}`（#2）
- cache 根の OS 別規則（#3）
- provider: **気象庁**（詳細は spec 1b。NASA は対象外）
- GUI: 起動 bootstrap・combo `*…` 表示・既存 combo 連携（専用 Import/Sync ボタンなし）
- 帰属・ToS 文言（#9、サイトごと）
- Slideshow 用 **アイコン**（#12、Lucide 追加）

**C-01 に含めない（初期）:**

- ユーザー管理 **API key** が必要なサイト（#5）
- **CLI** 拡張（#8）
- **catalog schema_version 2**（#6）
- **相手先サイト内検索**・**サムネプレビュー**・検索ギャラリー UI（#7 — **対象外・予定なし**）
- **embed 強制マージン**へのライセンス焼き込み（面白いが **議論分かれ・defer**）
- GTK registry / preset UI parity（follow-up）

## オーナー選定 — 第 1 ターゲット候補（#1）

### 訂正（2026-06-03）— NASA APOD 見送り

NASA APOD（https://api.nasa.gov/）は **API に DEMO key が必要**なため、**第 1 実装から除外**（オーナー判断・調査不足の訂正）。**#5** と整合させ、**実装への API key 埋め込み（DEMO 含む）も行わない**。

**第 1 実装サイト:** **気象庁**（2026-06-03 オーナー指定）。参照: [天気図コメント](https://www.jma.go.jp/jma/kishou/info/coment.html)、[weather_map list.json](https://www.jma.go.jp/bosai/weather_map/data/list.json) 等。CC BY 4.0 互換・出典「気象庁ホームページより引用」等（#9）。

**planning では決めない（段 1b に委任）:**

| 論点 | 段 1b で行うこと | 停止点 |
| --- | --- | --- |
| 取得対象 | list.json / 公開 URL から **どの天気図（種別・時刻帯）を cache するか** | spec PR で提案 → **オーナー確認** |
| 左右割当 | デュアルスライドショー（C-05）と整合する **L/R への画像対応**（同一画像・種別ペア・profile 2 source 等） | 同上 |
| fetch 手順 | キー不要エンドポイント、更新頻度、ファイル名規則、失敗時 | spec に記載 |
| 帰属 | 表示文言・メタデータの置き場（#9） | spec に記載 |

オーナーは **高レベルで気象庁を選ぶ**のみ。細部調査・案作成は **spec 段（1b）の担当**とし、PR レビューで合意する（本リポジトリの通常フロー）。

| 候補（preset / provider） | メモ |
| --- | --- |
| ~~**NASA APOD**~~ | **見送り**（DEMO key 必須） |
| **気象庁** | **第 1 impl** — `kind` 例: `remote-jma-weather-map`（略称は spec 1b で確定） |
| **NDL** / **CODH** | 後続（#10） |

採用サイトは **preset 定義 + provider 実装**を段階追加（#10）。一括実装はしない。

**API key（#5）:** **ユーザー管理の API key も、実装埋め込み（NASA DEMO_KEY 等）も使わない**。キー不要で取得できるエンドポイントのみ対象。

## Open questions — オーナー決定（2026-06-03）

| # | 論点 | 決定 |
| --- | --- | --- |
| **1** | 第 1 ターゲット | **気象庁**。~~NASA APOD~~ 見送り。画像種別・L/R は **1b 調査** |
| **2** | `kind` 命名 | **`remote-{provider略称}`**（例: `remote-jma-weather-map` — 1b で確定） |
| **3** | cache 場所 | **Linux:** `XDG_CACHE_HOME` 配下。**Windows:** Roaming の `harite/` 配下（settings と同系）。不可なら `%USERPROFILE%\Pictures` 等に `harite_cache_dir` — **spec 段で技術確認** |
| **3b** | cache 保持 | **最新 1 枚のみ**（都度上書き。古い天気図は保持しない） |
| **4** | start 前 auto-sync | preset 同梱ファイルは **アプリ版とともに不変**（版アップまで考慮不要）。**user source の sync** は手動（Sync 操作）— stale 自動 poll は初期外 |
| **5** | API key | **一切使わない**（ユーザー管理・DEMO_KEY 埋め込み含む） |
| **6** | catalog schema | **変更なし**（v1）。preset は **別ファイル**（§11） |
| **7** | GUI 深度 | **検索・サムネなし**。combo に **`*…` preset 行** + 起動 bootstrap（**専用 Import/Sync ボタンなし**） |
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
| **0** | 本 planning（本書） | ~~マージ許可~~ **完了**（#386） |
| **1a** | spec — preset 契約、remote kind、cache 根、provider インタフェース | ~~spec PR~~ **完了**（#388） |
| **1b** | spec — 気象庁 §15、オンデマンド cache、preset `min_slideshow_interval_seconds` | ~~spec PR~~ **完了**（#390） |
| **2** | tests — preset load、fetch モック、resolve + slideshow 連携 | tests PR |
| **3** | impl — preset loader、第 1 provider、cache、resolve 拡張 | impl PR |
| **4** | GUI — bootstrap、combo `*…`、Refresh、icons（#12） | 段階停止 |
| **5** | 3-layer audit | close |

**第 1 完了定義（案）:** 気象庁 preset を import → Sync → Slideshow start（単独・デュアル L/R は **1b で定めた割当**どおり）、帰属文言は spec 通り。

## 3 層比較（段 0 — 未着手）

| 層 | 状態 |
| --- | --- |
| **spec** | [harite-source-spec §12–15](../specs/source/harite-source-spec.md)（#388–390） |
| **tests** | なし |
| **impl** | なし |

## 次アクション

1. ~~open questions #1–12~~ — **決定済**（**#1 = 気象庁**）
2. ~~**本 planning PR マージ**~~ — **#386 済**
3. ~~**spec PR 1a**~~ — **#388 済**
4. ~~**spec PR 1b**~~ — **#390 済**
5. **段 2 tests** — preset / sync モック、resolve + slideshow
6. tests + impl → GUI → audit

## 参照

- [C-02](../20260601-1400-c02-source-registry-planning.md) / [C-05](../20260602-1400-c05-slideshow-source-enhancement-planning.md) planning
- [harite-source-spec.md](../specs/source/harite-source-spec.md)
- [gui resources README](../../src/harite/gui/resources/README.md)
- [feature-overview §C-01](20260518-2047-feature-overview.md)

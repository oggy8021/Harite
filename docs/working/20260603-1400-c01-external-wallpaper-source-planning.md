# C-01 — 外部壁紙サイト連携 planning

最終更新: 2026-06-03（**段 0 着手** — open questions 未決）

## 位置づけ

- 親 inventory: [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) §C-01
- 第4波の **本丸**（オーナー発案）。前提: **C-02**（registry）+ **C-05**（slideshow 実行面）**完了**
- `kind` フィールドは C-02/C-05 で **将来拡張用**として温存済み — C-01 で初めて **remote 系 kind** を載せる

## 用語

| 語 | 意味 |
| --- | --- |
| **source** | [harite-source-spec.md](../specs/source/harite-source-spec.md) の catalog エントリ |
| **`local-dir`** | 既存 kind。OS 上の directory path を直接参照 |
| **remote source**（C-01 案） | 外部サイト / API から画像候補を取得し、**ローカル cache directory** へ同期したうえで slideshow / optimize が読む source |
| **provider** | サイト別の取得実装（API client、認証、ページング） |
| **resolve** | C-05 継承 — start 前に id → **実行用 directory path**（remote の場合は **cache 済み directory**） |

## ゴール（C-01 で言う「外部壁紙サイト連携」）

外部サイトや公開 API から壁紙候補を取得し、**既存の source registry / profile / slideshow 経路**で再利用できるようにする。

| 現状（C-05 完了後） | C-01 後（目標イメージ） |
| --- | --- |
| `kind: local-dir` のみ | **`local-dir` + remote 系 kind**（1 種類から開始可） |
| 入力は手動 path / ローカル NAS のみ | **登録済み remote source** を catalog に保存し、profile / Slideshow から選択 |
| slideshow は directory 内画像を列挙 | remote も **最終的には local cache directory** を `resolve` し、C-05 実行面を **そのまま流用** |
| 利用規約・キャッシュなし | **サイトごとの取得規則 + ローカル cache 方針**を spec で固定 |

**product 上の価値:** オーナー用途の「ネット上の壁紙ストックを Harite の slideshow に載せる」。C-05 で固めた NAS/UNC/G: はローカル系として維持し、**インターネット経由の候補源**を足す。

## 現状 inventory（2026-06-03、post C-05）

### 既存基盤（再利用）

| 層 | 内容 |
| --- | --- |
| **catalog** | `harite-sources.json` — `harite.sources` CRUD / resolve |
| **settings tracking** | `slideshow_source_id_l/r`, `slideshow_profile_id` |
| **slideshow 実行** | start 前 resolve（#384）、tick は path のみ、catalog 変更 stop（§7.6） |
| **GUI** | Qt: Manage dialog、Saved source / profile combo（GTK parity は follow-up） |
| **CLI** | `harite source` サブコマンド **なし**（C-02 打ち止め） |

### 未存在

- remote / API 用 **provider** モジュール
- catalog 上の **remote 設定フィールド**（endpoint、query、API key 参照 id 等）
- **cache directory**  layout と sync / refresh API
- サイト別 **利用規約・帰属**の product 記載
- GUI: 検索・プレビュー・「今すぐ同期」等の **remote 専用 UI**

### C-05 / C-02 から引き継ぐ制約

| 決定 | C-01 への影響 |
| --- | --- |
| PyGObject / GVFS で NAS 読む案は **見送り** | remote も **HTTP(S) + ローカル cache** が自然。SMB 直結は `local-dir` のまま |
| `smbprotocol` 等の独自 SMB クライアント **見送り** | 同上 |
| profile **ordered list 非採用** | remote も **フラット catalog + L/R profile** のみ |
| slideshow **tick 毎の catalog 再 load なし** | remote 画像の更新は **明示 refresh** または **start 前 sync** で扱う |
| Main タブ input の registry 化 **対象外** | C-01 は **Slideshow source 系**を主戦場 |

## C-01 と隣接 feature の境界

```text
C-02  registry + profiles     … 完了
C-05  slideshow 実行面        … 完了（local-dir resolve）
C-01  外部サイト / API        … remote kind + cache + provider + GUI（本 planning）
K-02  metadata / history      … 構想保持（C-01 と同時に広げない）
K-05  scheduler               … 構想保持（自動 refresh は別 feature）
```

**C-01 に含める（案）:**

- source-spec 拡張: remote kind、cache path 規則、resolve 契約（cache 必須）
- 新規または分冊: **remote provider 契約**（1 サイト目の API 詳細）
- core: fetch + cache 書き込み + `resolve_source` 拡張
- GUI: remote source 登録・同期トリガー・Slideshow 既存 combo 連携
- tests: provider モック、cache layout、resolve-at-start 連携

**C-01 に含めない（初期）:**

- **複数サイト同時** — 1 provider 完了後に追加（plugin パック型は K-04 構想）
- **K-02** タグ・評価・履歴の本格モデル
- **CLI `harite source sync`** — C-02 打ち止めを **維持する案が default**（open question）
- **GTK parity** — Qt-first（C-02 follow-up と同型）
- **認証 UI の一般化** — 1 サイト目で最小（API key を settings / env のどちらか）

## planning で詰める論点

### 1. 第 1 ターゲットサイト / API

feature-overview: 対象サイト、取得方法、利用規約。

| 観点 | planning 案 |
| --- | --- |
| **第 1 弾** | **1 サイト / 1 公開 API** に限定（完了定義を明確化） |
| **候補** | オーナー指定待ち — 例: Wallhaven 系 API、Unsplash Source、静的 JSON フィード、自作 NAS の HTTP index（`local-dir` で足りるなら対象外） |
| **利用規約** | 各 provider の ToS / 帰属表示を **spec + README** に明記。実装前に **オーナー確認** |

### 2. アーキテクチャ — cache-first（推奨案）

slideshow / Pillow / `collect_slideshow_input_images` は **ローカル file path 前提**（C-05）。よって remote source の **resolve 結果は常に directory path** とする。

```text
[登録] catalog: kind=remote-*, provider_id, query, ...
         ↓
[同期] provider.fetch → cache_dir/{source_id}/ に画像保存
         ↓
[resolve] resolve_source → cache_dir の Path（directory 検証は C-05 同型）
         ↓
[実行] on_slideshow_start 前 resolve → collect_slideshow_input_images（変更最小）
```

| 案 | 内容 | トレードオフ |
| --- | --- | --- |
| **A. cache-first（推奨）** | 上記。C-05 実行面を **ほぼ無変更** | ディスク使用、明示 sync が必要 |
| **B. 毎 tick HTTP** | tick ごとに URL 取得 | slideshow / Pillow 改修大。非採用寄り |
| **C. 一時 download のみ** | start 時だけ全取得 | 毎 start が遅い。A の部分集合 |

**cache 場所（案）:**

| 案 | path |
| --- | --- |
| **A** | `{XDG_CACHE_HOME}/harite/sources/{source_id}/` — 揮発扱い可 |
| **B** | `{ピクチャ}/Harite/sources/{source_id}/` — slideshow 作業 dir と同型の非揮発 |

**初期推奨:** 案 A（cache）。オーナーが「常に残す」要望なら B へ。

### 3. データモデル — `kind` と追加フィールド

| フィールド（案） | 用途 |
| --- | --- |
| `kind` | 例: `"remote-wallhaven"` または `"remote"` + `provider` サブフィールド |
| `provider` | サイト識別子（registry 内 enum） |
| `remote_config` | object — query、category、API key 参照名等（**path は cache 解決後に denormalize 可**） |
| `path` | **同期後**の cache directory 絶対 path（`local-dir` と同型の実行値）または空＋resolve 時生成 |

**schema_version:** `harite-sources.json` を **2** に上げるか、source エントリに **optional `remote`** のみ足し v1 維持か — open question。

### 4. sync / refresh のタイミング

C-05（tick 毎 catalog 再 load なし）と整合:

| タイミング | 案 |
| --- | --- |
| **手動** | Manage dialog または source 詳細の「Sync now」 |
| **start 前** | `resolve` 内で **stale なら同期**（max-age 設定） |
| **scheduled** | K-05 — **C-01 初期外** |

**open:** start 前の自動 sync を **必須**にするか（遅延許容 vs 失敗）。

### 5. 認証・秘密情報

| 案 | 説明 |
| --- | --- |
| **settings** | `harite-settings.json` に `remote_api_keys.{provider}` — GUI settings で編集 |
| **env** | `HARITE_WALLHAVEN_API_KEY` 等 — CI / ヘッドレス向け |
| **catalog 禁止** | API key を `harite-sources.json` に **平文保存しない** |

### 6. GUI スコープ（第 1 段階）

| 含める（案） | 含めない（初期） |
| --- | --- |
| Manage dialog に remote source 追加（provider + 最小 query） | リッチなギャラリー browser |
| Sync ボタン + last_sync / 件数表示 | Main タブへの統合 |
| 既存 Slideshow combo / profile 連携 | GTK parity |
| sync 失敗時の status / `last_error` | 複数 provider 横断検索 |

### 7. エラー・オフライン

| 条件 | 案 |
| --- | --- |
| sync 失敗 | CRUD / sync は `ValueError`。start 前 resolve で cache 空 → **start failure**（C-05 同型） |
| 実行中 cache 削除 | **inaccessible** → stop（§7.5 既存） |
| レート制限 | provider が backoff / user-facing メッセージ |

### 8. CLI

C-02 **打ち止め**を default 維持。remote 追加でも `harite source` サブコマンドは **初期外**（open question）。

## 提案フェーズ分割（第4波内・C-01）

| 段 | 内容 | 正本 | 停止点 |
| --- | --- | --- | --- |
| **0** | 本 planning + オーナー決定（open questions） | working（本書） | マージ許可 |
| **1** | spec — source-spec 拡張 + provider 分冊（1 サイト目） | `source-spec` + `remote-*-spec` 案 | spec PR マージ |
| **2** | tests — provider モック、cache、resolve | tests | tests PR マージ |
| **3** | impl — `harite.sources` 拡張 + 1 provider | src | 段 2 と同梱可 |
| **4** | GUI — Manage + sync + Slideshow 連携 | gui-spec + design slice | 段階停止 |
| **5** | 3-layer audit | `docs/working/finished/` | close |

## Open questions — 未決（オーナー確認待ち）

| # | 論点 | 選択肢 / メモ |
| --- | --- | --- |
| **1** | 第 1 ターゲット | **どのサイト / API から始めるか**（必須） |
| **2** | `kind` 命名 | `"remote"` + `provider` **vs** `"remote-{site}"` 固定 |
| **3** | cache 場所 | **XDG cache** **vs** ピクチャ配下 **vs** catalog `path` にユーザー指定 |
| **4** | start 前 auto-sync | **必須** **vs** 手動 sync のみ **vs** stale 時のみ |
| **5** | API key 保管 | **settings** **vs** **env のみ** **vs** 両方 |
| **6** | catalog schema | **v2** **vs** v1 + optional `remote` object |
| **7** | 第 1 GUI 深度 | Manage 最小 **vs** 検索プレビュー付き |
| **8** | CLI | **打ち止め維持** **vs** `harite source sync` 追加 |
| **9** | 帰属・ToS | 表示義務（ウォーターマーク、クレジット）の要否 |
| **10** | 追加サイト | 第 1 完了後に **同型 provider 追加**でよいか |

## 3 層比較（段 0 — 未着手）

| 層 | 状態 |
| --- | --- |
| **spec** | C-05 まで `local-dir` のみ。remote 未記載 |
| **tests** | なし |
| **impl** | なし |

## 次アクション

1. **本 planning PR** — オーナーが open questions (#1–10) を決定
2. **spec PR**（段 1）
3. **tests + impl**（段 2–3）
4. **GUI**（段 4）
5. **audit close**

## 参照

- [C-02 planning](20260601-1400-c02-source-registry-planning.md) / [audit](finished/20260601-c02-3layer-audit.md)
- [C-05 planning](20260602-1400-c05-slideshow-source-enhancement-planning.md) / [audit](finished/20260602-c05-3layer-audit.md)
- [harite-source-spec.md](../specs/source/harite-source-spec.md)
- [harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md) §6.6
- [feature-overview §C-01](20260518-2047-feature-overview.md)

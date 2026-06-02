# C-05 — slideshow source 強化 planning

最終更新: 2026-06-02（**段 1 spec 着手** — open questions 決定済）

## 位置づけ

- 親 inventory: [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) §C-05
- 第4波の **2 本目**。前提: **C-02 完了**（#373–381, audit: [20260601-c02-3layer-audit.md](finished/20260601-c02-3layer-audit.md)）
- 後続: **C-01**（外部壁紙サイト）— C-05 の source type / 実行面を拡張した上で remote source を載せる

## 用語（C-02 から継承）

| 語 | 意味 |
| --- | --- |
| **Slideshow** | GUI `Slideshow` タブ、interval / tick による壁紙ローテーション（[gui-spec §6](../../specs/gui/harite-gui-spec.md)） |
| **source / profile / catalog** | [harite-source-spec.md](../specs/source/harite-source-spec.md) — `harite-sources.json` |
| **registry 解決** | source id / profile id → 実行用 directory `Path`（`resolve_source` / `resolve_profile_members`） |

## ゴール（C-05 で言う「slideshow source 強化」）

C-02 が **箱と索引**（catalog CRUD + Slideshow からの選択 UI）を届けた。C-05 は **実行面** と **source 種別の扱い** を固め、マウント済み NAS / 同期 cloud folder 等を product として説明可能にする。

| 現状（C-02 完了後） | C-05 後（目標イメージ） |
| --- | --- |
| registry 選択時に path を **一度** `slideshow_srcdir_l/r` へコピー | **slideshow start 前**に id から **再 resolve**（path 陳腐化を start 時点で検知） |
| `kind: local-dir` のみ。GVFS path 等は CRUD を通過しうる | C-05 は **`local-dir` 維持** + path **推奨注記**（`/mnt`・ドライブレター）。GVFS 専用ガードは **必須外** |
| inaccessible path の契約は source-spec §7.5 に記載あるが GUI tick 未統合 | start 前 / tick 中の **中断・status** が spec / tests / impl で一致 |
| slideshow tick / cycle 変更は source-spec で C-05 送り | slideshow-spec に **registry 連動実行** を明文化 |

**feature-overview 原文の「複数 source・source profile」:** C-02 で **L/R 2 スロット profile** は実装済み。**ordered list profile は非採用**（C-02 オーナー決定、変更なし）。C-05 の「複数 source」は **catalog 内の複数登録 + L/R 割当** の実行品質を指す（プレイリスト型ではない）。

## 現状 inventory（2026-06-02、post C-02）

### データ / 永続化

| 場所 | 内容 |
| --- | --- |
| `harite-sources.json` | source 列 + profile 列（`schema_version: 1`） |
| `harite-settings.json` | `slideshow_srcdir_l/r` **と** `slideshow_source_id_l/r` / `slideshow_profile_id` を併存 |
| resolve | 選択・profile 適用時に path を owner へ書き込み。**tick 時は path 文字列のみ参照** |

### コード（実行経路）

- `MainWindow.on_slideshow_start` / `on_slideshow_tick`: `slideshow_srcdir_l/r` → `Path` → `collect_slideshow_input_images`
- registry ID は settings に保存されるが、**実行ループは catalog を再読しない**
- `resolve_source` の inaccessible 検証は **選択時** にのみ効く（path コピー後は stale 化しうる）

### GUI

- Qt: Slideshow source / profile combo + Manage dialog（#378, #381 follow-up 済）
- GTK: registry combo **未実装**（C-02 follow-up として defer）

### 実機観測（C-02 後）

[20260602-c02-real-device-observations.md](finished/20260602-c02-real-device-observations.md)（Linux）:

- Thunar / GVFS 経由 NAS path（`/run/user/.../gvfs/smb-share:...`）が `local-dir` として登録・存在チェック通過しうる
- Slideshow 実行で GLib-GIO-CRITICAL（クラッシュなし）— **低優先だが C-05 で policy 決定が必要**

**オーナー観測（2026-06-02, Windows）:**

- Google Drive を **G: 等のドライブレターにマウント** した path を source / slideshow に使うと **問題なく動作**（registry 登録・実行とも通常の `local-dir` と同様）。
- 示唆: feature-overview の「同期済み cloud folder」は、**OS が通常の directory path として見せるもの**（Windows ドライブレター、Linux の `/mnt/...` 等）は **`local-dir` 一本で足りる**。追加 `kind` や Windows 向け特別扱いは **不要**。
- GVFS transient path 問題は **Linux + ファイルマネージャ経由** に限定。Windows 実機では同型の問題は **未確認**。

**オーナー想定（2026-06-02, XFCE / Linux — 未検証）:**

- NAS も Thunar / GVFS に頼らず、**`/mnt` 等のマウントポイントまで path を直接指定**すれば slideshow source として使える **想定**（実機試行は未実施）。
- 示唆: Linux で問題になるのは **ファイラーが返す GVFS transient path** であり、**fstab / mount 済みの実 path** は Windows ドライブレターと同型の `local-dir` として扱える見込み。

**オーナー観測（2026-06-02, Windows — SMB UNC）:**

- registry に **`\\fortress\share\Photo`** 形式（`harite-sources.json` 上は `\\\\fortress\\share\\Photo`）を登録し、**slideshow は動作**（家の NAS 利用の主経路は Windows 側で足りうる）。
- 示唆: Windows では UNC が **通常の `local-dir` path** として Win32 API / Pillow で読める。C-05 で SMB 専用 kind やクライアントは **不要**。

## C-05 と隣接 feature の境界

```text
C-02  registry + profiles     … 完了（箱・CRUD・Qt 選択 UI）
C-05  slideshow 強化          … 実行面・path 種別・tick 連動（本 planning）
C-01  外部サイト              … remote / API source type（C-05 の type 拡張の上）
```

**C-05 に含める（案）:**

- source-spec 更新: `kind` / path 検証の第 2 段階（mounted / sync の説明、GVFS 方針）
- slideshow-spec 更新: registry ID からの resolve タイミング、inaccessible 時の stop / failure 分類
- core / GUI: **start 前**の resolve、settings の path と id の整合
- tests: resolve-at-start、既存 spec に沿う inaccessible 分類

**C-05 に含めない（C-02 / 他 feature で固定）:**

- profile **ordered list**、profile 間ローテ
- CLI `harite source` サブコマンド（CLI 打ち止め）
- 外部 API / サイト直結（C-01）
- Main タブ input の registry 化
- GTK registry UI parity（C-02 follow-up — C-05 と **並行可** だが必須スコープ外）
- slideshow 作業ディレクトリ R1–R5（既存 slideshow-spec §6.1 — 別 issue 系）

## planning で詰める論点

### 1. source `kind` の第 2 段階

feature-overview: local directory、**同期済み cloud folder**、**ローカル mount 済み** NAS/SMB/WebDAV まで。

| 案 | 内容 | トレードオフ |
| --- | --- | --- |
| **A. `local-dir` 一本化** | 実体はすべて directory path。`notes` や UI ラベルで用途を区別 | モデル単純。GVFS / mount の **検証規則** を path 規則に集約 |
| **B. kind 追加** | 例: `mounted-dir`, `sync-dir` — 検証・help text が kind 別 | C-01 の remote kind 追加と整合しやすい。CRUD / GUI がやや重い |

**オーナー決定（2026-06-02）:**

- `kind` フィールドを設ける理由は **将来拡張性**（C-01 の network / REST API source 等）への備えでよい。
- **C-05 段階**では新 kind は追加せず **`local-dir` のみ**（案 A）。mounted / sync / ドライブレターはすべて `local-dir` の path として扱う。
- オーナー観測（Windows G:）は上記を裏付け。

### 2. path 正規化と GVFS / NAS

| 論点 | 選択肢 |
| --- | --- |
| GVFS path（`/run/user/.../gvfs/...`） | **拒否** / **警告のみで登録可** / **実 mount path へ正規化**（可能な場合） |
| SMB / WebDAV | OS が見せる **ローカル mount path**（`/mnt/...`、Windows ドライブレター）を許可。GVFS は Thunar 等の **transient path** として別扱い |
| Windows cloud sync | **ドライブレター path**（例: `G:\Pictures`）は通常 directory として扱う — **追加検証不要**（オーナー確認済） |
| Linux NAS（想定・未検証） | **`/mnt/...` 等の直接マウント path** は `local-dir` として問題ない見込み。registry 登録は手入力 or path 直接指定が前提（ファイラー picker は GVFS を返しうる） |
| CRUD vs 実行 | 既存 spec に従う（§5 参照）。GVFS 専用 CRUD 拒否は **C-05 必須外** |

**オーナー決定（2026-06-02）:**

- GVFS path を pip 依存で読めるかは **一般論として未確定** — C-05 では **新規 pip / GVFS 専用実装はしない**（マウント一般も珍しい前提）。
- 実機問題は観測メモに残す。product 上は **`/mnt` 等の直接マウント path を推奨**（docs / notes 程度）。Thunar picker 経由の GVFS 登録は **禁止しない**（低優先）。

**オーナー決定（追記 — NAS UX / 技術路線の見直し）:**

- 家に NAS があり UX 上の需要は **ある**（Windows UNC 実機で足りうる）。
- **採用しない:** `smbprotocol` 等の独自 SMB（id/password 管理が増える）。**PyGObject / GIO で GVFS を読む**（Qt 寄せの意味が薄れる）— **両方とも見送り**。
- **C-05 の #2:** **現状許容で確定** — GVFS path の登録は拒否しない。Linux GVFS で slideshow が失敗するケースは観測メモ＋**`/mnt` 直指定を推奨**（doc）。Windows は **UNC・ドライブレター** で `local-dir` としてそのまま使う。
- 将来、Linux GVFS 同等が必須になった場合は **C-01 以降の remote source** や別 feature で再検討（PyGObject 経路は product 方針上 **再採用しない**）。

実機メモ: Linux GVFS — [20260602-c02-real-device-observations.md](finished/20260602-c02-real-device-observations.md) §GVFS。Windows — 本書 §実機観測（G:、UNC）。

### 3. 実行時 resolve のタイミング

| タイミング | 役割 |
| --- | --- |
| **選択時**（現状） | combo / profile 適用 → path + id を owner / settings へ |
| **start 前**（C-05 候補） | id から path を再取得。inaccessible → start failure |
| **各 tick 前** | **catalog 再 load しない**（機会が細かすぎる） |

**オーナー決定（2026-06-02）:** **start 前**に resolve を実施。**tick 毎の catalog 再 load は不要**。catalog の読み込みは **現状どおりアプリ起動時**（および Manage dialog 等の明示操作）で足りる。tick 中の inaccessible は **新規取り決めなし** — 既存 §7.5 / slideshow-spec に従う（§5）。

### 4. settings の path と id の正本

現状は **両方** 永続化。C-05 での整理案:

| 案 | 説明 |
| --- | --- |
| **id 正本** | 実行は常に id → resolve。path は表示・legacy 互換の denormalized cache |
| **path 正本**（現状に近い） | 手動 picker path は id なし。registry 選択のみ id あり |

**オーナー決定（2026-06-02）:** 論点 #4 は **手動 Srcdir-L/R 指定時に source UUID を付与しない** ことの確認。**その理解で正しい。許容**（registry 選択時のみ id、手動 picker は srcdir のみ — C-02 現状維持）。

### 5. inaccessible / 空 directory の振る舞い

source-spec §7.5 / slideshow-spec §9 と揃える:

- **start 前:** start failure（transient 扱いしない）
- **tick 中:** stop / failure（pause 対象か — display loss の pause とは別軸）
**オーナー決定（2026-06-02）:** **特別な新規取り決めは作らない**。source-spec §7.5 / slideshow-spec / core-spec の先行仕様に沿う。

### 6. slideshow tick / cycle ロジック

source-spec が C-05 送りにした項目。C-05 で **必須** とする範囲:

- registry 連動の **入力解決**（cycle 算法そのものの変更は最小）
- dual-source 時の L/R **独立 state** は現行維持（[slideshow-spec §5](../../specs/slideshow/harite-slideshow-spec.md)）

**オーナー決定（2026-06-02）:** start 条件・cycle ロジックは **現段階では変えない**（L/R 両方 path 必須等、現行維持）。

### 7. GUI / owner state

| サブ | 論点 | オーナー決定（2026-06-02） |
| --- | --- | --- |
| **7-1** | C-02 の combo 選択 → source **label** 反映 | **現状維持** — combo で選んだ registry 内容がラベル等に反映される仕様はこのまま（意図の確認: **合っている**） |
| **7-2** | C-05 追加 GUI（kind 別ヒント等） | **現時点では想起なし** — 段 4 は status / start 前 resolve 連動が必要なら最小追記 |
| **7-3** | 実行中の catalog 変更（旧 #9） | **安全側** — **実行に影響する変更**なら **stop**、影響しないなら **続行**。切り分けは spec 段で定義（下表 #9） |

## 提案フェーズ分割（第4波内・C-05）

| 段 | 内容 | 正本 | 停止点 |
| --- | --- | --- | --- |
| **0** | 本 planning + オーナー決定（open questions） | working（本書） | マージ許可 |
| **1** | spec — source-spec §kind/path、slideshow-spec §実行/registry 連動 | `source-spec` + `slideshow-spec` | spec PR マージ |
| **2** | tests — resolve-at-start、inaccessible（既存 spec 準拠） | tests | tests PR マージ |
| **3** | impl — `MainWindow` / slideshow 経路、必要なら `sources.py` 検証 | src | **段 2 PR に同梱可** |
| **4** | GUI — status / 表示のみ必要なら gui-spec 追記 + Qt（GTK parity は follow-up） | gui-spec + design（必要時） | 段階停止 |

CLI 変更なし（C-02 打ち止め継続）。

## Open questions — オーナー決定（2026-06-02）

| # | 論点 | 決定 |
| --- | --- | --- |
| **1** | source `kind` | **`kind` は将来拡張用フィールド**（C-01 の network / REST API 等）。**C-05 は `local-dir` のみ** — 新 kind 追加なし |
| **2** | GVFS / NAS path | **現状許容で確定** — pip / PyGObject / smbprotocol **なし**。Windows **UNC**・ドライブレターは `local-dir` のまま。Linux GVFS 失敗時は doc で `/mnt` 推奨。登録拒否・専用 resolve **しない** |
| **3** | resolve タイミング | **slideshow start 前**に id → path を再 resolve。**tick 毎の catalog 再 load なし**。catalog load は **起動時＋明示操作**（現状維持） |
| **4** | 手動 Srcdir vs UUID | **手動 L/R は source UUID なしで許容**（registry 選択時のみ id）。id + path **併存維持** |
| **5** | tick 中 inaccessible | **新規取り決めなし** — source-spec §7.5 / slideshow-spec 既存に従う |
| **6** | 片側 inaccessible / start 条件 | **現段階では変更なし**（#7 と同型） |
| **7** | start 条件 | **L/R 両方 path 必須など現行維持** |
| **8** | C-05 GUI スコープ | **7-1** combo→label 維持。**7-2** 追加 GUI は現時点なし。GTK parity は C-02 follow-up のまま defer |
| **9** | 実行中 catalog 変更 | **安全側**: 実行中 slideshow が参照する source / profile に **影響する変更** → **stop**；**影響しない**（無関係 source の notes 等）→ **続行**。spec 段で影響判定を列挙（例: 実行中 side の `source_id` の path 変更・削除、当該 profile の member 変更 → stop） |

## 3 層比較（段 0 — 未着手）

| 層 | 状態 |
| --- | --- |
| **spec** | C-05 段 1 — [source-spec](../specs/source/harite-source-spec.md) §4.1, §6.3–6.4, §7.6 / [slideshow-spec](../specs/slideshow/harite-slideshow-spec.md) §6.6 |
| **tests** | C-02 registry / GUI tests あり。**実行時 resolve** の tests なし |
| **impl** | path 直参照の slideshow 経路。GVFS ガードなし |

## 次アクション

1. ~~open questions (#1–9)~~ — **2026-06-02 決定済**
2. ~~**本 planning PR マージ**~~ — #382 済
3. **spec PR**（段 1）— source-spec + slideshow-spec + gui-spec §6.4
4. **tests + impl**（段 2–3）
5. **GUI / gui-spec**（段 4、必要分のみ）
6. **3-layer audit** — `docs/working/finished/YYYYMMDD-c05-3layer-audit.md`

## 参照

- [C-02 planning](20260601-1400-c02-source-registry-planning.md) / [audit](finished/20260601-c02-3layer-audit.md)
- [C-02 実機観測](finished/20260602-c02-real-device-observations.md)
- [harite-source-spec.md](../specs/source/harite-source-spec.md)
- [harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md)
- [feature-overview §C-05](20260518-2047-feature-overview.md)

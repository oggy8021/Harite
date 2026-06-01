# C-05 — slideshow source 強化 planning

最終更新: 2026-06-02（**段 0 着手** — open questions 未決）

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
| registry 選択時に path を **一度** `slideshow_srcdir_l/r` へコピー | start / tick 前に catalog から **再 resolve**（path 陳腐化・NAS 一時切断を検知） |
| `kind: local-dir` のみ。GVFS path 等は CRUD を通過しうる | **path 正規化 / 拒否規則** が mounted / sync 系を spec で説明可能 |
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
- 示唆: Linux で問題になるのは **ファイラーが返す GVFS transient path** であり、**fstab / mount 済みの実 path** は Windows ドライブレターと同型の `local-dir` として扱える見込み。C-05 spec では「推奨: マウントポイント path」「GVFS path は拒否または警告」と整理しうる。

## C-05 と隣接 feature の境界

```text
C-02  registry + profiles     … 完了（箱・CRUD・Qt 選択 UI）
C-05  slideshow 強化          … 実行面・path 種別・tick 連動（本 planning）
C-01  外部サイト              … remote / API source type（C-05 の type 拡張の上）
```

**C-05 に含める（案）:**

- source-spec 更新: `kind` / path 検証の第 2 段階（mounted / sync の説明、GVFS 方針）
- slideshow-spec 更新: registry ID からの resolve タイミング、inaccessible 時の stop / failure 分類
- core / GUI: start・tick 前の resolve、settings の path と id の整合
- tests: resolve-at-tick、NAS 切断相当の failure 分類

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

**初期推奨（planning 案、未決）:** 案 A を default とし、GVFS 拒否等は **path 規則** で扱う。C-01 前に kind 分割が必要なら段 1 spec で B へ切替。

**オーナー観測（Windows, Google Drive → G:）:** ドライブレター mount は現行 `local-dir` で十分 — **案 A を強める根拠**。

### 2. path 正規化と GVFS / NAS

| 論点 | 選択肢 |
| --- | --- |
| GVFS path（`/run/user/.../gvfs/...`） | **拒否** / **警告のみで登録可** / **実 mount path へ正規化**（可能な場合） |
| SMB / WebDAV | OS が見せる **ローカル mount path**（`/mnt/...`、Windows ドライブレター）を許可。GVFS は Thunar 等の **transient path** として別扱い |
| Windows cloud sync | **ドライブレター path**（例: `G:\Pictures`）は通常 directory として扱う — **追加検証不要**（オーナー確認済） |
| Linux NAS（想定・未検証） | **`/mnt/...` 等の直接マウント path** は `local-dir` として問題ない見込み。registry 登録は手入力 or path 直接指定が前提（ファイラー picker は GVFS を返しうる） |
| CRUD vs 実行 | CRUD で拒否 vs CRUD は通し **tick で中断**（現状に近い） |

実機メモ: Linux GVFS — [20260602-c02-real-device-observations.md](finished/20260602-c02-real-device-observations.md) §GVFS。Windows ドライブレター cloud — 本書 §実機観測。

### 3. 実行時 resolve のタイミング

| タイミング | 役割 |
| --- | --- |
| **選択時**（現状） | combo / profile 適用 → path + id を owner / settings へ |
| **start 前**（C-05 候補） | id から path を再取得。inaccessible → start failure |
| **各 tick 前**（C-05 候補） | NAS 一時切断等を検知。source-spec §7.5「実行時中断」と整合 |

**open:** tick 毎の catalog 再 load は **毎回** か、**mtime / 明示 refresh** か。

### 4. settings の path と id の正本

現状は **両方** 永続化。C-05 での整理案:

| 案 | 説明 |
| --- | --- |
| **id 正本** | 実行は常に id → resolve。path は表示・legacy 互換の denormalized cache |
| **path 正本**（現状に近い） | 手動 picker path は id なし。registry 選択のみ id あり |

**open:** 手動 path picker と registry 選択の **混在** を今後も許容するか（C-02 では許容）。

### 5. inaccessible / 空 directory の振る舞い

source-spec §7.5 / slideshow-spec §9 と揃える:

- **start 前:** start failure（transient 扱いしない）
- **tick 中:** stop / failure（pause 対象か — display loss の pause とは別軸）
- **片側のみ inaccessible**（L だけ NAS 切断）: 両方 stop か、可能側のみ継続か

### 6. slideshow tick / cycle ロジック

source-spec が C-05 送りにした項目。C-05 で **必須** とする範囲:

- registry 連動の **入力解決**（cycle 算法そのものの変更は最小）
- dual-source 時の L/R **独立 state** は現行維持（[slideshow-spec §5](../../specs/slideshow/harite-slideshow-spec.md)）

**open:** 空画像 directory・単 side のみ registry 等、start 条件の緩和は **対象外** か（現行: L/R 両方 path 必須）。

### 7. GUI / owner state

- combo 表示: source **name** vs resolved path（現行 label 規則の維持）
- inaccessible 時の status message / `last_error` 文言
- catalog 更新後（Manage dialog Close）の **実行中** slideshow — 次 tick から新 catalog を見るか即 stop か

## 提案フェーズ分割（第4波内・C-05）

| 段 | 内容 | 正本 | 停止点 |
| --- | --- | --- | --- |
| **0** | 本 planning + オーナー決定（open questions） | working（本書） | マージ許可 |
| **1** | spec — source-spec §kind/path、slideshow-spec §実行/registry 連動 | `source-spec` + `slideshow-spec` | spec PR マージ |
| **2** | tests — resolve-at-start/tick、inaccessible、GVFS 拒否（方針決定後） | tests | tests PR マージ |
| **3** | impl — `MainWindow` / slideshow 経路、必要なら `sources.py` 検証 | src | **段 2 PR に同梱可** |
| **4** | GUI — status / 表示のみ必要なら gui-spec 追記 + Qt（GTK parity は follow-up） | gui-spec + design（必要時） | 段階停止 |

CLI 変更なし（C-02 打ち止め継続）。

## Open questions — **未決**（オーナー確認待ち）

| # | 論点 | 選択肢 / メモ |
| --- | --- | --- |
| **1** | source `kind` 第 2 段階 | **A** `local-dir` 一本 + path 規則 **vs** **B** `mounted-dir` / `sync-dir` 追加 — **Windows G: 実機は A で問題なし** |
| **2** | GVFS path（Linux `/run/user/.../gvfs/...`） | **拒否** / **警告付き許可** / **正規化試行** — **Windows 対象外**；**`/mnt` 直マウントは未検証だが local-dir 想定** |
| **3** | resolve タイミング | start のみ **vs** start + **毎 tick** **vs** tick + catalog mtime 監視 |
| **4** | settings 正本 | **id 正本**（path は cache） **vs** 現状の **id + path 併存** |
| **5** | tick 中 inaccessible | **即 stop** **vs** 1 回 retry **vs** 可能 side のみ継続 |
| **6** | 片側 inaccessible | **全体 stop** **vs** 可能 side のみ tick |
| **7** | start 条件 | L/R **両方必須** 維持 **vs** 片側 registry のみ許可 |
| **8** | C-05 GUI スコープ | status / error のみ **vs** kind 別 picker ヒント **vs** GTK registry parity を同梱 |
| **9** | catalog 変更と実行中 slideshow | 次 tick 反映 **vs** 即 stop **vs** 実行中は catalog スナップショット |

## 3 層比較（段 0 — 未着手）

| 層 | 状態 |
| --- | --- |
| **spec** | C-02 正本のみ。tick/registry 連動は **未記載**（送り先: 本 feature） |
| **tests** | C-02 registry / GUI tests あり。**実行時 resolve** の tests なし |
| **impl** | path 直参照の slideshow 経路。GVFS ガードなし |

## 次アクション

1. **本 planning PR** — オーナーが open questions (#1–9) を決定
2. **spec PR**（段 1）— source-spec + slideshow-spec 更新
3. **tests + impl**（段 2–3）
4. **GUI / gui-spec**（段 4、必要分のみ）
5. **3-layer audit** — `docs/working/finished/YYYYMMDD-c05-3layer-audit.md`

## 参照

- [C-02 planning](20260601-1400-c02-source-registry-planning.md) / [audit](finished/20260601-c02-3layer-audit.md)
- [C-02 実機観測](finished/20260602-c02-real-device-observations.md)
- [harite-source-spec.md](../specs/source/harite-source-spec.md)
- [harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md)
- [feature-overview §C-05](20260518-2047-feature-overview.md)

# two-screen / resolution / l-display / r-display — 整理メモ

最終更新: 2026-06-12  
**従属文書** — 親 planning: [20260611-1200-cli-v2-roadmap.md](20260611-1200-cli-v2-roadmap.md)（MAT-21 の設計入力）  
文脈: v2.0.0 前の整理ブランチ（`docs/pre-bump-v2.0.0-planning`）上で、CLI 総点検中にオーナー（原作者）と整理した内容。  
正本: [harite-core-spec.md §3](../specs/core/harite-core-spec.md#3-入力解決と表示コンテキスト)、[harite-cli-spec.md §4](../specs/cli/harite-cli-spec.md)

**ステータス:** §6 オーナー判断は **確定**（2026-06-12）。**MAT-21 前半**（2枚＝dual 必須・半分キャンバス廃止）は実装済み。**MAT-21 後半**（四重露出の撤去・名称是正）は §6 に従い spec 改定 → 実装へ。

---

## 1. 一行結論

**母体では WorkSpace 検出が幾何の正で、2枚入力＝dual は暗黙。** Harite は同じ情報を `two_screen` / `resolution` / `l_display` / `r_display` に **分解して CLI に露出**したため、原作者モデルから見ると **重複した混乱要素** になっている。CLI 総点検では **これらのフラグは通常スキップ** でよい（検出と入力枚数だけ見る）。**§6 確定後:** ユーザー向け露出は **全面撤去** し、検出＋入力枚数（1:1）だけが製品面に残る。

---

## 2. 母体（wallpaperoptimizer）のモデル

| 概念 | 母体での扱い |
| --- | --- |
| **WorkSpace** | マシン上のモニタ幾何を検出する **唯一の正** |
| **lScreen / rScreen** | WorkSpace から得た左右モニタ矩形（配置・収納判定・merge の基準） |
| **合成全体** | WorkSpace + 2枚バインドから **暗黙**（`_mergeWallpaper`、右画像は `lScreen.width` オフセット） |
| **2画面か否か** | **ユーザーが選ばない**。L/R に画像2枚 → dual 一択に近い |
| **CLI 相当** | `--two-screen` / `--l-display` / `--r-display` のような **独立ノブは無い** |

参照: [MAT-01b ドラフト](design/20260609-mat-01b-native-placement-repair-draft.md)、[MAT-15 監査](finished/20260609-mat-15-core-geometry-audit.md) §1.1（母体 `Core.py` 再読）

---

## 3. Harite のモデル（分解と露出）

Harite は再実装時に内部で必要だった分解を、そのまま設定・CLI 面に載せた。

| 母体（暗黙） | Harite（明示） | 主な実装 |
| --- | --- | --- |
| WorkSpace → lScreen / rScreen | `l_display` / `r_display` | `workspace.detect_displays()` → `build_two_screen_optimize_context()` |
| WorkSpace からの合成面 | `resolution` | `derive_virtual_resolution()`（two-screen 時は仮想デスクトップ外接矩形） |
| 2枚＝dual | `two_screen`（`auto` / on / off） | `resolve_optimize_display_settings()` |
| 検出モジュール名 | `src/harite/workspace.py` | **検出のみ**。母体の WorkSpace 全体（バインド・合成）ではない |

### 3.1 各パラメータの実態（用語の注意）

| パラメータ | Harite での意味 | **ではない** もの |
| --- | --- | --- |
| **`resolution`** | optimize が描く **合成キャンバス全体のピクセルサイズ**（出力 JPEG の作業解像度） | Windows 設定の「論理解像度」、タスクバー除きの利用可能領域 |
| **`l_display` / `r_display`** | 各モニタの **いま有効なピクセル寸法**（分割比率・スロット高さの根拠） | 「論理最大解像度」。パネル最大対応解像度一覧でもない |
| **`two_screen`** | 上記幾何モードを使うかの **明示フラグ**（未指定時は auto） | 母体にあった独立オプションではない |

**OS 別の検出:**

- **Windows:** `EnumDisplayMonitors` の `rcMonitor` = **physical pixel**（150% DPI 設定でも物理解像度）。`scale_percent` は取るが **resolution / l/r 解決には使わない**（core-spec §3.3）。
- **Linux:** `xrandr --query` の `connected` 行の **現在モード**（例 `1920x1080+1920+0`）。

### 3.2 two-screen ON 時の3つの関係（自動補完）

例: 左 1920×1080、右 1920×1080、横並び

- `l_display` = `1920x1080`
- `r_display` = `1920x1080`
- `resolution` = `3840x1080`（仮想デスクトップ外接）

`core.py` の `_resolve_display_slots` は `left_w : right_w` で `split_x` を決め、L margins `(ml,0,mt,mb)` / R `(0,mr,mt,mb)` を使う。

---

## 4. 混乱の本体（オーナー観点）

### 4.1 `two_screen` フラグ

- **母体:** 画像枚数（L/R の埋まり）で実質決まる。
- **Harite:** 2枚でも `two_screen=OFF` 可能 → **1キャンバスを半分ずつ** の第3経路。
- **オーナー判断:** この経路は **余計・嫌**（意図したユースケースではない）。2枚なら dual に寄せたい。

`two_screen=OFF` + 2枚になり得る状況:

1. Settings / 設定 JSON で `two_screen: false`（または off）を明示
2. CLI で `--no-two-screen`
3. **auto** だがモニタ検出が2台未満（context `None` → OFF に戻る → 半分ずつ）

### 4.2 `resolution` と `l/r-display` の三重露出

母体では **WorkSpace 一括** だった幾何が、Harite では **3〜4 個の名前** で重複表示されている。`workspace.py` という名前も母体 WorkSpace の **一部（検出だけ）** を指し、責務分割と名前の残りがさらに紛らわしい。

### 4.3 関連だが別レイヤの概念

- **Apply** の Span / Auto-Split / No Split（`apply_surface.margin_settings_split_label`）は **壁紙の貼り方**。optimize の `two_screen` とは別。
- **Slideshow dual-source** は `build_two_screen_optimize_context()` 必須（検出2台）。

---

## 5. CLI 総点検 — 実務ガイド

> **移行期（MAT-21 前半〜後半）:** 現行 CLI には §4 の四重露出が残る。§5 は総点検用の暫定ガイド。**MAT-21 後半完了後は本節の「触らない」前提が製品仕様になる**（§6）。

### 5.1 通常は触らない

| フラグ | 総点検での扱い |
| --- | --- |
| `--two-screen` / `--no-two-screen` | **スキップ可**（未指定 = auto） |
| `--l-display` / `--r-display` | **スキップ可**（検出に任せる） |
| `--resolution` / `-r` | **スキップ可**（検出 or 設定ファイル） |

確認すべきは **入力枚数** と **検出が効いているか**（出力の分割比率、`posit` が left/right か、ログ）。

### 5.2 設定ファイルだけ注意

`--settings-file` に `"two_screen": false` や `"off"` が入っていると、2枚でも明示 OFF になる。GUI 保存 JSON を CLI に流用している場合は要確認。

### 5.3 CLI と spec の既知ギャップ（参考）

[specs-checking](finished/20260530-1509-specs-checking-from-cursor.md) CLI1: Typer の `--two-screen` デフォルト `False` と、未指定時 auto 扱いの説明が読み手を混乱させやすい。実動は `resolve_bool_or_auto_option` が CLI 未指定なら `None`（auto）を返す経路。

---

## 6. 将来整理の方向（オーナー判断・確定 2026-06-12）

母体（WorkSpace + 入力枚数）に寄せる **製品方針**。MAT-21 後半の spec 改定・実装の正とする。

### 6.1 画像枚数とディスプレイ枚数 — 常に 1:1

| 原則 | 内容 |
| --- | --- |
| **1:1** | 入力画像枚数と扱うディスプレイ枚数は **常に一致** させる（L/R 各1枚）。 |
| **最大2台** | Harite が扱うのは **最大2ディスプレイ**（ordered 先頭2件）。3台以上は製品対象外（3台目以降は無視）。トレーダー向け多画面構成は想定しない。 |
| **非サポート** | **1 ディスプレイに複数枚**（tile 等で並べる）は **Harite サポート外**。tile 系は複雑化の割に価値が薄い。 |
| **代替** | 並べたいなら **1 枚を適正倍率で貼る**（fit / 余白）に留める。 |
| **Slideshow** | tick 単位で L/R 各1枚 — 1:1 と矛盾しない（連続運用の話）。 |

→ 半分キャンバス第3経路廃止（MAT-21 前半）と整合。3枚以上の等分スプリットも製品ストーリー外。

### 6.2 `two_screen` — 露出全面撤去

| 層 | 方針 |
| --- | --- |
| **内部** | 実装都合で必要なら **内部フラグ** として残してよい。不要と判明すれば **コードからも除去** 可。 |
| **UI / CLI** | **露出しない**（ユーザーが選ばない）。 |
| **設定ファイル** | `two_screen` / `two_screen_mode`（auto/on/off）を **設定からも廃止**。 |
| **embed 等** | `embed-info` 出力への `two_screen=1` 等、**あらゆる露出をやめる**。 |

枚数 + WorkSpace 検出だけで dual か否かが決まる（§2 母体モデル）。

### 6.3 `l_display` / `r_display` — 上級者 override、廃止も検討

| 方針 | 内容 |
| --- | --- |
| **格下げ** | CLI / GUI / 設定 JSON からは **見えない上級者 override** に落とす（残す場合）。 |
| **疑問** | デスクトップアプリ利用者に、**自動検出に頼らず手動で l/r を指定しなければならない用事はそもそも無いのでは？** |
| **点検** | 上記が成立すれば **いっそ廃止** する。MAT-21 後半で use-case 洗い出し → spec で廃止 or 隠蔽を確定。 |

検出が正のときは `build_two_screen_optimize_context()` が暗黙で補完（§3.2）。

### 6.4 合成キャンバスサイズ（旧 `resolution`）— 名称是正と `xx%`

**問題:** 「論理解像度」「各モニタ寸法」と混同しやすい名前のまま CLI に露出している（§4.2）。

**狙い:** メモリ・速度・品質のトレードオフ。検出された **virtual desktop 外接矩形**（左右をつないだ合成空間）より **小さい作業解像度** で JPEG を作り、Apply の auto-split が実ディスプレイへ比率分割して貼る。

**`xx%` の意味（確定 2026-06-12）:**

| 項目 | 方針 |
| --- | --- |
| **基準** | 検出 virtual desktop の **幅・高さそれぞれ** に対する比率（例: 75% → `round(virtual_w×0.75) × round(virtual_h×0.75)`）。幅と高さは同じ考え方。 |
| **margins** | 半ば **額縁** として壁紙の一部。旧 `resolution` が指す合成キャンバスは **margins を内包した出力全体**（margins はキャンバス外の別レイヤではない）。 |
| **対象外** | 512×256 等の極小ディスプレイ — Harite 自体が起動できるウィンドウサイズを持たないため製品対象外。 |

**非対称デュアル（オーナー経験・確定）:**

- 右が小さいサブディスプレイ等は **想定内**（昔の自身の構成）。
- 現行 optimize はスロット高さを `l_display[1]` / `r_display[1]` で切り、**上辺揃え**（`origin_y = 0`）で生成する。下辺揃えもあり得るが、OS 配置の検出・対応は困難なため **採用しない**。
- `split_x`（下記）は幅比分割に使う。高さ差はスロット `screen_h` で表現し、短い側は下に余白（背景色）が残る。

**`split_x` とは（用語整理）:**

| 段階 | 役割 |
| --- | --- |
| **Optimize 合成**（`core._resolve_display_slots`） | 作業キャンバス幅 `w_target` 上で、左右モニタ幅比 `left_w : right_w` から縦境界 `split_x` を決め、左画像は `x ∈ [0, split_x)`、右画像は `x = split_x + …` に paste する。**Auto-split の前段**。 |
| **Apply auto-split**（`core.split_composite_for_displays`） | 完成 JPEG を各 `Display` の offset/幅比で **横クロップ** し、各モニタ解像度へ fit する。**別経路** — virtual 全体に対する正規化比率で切るため、小さい合成 JPEG でも実レイアウト比が保たれる。 |
| **GUI preview** | optimize 合成と同型の `split_x` で左右プレビュー矩形を切る（gui-spec §6）。 |

→ §6.4 の `xx%` は **Optimize 段の作業キャンバス縮小** に効く。`split_x` は縮小後の `w_target` 上で再計算される（l/r 幅比は検出のまま）。

| 項目 | 方針 |
| --- | --- |
| **名称** | 正本・UI では **合成キャンバスサイズ**（作業解像度）。ユーザー向けラベルは `resolution` を避ける。 |
| **露出** | `xx%` を第一手段に。`WxH` 直接指定は上級者 override に格下げ（または廃止）。 |
| **設定ファイル** | 平文 `resolution` キーは `canvas_scale_percent` 等へ置換検討（後半 spec）。 |

### 6.5 embed / Placement 略称の正規化（別フェーズ）

§6.2 で `two_screen=1` 等の embed 露出は撤去する。**併せて正規化したいが、MAT-21 後半と同梱必須ではない**（MAT-20 後半または専用フェーズ可）。

| 現行略称 | 出所 | 正規化の方向（案） |
| --- | --- | --- |
| `posit=` | CLI `Placement:` 行、`PlacementResult.posit` | `monitor=left\|right` または `slot=` 等、母体用語に寄せる |
| `res=` | embed params 行 | `canvas=` または §6.4 の新名称 |
| `align=` / `inputs=` | embed params 行 | 露出縮小とセットで見直し（params モード自体の整理） |
| `embed-info` / `embed_info` | CLI・設定キー名 | MAT-20 後半の rename と連動 |

正規化時は **CLI stdout・embed 焼き込み・settings キー・GUI ラベル** を一括で spec 改定する（破壊的変更は v2.0.0 にまとめる）。

### 6.6 後半 spec 改定で触れる追加論点（提案）

| 論点 | 提案 |
| --- | --- |
| **検出失敗時** | 2枚入力 + display `< 2` はエラーのみ（前半どおり）。手動 l/r override は **廃止** し、§6.3 の点検を「廃止で確定」に寄せる。 |
| **Settings 移行** | `two_screen` / `resolution` キー削除時、旧 JSON を読んだら無視 + ログ1行（サイレント落としでよい）。 |
| **GUI `_sync_two_screen_state`** | 露出撤去後は **入力枚数変更時に resolution/l/r を検出から再同期** するだけに縮小。TwoScreen Off コントロール廃止。 |
| **3台環境の UX** | エラーにしない（先頭2台のみ使用）。help / GUI に「最大2台」と明記。 |
| **`xx%` 既定** | 100%（検出 virtual と同サイズ）を default。未指定＝フルサイズ合成。 |
| **§6.5 略称正規化** | MAT-21 後半と **並行可・同梱不要**。MAT-20 後半（embed リネーム）完了後の方が依存が少ない。 |

### 6.7 MAT-21 実装フェーズ対応表

| フェーズ | 内容 | 状態 |
| --- | --- | --- |
| **前半** | 2枚＝dual 必須、半分キャンバス廃止、2枚+検出1台→エラー | **実装済み**（`optimize_settings`, `core`, spec §3.1, tests） |
| **後半** | §6.2–6.4: 四重露出撤去、Settings TwoScreen Off 廃止、`xx%` spec、用語是正 | **未着手**（v2.0.0 同梱想定） |
| **別フェーズ** | §6.5: embed / Placement 略称正規化（`posit` 等） | **未着手**（MAT-20 後半連動可） |

**横断着手の入口:** [20260611-1200-cli-v2-roadmap.md](20260611-1200-cli-v2-roadmap.md)（MAT-21）。

---

## 7. コード・正本への索引

|  topic | 場所 |
| --- | --- |
| 表示解決 | `src/harite/optimize_settings.py` — `resolve_optimize_display_settings` |
| two-screen context | `src/harite/display_context.py` — `build_two_screen_optimize_context` |
| 検出 | `src/harite/workspace.py` — `detect_displays` |
| スロット分割 | `src/harite/core.py` — `_resolve_display_slots` |
| CLI 入口 | `src/harite/cli.py` — `optimize` の `--two-screen`, `--l-display`, `--r-display`, `--resolution` |
| GUI 自動同期 | `src/harite/gui/views/main_window.py` — `_sync_two_screen_state` |
| Settings 三値 | `src/harite/settings.py` — `two_screen_mode`（auto/on/off） |

---

## 8. 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-11 | 初版（CLI 総点検中のオーナー対応を markdown 化） |
| 2026-06-11 | ステータス追記 — core 等の基底変更は先送り、他話題と横断整理予定 |
| 2026-06-11 | 親 roadmap リンク — MAT-21 設計入力として従属化 |
| 2026-06-12 | §6 オーナー判断確定（1:1 原則、two_screen 露出撤去、l/r 格下げ/廃止検討、resolution 名称・xx% 案） |
| 2026-06-12 | ステータス更新 — MAT-21 前半実装済み、後半は §6 に従う |
| 2026-06-12 | §6.1 最大2台、§6.4 非対称デュアル・margins・virtual %・split_x 整理、§6.5 embed 略称正規化（別フェーズ） |

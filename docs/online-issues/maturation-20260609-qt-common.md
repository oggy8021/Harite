# 熟成運転ログ — Qt / 共通（2026-06-09〜）

GitHub Issue 起票前の観測転記。

- 親: [20260609 feature-overview](../working/20260609-1200-feature-overview.md)
- 対象: **Qt 版**および **backend 共通**（GTK 専用は [GTK 熟成メモ](../working/20260609-1200-feature-overview.md#熟成運転メモxfce-実機) 参照）
- **転記（中間整理 2026-05-31）:** 改修系・確かさ向上・**MAT-11** まで **完了**（#442〜#452）。
- **機能要望（2026-06-09）:** **MAT-04**（#455）、**MAT-09**（#456）**完了**。Post Main Merge CI 緑（run 27195018405）。
- **v2.0.0 backlog（2026-05-31）:** **MAT-13**（#458）〜**MAT-16**（#461）**完了**。**MAT-17** 実装中（CLI slideshow + `--settings-file`）。次: **Q-01**。
- **熟成運転:** 2026-06-09 **打ち切り**（継続には改修が先決）。
- **製品線:** `v1.9.0` は熟成運転の **中間マイルストーン**。本 stream の営みは **`v2.0.0` を目指す**（Qt 一本化・remote source の確かさ・製品線の再定義）。詳細は下記 [v2.0.0 への再整理](#v200-への再整理オーナー方針-2026-06-09)。

## v2.0.0 への再整理（オーナー方針 2026-06-09）

熟成運転の過程で **先送り** したものと **閃いた** ものを改めて並べる。骨格は **Q-01** — GTK を **メンテ対象外** に落とす（回収コスト観点）。**例: `v2.0.0` を GTK 同梱の最終版とする** 等は planning で確定。**MAT-10** は完全新規 source 調査のため、下記の **後** で十分。

**GTK 熟成メモ:** [overview §Xfce](../working/20260609-1200-feature-overview.md#熟成運転メモxfce-実機) は **削除しない**（観測記録として残す）。GTK への parity 拡張・改修は行わない。

### 完了（v1.9.0 マイルストーン）

| 区分 | ID | PR |
| --- | --- | --- |
| 改修系 | MAT-01, 01b, 02, 03, 05, 06, 07 | #442〜#449 |
| 確かさ向上 | MAT-08, 12 | #450, #451 |
| 機能要望 | MAT-04, 09, 11 | #455, #456, #452 |
| infra | CI docs-only skip 等 | #453 |

### 完了（v2.0.0 向け・MAT-13〜16）

| 区分 | ID | PR |
| --- | --- | --- |
| polish | MAT-13 | #458 |
| 機能要望 | MAT-14 | #459 |
| 確かさ向上 | MAT-15, 16 | #460, #461 |

### 先送り（v2.0.0 までに再棚卸）

| ID | 要約 | 先送り理由 / 次の詰め |
| --- | --- | --- |
| **MAT-02b** | NDL / CODH slideshow **tick / apply 不安定** | MAT-08 viper3 で JMA のみ安定。**実装中** `fix/mat-02b-slideshow-stability` |
| **MAT-08 観測** | Preset slideshow JSONL 操作ログの **実機切り分け** | v0 実装済（#450）。viper3 途中結果: **JMA のみ安定**、NDL/CODH は tick 不発・未反映あり（[観測メモ](../working/20260609-mat-08-viper3-slideshow-op-observation.md)）→ MAT-02b 前提 |
| **Q-01** | GTK を **メンテ対象外** に落とす → Qt 一本化 | **v2.0.0 の骨格** — 例: v2.0.0 を GTK 同梱の最終版とする。entrypoint / CI / packaging / docs の削除範囲を planning で確定 |

### 残 backlog（v2.0.0 向け）

| ID | 要約 | 区分 |
| --- | --- | --- |
| **MAT-17** | **CLI slideshow** でも設定ファイルを読む | planning（CLI） |
| **MAT-10** | 江戸切絵図 / edo-maps 雰囲気 source（完全新規） | 機能要望・**後回し** |

### おおよその次の流れ（オーナー確定 2026-06-09）

1. ~~**MAT-13 → 14 → 15 → 16**~~ **完了**（#458〜#461）→ **MAT-17** — v2.0.0 向け backlog を順に片づけ（下記 § 参照）
   - **並行 / 前提:** MAT-02b + MAT-08 観測（viper3 途中結果転記済み。apply 層は未）
2. **Q-01** — GTK をメンテ対象外に落とす（例: v2.0.0 を最終同梱版）。**MAT-10 より先**
3. **MAT-10** — 完全新規 source 調査（**最後**）

## 着手順（オーナー方針・熟成運転中の区分）

着手・Issue 化の **おおよその優先**（確定順ではない）:

1. **改修系** — 明らかな不具合・期待とのズレ
2. **確かさ向上** — 観測・仕様の明確化（直す前に切り分けたいもの）
3. **機能要望系** — 新規 UX / source / product 判断

| 区分 | ID |
| --- | --- |
| 改修系 | MAT-01, MAT-01b, MAT-02, MAT-03, MAT-05, MAT-06, MAT-07 |
| 確かさ向上（完了） | MAT-08, MAT-12, MAT-15, MAT-16 |
| 確かさ向上（観測途中） | MAT-08 観測 |
| 機能要望系（完了） | MAT-04, MAT-09, MAT-11, MAT-14 |
| 機能要望系（未着手） | MAT-10 |
| polish（完了） | MAT-13 |
| CLI（未着手） | MAT-17 |
| 改修系（実装中） | MAT-02b |
| 先送り（v2.0.0 再棚卸） | Q-01 |

※ MAT-02b は [v2.0.0 への再整理](#v200-への再整理オーナー方針-2026-06-09) 参照。MAT-10 の具体 URL は例示のみ（[MAT-10](#mat-10--江戸切絵図を雰囲気絵ソースにできないか検討)）。MAT-13〜17 は [v2.0.0 向け採番](#mat-13--エラーメッセージを赤色で表示したい) 参照。

---

## MAT-01 — Main direction toggle（xxAlign）が効かない

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Qt: Main direction toggles (xxAlign) have no visible effect`

### 事象

- Main タブの十字 direction toggle（`Top-*` / `Bottom-*` / `Left-*` / `Right-*`）で **上寄せなどが発生しない**（期待どおり画像位置が変わらない）。
- `margins=0,0,0,0` にしても効果が出ない。
- embed（margin text）の有無は **関係しない** と観測。
- `Top Align` / `Bottom Align` も **弱い／おそらく効いていない**。

### 分類

- `bug`（Qt / 共通 optimize パイプラインの疑い）
- `investigation`

### 関連

- 正本: [harite-gui-spec.md §3 Main](../specs/gui/harite-gui-spec.md)（direction toggle 十字配置）
- 実装候補: `src/harite/gui/views/main_window.py`、`optimize` / `positioning` 周辺

### 取り込み方針

- **完了** — #442 マージ。実機で align 体感 OK（オーナー確認 2026-06-09）。
- スコープ: direction toggle → `form_state.align` / `valign` への反映

### 調査メモ

- memo（オーナー）: margin ゼロ・embed 無関係で再現
- **原因（2026-06-09）:** Qt `QtSignalBackend._on_direction_toggled` が GTK と異なり `on_toggle_position(widget_name, active)` の **`active` 引数を渡していなかった**（`TypeError` または state 未更新）。解除時の `on_toggle_position_reset` も未呼び出し。
- **修正:** GTK 実装に合わせ `active` 渡し + 非 active 時 reset。テスト: `tests/gui/test_qt_signal_wiring.py`
- **関連:** 出力で align が見えない主因の一つは **MAT-01b**（core upscale）。handler 修正だけでは不十分。

---

## MAT-01b — Optimize が小画像を拡大し align 座標系が母体と乖離

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `core: restore native-size placement and display-rect align (parent parity)`
- 改修方針ドラフト: [20260609-mat-01b-native-placement-repair-draft.md](../working/design/20260609-mat-01b-native-placement-repair-draft.md)

### 事象

- 解像度領域に **小さい画像** を載せると、**引き伸ばし（拡大）** されて配置される。
- xxAlign / x 寄せの体感が悪い（toggle しても Optimize 結果が変わらない、または拡大で余白が消える）。
- オーナー認識: Optimize に **無理な拡大は含めない**。原寸志向であったが Harite 現行はそうなっていない。

### 分類

- `bug`（core / 共通 optimize 幾何の **母体からの回帰**）
- `investigation` → **照合完了**（2026-06-09）

### 母体照合（`C:\Users\oggy_\Develop\Repos\wallpaperoptimizer`）

| 観点 | 母体 | Harite 現行 |
| --- | --- | --- |
| 小画像 | `containsPlusMergin` 通過 → **原寸** | `_scale_to_fit` で **拡大** |
| resize | 収まらないときのみ `_downsizeImg`（**縮小のみ**） | **毎回** fit（`scale` 上限なし） |
| align 座標系 | 各 `lScreen` / `rScreen` **全矩形**（初期 left/top） | margins 差引き **cell 内余白** |
| two-screen margins | L `(L,0,T,B)` / R `(0,R,T,B)` | 左右とも同一 `(ml,mr,mt,mb)` で cell 計算 |
| paste | 右画像 `x += lScreen.width` | split_x + cell offset |

**結論:** オーナー記憶は **正しい**。reformation 以降の Harite core が母体基底から逸脱している。

### 関連

- MAT-01（#442）— handler 層。本件と **併せて** 初めて align 体感が戻る。
- 母体: `WallpaperOptimizer/Core.py` — `_checkContain`, `_downsizeImg`, `_allocateImg`, `_mergeWallpaper`
- Harite: `src/harite/core.py` — `_scale_to_fit`, `optimize_wallpapers`
- spec: [harite-core-spec.md §4.1](../specs/core/harite-core-spec.md)（現行は upscale 前提で **要改訂**）
- `scaling` 設定無効は **合意済み** — 本件スコープ外

### 取り込み方針

- **完了** — #444 マージ。実機で align 体感 OK（オーナー確認 2026-06-09）。
- 詳細: [改修方針ドラフト](../working/design/20260609-mat-01b-native-placement-repair-draft.md)

### 調査メモ

- memo（オーナー）: 「悲劇」— 母体は原寸・拡大なし。align は display 内限界寄せ / margins は収納・縮小制約。
- **修正（2026-06-09）:** `core.py` — `_resolve_native_dimensions`, `_allocate_on_display`, `_resolve_display_slots`。spec §4.1 更新。テスト反転。
- GUI 注釈 `margins define area; align/valign act inside it` は **旧 Harite 実装向け**。gui-spec 整合は follow-up。
- **実機（オーナー・Windows）:** Preset ソースで顕著。**真の価値・見え方に戻った**（誤 upscale 時代のプロダクト誤解を解消）。天気図など **小画像は原寸のまま中央にポツン** — align では動かせない（余白があるから可能；画像が小さいと center 既定のまま）。→ **MAT-11**（Slideshow でも Optimize）と強く結びつく。
- **製品線:** 高解像度向け **意図的 2x / 4x** は [MAT-14](#mat-14--2x--4x-display-scale意図的拡大)（MAT-01b の拡大禁止とは別軸）。

---

## MAT-02 — Slideshow タブ `(stopped)` と footer `running` の不一致

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Qt: Slideshow tab title (stopped) vs footer summary (running) mismatch`

### 事象

- Slideshow **タブ見出し**は `Slideshow (stopped)`。
- **右下 footer**（`lblSlideshowSummary` 相当）は `Slideshow: running`。
- このとき **Start 無効・Stop 有効** — widget 状態は「running」側に寄っているが、タブ表示と不一致。
- ただし **壁紙は切り替わっていない**。
- Error 表示は `none`。
- **NDL / CODH 取得問題**の可能性あり → **別事象として後送**（本件からは切り離して記録）。

### 分類

- `bug`（状態表示の整合）
- `investigation`（slideshow state machine / label refresh）

### 関連

- MAT-02b（未記録）: NDL/CODH 取得 — 後からオーナー伝達予定
- 正本: [harite-gui-spec.md §3 Slideshow](../specs/gui/harite-gui-spec.md)、[harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md)
- 実装候補: `refresh_slideshow_summary_label`、`slideshow_tab_title`、`_slideshow_running` 同期

### 取り込み方針

- **完了** — #445 マージ。実機でタブ / footer 整合 OK（オーナー確認 2026-06-09）。
- スコープ: **表示整合のみ**（タブ title / footer / Start-Stop enable）。tick 失敗・remote sync は MAT-02b へ

### 調査メモ

- memo（オーナー）: 壁紙未切替・Error none だが Stop 有効。取得系は別枠
- **原因（2026-06-09）:** Qt は footer のみ更新。`QTabWidget.setTabText` と `lblSlideshowTabTitle` が初期 `Slideshow (stopped)` のまま。GTK `refresh_slideshow_summary_label` は両方を `Slideshow ({state})` に同期。
- **修正:** `qt_widget_helpers.refresh_slideshow_summary_label` — stopped/running/paused を GTK 同型で footer + tab に反映。spec: gui-spec §3 footer / notebook 同期。

---

## MAT-02b — NDL / CODH slideshow 取得・壁紙更新の不安定

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09（MAT-08 観測後に着手）
- 仮タイトル: `Fix NDL/CODH slideshow tick stability and wallpaper apply on Linux`

### 事象

- MAT-02 は **表示整合のみ** 完了（#445）。**壁紙が切り替わらない** / **期待 tick が来ない** は本項目。
- [MAT-08 viper3 観測](../working/20260609-mat-08-viper3-slideshow-op-observation.md): **JMA のみ安定**。NDL / CODH は JSONL GET 成功でも実機未反映・tick 不発あり。

### 分類

- `bug`（slideshow tick / apply / UI state）
- `investigation`（remote sync 後パイプライン）

### 関連

- MAT-02（#445 — 表示のみ）、MAT-08（#450 + viper3 観測）、MAT-11（#452 — Optimize 経路）
- [20260609-mat-02b-slideshow-remote-stability.md](../working/20260609-mat-02b-slideshow-remote-stability.md)

### 取り込み方針

- 実装（`fix/mat-02b-slideshow-stability`）:
  - `— none —` 選択時に `slideshow_srcdir_*` もクリア（gui-spec §4.2 更新）
  - op log に `SLIDESHOW_TICK` / `SLIDESHOW_APPLY` を追加（MAT-08 観測の切り分け強化）
  - Linux `LinuxPlugin.apply` — 同一 path 再適用前に `touch`（XFCE 等の再描画促進）
- **未着手（follow-up）:** NDL sync-on-tick（product）、tick apply 失敗時の pause 継続方針

### 調査メモ

- viper3: R `--none--` で path 残存 → dual 幽霊 R。CODH 20:37 `CODH_TICK` OK だが壁紙未更新 → apply / DE キャッシュ疑い
- NDL は設計上 tick で新規取得しない — 「新しい図版毎 10 分」は別 feature

---

## MAT-03 — Optimize で Color が効かない

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Qt: background Color not applied on Optimize`

### 事象

- **Optimize** 実行時に **Color**（背景色設定）が効かない。

### 分類

- `bug`

### 関連

- 正本: [harite-gui-spec.md](../specs/gui/harite-gui-spec.md)（Color dialog / optimize フロー）
- 実装候補: `on_optimize`、背景色の form_state / CLI 引数渡し

### 取り込み方針

- **完了** — 実機で preview + Apply → Optimize 反映 OK（オーナー確認）。
- スコープ: Color dialog → `on_set_color` → Optimize の `background_color` 反映（core パイプラインは正常）

### 調査メモ

- memo（オーナー）: Optimize 時 Color 無効
- **原因（2026-06-09）:** `open_dialog()` が `QColorDialog.getColor` を直呼び（header Color 押下で手動 editor + Apply を経由しない）。`get_pending_color()` が内部 `_pending_color` のみ参照し entry 編集を無視（GTK は entry 読取）。`pick_color` 未実装で Pick も `open_dialog` へ誤配線。
- **修正:** `open_dialog` → show（GTK 同型）、`pick_color` 追加、entry 読取、`qt_backend._on_color_pick_clicked` 修正。Qt picker host は preview 面 + `Pick Color`（embedded `QColorDialog` は Windows で別窓 `Select Color` 重複のため不採用）。spec: [harite-gui-spec.md §3.1](../specs/gui/harite-gui-spec.md)。テスト: `test_qt_dialogs.py`, `test_qt_signal_wiring.py`
- **実機（オーナー・Windows）:** preview 表示・Apply 書き戻し OK。

---

## MAT-04 — 江戸買物案内 preset をやめる（不具合ではない）

### 管理情報

- GitHub: **未起票**（product / catalog 判断）
- 記録日: 2026-06-09
- 仮タイトル: `Source catalog: drop CODH 江戸買物案内 presets (text-heavy)`

### 事象

- **江戸買物案内**（CODH `edo-shops`）は **文字図版ばかり**で slideshow 用途に合わない。
- **不具合ではない** — 提供内容の product 判断で **やめる**。

### 分類

- `planning`（source catalog / preset 整理）
- 不具合 **ではない**

### 関連

- [C-01-E 統合索引](../working/finished/20260603-c01-e-merged-inventory.md)
- 同梱 preset: `src/harite/gui/resources/source_presets/harite-source-presets.json`（`codh-edo-shops-keyword` / `codh-edo-shops-random`）
- spec: [harite-source-spec.md §CODH edo-shops](../specs/source/harite-source-spec.md)

### 取り込み方針

- **改修着手** — 同梱 preset から `codh-edo-shops-keyword` / `codh-edo-shops-random` を削除。江戸**観光**（`edo-spots`）は維持。
- スコープ: 江戸**買物**のみ。CLI / remote indexer 実装の `edo-shops` API 経路はコードに残すが **同梱・sync マップからは外す**。
- 既存 catalog: 江戸買物由来 source が残っている場合は sync 非対応（手動削除想定）。`slideshow_source_id_*` は catalog 上の source_id を指すため、source 削除まで有効。

### 調査メモ

- memo（オーナー）: 文字図版中心のため採用見送り
- **実装:** `harite-source-presets.json`、`sources_remote.py`（`CODH_KEYWORD_PRESET_IDS` / `_CODH_PRESET_SEARCH`）、source-spec §15.4、gui-spec keyword 行。テスト: `test_c01_source_presets`（MAT-04 削除検証）
- **完了** — #455 マージ（2026-06-09）。Post Main Merge CI 緑。

---

## MAT-05 — CODH キーワード: Close しないと確定されない

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `CODH keyword field reverts until Manage dialog Close`

### 事象

- Manage sources 内の **CODH キーワード入力**で、**Close でダイアログを閉じないと**文字列が確定できない。
- **Enter** や **入力フォーカスの移動**だけでは、編集内容が破棄され **元の値（例: `桜`）に戻る**。
- 期待: ダイアログを閉じる前でも、メモリ上の同値は **フォーム内の最新状態**に沿う。**Close 等による確定までは最新状態を保つ**べき。

### 分類

- `bug`（Qt / 共通 — dialog 確定タイミング）
- `polish`

### 関連

- [C-01-E-KW planning](../working/finished/20260605-c01-e-kw-codh-keyword-planning.md)（#413 完了）
- 正本: [harite-gui-spec.md](../specs/gui/harite-gui-spec.md)（Manage / CODH keyword 行）
- 実装候補: Manage dialog、`codh_keyword` の load/save タイミング

### 取り込み方針

- **完了** — #447 マージ。実機でドラフト保持 OK（オーナー確認）。
- スコープ: keyword フィールドの **編集中ドラフト保持**（Enter / focus-out / 選択変更で revert しない）。disk 反映は従来どおり Close / Refresh

### 調査メモ

- memo（オーナー）: Enter・フォーカス移動で `桜` に戻る。Close 必須
- **原因（2026-06-09）:** `codh_keyword` は settings 全体で 1 値だが、選択 sync が毎回 persisted 値で field を上書き。リスト `currentRowChanged` はフォーカス移動・Enter 後にも発火しうる。
- **修正:** `sync_manage_dialog_keyword_field` — enabled のみ更新。spec: gui-spec Manage dialog `keyword(CODH)`。テスト: `test_qt_source_registry_dialog.py`

---

## MAT-06 — CODH キーワード: Xfce + Qt で日本語入力不可

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Qt on Xfce: IME unavailable in CODH keyword field`
- 環境: **Qt 版**、**XFCE 実機のみ**（他 DE / Windows は未確認）

### 事象

- CODH キーワード入力欄で **日本語文字列が入力できない**。
- **Ctrl + Space** 等で IME を起動できない。

### 分類

- `bug`（Qt / platform — IME）
- `investigation`

### 関連

- MAT-05（同一 surface、別症状）
- 実装候補: Qt `QLineEdit` / dialog IME 属性、Xfce fcitx/ibus 連携

### 取り込み方針

- **完了（マージ待ち）** — #448。実機 OK（viper3: keyword IME + SVG アイコン + 静かな起動）。
- スコープ: `prepare_qt_input_method_env`（`QT_IM_MODULE` 補完、distro PyQt6 は `QT_PLUGIN_PATH`、pip PyQt6 は fcitx 非互換 warning）、`configure_text_input_widget`、`qt_svg_support`、`requirements-linux-qt.txt`。Linux Qt は **distro PyQt6 + fcitx5-frontend-qt6 + python3-pyqt6.qtsvg** を正本とする。

### 調査メモ

- memo（オーナー）: Xfce のみ。Ctrl+Space 無効
- **仮説（2026-06-09）:** pip PyQt6 の `platforminputcontexts` に ibus のみで fcitx 欠落。`GTK_IM_MODULE=fcitx5` でも `QT_IM_MODULE` 未設定だと Qt が IM に繋がらない。Manage dialog の keyword は日本語入力の主導線のため同 surface で顕在化。
- **実機（オーナー・viper3 / Xfce / Linux Mint 22.3 Zena）:** mozc（fcitx 内）。env 整合・Firefox OK。`fcitx5-frontend-qt6` 導入済み。**`QT_DEBUG_PLUGINS=1` で確定:** distro fcitx プラグインは pip PyQt6 と `Qt_6_PRIVATE_API` **非互換**。**回避:** apt `python3-pyqt6` + `--system-site-packages` venv → **keyword 欄 IME 成功**（オーナー確認）。**副作用:** 全 SVG アイコン非表示（`QPixmap::scaled: Pixmap is a null pixmap`）— distro PyQt6 は **QtSvg 別パッケージ**（`python3-pyqt6.qtsvg`）が要る。Harite #448: pip fcitx symlink 廃止、起動時 warning、`qt_svg_support` 追加。
- **修正:** `qt_input_method.py`、`qt_svg_support.py`、`requirements.txt` / `requirements-linux-qt.txt`。spec: gui-spec Linux Qt 前提。テスト: `test_qt_input_method.py`、`test_qt_svg_support.py`
- **実機最終（オーナー）:** distro venv + apt 3 パッケージで IME・アイコン・起動 warning 解消。CI 後 #448 マージ予定。

---

## MAT-07 — embed Text: 2・3 行目で Enter が先頭行へジャンプ

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Margin embed Text: Enter on line 2/3 jumps cursor to line 1`

### 事象

- **embed pattern: Text**（margin text 自由入力）で **2 行目・3 行目**を入力中に **Enter** を押すと、カーソルが **先頭行**に移ってしまう。
- 結果として複数行入力がしづらい。

### 分類

- `bug`（Qt / 共通 — margin text widget）
- `polish`

### 関連

- 正本: [harite-gui-spec.md §8 margin text](../specs/gui/harite-gui-spec.md)
- 実装候補: `txtMarginText` / `QTextEdit` の key-press ハンドラ、`max_lines` 制約

### 取り込み方針

- **改修着手** — Qt: `textChanged` 後の owner sync が同一 plain text を `setPlainText` し直し、カーソルが先頭へ戻る（GTK は key-press guard あり、Qt は stub）。
- スコープ: `set_entry_text` の no-op 同値更新、Qt Enter ガード（5 行 cap）、`read_margin_text_widget_text` の `QPlainTextEdit` 対応

### 調査メモ

- memo（オーナー）: 2・3 行目 Enter で先頭行へジャンプ
- **原因（2026-06-09）:** `_on_margin_text_changed` → `_sync_margins_state_with_feedback_from_owner` → `setPlainText(embed_text)` が毎 Enter で走りカーソルリセット。Qt `_on_margin_text_key_press` は未配線。
- **修正:** `qt_margin_text.py`、`set_entry_text` 同値スキップ、spec 追記。テスト: `test_qt_margin_text.py`
- **実機（オーナー）:** Enter・IME 変換確定とも体感 OK。#449 マージ済み。

---

## MAT-08 — Preset 系 Slideshow の動作ログ（CODH / NDL 観測用）

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Feature: Preset slideshow operation log for remote source diagnosis`

### 事象 / 要望

- **実質機能要望** — 現状このログがないと **CODH / NDL の観測が十分にできない**（熟成運転・MAT-02 系の切り分けにも必要）。
- **Preset 界隈**を対象にした Slideshow について、**動作ログを採る**仕組みが欲しい。

### ログに含めたい内容（オーナー指定）

1. **画像取得までのシーケンス**に沿ったステップ記録
2. **URL 組み立ての過程**（中間 URL / クエリ / 解決結果）
3. **アクセス日時（JST）**
4. **取得したい情報が取れたか / 取れなかったか**（成否・理由の要約）

### 分類

- `planning`（観測・診断 infrastructure）
- `investigation`（remote sync / preset slideshow の実機検証支援）
- 不具合報告 **ではない** — **機能要望**

### 関連

- MAT-02 / MAT-02b（NDL・CODH 取得 — 後送予定）
- [C-01-F remote sync](../working/finished/20260604-c01-f-remote-sync-on-tick-planning-draft.md)、[harite-slideshow-spec.md §remote](../specs/slideshow/harite-slideshow-spec.md)
- [harite-source-spec.md](../specs/source/harite-source-spec.md)（CODH / NDL indexer）
- 既存: `format_remote_sync_error`、footer Error — ユーザー向け要約はあるが **開発者向けシーケンスログは不足**

### 取り込み方針

- **改修着手（v0）** — Preset remote の start sync / Manage Refresh sync / CODH tick に JSONL 操作ログ。
- スコープ: NDL・CODH の URL 組み立て〜 GET〜 cache 書き込み、CODH index build、tick 成否。手動 srcdir のみは対象外。
- 出力: 環境変数 `HARITE_SLIDESHOW_OP_LOG`（ファイル path または `stderr`）。未設定時は no-op。
- 実装: `slideshow_op_log.py`、`sources_remote*` / `main_window` フック。spec: source-spec §12。テスト: `test_slideshow_op_log.py`

### 調査メモ

- memo（オーナー）: CODH・NDL 観測の前提。JST タイムスタンプ必須。URL 組み立て過程の可視化が欲しい
- **v0（2026-06-09）:** `REMOTE_SYNC_*` / `NDL_*` / `CODH_*` / `JMA_TICK` ステップ。`ts_jst` は `+09:00` 固定オフセット。viper3 観測は `export HARITE_SLIDESHOW_OP_LOG=~/.cache/harite/slideshow-op.jsonl` 等。
- **実装:** #450 マージ済み。
- **観測（途中・2026-06-09）:** viper3 `slideshow-op.jsonl` 90 行 + オーナー実機メモ。[20260609-mat-08-viper3-slideshow-op-observation.md](../working/20260609-mat-08-viper3-slideshow-op-observation.md)
  - **JMA:** 問題なし（ログ・体感一致）
  - **NDL おまかせ:** 手編集 catalog 残存 — 想定どおり失敗（product 問題ではない）
  - **NDL / CODH その他:** **不安定** — 期待 tick（20:04 / 20:20 / 20:49）不発、CODH は 20:37 に JSONL 上 `CODH_TICK` OK だが **壁紙未更新**
  - **副次:** R を `--none--` にしても画像パス残存（`Clear-R` と不整合）→ L-only 観測が汚染
  - **MAT-02b 示唆:** GET 成功 ≠ 壁紙更新。tick 発火・apply 層が主戦場。op log v1+ で apply/tick 記録が必要

---

## MAT-09 — Margin 一括変更・リセット

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Feature: bulk Margin edit and reset`

### 事象 / 要望

- **単発の新規要望** — Margin を **一括変更**できる操作と、**リセット**（既定値へ戻す等）が欲しい。

### 分類

- `planning`（機能要望）
- `polish`

### 関連

- 正本: [harite-gui-spec.md §3 Margins / Main cross-grid](../specs/gui/harite-gui-spec.md)

### 取り込み方針

- **改修着手** — cross-grid 右下に **All margins (px)** spin。四辺同値・即時反映。`0` で既定復帰（専用 Reset なし）。
- スコープ: 四辺同値のみ（L=R 対称のみ・プリセットは対象外）。
- 表示: 四辺同値のときラベル有効 + all spin 同期。不一致時は **ラベルのみ無効化**（spin 値は維持）。all spin `valueChanged` でラベル復帰。

### 調査メモ

- memo（オーナー）: 熟成運転中の単発要望
- **UX（2026-05-31）:** 案 B（既存 spin に All）は分かりにくいため不採用。案 A 変形（右下専用 spin）を採用。
- **実装:** `build_margin_cross_grid`、`on_change_margins`（`spnAllMargins`）、`refresh_all_margins_bulk_controls`、gui-spec §3。Qt/GTK parity。
- **完了** — #456 マージ（2026-06-09）。Post Main Merge CI 緑（run 27195018405）。

---

## MAT-10 — 江戸切絵図を「雰囲気絵」ソースにできないか（検討）

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09（2026-06-09 補足: 具体 URL・地図名は **例示のみ**）
- 仮タイトル: `Investigate Edo Kiriezu as mood/atmosphere slideshow source`
- 参考: [江戸マップ（CODH）](https://codh.rois.ac.jp/edo-maps/)

### 事象 / 要望

- MAT-04（江戸**買物**案内やめる）により **CODH 系ソースが減る**。
- 代替として、slideshow に **雰囲気のある絵**（江戸切絵図の地図画像）が出せる経路が欲しい。
- [CODH 江戸マップ](https://codh.rois.ac.jp/edo-maps/) は NDL 所蔵切絵図と IIIF 連携の入口になりうるため、**技術・ライセンスの観点で検討**する価値がある。
- **特定の地図・URL に固定する意図はない**（転記時の築地八丁堀例・`dl.ndl.go.jp/.../1286660/...` は雰囲気イメージの **例示**）。
- **ライセンス NG なら当然断念**。

### 分類

- `investigation`（source / remote / IIIF）
- `planning`

### 関連

- MAT-04（江戸買物削除）、MAT-08（観測ログ）
- [C-01-E / NDL 調査](../working/finished/20260603-c01-e-ndl-tsugidigi-inventory.md)、[CODH 調査](../working/finished/20260603-c01-e-codh-icp-inventory.md)
- CODH: IIIF Curation Platform 経由で NDL 江戸切絵図 29+ 枚を地名 DB 化（[edo-maps 概要](https://codh.rois.ac.jp/edo-maps/)）
- 実装候補: `remote-ndl` / `remote-codh-edo-maps` 新 indexer、または既存 CODH 経路の拡張

### 取り込み方針

- 現時点: **転記のみ** — 棚卸で source 拡張候補として評価
- ゲート: NDL / CODH **利用規約・IIIF 利用条件**の確認が先
- 次: 代表 1 枚での試験（IIIF → download → slideshow）とライセンスメモ。採用時の選定軸は「雰囲気絵」

### 調査メモ

- memo（オーナー）: **雰囲気絵が出てほしい** — 文字図版中心の買物案内の代替。具体地図は例示のみ

---

## MAT-11 — Slideshow でも Optimize を掛ける

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Feature: run Optimize on Slideshow (same pipeline as Main)`

### 事象 / 要望

- Slideshow 実行時にも **Main と同型の Optimize** を掛けたい（Harite＝WallpaperOptimizer としての本来の経路）。
- margin / embed / Color / align 等は **個別オプションの列挙ではなく**、Optimize 未経由だと **Main の設定全体が slideshow に効かない** という症状の例。スコープは **オプション限定ではない**。

### 分類

- `planning`（機能要望）
- `investigation`（optimize / apply パイプラインとの接続）

### 関連

- MAT-03（Optimize で Color が効かない — 関連症状の可能性）
- 正本: [harite-slideshow-spec.md §6](../specs/slideshow/harite-slideshow-spec.md)、[harite-gui-spec.md](../specs/gui/harite-gui-spec.md)
- MAT-12 接続: single 直接 apply は **#452 で廃止**（§6.2.1 正本化は #451）
- CLI `slideshow` は当時 optimize 非経由（**MAT-17 で GUI parity へ拡張**）

### 取り込み方針

- **完了** — #452 マージ（2026-05-31）。single / dual とも Main と同型 `form_state` → `run_slideshow_optimize` → apply。
- スコープ: **Optimize 全体**（特定オプション列挙に限定しない）
- 実装: `_apply_slideshow_single_source`、`_set_slideshow_active_generated_files`（同一スロット再追跡時の誤削除防止）

### 調査メモ

- memo（オーナー）: Slideshow でも **ふつうに Optimize を掛ける**意図。オプション列挙にスコープを限定しない
- **実機（オーナー・Windows・MAT-01b 後）:** Preset 天気図が **原寸中央にポツン** — single 経路が Optimize を通らないため。MAT-01b で Main 側は正しくなったが、slideshow が **Optimize 迂回**のままが次のボトルネック
- **実装（#452）:** spec §6.2 / §6.2.1 更新。テスト: `test_mat11_slideshow_single_optimize.py` 他。
- **実機（オーナー・#452 後）:** おおまかには良好。細部は別途。
- 関連: 意図的 **2x/4x** は [MAT-14](#mat-14--2x--4x-display-scale意図的拡大)（MAT-11 とは別軸）。

---

## MAT-12 — Preset slideshow 時の Optimize 有無・保存先

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Investigation: does Preset slideshow run Optimize and where are outputs saved?`

### 事象 / 質問（そもそも話）

- **Preset 選択時、Optimize しているのか？**
- **Optimize 後のファイルはどこに保存しているのか？**
- 熟成運転（MAT-02 / MAT-08）の前提整理としての根本質問。

### 分類

- `investigation`
- `planning`（仕様明確化）

### 関連

- MAT-02、MAT-08、MAT-11
- 正本: [harite-slideshow-spec.md §6.1 / §6.2](../specs/slideshow/harite-slideshow-spec.md) — GUI slideshow 作業ディレクトリ、dual-source 時の optimize 出力管理
- [source-spec §12.4](../specs/source/harite-source-spec.md)（remote sync on tick）
- 調査入口: `run_optimize` 呼び出し経路、weather-map preset の「optimize 出力なし」分岐（§6.2 付近）

### 取り込み方針

- **改修着手** — コード + spec 照合で回答を正本化。表は [slideshow-spec §6.2.1](../specs/slideshow/harite-slideshow-spec.md)。
- 結論: **現行コード**はソース構成 dual → optimize、single（片方のみ）→ 直接 apply。tick network は別軸（§6.2.1）。**製品上** single の直接 apply は MAT-11 論旨で **認めない**（WallpaperOptimizer 意味が失われる）。
- 副次修正: R1 孤児掃除に `harite_slideshow_*` を含める。single-source 成功時に未追跡スロットも削除。

### 調査メモ

- memo（オーナー）: 壁紙が切り替わらない事象（MAT-02）の土台質問
- **確定（2026-06-09）:** ソース構成 dual（L+R 指定）→ optimize + 作業ディレクトリ。single（片方のみ）→ **現行** optimize なし・直接 apply。オーナー指摘: dual 指定時点でソースは dual。single の Optimize 迂回は **MAT-11 で廃止**（Main と同型の Optimize 経路へ）。
- **完了:** #451 マージ済み（§6.2.1 正本化、R1 掃除・single スロット削除）。

---

## MAT-13 — エラーメッセージを赤色で表示したい

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `GUI: show error feedback in red (stronger message affordance)`

### 事象 / 要望

- エラー時のメッセージが **赤色で出て欲しい**。現状、メッセージ性がすごく弱い。

### 分類

- `polish`
- `planning`（feedback / Status 面の視認性）

### 関連

- 正本: [harite-gui-spec.md §9 footer Status](../specs/gui/harite-gui-spec.md)
- 実装候補: `set_feedback` / `status_phase=error`、Qt/GTK の error 色スタイル

### 取り込み方針

- スコープ: 色・コントラスト・failure state の error 行表示（文言の全面見直しは別途）
- **完了:** #458 マージ済み — footer `Error` 行を **赤・太字** で強調（Qt `hasError` / GTK `harite-error-active`）。失敗 trace state（`*-failed` 等）は Error 行へ昇格。

### 調査メモ

- memo（オーナー）: v2.0.0 向け backlog 採番（MAT-13）
- **実装:** `footer_feedback`（`FOOTER_ERROR_ACTIVE_COLOR`、failure state 昇格）、`qt_stylesheet`、`gtk_runtime_widget_access`。テスト: `test_footer_feedback`、`test_qt_stylesheet`、`test_qt_widget_helpers`

---

## MAT-14 — 2x / 4x display scale（意図的拡大）

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Feature: per-display preset scale (2x/4x) separate from native placement`

### 事象 / 要望

- 高 DPI 向けに **意図的 2x / 4x** 等の display scale をユーザーが選べるようにしたい。
- **MAT-01b** の原寸回帰（拡大禁止）とは **別軸**（ユーザーが選ぶ product 判断）。

### UX メモ（オーナー指定）

- **QSlider の自由スライドではなく**、プリセット値を **ステップ移動**（縦横どちらのコントロールでも可）。
- Optimize 時に解像度を突破する判定となった場合は **エラー**。
- 理想は **L / R に一つずつ** 用意。
- Compose エリアが詰め込みすぎ — **Clear ボタン左**、または **下** に置く案（要 mock）。

### 分類

- `planning`（機能要望）
- `investigation`（optimize 解像度ゲートとの接続）

### 関連

- MAT-01b（#444 — 原寸配置・誤 upscale 禁止）
- MAT-11（#452 — Optimize 経路）
- `Display.scale_percent`（W-03-C — 付加情報として既存）
- 正本: [harite-core-spec.md](../specs/core/harite-core-spec.md)、[harite-gui-spec.md §3 compose grid](../specs/gui/harite-gui-spec.md)

### 取り込み方針

- スコープ: per-display preset scale UI + optimize 時の解像度上限チェック
- **完了:** #459 マージ済み（`fix/mat-14-display-scale`）:
  - **対象は元画像のみ**（detected display / composite 解像度は変えない）
  - `display_scale.py` — プリセット **100% / 125% / 150% / 200%**（内部係数 `1.0 / 1.25 / 1.5 / 2.0`）、スケール後画像の上限 `16384px/edge`
  - Compose Clear 左に L/R 各 % コンボ（Qt/GTK）。旧 `4x` 設定は `200%` へ正規化
  - `optimize_wallpapers` 配置時に元画像を意図的拡大（`100%` は MAT-01b 原寸/down-only）
  - 拡大後が display 矩形（margins 込み）に収まらない場合は `ValueError` → Optimize エラー（MAT-13 赤表示）

### 調査メモ

- memo（オーナー）: 旧「閃き」を MAT-14 として正式採番。MAT-11 調査メモの 2x/4x 言及と同系
- `Display.scale_percent`（W-03-C）は OS DPI 情報のみ。本項目のユーザー render scale とは別軸

---

## MAT-15 — align / margin / ストレッチの core 幾何総点検

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Investigation: re-audit alignment vs margin precedence and core geometry`

### 事象 / 要望

- **MAT-12 → MAT-11** の Optimize 必須線を踏まえ、**Alignment とマージンの勝ち負け**を再々点検したい。
- Alignment と画像のストレッチで **大きな誤解**があったため、**core を中心とした幾何計算**を総点検する。

### 分類

- `investigation`
- `planning`（core-spec / gui 注釈の整合）

### 関連

- MAT-01（#442）、MAT-01b（#444）、MAT-11（#452）、MAT-12（#451）
- 正本: [harite-core-spec.md](../specs/core/harite-core-spec.md)、gui-spec margin 注釈（`margins define area; align/valign act inside it`）
- 設計ドラフト: [MAT-01b native placement repair](../working/design/20260609-mat-01b-native-placement-repair-draft.md)

### 取り込み方針

- スコープ: core 幾何の照合（母体 `wallpaperoptimizer` 含む）→ spec / GUI 注釈整合 + テスト
- **完了:** #460 マージ済み（`fix/mat-15-core-geometry-audit`）:
  - 監査: [20260609-mat-15-core-geometry-audit.md](../working/20260609-mat-15-core-geometry-audit.md)
  - **結論:** core パイプラインは MAT-01b + MAT-14 整合。誤解の主因は GUI 旧注釈
  - GUI priority rule 更新（margin-inner → **full display slot**）
  - core-spec §4.1 に MAT-14 計算順・`scaling` 無効を明記
  - `tests/core/test_mat15_geometry_audit.py` 追加

### 調査メモ

- memo（オーナー）: MAT-01b で誤 upscale を直したが、align / margin / stretch の優先関係は別途総点検が必要
- **点検（2026-06-09）:** `scaling` 設定は幾何に無効（テスト確認）。MAT-14 は slot 解決後・align 前に元画像サイズのみ変更。left/top + margins で小画像が margin 帯に重なるのは母体同型（バグではない）
- **母体再読（2026-06-09）:** `wallpaperoptimizer` の `Core.py` / `Rectangle.py` を直接再読し、上記優先関係を確認（監査 §1.1）

---

## MAT-16 — 時刻フィールドをローカルタイム（JST）で扱う

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Use local timezone (JST) for cache metadata and op logs`

### 事象 / 要望

- `jma-cycle.json` をはじめ、`updated_at` など時刻は **ローカルタイム**（日本なら **JST**）で扱って欲しい。
- 正直、解析しづらい。**先行する MAT-08**（slideshow 操作ログ）も同じ。

### 分類

- `planning`（観測・診断 infrastructure）
- `investigation`（既存 UTC / naive 表現の棚卸）

### 関連

- MAT-08（#450 — `ts_jst` は JSONL で `+09:00` 固定オフセット済み。cache / settings 側は未整理）
- [harite-source-spec.md](../specs/source/harite-source-spec.md)（remote cache、`jma-cycle.json`）
- `HARITE_SLIDESHOW_OP_LOG` 出力形式

### 取り込み方針

- スコープ: cache メタデータ・op log の **表記方針統一**（ローカル TZ、日本環境では JST）
- **完了:** #461 マージ済み（`fix/mat-16-local-tz-cache`）:
  - `harite.local_time` — `local_now_iso`（cache）、`jst_now_iso`（op log MAT-08 互換）
  - `jma-cycle.json` / `codh-cycle.json` の `updated_at`、`codh-index.json` の `built_at` を UTC → ローカル TZ へ
  - source-spec §12.5 にタイムスタンプ契約を追記
  - `tests/test_mat16_local_time.py`

### 調査メモ

- memo（オーナー）: MAT-08 観測の前提整理にも効く
- **棚卸（2026-05-31）:** UTC だったのは JMA/CODH cache のみ。op log `ts_jst` は #450 済み。settings JSON に時刻フィールドなし

---

## MAT-17 — CLI slideshow でも設定ファイルを読む

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `CLI: slideshow command loads harite-settings.json`

### 事象 / 要望

- **CLI:** `slideshow` でも **設定ファイルを読ませる**。
- **headless モード**との差異なども点検が必要か。

### 分類

- `planning`（CLI / GUI parity）
- `investigation`（現行 CLI slideshow の settings 未読経路）

### 関連

- MAT-11（GUI slideshow は `form_state` 経由で settings 反映 — #452）
- 正本: [harite-cli-spec.md](../specs/cli/harite-cli-spec.md)、[harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md)
- MAT-11 調査メモ: CLI `slideshow` は optimize 非経由のまま（仕様どおり・当時対象外）— 本件は **settings 読込** の話

### 取り込み方針

- **実装（MAT-17）:** CLI `slideshow` に `--settings-file` / `-c` を追加。`optimize` と同様 **CLI > settings > 既定値**。
- **optimize 経路（MAT-11 parity）:** single / dual とも毎 cycle `run_slideshow_optimize` → apply。settings の optimize 一式を反映。
- 読むキー: slideshow 系 + optimize / apply 系（`resolution`, `margins`, `align`, `plugin`, `apply_mode`, …）。
- **スコープ外:** `slideshow_source_id_*` / `slideshow_profile_id` の catalog 解決、remote sync-on-tick、op log。
- 正本: [harite-cli-spec.md](../specs/cli/harite-cli-spec.md) §6、[harite-slideshow-spec.md](../specs/slideshow/harite-slideshow-spec.md) §7。

### 調査メモ

- memo（オーナー）: MAT-11 当時 CLI は対象外だったが、settings 読込だけでは意味が薄い → **optimize 経路まで揃える**（オーナー確定）

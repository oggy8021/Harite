# 熟成運転ログ — Qt / 共通（2026-06-09〜）

GitHub Issue 起票前の観測転記。

- 親: [20260609 feature-overview](../working/20260609-1200-feature-overview.md)
- 対象: **Qt 版**および **backend 共通**（GTK 専用は [GTK 熟成メモ](../working/20260609-1200-feature-overview.md#熟成運転メモxfce-実機) 参照）
- **転記:** MAT-01〜12 完了。MAT-02b（NDL/CODH 取得）は後送予定。
- **熟成運転:** 2026-06-09 **打ち切り**（継続には改修が先決）。
- **現フェーズ:** **改修着手** — 下記並びの **改修系から端から**（GitHub Issue 化なし）。

## 着手順（オーナー方針）

着手・Issue 化の **おおよその優先**（確定順ではない）:

1. **改修系** — 明らかな不具合・期待とのズレ
2. **確かさ向上** — 観測・仕様の明確化（直す前に切り分けたいもの）
3. **機能要望系** — 新規 UX / source / product 判断

| 区分 | ID |
| --- | --- |
| 改修系 | MAT-01, MAT-01b, MAT-02, MAT-03, MAT-05, MAT-06, MAT-07 |
| 確かさ向上 | MAT-08, MAT-12 |
| 機能要望系 | MAT-04, MAT-09, MAT-10, MAT-11 |

※ MAT-02 の NDL/CODH 取得側は **MAT-02b** として別枠（未転記）。MAT-10 の具体 URL は例示のみ（[MAT-10](#mat-10--江戸切絵図を雰囲気絵ソースにできないか検討) 参照）。

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
- **実機（オーナー・Windows）:** Preset ソースで顕著。**真の価値・見え方に戻った**（誤 upscale 時代のプロダクト誤解を解消）。天気図など **小画像は原寸のまま中央にポツン** — align では動かせない（余白があるから可能；画像が小さいと center 既定のまま）。→ **MAT-11**（Slideshow へ margin/align 浸透）と強く結びつく。
- **製品線（別 planning）:** 高解像度ディスプレイ向けの **意図的 2x / 4x 等**は、MAT-01b の「拡大禁止」とは **別軸**（ユーザーが選ぶ display scale）。本改修で誤った「常時 fit 拡大」路線には進まなくてよかった。

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

- 現時点: **転記のみ** — 棚卸後に preset 削除 or 非表示方針を決定
- スコープ: 江戸**買物**のみ（江戸観光は別判断）
- 次: 既存 settings での `slideshow_source_id_*` 参照時の挙動を含めて整理

### 調査メモ

- memo（オーナー）: 文字図版中心のため採用見送り

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

- **改修着手** — Linux / pip PyQt6 は fcitx 用 `platforminputcontexts` を同梱しないことが多く、Qt 全体で IME が無効化されうる（keyword field で顕在化）。
- スコープ: `prepare_qt_input_method_env`（`QT_IM_MODULE` 補完 + システム fcitx プラグイン symlink）、`keyword(CODH)` の IME 有効化。Xfce 実機での効果は **要確認**（IME フレームワーク差あり）

### 調査メモ

- memo（オーナー）: Xfce のみ。Ctrl+Space 無効
- **仮説（2026-06-09）:** pip PyQt6 の `platforminputcontexts` に ibus のみで fcitx 欠落。`GTK_IM_MODULE=fcitx5` でも `QT_IM_MODULE` 未設定だと Qt が IM に繋がらない。Manage dialog の keyword は日本語入力の主導線のため同 surface で顕在化。
- **実機（オーナー・viper3 / Xfce）:** mozc（fcitx 内）。env 整合・Firefox OK。PyQt6 venv は `ibus` + `compose` のみ。`libfcitx5-qt6-1` の `dpkg -L` は doc のみ（`5.1.4-1build5`、`Depends: libfcitx5-qt-data`）→ **Qt6 プラグインは `libfcitx5-qt-data` 側の可能性**。Qt5 の `libfcitxplatforminputcontextplugin.so` のみ観測 — PyQt6 では不可。
- **修正:** `qt_input_method.py` — 起動前 env、システムプラグイン symlink、`configure_text_input_widget`、欠落時 warning。spec: gui-spec Manage dialog Linux IME。テスト: `test_qt_input_method.py`

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

- 現時点: **転記のみ**
- スコープ: Enter 時のカーソル移動。行数上限ロジックとの関係は調査で確定
- 次: 再現（2 行目 Enter）→ 既存 `key-press-event` 処理の確認

### 調査メモ

- memo（オーナー）: 2・3 行目 Enter で先頭行へジャンプ

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

- 現時点: **転記のみ** — 棚卸で「観測用 logging」としてグループ化
- スコープ v0 案: Preset 選択時の start / tick / sync パス。手動 srcdir のみは対象外でも可
- 出力先: ファイル / stderr / 専用 dialog — **未決**（棚卸で決める）
- 次: シーケンス節の列挙（gui-spec or slideshow-spec 非正本メモ）→ 実装粒度の判断

### 調査メモ

- memo（オーナー）: CODH・NDL 観測の前提。JST タイムスタンプ必須。URL 組み立て過程の可視化が欲しい

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

- 現時点: **転記のみ**
- スコープ: 一括変更の対象（四辺同値 / プリセット / L-R 対称等）は棚卸で決定
- 次: UX 案（dialog / spin 一括 / settings 連動）の整理

### 調査メモ

- memo（オーナー）: 熟成運転中の単発要望

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

## MAT-11 — Slideshow に Margin / embed / Color を浸透

### 管理情報

- GitHub: **未起票**
- 記録日: 2026-06-09
- 仮タイトル: `Feature: apply Main Margin / embed / Color options to Slideshow path`

### 事象 / 要望

- Slideshow 実行時にも、Main で設定している次のオプションを **浸透**（反映）させたい:
  - **Margin**
  - **embed**（margin text パターン）
  - **Color**（背景色）

### 分類

- `planning`（機能要望）
- `investigation`（optimize / apply パイプラインとの接続）

### 関連

- MAT-03（Optimize で Color が効かない — 関連症状の可能性）
- 正本: [harite-slideshow-spec.md §6](../specs/slideshow/harite-slideshow-spec.md)、[harite-gui-spec.md](../specs/gui/harite-gui-spec.md)
- 現状: dual-source GUI slideshow は tick ごとに optimize 経路あり（§6.1 作業ディレクトリ）。単一 preset / remote の経路は要照合

### 取り込み方針

- 現時点: **転記のみ**
- スコープ: 「浸透」の定義（毎 tick optimize に渡す / apply 前処理 / preset 専用）は棚卸で確定
- 次: 現行 slideshow tick が margins / embed / background を読んでいるかコード照合

### 調査メモ

- memo（オーナー）: Slideshow でも Main と同じ見た目制御を期待
- **実機（オーナー・Windows・MAT-01b 後）:** Preset 天気図が **画面中央に原寸でポツン** — Main の xxAlign だけでは寄せられない／slideshow tick が margin・align を読んでいない疑い。**MAT-01b で見え方は正しくなったが、slideshow 側の「浸透」が次のボトルネック。**
- 関連: 意図的 **2x/4x** 計画は MAT-11 とは別（高 DPI 向け product 判断）。原寸回帰と混同しない。

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

- 現時点: **転記のみ** — コード + spec 照合で回答を docs に書く（GitHub Issue 化は棚卸後）
- 期待する成果: Preset 種別ごとの表（optimize する/しない、保存先 path、apply 入力）
- 次: MAT-08 ログと合わせて tick シーケンスを可視化

### 調査メモ

- memo（オーナー）: 壁紙が切り替わらない事象（MAT-02）の土台質問
- spec 仮説（転記時点・未検証）: dual-source auto-split は §6.1 作業ディレクトリへ optimize 出力。単画像 preset / remote-only は経路が異なる可能性

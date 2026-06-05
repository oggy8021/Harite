# Harite GUI 仕様 (GUI Spec)

最終更新: 2026-06-04 (C-04 Wave b — Slideshow options drawer)

## 1. GUI の責務

- GUI は日常操作面として、compose -> optimize -> apply -> slideshow の導線を提供する。
- framework-neutral な状態モデル（`views/`）と runtime（`adapters/` または `adapters_qt/`）を分離し、保守可能性を確保する。
- GUI は `MainWindow` を中心に、設定、スライドショー、status、message history を一貫した状態として保持する。
- エントリーポイントは GTK backend（`harite-gtk` / `app.py`）と Qt backend（`harite-qt` / `app_qt.py`）の 2 系統を持つ。いずれも同じ `MainWindow` を生成し、framework 固有の処理は各 adapters 側が担う。

## 2. GUI 起動導線

### GTK backend（harite-gtk）

```mermaid
sequenceDiagram
    actor User
    participant App as gui/app.py
    participant Window as views/main_window.py
    participant Backend as adapters/gtk_backend.py
    participant Tray as adapters/tasktray_adapter.py
    participant GTK as Gtk runtime

    User->>App: harite-gtk / python -m harite.gui.app
    App->>Window: MainWindow()
    Window->>Window: load default 設定
    App->>Backend: load_gtk_runtime_signal_backend()
    Backend-->>App: signal backend
    App->>Tray: initialize_tasktray(signal_backend)
    Tray-->>App: tasktray adapter / RuntimeError
    App->>Backend: present_gtk_window(...)
    Backend->>GTK: build widgets and connect dispatch
    GTK-->>User: window shown
```

GTK 起動時の実際の流れ:

- entrypoint は最初に `MainWindow()` を生成し、ここで既定の設定ファイル読み込みまで完了する。
- その後に GTK signal backend の読み込み、signal dispatch 接続、tray 初期化、実 window 表示を順に試みる。
- GTK / PyGObject が利用できない場合や tray 初期化が失敗した場合でも、entrypoint 全体は即失敗せず、可能な範囲で `window.show()` へフォールバックする。
- したがって GTK 起動は、GTK runtime の完全初期化に成功する経路と、部分機能で継続する経路の 2 面を持つ。

### Qt backend（harite-qt）

```mermaid
sequenceDiagram
    actor User
    participant App as gui/app_qt.py
    participant Window as views/main_window.py
    participant Backend as adapters_qt/qt_backend.py
    participant Qt as Qt runtime (QApplication)

    User->>App: harite-qt / python -m harite.gui.app_qt
    App->>Qt: QApplication()
    App->>Window: MainWindow()
    Window->>Window: load default 設定
    App->>Backend: load_qt_runtime_signal_backend()
    Backend-->>App: QtSignalBackend
    App->>Backend: connect_signals(dispatch)
    App->>Backend: present_qt_window(...)
    Backend->>Qt: build QMainWindow and show
    Qt-->>User: window shown
    App->>Qt: app.exec()
```

Qt 起動時の実際の流れ:

- `QApplication` を生成してから `MainWindow()` を生成する。
- `load_qt_runtime_signal_backend()` で `QtSignalBackend` を得て、`RUNTIME_HANDLER_MAP` から生成した dispatch を `connect_signals()` で渡す。
- `present_qt_window()` が `QMainWindow` を構築して表示し、`app.exec()` でイベントループに入る。
- PyQt6 が利用できない場合は即座に `SystemExit` で終了し、GTK backend と異なりフォールバック経路は持たない。

### 共通事項

- 両 backend とも `MainWindow` owner state を共有する。`ui_adapter.py` の `RUNTIME_HANDLER_MAP` は両 backend が共用する handler 名 / method 名の対応表である。
- ウィンドウタイトルは `Harite`、ウィンドウアイコンは `harite_app.svg` を使う（両 backend 共通）。
- ウィンドウの初期サイズは 900×640 を基準とする。

## 3. 画面全体構成

layout 戦略:

- GUI は top-level window の直下を単一の縦積み root container とし、header、center body、footer の 3 層で構成する。
- center body は notebook を 1 つ持ち、tab 順は `Main`、`Margins (for each display)`、`Slideshow (...)` とする。
- `Main` は日常操作の主導線、`Margins` は配置と margin text の詳細調整、`Slideshow` は継続実行面という役割分担を持つ。
- page ごとの内容は page shell や spacer を使って中央寄せしつつ、各 page 内では必要に応じて fill と center を切り替える。
- GUI の常設補助説明面は以下である。
  - header の flow legend
  - footer の status / slideshow summary / error
  - Main tab の `apply mode help row`
  - Margins tab の embed / margin text まわり（line limit 等は tooltip）
  - Slideshow tab の mode help（**Drawer 内** — C-04）
  - settings dialog の state/notice
  - color dialog の state/notice
- これらの補助説明面は、操作 widget と同一 row に埋め込まず、対応する操作面の近傍に独立 row または独立 block として置く。
- したがって GUI layout の基本方針は「window 全体は縦 3 層」「center body は notebook」「各 page は独立した責務を持つ」である。

Main Window:

- header は 2 行構成で、1 行目は title を左、command bar を右に置く。
- command bar には `Color`、`Settings`、`About` を右寄せで並べる。
- 2 行目の flow row では左に `Compose -> Optimize -> Apply` を置き、右に `Export Image` を置く。
- flow row の `Export Image` は optimize 結果画像の書き出し導線であり、設定ファイル保存とは別面である。
- flow row の左端には導線説明として flow legend を常設する。
- footer も 2 行構成で、1 行目は左に `Status`、右に `Slideshow summary` を置く。
- footer 2 行目は separator の下に `Error` を置き、status と error を縦 2 段で分離する。
- footer の `Status`、`Slideshow summary`、`Error` は実行状態と失敗面を読むための常設説明面である。
- footer の `Error` は `Status` / `Slideshow summary` と **視覚的に区別**する（例: 赤系 foreground）。同一の muted 色で status と error を並べない（C-04 Wave 0 — [planning draft](../../working/20260604-c04-gui-surface-planning-draft.md) §3）。
- footer の `Status` 行に **`{Phase}: {state}`** 形式（例: `Slideshow: planned`, `Margins: updated`）を常設しない。ユーザー向けは短い人間語または空とし、進行中の slideshow 状態は 1 行目右の `Slideshow summary` に寄せる。内部の `status_phase` は保持してよい（C-04 — 同上 §3.2）。

Main tab:

- `Main` tab は縦積みの `main_col` を持ち、その上段に compose grid、下段に action cluster を置く。
- compose grid は左・中央・右の 3 列構成で、左 panel と右 panel は display ごとの入力・方向操作面、中央 panel は pick state と swap 操作面とする。
- 中央 panel は direction toggle 群と **同型 3 行**とし、上段に pick state label、**中段**（Left-L … Right-L / Left-R … Right-R と同高）に **`Swap L/R`** button を置く（§4.1）。
- 左右 panel は同型で、上段に十字配置の direction toggle と `Open-L/R`、下段に選択 path 表示と `Clear-L/R` を置く。
- Main tab の選択 path 表示（`entPathL` / `entPathR`）は full path をそのまま出さず、共通 helper `format_input_display(...)` で **basename の省略表示** にする（§6.1 参照）。
- direction toggle 群は `Top/Bottom/Left/Right` を display ごとに十字状へ配置し、画像 picker button を中央に置く。
- action cluster は横 3 群構成で、左から `Preview`、`Optimize`、`Apply` を置く。
- action cluster の 3 群は **上端揃え** とする。群の高さ差（Apply 群の mode row 等）によって section label や button 行が縦方向にずれないこと。
- `Optimize` 群は button と result label を 1 行にまとめる（GTK backend の現行レイアウト）。
- Qt backend では、`Optimize` 群の result label（`Optimize result: ...`）を button の **直下** に置いてもよい。button は icon + 文字列を維持する。
- `Apply` 群は button と target label の行に加え、`apply mode row` と `apply mode help row` を別行で持つ（GTK backend の現行レイアウト）。
- Qt backend では、`Apply` 群の target label（`Apply target: ...`）を button の **直下** に置き、mode row 以降は現行どおり残り領域へ並べてよい。
- `apply mode row` は `No Split` / `Auto-Split` の radio を置き、`apply mode help row` は選択意味の説明 label を置く。
- `Preview` 群は左右 preview box を横並びに置き、その上下に assignment、画像 preview、result、state/source/assist を縦積みする。

Margins tab:

- `Margins` tab は **専用 tab として維持**する（C-04 案 A）。Main tab への全面統合や permanent 3-tab 廃止は行わない。将来の Main+Margins Drawer（案 B）は操作削減なしの載せ替えオプションとして [planning draft](../../working/20260604-c04-gui-surface-planning-draft.md) §7.2 に記す。
- `Margins` tab は単一の縦積み column を持ち、**cross-grid editor を主役**とする（4 辺 margin spin + 中央 stack）。
- cross-grid editor は上に top margin、左に left margin、右に right margin、下に bottom margin を置き、中央に詳細編集 stack を置く。
- 中央 stack は上から `embed pattern`、`margin text notebook`、`position selector` を縦積みする。**`current alignment summary`（`align=...` 長文）と `notes`（3 行 legend）は持たない** — ルール・制限は tooltip / hoobar へ逃がす（C-04 — [surface slice memo](../../working/design/20260604-c04-slideshow-margins-surface-slice-memo.md) §5）。
- `embed pattern` は `Off` / `Settings` / `Text only` / `Both` の radio row を持つ。
- `margin text notebook` は `Settings` page と `Text` page の 2 page 構成とする。
- `Settings` page は preview label を中心とした状態確認面、`Text` page は margin text entry 面とする。
- `position selector` は `Left` 列と `Right` 列を横並びに置き、それぞれ `Top` / `Bottom` radio を持つ（Main の direction 十字とは別物のまま維持する）。

Slideshow tab:

- `Slideshow` tab の **正面（中核）** は外周を縦積みで組み、top spacer、**profile row**、srcdir row、**interval/start/stop row**、（任意）**More slideshow options…** トリガ、bottom spacer の順とする（C-02 骨格 + C-04 — [surface slice](../../working/design/20260604-c04-slideshow-margins-surface-slice.html) / [memo](../../working/design/20260604-c04-slideshow-margins-surface-slice-memo.md)）。
- **profile row** は tab 幅中央に `combo_slideshow_profile`（`— none —` + profile 名一覧）を 1 本置く。常設の「選択で L/R を一括反映」類の補助 label は **持たない**（tooltip で足りる）。
- srcdir row は **Main tab compose grid と同型**の左・中央・右 3 列とする。左右 panel は上から **`combo_slideshow_source_l/r`（Saved source）**、`Srcdir-L/R` button、`L:` / `R:` path label、右下に `Clear-L/R` を持つ。中央 panel には **`Swap L/R`** button のみを置く（§4.1 / §4.2）。
- **interval/start/stop row** は正面に `Interval`、spin、`Slideshow Start`、`Slideshow Stop` を 1 行にまとめ、視線の終点とする。
- **補助面（Drawer）** — 正面からは `manage registry row`、`mode row`、`mode help row`、`detail row`（current/output）を除き、**開閉パネル（Drawer）** 内へ移す。トリガ label は `More slideshow options…`（rename 可）。Drawer 内に置くもの:
  - `Mode` + sequential/random + 短い mode help（1 行まで）
  - `btn_manage_source_registry`（`Manage sources and profiles…`）— 専用 Sources タブは **作らない**
  - `Slideshow current` / output 表示（path は tooltip または footer 要約で足りる場合は常設 label を省略してよい）
  - 将来の C-01-E-KW 入力は **Manage dialog 内**（Drawer 経由）を前提とする
- registry / remote の **Refresh** 注意は既存どおり OK ダイアログ（C-04 パターン）。
- C-04 Wave b 以降、補助面は **options drawer**（`More slideshow options…`）内に置き、正面は中核のみとする。

Dialogs:

- settings dialog は単一の縦積み editor box を持ち、上から `header row`、`settings rows`、`actions row`、`notice separator`、`state/notice` を並べる。
- settings dialog の header row は左に title、右に `Save Settings` を置く。
- settings dialog の `Save Settings` は設定ファイル保存を指し、main window の `Export Image` や image export dialog とは別の保存面である。
- settings dialog の現行 runtime 実装で常設 row として露出するのは `Resolution`、`Scaling`、`Plugin`、`Apply` である。
- settings dialog の `Apply` row は radio を横並びに持つが、main tab の apply mode help label に相当する補助説明 row は持たない。
- settings dialog は下段に `Settings: current values` を起点とする state label と notice label を持つ。
- optimize 結果画像の書き出しには別の image export dialog を使い、user-facing surface は dialog title に `Export Image`、状態表示に `Export path`、選択結果表示に `Export target` を使う。
- color dialog は title、picker host、値 entry、actions row、separator、state/notice の順で縦積みする。
- color dialog は下段に `Color: ...` を起点とする state label と notice label を持つ。
- about dialog は content 全体を window 内で上下中央寄せし、icon、title、version、description、credits、license、close button を縦積みする。
- about dialog の `Version`、`description`、`Credits`、`License` は product 情報を読むための常設情報 label 群である。
- dialog 群は main window より小さい独立 window として扱い、settings だけ resizable、color/about は fixed-size 寄りの扱いを取る。

## 4. メイン操作フロー

```mermaid
flowchart TD
    A[input and 設定] --> B[optimize]
    B --> C[saved files]
    C --> D[apply]
    C --> E[slideshow start]
    D --> F[status update]
    E --> F
```

- GUI は日常操作面として apply や slideshow を直接起動するが、内部では core / plugin / slideshow helper の経路を利用する。

Optimize / Apply クリック後の action cluster ラベル（GTK / Qt 共通）:

- `Optimize` クリック成功時: `lblOptimizeResult` = `Optimize result: success`、`lblApplyTarget` = `Apply target: ready`、`btnSetWall` を有効化する。
- `Optimize` クリック失敗時: `lblOptimizeResult` = `Optimize result: failed`、`lblApplyTarget` = `Apply target: not-ready`、`btnSetWall` を無効化する。
- handler 未接続時: `Optimize result: handler-missing`。
- 成功 / 失敗後の owner 同期は **`_sync_preview_state_from_owner` と `_sync_action_availability_from_owner` のみ** とし、`sync_input_state_from_owner`（`Optimize result: not-run` へ戻す）を走らせてはならない。
- `Apply` クリック成功時: `lblApplyTarget` = `Apply target: last applied`。

apply mode の user-facing 意味:

- action cluster の apply mode は GUI 上 `No Split` と第 2 択（Linux: `Auto-Split`、Windows: **`Span`**）である。
- `No Split` は内部的に `single-file` へ対応し、最適化済み画像を 1 ファイルのまま plugin apply する。
- Linux の `Auto-Split` は内部的に `per-monitor-auto-split` へ対応し、最適化済み画像を display ごとに分割して apply する。
- Windows の **`Span`** も内部値は `per-monitor-auto-split` だが、Apply target は **合成 1 ファイル**（Windows plugin）。OS **Span 表示** と組み合わせて左右見え方を揃える。per-monitor map は約束しない。
- Windows で display が 2 枚以上検出された場合、Main タブの既定選択は **Span** とする。No Split も選択可能。
- Settings の **`windows_apply_span`**（bool、既定 `false`）が有効なときだけ、Span モード Apply 前に HKCU `WallpaperStyle=22` を best-effort 設定する（B-lite）。Span 選択は Apply 時 Span 切替への同意とみなす。
- 補助ラベルとプレビュー文言は `apply_surface.py` が platform 別に生成する（Windows では auto-split / crop 等の Linux 用語を出さない）。
- apply mode の補助ラベル（Linux 従来）: `No Split` → single file、`Auto-Split` → per display split。
- CLI にある `per-monitor-explicit` は expert 向け escape hatch として残るが、GUI 主導線には露出しない。
- GUI は plugin 名を settings から保持するが、target 解決規則は core に従う。
- `_default_apply_mode` は XFCE セッション時 `per-monitor-auto-split`、Windows plugin かつ display 2 枚以上時も `per-monitor-auto-split`（UI 上 Span）、それ以外は `single-file`。
- `_default_plugin_name` はプラットフォームマップ（`linux`→`linux`、`win32`→`windows`、`darwin`→`macos`）から初期値を決定する。マップに該当しないプラットフォームでは `linux` を既定とし、その値が `available_plugins` に存在しない場合は先頭の利用可能 plugin を使う。

### 4.1 L/R swap と Slideshow srcdir clear（P-01 / P-02）

design 合意: [20260601-p01-p02-lr-swap-clear-slice.html](../../working/design/20260601-p01-p02-lr-swap-clear-slice.html)

| Handler | 呼び出し元 | Owner 操作 | Widget 同期 |
| --- | --- | --- | --- |
| `on_swap_input_paths()` | Main 中央 `Swap L/R` | `input_path_l` ↔ `input_path_r` を swap | `_apply_input_paths()` 経由で path 表示を更新 |
| `on_swap_slideshow_srcdirs()` | Slideshow 中央 `Swap L/R` | `slideshow_srcdir_l` ↔ `slideshow_srcdir_r` を swap | srcdir label（`L:` / `R:` 行）を更新 |
| `on_clear_slideshow_srcdir(side)` | Slideshow `Clear-L/R` | 指定 side の srcdir のみ `""` | 該当 label を空表示に更新 |

- 上記 3 handler は `ui_adapter.py` の `RUNTIME_HANDLER_MAP` に追加し、GTK / Qt 両 backend が同じ handler 名で `MainWindow` メソッドへ dispatch する。
- `side` 引数は `on_clear_input` と同型で、`"L"` / `"R"`（大文字小文字は strip 後に正規化）を受け付ける。不正 side は `False` を返し message history に理由を残す。
- **Swap** は path / srcdir の **値のみ**入れ替える。ファイル移動、registry 更新、direction toggle、pick state、apply mode は変更しない。
- **Swap** は片方だけ値がある場合も実行可能（空 ↔ 値の入れ替え）。
- **Clear-L/R**（Slideshow）は Main の `on_clear_input` と同型の per-side clear とする。**Clear both（同時クリア）は提供しない**。
- srcdir clear 後、両方非空でなければ `can_start_slideshow` は `False` となり Start を無効化する（§6 既存ガード）。実行中 slideshow を **自動 stop しない**（Main path clear と同様、owner 値と widget 表示の更新のみ）。
- swap / clear 後は `_sync_action_availability_from_owner`（または同等）で Start / Apply 等の有効状態を再評価する。
- 第2波 impl は **Qt backend** を先行。GTK backend は maintenance mode だが、上記 handler と widget 配置は spec 上 **parity 対象**とする。

### 4.2 Slideshow source registry（C-02）

design 合意: [20260601-c02-slideshow-source-registry-slice.html](../../working/design/20260601-c02-slideshow-source-registry-slice.html)（#376 マージ済）。catalog 契約は [source-spec §7](../source/harite-source-spec.md)。

| Widget / Handler | 用途 |
| --- | --- |
| `combo_slideshow_profile` | profile 選択 → L/R 一括反映 |
| `combo_slideshow_source_l` / `combo_slideshow_source_r` | 側別 saved source 選択 |
| `btn_manage_source_registry` | Manage dialog を開く |
| `source_registry_dialog` | sources + profiles CRUD（modal） |
| `on_select_slideshow_profile(profile_id \| none)` | profile → `resolve_profile_members` → owner / combo / label 更新 |
| `on_select_slideshow_source(side, source_id \| none)` | 側別 `resolve_source` → owner / label 更新 |
| `on_manage_source_registry()` | dialog 表示。Close 後に tab 上 combo を catalog から再構築 |
| `bootstrap_preset_sources` | startup および Manage dialog Close 後（[source-spec §13.4](../source/harite-source-spec.md)） |

**Saved source と Srcdir ブラウズの併存（オーナー合意 2026-06-01）:**

| 操作 | owner path | registry tracking（`slideshow_source_id_*` / `slideshow_profile_id`） | combo 表示 |
| --- | --- | --- | --- |
| Saved combo で source 選択 | `resolve_source` → `slideshow_srcdir_*` 更新 | 当該 side の source id を記録 | 選択 source 名 |
| Saved combo で `— none —` | path **は変更しない** | 当該 side の source id のみクリア | `— none —` |
| Srcdir-L/R ブラウズ確定 | 従来どおり path 直書き | 当該 side の source id をクリア | `— none —` |
| Profile 選択 | L/R 両 path を profile から展開 | `slideshow_profile_id` + 両 source id を記録 | 各 side を対応 source に |
| Clear-L/R（§4.1 拡張） | 当該 side path を `""` | 当該 side source id + **`slideshow_profile_id` をクリア** | 当該 side saved combo → `— none —`。**Profile combo → `— none —`** |
| Swap L/R（§4.1 拡張） | `slideshow_srcdir_l/r` swap | `slideshow_source_id_l/r` swap。`slideshow_profile_id` は **クリア**（L/R 対応が崩れるため） |

- slideshow **tick 中**は `slideshow_srcdir_l/r` の path のみ参照する（C-05 — [slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md)）。
- **Start 直前**に tracking `source_id` / `profile_id` から [source-spec §6.4](../source/harite-source-spec.md) に従い再 resolve し、`slideshow_srcdir_*` を上書きしてから画像収集する。
- registry 外 path（ブラウズのみ）も **許容**する。Saved combo が `— none —` でも path label に basename 省略表示があれば Start ガードは従来どおり評価する。
- profile / source の **ordered list 化・profile 周回**は行わない。

**Manage dialog:**

- Sources: 一覧、Add（name + directory browse）、Delete（profile 参照中は [source-spec §7.5](../source/harite-source-spec.md) に従い拒否）。
- Profiles: 一覧、L/R slot combo（source id または empty）、Add / Delete profile。
- 保存は `harite-sources.json` へ即 write。settings dialog とは別 surface。
- dialog Close 後、Slideshow tab の profile / saved source combo を reload する。

**§4.1 との関係:**

- `on_swap_slideshow_srcdirs()` は §4.1 に加え、上表の tracking swap / profile id クリアを行う。
- `on_clear_slideshow_srcdir(side)` は path に加え、当該 side の source id tracking と saved combo を `— none —` に同期する。

**実装:**

- 第4波 impl は **Qt backend** 先行。GTK は maintenance mode だが widget / handler は **parity 対象**。
- core API は `harite.sources` のみ使用。CLI surface は追加しない。

## 5. 設定 (settings) 保存と再読込

- startup 時に既定の設定ファイル (settings file) を読む。
- 設定 dialog (settings dialog) から apply / load / save を行える。
- 物理保存先と key 仕様は core spec に従う。

設定読み込みの扱い:

- startup では既定 path を解決し、ファイルが存在する場合だけ読み込みを試みる。
- startup 読み込みで `FileNotFoundError`, `OSError`, `ValueError` が起きた場合は、GUI 全体を失敗させず message history に skip 理由を残して続行する。
- startup 読み込み時は、既存の `status_level`, `status_phase`, `status_message`, `last_error` を退避し、設定反映後に復元することで、起動直後の status を不必要に上書きしない。
- startup で owner（`MainWindow`）へ設定を反映したあと、各 backend は **`connect_signals` 完了時点**で owner → widget の非 preview 状態（input / main / margins / slideshow / feedback）を同期する。GTK は `_sync_non_preview_state_from_owner`、Qt も同型。これにより事前配置した既定 settings が起動直後の widget に載る。

設定 dialog の責務:

- dialog を開く時点で form state を取り込み、必要なら two-screen 状態を同期する。
- apply ではアプリ設定モデルを GUI state に展開し、optimize / apply / slideshow の各状態へ反映する。
- save では現在の GUI state をアプリ設定モデルへ戻して JSON payload を作り、指定 path または既定 path へ保存する。
- load では指定 path の JSON を読み込み、設定ファイルからアプリ設定モデルへ変換したうえで GUI state に反映する。

## 6. slideshow との接続

- GUI のスライドショー機能は `MainWindow` 側に運用責務を持つ。
- slideshow start 時に srcdir（空不可）と plugin（解決可否）を検証する。apply_mode は start 時に検証しない。
- dual-source（Srcdir-L と Srcdir-R の両方に画像が存在する）実行では、GUI の apply_mode 設定値にかかわらず常に `per-monitor-auto-split` を使用する。single-source 実行では常に `single-file` を使用する。
- slideshow tick は runtime timer（GTK: GLib timeout / Qt: `QTimer`）と owner state の同期で動く。
- GUI は CLI slideshow helper をそのまま露出するのではなく、GUI 状態管理を被せたうえで利用する。
- GUI は slideshow tab に mode 選択面を持つ。
- mode の user-facing 表記は `sequential` / `random` とする。
- slideshow tab の mode 既定値は `random` とする。
- `slideshow_interval_seconds` の既定値は `60`（秒）である。
- mode は slideshow 関連設定値として load / save 対象に含める。
- mode 選択面は manage registry row（または srcdir row）の下、interval/start/stop row の上に独立 row として置く。
- mode help row は選択中 mode の簡潔な補助説明を表示する user-facing surface とし、`sequential` 時は `Sequential rotates images.`、`random` 時は `Random rotates images.` を表示する。

### 6.1 path 省略表示（Main input / Slideshow current）

GTK / Qt 両 backend で、次の user-facing surface は **同じ省略規則** を使う。

| surface | 表示内容 | helper |
| --- | --- | --- |
| Main tab `entPathL` / `entPathR` | 選択画像 path | `format_input_display(...)` |
| Slideshow tab `Slideshow current` | 現在 tick の L/R 選択画像 path | `format_slideshow_path_display(...)` → 内部で `format_input_display(...)` |

省略規則:

- 表示対象は path の **basename** とする（directory 部分は出さない）。
- basename が 36 文字以下ならそのまま表示する。
- 36 文字を超える場合は `head + "..." + tail` へ切り詰める。既定では末尾 12 文字を残し、head 側は `36 - 12 - 3` 文字を使う（preview assignment 表示と同型）。
- owner 側の `slideshow_current_display` 文字列も、上記規則で整形した L/R を含める。

### 6.2 Interval spin と settings の優先順位

`slideshow_interval_seconds` は settings JSON の load / save 対象であるが、**実行時の有効値は slideshow tab の Interval spin が起点** となる。

| タイミング | 挙動 |
| --- | --- |
| 起動時 settings load / Settings Apply | settings 値を owner `slideshow_interval_seconds` へ反映し、spin も同期する |
| spin 変更（`value-changed`） | `on_slideshow_interval_change` で owner を即更新する（Save 前でもセッション中有効） |
| **Start 直前** | spin の現値を owner へ **必ず commit** する（`value-changed` 未発火でも可）。GTK / Qt 共通 |
| Start 成功後 | runtime timer は commit 後の `slideshow_interval_seconds` で起動する |
| 実行中の spin 変更 | owner のみ更新。timer は再起動せず、新 interval は **次回 Start 以降** で有効 |

したがって、ユーザーが spin を 3 秒に変えて Start した場合、保存済み settings が 60 秒でも **3 秒がその Start の timer に使われる**。tray の Start も同じ backend 経路のため同規則が適用される。

実装参照: `commit_slideshow_interval_from_spin(...)`（`gtk_runtime_slideshow_ui.py`）、各 backend の `_on_slideshow_start_clicked(...)`。

### 6.3 source registry 接続（C-02）

- Slideshow tab の registry UI は §4.2 の layout / handler に従う。catalog 永続化は [source-spec](../source/harite-source-spec.md) が正本。
- startup / settings load 後、backend は catalog を load し、[source-spec §13.4](../source/harite-source-spec.md) `bootstrap_preset_sources` のち tab 上 combo を構築する（§6.5）。settings の任意 key `slideshow_source_id_l/r` / `slideshow_profile_id` があれば、対応 combo 選択を復元してよい（path は従来どおり `slideshow_srcdir_*` が実行値）。
- Saved / Profile 選択および Srcdir ブラウズの優先関係は §4.2 の併存表が正本。**`— none —` は source id のみクリアし path は維持**、**Srcdir ブラウズは registry 外 path として combo を `— none —` に戻す**。

### 6.4 Registry resolve at start（C-05）

- `on_slideshow_start`（tray Start 含む）の画像収集前に §4.2 / [slideshow-spec §6.6](../slideshow/harite-slideshow-spec.md) の resolve を行う。
- Manage dialog Close で catalog を保存したとき、実行中 slideshow が [source-spec §7.6](../source/harite-source-spec.md) の「影響あり」変更を含めば **stop** する。

### 6.5 Remote source と preset（C-01）

catalog / cache / provider の契約は [source-spec §12–16](../source/harite-source-spec.md)。

**Startup（Slideshow combo 構築前）:**

| 順序 | 処理 |
| --- | --- |
| 1 | `bootstrap_preset_sources(catalog)` — 変更時は `save_catalog` |
| 2 | preset 由来の各 remote source に `sync_remote_source`（失敗は message history、起動は継続） |
| 3 | §4.2 の profile / saved source combo を再構築 |

`combo_slideshow_profile` / `combo_slideshow_source_l` / `combo_slideshow_source_r` は、同梱 preset 由来の source / profile を user 追加分とあわせて列挙する。

**Combo 表示（catalog `name` とは別。GUI 接頭辞 `*` のみ）:**

| エントリ種別 | 表示 | 内部値 |
| --- | --- | --- |
| `local-dir` | `name` | source / profile `id` |
| preset 由来（`notes` に `harite-preset:{preset_id}`） | `*{name}` | source / profile `id` |
| 未選択 | `— none —` | none |

選択時の handler・tracking・start 前 resolve は §4.2 / §6.4 と同型。

**Slideshow Interval 下限（preset 駆動）:**

| タイミング | 契約 |
| --- | --- |
| saved source / profile 選択変更 | `catalog_slideshow_interval_floor`（[source-spec §13.3](../source/harite-source-spec.md)）を求め、戻り値があれば `slideshow_interval_seconds` と spin を **その秒数以上**へ引き上げ |
| profile 選択 | profile テンプレートに `min_slideshow_interval_seconds` があればそれを使う。無ければ members の各 source preset 下限の **最大値** |
| 側別 source 選択 | 当該 source の `notes` の `harite-min-interval:{秒}`（import 時に preset から複写）または preset 定義を参照 |

**`remote-jma-weather-map` 実行（Start 直前 Sync）:**

| 項目 | 契約 |
| --- | --- |
| `on_slideshow_start` 直前 | 実行 L/R が参照する当該 source それぞれで `sync_remote_source`（[source-spec §12.4](../source/harite-source-spec.md)） |

**Manage dialog:**

| 項目 | 契約 |
| --- | --- |
| remote source 行の Refresh | `sync_remote_source` |
| Profile 行 icon | Lucide `bookmark` / `star` / `folder-heart` のいずれか（package resource） |
| Manage 行 icon | Lucide `archive`（package resource） |

**Backend:** 第 4 波 GUI impl は Qt 先行。GTK は maintenance mode（parity 対象）。

### slideshow start / tick / stop

- GUI の slideshow source は `Srcdir-L` と `Srcdir-R` の 2 面で固定する。Start ボタンは **両方が非空のときのみ有効**になる。どちらか一方だけ設定された状態では slideshow を開始できない（`can_start_slideshow = False`）。
- start では Srcdir-L と Srcdir-R の両 source から画像を収集する。どちらかが空なら開始前に `slideshow srcdir is required` として止める。
- start 時点では slideshow tab 上の mode 選択値を採用する。
- start 時点で各 source から初回選択を行い、現在表示を更新してから apply を試みる。
- tick では次画像を選び直し、現在表示を更新したうえで apply を行う。
- apply に失敗した場合はスライドショー実行を停止し、status と message history に failure を残す。
- monitor 検出欠落のような一部条件では stop ではなく pause として扱い、状態表示を `paused` へ更新する。
- 実行中に mode 選択値を変えても進行中の run には反映しない。新しい mode を使うには stop 後に start し直す。
- dual-source auto-split 実行中の optimize 出力管理（差し替え・純増ギャップ）は [docs/specs/slideshow/harite-slideshow-spec.md §6.2–6.3](docs/specs/slideshow/harite-slideshow-spec.md) を参照する。

### Windows dual-source slideshow（W-02）

- plugin が `windows` かつ **display 2 枚以上** 検出時、Srcdir-L / Srcdir-R の dual-source slideshow を **開始できる**。
- 各 start / tick では GUI apply mode 設定にかかわらず `per-monitor-auto-split` 相当の optimize → composite を行い、core が **single-file + `windows_span`** に解決してから windows plugin へ apply する（Span 表示は OS 設定 + opt-in registry）。
- per-monitor 分割ファイルは slideshow 作業ディレクトリに **生成しない**（composite スロット `harite_slideshow.jpg` のみ）。
- `windows_apply_span`（Settings）が有効なとき、tick apply 前に `ensure_span_style()` を best-effort 呼び出す（Main タブ Apply B-lite と同型）。
- registry 自動復元は **実装しない**（slideshow 中の書き戻しは表示崩れリスク — [#343](../online-issues/closed/issue-343.md)）。

### GUI single-srcdir slideshow（W-02-B — 見送り）

- Start は **Srcdir-L と Srcdir-R の両方非空** のときのみ有効（現行どおり）。片方のみの Start は **採用しない**（2026-05-31）。
- 理由: source 1 件は display 1 枚が通例。GUI で single-source を許すと apply モード（No Split 等）との整理が別途必要。single display × single source は **将来の横断整理** とする。
- 代替: CLI `harite slideshow --input <directory>`（1 件入力 = single-source、選んだ画像を `plugin.apply` — [cli-spec §6](../cli/harite-cli-spec.md)）。

### 出力ディレクトリ（手動 Optimize と slideshow）

| 用途 | ディレクトリ | 既定の解決 |
| --- | --- | --- |
| 手動 Optimize / Export Image | `form_state.output_dir` | Linux: ピクチャ根（XDG）。Windows: `SHGetFolderPathW` Pictures → `~/Pictures` |
| slideshow 作業（dual-source composite 等） | `{ピクチャ根}/Harite/slideshow/` | 上記ピクチャ根の製品サブディレクトリ（§6.1 / slideshow-spec） |

- slideshow 作業ディレクトリは **ピクチャ配下** とし、`XDG_CACHE_HOME` は使わない。XFCE 系 plugin が `xfconf-query` で参照する壁紙 path の実体が、キャッシュ削除等で消えないようにするため。
- slideshow tab の `Slideshow output` は作業ディレクトリを示す。Main 導線の出力先表示とは別である。
- issue #317 の要件 R1–R5 は **いずれも対応する**（[slideshow spec §6.3](docs/specs/slideshow/harite-slideshow-spec.md)）。現行実装は過渡状態。
- R4 確定: `on_slideshow_stop` 時は作業ディレクトリのスロットファイルを削除せず、追跡 state のみクリア（xfconf path 維持）。

### エッジケース

- `SlideshowCycleState`（L・R）は `on_slideshow_stop` / `on_slideshow_start` でリセットされない。`mode=sequential` の場合、再起動後も前回の画像インデックスから継続する。
- `slideshow_output_display` の初期値は `"Slideshow output: ."` であり、`_update_slideshow_output_display()` 呼び出し前は一時的にドット表示になりうる。
- `slideshow_interval_seconds` をスライドショー実行中に変更した場合、モデル値のみが更新される。runtime timer（GTK / Qt）は再起動されず、新しいインターバルは次回の start 以降で有効になる（§6.2）。
- `_apply_slideshow_selection` で L・R 両方の選択画像が `"-"`（選択なしセンチネル）の場合、apply を行わず `(True, None)` を返す（成功扱いだが壁紙は変更されない）。
- `on_slideshow_tick()` を `slideshow_running=False` の状態で呼んだ場合、`False` を返してログのみ出力する。スライドショーの進行は行わない。
- `on_settings_dialog_open` は L・R 両方の input path が設定されている場合のみ two-screen 設定を同期する。片側のみの場合は two-screen 同期をスキップする。

## 7. tray / indicator / app icon surface

```mermaid
sequenceDiagram
    actor User
    participant Tray as GtkTaskTrayAdapter
    participant Backend as gtk signal backend
    participant Window as MainWindow / GTK window

    User->>Tray: open indicator menu
    Tray->>Tray: refresh visible/slideshow state

    alt Visible toggle
        User->>Tray: Visible / Invisible
        Tray->>Window: show/hide/present
    else Start Slideshow
      User->>Tray: Start Slideshow
      Tray->>Backend: _on_slideshow_start_clicked()
      Backend->>Window: on_slideshow_start()
    else Stop Slideshow
      User->>Tray: Stop Slideshow
      Tray->>Backend: _on_slideshow_stop_clicked()
      Backend->>Window: on_slideshow_stop()
    end
```

- tray は可視状態切り替えと slideshow 開始停止の補助面である。
- icon は slideshow 状態に応じて切り替わる。

tray 初期化の前提:

- task tray binding は `AyatanaAppIndicator3` を先に試し、利用できない場合に `AppIndicator3` を試す。
- tray 初期化には signal backend が main GTK window を解決できることが必要で、window を解決できない場合は task tray adapter を作らず初期化失敗として扱う。

icon / resource surface:

- main window と about dialog は product icon として `harite_app.svg` を優先利用する。
- main GTK window では window icon surface に `harite_app.svg` を与え、GTK runtime がそれを採る環境では taskbar / launcher / window surface 側の application identity に使われる。
- about dialog では window icon に加えて dialog content 内にも `harite_app.svg` を表示する。
- task tray indicator は slideshow 実行中に `harite.svg`、停止中に `harite_off.svg` を使い分ける。
- task tray indicator の icon surface は application icon の再利用ではなく、slideshow 状態を示す専用の product icon surface として分ける。
- product icon resource が見つからない場合、tray は system theme icon へフォールバックする。
- tray fallback は slideshow 実行中に `applications-graphics`、停止中に `media-playback-pause` を使う。
- header / tab / dialog の各 button icon は package 内の lucide SVG resource を使う。
- 現行 runtime で使う icon や button image は package resource として `src/harite/gui/resources/icons/` 配下に置き、legacy glade 資産とは混線させない。

button と icon の対応:

- header command では `Color` に `palette.svg`、`Settings` に `settings.svg`、`About` に `info.svg` を割り当てる。
- flow row の `Export Image` には `image-down.svg` を割り当てる。
- action cluster の `Optimize` には `image.svg`、`Apply` には `wallpaper.svg` を割り当てる。
- input 面の direction toggle は `Top-*` に `arrow-up.svg`、`Bottom-*` に `arrow-down.svg`、`Left-*` に `arrow-left.svg`、`Right-*` に `arrow-right.svg` を割り当てる。
- input 面の `Open-L` / `Open-R` と slideshow 面の `Srcdir-L` / `Srcdir-R` には `folder-open.svg` を割り当てる。
- input 面の `Clear-L` / `Clear-R` には `folder-x.svg` を割り当てる。
- compose grid 中央および slideshow srcdir row 中央の **`Swap L/R`** には `arrow-left-right.svg` を割り当てる（Lucide resource を package に追加する）。
- slideshow srcdir 面の `Clear-L` / `Clear-R` には `folder-x.svg` を割り当てる（Main Clear-L/R と同型）。
- slideshow 面の `Slideshow Start` と `Slideshow Stop` にはそれぞれ `play.svg` と `pause.svg` を割り当てる。
- settings dialog では header の `Save Settings` に `save.svg` を割り当てる。
- 一方で settings dialog の `OK` / `Cancel` には現行実装で専用 icon 割当てはない。

tray menu の現行項目:

- tray menu は `Visible/Invisible`, `Start Slideshow`, `Stop Slideshow`, `Settings`, `BaseColor`, `About`, `Quit` を持つ。
- `Visible/Invisible` は main window の show/hide を切り替える。
- `Settings`, `BaseColor`, `About` は dialog open request の補助導線である。

## 8. GUI の層構造

```text
GTK backend:  app.py    -> views/main_window -> controllers/services -> adapters/    (GTK runtime)
Qt backend:   app_qt.py -> views/main_window -> controllers/services -> adapters_qt/ (Qt runtime)
```

- `views/` と `controllers/` と `services/` は両 backend が共用する（framework-neutral）。
- `adapters/` は GTK backend 専用（maintenance mode）。
- `adapters_qt/` は Qt backend 専用（development focus）。

margin text position の visible semantics:

- `Margins` 面は margin text position を 4 つの radio で見せる: `Left Top`, `Left Bottom`, `Right Top`, `Right Bottom`。
- GUI state / Settings / CLI / core の `embed_position` は `left-top|left-bottom|right-top|right-bottom` で統一する。
- GUI の margin text position 変更 handler はこの 4 値だけを受け付ける。
- radio 表示と内部値は 1 対 1 に対応し、`Left Top=left-top`, `Left Bottom=left-bottom`, `Right Top=right-top`, `Right Bottom=right-bottom` である。
- `embed_position` が未指定のときの既定値は `right-bottom` である。

### 詳細分類

```text
views/                                       ← 両 backend 共用
  main_window.py          主状態モデル
  main_window_preview.py  preview 補助計算
controllers/                                 ← 両 backend 共用
  optimize_controller.py  optimize bridge
services/                                    ← 両 backend 共用
  cli_mapper.py           GUI state to CLI args
adapters/                                    ← GTK backend 専用（maintenance mode）
  gtk_backend.py          GTK runtime 統合窓口
  ui_adapter.py           signal dispatch table（両 backend 共用）
  tasktray_adapter.py     GTK tray / indicator
  gtk_layout_builders.py / gtk_tab_builders.py / gtk_dialog_builders.py
  gtk_runtime_*           signal, sync, dialog, slideshow, helper 群
adapters_qt/                                 ← Qt backend 専用（development focus）
  qt_backend.py           Qt runtime 統合窓口（QApplication / QMainWindow）
  qt_layout_builders.py   Qt レイアウト骨格の構築
  （以降のモジュールは Phase 3–9 で順次追加する）
```

preview 補助計算の現行規則:

- preview widget の目標サイズは container 幅から計算し、`target_width = max(120, min(320, int((allocated_width - 6) * 0.48)))`, `target_height = max(68, round(target_width * 9 / 16))` で決める。container 幅が取れない場合は `160x90` を使う。
- auto-split preview の crop box は、保存済み合成画像の幅 `comp_width` に対して `split_x = round((left_width / (left_width + right_width)) * comp_width)` で左右分割する。`comp_width > 1` のときは `split_x` を `1..comp_width-1` に clamp する。
- 左 preview box は `(0, 0, split_x, comp_height)`、右 preview box は `(split_x, 0, comp_width - split_x, comp_height)` であり、現行 GUI preview も y 方向は分割せず full-height の縦スライスを使う。
- `build_result_preview_state(...)` では、まず form state の `l_display`, `r_display` を読み、その後 `resolve_optimize_display_settings(...)` が成功した場合だけ、そこから得た display size で上書きする。したがって GUI preview の左右 display 情報は core と同じ display 解決結果へ寄せられる。
- preview assignment 表示のファイル名は、basename が 36 文字を超える場合だけ `head + "..." + tail` へ切り詰める。既定では末尾 12 文字を残し、head 側は `36 - 12 - 3` 文字を使う。

margin text preflight の現行規則:

- GUI は margin text mode が `none` のとき、preflight を `margin text off` として終了する。
- mode が `none` 以外のときは、まず `embed_position` を `_normalize_margin_text_position(...)` で正規化し、その値を form state へ書き戻す。
- preflight で使う margin area は `resolve_margin_text_region(...)` を通じて求め、結果が `None` なら `margin area unavailable` で失敗扱いにする。
- area が取れた場合でも、`area_width < 40` または `area_height < 12` なら `selected margin area is too small for margin text` として失敗扱いにする。
- `area_width < 40` または `area_height < 12` の条件で失敗する場合、`status_message` には `margin text does not fit current margin area` を設定する。
- area が十分あれば、GUI は `margin text ready in ... position ({area_width}x{area_height})` を status / log へ出す。
- GUI の実効行数は widget 値をそのままは使わず、`_effective_margin_text_max_lines()` により `free=5`, `combo=8`, それ以外は `3` へ正規化して optimize request へ渡す。
- free text 入力は GUI 側で先に最大 5 行へ切り詰め、空文字・空行のみなら `None` として保持する。
- `embed_info` の内部値と UI ラベルのマッピングは `none`↔"Off"、`params`↔"Settings"、`free`↔"Text only"、`combo`↔"Both" である。

## 9. GUI での失敗時挙動

- GUI は `status_level`, `status_phase`, `status_message`, `last_error` を持つ。
- footer に `Status:` と `Error:` を表示する。`Status` は **人間語の `status_message`（または空）** とし、`status_phase` をそのまま `"{phase}: {state}"` として出さない（§3 Main Window footer）。
- `Error` は failure 本文を示し、status 行と **色・重みで区別**する。
- slideshow, apply, 設定, input dialog などの failure は `last_error` / Error 行で読めるようにする（内部では phase 名を揃えてよい）。
- GUI の `logs` 相当領域も、利用者向けには message history として扱う。
- CLI の実行メッセージ粒度 option のような概念を GUI に持ち込まず、GUI 側は状態表示と履歴表示の面として説明する。

status 更新の原則:

- `_set_status(...)` は `status_level`, `status_phase`, `status_message`, `last_error` を一括更新する統一入口である。
- `settings`, `slideshow`, `apply`, `input` など phase 名は内部 trace 用に揃える。footer Status への phase 機械語の常設表示は行わない（§3）。
- message history は設定 dialog open/apply/save、slideshow start/tick/pause/resume/stop、startup settings load skip などの運用イベントを残す。

## 10. メッセージ分類

- `idle`: 待機
- `running`: 実行中
- `success`: 完了
- `paused`: 一時停止
- `error`: 失敗

## 11. CLI / core / slideshow との境界

- core 挙動は [docs/specs/core/harite-core-spec.md](docs/specs/core/harite-core-spec.md)
- CLI command surface は [docs/specs/cli/harite-cli-spec.md](docs/specs/cli/harite-cli-spec.md)
- slideshow 詳細は [docs/specs/slideshow/harite-slideshow-spec.md](docs/specs/slideshow/harite-slideshow-spec.md)

境界整理:

- GUI は widget と状態表示の面を持つが、設定ファイルの物理仕様や apply target 解決規則そのものは core に依存する。
- GUI のスライドショー機能は slideshow helper を利用するが、pause / resume 的な扱い、状態表示、message history は GUI 側の責務である。
- tray は GUI の補助導線であり、独立した業務規則の一次置き場にはしない。

# Harite スライドショー仕様 (Slideshow Spec)

最終更新: 2026-06-07

## 1. スライドショー機能の責務

- 入力画像列を一定間隔で選択し、apply 面へ接続する。
- CLI と GUI の両面で、スライドショー機能としての継続実行を説明する。

public surface では、この機能を `スライドショー` と呼ぶ。画像候補集合を一定間隔で巡回し、次に適用する画像を選ぶ継続実行面を指す。

### 1.1 本書の読み方

| 層 | 節 | 内容 |
| --- | --- | --- |
| **本編** | §2–5 | 起動条件、cycle、pause/stop |
| **本編** | §6 | GUI 連動（作業ディレクトリ・registry・remote tick） |
| **付録** | §7 以降 | CLI command、失敗分類 |

source catalog / remote sync は [source-spec](../source/harite-source-spec.md)。GUI 操作面は [gui-spec](../gui/harite-gui-spec.md)。

## 2. 起動条件

- CLI 側のスライドショー実行は入力 directory 1 件または最大 2 件, interval, mode, plugin 条件を満たす必要がある。
- GUI 側のスライドショー実行は srcdir, plugin, dual-source 時の display 条件を満たす必要がある。

CLI 側の最低要件:

- `--input` 正規化後に採用された 1 件または 2 件の各要素が既存 directory であること
- directory 内に画像ファイルが 1 件以上あること
- `--interval-sec >= 1`
- `--mode` が `sequential` または `random`

CLI 側の入力正規化:

- `--input` は複数回指定できる。
- 1 回の `--input` 値内ではカンマ区切りで複数 directory を指定できる。
- CLI は各値をカンマ分割し、空要素を落とし、順序を保った directory 列へ正規化する。
- public surface で採用する source directory 数は最大 2 件であり、3 件以上与えられた場合は先頭 2 件だけを使う。
- 1 件入力時は single-source slideshow として扱う。
- 採用済み source directory の順序は保持され、画像列収集時もその順に連結する。
- CLI current command は left source / right source の別 apply target を直接は持たず、GUI の `Srcdir-L` / `Srcdir-R` のような左右別 owner state は持たない。

GUI 側では、これに加えて現在の画面状態、設定、スライドショー source directory の整合が必要になる。

GUI の source registry 連動:

- Start 前に [source-spec §6.4](../source/harite-source-spec.md) に従い、tracking `source_id` / `profile_id` から **再 resolve** して `slideshow_srcdir_l/r` を更新する（§6.6）。
- **検出 2 枚以上**（`len(detect_displays()) >= 2`）: **Srcdir-L と Srcdir-R の両方**が非空であること。どちらか空なら start 前に拒否。
- **検出 1 枚**（[gui-spec §6](../gui/harite-gui-spec.md)）: **Srcdir-L のみ**非空で start 可。第二スロット UI は disabled。profile / saved source の R 指定は実行時に無視。start は L source のみで single-file apply。
- 手動 Srcdir のみ（tracking key なし）の side は、既存 path をそのまま検証する。
- CLI は registry tracking を使わず、従来どおり `--input` directory path のみ。

## 3. スライドショーシーケンス図 (slideshow sequence)

```mermaid
sequenceDiagram
    actor User
    participant GUI as MainWindow
    participant Slideshow as slideshow.py / GUI slideshow state
    participant Core as optimize/apply 設定
    participant Plugin as plugin impl

    User->>GUI: start slideshow
    GUI->>GUI: resolve registry ids to srcdir paths
    GUI->>GUI: validate srcdir / plugin / apply mode
    GUI->>Slideshow: collect or select next image(s)
    alt single source
        GUI->>Plugin: apply(image)
    else dual source (Linux per-monitor)
        GUI->>Core: run_optimize(two-screen state)
        Core-->>GUI: composite file
        GUI->>Core: resolve_apply_settings(...)
        Core-->>GUI: per-monitor target map
        GUI->>Plugin: apply(target map)
    else dual source (Windows Span)
        GUI->>Core: run_optimize(two-screen state)
        Core-->>GUI: composite file
        GUI->>Core: resolve_apply_settings(...)
        Core-->>GUI: single-file target (windows_span)
        opt windows_apply_span
            GUI->>Core: ensure_span_style (best-effort)
        end
        GUI->>Plugin: apply(single wide image)
    end
    Plugin-->>GUI: ok / failed / exception
    GUI->>GUI: update status display, status, message history
```

### 3.1 start / tick / apply / pause の責務分離

スライドショー面は 1 本の機能に見えるが、仕様上は少なくとも次の 4 段階へ分かれる。

1. start: 実行開始前の入力条件と owner state を確定する段階
2. tick: 各サイクルで次画像または次画像群を選ぶ段階
3. apply: 選ばれた画像または target を plugin 実行面へ渡す段階
4. pause / stop: 一時条件不成立と恒久 failure を owner state へ反映する段階

各段階の主責務は次のとおりである。

| 段階 | 主責務 | 補助責務 / 呼び出し先 | 持ち込まないもの |
| --- | --- | --- | --- |
| start | CLI / GUI owner | slideshow helper, core, plugin registry | plugin 実適用 |
| tick | slideshow helper または GUI owner state | 画像列収集済み state, mode 規則 | widget 更新詳細 |
| apply | plugin | core が必要なら target を先に解決する | mode 選択や timer 管理 |
| pause / stop | GUI owner / CLI command | status, history, completed 集計 | plugin fallback の詳細 |

この整理により、「次画像を選ぶこと」と「選ばれた target を実際に適用すること」と「条件不足時に paused とみなすこと」は別層の責務として読む。

## 4. 継続実行ループの基本動作

- この機能はサイクルごとの選択ループである。
- `sequential` と `random` の選択モードを持つ。
- 選択モードは CLI / helper だけに閉じず、GUI 側にも user-visible な選択面を持つ。
- GUI 側の mode 表記は `sequential` / `random` とする。
- GUI 側の mode 既定値は `random` とする。
- GUI 側でも `random` を選べるようにし、`sequential` は互換的な選択肢として残す。
- GUI の mode 選択面は slideshow tab 上で srcdir row と interval/start/stop row の間に独立 row として置く。
- GUI 実行中に mode 選択値を変えても、その run には反映しない。新しい mode は stop 後の次回 start から使う。

slideshow helper の最小構成:

- source directory 正規化 helper は、採用済み source directory の妥当性確認と画像列収集を受け持つ。
- source directory 正規化 helper は、採用済み source directory を順にたどり、各 directory の画像列をその順のまま連結した 1 本の候補列へ正規化する。
- `select_next_image(...)` は `sequential` / `random` の選択規則を受け持つ。
- `run_slideshow_cycle(...)` は 1 サイクル分の選択と state 更新を受け持つ。
- `run_slideshow_cycles(...)` は interval を加えた継続ループを受け持つ。

状態モデル:

- `index`: sequential 時の次位置
- `previous_selected`: random 時に直前重複を避けるための参照
- `completed`: 完了サイクル数

状態遷移の現行規則:

- `sequential` では `selected_index = index % len(images)` で選び、次 state は `index = index + 1`, `previous_selected = selected`, `completed = completed + 1` になる。
- `random` では候補数が 2 件以上かつ `previous_selected` が候補に含まれる場合だけ、その 1 件を除外した候補集合から選ぶ。候補が 1 件しかない場合や直前画像が候補集合にない場合は、全候補から選ぶ。
- `random` の next state は `index` を進めず、`previous_selected` と `completed` だけを更新する。
- `run_slideshow_cycles(...)` の callback へ渡す cycle 番号は `completed - 1` であり、内部 callback 番号は 0 始まりになる。
- sleep は継続実行を続ける場合にだけ入る。

## 5. pause / resume / retry

- GUI 側のスライドショー実行は display loss や auto-split 条件未成立時に pause 的な扱いを持つ。
- CLI 側は簡潔な実行ループとして実行メッセージを返す。

整理すると、明示的な pause / resume API を slideshow helper 自体は持たない。pause / resume 的な制御は主に GUI 側の状態管理として現れ、CLI 側は開始から終了まで 1 本のループを実行するモデルである。

GUI pause / resume の現行条件:

- dual-source auto-split の `tick` 中に `per-monitor apply requires at least two detected displays` が返った場合、GUI は stop せず pause へ遷移する。
- この pause は `slideshow paused: waiting for two detected displays for auto-split` を status message に入れ、状態表示を `paused` に切り替える。
- pause 中に次 tick が成功すると GUI は `slideshow resumed` を出して running へ戻る。
- 同じ `ValueError` でも `start` 時は transient 扱いせず、start failure として止める。

pause / stop 判定の境界:

- start 前の条件不足は pause ではなく start failure として扱う。
- tick 中に起きる一時的な display 条件不足だけを GUI は paused として吸収してよい。
- plugin が `False` を返した場合や plugin exception は、GUI / CLI の owner が failure として分類するが、その失敗理由の生成自体は plugin 側の契約に属する。
- auto-split target 解決失敗と plugin 実 apply failure は同じ `apply failed` に潰さず、owner 側の status / history では別理由として保持する。

GUI timer / side state の現行規則:

- GUI runtime timer は `interval_ms = max(1, int(interval_seconds)) * 1000` で作る。したがって現行 GUI は秒未満を扱わず、秒整数へ量子化して GLib / Qt timer に渡す。
- **Start 直前**に Interval spin の現値を owner `slideshow_interval_seconds` へ commit する。timer は commit 後の owner 値で起動する。settings ファイルに保存された値より、Start 時点の spin 表示が優先される（詳細は [gui-spec §6.2](../gui/harite-gui-spec.md)）。
- dual-source 実行では L/R で独立した slideshow state を持ち、それぞれ `run_slideshow_cycle(images, backend.slideshow_mode, backend._slideshow_state_l|r)` で更新する。
- したがって GUI dual-source の左右選択は、同じ tick の中でも 1 本の共有 index ではなく、L side state と R side state を別々に進める。
- signal handler 経由の slideshow tick が使える場合は owner 側 callback を優先し、callback が `False` を返した時点で timer を止める。signal handler がない fallback 経路のときだけ GUI runtime 自身が L/R 選択を進める。

## 6. GUI のスライドショー責務

- srcdir 解決
- 現在表示 / 状態表示 / 出力表示の更新
- dual-source auto-split の準備
- tray からの start / stop 接続

GUI は単なるタイマー処理ではなく、状態表示の責務を強く持つ。特に次の情報を UI 上で維持する必要がある。

- 現在選ばれている入力や出力
- スライドショー実行が進行中か停止中か
- 直近 apply の成否
- display 条件不足や plugin 失敗の理由

### 6.0 GUI 表示面（current / output）

- **`Slideshow current`**: 現在 tick（または start 直後）で選ばれた L/R 画像 path を示す。user-facing label では full path をそのまま出さず、[gui-spec §6.1](../gui/harite-gui-spec.md) の basename 省略規則（`format_slideshow_path_display`）を使う。長いマウント path（例: クラウド同期 drive 配下）でもファイル名中心で読めること。
- **`Slideshow output`**: §6.1（slideshow 作業ディレクトリ）の path を示す（省略規則の対象外。directory path をそのまま表示してよい）。
- owner の `slideshow_current_display` も、上記と同じ整形済み L/R を含める。

### 6.1 slideshow 作業ディレクトリ（案 A: ピクチャ配下）

GUI slideshow が生成する optimize 成果物（composite と per-monitor 分割画像）は、手動 Optimize / Export の出力先とは **別の slideshow 作業ディレクトリ** に書く。

#### 解決規則（Windows）

1. **ピクチャ根** — `SHGetFolderPathW`（Pictures、CSIDL 0x27）。未解決時は `~/Pictures`。
2. **slideshow 作業ディレクトリ** — `{ピクチャ根}/Harite/slideshow/`（Linux と同型）。

#### 解決規則（Linux / XDG）

1. **ピクチャ根**（手動 Optimize / Export の既定 `output_dir` と同型）  
   - `XDG_PICTURES_DIR` 環境変数  
   - 未設定時は `$XDG_CONFIG_HOME/user-dirs.dirs` の `XDG_PICTURES_DIR=`  
   - さらに未解決時は `~/Pictures`
2. **slideshow 作業ディレクトリ**  
   - `{ピクチャ根}/Harite/slideshow/`（製品固定のサブディレクトリ名。未存在なら作成する）

`XDG_CACHE_HOME` 等のキャッシュ領域は **採用しない**。Linux / XFCE 系 plugin は `xfconf-query` 等で壁紙 path を永続設定に書き込むため、apply 対象の画像実体は **ユーザーが通常アクセスできる非揮発のディレクトリ**（ピクチャ配下）に置く。キャッシュ削除で壁紙 path が無効化されるリスクを避ける。

#### GUI surface

- slideshow tab の `Slideshow output` は **slideshow 作業ディレクトリ** の path を示す。
- Main 導線の手動 Optimize / Export の出力先（`form_state.output_dir`、既定はピクチャ根）とは別 surface とする。

### 6.2 GUI dual-source auto-split 時の optimize 出力ファイル管理

GUI が dual-source slideshow を `per-monitor-auto-split` で実行するとき、各 tick で `optimize` と auto-split により §6.1 の作業ディレクトリへ出力する。R1–R3 により、継続実行中に作業ディレクトリへ **追跡スロット以外のファイルが残らない** ことを保証する。

#### 固定スロット（R2）

作業ディレクトリ内のファイル名は tick ごとに増えない **固定スロット** とする。存在ベース採番（`harite_output_{NNNN}.jpg`）は slideshow 経路では使わない。

| 種別 | ファイル名 |
| --- | --- |
| composite | `harite_slideshow.jpg` |
| per-monitor 分割（Linux plugin のみ） | `harite_slideshow_{display_name_safe}.jpg`（`display.name` を file-safe 化した suffix。例: `HDMI-1` → `harite_slideshow_HDMI-1.jpg`） |

Windows **Span** 経路（`windows_span`）では **composite スロットのみ** を生成・apply する。per-monitor 分割ファイルは作らない（B-lite / [gui-spec § Main Apply](../gui/harite-gui-spec.md) と同型）。

- dual-source の optimize / split は、上記 path を `output_path` / `output_dir` として明示指定し、毎 tick 上書きする。
- 手動 Optimize（ピクチャ根）は従来どおり `harite_output_{NNNN}.jpg` 採番でよい（R5 により作業ディレクトリと分離）。

#### tick 終了時の整理（R1, R3）

各 dual-source tick の終了時（成功・pause・失敗を問わない）に、当該 tick で生成した path 集合 `_slideshow_tick_generated_files` を確定し、次を行う。

1. **R3 rollback** — apply 未完了（pause、prepare 失敗、apply 失敗）のとき、当該 tick 生成分を作業ディレクトリから削除する。追跡スロット（`_slideshow_active_generated_files`）は更新しない。
2. **R1 作業ディレクトリのスロット外掃除** — 作業ディレクトリ直下で、現行スロット集合および `_slideshow_active_generated_files` に含まれる path 以外の `harite_slideshow_*.jpg` / レガシー `harite_output_*.jpg` を削除する（移行期の掃除を含む）。
3. **apply 成功時** — 当該 tick のスロット集合を `_slideshow_active_generated_files` に記録する（path は tick ごと固定のため、実体は上書き済み）。

single-source（MAT-11）:

- **毎 start/tick** で Main と同型の `run_slideshow_optimize` を実行する（`form_state` 一式、`input_value` は cycle 選択 1 枚）。
- 成果物は `harite_slideshow.jpg` 固定スロット（dual の composite と同型）。apply はその path。
- apply 成功時はスロットを `_slideshow_active_generated_files` に記録し、R1 でスロット外（旧 split 等）を掃除する。

対象範囲:

- R1–R3 は **slideshow の optimize 経路**（single / dual）に適用する（GUI + CLI）。
- CLI `slideshow` も毎 cycle optimize 出力を `{Pictures}/Harite/slideshow/` へ書く（§7）。

ライフサイクル:

| タイミング | 挙動 |
| --- | --- |
| dual-source tick / apply 成功 | スロットへ上書き → `_slideshow_active_generated_files` 更新 → R1 掃除 |
| dual-source tick / pause | R3 で当該 tick 生成分 rollback → R1 掃除。timer は継続可 |
| dual-source tick / apply 失敗 | R3 rollback → slideshow 停止 → R1 掃除 |
| single-source / apply 成功 | スロットへ上書き → `_slideshow_active_generated_files` 更新 → R1 掃除 |
| `on_slideshow_stop` | スロットファイルは残す。追跡 state のみクリア（§6.3 R4） |

#### 6.2.1 Preset / remote source と optimize 経路（MAT-12）

**用語（混同しやすい点）:**

| 語 | 意味 |
| --- | --- |
| **ソース構成 dual** | **Srcdir-L と Srcdir-R の両方**に source が割り当て済み（§2: 2 ディスプレイ時は start 必須）。ユーザーが「Dual」と呼ぶのは通常こちら。 |
| **ソース構成 single** | **片方のみ**（1 ディスプレイ時は L のみ。R は空または無視）。 |
| **remote tick sync** | 各 tick で、**当該 side** が `remote-*` なら provider 別に network を走らせうる（JMA / CODH。NDL は tick ではしない）。**ソース構成 dual では L と R で独立に実行**する（§6.6）。optimize の有無とは **別軸**。 |
| **apply 経路 dual** | cycle 後に L/R **両方**の選択 path があり、`run_slideshow_optimize` → 作業ディレクトリの固定スロット → apply。 |
| **apply 経路 single** | 有効な選択 path が **1 件**のとき、`run_slideshow_optimize` → `harite_slideshow.jpg` → single-file apply。 |

**Optimize の有無は preset 種別（JMA/NDL/CODH）ではなく、ソース構成と apply 経路で決まる。** Srcdir-L/R をそれぞれ指定した時点でソース構成は **dual** であり、2 ディスプレイ + auto-split が有効なら **毎 start/tick で optimize する**。

| ソース構成 | 2 ディスプレイ時の start | Optimize（start/tick） | 成果物の保存先 | plugin `apply` 入力 |
| --- | --- | --- | --- | --- |
| **dual**（L+R 指定） | 可（§2） | **する** | `{ピクチャ根}/Harite/slideshow/` 固定スロット（§6.2 R2） | Windows: `harite_slideshow.jpg`（Span）。Linux: per-monitor 分割 map |
| **single**（片方のみ） | L のみ可 | **する**（MAT-11） | 同上（`harite_slideshow.jpg`） | `harite_slideshow.jpg`（Optimize 済み） |

**MAT-11:** single も **Main と同型の Optimize**（margins / align / embed 等は Main `form_state` と共有）を毎 start/tick 通す。手動 source scale（MAT-14 %）は slideshow 経路では **常に 100%**。

**MAT-14b:** auto 倍率だけは **Slideshow 専用設定**（`slideshow_l_auto_display_scale` / `slideshow_r_auto_display_scale`）。Main の `l_auto_display_scale` は slideshow optimize では参照しない。GUI は Slideshow タブの auto checkbox、CLI は settings の slideshow 面キー。

**Tick シーケンス（ソース構成 dual + 両 side が remote preset の例）:**

1. L: `jma_slideshow_tick` 等 → L cache 更新 → L cycle
2. R: `codh_slideshow_tick` 等 → R cache 更新 → R cycle
3. `run_slideshow_optimize`（L/R 選択 path を入力）→ 作業ディレクトリへ書き込み → apply

network は step 1–2、optimize は step 3。**「tick で network する」と「optimize しない」は両立しない（dual 構成では optimize もする）。**

**Preset 種別ごとの remote sync（ソース構成に依存しない。当該 side が remote のとき）:**

| Preset / source | Start 前 sync | Tick 前 sync（当該 side） | Slideshow Mode（cache 1 枚時） |
| --- | --- | --- | --- |
| JMA 天気図 | `sync_remote_source` | `jma_slideshow_tick` | 実質無効（`latest.png` 1 枚） |
| NDL 図版 | `sync_remote_source` | `ndl_slideshow_tick` | 実質無効（`latest.jpg` 1 枚。tick 毎 randomwithfacet で候補更新） |
| CODH 江戸 | `sync_remote_source` | `codh_slideshow_tick` | 有効（sequential / random） |
| `local-dir` | なし | なし | 有効（複数枚時） |

**Optimize 設定の合成（single / dual 共通）:** Main `form_state` をベースに、auto 倍率のみ `slideshow_*_auto_display_scale` で上書きして `run_slideshow_optimize` へ渡す（MAT-11 + MAT-14b）。

**実装入口:** `_apply_slideshow_single_source`（single）、`_apply_slideshow_selection` の dual 分岐。`on_slideshow_tick` は L/R 各 side で `_remote_slideshow_tick_for_side` を **独立に**呼んでから cycle する。

### 6.3 dual-source 作業ディレクトリの整理要件（R1–R5）

以下を満たす。

| ID | 要件 |
| --- | --- |
| R5 | 手動 Optimize はピクチャ根（`form_state.output_dir`）。slideshow 作業は `{ピクチャ根}/Harite/slideshow/`。`XDG_CACHE_HOME` は使わない（§6.1） |
| R2 | 作業ディレクトリ内は §6.2 の固定スロットのみ。`harite_output_{NNNN}.jpg` 採番は slideshow 経路で使わない |
| R3 | pause / apply 失敗 / prepare 失敗 tick で、当該 tick の `_slideshow_tick_generated_files` を rollback 削除する |
| R1 | dual-source 継続実行中、各 tick 終了時に作業ディレクトリへスロット外ファイルを残さない（§6.2 の掃除） |
| R4 | `on_slideshow_stop` 時の作業ディレクトリと追跡 state の扱い（下記） |

禁止される挙動（R1–R3 / R5 で防止）:

- pause tick で optimize のみ成功し rollback しない
- apply 失敗で生成ファイルを残す
- ピクチャ根と作業ディレクトリ未分離で手動 Optimize と採番競合
- 存在ベース採番で orphan が次 tick の番号を押し上げる

#### R4（`on_slideshow_stop`）

stop 時は作業ディレクトリ内のスロットファイル **を削除しない**。

- XFCE 系は最終 tick で apply 済みの path を `xfconf-query` が参照しうる。stop 直後に削除すると、設定上の壁紙 path が無効になる。
- stop 時に `_slideshow_active_generated_files` と `_slideshow_tick_generated_files` は **クリア**する（次回 start で古い追跡を引き継がない）。
- 次回 `on_slideshow_start` では、R2 スロット path へ上書きする前提で作業ディレクトリを用意する（必要なら `mkdir -p`）。R1 掃除は各 tick 終了時に継続する。

### 6.6 Registry 連動実行

[source-spec](../source/harite-source-spec.md) の catalog と GUI slideshow 実行の接続。

#### start 前の resolve

`on_slideshow_start`（および tray からの start が同経路の場合）の **画像収集より前**に次を行う。

1. in-memory catalog を参照する（この時点で disk からの再 load は必須ではない）。
2. 実行 L/R が参照する **すべての `remote-*`** source について `sync_remote_source`（[source-spec §12.4](../source/harite-source-spec.md)）。
3. `slideshow_profile_id` が設定されていれば `resolve_profile_members` で L/R path と tracking id を揃える。
4. 各 side で `slideshow_source_id_l` / `slideshow_source_id_r` が設定されていれば `resolve_source` で当該 side の `slideshow_srcdir_*` を上書きする（profile 展開と矛盾する場合は **profile 優先**）。
5. `resolve_*` が `ValueError` なら **start failure** とし、slideshow は開始しない。
6. 確定した `slideshow_srcdir_l/r` で §2 の directory 検証と `collect_slideshow_input_images` を行う。

`remote-*` の cache directory は `local-dir` と同型の slideshow 入力 directory として扱う（[source-spec §12.5 / §15.2](../source/harite-source-spec.md)）。

手動 Srcdir のみの side（tracking key 空）は、手順 2 をスキップし、既存 `slideshow_srcdir_*` を検証する。

#### remote source と Mode

[source-spec §12.5](../source/harite-source-spec.md) が正本。要約:

- **CODH**: tick 前に cursor で次 URL を選び画像 GET → `latest.*` 上書き。cache は 1 枚だが Slideshow Mode（sequential / random）が有効。
- **JMA**: tick 前に `list.json` で filename を確認し、変化時のみ PNG 等画像ファイルを取得する。Slideshow Mode は **作用しない** — cache は `latest.*` 1 枚のため `sequential` / `random` 切替で見た目は変わらない。
- **NDL**: tick 前に §15.3.4 と同型で `randomwithfacet` → IIIF GET → `latest.jpg` 上書き。Slideshow Mode は **作用しない** — cache は `latest.*` 1 枚のため `sequential` / `random` 切替で見た目は変わらない。
- **`local-dir`（複数枚）**: 従来どおりファイル列に Mode を適用。L/R は独立 cycle。

#### tick 前の remote sync

各 tick の **画像収集より前**に、当該 side の `remote-*` について [source-spec §12.4](../source/harite-source-spec.md) の provider 別 tick sync を行う。順序:

1. remote tick sync（JMA: §15.1.3、CODH: §15.4.5、NDL: §15.3.4）
2. `collect_slideshow_input_images`
3. `select_next_image`（Mode）
4. optimize / apply

tick 中の画像 GET 失敗（CODH 等）は前回 `latest.*` を維持して tick 継続する。

#### tick 中（registry）

- catalog の再 load も、id からの再 resolve も行わない。start 時に確定した path で directory を参照する。
- directory がアクセス不能になった場合、または画像 0 件になった場合は、**新規取り決めを設けず** §9 および [source-spec §7.5](../source/harite-source-spec.md) / [core-spec §7](../core/harite-core-spec.md) の既存 failure 分類に従い **stop / failure** とする（display loss による **pause** とは別軸）。
- start 条件（L/R 両方必須）・dual-source cycle 算法・L/R 独立 `SlideshowCycleState` は **変更しない**。

#### 実行中の catalog 変更

[source-spec §7.6](../source/harite-source-spec.md) が正本。実行に影響する保存内容があれば GUI は **slideshow stop** する。

#### path 種別（NAS / GVFS）

[source-spec §4.1](../source/harite-source-spec.md)。GVFS path の slideshow 成功は保証しない。Windows UNC / ドライブレターは `local-dir` のまま利用する。

## 7. CLI `slideshow` command の責務

- 入力 directory 1 件または最大 2 件からの画像収集（dual 時は L/R 各 side で独立 cycle 状態）
- サイクル実行（MAT-11 同型: 毎 cycle `run_slideshow_optimize` → apply）
- settings / `--settings-file` から optimize 一式を読み、GUI `form_state` と同型で optimize に渡す
- plugin 解決と各サイクルの実 apply（single: composite 1 枚、dual: auto-split map または Windows Span）
- `Slideshow start` / `Slideshow cycle` / `Slideshow interrupted by user` 実行メッセージ出力

CLI `slideshow` command の特徴:

- 開始後は各サイクルで `apply(...)` を呼ぶ。
- CLI `slideshow` の `--mode` 既定値は `sequential` である。
- plugin が例外を投げてもループ全体を即停止せず、そのサイクルの `apply_error` カウンタを 1 件増やす。
- plugin が `False` を返した場合は、そのサイクルの `apply_failed` カウンタを 1 件増やす。
- これらのカウンタは各サイクルの途中で保持され、bounded run や将来の明示完了経路がある場合にだけ `Slideshow completed` 行の実行メッセージ要約として出力する。
- `log_level` option は持たず、固定方針は旧 `normal` 相当とする。
- 継続実行の通常停止は `Ctrl+C` による `Slideshow interrupted by user` を中心に扱い、`Slideshow cycle=...` は失敗サイクルでだけ出す。
- したがって成功のみの実 apply では cycle 行を出さない。

集計規則の補足:

- 実 apply 時の `apply_ok`, `apply_failed`, `apply_error` はサイクルごとの結果分類であり、1 サイクルで多重加算しない。

## 8. 出力と観測面

- CLI `slideshow` command は stdout に実行メッセージを出す。
- CLI は固定の自然な user-facing 実行メッセージ方針を採る。現行英語表記では `Slideshow ...` を使い、全部大文字の prefix は使わない。
- GUI は status, history, output display を併用する。
- CLI も §6.1 の作業ディレクトリ `{Pictures}/Harite/slideshow/` へ optimize 出力を書く（手動 Export 成果物とは別）。

GUI feedback の補足:

- GUI runtime は `status_message` を 1 行目、`last_error` を 2 行目へ同期する。
- ただし `last_error == status_message` のときは 2 行目を抑止し、同一内容を二重表示しない。
- 状態表示 / tab title は `running|paused|stopped` の 3 状態を共有する。
- `Slideshow current`（label / owner `slideshow_current_display`）は §6.0 および [gui-spec §6.1](../gui/harite-gui-spec.md) の path 省略規則に従う。full path の生表示は観測面として採用しない。

CLI の主な観測値:

- 開始時の `input`, `images`, `interval_sec`, `mode`, `plugin`
- 各サイクルの selected image
- `apply_ok`, `apply_failed`, `apply_error`
- 完了時の total サイクル数

完了時 summary の見方:

- 実 apply では `apply_ok`, `apply_failed`, `apply_error`, `apply_failed_total` が `Slideshow completed` 行へ出る。

固定方針では start 行と completed 行が基本であり、cycle 行は failure が起きたサイクルでだけ観測される。

## 9. 安定性上の注意点

### dual-source 起動要件（GUI）

| plugin | display 条件 | apply 経路 |
| --- | --- | --- |
| `linux` | 2 枚以上検出 | per-monitor map（§6.2 分割スロット） |
| `windows` | 2 枚以上検出 | wide composite + OS **Span**（single-file apply、`windows_span`） |
| その他 | — | dual-source **非対応**（start 前に拒否） |

- Windows では linux plugin を要求しない。`resolve_apply_settings` が `per-monitor-auto-split` を single-file に解決する（[plugin-spec §4.1](../plugins/harite-plugin-spec.md)）。
- Settings `windows_apply_span` が有効なとき、各 tick の apply 前に HKCU Span を best-effort 設定する。registry **自動復元は行わない**（slideshow 中の書き戻しは表示崩れリスク）。
- plugin exception は apply_error 系として扱う。
- input directory が空なら起動前に止める。

追加の注意点:

- `interval_sec < 1` は helper 側でも不正として扱う。
- random 選択では候補が複数ある場合、直前と同じ画像を避ける。
- `KeyboardInterrupt` は CLI では異常終了ではなく、ユーザー中断として `0` 扱いにする。
- GUI dual-source auto-split では、display 条件喪失が一時的なら pause で吸収し、raw な `ValueError` をそのまま user-facing failure にしない。

### registry / directory の実行時失敗

| タイミング | 条件 | 扱い |
| --- | --- | --- |
| start 前 | `resolve_source` / `resolve_profile_members` 失敗 | start failure（§6.6） |
| start 前 | `collect_slideshow_input_images` が空 directory / 不存在 | start failure（§2） |
| tick 中 | start 時 path が inaccessible または画像 0 件 | stop / failure（source-spec §7.5 既存。pause ではない） |
| tick 中 | catalog 変更が [source-spec §7.6](../source/harite-source-spec.md) に該当 | slideshow stop |

片側のみ inaccessible になった場合の **可能 side のみ継続**は **採用しない**（全体 stop）。

## 10. core / GUI / CLI との境界

- スライドショー helper の最小ループは `slideshow.py` にある。
- GUI 実運用の状態管理は `MainWindow` と GTK runtime に跨る。
- core / apply target 解決は [core-spec](../core/harite-core-spec.md) を参照する。
- source registry / start 前 resolve / catalog 変更は [source-spec](../source/harite-source-spec.md) §6.4, §7.6 および本書 §6.6。

境界整理:

- slideshow helper は画像選択と cycle 制御を持つが、GUI 特有の state 表示や tray 制御は持たない。
- CLI `slideshow` command は helper の呼び出しと実行メッセージ出力を担う。
- GUI は helper だけでは表現しきれない dual-source, auto-split, status 表示を追加で担う。
- apply target の解決は core が担い、選択済み plugin がその target を受け付けるかと実 apply の成否は plugin 契約側で扱う。
- tray は slideshow owner state を直接持たず、GUI owner が持つ running / paused / stopped を補助操作面として起動・停止する。

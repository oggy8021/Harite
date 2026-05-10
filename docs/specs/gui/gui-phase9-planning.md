# GUI Phase 9 Planning

最終更新: 2026-05-10

## 位置づけ

- 本書は [docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md) のうち、Phase9 を単独 planning として具体化する文書である。
- Phase9 では新機能追加より先に、GUI 中核の責務集中をほぐし、Phase10 / Phase11 を載せられる構造へ整える。
- 主対象は [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) と [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) である。

## 現状認識

### MainWindow 側の責務集中

- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) は、単一クラスの中に以下を抱えている。
- 入力管理: `on_pick_input`、`on_change_input_text`、`on_clear_input`
- margins / margin text: `_current_margin_values`、`_margin_text_area`、`_update_margin_text_preflight_status`、`on_change_margins`、`on_change_margin_text_*`
- preview: `build_result_preview_state`、`build_optimize_cli_preview`
- optimize / apply flow: `on_save_as`、`on_optimize`、`_apply_latest`、`on_apply`
- settings / about / color: `on_open_settings_dialog`、`on_apply_settings`、`export_settings_config`、`on_about`、`on_set_color`
- watch: `_prepare_watch_apply`、`_apply_watch_selection`、`on_watch_start`、`on_watch_tick`、`on_watch_stop`

### GTK backend 側の責務集中

- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) は、単一 runtime backend の中に以下を抱えている。
- widget tree 構築: `GtkRuntimeSignalBackend.__init__`
- owner state 同期: `_sync_main_state_from_owner`、`_sync_input_state_from_owner`、`_sync_margins_state_from_owner`、`_sync_result_preview_from_owner`
- dialog proxy と dialog close/open 制御: save path / open image / srcdir / settings / color / about
- watch timer と watch bridge: `_start_watch_timer`、`_on_watch_timer_event`、`run_watch_cycle_once`
- event handler 群: `_on_*` 系が広く分散している

### 現代的な分け方としての前提

- 単純に「ファイルが大きいから半分に割る」ではなく、状態の所有者と副作用の出口を分ける。
- `MainWindow` は最終的に「画面状態の owner 兼 application coordinator」へ寄せ、細かな feature rule を外へ出す。
- GTK backend は「widget build」「owner sync」「dialog / timer / preview などの runtime service」「signal binding」に分ける。
- `ui_adapter` は大問題ではないため、Phase9 では rewrite せず、分割結果に合わせて契約面だけを整える。

## 分割方針

### 1. MainWindow は feature slice 単位で分ける

- `MainWindow` から最初に切る候補は以下とする。
- margins / margin text slice
- preview / CLI preview slice
- settings / about / color slice
- watch slice

### MainWindow 分割のねらい

- 状態更新ロジックを「関心ごと単位」で分離し、1 変更で 1 領域だけ追えば済むようにする。
- feature ごとのテストを MainWindow 全体から切り離しやすくする。

### MainWindow 分割後の期待形

- `MainWindow` は state holder と coordinator に寄せる。
- feature slice は `services` または `features` 配下へ逃がし、`MainWindow` からは明示的に呼ぶ。
- 既存 public handler 名は急に崩さず、まず中身だけ feature service へ委譲する。

## 2. GTK backend は UI composition と runtime behavior を分ける

- `GtkRuntimeSignalBackend.__init__` で widget を全面構築しているが、ここは組み立て責務が重すぎる。
- 分割候補は以下とする。
- widget composition
- owner-to-widget sync
- dialog coordinators
- preview renderer
- watch timer bridge
- signal handler binding

### GTK backend 分割のねらい

- runtime backend の変更時に、毎回 3000 行超を横断しなくてよい状態へ寄せる。
- dialog / preview / timer のような副作用境界を isolated にし、テストと差し替えを容易にする。

### GTK backend 分割後の期待形

- backend 本体は object registry と signal wiring の薄い coordinator に寄せる。
- dialog proxy 群は grouped module へまとめる。
- owner sync は `sync_*` 群としてまとめ、widget build から切り離す。
- preview 描画と watch timer は runtime service として明示分離する。

## 3. 分割順は「危険が小さい順」にする

- Phase9 は一気に class hierarchy を再設計しない。
- 以下の順を推奨する。

1. 純ロジック寄りの slice を外出しする
2. owner sync 群をまとめる
3. dialog coordinator を grouped module 化する
4. widget build を section builder 化する
5. 最後に `MainWindow` / backend の coordinator 化を仕上げる

### owner sync を先に切る理由

- 先に widget build 全面改修へ入ると、見た目 regressions と signal regressions が同時発生しやすい。
- 先に純ロジックと sync 群を外へ出せば、挙動を変えずに可読性を上げやすい。

## 4. legacy / compatibility は棚卸ししてから削る

- Phase9 では「謎の互換性」を感覚で消さない。
- 以下を棚卸し対象とする。
- fallback backend とその存在意義
- handler 名互換
- owner state から backend への暗黙依存
- legacy docs / glade 由来命名の残骸
- partial GTK environment を前提とした安全網

### 判断基準

- いま実際に使っているか
- テストや manual validation の前提になっているか
- 将来の Phase10 / Phase11 で必要になるか
- 単に過去互換の名目で残っているだけか

## 推奨モジュール境界

以下は Phase9 時点の推奨案であり、最初から完全到達を要求しない。

### MainWindow 側

- `main_window.py`: state owner / high-level handler entrypoint
- `main_window_margin_text.py` 相当: margins と margin text preflight
- `main_window_preview.py`: result preview / CLI preview
- `main_window_settings.py` 相当: settings / about / color
- `main_window_watch.py` 相当: watch state / watch apply bridge

### GTK backend 側

- `gtk_backend.py`: backend coordinator / object registry / signal wiring
- `gtk_runtime_builders.py`: widget builder facade / re-export
- `gtk_runtime_object_registry.py`: runtime object alias / registry mapping
- `gtk_layout_builders.py`: layout / shell / footer builder
- `gtk_tab_builders.py`: main tab / watch tab / margins tab builder
- `gtk_dialog_builders.py`: settings / color / about builder
- `gtk_runtime_file_dialog_flow.py`: input/open/srcdir/save-path dialog flow
- `gtk_runtime_margin_text.py`: margin text sanitization / return-key guard logic
- `gtk_runtime_margin_text_gtk.py`: margin text GTK styling / keypress bridge
- `gtk_runtime_owner_sync.py`: owner-driven UI sync orchestration helper
- `gtk_runtime_settings_dialogs.py`: settings / color / about runtime dialog orchestration
- `gtk_runtime_signal_wiring.py`: runtime signal binding enumeration
- `gtk_runtime_save_path_access.py`: save-path dialog/state alias access helper
- `gtk_runtime_state_labels.py`: current margin / align state label refresh helper
- `gtk_runtime_sync.py`: owner-to-widget sync 群
- `gtk_runtime_dialogs.py`: save/open/settings/color/about dialog coordinators
- `gtk_runtime_preview.py`: preview render helper
- `gtk_runtime_widget_access.py`: generic widget access / feedback helper
- `gtk_runtime_watch_ui.py`: watch UI refresh / start-stop handler flow
- `gtk_runtime_watch.py`: timer bridge / watch-specific runtime helper

### 契約面

- `ui_adapter.py` は handler map と dispatch factory の薄い責務に留める。
- Phase9 では新しい抽象層を増やしすぎず、既存 handler 契約を温存しながら内部委譲を進める。

## 実施済み反映

2026-05-10 時点で、Phase9 のうち以下は実装済みである。

- `MainWindow` の preview / CLI preview は [src/harite/gui/views/main_window_preview.py](src/harite/gui/views/main_window_preview.py) へ切り出し済み。
- GTK backend の owner sync 群は [src/harite/gui/adapters/gtk_runtime_sync.py](src/harite/gui/adapters/gtk_runtime_sync.py) へ切り出し済み。
- GTK backend の preview 反映 / 描画 helper は [src/harite/gui/adapters/gtk_runtime_preview.py](src/harite/gui/adapters/gtk_runtime_preview.py) へ切り出し済み。
- GTK backend の dialog proxy 群は [src/harite/gui/adapters/gtk_runtime_dialogs.py](src/harite/gui/adapters/gtk_runtime_dialogs.py) へ切り出し済み。
- GTK backend の watch timer / watch bridge は [src/harite/gui/adapters/gtk_runtime_watch.py](src/harite/gui/adapters/gtk_runtime_watch.py) へ切り出し済み。
- GTK backend の widget build は [src/harite/gui/adapters/gtk_runtime_builders.py](src/harite/gui/adapters/gtk_runtime_builders.py) を facade としつつ、[src/harite/gui/adapters/gtk_layout_builders.py](src/harite/gui/adapters/gtk_layout_builders.py) / [src/harite/gui/adapters/gtk_tab_builders.py](src/harite/gui/adapters/gtk_tab_builders.py) / [src/harite/gui/adapters/gtk_dialog_builders.py](src/harite/gui/adapters/gtk_dialog_builders.py) へ再分割済み。header / main tab compose-input-display / action-preview cluster / watch tab / margins tab / settings editor / color-about window / footer-status / runtime state labels / primary margin controls が builder 化済み。

- 現時点の GTK backend 本体 [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) は、object registry・signal wiring・dialog runtime coordination・handler 群の coordinator としての比重が以前より高い。
  - `__init__` では以下まで整理済みで、不要 unpack も縮小されて backend 本体は一段薄い coordinator に寄ってきている。
    - runtime state 初期化
    - window 構築
    - root / header / main composition
    - watch / margins tab composition
    - footer attach composition
    - dialog runtime bundle の downstream 受け渡し
    - section bundle 前提の object map 組み立て
    - section bundle 前提の signal wiring
    - dialog runtime 準備の helper 化
  - 外出し済みの grouped module は以下。
    - object map alias 列挙: [src/harite/gui/adapters/gtk_runtime_object_registry.py](src/harite/gui/adapters/gtk_runtime_object_registry.py)
    - signal wiring 列挙: [src/harite/gui/adapters/gtk_runtime_signal_wiring.py](src/harite/gui/adapters/gtk_runtime_signal_wiring.py)
    - file/dialog flow: [src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py)
    - save-path alias access: [src/harite/gui/adapters/gtk_runtime_save_path_access.py](src/harite/gui/adapters/gtk_runtime_save_path_access.py)
    - margin text の純粋ロジック: [src/harite/gui/adapters/gtk_runtime_margin_text.py](src/harite/gui/adapters/gtk_runtime_margin_text.py)
    - margin text の GTK bridge: [src/harite/gui/adapters/gtk_runtime_margin_text_gtk.py](src/harite/gui/adapters/gtk_runtime_margin_text_gtk.py)
    - owner-driven sync orchestration: [src/harite/gui/adapters/gtk_runtime_owner_sync.py](src/harite/gui/adapters/gtk_runtime_owner_sync.py)
    - settings / color / about runtime dialog flow: [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py)
    - watch UI 補助: [src/harite/gui/adapters/gtk_runtime_watch_ui.py](src/harite/gui/adapters/gtk_runtime_watch_ui.py)
    - generic widget access / feedback helper: [src/harite/gui/adapters/gtk_runtime_widget_access.py](src/harite/gui/adapters/gtk_runtime_widget_access.py)
    - current state label helper: [src/harite/gui/adapters/gtk_runtime_state_labels.py](src/harite/gui/adapters/gtk_runtime_state_labels.py)

## Workstream

### 1. 分割対象の棚卸し

- 目的:
  - `MainWindow` と GTK backend の責務塊を feature / runtime service 単位で列挙する。
- 成果物:
  - 分割対象一覧
- 現在地:
  - `MainWindow` と GTK backend の主要責務塊は列挙済みで、GTK backend 側は module 単位の切り出しまで着手済み。

### 2. MainWindow 委譲化

- 目的:
  - public handler 名を維持したまま、中身を slice へ逃がす。
- 成果物:
  - MainWindow 分割方針メモ
- 現在地:
  - preview / CLI preview は委譲化済み。margins / settings / watch は未着手または後続。
  - 2026-05-10 時点の追加判断として、Phase9 内での MainWindow 追加整理線は「margins / margin text は追加分離候補、settings と watch は判断先行で止める」を基本とする。
    - margins / margin text は `_current_margin_values`、`_margin_text_area`、`_update_margin_text_preflight_status`、`on_change_margins`、`on_change_margin_text_*` が比較的まとまった関心事を成し、pure logic と preflight 判定の外出し余地が大きい。
    - settings は `AppPreferences` と `form_state` / `preferences` / watch 設定へ横断反映しており、Phase9 時点では state owner との結びつきが強い。委譲先境界は説明可能だが、追加分離を close 必須にはしない。
    - watch は plugin 適用、optimize 実行、出力 cleanup、状態遷移が密に絡むため、Phase9 では「watch slice として分ける対象である」判断までを確定し、実装上の追加分離は後段判断でもよい。
    - したがって Phase9 close に必要な最小線は、preview 以外では margins / margin text を最有力追加分離候補として明示し、settings / watch は owner-coordinator 依存が強い slice として分離方針のみ確定しておくことで足りる。

### 3. GTK backend 分割

- 目的:
  - widget build / sync / dialog / preview / watch を grouped module 化する。
- 成果物:
  - GTK backend 分割方針メモ
- 現在地:
  - sync / preview / dialog / watch は grouped module 化済み。
  - widget build は facade + 責務別 module へ再分割済み。
    - header
    - main tab compose-input-display
    - action-preview
    - watch tab
    - margins tab
    - settings editor
    - color-about window
    - footer-status
    - runtime state labels
    - primary margin controls
  - backend `__init__` は coordinator 寄せを継続中で、受け口も section bundle 前提へ揃いつつある。
    - runtime state 初期化
    - window 構築
    - root-header-main composition
    - watch-margins composition
    - footer-attach composition
    - dialog runtime bundle pass-through
    - section bundle object-map assembly
    - section bundle signal wiring
    - dialog runtime 準備の helper 化
    - object map の alias 列挙は registry module へ退避済み
    - signal wiring の列挙は wiring module へ退避済み
    - file/dialog flow・save-path access・margin text pure/GTK split・owner-driven sync orchestration・settings-color-about flow・watch UI flow・generic widget access・current state label refresh もそれぞれ grouped module へ退避し始めている
    - 不要 unpack 縮小を含めて、残る大塊はさらに coordinator 寄せを継続する段階
  - 2026-05-10 時点の追加判断として、Phase9 close に必要な `__init__` 側の最小追加整理線は「section bundle 前提の helper 化まで」とする。
    - 現時点で backend ローカルに残る主な塊は `_build_dialog_runtime_widgets` 内の dialog widget / proxy 組み立て配線と `_configure_spin_button` のような小粒 helper であり、前者は dialog runtime 準備 helper の範囲、後者は backend 局所設定として扱える。
    - したがって Phase9 では、`__init__` から直接読める大塊を helper / section bundle 単位へ落とせていれば十分とし、これ以上の追加 module 化は close の必須条件にしない。
    - Phase10 以降で通常起動導線や runtime 境界を再整理する際に、dialog runtime assembly の更なる module 化や local helper の吸収を再判定する。

### 4. legacy / compatibility 監査

- 目的:
  - 互換の名目で残っているものを、維持・縮退・削除候補へ分ける。
- 成果物:
  - compatibility 監査メモ
- 現在地:
  - current runtime は repo 内の glade prototype を直接使わず、legacy UI 資産は [docs/legacy-ui/README.md](docs/legacy-ui/README.md) と [src/harite/gui/resources/README.md](src/harite/gui/resources/README.md) の方針どおり docs 側の証跡へ寄せる整理が進んでいる。
  - XFCE 自体は legacy ではなく、[docs/manual-validation-gate.md](docs/manual-validation-gate.md) のとおり current GUI 実機確認の正本環境として継続して扱っている。
  - GTK runtime fallback は [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) と [src/harite/gui/app.py](src/harite/gui/app.py) の現状どおり、legacy Glade を Gtk.Builder が実行時に消費できない場合と partial GTK environment で present / bind flow を維持する安全網として残している。
  - [src/harite/gui/app.py](src/harite/gui/app.py) の `--bind-ui-backend` / `--present-ui-window` で暫定と呼んでいる対象は XFCE 対応そのものではなく、framework-neutral な [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) と optional な GTK backend を明示 option で橋渡ししている bootstrap 導線である。
  - この bootstrap 導線の暫定解消条件は、owner の通常利用環境である XFCE で current GUI を追加 option や環境変数なしに既定導線から起動でき、backend bind / present の必要処理が利用者から隠蔽されることである。
  - handler 名互換は「legacy signal 名へ戻す」のではなく、[docs/manual-validation-gate.md](docs/manual-validation-gate.md) の受け入れ基準どおり current handler 名での dispatch / bind を正本として維持する方針が明文化済みである。
  - compatibility 項目の維持・縮退・削除判断は、Phase9 の中で一通り確定した。

#### compatibility 監査結果

| 項目 | 現状 | 判定軸 | 現時点の整理候補 | owner 判断 |
| --- | --- | --- | --- | --- |
| runtime fallback backend | [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) は legacy Glade 非依存の current runtime backend として機能し、[src/harite/gui/app.py](src/harite/gui/app.py) でも partial GTK environment の安全網として扱っている。ここでの暫定は XFCE 対応ではなく、framework-neutral な MainWindow と optional backend を明示 option で橋渡しする bootstrap にある | Phase9 内で安全網として維持するか、より薄い bind/present 専用層へ縮退するか | Phase9 では維持。XFCE は正本運用環境として残しつつ、option 依存 bootstrap の解消は Phase10 完了条件として扱う。backend 本体は巨大な何でも屋ではなく、GTK runtime の入口 / 接着点へ寄せ続ける | 維持 |
| ui_adapter の契約面 | `ui_adapter` は主問題ではないが、dispatch factory / handler map の名前合わせと signal 接続差異吸収を担う薄い層として残っている | Phase9 内で薄い契約層として維持するか、backend / MainWindow 直結へさらに寄せるか | Phase9 では薄い層として維持する。独立ファイルとして最後まで残すかは、Phase10 で通常起動導線を整理したあとに再判定する | 維持 |
| handler 名互換 | current handler 名での dispatch / bind を正本とし、legacy signal 名へ戻さない方針は [docs/manual-validation-gate.md](docs/manual-validation-gate.md) で固定済み | 入口互換を残す範囲をどこまで許すか | current handler 名を正本として維持し、legacy signal 名への回帰はしない。元々の移植方針とも整合するため、この方針で固定する | 維持 |
| legacy Glade / legacy UI 資産 | current runtime は repo 内の glade prototype を直接使わず、証跡は [docs/legacy-ui/README.md](docs/legacy-ui/README.md) と [src/harite/gui/resources/README.md](src/harite/gui/resources/README.md) の整理方針へ寄っている | 実装資産としては削除済み扱いを維持し、docs 側証跡のみ残すか | docs 側証跡のみ維持し、runtime 実装依存は増やさない。legacy Glade は復活させない方針で固定する | 維持 |
| partial GTK environment の安全網 | [src/harite/gui/app.py](src/harite/gui/app.py) は backend load / dispatch connect / present を non-fatal に扱っている | CI / headless / partial GTK での安全網を Phase9 内でどこまで維持するか | GTK 周りの一部失敗を即クラッシュ扱いにせず、起動継続できる安全網として維持する。OS から終了させられる場合を除き、GUI アプリ側はこの non-fatal 方針を保つ | 維持 |

## 初動タスク

1. `MainWindow` の handler 群を feature slice 単位へ分類する。
2. GTK backend の `_sync_*` / `_on_*` / dialog proxy / widget build を責務別に分類する。
3. public handler 契約を壊さずに移動できる最小単位を決める。
4. fallback / compatibility 項目を別紙で監査する。

## 初手 planning 時点の実装候補

### 当初推奨: GTK backend の owner sync 群から着手する

- 初手は preview 群よりも、GTK backend 側の owner sync 群をまとめる方を推奨する。
- 対象の中心は `_sync_main_state_from_owner`、`_sync_input_state_from_owner`、`_sync_margins_state_from_owner`、`_sync_result_preview_from_owner`、`_sync_watch_state_from_owner` である。

### 理由

- public handler 名や `MainWindow` の entrypoint を変えずに進めやすい。
- widget build や dialog 制御より局所的で、UI 崩れの波及範囲が比較的小さい。
- 現在の backend では owner から widget への反映責務が散っており、ここを束ねるだけでも読みやすさの改善が大きい。
- test も GTK runtime backend 側に多く存在し、focused validation を取りやすい。

### 当初の次点: preview 群の分離

- `MainWindow` の `build_result_preview_state` / `build_optimize_cli_preview` と、GTK backend の preview 反映をまとめて preview slice 化する案は次点とする。
- ただし preview は `MainWindow` と backend の両側にまたがるため、初手としては owner sync 群より edit surface が広い。

### 当初のブランチ候補

- `feature/gui-phase9-owner-sync-split`
- `feature/gui-phase9-gtk-sync-refactor`
- `feature/gui-phase9-backend-owner-sync`

## GTK backend の UI 状態反映処理 分割表

Phase9 の初手 planning 時点では、[src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) の `_sync_*` 群を以下のように分ける想定だった。

| 現在の関数 | 主責務 | 依存している owner 側状態 | 分割先の第一候補 | 初手対象 | 備考 |
| --- | --- | --- | --- | --- | --- |
| `_sync_input_state_from_owner` | 入力欄、Save/Optimize/Apply の活性状態、save path dialog open 状態を widget へ反映する | `input_path_l` / `input_path_r` / `can_optimize` / `can_apply` / `save_path_dialog_open` | `gtk_runtime_sync.py` の input sync 群 | yes | 反映対象が明確で、public handler 契約にも触れない |
| `_sync_main_state_from_owner` | margins / align / valign の基本 widget 状態を反映する | `form_state.margins` / `form_state.align` / `form_state.valign` | `gtk_runtime_sync.py` の main layout sync 群 | yes | `_parse_margin_values` と近いため、同時移動候補 |
| `_sync_margins_state_from_owner` | margin text mode / position / text / max lines と notebook page を反映する | `form_state.embed_info` / `embed_position` / `embed_text` / `embed_max_lines` | `gtk_runtime_sync.py` の margin text sync 群 | yes | `_refresh_margins_controls` と一体で寄せる方が自然 |
| `_sync_watch_state_from_owner` | watch srcdir / running / interval / output 表示を反映する | `watch_srcdir_l` / `watch_srcdir_r` / `watch_running` / `_watch_state_*` / `watch_interval_seconds` / `form_state.output_dir` | `gtk_runtime_watch.py` または `gtk_runtime_sync.py` の watch sync 群 | yes | 初手に含めてよいが、watch timer 制御までは同時移動しない |
| `_sync_result_preview_from_owner` | preview label / image / assist 表示を反映する | `build_result_preview_state()` の返り値 | `gtk_runtime_preview.py` | no | preview renderer と結び付きが強く、初手より 2 手目向き |
| `_sync_feedback_from_owner` | status / error を footer feedback へ反映する | `status_phase` / `status_message` / `last_error` | `gtk_runtime_sync.py` の feedback sync 群 | yes | 小粒で切り出しやすく、他 sync 群の足場になる |

## 初手 planning 時点で backend 本体に残すもの

- object registry (`self._objects` 等)
- signal handler registry (`self._signal_handlers`)
- `connect_signals` / `connect`
- 分割先 module を呼ぶ薄い coordinator

## 初手 planning 時点ではまだ動かさない想定だったもの

- `GtkRuntimeSignalBackend.__init__` の widget 全面構築
- dialog proxy 群そのもの
- watch timer の start / stop / GLib 接続
- preview renderer 本体 (`_set_preview_widget`、`_build_preview_crop_boxes` など)

上記は初手 planning 時点の安全側想定であり、このうち dialog proxy・watch timer・preview renderer・widget build の一部 section builder 化は 2026-05-10 時点で実施済みである。

## 完了済み slice

### feature/gui-phase9-ui-state-sync

1. `_sync_input_state_from_owner`、`_sync_main_state_from_owner`、`_sync_margins_state_from_owner`、`_sync_watch_state_from_owner`、`_sync_feedback_from_owner` を grouped module へ移した。
2. `gtk_backend.py` 側には wrapper と薄い委譲を残した。

### feature/gui-phase9-preview-state-sync

1. `MainWindow` の `build_result_preview_state` / `build_optimize_cli_preview` を preview module へ移した。
2. GTK backend の preview 反映 / 描画 helper を preview module へ移した。

### feature/gui-phase9-gtk-backend-responsibility-split

1. dialog proxy 群を dialog module へ移した。
2. watch timer / watch bridge を watch module へ移した。
3. widget build の一部を builder module へ移し、header / action-preview cluster / watch tab / margins tab を section builder 化した。

### feature/gui-phase9-gtk-builder-sections

1. main tab の compose / input / display 構築を builder module へ移した。
2. settings editor / color window / about window / footer-status row を builder module へ移した。
3. runtime state labels と primary margin controls を builder module へ移し、`gtk_backend.py` の `__init__` をさらに coordinator 寄りへ寄せた。
4. `gtk_runtime_builders.py` の集中を解くため、layout / tab / dialog builder へ再分割し、`gtk_runtime_builders.py` は互換 facade に切り替えた。
5. backend 側の object map 組み立て / signal wiring / dialog runtime 準備を helper 化し、`__init__` の残塊整理を継続した。

### 現在の残件

- 現時点の残件は close 判断の文書化のみであり、実質論点は以下の照合で解消した。

### Phase9 close 判断

- [docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md) の Phase9 完了条件 1「`MainWindow` の責務分離方針が確定している」について:
  - preview / CLI preview は委譲化済みであり、preview 以外は margins / margin text を最有力追加分離候補、settings / watch は分離方針確定までを Phase9 の到達線としたため、責務分離方針は確定している。
- 完了条件 2「GTK runtime backend の大ブロックが分割可能な単位で整理されている」について:
  - sync / preview / dialog / watch / builder 再分割 / object registry / signal wiring / dialog runtime helper 化まで進んでおり、`__init__` 側の最小追加整理線も helper / section bundle 単位までで十分と確定したため、満たしている。
- 完了条件 3「legacy / compatibility 項目の維持・縮退・削除候補が文書化されている」について:
  - Workstream 4 の compatibility 監査結果で runtime fallback backend / `ui_adapter` / handler 名互換 / legacy Glade / partial GTK safety net の判断が一通り確定しており、満たしている。
- 完了条件 4「Phase10 / Phase11 に送るための境界が説明可能になっている」について:
  - Phase10 には option 依存 bootstrap の解消と通常起動導線整備を送り、Phase11 には OS integration を送る境界が [docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md) と本 planning の両方で説明可能である。
- 結論:
  - 2026-05-10 時点の planning / 実装反映 / compatibility 判断を前提に、Phase9 は close 可能と判断する。
  - 以後の追加改善候補は Phase9 の未完了条件ではなく、Phase10 以降で扱う通常起動導線整備・visual aid・OS integration 側の論点として扱う。

## 非目的

- Phase9 中に GUI の見た目 final polish を完成させること。
- icon 導入や tray / indicator 実装まで同時に進めること。
- MVC や MVVM などの名称を先に決めて、それへ無理に当てはめること。

## 完了条件

- `MainWindow` と GTK backend の分割対象が文書として説明可能である。
- 委譲先の単位と分割順が決まっている。
- legacy / compatibility の監査観点が明文化されている。
- Phase10 / Phase11 へ送る前提として、GUI 中核をどう modernize するかの道筋が合意されている。

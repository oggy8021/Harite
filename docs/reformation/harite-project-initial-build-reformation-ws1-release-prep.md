# Harite Project Initial Build Reformation WS1 Release Prep

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 1 を具体化する子文書である。
- 主題は、初期製造を `1.0.0` として出荷可能な状態へ寄せるための仕上げ、掃除、packaging、sdist、release judgement である。
- docs 再編や仕様書本文の執筆は本書の主責務ではない。

## この stream で固定すること

- 出荷前に消すもの、隠すもの、残すものを区別する。
- packaging と配布物の成立条件を明示する。
- `1.0.0` 判定に必要な最小 release 証跡を定める。
- 別紙の大部 checklist を増やさず、この WS 文書と chat 上の判断記録で回せる形にする。

## 対象

- 起動時メッセージ
- 出荷時に不要な debug / 暫定表示
- `1.0.0` 前に落とすべき code residue / skeleton / placeholder / legacy alias
- `pyproject.toml`
- package data
- entrypoint
- sdist / release 実務
- CHANGELOG / release notes / version judgement

## 非対象

- docs 全体の情報設計
- 常設仕様書の章立て設計
- post-1.0.0 機能棚卸し

## 現時点の論点

### 1. 起動時メッセージをどう扱うか

- 削除でよいもの
- 開発時のみ見せるもの
- 通常利用でも残すべきもの

### 2. packaging の成立条件をどこまでに置くか

- sdist が作れること
- entrypoint が配布物でも自然に使えること
- GUI resource / icon resource が欠落しないこと
- README や release 文書と配布実態が矛盾しないこと

### 3. `1.0.0` judgement の最小証跡を何にするか

- 配布構成の確認
- バージョン表記と release notes の整合
- 必要最小限の回帰確認
- owner judgement をどこへ残すか

### 4. `1.0.0` 前に消す code residue をどこまで扱うか

- docs 再編や仕様書化ではなく、製品を閉じる前の掃除として扱う。
- 「敢えて残してきたが、今の current Harite には不要寄り」のものは WS1 で扱う。
- WS2 / WS3 へ送らず、`1.0.0` 前に消す・残すを明示する。
- 利用者根拠のない互換層への退避は採らない。不要な legacy / residue は、互換のために温存するのではなく削除前提で扱う。

## 現時点の観測

### 1. 起動時メッセージの主要発生箇所

- [src/harite/gui/app.py](src/harite/gui/app.py) と [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の通常起動に関わる `print(...)` は削除済みである。
- これにより、release build 前提では GUI 起動時の常設 stdout ノイズは解消済みとみなしてよい。
- 一方で `MainWindow` の通常状態通知は status row / feedback として内部状態へ寄せており、WS1 では「CLI/stdout に出す必要があるもの」と「GUI 内 state 表示で足りるもの」を分ける必要がある。

#### 棚卸し対象一覧

`app.py` の出力:

- 現在、常設の `print(...)` は残っていない。

`main_window.py` の出力:

- 現在、常設の `print(...)` は残っていない。

#### 暫定分類

- 出荷前に削除候補:
  - 現時点の主対象は解消済みであり、`show()` 末尾の skeleton/debug 出力 5 件、`app.py` の `... ready` 系 3 件、`... skipped` 系 5 件は削除済み。
- 条件付き保持候補:
  - 現時点では常設 stdout 出力として残している項目はない。

### 2. packaging の現状

- [pyproject.toml](pyproject.toml) では project 名は `harite`、version は `0.1.3`、script entrypoint は `harite` / `harite-gui` になっている。
- package data は `"harite.gui" = ["resources/**/*"]` として GUI resource 一式を含める構成になっており、tray / application icon の packaging 方針とは整合している。
- したがって WS1 の主論点は「package data が未設定」ではなく、「`1.0.0` 出荷物として十分な資産が本当に全てこの定義で拾われるか」と「sdist/wheel 観点の最終確認をどこまで再実施するか」にある。

#### `sdist/wheel` で見る資産群

- Python package 本体:
  - `src/harite/*.py`
  - `src/harite/gui/**/*.py`
  - CLI / GUI entrypoint の実体である [src/harite/cli.py](src/harite/cli.py) と [src/harite/gui/app.py](src/harite/gui/app.py)
- GUI runtime resource:
  - [src/harite/gui/resources/README.md](src/harite/gui/resources/README.md)
  - `src/harite/gui/resources/icons/product/*.svg`
  - `src/harite/gui/resources/icons/lucide/*.svg`
- project metadata / 配布説明:
  - [pyproject.toml](pyproject.toml)
  - [README.md](README.md)
  - [LICENSE](LICENSE)
  - [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
  - 配布手順の現行ベースである [docs/release-delivery.md](docs/release-delivery.md)

#### 現時点の暫定資産一覧

- CLI 側の最低限確認対象:
  - `harite` entrypoint
  - core package (`core.py`, `plugins.py`, `watch.py`, `preferences.py`, `workspace.py` など)
- GUI 側の最低限確認対象:
  - `harite-gui` entrypoint
  - GTK runtime backend / adapter 群
  - tasktray adapter
  - application / tray icon を含む `resources/icons/product/`
  - header icon を含む `resources/icons/lucide/`

#### 暫定判断

- wheel では「entrypoint が起動できること」と「GUI resource が importlib.resources で欠落しないこと」を最優先に見る。
- sdist では、それに加えて「ビルド元として必要な source / metadata / resource が揃っていること」を見る。
- license 面では、Harite 本体の MIT を [LICENSE](LICENSE) で同梱し、vendor した Lucide icon の upstream notice を [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) で配布物へ残す。
- [src/harite/gui/resources/README.md](src/harite/gui/resources/README.md) の方針どおり、runtime で使う資産は `src/harite/gui/resources/` 配下に閉じているため、WS1 ではこの閉じ方が配布物でも維持されるかを確認対象にする。

### 3. release 実務文書の現状

- [docs/release-readiness-checklist.md](docs/release-readiness-checklist.md) は現時点で `v0.1.0` 前提のチェックリストであり、初回リリース時の証跡としては有用だが、そのまま `1.0.0` 判定の正本には使えない。
- 既存 checklist には `pytest`、`python -m build --sdist --wheel`、`.venv` 非依存実行確認、release notes 草案など、WS1 でも流用可能な確認項目が既にある。
- WS1 では、この既存 checklist を丸ごと再利用するのではなく、「`1.0.0` 判定へ流用する項目」「更新が必要な項目」「初回リリース固有で畳んでよい項目」を分ける必要がある。

#### 文書運用の暫定方針

- [docs/release-readiness-checklist.md](docs/release-readiness-checklist.md) は source material として読むに留める。
- `1.0.0` 向けには、再利用性の低い大部 checklist を育て直すのではなく、WS1 の論点に直結した軽量 release gate へ落とす方がよい。
- agent 作業上も必要なのは詳細な儀式一覧ではなく、「何が揃えば出せるか」の判定軸が少数で固定されていることである。
- 現運用では、WS / 事前文書で大半の論点が既に押さえられており、残差分は chat 欄の判断記録で十分追えるため、独立 checklist の常設価値は高くない。

### 4. version judgement の現状

- [pyproject.toml](pyproject.toml) の version はまだ `0.1.3` であり、`1.0.0` へ上げる判断そのものは未反映である。
- したがって WS1 では、version bump を先に行うのではなく、「何が揃ったら `1.0.0` に上げるか」を先に固定する。

### 5. release 面の整合状況

- [pyproject.toml](pyproject.toml) の version は `0.1.3`、[CHANGELOG.md](CHANGELOG.md) も `0.1.3 (2026-05-16)` まで更新されており、この 2 つは現時点で整合している。
- [docs/release-notes-draft.md](docs/release-notes-draft.md) は `v1.0.0 draft` として current 化済みであり、stale 状態は解消した。
- そのため Gate 3 の現時点の主な未充足は「最終 version をいつ `1.0.0` に上げるか」と「release note 上で何を最終同梱範囲として言い切るか」に寄っている。
- WS1 では、release note 草案を土台にしつつ、最終版で確定させる文言の境界を詰める。

### 6. code residue の初期観測

- marker ベース検索では、当初 `skeleton` / `placeholder` / `legacy` / `WallPosit` / `Debug:` 系の名残が複数箇所に見えていたが、product surface に近いものは段階的に解消している。
- この中には「単なる docstring 上の古語」と「実際の product surface に見えてしまう残骸」が混在しているため、WS1 では後者を優先して消す。

#### 初期候補

- product surface に見えるため優先度が高い候補:
  - 現時点では、product surface に直接見える大きな residue はおおむね一巡した。
- product の読みを濁すため次点で整理したい候補:
  - legacy Glade / fallback / debug overlay のように、実装安全策と残骸が近接している層
- すぐ消すとは限らない候補:
  - legacy Glade 互換や debug overlay のように、runtime safety / 開発補助として役割が残っているもの

#### 解消済み

- [src/harite/gui/adapters/gtk_tab_builders.py](src/harite/gui/adapters/gtk_tab_builders.py) の `Debug: apply is immediate` は、中立な product 文言へ置換済み。
- [src/harite/gui/app.py](src/harite/gui/app.py) / [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) / [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py) / [src/harite/gui/adapters/gtk_runtime_object_registry.py](src/harite/gui/adapters/gtk_runtime_object_registry.py) に残っていた `WallPosit_MainWindow` は削除済み。
- [src/harite/gui/app.py](src/harite/gui/app.py)、[src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py)、[src/harite/cli.py](src/harite/cli.py)、[src/harite/watch.py](src/harite/watch.py) の `skeleton` / `placeholder` 文言は current wording へ更新済み。
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) の `HARITE_DEBUG_LAYOUT` / debug layout overlay は削除済み。
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) の未使用 `Gtk.Builder` / `ui_file` / runtime Glade fallback 分岐は削除済みであり、GTK signal backend は current runtime backend 直結に整理済み。
- [src/harite/gui/adapters/gtk_runtime_signal_wiring.py](src/harite/gui/adapters/gtk_runtime_signal_wiring.py) の mandatory widget wiring に残っていた broad `except Exception: pass` は削除済み。
- [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py) の current runtime handler map からは legacy save/settings alias は既に消えており、対応する legacy 前提テストも整理済み。
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) / [src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py) の dialog destroy notify に残っていた broad catch は削除済みで、close handler failure は伝播する contract に揃えた。
- [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) の settings/color/about open helper に残っていた silent swallow は削除済みで、getter / notice build failure は outer feedback で `...: error` として見える contract に揃えた。
- [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py) の tray icon update / binding discovery / resource fallback は、broad catch ではなく API 差・import failure・resource missing に限定した fallback へ整理済み。
- [src/harite/gui/adapters/gtk_runtime_preview.py](src/harite/gui/adapters/gtk_runtime_preview.py) の preview helper は、broad catch ではなく conversion / expected image-load failure に限定した fallback へ整理済みで、unexpected runtime failure は伝播する contract に揃えた。
- [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) / [src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py) の legacy callback signature fallback は削除済みで、current handler contract から外れた呼び出しは error として表面化する。
- [src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py) の watch srcdir confirm も owner 解決を backend の正規 helper に揃え、局所 `__self__` 直読みを残さないようにした。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の unused な broad handler fallback は削除済みで、input pick / watch srcdir 選択 / input clear は current side-required contract に、margin change は current widget-value contract に、save path / settings load は explicit-path contract に揃えた。
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) の direction position bridge は `_on_direction_pressed` / `_on_direction_toggled` で unexpected callback failure を silent swallow せず、`Position: error` feedback として表面化するようにした。
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) の save path bridge は `_on_save_clicked` で unexpected `on_save_as` failure を silent swallow せず、`SavePath: error` feedback として表面化するようにした。
- [src/harite/gui/adapters/gtk_runtime_dialogs.py](src/harite/gui/adapters/gtk_runtime_dialogs.py) の color dialog GDK probe は optional import/version failure だけを fallback 扱いにし、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_dialogs.py](src/harite/gui/adapters/gtk_runtime_dialogs.py) の color conversion fallback も絞り、embedded/native color sync では invalid conversion だけを吸い、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_dialogs.py](src/harite/gui/adapters/gtk_runtime_dialogs.py) の native notice host probe でも internal child 探索は signature mismatch だけを fallback 扱いにし、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_dialogs.py](src/harite/gui/adapters/gtk_runtime_dialogs.py) の parent/native-host probe も同様に signature mismatch だけを fallback 扱いにし、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_margin_text_gtk.py](src/harite/gui/adapters/gtk_runtime_margin_text_gtk.py) の margin-text GTK helper も optional import/version failure だけを fallback 扱いにし、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_watch.py](src/harite/gui/adapters/gtk_runtime_watch.py) の GLib probe も optional import/version failure だけを fallback 扱いにし、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_preview.py](src/harite/gui/adapters/gtk_runtime_preview.py) の GdkPixbuf probe も optional import/version failure だけを fallback 扱いにし、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py) の GTK/AppIndicator probe も import/version failure だけを fallback 扱いにし、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) の GTK runtime/bootstrap probe も import/version failure だけを wrapper 化し、unexpected runtime failure は握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_watch_ui.py](src/harite/gui/adapters/gtk_runtime_watch_ui.py) の watch interval dispatch は current `int seconds` contract に揃え、owner 非接続時だけ widget を渡す legacy signature fallback を削除した。
- [src/harite/gui/adapters/gtk_runtime_watch_ui.py](src/harite/gui/adapters/gtk_runtime_watch_ui.py) の watch start/stop wrapper も expected callback/input failure だけを `Watch: error` へ載せ、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_watch.py](src/harite/gui/adapters/gtk_runtime_watch.py) の watch tick callback wrapper も expected signature mismatch だけを `Watch: error` へ載せ、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) の settings save wrapper も expected signature/input failure だけを `SettingsSave: error` へ載せ、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) の settings apply wrapper も expected signature/input failure だけを `SettingsApply: error` へ載せ、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) の color/about open wrapper も getter failure は従来どおり feedback へ載せつつ、callback invocation では expected signature mismatch だけを `Color: error` / `About: error` へ載せ、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) の color apply/confirm wrapper も expected callback/input failure だけを `Color: error` へ載せ、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/views/main_window_preview.py](src/harite/gui/views/main_window_preview.py) の result preview display-settings fallback も expected `ValueError` だけに絞り、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の startup default-settings load も expected file/config failure だけを skip 扱いにし、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の Windows Pictures known-folder probe も expected platform/OS failure だけを fallback 扱いにし、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の explicit settings-file load も expected file/config failure だけを status error 化し、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の settings-file save も payload build と file write を分離し、expected save/write failure だけを status error 化して、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の watch auto-split prepare も expected validation failure だけを watch error 化し、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の Save As export も expected validation failure だけを save error 化し、unexpected runtime failure は黙って握り潰さないようにした。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の optimize 実行も expected validation failure だけを optimize error 化し、unexpected runtime failure は黙って握り潰さないようにした。

#### 現時点の扱い方針

- 初期候補は、原則として `1.0.0` 前に削除対象として扱う。
- 「互換層へ閉じ込める」は、実利用者や保守上の必然が確認できる場合だけに限る。
- 現時点ではその根拠が見えていないため、残っている residue 候補も温存ではなく削除側で読む。

#### 次の主候補

- active code よりも test / comment / historical wording 側に残る legacy 前提を落とす層
- runtime safety と residue が近接していて、削除境界を切りたい層
- preview / tray adapter 以外に残る capability fallback や historical wording が、本当に runtime safety として必要かを切り分ける層

## `1.0.0` 少数 gate

### Gate 1. 起動ノイズと暫定表示の整理

- 通常利用の GUI 起動で、skeleton/debug 出力が stdout に残っていない。
- `ready` 系の起動メッセージは release build 前提では外れている。
- 例外的に残す診断がある場合も、通常利用時の常設ノイズではなく、必要性を説明できる。
- product surface に見える code residue も、`1.0.0` 前に整理対象へ含める。
- 証跡の置き場:
  - 本文中の整理判断
  - 必要なら chat 上の owner/agent 判断ログ

### Gate 2. packaging / resource / license 成立

- `harite` / `harite-gui` entrypoint が配布物観点で成立している。
- 本体 Python package と `src/harite/gui/resources/` 配下の runtime asset が配布物で欠落しない。
- [LICENSE](LICENSE) と [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) が配布物に残る。
- 証跡の置き場:
  - [pyproject.toml](pyproject.toml)
  - [README.md](README.md)
  - [docs/release-delivery.md](docs/release-delivery.md)
  - 本文中の packaging 判断

### Gate 3. release 面の整合

- version、CHANGELOG、release notes 草案、配布説明の間で大きな矛盾がない。
- `1.0.0` として何を出すか、何をまだ含めないかが説明できる。
- 証跡の置き場:
  - [pyproject.toml](pyproject.toml)
  - [CHANGELOG.md](CHANGELOG.md)
  - [docs/release-notes-draft.md](docs/release-notes-draft.md)
  - 本文中の version / release judgement

現時点の評価:

- [pyproject.toml](pyproject.toml) と [CHANGELOG.md](CHANGELOG.md) は `0.1.3` で整合している。
- [docs/release-notes-draft.md](docs/release-notes-draft.md) は `v1.0.0 draft` として更新済みであり、草案不在は解消した。
- ただし final release の version / scope はまだ未確定であり、Gate 3 は完全充足前の段階にある。

### Gate 4. owner 判定に必要な最小確認が揃っている

- owner が実施するテスト・実機確認・Git 操作の対象が過不足なく見えている。
- agent 側では、release 判定前に不足している確認項目を列挙できる。
- 判定に必要な残論点が、WS2 以降の論点と混線していない。
- 証跡の置き場:
  - この WS1 文書
  - 関連する release / manual validation 文書
  - chat 上の最終判断ログ

## WS1 の暫定判断

- 起動時メッセージは、まず [src/harite/gui/app.py](src/harite/gui/app.py) の `print(...)` 群と [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) 末尾の debug 出力を出荷前整理の一次対象とみなす。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の `show()` 末尾出力は削除済みであり、Gate 1 の一段目は通過済みとみなしてよい。
- [src/harite/gui/app.py](src/harite/gui/app.py) の `ready` 系、`skipped` 系、window presentation skipped は stdout から外したため、Gate 1 の常設起動ノイズ整理は一旦完了扱いでよい。
- packaging は resource 同梱方式そのものを作り直す段ではなく、既存 `pyproject.toml` を前提に `sdist/wheel` の最終確認条件を再定義する段として扱う。
- packaging の最小成立条件は、`harite` / `harite-gui` entrypoint、本体 Python package、`src/harite/gui/resources/` 配下の runtime asset が配布物で欠落しないことである。
- packaging の license 成立条件は、自前 MIT と vendored Lucide notice の両方が配布物に残ることである。
- release 判定文書は [docs/release-readiness-checklist.md](docs/release-readiness-checklist.md) を source material として参照しつつ、`1.0.0` 用には少数 gate の軽量正本へ縮退させる前提でよい。
- release 証跡は、必要最小限なら WS1 本文と関連文書、補足は chat 上の owner/agent 判断ログで足りる。
- `1.0.0` 判定は、上の 4 gate を満たしているかで見ればよく、別紙 checklist を前提にしない。
- Gate 3 については、release notes 草案の current 化は済んだため、現時点の主残論点は version bump と最終同梱範囲の確定である。
- code residue の扱いは WS2 / WS3 へ送らず、WS1 の掃除対象として `1.0.0` 前に消す前提で扱う。
- code residue の扱いは「削除」優先であり、利用者不在の互換層温存は採らない。
- version はまだ上げず、先に「起動ノイズ」「packaging 成立条件」「release 証跡」の 3 点を固める。

## 初動タスク

1. [src/harite/gui/app.py](src/harite/gui/app.py) と [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) に残る出荷前整理対象の `print(...)` を棚卸しする。
2. [pyproject.toml](pyproject.toml) の package data / entrypoint を前提に、`sdist/wheel` 最終確認で見る資産一覧を列挙する。
3. `1.0.0` 判定に必要な少数 gate を、この WS 文書内で説明可能な形へ絞る。
4. version bump 前に必要な gate と、その証跡の置き場を文書化する。

## 完了条件

- 出荷前に整理すべき表示と残す表示の境界が説明可能になっている。
- packaging / sdist の成立条件が説明可能になっている。
- `1.0.0` judgement に必要な最小証跡が説明可能になっている。
- その証跡が、不要な独立 checklist なしでも追える構成になっている。
- `1.0.0` 判定を 4 つ前後の gate で説明できる。
- Workstream 2-4 に属する論点と混線していない。

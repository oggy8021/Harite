# Harite Project Initial Build Reformation WS1 Code Residue Inventory

最終更新: 2026-05-18

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md](docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md) の [code residue の現状観測](docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md#L156) にあった解消済み一覧を、別紙として切り出したものである。
- 対象は、同文書の旧一覧範囲だった 53 件の cleanup 記録である。
- 目的は、WS1 の residue cleanup を「総合見解」と「ファイル別内訳」で読み直せるようにすることにある。

## 総合見解

- 堅牢性は増した。特に [tests/gui/test_gtk_runtime_backend.py](tests/gui/test_gtk_runtime_backend.py) と [tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py) に追加した focused regression test により、「legacy signature mismatch は feedback に乗る」「expected partial-environment failure だけを非致命 fallback に残す」「unexpected runtime failure は伝播する」という境界が固定され、本来は表面化すべき異常が再び黙って握り潰される戻りを起こしにくくなった。
- ただし増した堅牢性の中心は GUI runtime callback bridge まわりであり、効いた範囲は主に runtime adapter/backend の回帰耐性である。WS1 全体の packaging や release 実務は、現在は [docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) へ移している。
- やったことは大きく 3 類型に分かれる。第 1 に residue wording / legacy marker / dead compatibility の除去、第 2 に current callback contract への揃え直し、第 3 に broad catch / broad fallback の expected-failure 限定化である。
- この意義は、`1.0.0` 前に「古い設計の名残が見える」「unexpected failure を黙って飲む」「今は使っていない legacy contract に再度依存する」という 3 種の不安定さを減らした点にある。
- 後続で防いだものは、主に 4 つである。unexpected runtime failure の見逃し、legacy callback signature への逆戻り、owner 解決や dispatch contract の局所分岐の再発、product surface に残る stale wording の再流入である。

## 数的評価

- 解消済み項目数: 53 件
- 参照ファイル数: 19 件
- 内訳: production file 18 件、test file 1 件
- 集中領域: [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) 14 件、[src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) 9 件、[src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py) 8 件、[src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) 6 件で、上位 4 ファイルに 37 / 53 件、約 70% が集中している。
- 便宜分類: residue / legacy marker cleanup 7 件、contract alignment 4 件、exception or fallback hardening 42 件
- test 増分: [tests/gui/test_gtk_runtime_backend.py](tests/gui/test_gtk_runtime_backend.py) に focused regression test を 31 件追加し、[tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py) には entrypoint fallback / dispatch binding の回帰を 5 件追加した。[tests/core/test_core.py](tests/core/test_core.py) は 2 件を rename / wording cleanup したが純増ではない。
- 残留 broad catch 候補: 2026-05-18 時点では GUI 配下に 7 か所あり、これは「解消済み 53 件」と同じ cleanup 項目単位ではなく、個別の catch 節監査候補数である。
- 残留 broad catch の監査結果: 7 か所すべて `intentional wrapper` と判定した。`要修正` は現時点で 0 か所である。
- 判定根拠: [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の 2 か所は plugin apply / watch apply の外部失敗を `status_message` / `last_error` に畳む contract で、[src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) の 5 か所は toggle/save 操作失敗を `Position: error` / `SavePath: error` feedback に載せる contract である。いずれも [tests/gui/test_main_window_signals.py](tests/gui/test_main_window_signals.py) と [tests/gui/test_gtk_runtime_backend.py](tests/gui/test_gtk_runtime_backend.py) の既存回帰が前提を固定している。

## WS1 の中での位置づけ

- この cleanup は WS1 の中でも、[docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md](docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md) にある Gate 1 の「product surface に見える code residue を整理する」と、Gate 4 の「owner 判定前に不足確認を列挙できる状態へ寄せる」に最も強く関わる。
- 逆に、Gate 2 の packaging / resource 成立と Gate 3 の release 面整合は [docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) へ分離した。ここでやったのは、出荷前の挙動を current contract に固定し、予期しない異常を握り潰さないようにしたことだ。
- したがって WS1 テーマの中での位置づけは、「release 前の見た目の掃除」だけではなく、「release 前に runtime adapter/backend の曖昧さを減らす hardening」である。
- `1.0.0` に向けた意味は、利用者に見える residue を落としつつ、owner が pass/fail を判断するときに本来表面化すべき失敗が feedback または例外として見える状態を作った点にある。

## ファイル別変更一覧

### [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py)

- `WallPosit_MainWindow` の残骸を削除した。
- `HARITE_DEBUG_LAYOUT` / debug layout overlay を削除した。
- 未使用の `Gtk.Builder` / `ui_file` / runtime Glade fallback 分岐を削除し、GTK signal backend を current runtime backend 直結へ整理した。
- dialog destroy notify の broad catch を [src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py) 側と合わせて除去し、close handler failure を伝播する contract に揃えた。
- direction position bridge で unexpected callback failure を silent swallow せず、`Position: error` feedback として表面化するようにした。
- save path bridge で unexpected `on_save_as` failure を silent swallow せず、`SavePath: error` feedback として表面化するようにした。
- apply-mode / apply / optimize bridge を、expected signature mismatch だけを error feedback に載せる形へ narrowed した。
- margin change / margin text mode / margin text / margin text position / margin text max-lines bridge を、expected signature mismatch だけを feedback に載せる形へ narrowed した。
- GTK runtime/bootstrap probe を import/version failure 限定の wrapper に寄せ、unexpected runtime failure を握り潰さないようにした。

### [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py)

- `skeleton` / `placeholder` wording を current wording へ更新した。
- unused broad handler fallback を削除した。
- input pick / watch srcdir 選択 / input clear を current side-required contract に揃えた。
- margin change を current widget-value contract に揃えた。
- save path / settings load を explicit-path contract に揃えた。
- startup default-settings load を expected file/config failure だけ skip する形へ narrowed した。
- Windows Pictures known-folder probe を expected platform/OS failure だけ fallback 扱いにした。
- explicit settings-file load を expected file/config failure だけ status error 化する形へ narrowed した。
- settings-file save は payload build と file write を分離し、expected save/write failure だけ status error 化するようにした。
- watch auto-split prepare / Save As export / optimize 実行を、expected validation failure だけ UI error 化する形へ narrowed した。

### [src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py)

- dialog destroy notify の broad catch を [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) 側と合わせて除去した。
- legacy callback signature fallback を削除し、current handler contract から外れた呼び出しを error として表面化する形へ揃えた。
- save path confirm / cancel wrapper を、expected signature mismatch だけを `SavePath: error` へ載せる形へ narrowed した。
- open dialog confirm wrapper を、expected signature mismatch だけを `Open-*: error` へ載せる形へ narrowed した。
- input change / input clear wrapper を、expected signature mismatch だけを `Input: failed` / `Clear-*: failed` へ載せる形へ narrowed した。
- watch srcdir confirm では owner 解決を backend の正規 helper に揃え、局所 `__self__` 直読みを除去した。
- watch srcdir confirm wrapper を、expected signature mismatch だけを `Srcdir-*: error` へ載せる形へ narrowed した。

### [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py)

- settings / color / about open helper に残っていた silent swallow を削除した。
- [src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py) 側と合わせて、legacy callback signature fallback を削除した。
- settings open では getter / notice build failure だけを `Settings: error` へ載せ、open callback の unexpected runtime failure は握り潰さないようにした。
- settings save / settings apply wrapper を、expected signature or input failure だけを `SettingsSave: error` / `SettingsApply: error` へ載せる形へ narrowed した。
- color / about open wrapper は getter failure を従来どおり feedback へ載せつつ、callback invocation では expected signature mismatch だけを `Color: error` / `About: error` へ載せる形へ揃えた。
- color apply / confirm wrapper を、expected callback or input failure だけを `Color: error` へ載せる形へ narrowed した。
- settings / color / about open helper では、getter / notice build の expected failure を `RuntimeError` / `TypeError` / `ValueError` に限定し、unexpected getter/build error は伝播するようにした。

### [src/harite/gui/adapters/gtk_runtime_dialogs.py](src/harite/gui/adapters/gtk_runtime_dialogs.py)

- color dialog GDK probe を optional import/version failure だけ fallback 扱いにした。
- color conversion fallback を invalid conversion だけ吸う形へ絞った。
- native notice host probe を signature mismatch だけ fallback 扱いにした。
- parent/native-host probe も signature mismatch だけ fallback 扱いにした。

### [src/harite/gui/adapters/gtk_runtime_watch_ui.py](src/harite/gui/adapters/gtk_runtime_watch_ui.py)

- watch interval dispatch を current `int seconds` contract に揃え、owner 非接続時だけ widget を渡す legacy signature fallback を削除した。
- watch start/stop wrapper を、expected callback or input failure だけを `Watch: error` へ載せる形へ narrowed した。

### [src/harite/gui/adapters/gtk_runtime_watch.py](src/harite/gui/adapters/gtk_runtime_watch.py)

- GLib probe を optional import/version failure だけ fallback 扱いにした。
- watch tick callback wrapper を、expected signature mismatch だけを `Watch: error` へ載せる形へ narrowed した。

### [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py)

- `WallPosit_MainWindow` の残骸を削除した。
- tray icon update / binding discovery / resource fallback を、API 差・import failure・resource missing に限定した fallback へ整理した。
- GTK/AppIndicator probe を import/version failure だけ fallback 扱いにした。

### [src/harite/gui/adapters/gtk_runtime_preview.py](src/harite/gui/adapters/gtk_runtime_preview.py)

- preview helper を conversion / expected image-load failure 限定の fallback へ整理した。
- GdkPixbuf probe を optional import/version failure だけ fallback 扱いにした。

### [src/harite/gui/adapters/gtk_tab_builders.py](src/harite/gui/adapters/gtk_tab_builders.py)

- `Debug: apply is immediate` を中立な product 文言へ置換した。

### [src/harite/gui/app.py](src/harite/gui/app.py)

- `WallPosit_MainWindow` の残骸を削除した。
- `skeleton` / `placeholder` wording を current wording へ更新した。
- entrypoint fallback では `_load_ui_signal_backend` / `_initialize_tasktray` / `_present_ui_window` が正規化した `RuntimeError` だけを非致命扱いに残し、unexpected runtime failure は黙って握り潰さないようにした。
- runtime dispatch 接続 fallback も `ImportError` / `TypeError` だけを非致命扱いに絞り、unexpected dispatch binding error は伝播するようにした。

### [src/harite/gui/adapters/gtk_runtime_object_registry.py](src/harite/gui/adapters/gtk_runtime_object_registry.py)

- `WallPosit_MainWindow` の残骸を削除した。

### [src/harite/cli.py](src/harite/cli.py)

- `skeleton` / `placeholder` wording を current wording へ更新した。

### [src/harite/watch.py](src/harite/watch.py)

- `skeleton` / `placeholder` wording を current wording へ更新した。

### [src/harite/gui/adapters/gtk_runtime_signal_wiring.py](src/harite/gui/adapters/gtk_runtime_signal_wiring.py)

- mandatory widget wiring に残っていた broad `except Exception: pass` を削除した。

### [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py)

- current runtime handler map から legacy save/settings alias を除去し、対応する legacy 前提テストも整理した。

### [src/harite/gui/adapters/gtk_runtime_margin_text_gtk.py](src/harite/gui/adapters/gtk_runtime_margin_text_gtk.py)

- margin-text GTK helper を optional import/version failure だけ fallback 扱いにした。

### [src/harite/gui/views/main_window_preview.py](src/harite/gui/views/main_window_preview.py)

- result preview display-settings fallback を expected `ValueError` だけに絞った。

### [tests/core/test_core.py](tests/core/test_core.py)

- `*_placeholder` test 名を current smoke wording へ更新した。
- 未実装前提 docstring を current wording へ更新した。
- module import skip を broad catch ではなく `ImportError` に絞った。

## 関連 test 追加

### [tests/gui/test_gtk_runtime_backend.py](tests/gui/test_gtk_runtime_backend.py)

- focused regression test を 28 件追加した。
- 主な固定点は 2 つである。legacy signature mismatch は feedback 文言へ載ること、unexpected runtime failure は `RuntimeError` として伝播すること。
- 対象面は、input change、watch srcdir confirm、open dialog confirm、save path confirm/cancel、settings open、apply-mode、apply、optimize、margin change、margin text mode、margin text、margin text position、margin text max-lines、clear button である。

### [tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py)

- entrypoint fallback の focused regression test を 3 件追加した。
- 主な固定点は 2 つである。GTK 不可や headless のような expected partial-environment failure は `RuntimeError` として non-fatal fallback に残ること、unexpected `ValueError` は伝播すること。
- 対象面は、signal backend load、tasktray 初期化、window presentation である。

## 読み方メモ

- 本書は「どの file で何を片付けたか」を早く再確認するための inventory である。
- release 判定そのものは [docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md](docs/reformation/harite-project-initial-build-reformation-ws1-release-prep.md) を正本として読む。

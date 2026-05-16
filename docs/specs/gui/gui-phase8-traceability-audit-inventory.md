# GUI Phase 8 Traceability Audit Inventory

最終更新: 2026-05-10

## 位置づけ

- 本書は [docs/specs/gui/gui-phase8-traceability-followup-memo.md](docs/specs/gui/gui-phase8-traceability-followup-memo.md) の 8 / 9 / 10 を具体化するための監査用 inventory である。
- 目的は、canonical 名と legacy alias の残存、代表経路の 1 hop trace、alias / typo / 歴史的 ID の撤去条件を 1 枚で確認できるようにすることにある。
- current runtime の新しい正本仕様を定義する文書ではなく、traceability 改善ブランチの進捗と残課題を記録する監査補助として扱う。

## 使い方

- 実装中: canonical 名を追加したとき、legacy alias を残したままになっていないかを本書で棚卸しする。
- 実装後: representative path を検索で 1 hop ずつ辿り、traceability が改善したかを本書で確認する。
- merge 前: alias / typo / 歴史的 ID に必要理由と撤去条件が書かれているかを本書で確認する。

## 1. 検索ベース静的監査

| 項目 | canonical 側 | 残存 alias / typo | 主な観測箇所 | 現時点評価 | 次に詰めること |
| --- | --- | --- | --- | --- | --- |
| Settings dialog handlers | `on_get_settings_config`、`on_apply_settings`、`on_load_settings_file`、`on_save_settings_file` | 履歴上の `Preferences` 呼称のみ | [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py)、[src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) | code 上の handler 名は canonical 化済み | 履歴文書で旧呼称の注記粒度を維持する |
| Settings dialog object names | `btnSettings*`、`lblSettingsState`、`entSettings*` | 履歴上の `Prefs` 呼称のみ | [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) | settings dialog の object map は canonical 化済み。watch 系 negative check 以外の `Prefs` object ID は撤去済み | canonical object 名だけを使う前提を維持する |
| Save As handler path | `on_save_as` | なし | [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py)、[src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) | code 上の save handler 名は canonical 化済み | 履歴文書で旧 `on_save` 呼称を再導入しない |
| save path close callback | `on_close_save_path_dialog` | `on_SavePathDialog_destroy` の履歴表現 | [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py)、[src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) | code 上は canonical 化済み | 履歴文書とのズレは別途整理対象 |
| margin object names | `spnLeftMargin`、`spnRightMargin`、`spnTopMargin`、`spnBottomMargin` | なし | [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py)、[src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) | code 上の margin object 名は canonical 化済み | typo 名を test / docs へ再導入しない |
| Glade 由来 object IDs | `main_window` を正本利用 | なし | [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) | `hbox11` / `hbox2` / `vbox4` / `window1` は削除済み | 新規変更で歴史的 ID を増やさない |

## 2. 代表 1 hop trace

| 機能 | runtime object / 入口 | backend 内の受け | dispatch key | MainWindow handler | 現時点評価 |
| --- | --- | --- | --- | --- | --- |
| Save As open | `btnSave` | `_on_save_clicked` | `on_save_as` | `on_save_as` | 1 hop 化済み |
| Settings open | `btnSettings` | `_on_settings_clicked` | `on_open_settings_dialog` | `on_open_settings_dialog` | open 導線は単純 |
| Settings apply | `btnSettingsApply` | `_on_preferences_apply_clicked` | `on_apply_settings` | `on_apply_settings` | backend fallback を除去済み |
| Settings load | `btnSettingsLoad` | `_on_preferences_load_clicked` | `on_load_settings_file` | `on_load_settings_file` | backend fallback を除去済み |
| Settings save | `btnSettingsSave` | `_on_preferences_save_clicked` | `on_save_settings_file` | `on_save_settings_file` | backend fallback を除去済み |
| Clear input | `btnClrPathL` / `btnClrPathR` | `_on_clear_input_clicked` | `on_clear_input` | `on_clear_input` | 1 本化済み |

判定メモ:

- Save As と clear input は、代表経路としてかなり 1 hop に近い。
- Settings 系は backend 側の legacy fallback を除去済みで、今回対象の canonical 経路は 1 hop で確認できる。

## 3. alias / typo / 歴史的 ID inventory

| 区分 | 項目 | 現在の必要理由 | 撤去条件 |
| --- | --- | --- | --- |
| legacy handler alias | `on_get_preferences_config` など `Preferences` 系 wrapper | 削除済み | 履歴文書でのみ旧呼称を扱い、code に再導入しないこと |
| legacy save alias | `on_save` | 削除済み | 履歴文書でのみ旧呼称を扱い、code に再導入しないこと |
| typo alias | `LMergin` / `RMergin` / `TopMergin` / `BtmMergin` | 削除済み | typo 名を code / test に再導入しないこと |
| historical object IDs | なし | 削除済み | 追加の Glade 由来 ID を持ち込まないこと |

## 4. merge 前の確認観点

- [x] canonical 名と alias 名の棚卸し結果を更新した
- [x] representative path を 1 hop ずつ辿れることを確認した
- [x] alias / typo / 歴史的 ID に必要理由と撤去条件を書いた
- [x] 今回対象外の `about` / `help` を誤って巻き込んでいない

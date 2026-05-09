# GUI Phase 8 Traceability Follow-up Memo

最終更新: 2026-05-09

## 位置づけ

- 本メモは、`src/harite/gui/views` と `src/harite/gui/adapters` の間で今回顕在化した traceability 低下要因を、Phase8 内の後続ブランチで解く課題として固定するための短い設計メモである。
- layout 正本は [docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md)、Phase8 backlog は [docs/specs/gui/gui-phase8-backlog.md](docs/specs/gui/gui-phase8-backlog.md) を参照する。

## 今回の扱い

- 今回のブランチでは、Margins / Margin text 系の公開 symbol rename と signal rename までを対象にした。
- `about` / `help` は先送り合意済みのため、本メモでは検出記録のみとし、是正対象には含めない。
- 下記の課題は、Phase8 内の新ブランチでまとめて解消する。

## 着手タイミング

- 本メモは「次に必ず着手する」ことを固定する文書ではなく、Margins branch 完了後に見えた GUI traceability debt の受け皿である。
- Phase8 全体の branch order は [docs/specs/gui/gui-phase8-repair-plan.md](docs/specs/gui/gui-phase8-repair-plan.md) を正本とし、2026-05-09 時点の再開判断は [docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md](docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md) を参照する。
- 原則としては、未了の semantics 修復を優先し、その直後の GUI 専用ブランチで本メモを扱う。
- ただし break 明けの再始動コスト低減を優先して traceability 改善を前倒しする場合は、その判断理由を PR 本文と resume 文書へ明記する。

## 後続ブランチで解く課題

### 1. save path close callback の命名不一致

- adapter 側の destroy callback 名と runtime dispatch / MainWindow handler 名が一致していない。
- `on_SavePathDialog_destroy` と `on_close_save_path_dialog` を二重に持たず、close 系の一貫した命名へ寄せる。

### 2. clear input 経路の二重化

- runtime adapter が `on_clear_input` を使わず、独自の `_on_clear_input_clicked` から `on_change_input_text` へ流している。
- clear 操作の正規入口を 1 本に寄せ、button click と MainWindow handler の関係を単純化する。

### 4. Settings / Prefs 語彙の混在

- signal / state / object 名 / status 文言で `Settings` と `Prefs` が混在している。
- dialog 機能の user-facing 語彙と internal 語彙を一本化し、検索単位を揃える。

### 5. Save As / Save / Optimize の境界が読みにくい命名

- `Save As` button が `btnSave` / `on_save` として表現される一方、`Optimize` も近接して存在し、責務境界が追いにくい。
- save-path chooser 起点の操作と optimize 実行を、object 名・handler 名・status 文言の 3 面で区別しやすくする。

### 6. margin 系 object 名の typo 契約

- `LMergin` / `RMergin` / `TopMergin` / `BtmMergin` の typo が object 名と widget-name 判定に残っている。
- margin 系 object 名は typo を解消し、MainWindow 側の widget 判定も typo 前提を脱却する。

### 7. Glade 由来 ID 群の残存

- `window1` / `hbox11` / `hbox2` / `vbox4` など、意味で追えない歴史的 ID が runtime object map に残っている。
- 後続ブランチでは、以下のいずれかに整理する。
  - 現在も参照されるものだけを意味語彙へ rename する
  - 参照されていないものは object map から削除する
- 少なくとも、新規変更でこれらの ID を増やさない。

## 受け入れ条件

- `views` と `adapters` をまたぐ公開 symbol について、同一機能を指す名称が 1 系統に揃っている。
- runtime object 名から MainWindow handler まで、検索で 1 hop ずつ辿れる。
- 歴史的 alias や typo 名を残す場合は、必要理由と撤去条件が明記されている。
- `about` / `help` は本メモの対象外として維持する。

## 補足

- 今回見えたものは、どれも今すぐの機能破綻より「後続変更で追跡コストを増やす技術的負債」に属する。
- そのため、Phase8 の後続ブランチでは feature 追加と混ぜず、traceability 改善としてまとめて扱う。

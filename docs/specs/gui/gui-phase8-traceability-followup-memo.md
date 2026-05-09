# GUI Phase 8 Traceability Follow-up Memo

最終更新: 2026-05-10

## 位置づけ

- 本メモは、`src/harite/gui/views` と `src/harite/gui/adapters` の間で今回顕在化した traceability 低下要因を、Phase8 内の後続ブランチで解く課題として固定するための短い設計メモである。
- layout 正本は [docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md](docs/specs/gui/gui-margin-tab-grid-re-layout-contract.md)、Phase8 backlog は [docs/specs/gui/gui-phase8-backlog.md](docs/specs/gui/gui-phase8-backlog.md) を参照する。

## 今回の扱い

- 今回のブランチでは、traceability 低下要因の棚卸しに加えて、Settings / Save As / margin 名を中心とした canonical 化まで実施した。
- `about` / `help` は先送り合意済みのため、本メモでは検出記録のみとし、是正対象には含めない。
- 下記の課題は、本ブランチで整理・是正し、残る論点は履歴文書上の注記に縮小した。

## 着手タイミング

- 本メモは「次に必ず着手する」ことを固定する文書ではなく、Margins branch 完了後に見えた GUI traceability debt の受け皿である。
- Phase8 全体の branch order は [docs/specs/gui/gui-phase8-repair-plan.md](docs/specs/gui/gui-phase8-repair-plan.md) を正本とし、2026-05-09 時点の再開判断は [docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md](docs/specs/gui/gui-phase8-resume-planning-after-2weeks-break.md) を参照する。
- 2026-05-10 時点では、`padding` / `mosaic` 整理と `Margins` 4 値の semantics 修復が main に取り込まれている。
- したがって次の専用ブランチ候補として、本メモをそのまま正本に使ってよい。

## 今回のブランチで整理した課題

### 1. save path close callback の命名不一致

- adapter 側の destroy callback 名と runtime dispatch / MainWindow handler 名が一致していない。
- `on_SavePathDialog_destroy` と `on_close_save_path_dialog` を二重に持たず、close 系の一貫した命名へ寄せる。
- 対応結果: code 上の close callback 名は `on_close_save_path_dialog` に統一し、旧 destroy 呼称は履歴表現だけに残した。

### 2. clear input 経路の二重化

- runtime adapter が `on_clear_input` を使わず、独自の `_on_clear_input_clicked` から `on_change_input_text` へ流している。
- clear 操作の正規入口を 1 本に寄せ、button click と MainWindow handler の関係を単純化する。
- 対応結果: clear 操作は `on_clear_input` を正規入口とする構成へ寄せ、side-aware な状態更新も MainWindow 起点に統一した。

### 3. 受け入れ条件の確認方法が曖昧

- 本メモの受け入れ条件は、pytest 通過だけでは満たしたと判定できず、確認方法が暗黙のまま残っている。
- 後続ブランチでは、少なくとも次の観点で確認可能な形にする。
- 今回のブランチでは、少なくとも次の観点で確認可能な形にした。
  - symbol / object / handler の canonical 名と alias 名を grep で棚卸しできること
  - runtime object 名から MainWindow handler まで、代表経路を検索で 1 hop ずつ辿れること
  - alias / typo / 歴史的 ID を残す場合は、必要理由と撤去条件を文書またはコード近傍で確認できること

### 4. Settings / Prefs 語彙の混在

- signal / state / object 名 / status 文言で `Settings` と `Prefs` が混在している。
- dialog 機能の user-facing 語彙と internal 語彙を一本化し、検索単位を揃える。
- 対応結果: code 上の handler / object / status は `Settings` 系に統一し、`Preferences` / `Prefs` は履歴文書上の旧呼称としてのみ扱う状態まで縮小した。

### 5. Save As / Save / Optimize の境界が読みにくい命名

- `Save As` button が `btnSave` / `on_save` として表現される一方、`Optimize` も近接して存在し、責務境界が追いにくい。
- save-path chooser 起点の操作と optimize 実行を、object 名・handler 名・status 文言の 3 面で区別しやすくする。
- 対応結果: save handler 名は `on_save_as` に統一し、legacy `on_save` は code 上から撤去した。button 表示と save-path status も Save As 系として追える状態に寄せた。

### 6. margin 系 object 名の typo 契約

- `LMergin` / `RMergin` / `TopMergin` / `BtmMergin` の typo が object 名と widget-name 判定に残っている。
- margin 系 object 名は typo を解消し、MainWindow 側の widget 判定も typo 前提を脱却する。
- 対応結果: margin 系 object 名と widget 判定は canonical の `*Margin` に統一し、typo 名は code / test から撤去した。

### 7. Glade 由来 ID 群の残存

- `window1` / `hbox11` / `hbox2` / `vbox4` など、意味で追えない歴史的 ID が runtime object map に残っている。
- 後続ブランチでは、以下のいずれかに整理する。
  - 現在も参照されるものだけを意味語彙へ rename する
  - 参照されていないものは object map から削除する
- 少なくとも、新規変更でこれらの ID を増やさない。
- 対応結果: `window1` / `hbox11` / `hbox2` / `vbox4` は code 上から撤去済みであり、今後も新規導入しない方針を確認した。

### 8. 検索ベースの静的監査で canonical / alias 併存を棚卸しする

- 受け入れ条件の確認では、検索ベースの静的監査を有効な確認手段として扱う。
- たとえば Settings 系は `ui_adapter.py` 上で canonical 名と legacy 名が並存し、`main_window.py` では canonical 実装と wrapper が同時に残っている。
- 同様に object 名でも `gtk_backend.py` 上で `Settings` と `Prefs` の alias 併存が見え、margin typo も `gtk_backend.py` 内に残っている。
- したがって「同一機能を指す名称が 1 系統に揃っているか」は、grep 棚卸しで現状を機械的に点検できる。
- 対応結果: inventory を [docs/specs/gui/gui-phase8-traceability-audit-inventory.md](docs/specs/gui/gui-phase8-traceability-audit-inventory.md) に作成し、canonical / alias の残存有無を PR 前に確認できる形へ整理した。

### 9. 1 hop trace の実地確認で経路の単純さを判定する

- 「runtime object 名から MainWindow handler まで、検索で 1 hop ずつ辿れるか」は、代表経路を実地に追って確認可能である。
- たとえば Save As 系では、object 側 click 入口、backend 内の受け、dispatch map、最終 handler を順に辿ることで、かなり 1 hop ずつの経路に近づいていることを確認できる。
- 一方で Settings 周辺は canonical 優先 fallback が複数箇所に残っており、検索経路がまだ二股になっている。
- したがって本条件は、代表経路ごとに「1 hop で辿れるか」「途中で fallback に分岐しないか」を見て判定する。
- 対応結果: Save As / Settings / Clear input の代表経路は inventory 上で 1 hop trace を確認できる状態にした。

### 10. alias / typo の残存理由と撤去条件を inventory 化する

- alias と typo の管理条件は、現時点ではテストよりも棚卸しで確認するのが現実的である。
- たとえば MainWindow 側の typo 互換や、GTK backend 側の Glade 由来 ID 群は、コード検索で残存箇所を列挙できる。
- ここで重要なのは、受け入れ条件が「alias を残さないこと」ではなく、「残すなら必要理由と撤去条件が明記されていること」にある。
- そのため、後続ブランチでは alias / typo / 歴史的 ID の inventory を作り、各項目について必要理由と撤去条件を確認できる状態にする。
- 初版 inventory は [docs/specs/gui/gui-phase8-traceability-audit-inventory.md](docs/specs/gui/gui-phase8-traceability-audit-inventory.md) に置く。
- 対応結果: alias / typo / 歴史的 ID の inventory を同文書に記録し、削除済み項目と再導入防止条件を確認できるようにした。

## 受け入れ条件

- `views` と `adapters` をまたぐ公開 symbol について、同一機能を指す名称が 1 系統に揃っている。
- runtime object 名から MainWindow handler まで、検索で 1 hop ずつ辿れる。
- 歴史的 alias や typo 名を残す場合は、必要理由と撤去条件が明記されている。
- `about` / `help` は本メモの対象外として維持する。

## 現在地

- code 上の `Settings` / `Save As` / `*Margin` について、今回対象にした canonical 化は完了した。
- 代表 GUI tests は owner 実行の `tests/gui` で pass 済みである。
- PR 前の監査基準は [docs/specs/gui/gui-phase8-traceability-audit-inventory.md](docs/specs/gui/gui-phase8-traceability-audit-inventory.md) を参照する。

## 補足

- 今回見えたものは、どれも今すぐの機能破綻より「後続変更で追跡コストを増やす技術的負債」に属する。
- そのため、Phase8 の後続ブランチでは feature 追加と混ぜず、traceability 改善としてまとめて扱う。

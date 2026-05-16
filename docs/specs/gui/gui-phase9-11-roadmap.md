# GUI Phase 9-11 Roadmap

最終更新: 2026-05-16

## 現在地

- Phase8 は [docs/specs/gui/gui-phase8-closing.md](docs/specs/gui/gui-phase8-closing.md) の判断により close 済みとして扱う。
- Phase10 は [docs/specs/gui/gui-phase10-closing-check.md](docs/specs/gui/gui-phase10-closing-check.md) の判断により close 済みとして扱う。
- Phase11 は [docs/specs/gui/gui-phase11-closing.md](docs/specs/gui/gui-phase11-closing.md) の判断により close 済みとして扱う。
- Phase9-11 を閉じた後の親文書は [docs/reformation/harite-1.0-reformation-plan.md](docs/reformation/harite-1.0-reformation-plan.md) とする。
- 次段では新機能を先に足すのではなく、GUI 中核の構造負債と起動導線の粗さを整理してから、見た目 polish と OS integration へ進む。
- 2026-05-10 時点の主な構造負債は、`MainWindow` と GTK runtime backend への責務集中である。

## 結論

- Phase9 は GUI 中核のリファクタリングと責務分離のフェーズとする。
- Phase10 はユーザー向け GUI 起動導線の整備と、視覚的な補助要素の導入フェーズとする。
- Phase11 は taskbar / tray / indicator / notification など OS 側インタフェースの整備フェーズとする。
- 実装修正の優先対象は `ui_adapter` 単体ではなく、`main_window.py` と `gtk_backend.py` を中心に据える。

## 現状認識

### 1. Phase9 の主対象

- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) は、入力管理、margin text、preview、settings、about、color、watch、apply までを単一クラスに抱えている。
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) は、runtime widget 構築、dialog、preview 反映、watch timer、各 signal handler を 1 ファイルへ集約している。
- [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py) は薄い dispatch 層であり、Phase9 の主問題というより、分割後の契約面整理に伴って見直す対象である。

### 2. Phase10 の前提

- [src/harite/gui/app.py](src/harite/gui/app.py) は現時点でも skeleton 的な entrypoint であり、`--bind-ui-backend` / `--present-ui-window` と環境変数前提の技術寄り導線が残っている。
- XFCE は current GUI の正本運用環境であり、ここでいう暫定は XFCE 対応そのものではない。
- この option 群は GTK 採用一般で通常要求される常設導線というより、framework-neutral な `MainWindow` と optional GTK backend を橋渡しする bootstrap 導線である。
- GUI 起動手順は README の常設ユーザー導線というより、manual validation や phase validation 文書に分散している。
- したがって Phase10 では、単なる見た目 polish ではなく、owner の通常利用環境である XFCE を含む current GUI を追加 option なしで起動できる導線へ再整理する必要がある。

### 3. Phase11 の前提

- tray / indicator / notification に関して、現時点で明示的な実装基盤はない。
- OS integration は小改修ではなく、新しい abstraction と platform 差分方針を要する。
- このため、Phase11 は Phase9 の責務整理を前提に進める。

## Phase9

### Phase9 の目的

- GUI 中核の責務集中を緩和し、可読性・保守性・検証容易性を上げる。
- legacy、残債、互換の名目で残っているコードを棚卸しし、維持するものと削除するものを分ける。
- Phase10 / Phase11 で UI polish や OS integration を載せても破綻しない境界へ整える。

### Phase9 の主対象

- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py)
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py)
- [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py)
- `controller` / `view` / `backend` / `service` の責務境界

### Phase9 の論点

- `MainWindow` から何を分離するか。
- GTK runtime backend を dialog / preview / watch / settings 同期などの単位で分割するか。
- `ui_adapter` を単なる handler map のまま保つか、より明示的な契約面へ整理するか。
- legacy / fallback / compatibility と呼んでいるもののうち、本当に必要なものは何か。
- テストを壊さずに分割するための最小単位はどこか。

### Phase9 の非目的

- 新しい GUI 機能を大量追加すること。
- 見た目の final polish をこのフェーズの主目的にすること。
- tray / indicator 実装までを同時に抱えること。

### Phase9 の完了条件

- `MainWindow` の責務分離方針が確定している。
- GTK runtime backend の大ブロックが分割可能な単位で整理されている。
- legacy / compatibility 項目の維持・縮退・削除候補が文書化されている。
- Phase10 / Phase11 に送るための境界が説明可能になっている。

## Phase10

### Phase10 の目的

- GUI の起動方法を利用者向けに整える。
- 補助線や装飾、カラー補助、settings dialog semantics、アイコン導入など、視覚面と操作面の改善を「機能を支える補助」として入れる。

### Phase10 の主対象

- GUI entrypoint と起動オプション
- README / docs 上の GUI 起動導線
- 補助線、強調表示、エラーメッセージの見せ方
- Settings dialog の action semantics
- icon library の選定と導入判断

### Phase10 の論点

- `python -m harite.gui.app` と各種 option を、利用者向けにどう見せるか。
- 開発用 option と通常起動導線をどう分けるか。
- 色による補助をどこまで導入し、文字情報との冗長化をどう保つか。
- Settings dialog の `Load / Save / Apply / Close` を、利用者へどう見せるか。
- icon library を導入するなら、依存・配布・ライセンスをどう扱うか。

### Phase10 の非目的

- Phase9 の構造負債を未整理のまま、見た目だけ上塗りすること。
- OS taskbar / tray integration までをこのフェーズで抱えること。

### Phase10 の完了条件

- GUI の通常起動導線が docs / 実装の両方で説明可能になっている。
- owner の通常利用環境である XFCE で、README 上の正本 GUI 導線から current GUI を追加 option なしに起動できる。
- 補助線、色、settings semantics、アイコンの導入方針が定まり、最低限の一貫した visual rule / operation rule ができている。
- Phase11 に送る OS integration 論点が切り分けられている。

## Phase11

### Phase11 の目的

- 各 OS の taskbar / tray / indicator / notification 領域とのインタフェースを用意する。

### Phase11 の主対象

- platform abstraction
- tray / indicator 常駐導線
- notification 表示方針
- watch / apply / error state と OS 側通知の接続

### Phase11 の論点

- OS ごとの差分をどこで吸収するか。
- 常駐させるのか、通知だけ行うのか。
- watch や apply の状態通知を GUI 内表示とどう分担するか。
- optional dependency として扱うか、標準機能として扱うか。

### Phase11 の非目的

- Phase9 の構造整理なしに OS integration を積み増すこと。
- 単一 OS だけを前提に設計を固定すること。

### Phase11 の完了条件

- OS integration の責務境界が定義されている。
- 主要 OS ごとの差分吸収方針が説明可能である。
- 通知 / 常駐の最小機能が GUI 本体と衝突せずに動く。

## 優先順

1. Phase9: GUI 中核の責務整理
2. Phase10: 起動導線と視覚補助の整備
3. Phase11: OS integration

この順で進める。Phase10 と Phase11 は、Phase9 で境界が整っていることを前提にする。

## 初動で作る planning 成果物

1. Phase9 単独 planning: [docs/specs/gui/gui-phase9-planning.md](docs/specs/gui/gui-phase9-planning.md)
2. Phase9 の legacy / compatibility 監査メモ
3. Phase10 の GUI 起動導線メモ: [docs/specs/gui/gui-phase10-1st-planning.md](docs/specs/gui/gui-phase10-1st-planning.md)
4. Phase10 の visual aid 方針メモ: [docs/specs/gui/gui-phase10-2nd-planning.md](docs/specs/gui/gui-phase10-2nd-planning.md)
5. Phase10 の settings semantics メモ: [docs/specs/gui/gui-phase10-3rd-planning.md](docs/specs/gui/gui-phase10-3rd-planning.md)
6. Phase10 の icon 導入メモ: [docs/specs/gui/gui-phase10-4th-planning.md](docs/specs/gui/gui-phase10-4th-planning.md)
7. Phase11 の初手 planning: [docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md)
8. Phase11 の OS integration 方式比較メモ
9. 現時点では [docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md) に主要判断を統合済みであり、追加メモは feature 実装で blocker が出た場合のみ作る。
10. tray icon の視認性 blocker に対する補助メモ: [docs/specs/gui/gui-phase11-2nd-planning.md](docs/specs/gui/gui-phase11-2nd-planning.md)
11. application / taskbar / about / main window の icon surface 分離メモ: [docs/specs/gui/gui-phase11-3rd-planning.md](docs/specs/gui/gui-phase11-3rd-planning.md)

## 判断メモ

- `ui_adapter` を過大評価しない。実際の重心は `MainWindow` と GTK runtime backend にある。
- Phase10 の「起動方法を整える」は docs 更新だけでは足りず、entrypoint と option 設計の再整理を含む。
- 2026-05-11 時点の Phase10 初手判断では、README 上の正本 GUI 導線は `harite-gui` を第一候補とし、`harite gui` は将来整理候補として残す。
- Phase10 close 判断の補助文書は [docs/specs/gui/gui-phase10-closing-check.md](docs/specs/gui/gui-phase10-closing-check.md) とする。
- Phase11 は新規抽象化を要するため、post-Phase10 の小粒追加ではなく、独立フェーズとして扱う。
- Phase11 実装は feature で進め、planning の追加分割は既定路線にしない。
- Phase11 close 判断の補助文書は [docs/specs/gui/gui-phase11-closing.md](docs/specs/gui/gui-phase11-closing.md) とする。
- ただし feature 実装中に icon visibility のような局所 blocker が出た場合は、補助 planning を追加してよい。
- tray icon と application icon family の surface 分離が必要になった場合も、補助 planning を追加してよい。

# GUI Phase10 Closing Check

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md) の Phase10 を close 判断するための補助文書である。
- 親文書は roadmap とし、本書は roadmap を上書きせず、Phase10 の完了条件に対する到達状況を対応づける。
- この closing check は、このターンで再確認した docs / 実装 / test を根拠に書く。XFCE 実機の再検証そのものは本書では代替しない。

## 暫定結論

- 現時点では、Phase10 は close 候補として扱ってよい。
- roadmap の Phase10 完了条件 4 点に対して、3 点は達成、1 点は「owner の通常利用前提に依存するが close 判断を妨げない条件付き達成」と整理できる。
- 未了として残すべき主論点は、Phase10 内の polish ではなく、Phase11 の OS integration 側で扱うべきものに収束している。

## 完了条件との対応

### 1. GUI の通常起動導線が docs / 実装の両方で説明可能になっている

判定: 達成

根拠:

- roadmap の Phase10 は、通常起動導線の整備を主対象に置いている。[docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md)
- README は current GUI の通常起動導線を `harite-gui` と明示し、`python -m harite.gui.app` を補助導線として整理している。[README.md](README.md)
- entrypoint 実装は no-option 既定で bind / present を有効化する制御を持つ。[src/harite/gui/app.py](src/harite/gui/app.py)
- no-option 既定の回帰は test で固定されている。[tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py)

判断メモ:

- Phase10 初手で論点だった `harite-gui` と `harite gui` の比較は、README 正本導線を `harite-gui` に寄せる形で実用上収束している。
- `--bind-ui-backend` / `--present-ui-window` は end user 向け常設導線ではなく、override として整理されている。

### 2. owner の通常利用環境である XFCE で、README 上の正本 GUI 導線から current GUI を追加 option なしに起動できる

判定: 条件付き達成

根拠:

- README は `harite-gui` を正本導線とし、通常利用で追加 option は不要と明記している。[README.md](README.md)
- entrypoint 実装は no-option 既定で bind / present を有効化している。[src/harite/gui/app.py](src/harite/gui/app.py)
- no-option 既定の挙動は test で固定されている。[tests/gui/test_app_entrypoint.py](tests/gui/test_app_entrypoint.py)
- README には XFCE 向け smoke 検証の節もある。[README.md](README.md)

判断メモ:

- 本書は XFCE 実機再検証の代替ではないため、ここだけは owner の通常利用実績を含む project judgement へ依存する。
- ただし docs / 実装 / test の 3 面は揃っており、Phase10 close の阻害要因として残すほどの未整理は見えない。

### 3. 補助線、色、settings semantics、アイコンの導入方針が定まり、最低限の一貫した visual rule / operation rule ができている

判定: 達成

根拠:

- visual aid / message surface の原則は 2nd planning で整理され、global summary と dedicated messaging region の役割分担が定義されている。[docs/specs/gui/gui-phase10-2nd-planning.md](docs/specs/gui/gui-phase10-2nd-planning.md)
- Settings dialog semantics は 3rd planning で `OK=Apply`、`Save=永続化`、`Cancel=無変更終了` として整理されている。[docs/specs/gui/gui-phase10-3rd-planning.md](docs/specs/gui/gui-phase10-3rd-planning.md)
- tab layout の実装契約は [docs/specs/gui/gui-phase10-layout-restructure-contract.md](docs/specs/gui/gui-phase10-layout-restructure-contract.md) に集約され、footer global summary と tab-local surface の境界も明記されている。
- icon 方針は 4th planning と mock 群で整理され、実装側では header の Color / Settings / About に Lucide icon を適用している。[docs/specs/gui/gui-phase10-4th-planning.md](docs/specs/gui/gui-phase10-4th-planning.md) [docs/specs/gui/gui-phase10-icon-html-mock-memo.md](docs/specs/gui/gui-phase10-icon-html-mock-memo.md) [docs/specs/gui/gui-phase10-icon-mock.html](docs/specs/gui/gui-phase10-icon-mock.html) [src/harite/gui/adapters/gtk_layout_builders.py](src/harite/gui/adapters/gtk_layout_builders.py)

判断メモ:

- icon は全面導入ではなく、意味差が強い面へ限定導入する方針で扱えば足りる。
- Help は未実装のまま保持するより不要判断で撤去した方が rule を乱さないため、現行判断としては narrowing であって欠落ではない。
- Color 類のさらなる polish は残り得るが、roadmap の要求は「最低限の一貫した rule」であり、全面 polish 完了ではない。

### 4. Phase11 に送る OS integration 論点が切り分けられている

判定: 達成

根拠:

- roadmap 自身が Phase11 を独立フェーズとして定義し、tray / indicator / notification / OS 状態通知分担を主対象としている。[docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md)
- Phase10 各 planning でも、tray / indicator / OS integration は対象外と明示されている。[docs/specs/gui/gui-phase10-2nd-planning.md](docs/specs/gui/gui-phase10-2nd-planning.md) [docs/specs/gui/gui-phase10-4th-planning.md](docs/specs/gui/gui-phase10-4th-planning.md)

判断メモ:

- Phase11 の比較メモ自体は roadmap の初動成果物一覧に残っているが、Phase10 close 条件は「論点が切り分けられていること」であり、Phase11 planning 完了までは要求していない。
- 本書では Phase11 の具体論点列挙までは扱わず、対象外として Phase11 planning へ送る前提で十分とする。

## close を妨げない残件

- XFCE 実機での最終手触り確認は、owner の closing 判断で補う性質のものであり、本書では再実施していない。
- Color 面や icon 面の追加 polish は残り得るが、Phase10 の完了条件を reopen するほどの未整理ではない。
- Phase11 planning は、Phase10 close 後の次作業として自然に着手できる。

## close 判断メモ

- roadmap を親文書とする限り、Phase10 の close 判断に必要なのは「通常起動導線」「visual / operation rule」「Phase11 切り分け」の 3 本柱が説明可能かである。
- 現時点の docs / 実装 / test の揃い方を見る限り、Phase10 は close 扱いへ進めてよい。
- 以後の小さな UI polish を理由に Phase10 を開け続けるより、Phase11 予備調査へ論点を送る方が roadmap 整合は良い。

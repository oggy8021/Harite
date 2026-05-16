# GUI Phase11 Closing

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md) の Phase11 を close 判断するための補助文書である。
- 親文書は roadmap とし、本書は roadmap を上書きせず、Phase11 の完了条件に対する到達状況を対応づける。
- Phase11 の判断根拠は [docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md)、[docs/specs/gui/gui-phase11-2nd-planning.md](docs/specs/gui/gui-phase11-2nd-planning.md)、[docs/specs/gui/gui-phase11-3rd-planning.md](docs/specs/gui/gui-phase11-3rd-planning.md) と実装到達点にまたがるため、本書はそれらを close judgement として集約する。
- tray / taskbar / about の最終確認は owner の XFCE 実機確認を含む。本書はその事実を整理するが、実機確認そのものを代替しない。

## 暫定結論

- 現時点では、Phase11 は close 扱いへ進めてよい。
- roadmap の Phase11 完了条件 3 点に対して、docs / 実装 / GUI test / owner 実機確認の組み合わせで、いずれも達成と整理できる。
- 残件として残り得るのは多 OS 展開や icon polish の追加であり、Phase11 の完了条件を reopen する未整理ではない。

## 完了条件との対応

### 1. OS integration の責務境界が定義されている

判定: 達成

根拠:

- 1st planning は、tray を watch 中心の常用導線として定義し、`Visible/Invisible`、`Settings`、`BaseColor`、`About`、`Quit` の最小 menu と、watch state 伝播、dialog-open request、settings JSON 永続化への責務境界を整理している。[docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md)
- tray / indicator 実装は [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py) に閉じ込められ、GUI 本体の dialog semantics や watch state 所有とは分離されている。[src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py)
- app icon family は 3rd planning で tray icon と surface 分離され、main window の in-window branding を増やさずに taskbar / about へ寄せる整理になっている。[docs/specs/gui/gui-phase11-3rd-planning.md](docs/specs/gui/gui-phase11-3rd-planning.md)

判断メモ:

- Phase11 で必要だったのは「OS surface を current GUI にどう接続するか」の境界定義であり、dialog や settings の意味面を tray 側へ移すことではない。
- tray 専用 icon と application icon family の分離まで含めて、責務境界は Phase11 内で十分に説明可能になった。

### 2. 主要 OS ごとの差分吸収方針が説明可能である

判定: 達成

根拠:

- 1st planning は、XFCE を first target としつつ、`AyatanaAppIndicator3` を本命、`AppIndicator3` を保険として runtime detection で吸収する方針を固定している。[docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md)
- 実装も `AyatanaAppIndicator3` / `AppIndicator3` の順で binding を探索する adapter 構成になっている。[src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py)
- 他 OS は Phase11 内で同時実装せず、後段で plugin / adapter 境界を保ったまま拡張する読みを維持している。[docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md)

判断メモ:

- roadmap の要求は「主要 OS すべての実装完了」ではなく、「差分吸収方針が説明可能であること」である。
- 現時点では Linux/XFCE first target と runtime detection 方針が明示されており、Windows / macOS / Ubuntu を未実装のまま close 不能とする理由はない。

### 3. 通知 / 常駐の最小機能が GUI 本体と衝突せずに動く

判定: 達成

根拠:

- 2nd planning に対応する tray icon 実装として、`harite.svg` / `harite_off.svg` が package resource 化され、watch on/off を shape 差分で読める tray asset へ置き換わっている。[docs/specs/gui/gui-phase11-2nd-planning.md](docs/specs/gui/gui-phase11-2nd-planning.md) [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py)
- 3rd planning に対応する application icon 実装として、`harite_app.svg` が追加され、main window の window icon と about 内 symbol に適用されている。[docs/specs/gui/gui-phase11-3rd-planning.md](docs/specs/gui/gui-phase11-3rd-planning.md) [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) [src/harite/gui/adapters/gtk_dialog_builders.py](src/harite/gui/adapters/gtk_dialog_builders.py)
- GUI 側の非 tray 面については [tests/gui/test_gtk_runtime_backend.py](tests/gui/test_gtk_runtime_backend.py) を含む `tests/gui` が通過済みで、about dialog や GTK runtime backend の既存挙動を壊していない。
- tray / taskbar / about の最終見え方については owner の XFCE 実機確認が済んでいる。

判断メモ:

- Phase11 の「最小機能」は、通知機能を大量追加することではなく、常駐導線と GUI 呼び出し・状態表示が衝突せず成立することにある。
- tray 自体の成立、watch 状態 icon、dialog 呼び出し、application icon surface の分離まで揃っているため、roadmap 要求には到達している。

## close を妨げない残件

- Windows / macOS / Ubuntu の各 OS 専用実装は今後の拡張対象として残るが、Phase11 の完了条件は方針説明可能性までであり、同時実装までは要求していない。
- tray icon や application icon family の追加 polish は残り得るが、現時点の実機確認結果を見る限り close を妨げる品質問題ではない。
- notification の追加バリエーションや設定項目拡張は将来論点として分離してよく、Phase11 の reopen 条件ではない。

## close 判断メモ

- Phase11 は、1st planning の substrate / menu / state propagation、2nd planning の tray icon、3rd planning の application icon surface 分離まで進んだことで、planning と feature 実装が一つの close judgement に収束した。
- roadmap 観点では、OS integration の責務境界、差分吸収方針、最小常駐機能の 3 本柱が説明可能であり、close 扱いへ進めてよい。
- 以後の icon polish や多 OS 展開を理由に Phase11 を開け続けるより、別論点として切り出す方が整理として素直である。

# GUI Phase11 3rd Planning

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/specs/gui/gui-phase11-1st-planning.md](docs/specs/gui/gui-phase11-1st-planning.md) と [docs/specs/gui/gui-phase11-2nd-planning.md](docs/specs/gui/gui-phase11-2nd-planning.md) を補う、icon surface 分離の補助メモである。
- 2nd planning では tray icon の正本を `harite.svg` / `harite_off.svg` として確定した。
- 本書では、その次段として application icon family をどう扱うか、特に taskbar、about、main window の 3 surface だけを切り出して決める。

## 現状認識

- tray / indicator 側は [src/harite/gui/adapters/tasktray_adapter.py](src/harite/gui/adapters/tasktray_adapter.py) で `harite.svg` / `harite_off.svg` を使う構成まで到達している。
- 一方で current GUI 側には、application icon family の正本 SVG はまだない。
- about dialog は [src/harite/gui/adapters/gtk_dialog_builders.py](src/harite/gui/adapters/gtk_dialog_builders.py) の現行実装では text-only に近く、symbol 専用 widget は持っていない。
- main window / settings / color / about の各 GTK window は title 付き window として構築されているが、現時点では icon surface の統一方針は固定していない。

## 今回の主題

- 旧 [out/wallopt.png](out/wallopt.png) を、application icon family の source SVG へ昇華させる。
- tray icon とは別に、taskbar で見える icon と about 内 symbol の扱いを決める。
- main window については、最近の desktop app で in-window icon を前面に出さない流れを踏まえて方針を決める。

## ここで固定すること

### 1. 旧 wallopt.png は application icon family の source へ昇華する

- 旧 [out/wallopt.png](out/wallopt.png) は tray icon の正本には採らないが、application icon family の由来としては残す。
- したがって「2 画面」「貼る」「異サイズ display でも収める」という意味核は、application icon 側でより素直に継承する。
- tray icon のような極小 panel 最適化は優先せず、application icon 側では旧 wallopt の情報量をやや戻してよい。
- source of truth は SVG で持つ。

### 2. taskbar で見える icon は application icon family を使う

- taskbar で見える icon は tray icon ではなく、application icon family の担当に置く。
- したがって taskbar surface は `harite_app.svg` を first choice とする。
- ここでいう taskbar icon は、window manager / launcher / task switcher で見える application identity を指し、tray icon とは責務を分ける。
- tray と taskbar は同じ motif family に属してよいが、同一 asset を強制しない。

### 3. about 内の symbol は application icon family と揃える

- about は、Harite の identity を最も素直に出してよい surface である。
- したがって about 内 symbol は、tray icon ではなく application icon family を使う。
- 初手では `harite_app.svg` をそのまま about symbol に流用してよく、専用 variant は必要になった時だけ切る。
- つまり about は text-only を維持する必要はなく、application icon family の導入先として最初に候補化してよい。

### 4. main window には in-window icon を載せない

- main window の content 領域には、Harite symbol を常設しない。
- 最近の desktop app では、main window は機能面を前に出し、brand mark を大きく常設しない方が自然である。
- したがって main window は title と機能 widget を主体に保ち、icon は taskbar / about に寄せる。
- ここで main window に載せないと言っているのは in-window logo / symbol であり、OS 側の window icon surface まで否定するものではない。

## surface ごとの役割分担

### tray

- `harite.svg` / `harite_off.svg`
- 小サイズ、symbolic 風、watch on/off の shape 差分を優先する

### taskbar / launcher / task switcher

- `harite_app.svg`
- application identity を優先する
- 旧 wallopt の意味核を tray より強く残してよい

### about

- `harite_app.svg`
- application identity を最も素直に見せる surface とする

### main window

- 専用 in-window icon は置かない
- branding は title / about / taskbar 側へ寄せる

## 現時点の判断

- tray icon 正本は 2nd planning の `harite.svg` / `harite_off.svg` を維持する。
- 旧 wallopt の昇華先は application icon family とし、初手 asset 名は `harite_app.svg` を first choice に置く。
- taskbar で見える icon は application icon family が担う。
- about 内 symbol も application icon family に揃える。
- main window には in-window icon を載せない。

## 次アクション

1. 旧 [out/wallopt.png](out/wallopt.png) を元に `harite_app.svg` の source を起こす。
2. about dialog に symbol を置く場合の最小 layout を決める。
3. GTK / packaging 側で taskbar / launcher surface に何を渡すかを実装上で詰める。
4. main window は icon 非表示のまま維持する。

## 完了条件

- tray と application icon family の責務が分離して説明可能になっている。
- taskbar で見える icon が application icon family 担当であることが説明可能になっている。
- about 内 symbol を tray ではなく application icon family に寄せる判断が説明可能になっている。
- main window に in-window icon を載せない理由が説明可能になっている。

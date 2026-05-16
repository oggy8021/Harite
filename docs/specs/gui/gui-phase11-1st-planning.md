# GUI Phase11 1st Planning

最終更新: 2026-05-16

## 位置づけ

- 本書は [docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md) の Phase11 を初手 planning として具体化する文書である。
- [docs/specs/gui/gui-phase10-closing-check.md](docs/specs/gui/gui-phase10-closing-check.md) により、Phase10 は close 候補として扱い、tray / indicator / notification は Phase11 の主題へ送られた。
- 本書の初版では、いきなり実装方式を固定せず、母体プログラムの踏襲点、owner の現在意図、未決定論点を切り分ける。

## いま Phase11 で扱いたいこと

- GUI を毎回前面起動するより、watch を中心に漫然と常用できる常駐導線を持たせたい。
- その常駐導線は、邪魔になりにくい tray / indicator / notification area に置くのが Harite の利用実態に合う。
- 特に XFCE での自然さを当座の正本対象とし、その後に Windows / macOS / Ubuntu などへ広げる余地を残す。

## owner 現意図

- 母体プログラムの歴史を引き継ぎつつ、Harite では preview など新機能と modernized GUI を足してきた。
- ただし壁紙ツールとして使い慣れると、window を毎回起動するより watch だけ使う比率が高くなる。
- この使い方には system tray / indicator / notification area がよく合う。
- tray icon は watch 起動状態を 2 状態 icon で表せるのが望ましい。
- tray icon は application icon を兼ねてよい。
- 既存 icon は owner のフルエディットであり、この用途に自由に使ってよい。
- multi-scale icon や smoothing の改善余地はあるが、Phase11 初手の必須条件ではない。
- tray の右クリック menu から GUI 本体を呼び出し、必要な操作へ到達できる必要がある。
- GUI 本体呼び出し項目の語彙は、母体どおり `Visible/Invisible` でよい。
- `Settings` と `BaseColor` も tray menu に置いてよい。dialog まで二段階で辿る手間を避ける読みを優先する。
- 終了項目の英字は `Exit` ではなく `Quit` を使う。
- 当座は XFCE で成立すればよく、他 OS は将来 plugin 層とほぼ 1:1 で持つ前提でもよい。

## 母体プログラムで確認できたこと

上流確認元:

- ローカル参照先は `/memories/repo/upstream-reference.md` に記録済みの wallpaperoptimizer リポジトリ。
- 今回の確認では upstream の tray / indicator 実装として `AppIndicator.py`, `Applet.py`, `WindowBase.py` を読んだ。

確認結果:

- tray / indicator menu の項目名は `Visible/Invisible`, `Settings`, `BaseColor`, `About`, `Quit` だった。
- watch 状態は icon の 2 状態切り替えで表現されていた。
- active 側と stopped 側で別 icon を使い分けていた。
- tray icon は application icon と同じ画像資産を兼用していた。
- applet 系では tooltip も `changer on` / `changer off` のように状態変化していた。
- 実装基盤は GNOME 2 panel applet や旧 appindicator 系であり、そのまま再利用する前提ではない。

## 踏襲したい点

- watch 状態を tray icon の 2 状態で読む考え方。
- tray icon と application icon を同一資産系で扱う考え方。
- tray menu から main GUI へ戻れること。
- `Visible/Invisible`, `Settings`, `BaseColor`, `About`, `Quit` の基本 menu 構成を強い踏襲候補として持つこと。
- 初手は既存 icon、既存 dialog、既存 handler、既存 GUI semantics の流用を正本に置くこと。

## そのまま踏襲しない点

- old GNOME / pygtk / appindicator 前提の実装基盤を再採用すること。
- Phase11 初手から全 OS で完全対等な tray 実装を同時に仕上げること。
- tray 導入に合わせて新規 UI 面や新規 dialog semantics を増やすこと。

## 初手論点

### 1. 常駐 surface の正本を何に置くか

- XFCE で自然に使える indicator / status icon / tray のどれを Harite の初手正本 surface と読むか。
- owner の利用実態を言うなら、「XFCE では xfce4-panel 上で使う」は利用先の説明として妥当である。
- ただし `xfce4-panel` は載る先の panel 名であり、採用する tray / indicator 実装基盤名とは分けて扱う。
- 実装基盤の初手候補は、`AyatanaAppIndicator3` 互換を本命に置き、`AppIndicator3` 名でも吸収できる構えを first choice とする。
- したがって検出方針も、install 時の固定判定より runtime の import / load 可否判定を主筋に置く方が安全である。
- Phase11 初手は XFCE 優先でも、将来 Windows / macOS / Ubuntu へ広げられる抽象にしておくか。

### 2. tray menu の最小項目をどこまでに絞るか

初手の基本候補:

- `Visible/Invisible`
- `Settings`
- `BaseColor`
- watch start / stop
- `About`
- `Quit`

保留候補:

- notification settings 的な将来項目

### 3. main GUI 呼び出し項目の語彙

- owner 判断として、main GUI 呼び出し項目の語彙は `Visible/Invisible` をそのまま採る。
- current Harite の語彙と完全一致はしなくても、母体の継承性と tray 上の短い操作語としての分かりやすさを優先する。
- 実装形としても、window visibility は 1 項目トグル寄りで扱う方が自然である。

### 4. watch start / stop の menu 形式

- watch は 1 項目トグルより、`Start Watch` / `Stop Watch` の二項分離を初手方針に置く。
- 理由は、watch には開始条件の検証、実行中状態、停止済み状態、失敗時の戻しがあり、単純な対称トグルより状態責務が重いためである。
- したがって tray menu では、片方を無効化する形を含めた二項分離を first choice として検討する。
- icon の 2 状態表現と menu 項目の 2 状態表現は、同じ意味を指すように揃える。
- tray menu の enabled/disabled は独立 state を持たず、既存の watch 系 state へ伝播し、同じ state に追随させる。

### 5. icon asset の扱い

- owner 既存 icon を Phase11 初手の正本候補に置いてよい。
- multi-scale icon や smoothing 改善は将来論点として残す。
- まずは XFCE で watch on/off と app identity を壊さず読めることを優先する。
- watch 状態の初手対応は単純で、enabled 側を `wallopt.png`、disabled 側を `wallopt_off.png` として扱ってよい。
- したがって icon 側は on/off の 2 状態をそのまま資産名で読み分ける前提に置く。

### 6. `Settings` / `BaseColor` の責務境界

- tray は `Settings` / `BaseColor` を直接編集する面を持たず、「dialog を開く要求」を投げる command surface に留める。
- dialog の所有、state row / notice row、`OK=Apply` や `Save=永続化` の semantics は current GUI 側が持つ。
- したがって tray 側で config 保存、color 適用、validation state を二重管理しない。
- 必要なら main GUI を visible にした上で既存 dialog を開くが、tray 側は launcher を超えない。
- tray 起点で `Settings` / `BaseColor` が変更された場合も、究極の正本は settings JSON への永続化に置く。
- したがって tray 由来の変更は current GUI と別系統に保持せず、既存の設定反映経路を通じて current GUI にも反映させる。

## Phase11 初手の非目的

- preview や settings semantics を再度 reopen すること。
- tray menu から全 dialog / 全 command に到達できるようにすること。
- 旧 pygtk / libappindicator 実装をそのまま移植すること。
- Windows / macOS / Ubuntu まで同時に完成させること。
- icon polishing や AI 生成改善を初手の必須条件にすること。

## 初手の暫定判断

- Phase11 の中心は、常駐そのものより「watch 中心の常用導線を GUI 本体と衝突せずに持つこと」に置く。
- XFCE を first target に置くのは妥当である。
- その説明としては、「Harite は XFCE では xfce4-panel 上の tray / notification area で使う」を採ってよい。
- 一方で実装検討では、`xfce4-panel` を実装基盤名として扱わず、panel 上に出すための実際の tray / indicator substrate を別途選ぶ必要がある。
- 初手の substrate は `AyatanaAppIndicator3` 互換を本命、`AppIndicator3` 名を保険として吸収する形でよい。
- 基盤検出は packaging 時の distro 名分岐より、起動時に import を試し、利用可能な名前空間へ束ねる設計が実務的である。
- 母体の tray icon 2 状態表現は、Harite でも強い踏襲候補とみなしてよい。
- tray menu の語彙は `Visible/Invisible` を採り、終了語彙は `Quit` で固定してよい。
- `Settings` と `BaseColor` は、二段階で dialog へ辿る手間を避けるため、Phase11 初手の基本 menu に含めてよい。
- ただし `Settings` / `BaseColor` の責務は tray へ移さず、tray は既存 dialog を開く要求だけを担う。
- 変更結果の正本は settings JSON に永続化され、その反映結果が current GUI にも戻る、という shared persistence 前提で扱ってよい。
- `Visible/Invisible` は 1 項目トグル寄り、watch は二項分離寄り、という実装観点で進めてよい。
- watch 二項分離の state 表現は、enabled 側が `wallopt.png`、disabled 側が `wallopt_off.png` という単純対応で進めてよい。
- watch 二項分離の enabled/disabled は tray 局所 state にせず、既存 watch state へ伝播して全同種 state を追随させる。
- 初手の新規開発は、既存資産を前提にした event 線の接続を中心とし、新しい意味面の追加は極力避ける。
- したがって初手の主論点は menu 項目の存廃より、XFCE での実装基盤と watch 二項分離の state handling へ寄る。
- 現時点では planning 上の主要判断は揃っており、Phase11 実装は feature 側で進めてよい。
- 追加の Phase11 planning 文書は既定では増やさず、feature 実装中に新しい blocker が出た場合のみ補助メモを切る。

## feature 実装で確認すること

1. `AyatanaAppIndicator3` 互換を本命に、`AppIndicator3` 名吸収まで含めた runtime detection を adapter へどう閉じ込めるかを固める。
2. watch 二項分離の enabled/disabled 切替を、既存 watch state と icon 更新へどう配線するかを固める。
3. `Settings` / `BaseColor` 要求を、dialog-open request から settings JSON 永続化と current GUI 反映まで既存経路へどう接続するかを固める。
4. tray icon / app icon の asset 参照を、初手で既存資産流用のままどこに束ねるかを固める。
5. plugin 層との境界を、OS surface adapter と wallpaper plugin の責務混線なしに保てるかを実装で確認する。
6. 新規作成物を event wiring と最小 adapter に収められるかを feature 実装で確認する。

## 現時点の未決定事項

- planning を止める未決定事項は、現時点では残っていない。
- 残件は feature 実装で具体化すべき接続順、adapter 配置、runtime detection の書き下ろし粒度である。
- したがって本書は「1st planning」の名を持つが、現時点では Phase11 planning の実質版として扱ってよい。

## 完了条件

- Phase11 初手で狙う常駐導線の正本 surface が説明可能になっている。
- tray icon と app icon の関係が説明可能になっている。
- tray menu の最小項目と対象外項目が切り分けられている。
- watch 状態を icon と menu のどちらでどう読むか、特に watch は二項分離かつ `wallopt.png` / `wallopt_off.png` 対応で、既存 watch state への伝播前提が説明可能になっている。
- `Settings` / `BaseColor` について、tray は dialog-open request のみを担い、dialog semantics は current GUI 側が所有し、最終的に settings JSON 永続化と current GUI 反映へ戻ることが説明可能になっている。
- 既存資産流用を正本とし、初手の新規開発が event wiring 中心で足りることが説明可能になっている。
- XFCE を first target に置く理由と、他 OS を後段へ送る理由が説明可能になっている。

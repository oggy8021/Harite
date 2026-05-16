# GUI Phase10 4th Planning

最終更新: 2026-05-13

## 位置づけ

- 本書は Phase10 の 4th planning として、icon 導入を中心に visual rule の後半論点を整理するメモである。
- [docs/specs/gui/gui-phase10-1st-planning.md](docs/specs/gui/gui-phase10-1st-planning.md) では GUI の通常起動導線を扱い、[docs/specs/gui/gui-phase10-2nd-planning.md](docs/specs/gui/gui-phase10-2nd-planning.md) では visual aid / message surface の初手を扱い、[docs/specs/gui/gui-phase10-3rd-planning.md](docs/specs/gui/gui-phase10-3rd-planning.md) では Settings dialog semantics を扱った。
- 本書では、それらで後段へ送ってきた icon library の採否、導入対象面、依存・配布・ライセンス・fallback 方針を扱う。
- ただし icon は主役ではなく、Phase10 で固めてきた message surface と operation semantics を補助するための visual aid として扱う。

## 既決定事項

- Phase10 の visual aid は、まず文字情報を正本とし、色・強調・配置で補助線を作る方針から始まっている。
- Settings dialog semantics は 3rd planning までで `OK=Apply`、`Save=永続化`、`Cancel=無変更終了` に整理済みであり、本書では reopen しない。
- dialog notice は surface 全体の最下段専用 row を持ち、state row と notice row を分離する方針を維持する。
- XFCE は current GUI の正本運用環境であり、icon 導入の評価も XFCE 実機観察を優先する。
- OS integration は Phase11 論点であり、本書では tray / indicator / notification icon までは扱わない。

## 本書に至る経緯

### 1. icon は Phase10 の後半論点として明示的に後送りされてきた

- roadmap では、Phase10 の対象に「補助線や装飾、カラー補助、settings dialog semantics、アイコン導入」を含めると整理されていた。
- ただし 1st planning では、初手で visual aid や icon 導入へ広げず、まず GUI の通常起動導線を利用者向けに整えることを優先した。
- 2nd planning では、settings semantics と icon library の比較へ入るより、どの面で文字・色・強調が不足しているかを先に切る方が局所的であるとして、icon 判断を後段へ送った。
- 3rd planning では、Settings dialog semantics を固めたうえで、icon library の採否や比較は 4th planning で扱う境界を明記した。

### 2. icon 論点は過去フェーズでも断片的に触れられていた

- before-phase5 の layout reconstruction では、方向トグルや open/clear/save/apply の操作種別が「アイコンまたは同等表現で判別できること」を要件に置いていた。
- その時点でも Stock API に依存しきらず、使えない環境では意味等価なアイコン名・記号・短文ラベルで代替し、判別性を維持する方針が書かれていた。
- P5-4 の retrofit modernize では、将来拡張として Lucide / Feather / Remix Icon / Font Awesome の候補をメモしていた。
- Phase6 / Phase8 系でも、アイコン表現の最終整理や About dialog のアプリアイコン導入が将来論点として残されていた。

## owner 由来の背景前提

### 1. 出発点は「画像配置の meaning を GTK 標準フェイスで伝える」ことだった

- もともとの発想は、画像をどう配置するかという直感的な story を、GTK button face や標準 control の見え方を使って伝えることにあった。
- そのため旧 Glade 構成では、GTK 側の標準的な見え方で自然に揃えられる箇所は、できるだけそれを活用する前提で UI を組んでいた。
- したがって icon 導入は、装飾を後付けする話ではなく、「標準 control の意味差で伝えたかったものを current GUI でどう再構成するか」という文脈で読む必要がある。

### 2. fixed window size には整列美と意味差の両方の意図があった

- window size をむしろ固定に寄せることで、各 control を崩さず綺麗に並べ、button face や配置差から meaning を読み取りやすくする意図があった。
- そのため icon を検討する際も、単体の pictogram の是非だけではなく、fixed size 前提での整列、余白、button 同士の見え方まで含めて判断する必要がある。

### 3. platform 方針は当初から Linux 主対象だった

- Windows は当時、Python との相性や GTK の扱いづらさがあり、気軽に対象へ入れにくかったため主対象から外していた。
- Mac は導入コストの高さから対象外としており、その事情は現在も大きくは変わっていない。
- Linux は無償で扱え、複数 distribution を仮想マシンで試せることが、factory class の学習対象としても都合がよく、かつ niche な領域として取り組む動機があった。
- したがって Harite の icon planning も、cross-platform 一般論から始めるより、Linux / XFCE で標準 control をどう活かすかを正本として組み立てる方が origin に近い。

## 現状認識

### 1. current GUI に汎用 icon 基盤はまだない

- current main surfaces は基本的に文字ラベル中心で構成されており、main action や direction toggle へ汎用 icon abstraction はまだ入っていない。
- 一方で native chooser 側には GTK stock 相当が残っており、`gtk_runtime_dialogs.py` では `gtk-save` / `gtk-open` / `gtk-cancel` に相当する stock fallback を dialog button へ渡している。
- したがって icon は既存の統一基盤を整理するより、新たにどこまで導入するかを決める段階にある。

### 2. icon 導入の目的は「装飾」ではなく意味差の補助である

- 方向トグルでは上/下/左/右の判別を補助したい。
- open / clear / save / apply / about / settings のような操作種別では、語だけでなくフェイス差で意味差を補助したい。
- ただし 2nd planning までで確立した message surface の役割を icon へ押し戻すべきではなく、error / corrective notice を icon に背負わせない方針は維持する。
- 特に十字配置とそれに伴う方向 button は、母体プログラム WallpaperOptimizer の面影を支える要素でもあり、これを捨てると「作り直しつつ最新化する」意味自体が薄くなる。

### 3. XFCE 実機と fallback backend の両立が必要である

- XFCE 実機で icon が浮かず、かつ button face や spacing を壊さないことが必要である。
- 一方で fallback GTK runtime backend と fake-GTK tests があるため、icon 導入時の failure mode をどう扱うかは先に決める必要がある。
- owner 方針としては、HTML の ALT 的な長文代替ラベルを UI へ置く発想は採らず、画像 asset が引けないならその環境は試験・利用対象外と割り切る寄りで読む。
- したがって Phase10 4th の論点は、単なる library 比較ではなく、「Linux / XFCE の標準 control 活用に沿う」「fallback 実装で壊れにくい」「テストで意味差を固定できる」を同時に満たすかにある。

## 問題の見立て

### 1. icon を入れたい気持ちはあるが、全面導入は責務が大きい

- app icon、button icon、toggle icon、tab icon、About icon、status icon まで一気に広げると、Phase10 の後半論点としては範囲が広すぎる。
- current GUI は起動導線、message surface、settings semantics の整理を優先してきたため、icon まで全面同期すると phase の焦点がぼける。

### 2. icon library の採用は dependency judgement を伴う

- pip dependency として導入するのか、SVG asset を vendor するのか、system icon theme を優先するのかで、配布・保守・ライセンス・テスト負荷が変わる。
- ただし owner の現時点判断では、配布・保守・ライセンス・テスト負荷は「避けるべき障壁」ではない。むしろ CCC や MIT 系の面白い icon collection を採ること自体に積極的な関心がある。
- XFCE は icon theme を持つが、それを正本にすると Harite 側が theme へ lock-in されるため、採るべき方向ではない。

### 3. icon が逆に UI を曖昧化する箇所もある

- Settings dialog のように操作 semantics をラベルで明確にした面では、icon を足しすぎると語義の読みをむしろ邪魔する可能性がある。
- 一方で icon と semantics 用語の対応が整理されれば、将来的に簡易ヘルプを置く意義へ繋がる余地もある。ただしこれは本書の中心論点ではなく、優先度は低い。

## 今回 reopen しない点

- message surface の state row / notice row 規約そのものは reopen しない。
- Settings dialog の button semantics を icon 設計の都合で再変更しない。
- tray / indicator / app indicator icon のような OS integration 論点は reopen しない。
- 色による success / error / running の最低限規約は reopen しない。

## 比較候補

### 案1: system icon theme 優先

- GTK / XFCE の icon theme 名を優先し、取得できない場合だけ文字ラベルへ戻す。

利点:

- XFCE との見た目整合は取りやすい。
- icon asset を repo へ抱え込まずに済む。
- native dialog 側に残っている stock / theme 的な流れと親和性がある。

懸念:

- Harite 側が desktop theme に lock-in される。
- theme 差分で見え方が揺れやすい。
- 母体プログラム由来の meaning を Harite 側で固定しにくい。

現時点の扱い:

- owner 判断に照らすと正方向の本命案ではなく、退ける前提の対照案として扱う。

### 案2: repo 内に軽量 SVG icon set を同梱

- Lucide / Feather / Remix Icon などの軽量 SVG を vendor し、必要箇所だけ使う。

利点:

- 見え方を repo 内で固定しやすい。
- XFCE でも他環境でも meaning consistency を保ちやすい。
- 将来 app icon や About dialog の固有 icon へ繋げやすい。
- CCC や MIT 系を含む icon collection を明示的に選び、その作者や license 条件を尊重した形で取り込める。
- 十字配置や方向 button の meaning を、WallpaperOptimizer 由来の面影を残したまま current GUI へ再構成しやすい。

懸念:

- asset 読み込み失敗時の扱いを UI 上でどう切るかを先に決める必要がある。
- fixed window size 前提で、どの面まで icon を載せても layout を崩さないかの見極めが要る。

### 案3: library 導入は見送り、語彙と簡易記号だけ整える

- 文字ラベルと最小限の記号だけで meaning difference を整え、icon library は Phase10 では導入しない。

利点:

- 依存・配布・ライセンス問題が増えない。
- current tests / fallback backend をほぼ崩さない。
- Phase10 の焦点を operation clarity に留められる。

懸念:

- roadmap で触れてきた icon 導入はさらに先送りになる。
- direction / helper actions の直感性改善は限定的になる。
- WallpaperOptimizer 由来のフェイス差や十字配置の面影を current GUI へ戻す力が弱い。

現時点の扱い:

- 初手の保険案としては残るが、WallpaperOptimizer の面影を戻す主題には弱く、第一候補ではない。

## 評価軸

1. XFCE 実機で自然か。
2. direction / open / clear / save / apply の意味差を強められるか。
3. message surface の既決定規約と競合しないか。
4. WallpaperOptimizer 由来の十字配置と方向 button の面影を保てるか。
5. fallback runtime backend と fake-GTK tests に対して、asset failure の扱いを明快に定義できるか。
6. app icon / About icon / main action icon へ段階展開しやすいか。

## 現時点の暫定落としどころ

- 4th planning の初期結論としては、「いきなり全面 icon 化」ではなく、「意味差が強い箇所へ限定導入する前提で、library 採否を比較する」が第一候補である。
- 比較対象は、P5-4 で候補化した Lucide / Feather / Remix Icon / Font Awesome のような独立 icon set を主軸にし、system icon theme 優先案は lock-in 懸念のある対照案として退ける方向で読む。
- 導入対象の初手は、direction toggle、open / clear 補助操作、Save / Apply 系の副操作差、About dialog の app icon に限定して読む。
- message / notice / status の意味付けは icon に寄せず、文字と色の rules を正本に据えたままにする。
- そのうえで、owner の origin に沿う第一読解は「GTK 標準フェイスや標準 control を活かして meaning を出せるか」であり、独自 icon set の導入はその後段比較とする。
- ただし system theme への依存は正方向ではなく、独立 icon set と fixed window size 前提の整列で、WallpaperOptimizer の面影を current GUI へ戻せるかを主眼に置く。

## ここまでで実質決めてよい点

1. system icon theme を Harite の正本方針にはしない。
2. icon 不在時に長い代替ラベルで UI を保険する方針は採らない。
3. 配布・保守・ライセンス・テスト負荷は、icon 導入を避ける理由にはしない。
4. 十字配置と方向 button は、WallpaperOptimizer の面影として保持対象に置く。
5. icon は全面導入ではなく、意味差が強い面から段階導入する。
6. 1st try の icon set は Lucide を第一候補として進める。
7. Harite が MIT である以上、非 MIT 系 icon set は採用ハードルが高い前提で比較する。
8. Lucide と Feather の差は現時点では大差なしだが、導入判断としては Lucide で進めてよい。
9. direction toggle の矢印だけは Lucide 内で arrow-normal と arrow-big の 2 派生を残論点として持つ。

## 実装ブランチへ持ち越す決定項目

### 決定 1: 採用する icon source 方針

- 独立 icon set を vendor する前提で進めるか。
- vendor する場合、1st try は Lucide で固定し、Feather は mock 比較の対照案として扱うに留めるか。
- application icon は比較対象から外し、button/toggle/main UI icon だけを icon set 比較対象にするか。

補足:

- owner 判断としては、Lucide と Feather の差は採用を覆すほど大きくないため、icon source は Lucide で進めてよい。
- そのため残る実質論点は icon set 間比較より、Lucide の direction toggle に `arrow-up/down/left/right` を使うか、`arrow-big-up/down/left/right` を使うかに寄る。
- この論点は HTML mock では閉じず、実装ブランチで GTK 実見を通して決める。

### 決定 2: Phase10 で実際に触る surface 範囲

- direction toggle を最優先面として固定するか。
- open / clear、Save / Apply、About dialog のうち、Phase10 同時着手対象をどこまでにするか。
- status / notice / settings semantics 面は、今回 icon 対象から明示的に外すか。

### 決定 3: asset failure の扱い

- asset が引けない環境は試験・利用対象外とみなす方針を、実装方針としてそのまま採るか。
- failure 時に即失敗させるのか、起動前検査で落とすのか、開発時チェックに寄せるのか。
- fake-GTK tests では何をもって「icon 導入済み」と見なすか。

## 次の成果物に流すもの

- icon set 比較メモ: [docs/specs/gui/gui-phase10-iconset-comparison.md](docs/specs/gui/gui-phase10-iconset-comparison.md)
- icon source 候補の shortlist と、その採否理由。
- Phase10 で触る widget / surface の対象一覧。
- Main Window icon 適用前の軽量 HTML mock: [docs/specs/gui/gui-phase10-icon-html-mock-memo.md](docs/specs/gui/gui-phase10-icon-html-mock-memo.md)、[docs/specs/gui/gui-phase10-icon-mock.html](docs/specs/gui/gui-phase10-icon-mock.html)
- asset failure をどこで検出し、どこで失敗扱いにするかの実装メモ。
- application icon は別系統 asset として扱う前提確認。
- fixed window size 前提で崩してよい箇所と崩してはいけない箇所の確認メモ。

## Lucide first wave inventory 暫定案

前提:

- ここでの first wave は、WallpaperOptimizer 由来の meaning difference を戻す面に絞る。
- icon 単独に寄せ切らず、必要に応じて短い文字列を残す前提で読む。
- icon only の最終判断は HTML mock だけでは置かず、GTK 実機へ載せた時点で再判断する。
- そのため feature として最初に試す UI は icon + label を基準に置く。
- SVG 自体の色替えや塗り variant は、現時点では組み込み asset の改変版を増やさず、まず元 asset のまま試す。
- application icon は本 inventory の対象外とする。
- Settings / Help / About / Color のような header command と、Settings dialog の Save / OK / Cancel は、GTK 標準 face を優先して後段送りに置く。

### first wave に入れる面

- tgl_upper_l: 現在ボタンフェイス文字列 Top-L / 代替短縮文字列案 Up-L / lucide icon URL <https://lucide.dev/icons/arrow-up> / 左 display の上寄せ toggle。
- tgl_upper_r: 現在ボタンフェイス文字列 Top-R / 代替短縮文字列案 Up-R / lucide icon URL <https://lucide.dev/icons/arrow-up> / 右 display の上寄せ toggle。
- tgl_lower_l: 現在ボタンフェイス文字列 Bottom-L / 代替短縮文字列案 Dn-L / lucide icon URL <https://lucide.dev/icons/arrow-down> / 左 display の下寄せ toggle。
- tgl_lower_r: 現在ボタンフェイス文字列 Bottom-R / 代替短縮文字列案 Dn-R / lucide icon URL <https://lucide.dev/icons/arrow-down> / 右 display の下寄せ toggle。
- tgl_push_left_l: 現在ボタンフェイス文字列 Left-L / 代替短縮文字列案 Lt-L / lucide icon URL <https://lucide.dev/icons/arrow-left> / 左 display の左寄せ toggle。
- tgl_push_right_l: 現在ボタンフェイス文字列 Right-L / 代替短縮文字列案 Rt-L / lucide icon URL <https://lucide.dev/icons/arrow-right> / 左 display の右寄せ toggle。
- tgl_push_left_r: 現在ボタンフェイス文字列 Left-R / 代替短縮文字列案 Lt-R / lucide icon URL <https://lucide.dev/icons/arrow-left> / 右 display の左寄せ toggle。
- tgl_push_right_r: 現在ボタンフェイス文字列 Right-R / 代替短縮文字列案 Rt-R / lucide icon URL <https://lucide.dev/icons/arrow-right> / 右 display の右寄せ toggle。
- btn_get_img_l: 現在ボタンフェイス文字列 Open-L / 代替短縮文字列案 Op-L / lucide icon URL <https://lucide.dev/icons/folder-open> / 左入力 image 選択。
- btn_get_img_r: 現在ボタンフェイス文字列 Open-R / 代替短縮文字列案 Op-R / lucide icon URL <https://lucide.dev/icons/folder-open> / 右入力 image 選択。
- btn_clr_path_l: 現在ボタンフェイス文字列 Clear-L / 代替短縮文字列案 Clr-L / lucide icon URL <https://lucide.dev/icons/folder-x> / 左入力 path の解除。
- btn_clr_path_r: 現在ボタンフェイス文字列 Clear-R / 代替短縮文字列案 Clr-R / lucide icon URL <https://lucide.dev/icons/folder-x> / 右入力 path の解除。
- optimize_btn: 現在ボタンフェイス文字列 Save As / 代替短縮文字列案 Save / lucide icon URL <https://lucide.dev/icons/save> / Compose -> Optimize -> Apply flow 上の保存操作。
- optimize_modern_btn: 現在ボタンフェイス文字列 Optimize / 代替短縮文字列案 Optimize / lucide icon URL <https://lucide.dev/icons/image> / action cluster 上の optimize 実行操作。image を処理対象の比喩として読む。
- apply_btn: 現在ボタンフェイス文字列 Apply / 代替短縮文字列案 Apply / lucide icon URL <https://lucide.dev/icons/wallpaper> / apply target を wallpaper へ反映する意味を優先して読む。Feather 比較では display 系の近似として monitor を当てる。
- btn_daemonize: 現在ボタンフェイス文字列 Watch Start / 代替短縮文字列案 Play / lucide icon URL <https://lucide.dev/icons/play> / watch 系は当面 play / pause の pair で固定する。
- btn_cancel_daemonize: 現在ボタンフェイス文字列 Watch Stop / 代替短縮文字列案 Pause / lucide icon URL <https://lucide.dev/icons/pause> / watch 系は当面 play / pause の pair で固定する。

### 今回は後段送りに置く面

- btn_setting: 現在ボタンフェイス文字列 Settings / 代替短縮文字列案 Settings / lucide icon URL <https://lucide.dev/icons/settings> / header command だが、まずは文字 face を維持する。
- btn_about: 現在ボタンフェイス文字列 About / 代替短縮文字列案 About / lucide icon URL <https://lucide.dev/icons/info> / app icon と論点が混ざりやすいため後段送り。
- btn_set_color: 現在ボタンフェイス文字列 Color / 代替短縮文字列案 Color / lucide icon URL <https://lucide.dev/icons/swatch-book> / color semantics は別論点が残るため後段送り。
- prefs_save_btn: 現在ボタンフェイス文字列 Save / 代替短縮文字列案 Save / lucide icon URL <https://lucide.dev/icons/save> / Settings dialog の標準 face を優先する。
- prefs_ok_btn: 現在ボタンフェイス文字列 OK / 代替短縮文字列案 OK / lucide icon URL なし / GTK 標準 button face を優先する。
- prefs_cancel_btn: 現在ボタンフェイス文字列 Cancel / 代替短縮文字列案 Cancel / lucide icon URL なし / GTK 標準 button face を優先する。
- about_close_btn: 現在ボタンフェイス文字列 About Close / 代替短縮文字列案 Close / lucide icon URL なし / dialog close は標準 face を優先する。

この inventory から先に進めるときは、Main Window から着手する前提を先に固定する。

- 第1群: direction toggle 8 件と open / clear 4 件。
- 第2群: Save As と Apply。
- 第3群: Watch Start と Watch Stop。

厳密な件数合わせではなく、Main Window の主操作面をおおよそ 3 分割で進める読みとする。

進め方としては、まず 1/3 ずつ適用して様子を見る。途中段階で見え方と操作感が十分に整い、icon 導入の迷いが薄れたなら、その時点で Main Window 面をまとめて適用し切る判断も許容する。

この判断は机上で詰め切るものではなく、最終的には実機で見て決める前提に置く。実装前に軽い HTML mock で面の当たりを確認するのは有効、ではなく、今回の icon 適用では低コストな正式通過点として扱う。正本の確認は XFCE 実機上での見え方と操作感に置くが、実装着手前に HTML mock を一度通し、必要なら Lucide / Feather の差し替え比較もそこで済ませる。

2026-05-15 時点の owner 判断では、Lucide と Feather の優劣差は小さいため Lucide で進めてよい。一方で direction toggle の `arrow-normal` と `arrow-big` はどちらも捨て切れず、ここだけは実見で再判断する。
また、`icon only` と `icon + label` の比較は HTML mock だけでは詰め切らず、feature 試行の初手は `icon + label` を採る。
さらに、filled などの SVG 改変 variant は今は増やさず、GTK へ元 asset を載せた印象を見てから必要時のみ別途検討する。

## Phase10 4th の閉じ方

- 本 planning では、icon source を Lucide で進めること、feature 初手を icon + label に置くこと、filled variant を今は増やさないこと、の 3 点までを確定扱いにして閉じてよい。
- `arrow-normal` と `arrow-big` のどちらを採るかは、planning で詰め切る対象ではなく、実装ブランチで GTK 実見を通して決める。
- したがって 4th planning の未了論点は「方向 icon の最終 face 決定」に限定され、これは planning 継続理由ではなく implementation entry 条件として扱う。

## 実装ブランチで再確認する点

1. direction toggle で `arrow-normal` と `arrow-big` のどちらが GTK 実見で自然か。
2. fallback runtime backend で icon presence をどう表現・検証するか。
3. asset failure を実装上どこで失敗扱いにするか。

## 非目的

- OS tray / indicator icon をここで設計すること。
- 全 button / 全 tab / 全 status へ同時に icon を載せること。
- Settings dialog semantics や message surface を icon 設計の都合で再変更すること。
- 美観だけを理由に current labels を一気に削ること。

## 完了条件

- icon 導入の目的が「装飾」ではなく、どの meaning difference を補助するものか説明可能になっている。
- shortlist 化した icon source の採否理由が説明可能になっている。
- 初手導入面と後段送り面が切り分けられている。
- Main Window icon 面の軽量 HTML mock が作られ、見た目とトーンの当たり確認を一度通している。
- asset failure の扱いが実装判断として説明可能になっている。
- Phase10 の visual rule / operation rule と衝突しない icon 方針が定義されている。
- 方向 icon の最終 face だけは実装ブランチ持ち越しでも、本 planning を閉じる支障にならないことが明示されている。

# GUI Phase10 Icon Set Comparison

最終更新: 2026-05-15

## 位置づけ

- 本書は [docs/specs/gui/gui-phase10-4th-planning.md](docs/specs/gui/gui-phase10-4th-planning.md) から切り出した、icon set 候補の比較メモである。
- 本書では icon source 候補そのものを比較し、導入面や operation rule 全体は 4th planning 側で扱う。
- 本書の比較対象は main UI / dialog / direction button 用 icon に限り、application 自体の icon は含めない。
- system icon theme は lock-in 懸念が強いため、本書の主比較対象から外し、独立 icon set を比較する。
- 記載内容は 2026-05-13 時点の quick check であり、採用決定前に最終確認を要する。

## 評価軸

1. ライセンス
2. コミュニティ状況
3. スケールへの対応可否
4. 具体的に使う候補のアイコンがあるか

## 読み方の前提

- Harite では icon font より、必要 icon だけを SVG asset として持つ前提を初手候補とする。
- 理由は、fixed window size 前提で size を詰めやすく、不要 asset を抱え込みにくく、PyPI 配布や build artifact でも同梱対象を局所化しやすいためである。
- したがって本書の「スケールへの対応可否」は、font 利用可否より、SVG vendor 前提での拡縮・整列・部分同梱のしやすさを重めに読む。
- Harite 本体は MIT project であるため、非 MIT 系または独自 license の icon set は、それだけで採用ハードルが一段上がる前提で読む。
- 実装前の軽い HTML mock は、単なる配置確認だけでなく、icon set 全体のトーン確認と、Lucide から Feather へ急に振りたくなった場合の差し替え容易性確認にも使う前提で読む。
- 候補比較のために各 icon set の配布 pack や zip をローカルへ取得して眺めること自体は許容する。理由は、差し替えや隣接候補の試行のたびに都度フェッチせず、比較コストを下げるためである。ただし、repo と配布物には必要 SVG だけを選んで残す前提で読む。

## 比較対象

- Lucide
- Feather
- Remix Icon
- Font Awesome Free

## 候補別メモ

### Lucide

- ライセンス:
  - 公式 license page 上は ISC License。
  - ただし Feather 由来 icon については MIT License の記載も併記されている。
- コミュニティ状況:
  - GitHub releases では 1.14.0 が 2 週間前公開で、直近数週間も継続更新がある。
  - issues / pull requests / discussions が継続しており、停止感は薄い。
- スケールへの対応可否:
  - 公式 icon page で Copy SVG / Copy JSX を持ち、html / icon font / 各種 framework package 導線もある。
  - SVG 前提で扱いやすく、fixed window size 内でも vector asset として調整しやすい。
- 具体候補アイコン:
  - `arrow-up`、`move`、`save` は公式 icon page で確認済み。
  - 方向系の派生も多く、direction button の初手候補には十分見える。
- 暫定所見:
  - active さと SVG 利用のしやすさの両面で強い。
  - license が単純寄りで、Phase10 の first candidate として読みやすい。
  - owner が最近見た記事や成立背景の印象も含め、今回の origin には最も合っている第一候補である。
  - ライセンス交差や交雑をできるだけ避けたい現時点判断とも噛み合い、1st try の本命として最も自然である。

### Feather

- ライセンス:
  - repo の LICENSE は MIT License。
- コミュニティ状況:
  - GitHub releases の latest は v4.29.2 で 2024-05-01。
  - 完全停止とは言い切れないが、Lucide や Remix Icon と比べると更新 cadence は遅い。
- スケールへの対応可否:
  - 公式 site に Customize があり、size / stroke width / color を直接変えられる。
  - raw SVG をそのまま vendor しやすく、fixed size 前提の整列にも合わせやすい。
- 具体候補アイコン:
  - raw SVG として `save.svg`、`settings.svg`、`image.svg`、`move.svg` は確認済み。
  - 公式 site 上でも `arrow-up` を含む方向系が確認できる。
- 暫定所見:
  - simple で origin に近い読みがしやすい。
  - ただし 2 年近く active update が弱く、Lucide や Remix Icon と比べると採用優先度は下がる。
  - それでも、過度に情報量が多くない smart さと簡潔さでは意外に second candidate として筋がよい。

### Remix Icon

- ライセンス:
  - official site では personal / commercial use free と案内されている。
  - repo の License file は Remix Icon License v1.0、Version 1.0 - January 2026。
  - この license は standalone icon sale を禁じるだけでなく、icon を logo / trademark / brand identifier / app icon として使うことも禁じている。
  - 一方で larger work の一部として icon を含めること、permissive license の project へ統合すること自体は許容している。
- コミュニティ状況:
  - GitHub releases の latest は v4.9.1 で 2026-01-29。
  - 2024-2026 にかけて継続追加と調整が見え、active さは十分高い。
- スケールへの対応可否:
  - official site で Vector を明示し、GitHub releases でも SVG zip と font zip を配布している。
  - category 数と variation が多く、scaled use の選択肢は広い。
  - Harite の初手ターゲットを SVG vendor に寄せるなら、font 導入を避けつつ必要 icon だけを同梱する読みがしやすい。
- 具体候補アイコン:
  - official site 上で `arrow-up`、`arrow-left-right`、`arrow-up-down`、`save`、`settings`、`image`、`layout-left`、`layout-right` などを確認できる。
  - 十字配置や方向 button の再構成にはかなり相性がよい。
- 暫定所見:
  - UI meaning 用の候補の豊富さはかなり強い。
  - ただし app icon や brand identity まで同一 set から取る構想とは強く衝突する。
  - 今回は application icon を本比較の外へ出すため、この制約は UI icon 用途に限定して読む。
  - PyPI 配布や build artifact の観点では、「必要 SVG だけを larger work の一部として同梱する」限りは読みやすい。
  - 逆に、icon pack 自体を再配布しているように見える bundling や、icons が主価値に見える packaging には注意が要る。

### Font Awesome Free

- ライセンス:
  - icon SVG / JS は CC BY 4.0。
  - font は SIL OFL 1.1。
  - code は MIT。
  - official license page では attribution と brand icon 利用上の注意が明示されている。
- コミュニティ状況:
  - GitHub releases の latest は 7.2.0 で 2026-02-11。
  - repo 規模と release cadence の両面で active さは高い。
- スケールへの対応可否:
  - SVG / JS / web and desktop fonts が揃っている。
  - 技術的には十分扱いやすいが、font 系と svg 系で license 読みが分かれる。
- 具体候補アイコン:
  - official search 上で `save`、`gear`、`image` に対応する名前は確認できる。
  - ただし quick scan では Free / Pro / Pro+ の混在が強く、実際に Harite で使う icon が Free 範囲に全て収まるかは追加確認が要る。
- 暫定所見:
  - community と asset の厚みは強い。
  - 一方で Free / Pro 境界と複数 license 体系があり、Harite の今回用途では少し読みが重い。

## quick comparison

| 候補 | ライセンス読み | コミュニティ状況 | スケール対応 | 候補アイコンの見え方 |
| --- | --- | --- | --- | --- |
| Lucide | 比較的読みやすい | 活発 | SVG 前提で扱いやすい | direction / move / save は良好 |
| Feather | MIT で単純 | やや穏やか | size / stroke 調整しやすい | direction / save / settings / image を確認 |
| Remix Icon | 独自 license v1.0 に注意 | 活発 | SVG / font とも強い | direction / layout / save / settings / image が豊富 |
| Font Awesome Free | 複合 license で重め | 活発 | 技術面は強い | 候補は多そうだが Free 範囲の pin が要る |

## 現時点順位

1. Lucide
2. Feather
3. Remix Icon
4. Font Awesome Free

## 現時点の読み

- active maintenance と成立背景の相性を両立すると、Lucide は現時点の最上位候補である。
- ライセンス交差をなるべく避け、自然な license path を優先するなら、1st try は Lucide に軍配が上がる。
- Feather は更新停滞の弱みを持つ一方、simple で smart な見え方という意味では second に再浮上しうる。
- Remix Icon は歴史も十分あり、UI meaning に必要な候補の豊富さでは非常に強いが、現時点では second より third 候補として置く方が整理しやすい。
- 候補の豊富さと十字配置再構成のしやすさでは Remix Icon が強い。
- application icon は独自 asset 側で扱う前提になったため、Remix Icon の brand identity 制約は UI icon 採否へ限定して読める。
- PyPI や build 配布を踏まえると、初手は icon font 化ではなく、必要 SVG だけを vendor して larger work の一部として同梱する読みが最も扱いやすい。
- Harite 自体は MIT project だが、Remix Icon を採る場合でも icons 自体は Remix Icon License v1.0 のまま扱う必要がある。
- そのため、MIT ではない候補は「使えなくはない」が、Harite の現行方針では明確に不利である。
- そのため配布面では「Harite 本体の一部として必要 SVG を同梱する」のは読みやすい一方、「icon pack を同梱再配布している」と見える形は避けた方が安全である。
- Font Awesome Free は asset と community は強いが、Harite の今回判断では Free / Pro 境界と複合 license が少し煩雑である。

## 現時点の暫定結論

- 1st try は Lucide を採る。
- 理由は、成立背景の相性、active maintenance、SVG 利用のしやすさ、license の単純さの 4 点が揃っているためである。
- Feather は比較対象として有効だったが、現時点の owner 判断では Lucide と有意差が薄いため、採用候補としては Lucide へ寄せてよい。
- ただし実見候補としては、Lucide 内で direction toggle のみ `arrow-normal` と `arrow-big` の 2 派生を分けて見る。
- Remix Icon は有力な third candidate として残すが、license の読みと配布時の扱いが Lucide や Feather より一段重い。
- MIT 以外の候補は、Harite が MIT である以上、相当に強い上積み理由がない限り first choice にはしにくい。

## HTML mock 上の候補棚

1. Lucide (arrow-normal)
2. Lucide (arrow-big)
3. Feather

- これは採用順位ではなく、2026-05-15 時点で出そろった目視比較用の候補棚である。
- 1 と 2 の差は icon set 全体ではなく、direction toggle に `arrow-up/down/left/right` を使うか、`arrow-big-up/down/left/right` を使うかの差である。
- 3 は set ごと差し替えた対照案である。

## 本比較の外に置くもの

- application 自体の icon
- owner が別途用意する独自 asset
- 母体プログラム由来で owner が既に保持している dot 絵 asset

## 採用前の追加確認

1. Harite で first wave に必要な icon 名を 10 個前後に絞り、各候補で実在確認する。
2. Remix Icon を採る場合、brand identifier 禁止条項と UI icon 用途が衝突しないかを明示確認する。
3. Remix Icon を採る場合、PyPI 配布物や build artifact に含める SVG 数と license notice の置き方を明示確認する。
4. Font Awesome Free を残す場合、使いたい icon が Free 範囲かを個別に pin する。
5. Lucide を 1st try に据えたままでも、同じ Main Window 面を Feather へ差し替えた mock をすぐ作れる構成にして、トーン差と差し替えコストを実見で比較する。

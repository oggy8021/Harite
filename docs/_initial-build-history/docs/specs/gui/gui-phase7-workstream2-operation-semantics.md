# GUI Phase 7 Workstream 2: 操作語彙の再設計

最終更新: 2026-04-21

## 位置づけ

- 本書は Phase7 product alignment における Workstream 2 の詳細メモである。
- 目的は、`optimize` / `apply` / `Default` / `Auto-split` / explicit mapping の語彙と責務境界を再定義することにある。
- index は [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md) を参照する。

## 現時点の読み解きメモ

- `two_screen` と `apply_mode` は別レイヤーの概念である。
  - `two_screen`: optimize 時に 2入力と表示構成に応じて 1 枚の合成結果をどう作るかを決める。
  - `apply_mode`: optimize 後の 1 枚を、そのまま貼るか、apply 時点で分割するかを決める。
- current CLI `apply --file <4096x1280>` の既定動作は、2画面文脈を見た暗黙分割ではなく、`single-file` として plugin 実装部へそのまま渡す経路である。
- GUI は 2入力かつ 2画面検出時に `two_screen` を自動で有効化するため、user からは optimize と apply が 1 本の two-screen workflow に見えやすい。
- 一方で apply 側の `Default` は `single-file` のままであり、`two_screen` 文脈を参照しない。
- `Default` という visible 語彙が、apply semantics の違いを隠してしまったことが、現行の誤読の直接原因である。

## 3世代比較メモ

### 母体プログラム

- `Apply` は独立した mode 切替ではなく、生成済みの 1 枚を即時に壁紙変更へ渡す動作だった。
- `dry-run` / `do-it` / `Default` / `Auto-split` のような apply mode 語彙は持たない。
- `two_screen` 相当の関心は optimize / compose 側にあり、apply 時点の暗黙分割はない。
- `align` / `valign` は single 値ではなく、左画像・右画像それぞれの pair として保持される。
- `tglPushLeftL` / `tglPushRightR` などの toggle は same-side の pair 要素を書き換える責務であり、反対側を巻き込まない。

### Harite v0.1.2

- CLI に独立した `apply` command と `dry-run` / `--do-it` を導入し、plugin 呼び出しの安全なラッパーとして設計した。
- `--left-file` / `--right-file` / `--auto-split` により、monitor 別 apply の語彙が追加された。
- GUI 側はまだ `dry-run` / `do-it` が前面で、現行の `Default` 語彙は存在しなかった。

### 現在

- CLI は `single-file` / `per-monitor-explicit` / `per-monitor-auto-split` の 3 経路を維持している。
- 曖昧さは、GUI が `Default` / `Auto-split` の 2 択へ言い換えたところで発生している。
- `Default` は current CLI / GUI とも `single-file` であり、2画面文脈を apply 時に参照しない。
- `per-monitor-explicit` は GUI には露出せず、CLI 側の expert 機能として残っている。

## 具体シナリオメモ

### `apply` のみで `per-monitor-explicit` を使う

- 既に `left-A` / `right-B` があるなら、`apply --left-file ... --right-file ...` だけで monitor 別適用できる。
- これは `optimize` workflow ではなく、apply 側の expert 経路である。

### 左右を別々に `optimize` して最後に explicit mapping で貼る

- single-screen optimize を 2 回行い、最後だけ explicit mapping を使う構成である。
- Harite の主導線とは別の expert workflow として読むのが自然である。

### 2 入力で `optimize` し、最後に `auto-split` で貼る

- GUI の現在の導線に最も近い。
- Harite に 2 画面横断の成果物を作らせ、その成果物から monitor ごとの apply target を自動生成する流れである。

### `Default` を選んだとき

- `Default` は current 実装上 `single-file` であり、合成済み 1 ファイルを plugin 実装部へそのまま渡す。
- monitor 別 apply が起きるのは `per-monitor-explicit` または `per-monitor-auto-split` を選んだときだけである。

## Phase7 の現時点判断

- `Default` は「single-file を plugin 実装部の通常 apply 経路へ渡す」と読む。
- GUI 表示語は、最終的に `Default` より `分割せず適用` のような非曖昧語へ寄せる。
- `Auto-split` は、Harite 独自価値として `Apply` の主導線に置く。
- explicit mapping は CLI 専用の低露出 escape hatch として残し、GUI には持ち込まない。
- CLI に残る「小さめ解像度で optimize し、後段 apply で使う」発想は、GUI 非対象の非主導線 workflow として分離する。
- `align` / `valign` については、Harite 独自の single 値類推を撤回し、母体どおり左右別 pair を正本とする。

## 2026-04-21 実装反映: L/R toggle semantics

- 発端:
  - `tglPushRightL` / `tglPushLeftR` などの見た目は左右独立指示なのに、Harite では内部で single `align` / `valign` に潰れていた。
  - これは母体未読のまま Harite 独自表現を類推した結果であり、Phase7 の整合性判断としても不適切だった。

- 母体再確認で分かったこと:
  - 母体 GUI は `option.opts.align[lr]` / `option.opts.valign[lr]` を持ち、toggle は same-side の要素だけを更新する。
  - 母体 CLI も `--align` / `--valign` を左右 2 値として受ける。

- このブランチで閉じたこと:
  - Harite の core / CLI / GUI / prefs / optimize CLI preview を、`align` / `valign` pair semantics へ統一した。
  - 既存 config の single 値は互換的に読みつつ、保存時は左右 2 値として保持する。
  - 「Harite 独自の single 値表現を正本とする」方向は捨て、母体踏襲で close する。

## 現時点で自然な表示語候補

- main 画面候補:
  - `分割せず適用`
  - `自動分割して適用`
- 設定ダイアログ候補:
  - `適用: 分割なし`
  - `適用: Auto-split`
- 補助文言候補:
  - `追加分割なしで適用`
  - `1ファイルをそのまま適用`

## 次に詰める問い

- main 画面では英語ラベルを維持するのか、日本語寄り説明へ寄せるのか。
- `Auto-split` は固有名として残すのか、`自動分割` へさらに言い換えるのか。
- main 画面の短いラベルと補助ラベル / tooltip 相当の説明責務をどう分担するか。
- `Prefs` dialog の apply mode 表示を main 画面と完全一致させるか、設定項目として少しだけ技術的な語を残すか。

## 再点検すべき仕様仮説

- 点検順は、まず current 実装ともっとも整合する基準線を置き、その派生として CLI 専用 workflow を扱い、最後に大きい方向転換や削減案を比較するのがよい。
- 依存関係としては、仮説C が基準線、仮説D/F がその派生、仮説A/B が別方向の上位方針、仮説E が D をさらに強めた削減案である。

### 基準線

- 仮説C: 現在もっとも自然なのは、`Default` を「single-file を plugin 実装部の通常 apply 経路へ渡す」と定義し直すこと。
  - 表示語彙は `single-file` をそのまま前面に出すより、`分割せず適用` のような user 向け表現へ寄せる。
  - そのうえで `Auto-split` は、「合成済み 1 ファイルから monitor 名付きの `left-file` / `right-file` 相当を内部生成して適用する追加処理」であると明示する。
- 少なくとも current 実装に即して読むなら、`Default` は「OS や user の既定動作」ではなく、「Harite が追加分割をせず、plugin 実装部へ 1 ファイルをそのまま渡す経路」を指すと定義しない限り、Phase6 終盤に出た ambiguity は解消しない。

### 基準線からの派生

- 仮説D: `per-monitor-explicit` は CLI 専用の expert 機能として残し、GUI には持ち込まない。
  - その代わり `Harite` の主導線は、「Optimize で最終成果物を作る」または「Auto-split でその成果物から monitor 別適用を自動生成する」に絞る。
  - manual mapping は product の主語から外す。
- 仮説F: CLI に残っている「小さめ解像度で optimize し、後段 apply で使う」発想は、desktop 解像度自動追従とは別の制作寄り運用としては成立するが、主流の user 体験としては弱い。GUI に持ち込む候補というより、CLI 側に残り得る非主導線のニッチ運用として扱うのが自然である。
- D と F は両立する。D は `apply` 側の explicit mapping の扱い、F は `optimize` 側に残る非主導線の CLI 運用をどう位置づけるかを定める派生案である。
- GUI の `Apply(default)` 実機観測では、single-file 経路が primary monitor 側だけに効いたように見えた。
  - この観測は、GUI 主導線を `Optimize` と `Auto-split` に絞る方向を支持する。
  - manual mapping や monitor 明示割当を CLI 専用 expert 機能として外に置く D の方向とも整合する。

### 別方向の上位方針

- 仮説A: 母体プログラムからの考え方の連続性は参照しつつも、Harite で正統進化した仕様を正本とする。そのうえで、`Apply` の基本責務は「生成済みの最終成果物を即時に貼る」に寄せ、`two_screen` は optimize 側の機能として分けて扱い、画面ごとの違いを見て貼り分ける apply は Harite 独自の追加機能として明示する。
- 仮説B: Harite 独自の multi-monitor product として進めるなら、`Apply` 自体を monitor-aware な概念へ拡張し、その場合でも `Default` が何を意味するかを曖昧語のままにしない。
- A/B は C の細部調整ではなく、`Apply` の上位コンセプト自体をどちらへ寄せるかという競合案である。
  - ただし A は「母体へ戻す」こと自体を正本とする案ではなく、母体を参照しつつ Harite で正統進化した仕様を正本として読む案として扱う。
  - そのため D/F より先に決めるというより、C を基準に見たうえで「そこから離れる必要が本当にあるか」を判定する対象である。

### 低露出案

- 仮説E: `per-monitor-explicit` は残す。ただし `Optimize` で作れるものへの user 想像を乱しやすく、`Harite` の価値を「monitor ごとに好きなファイルを貼る汎用ランチャー」へ寄せ過ぎるため、CLI でも主流導線には置かず低露出の escape hatch として扱う。
- この前提では、CLI apply における per-monitor 系でも主流は `auto-split` とし、`--left-file` / `--right-file` を `--auto-split` なしで使う経路は傍流と位置づける。
- E は D の強化版であり、「GUI へ持ち込まない」に加えて「CLI に残しても主流導線にはしない」を含む。そのため D/F の整理後に検討するのが自然である。

## Phase7 で決めるべき問い

### これまでの議論から自然成立している結論

- 正本は、母体か `Harite v0.1.2` かの二択ではなく、母体を参照しつつ Harite で正統進化した仕様に置く。
- `two_screen optimize` の結果に対する既定 `Apply` は、現時点では monitor-aware 既定ではなく、`single-file` による 1 枚貼りのままと読む。
- GUI に `Default` という語を残すより、`分割せず適用` のような非曖昧な表示語へ寄せる。
- CLI にある「実画面解像度へ厳密適合しない optimize 生成物を apply で活用する」発想は、product の中心責務ではなく、GUI 非対象の非主導線 workflow として分離する。

### この時点で置く owner 判断

- `Auto-split` は Harite 独自価値として `Apply` の主導線に置く。

### ここまでに固まった補足整理

- `--left-file` / `--right-file` による explicit mapping は、ひとまず CLI 専用の低露出な escape hatch として残す。
- CLI explicit mapping が許す「monitor ごとに別画像を貼る使い方」は可能ではあるが、Harite の主導線としては扱わない。

この論点は、母体踏襲の pair semantics を正本として Phase7 で close する。

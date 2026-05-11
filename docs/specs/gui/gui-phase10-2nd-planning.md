# GUI Phase10 2nd Planning

最終更新: 2026-05-11

## 位置づけ

- 本書は [docs/specs/gui/gui-phase9-11-roadmap.md](docs/specs/gui/gui-phase9-11-roadmap.md) の Phase10 における visual aid 方針メモである。
- [docs/specs/gui/gui-phase10-1st-planning.md](docs/specs/gui/gui-phase10-1st-planning.md) で起動導線を先に整えたため、本書では visual aid を独立論点として扱う。
- icon library の採否や比較は Phase10 3rd planning へ送る。
- 目的は見た目の派手さではなく、current GUI の理解コストと操作ミスを減らす補助線を定義することにある。

## 現在地

- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) には、`status_level` / `status_phase` / `status_message` / `last_error` という統一された状態表現がすでにある。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) には preview / result / margins / watch など、視覚補助の効果が出やすい面がまとまっている。
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) には footer の `status_label` / `error_label`、preview 同期、color dialog など、visual aid の受け皿がある。
- したがって Phase10 の visual aid は、新しい大きな UI 面を増やすよりも、既存の state / footer / preview / settings surface を整理する方が局所的である。
- ただし現状は Main / Margins / Watch それぞれで messaging の位置が定まっておらず、専用領域というより余白へ散発的に出している読みに近い。
- その結果、何か起きたときにどこを見ればよいかが tab や surface ごとに揺れ、status / error の統一 state が UI 上の統一読点へまだ変換されていない。

## Phase10 2nd の主眼

- status / error / preview の視認性を上げる。
- 文字だけでは見落としやすい操作段階に、補助線や強調を加える。
- 文字情報を正本にしたまま、色・強調・配置で理解負荷を下げる。
- 特に messaging を「何をどこへ出すか」の外周から固め、利用者が見る場所を迷わない状態へ寄せる。

## 非目的

- Phase10 の段階でアプリ全体を派手に再装飾すること。
- theme / dark mode / brand refresh を先に決めること。
- icon library の採否や比較をこの段階で行うこと。
- taskbar / tray / indicator など Phase11 の OS integration に踏み込むこと。

## 問題の見立て

### 1. いま強めたいのは status の階層感

- current GUI には `ready` / `running` / `success` / `error` のような状態語があるが、Phase10 ではこれを視認しやすくする余地が大きい。
- 特に `optimize` / `apply` / `margins` / `watch` は phase と result が混ざりやすいため、色・文言・配置の一貫ルールを先に決めた方がよい。
- いま不足しているのは文言数よりも、Main / Margins / Watch のどこで発生した message なのかを利用者が直感的に追える位置規約である。

### 2. preview は「飾り」ではなく判断補助

- preview/result 周辺は、入力や設定の結果を事前に読む面なので、補助線や軽い強調の費用対効果が高い。
- 一方で補助要素を増やしすぎると、preview の説明面がかえって読みづらくなる。

### 3. error の訴求レベルがまだ弱い

- 現状は error dialog を常設前提にしていないため、「今すぐ設定を直すべき error」なのか「様子見でよい status」なのかの訴え分けがまだ弱い。
- 母体プログラムは例外を dialog 化していたが、Phase10 ではそのまま modal dialog に戻すかどうかは未決定でよい。
- ただし dialog を採らない場合でも、各 surface 近傍に annotation 領域や赤系の注意表示を置くなど、修正動機を与える代替線は必要である。

### 4. 今回は icon 判断を先送りできる

- visual aid の初手としては、icon library を先に決めるより、どの面で文字・色・強調が不足しているかを先に切る方が局所的である。
- したがって 2nd planning では icon library の比較や採用判断へ入らず、3rd planning の独立論点として残す。

### 5. 説明過多より直感操作寄りへ振ってよい

- 最終的に直感的操作だけで完結させる意図があるなら、常時説明文を積み増すより「安全に触って分かる」設計へ寄せた方がよい。
- Harite 側は相手環境を無制限に破壊する類の UI ではないため、説明文で身構えさせるより、必要時だけ近傍で短く知らせる方が合う。
- したがって Phase10 2nd では、説明を増やすより「通常時は静か、注意時だけ目立つ」という messaging 原則を優先する。

## Phase10 2nd の判断方針

- 文字情報を正本にし、色・強調・配置だけでまず補助線を作る。
- まずは footer / status / error / preview / settings の 5 面だけを対象にする。
- error は赤、success は緑、running は中立強調、idle は非強調、のような最低限の状態規約を優先する。
- watch / margins / apply のような誤操作コストが高い箇所を先に読む。
- global な結果通知と、surface 近傍で修正を促す annotation を役割分担させる。
- modal dialog を採るかどうかは現時点で固定しないが、採らない場合でも「修正すべき error が埋もれない」ことを最低条件にする。
- 通常時の説明文は減らし、必要時だけ短く目立つ messaging へ寄せる。

## 近距離の対象面

### 1. Footer feedback

- `status_label` と `error_label` の視認性整理を最優先にする。
- phase と result が混ざらないよう、文言規約と視覚規約を揃える。
- footer は全体状態の要約に寄せ、個別の修正指示まで背負わせすぎない。

### 2. Preview / result area

- optimize 実行前後で、何が入力で何が結果かを見分けやすくする。
- crop / assignment / result note は decoration よりも読み順を整える方を先に取る。

### 3. Margin text / preflight

- ここは `error` と `info` が混ざりやすいので、単なる赤字ではなく「注意」「不可」の段差を出す価値がある。
- ただし Main / Margins は空きスペースが狭く、window サイズ可変や動的配置の影響も受けやすいため、局所 annotation の常設は layout 破綻を起こしやすい。
- したがって「近傍に出す」は必須条件ではなく、固定の message 領域を安全に確保できる場合だけ採る。

### 4. Watch / main flow

- watch は専用 tab を持つため、watch 固有 message は watch surface 側へ寄せた方が自然である。
- main flow も同様に、apply / optimize の修正指示は action cluster 周辺で読めた方が操作往復が短い。
- ただし Main も widget 密度が高いため、button 群の間へ message を差し込む案は優先しない。

### 5. Settings / color dialog

- color は視覚補助テーマと相性が良いが、まず background color と status color を混同しない整理が要る。
- settings dialog では、apply mode や color state の説明を揃える方が先である。

## messaging 外周の仮ルール

- global status:
  - 画面全体の現在相を示す短い要約だけを出す。
- local annotation:
  - 修正が必要な入力や設定の近傍に寄せる。
  - ただし空きスペースや resize 耐性が不足する面では、無理に inline 化しない。
- success:
  - 操作完了を短く示し、長文説明は出さない。
- warning / corrective error:
  - 利用者が次に何を直すべきかが読める短文を優先する。
- blocking error:
  - 将来 dialog を使う余地は残すが、2nd planning ではまず inline / near-field annotation で成立する線を先に考える。

## 開始不可 / 操作不可の見せ方

- 13 や 22 のように、先へ進ませない仕組みで潰す対象は、まず操作を無効化する方を第一候補にする。
- 現状でも前置き文や説明文が多いため、無効理由の常設文を安易に積み増さない。
- README や簡易マニュアルで補足できる範囲は、UI 側で重ねて説明しすぎない。
- 開始ボタンの無効化だけで十分に伝わるなら、それを許容する。
- 追加の補助文や annotation を出すのは、色と配置のルールが決まり、視線誘導の効果が見込める場合に限る。
- 補助文を出す場合も、常設の長文説明ではなく、近傍の短命な短文を優先する。

## messaging 文面の仮ルール

- dedicated messaging region に phase 名は原則として含めない。
- 利用者が見てすぐ動けることを優先し、「何が足りないか」「何を直すか」が読める短文を優先する。
- `input is required` のような抽象文では不足しやすく、対象が分かる文面へ見直す前提で扱う。
- 現在この文書に並べている英語 message 例は、現行実装から拾った観察用の仮案であり、そのまま採用する前提ではない。
- 実装時には、surface ごとに対象語彙を補って、利用者視点で意味が通る文へ再設計する。

## 日本語文面の決定対象

- 現時点の決定対象は、重複を寄せると 20 台前半で収まる。
- 数が爆発していないため、オーナーが上から日本語文面を決める進め方で十分回る。
- 以下は「最終文面」ではなく、「何を伝える message か」の整理である。
- ここでの日本語は planning 用の working 表現であり、実装へ落とす際はいったん英語文面で進めてよい。
- phase 名は message 本文に含めず、必要な補足情報は `()` で後置する前提とする。
- この文書では可読性のため全角 `（）` で補足を書いていても、実装上は半角 `()` でよい。
- 各項目の `←` コメントは、message 妥当性の再検討点、原因の掘り下げ点、または英語原文から追加で意味を取りたい点を表す。

### global summary

- 1: 最適化に失敗したこと
- 2: 適用に失敗したこと（対象Optimize済みファイル名）
- 3: チェンジャーを開始したこと（YYYY/MM/DD HH24:MI:SS）
- 4: チェンジャーを停止したこと（YYYY/MM/DD HH24:MI:SS）
- 5: チェンジャーに失敗したこと（YYYY/MM/DD HH24:MI:SS）
- 6: 設定を保存したこと（保存したパス）
- 7: 設定の読み込みに失敗したこと
- 8: 余白処理を続けられないこと
- 9: 余白テキストを反映できなかったこと

### corrective error

- 10: 左右いづれの画像も入力していないこと
- 11: 適用できる最適化結果がまだないこと
- 12: 保存先が未指定であること
- 13: 余白テキストの配置先を決められないこと ← 14 との差異を見て文面を寄せたい
  - 理由補足: 13 は 14 のような「領域はあるが狭い」ケースとは別で、現行実装では実質ほぼ「解像度が未確定で margin region を計算できない」場合に寄る。position は GUI 側で `top / bottom / left / right` へ正規化され、region 解決関数も valid position なら領域を返すため、「位置指定が解決できない」は現行 GUI では強い主因ではない。
  - 設計メモ: これは message 改善だけでなく、解像度未確定のまま margin text preflight へ進ませない user-blocking 仕様と実装で先に潰す方がよい。position 候補の無効化より、まず resolution 未確定時の操作制約を明示する方が筋が良い。十分に先へ進ませない仕組みを用意できるなら、13 は dedicated messaging region の正式候補から外してよい。無効理由の補助文は、色と場所が決まるまでは必須としない。
  - 英語原文: `margin area unavailable`
- 14: 選択した領域が小さすぎること（選択した領域名）
- 15: 余白値が不正であること ← どのように不正かが分からない、もう少し補足できるか。また、いずれの値が不正なのかは（）に記述したい
  - 理由補足: 現実の validation は「負値禁止」までしか見ていない。ただし UI 側で range 制限する、負値を絶対値へ正規化する、などの実装工夫余地があり、最終的には dedicated messaging region に出さない設計へ寄せる余地もある。
  - 設計メモ: UX 向上として UI 制約で潰す対象に寄せる。
  - 英語原文: `margins must be non-negative`
- 16: 最大行数が不正であること ← internal-only 扱いとし、日本語文面の決定対象からは外す
  - 理由補足: 実装 source 自体はあるが、通常 GUI 操作では出にくく、防御寄り validation に留まるため、利用者向け dedicated messaging region へは出さない前提でよい。
  - 英語原文: `margin_text_max_lines must be positive`
- 17: チェンジャー元フォルダが未指定であること
- 18: チェンジャー元フォルダが不正であること ← わざわざOpenして選んでいるのに不正とは？どのような状態？
  - 理由補足: file chooser 経由の通常操作だけなら出にくい。残すなら「選択後に directory が削除された」「参照不能になった」など、選択後の状態変化まで含めた複合ケースを想定する candidate として扱うのが妥当である。
  - 設計メモ: 想定は狭いが、実行時変化に対する保険として残す。
  - 英語原文: `watch srcdir {side} invalid`
- 19: チェンジャー間隔が不正であること ← 秒数を指定するとき、不正とは・・ マイナス値とかカンマ区切りなど？
  - 理由補足: GUI 実装の判定は `<= 0` のみで、少なくとも 0 以下を拒否する。ただし 15 と同様に UI 側で range 制限してしまえば、利用者向け message 自体を弱めたり不要化したりできる余地がある。
  - 設計メモ: UX 向上として UI 制約で潰す対象に寄せる。
  - 英語原文: `watch interval must be positive`
- 20: 背景色の指定が不正であること（指定した値）
- 21: 設定ファイルのパスが未指定であること ← これも発生しうるのか？
  - 理由補足: save / load の両方で `path` 引数が空文字なら発生する。file chooser を経由した通常操作では出にくいが、dialog が空で閉じた、既存 path が空のまま直接保存/読込した、または signal 経由で空値が渡った場合の防御寄り error と読める。
  - 設計メモ: 想定は狭いが、防御寄りの保険として残す。
  - 英語原文: `settings path is required`
- 22: チェンジャー元フォルダの左右指定が不足していること ← 17 との違いは発生面にある
  - 理由補足: 現行 GUI は `SrcdirL` / `SrcdirR` を押した時点で左右を明示しており、GUI 利用者に「左右指定不足」を出すのは不自然である。これは GUI message 候補というより、watch は左右双方の directory が揃うまで開始不可にする仕様へ寄せるべき論点である。
  - 設計メモ: desired spec としては、CUI では左右双方が揃わない場合は error、GUI では開始ボタンを無効化して未然に防ぐ方が良い。十分に先へ進ませない仕組みを用意できるなら、22 は dedicated messaging region の正式候補から外してよい。したがって 22 は文面確定より watch 開始条件の再設計項目として精査継続とする。GUI では無効化だけで十分に伝わるなら、補助文は必須としない。
  - 英語原文: `watch srcdir side is required`

### blocking 候補

- 23: この環境では壁紙変更に対応していないこと ← 未サポートと明示する
  - 理由補足: 実装上は plugin 名 lookup の `KeyError` をそのまま拾っているが、利用者は plugin を意識していないため、利用者文面では「未サポート環境」と言い切る方が自然である。
  - 英語原文: `unknown plugin`
- 24: 壁紙の適用そのものに失敗したこと（対象Optimize済みファイル名）
- 25: 設定の保存に失敗したこと（保存しようとしたパス）
- 26: チェンジャー開始時の適用に失敗したこと
- 27: チェンジャー中の適用に失敗したこと

### 扱いメモ

- 10 の「入力が不足していること」は、そのままでは抽象的すぎるため、最終文面では何の入力かを必ず補う。
- 15 と 16 のような数値系は、統一した言い方に寄せやすい。
- 16 は internal-only 扱いとし、dedicated messaging region の日本語文面候補から外す。
- 13 と 22 は、十分な user-blocking / UI 制約で未然に防げるなら、dedicated messaging region の文面候補から外してよい。
- 15 と 19 は UX 向上として UI 制約で潰す方を採る。
- 18 と 21 は想定が狭くても、保険として残す。
- 22 は文面確定を保留し、watch 開始条件と UI 制約の設計論点として再精査する。
- 23 から 27 は dedicated messaging region の強い 1 行候補であり、同時常設しない。

## error design の観点

### 基本方針

- error は「発生したか」だけでなく、「利用者に何をさせたいか」で分ける。
- 現状の code path には Main / Margins / Save / Settings / Color / Watch / dialog lifecycle にまたがる error source があるため、単一の赤字や単一 footer では意味が潰れやすい。
- したがって Phase10 2nd では、error を少なくとも global summary、local corrective error、internal-only error の 3 層で扱う前提を置く。
- ただし message を出す surface 自体が散逸すると、それだけで回帰になるため、surface の数を増やしすぎないことを同時に原則とする。

### surface 数の制約

- Phase10 2nd では、「どこでも出せる」設計を採らない。
- 常設の message surface は原則として window 最下部へ集約する。

1. footer の global summary
2. footer 直上の dedicated messaging region

- dedicated messaging region は補助線や区切りを伴う専用領域とし、Main / Margins / Watch の message をここで受ける。
- dedicated messaging region は 1 行前提とし、warning と blocking を同時常設しない。
- dialog は各 dialog 内の短命な notice を持ち得るが、window 常設 surface を追加する発想では扱わない。
- field-by-field annotation は例外扱いとし、fixed notice では意味が伝わらない箇所に限る。

### 1. global summary に出すもの

- 画面全体の現在相として利用者が把握すべき結果だけを出す。
- 以下の英語例は現行実装由来の仮案であり、最終文面ではない。
- 例:
  - optimize failed
  - apply failed
  - watch started / stopped / failed
  - settings saved / load failed
- ここでは長い例外文や内部事情は出しすぎない。

### 2. local corrective error として出すもの

- 利用者がその場で入力や設定を直せるものは、発生元 surface 近傍へ出す。
- 以下の英語例は現行実装由来の仮案であり、対象が曖昧なものは実装時に言い換える前提とする。
- 例:
  - input is required
  - margin area unavailable
  - selected margin area is too small for margin text
  - margins must be non-negative
  - watch srcdir is required / invalid
  - watch interval must be positive
  - invalid background color
  - settings path is required
  - save path is required
- これらは footer 要約だけでは不十分だが、surface 内の至る所へ分散させず、まずは window 最下部の dedicated messaging region へ集約する方を優先する。
- Main / Margins のように空きが薄く、動的配置の影響が大きい面でも、この dedicated region なら固定しやすい。

### 3. blocking error 候補

- 利用者が先へ進めず、その場で必ず認知してほしいものは blocking error 候補として別扱いする。
- 例:
  - apply 実行時の plugin 未解決
  - save / settings load-save の致命的失敗
  - watch start / tick の継続不能エラー
- ただし現時点では modal dialog を必須化せず、まずは dedicated messaging region の 1 行強調表示 + global summary の組み合わせで十分かを観察する。
- warning と blocking が競合する場合は、一般則として blocking を優先する。

### 4. internal-only に寄せるもの

- 利用者が直せないもの、または runtime fallback / partial GTK 環境の内部都合は、そのまま利用者向け error にしない。
- 例:
  - handler not connected
  - dialog closed / cancel ignored
  - save path ignored (closed)
  - watch stop ignored (idle)
  - backend load / presentation の部分失敗で non-fatal に継続するもの
- これらは debug log や開発向け trace に残せば足り、常設 UI で強く訴えない方がよい。

### 5. dialog ごとの見立て

- dialog 系は局所化を原則とし、直上または親 dialog 内の短命 notice で完結できるものは window 最下部へ返さない。
- dialog から window への往復は、dialog を閉じた後も全体状態として保持すべき結果や、dialog 単体で閉じない blocking 候補に限る。
- dialog 内 notice は dialog 最下部の専用エリアを予約し、補助線を含めて main window 側の messaging region と同系統で扱う。
- error のまま dialog を閉じた場合は、該当変更を反映せず、dialog を開く前の状態へ戻す。

- Save path dialog:
  - 必須 path 不足や save failure は、まず dialog 内短命 notice で出す価値がある。
  - cancel / closed ignored 系は出しすぎない。
- Settings dialog:
  - path required、load failed、save failed は、まず dialog 内短命 notice で閉じる方が自然である。
  - opened / closed の通知は global summary では弱くてよい。
- Color dialog:
  - invalid background color は dialog 内短命 notice が必要である。
  - confirmed / canceled 自体は error ではない。
- About dialog:
  - 原則として error 設計の中心には置かない。
- Watch srcdir dialog:
  - srcdir invalid や開始条件不足は、window へ返すより watch 側の開始制約で未然防止する方が自然である。

### 6. Main / Margins / Watch の優先観察点

- Main:
  - input required
  - optimize failed
  - apply failed / unknown plugin / no optimized file
- Margins:
  - unavailable / too small / invalid signal / invalid mode-position-lines
- Watch:
  - srcdir required / invalid
  - interval invalid
  - start failed / tick failed / apply failed
- この 3 面は発生頻度と修正必要性が高く、2nd planning の error design の中心に置く。

## error design 素案

### dedicated messaging region の仮仕様

- window 最下部に固定する。
- 補助線を挟んで footer と視覚的に分離する。
- 高さは 1 行前提とし、複数 message の同時常設を許さない。
- warning / corrective error と blocking 候補は排他表示にし、その時点で優先度の高い 1 件だけを出す。
- warning と blocking が競合する場合は blocking を優先する。
- phase 名は基本的に出さず、message 自体で意味が通る文面を優先する。
- 長い説明は置かず、「何を直すべきか」が分かる短文へ寄せる。
- `()` の補足情報は、主文より配色や視認性を落として抑制表示するか、必要なら detail 表示へ退避する。
- `()` の補足情報は、2nd planning 時点では常時表示を前提にする。
- 何を間違えたかの core 情報は log と同様に利用者へ伝える必要があるため、詳細を隠しても理由自体は失わない。
- 詳細や内部事情は log 側へ逃がすが、利用者が修正に必要な情報までは削らない。
- 補足情報の見せ方の最終判断は、実装してみてから調整してよい。

- 以下の table にある `代表 error` は、現行実装から拾った観察用の仮案である。
- 実際の表示文面は、この table の英語句をそのまま使うのではなく、対象や不足点が分かる文へ見直す。

### Main

| 種別 | 代表 error | 出し方の素案 |
| --- | --- | --- |
| global summary | optimize failed / apply failed / save failed | footer には短い結果要約だけ出す |
| local corrective | input is required / no optimized file to apply / save path is required | window 最下部の dedicated messaging region に集約して出す |
| blocking 候補 | unknown plugin / failed to apply wallpaper | footer 要約 + dedicated messaging region の強い error 表示。modal は保留 |
| internal-only | flow step blocked の詳細 trace / closed ignored 系 | log に残し、常設 UI では強く出さない |

読み:

- Main は操作密度が高いため、footer へ全件集約するより dedicated messaging region へ戻す方が自然である。
- widget 間の狭い空きへ直接 message を差し込む案は、resize 時のはみ出しや再配置コストが高いため採らない。
- `optimize failed` や `apply failed` は全体結果として出す価値があるが、例外全文を footer へ垂れ流さない。

### Margins

| 種別 | 代表 error | 出し方の素案 |
| --- | --- | --- |
| global summary | margins unavailable / margin text rejected | 原則 footer 主体にしない。必要時だけ短い要約 |
| local corrective | margin area unavailable / selected area too small / margins must be non-negative / max lines must be positive | window 最下部の dedicated messaging region に集約して出す |
| blocking 候補 | invalid margin signal / unknown margin widget | 利用者向けには弱く、開発向け寄り。現時点では blocking 扱いしない |
| internal-only | rejected / updated の細かい runtime feedback | log や debug 情報へ寄せる |

読み:

- Margins は発生箇所が明確だが、tab 内の余白は広くないため、field 直下の常設 annotation よりも、tab 上部または下部の shared notice の方が現実的な可能性が高い。
- Margins は発生箇所が明確だが、tab 内の余白は広くないため、field 直下の常設 annotation よりも dedicated messaging region の方が現実的な可能性が高い。
- `invalid signal` や `unknown widget` は利用者が直しにくく、Phase10 では internal-only 寄りに倒してよい。

### Watch

| 種別 | 代表 error | 出し方の素案 |
| --- | --- | --- |
| global summary | watch started / stopped / watch failed | footer で watch 全体の現在相を短く示す |
| local corrective | watch srcdir is required / watch srcdir invalid / watch interval must be positive | window 最下部の dedicated messaging region に集約して出す |
| blocking 候補 | watch start apply failed / watch tick apply failed / unknown plugin | dedicated messaging region の強い error と footer 要約を併用する |
| internal-only | watch stop ignored (idle) / apply cycle の細かい途中ログ | log に寄せ、通常 UI には出しすぎない |

読み:

- Watch は専用 tab を持つため、watch 固有 error は watch surface で完結する設計を優先する。
- start / tick failure は停止や継続不能に直結するので、watch の中では blocking 候補として扱う価値がある。

### Dialog 群

| Dialog | 出す価値が高い error | 弱くてよい / internal-only |
| --- | --- | --- |
| Save path | save path is required / save failed | closed ignored / cancel ignored |
| Settings | settings path is required / settings load failed / settings save failed | opened / closed 通知 |
| Color | invalid background color | confirmed / canceled |
| Watch srcdir | srcdir invalid / side missing | canceled / destroyed |
| About | 原則なし | opened / closed |

読み:

- dialog は「開いた・閉じた」より「何を直すべきか」があるときだけ強く出す。
- dialog 内で直せるものは dialog 内短命 notice で閉じ、window 最下部との往復は避ける。
- cancel 系は error ではなく、通常時の静けさを優先して目立たせない方がよい。

### provisional rule

1. footer は結果要約に限定し、修正指示の主戦場にしない。
2. corrective error は発生元 surface に紐づけつつ、window 最下部の dedicated messaging region へ集約する。
3. internal-only error は UI を汚さず log へ逃がす。
4. blocking 候補は modal を前提にせず、まず dedicated messaging region の strong error + footer 要約で成立するかを見る。warning と競合した場合は blocking を優先する。
5. Main / Margins のように resize 影響が強い面でも、message 面は増やさず dedicated messaging region を優先候補にする。
6. message で受ける前に UI 制約で潰せるものは、極力 UI 制約で潰す。
7. dedicated messaging region に残すのは、やむを得ず発生しうるもの、または CUI 等でも保険的に残す価値があるものを優先する。
8. dialog 内で完結できる corrective error は dialog 内短命 notice を第一候補とし、window 最下部との往復は避ける。
9. 13 は Optimize を無効化して未然防止する。
10. 22 は `SrcdirL` と `SrcdirR` が有効な値を持ち、かつ interval が 0 より大きい場合にのみ開始可能とする暫定仕様で扱う。
11. dialog を error のまま閉じた場合は変更を反映せず、dialog を開く前の状態へ戻す。

## message 面の候補列挙

### Main の候補

1. Main 専用の常設 notice row は増やさない。
2. Optimize / Apply の corrective error は dedicated messaging region へ返す。
3. Preview group の `preview_state_label` / `preview_source_label` / `preview_assist_label` は結果説明に寄せ、error 主面にはしない。
4. input row 直下の field-by-field annotation は、Main の密度と resize 耐性を考えると優先しない。

読み:

- [src/harite/gui/adapters/gtk_tab_builders.py](src/harite/gui/adapters/gtk_tab_builders.py) の `build_action_cluster_section()` は Optimize / Apply / Preview を一塊で持つが、ここへ別の常設 notice 面を増やすより、window 最下部の dedicated messaging region へ返す方が整合的である。
- Preview 側の既存 label は、結果説明や補助説明には使いやすいが、操作修正の主戦場にすると意味が混ざりやすい。

### Margins の候補

1. Margins 専用の常設 notice row は第一候補にしない。
2. `center_stack` 前段の notice は予備候補に留める。
3. `margin_text_tabs` の前後に page 共通の notice 領域を置く案も予備候補に留める。
4. field 直下の annotation は、余白と resize 耐性が確認できた箇所に限る。

読み:

- [src/harite/gui/adapters/gtk_tab_builders.py](src/harite/gui/adapters/gtk_tab_builders.py) の `build_margins_tab_section()` は `margins_layout_col` と `center_stack` を持つが、Margins 内に常設 notice を増やすより、dedicated messaging region を主面にした方が散逸しにくい。
- margin text page 内の `TextView` 周辺は一見空いて見えても、高さ変動や wrap の影響を受けるため、常設 error 領域の第一候補にはしない。

### Watch の候補

1. watch tab 冒頭 notice は予備候補に留める。
2. srcdir / interval / control の corrective error は dedicated messaging region へ集約する。
3. watch started / stopped / failed の全体結果は footer 要約を主とする。

読み:

- Watch は専用 tab で summary 群を最初から持つため tab 内 notice も置きやすいが、2nd planning では message surface を増やさない方を優先する。

### Footer の候補

1. `status_label` は global status の要約を常時持つ。
2. `error_label` は常設の長文 error 置き場ではなく、blocking 候補の短い全体要約だけに限定する。
3. watch summary は watch 固有詳細ではなく、全体状態の補助だけに残す。

読み:

- [src/harite/gui/adapters/gtk_layout_builders.py](src/harite/gui/adapters/gtk_layout_builders.py) の `build_footer_section()` は row が薄く、ここへ detail を積む前提ではない。

### dialog の候補

1. Settings / Color / Save path は dialog 内の冒頭または適用ボタン近くに短い notice row を持つ方を第一候補にする。
2. dialog 内で修正可能なものは dialog 内短命 notice で閉じ、window 最下部へ返さない。
3. cancel / closed ignored 系は dialog 内 notice へ出さず、静かに閉じる方を優先する。
4. About は notice 面を持たない前提でよい。

### 現時点の優先順位

1. Footer はそのまま global summary 専用に保つ。
2. window 最下部の dedicated messaging region を corrective / blocking の第一候補にする。
3. Main / Margins / Watch の常設 notice row は原則として増やさない。
4. dialog 内で直せるものは dialog 内短命 notice を第一候補にし、window との往復は避ける。
5. field 直下 annotation は、個別面で余白が確認できた箇所に限る。

## 初動タスク

1. footer / status / error の current 文言と状態段階を棚卸しする。
2. Main / Margins / Watch の message が、いまどこへ出ているかを surface ごとに棚卸しする。
3. preview / result / margins / watch で、色や強調に加えて局所 annotation が必要な箇所を短く列挙する。
4. Main / dialog / watch ごとに、利用者へ出すべき error と internal-only に留める error を分ける。
5. icon library の採否や比較は 3rd planning で扱う前提を維持する。

## 完了条件

- visual aid を入れる対象面が footer / preview / margins / settings などの単位で説明可能になっている。
- text / color / emphasis の優先順位が整理されている。
- icon library 論点を 3rd planning へ送る境界が整理されている。
- messaging の global / local の役割分担が説明可能になっている。
- error の発生面と、利用者へ出すべきもの / internal-only に留めるものの境界が説明可能になっている。
- Phase10 の visual rule を決めるための次の観察対象が列挙されている。

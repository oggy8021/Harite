# GUI Phase 6 レイアウト再定義メモ

最終更新: 2026-04-16

## 目的

- glade 由来の行構成を、現 GUI の責務に照らしてどこまで維持し、どこから再定義するかを決める。
- T6-3 の下部コントロール責務表を、実際の画面 zone 配置へ落とし込む。
- T6-5 の glade / adapter 判断に先立ち、「layout の意味として残す構造」と「glade 実体を消しても docs に残す構造」を分離する。

## この文書の位置づけ

- 本書は Phase6 の最終レイアウト決定書ではなく、判断前に読むための zone たたき台である。
- `第一候補` や `暫定結論` は採択済み案を意味しない。
- 目的は、glade 再現と現責務整理の間で、どの粒度に論点があるかを先に可視化することにある。

## 一次参照

- [docs/legacy-ui/wallpositapplet.glade](docs/legacy-ui/wallpositapplet.glade)
- [docs/specs/gui/gui-glade-layout-reconstruction.md](docs/specs/gui/gui-glade-layout-reconstruction.md) 旧 Glade レイアウト再構成の履歴資料
- [docs/specs/gui/gui-phase6-lower-controls-responsibility.md](docs/specs/gui/gui-phase6-lower-controls-responsibility.md)
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py)
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py)

## glade の骨格と現 GUI の差

### glade 側の骨格

- 上マージン行
- 中央本体
- 下マージン行
- 下部アクションバー
- statusbar

これは「1 本の MainWindow に、配置調整・保存・適用・watch を高密度に詰める」構成だった。

### 現 GUI 側の骨格

- Hero 入力部
- Optimize セクション
- Apply セクション
- Status セクション
- fallback のみ command bar を別途保持

これは「Compose -> Optimize -> Apply」の現代化フローを前面に出す構成で、glade の 1 行 command bar をすでに崩している。

## 再定義の前提

- Phase6 では glade の行数やボタン順をそのまま再現することを目的にしない。
- owner 判断により、legacy glade 実体は repo に保険的に残さない前提で読む。
- owner 判断では、画面全体の性格は「Studio」より「Commander」や gamepad 的な操作感に近いものとして読む。
- ただし glade の大枠で有効だったものは残す。
  - 上下左右マージンと中央操作の分離
  - watch 系が apply 系と別責務であること
  - 状態表示を末尾に集めること
- T6-3 の結果に従い、下部 command bar は「何でも置く帯」から外す。

## zone 再定義

### Zone 1. Header / Flow

役割:

- 画面の主目的を示す
- 現在の基本フローを示す

配置対象:

- title
- subtitle
- flow legend

判断:

- glade には強い header zone はなかったが、現 GUI の `Compose -> Optimize -> Apply` は維持価値が高い。
- Phase6 でも header zone は維持する。
- この zone は単なる見出しではなく、現在どの段階にいるか、次に何をすべきかを示す進行ガイドとして扱う。
- 十字配置まわりの下に散っている進行状態メッセージのうち、フロー要約に属するものはここへ吸収する。
- owner 判断では、watch でもマージンや既定設定を引きずるため、Header / Flow は watch 専用ではなく app 全体で共通に見る読みでよい。

### Zone 2. Compose / Input

役割:

- 左右入力、取得、クリア、配置トグル、fixed、マージンをまとめる

配置対象:

- `entPathL/R`
- `btnGetImgL/R`
- `btnClrPathL/R`
- `tglUpper*`, `tglLower*`, `tglPushLeft*`, `tglPushRight*`
- `radFixed`, `radNoFixed`
- top/left/right/bottom margins

判断:

- ここは glade の中央本体を最も強く継承する zone である。
- Phase6 でも「十字配置 + マージン列」の意味は維持する。
- ただし見た目の 1:1 再現ではなく、入力責務が一目で分かることを優先する。

### Zone 3. Optimize

役割:

- 保存先選択と optimize 実行を扱う

配置対象:

- save target 表示
- `Optimize`
- optimize result

判断:

- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py#L296) の `Save` は保存実行ではなく保存先選択の前段である。
- owner 判断では、`Save` は `Optimize` / `Apply` と同列の主操作としては置かない。
- `Save` は使用頻度が薄いが残す価値はあり、Flow / Header の右端など、標準的な保存配置へ分けて置く読みでよい。
- 現時点の英語ラベルは `Save As` を採る。
- T6-3 の判断どおり、`Save Confirm` / `Save Cancel` は常設配置しない。
- dialog 内部操作として吸収する。
- owner 判断では、Zone 3 / Zone 4 は Phase7 以降の preview window と並ぶ可能性を見越して考える必要がある。
- main tab 全体を上下左右の 2x2、計 4 マスで見るなら、Optimize / Apply は右下にあるのが操作しやすいという読みを採る。
- したがって Zone 3 は `Apply` と近接する前提で右下へ寄せる。

### Zone 4. Apply

役割:

- optimize 済み結果に対する適用判断を扱う

配置対象:

- saved files / latest target
- `Apply`
- apply target

判断:

- owner 判断により、`do-it` は不要である。
- glade の `btnSetWall` は「即時 apply」だったので、Phase6 ではその即時性へ戻す読みが自然である。
- ただし owner 認識では `Optimize` と `Apply` は本来かなり近い意味を持つ。
- owner 判断では、`Optimize` と `Apply` は隣り合わせでよい。
- owner 判断では、右利きマウス前提なら main tab の右下に Zone 3 / Zone 4 系の主操作がある方が楽である。
- したがって Decision 3 では、Optimize / Apply の距離感だけでなく、main tab 右下への配置を前提条件として読む。

### Zone 5. Watch

役割:

- source dir、interval、start/stop、watch 状態を扱う

配置対象:

- `Srcdir-L`, `Srcdir-R`
- interval
- `Watch Start`, `Watch Stop`
- watch sources / current

判断:

- T6-3 の時点で、下部コントロール帯に残す理由が最も強いのは watch 系だった。
- ただし Phase6 では「watch 専用 zone」として独立させる方が責務が明瞭である。
- command bar に残す案もあり得るが、`Prefs` や `Color` と同居させないことを優先する。
- さらに、通常操作 panel と Watch panel をタブ切替にし、watch controls をそちらへ寄せる案も成立する。
- watch は壁紙チェンジャーとして通常の compose / optimize / apply と利用文脈がかなり異なるため、タブ分離は「邪魔にならない」整理として筋が通る。
- ただしその場合でも、watch の要約状態は Status / Logs に残し、現在動作中かどうかが main 側から見えなくならないようにする必要がある。
- owner 判断では、watch 稼働中の要約状態は main tab 側にも何らかの形で見せる方がよい。
- owner 判断では、その要約粒度は `running / stopped` 程度でよい。
- watch `running` 中でも `Apply` は可能だが、その後の watch 周期で壁紙が切り替わるなら、手動 apply が上書きされること自体は許容する。
- その場合は、必要に応じて watch tab 側へ切り替えて停止や詳細確認を行う読みでよい。
- 現時点では「独立 Watch zone」が最も読みやすいが、タブ分離案は十分実現可能な対案として扱う。

### Zone 6. Secondary / Meta

役割:

- コアフローに直接関与しない補助導線をまとめる

配置対象:

- `About`
- `Help`
- `Prefs` を残すならここ

判断:

- `About` / `Help` は secondary 扱いを維持する。
- owner 判断では、この zone は「余ったところ」「邪魔にならないところ」でよい。
- `Prefs` もこの zone に置く前提でよい。
- `Color` はこの zone にも置かず、Phase7 候補として退避する。

### Zone 7. Status / Logs

役割:

- status, error, save target, watch state, logs を集約する

配置対象:

- status message
- last error
- save target
- watch sources / current
- logs

判断:

- glade の statusbar を、現 GUI では複数行の status zone として拡張した理解でよい。
- この拡張は責務上も妥当なので維持する。
- Header / Flow に上げない詳細状態、実行ログ、watch current/source、直近エラーはこの zone に集約する。
- したがって、いま十字配置まわりの下に見えているメッセージ類は、「進行ガイド」と「詳細状態/ログ」に分けて再配置する前提で読む。
- owner 判断では、この zone の読みで問題ない。
- main 側に残す watch 要約は `running / stopped` の最小表示でよい。

## 再配置方針

### 維持する構造

- Compose / Input が画面の中核であること
- Optimize と Apply を分けること
- Optimize と Apply を右下で近接配置すること
- 状態表示を専用 zone に寄せること
- main tab を 2x2 で見たとき、主操作が右下に寄ること

### 崩す構造

- glade の「何でも下部 1 行バーへ置く」構造
- save path chooser 内部操作を恒常ボタンとして見せる構造
- `Prefs` / `Color` / `Apply` を同列の補助ボタンとして並べる構造

### 参照のみ維持する構造

- glade の hbox14 の順番そのもの
- `btnSetting` と `SettingDialog` の存在だけを根拠にした `Prefs` 常設
- `btnSetColor` をコア導線に含めること

補足:

- ここでいう「参照のみ維持」は、glade 実ファイルを repo に残す意味ではない。
- 必要な意味は [docs/specs/gui/gui-glade-layout-reconstruction.md](docs/specs/gui/gui-glade-layout-reconstruction.md) のような履歴再記述 docs 側へ吸収する前提である。

## zone 案

### 案A: Watch 独立 zone

構成:

- Header
- Compose
- Optimize
- Apply
- Watch
- Secondary
- Status

評価:

- 責務分離が最も明瞭
- `Prefs` を切っても watch 導線が失われない
- `Prefs` を Secondary / Meta の余り領域へ置く読みとも両立しやすい
- 現時点の第一候補

### 案B: Watch を command bar として残す

構成:

- Header
- Compose
- Optimize
- Apply
- Watch command bar
- Status

評価:

- glade の下部帯に近い見た目を残しやすい
- ただし command bar の意味が watch 専用へ変わるため、旧 hbox14 再現とは別物になる

### 案C: Watch を別タブへ分離

構成:

- Main tab
  - Header
  - Compose
  - Optimize
  - Apply
  - Secondary
  - Status
- Watch tab
  - watch controls
  - watch status

評価:

- 通常操作と壁紙チェンジャー操作の利用文脈を最も明確に分離できる
- watch controls が main 操作面の邪魔になりにくい
- 「通常の壁紙作成」と「継続切替」は別機能だという owner 認識と相性がよい
- 一方で watch 状態が main tab から消えすぎると不便なので、要約状態は main 側にも残す必要がある
- main 側に残す watch 要約は `running / stopped` の最小表示でよい
- owner 判断では、Header / Flow は tab ごとに分けず、app 全体で共通に見る読みでよい
- owner 反応としても、単なる思いつきではなく検討価値のある案として読むことができる

## owner 判断の要約

- Zone 1 は app 全体共通の Header / Flow として扱う。
- Zone 2 は Compose / Input の中核を維持する。
- `Save` は Flow / Header の右端など、標準的な保存位置へ独立で置く。
- `Save` の英語ラベルは `Save As` とする。
- Zone 3 / Zone 4 は preview window との将来整合を見越しつつ、main tab の右下へ寄せ、`Optimize` と `Apply` は隣接させる。
- Zone 5 は独立 zone より、watch 専用 tab へ分離する案が有力である。
- Zone 6 は「余ったところ」「邪魔にならないところ」でよく、`Prefs` もそこへ置く。
- Zone 7 は現行の Status / Logs 読みでよい。
- watch 稼働要約は main 側に `running / stopped` のみ残し、詳細は watch tab 側で扱う。
- アイコン表現そのものは Phase6 ほぼ最後に扱う。
- 画面の操作感は Studio 的な制作画面より、Commander / gamepad 的な操作面として読む。

## 現時点のたたき台

- owner 判断を反映すると、main tab 側は 7 zone の考え方を維持しつつ、watch は別 tab へ分ける読みが最も自然になってきた。
- owner 判断を反映すると、`Save` は標準的な保存位置へ独立で置き、main tab 側は `Optimize` / `Apply` を右下へ寄せて近接配置し、watch は別 tab へ分ける読みが最も自然になってきた。
- つまり、glade の 5 段構成をそのまま復元するより、責務単位の zone 再定義と watch tab 分離を組み合わせる方が筋が通って見える。
- glade から強く継承する対象は Compose zone の構造と status 集約の考え方であり、下部 1 行バーそのものではない、という読み筋が有力である。
- owner 判断ベースでは、Zone 7 はこのままでよく、Zone 6 は「邪魔にならない余り領域」として扱い、`Prefs` もそこへ置く読みでよい。
- watch を「通常操作と全く使う機会が異なる壁紙チェンジャー」とみなすなら、案C のタブ分離は有力対案ではなく、現時点の第一候補に近い。
- さらに main tab の操作感としては、上下左右 2x2 のうち右下に Optimize / Apply 系主操作を置き、`Save` は別の標準位置へ置く読みが有力である。

## T6-5 への引き継ぎ

1. glade は Compose zone の意味解釈には有効だが、command bar の最終形を拘束する正本ではない。
2. fallback backend が command bar を大量に抱えているのは Phase5 暫定事情であり、構造正当化には使わない。
3. adapter / backend を残す場合も、最終構成は「Main に 7 zone を置く案」または「Watch を別 tab へ分ける案」のどちらかを前提に見直す。

## 次アクション

1. 本ファイルを T6-4 の初版として固定する。
2. T6-5 で glade / adapter / fallback backend の責務をこの zone 構成に照らして再判定する。
3. アイコン表現の最終整理は Phase6 後半で、既存 docs の記述も参照しつつ行う。
4. 文言の多言語化は i18n 企画時に扱い、Phase6 では英語ラベル `Save As` を前提に読む。

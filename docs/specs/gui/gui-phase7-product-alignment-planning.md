# GUI Phase 7 計画（プロダクト整合性の再設計フェーズ）

最終更新: 2026-04-19

## 位置づけ

- 本書は Phase6 の成果物として作成する、次フェーズ準備用の計画文書である。
- 2026-04-18 時点で、従来「Phase7 = 新機能フェーズ」としていた読みは改める。
- 新しい Phase7 は、GUI / CLI / core の機能差分と操作語彙を棚卸しし、プロダクトとしての整合性を再設計するフェーズとする。
- 新機能の実装フェーズは Phase8 へ後ろ倒しし、Phase7 で承認された項目だけを送る。
- したがって Phase7 は「実装追加の前に、何を揃え、何を意図差として残し、何を Phase8 候補とするかを決めるフェーズ」と読む。

## 目的

- CLI / GUI / core の機能差分を、偶発的な抜け漏れと意図的なチャネル差に分離する。
- `optimize` / `apply` / `dry-run` / `do-it` / `watch` の語彙と責務境界を再設計する。
- CLI に先行して存在する機能のうち、GUI にもたらすべきものと CLI 専用に残すものを分類する。
- GUI にだけ残る planned / deferred 項目について、プロダクト候補として維持するか、落とすか、Phase8 候補へ送るかを判断する。
- `Prefs` について、Phase6 で復旧した入口と値同期の土台を前提に、内容 grouping、初期値埋め込み、auto-detect の露出方針、main 画面との責務分担を整理する。
- Phase8 に送る新機能バックログを、整合性判断済みの状態で作る。

## 非目的

- Phase7 中に新機能をまとめて実装すること。
- GUI の全面 redesign を再度始めること。
- CLI / GUI の表面的なラベルだけを先に変えて、責務整理を後回しにすること。
- `do-it` の是非を感覚だけで決め、plugin apply や実機運用との関係を見ないこと。

## Phase6 から受け取る前提

- GUI current runtime は glade prototype 前提を外し、`Apply` を即時実行の正本へ戻している。
- save path chooser、watch tab 分離、adapter/runtime 名寄せなどの構造整理は Phase6 で進んだ。
- `Prefs` は Phase6 で必要部品として復旧し、最低限の可視化と config 同期の入口が戻っている。
- Phase6 の close 判定は、見た目とレイアウトの了承ライン到達を基準として受領済みである。
- デスクトップ貼り付け結果から見えた `Apply` 結果の疑義は、Phase6 の見た目未達ではなく、Phase7 で扱う product alignment 上の整合性論点として引き継ぐ。
- 確認済みの具体例として、XFCE 2 画面（2048x1280 x 2、連続 4096x1280）での `Default` 適用には、少なくとも次の観測がある。
  - `700x1244.jpg` と `700x394.jpg` から作った 4096x1280 の optimize 結果を `Default` で適用すると、各 2048x1280 画面へ同一ワイド画像を当てに行くような圧縮表示に見える。
  - 同じ画像を XFCE で手動選択し、日本語 UI 上の「縦横比を維持せず全画面化」として表示した場合も、見た目は同様だった。
  - GUI の `Apply(default)` を実機で観測したところ、plugin を通じた `xfconf-query` は primary monitor 側へ 1 回だけ効いたように見え、左画面だけ画像が変わった。
  - 以上から、これは単純な内部不整合というより、plugin 実装部が持つ通常 apply 経路の意味と GUI の `Default` 語彙の整合問題である可能性が高い。
  - とくに最後の観測は、`Default` が multi-monitor aware な割当ではなく、single-file の通常 apply 経路として読まれるべきことを補強している。
  - ただし XFCE は style の選択肢が多く、single-file だけでなく `Auto-split` 後の各 monitor 画像の見え方にも影響し得るため、desktop 上の見え方だけで `optimize` / `split` の良否を即断しない。
  - 少なくとも Phase7 の検証では、まず生成された JPG（合成結果と split 結果）を正本として確認し、その後に desktop 表示を参考観測として扱う。
- CLI 側には `apply --do-it` と `watch --dry-run/--do-it` が残っている。
- core / CLI には margin 情報埋め込みや monitor split など、GUI 未露出の機能が既に存在する。
- watch は CLI が loop / apply / failure-continue を持ち、GUI 側も Phase7 で timer event 駆動の front-end として接続が進んでいる。

## 一次参照

- [docs/specs/gui/gui-phase6-planning.md](docs/specs/gui/gui-phase6-planning.md)
- [docs/specs/gui/gui-phase6-baseline-recheck.md](docs/specs/gui/gui-phase6-baseline-recheck.md)
- [docs/specs/gui/gui-phase6-cli-reference-check.md](docs/specs/gui/gui-phase6-cli-reference-check.md)
- [docs/specs/core/margin-info-embedding.md](docs/specs/core/margin-info-embedding.md)
- [docs/specs/core/monitor-split-design.md](docs/specs/core/monitor-split-design.md)
- [docs/specs/watch/harite-watch-minimum-spec.md](docs/specs/watch/harite-watch-minimum-spec.md)
- [docs/manual-validation-gate.md](docs/manual-validation-gate.md)
- [docs/meta/do-it.md](docs/meta/do-it.md)
- [src/harite/cli.py](src/harite/cli.py)
- [src/harite/core.py](src/harite/core.py)
- [src/harite/plugins.py](src/harite/plugins.py)

## Workstream

### 1. 機能棚卸し

- 対象:
  - core にあり CLI / GUI の両方へ露出し得るもの
  - CLI にあり GUI に未露出のもの
  - GUI にだけ残る planned / deferred / provisional なもの
- 主要論点:
  - 何が単なる未着手か
  - 何がチャネル差として意図的か
  - 何が名前だけ残って意味が変質したか
- 成果物:
  - 機能棚卸し表
  - 抜け漏れ一覧

### 2. 操作語彙の再設計

- 2026-04-19 時点では、本書で最も整理が進んでいるのはこの workstream であり、主要論点の棚卸しと暫定方針づけはおおよそ一巡した。

- 対象:
  - `optimize`
  - `apply`
  - `dry-run`
  - `do-it`
  - Save As / watch / per-monitor apply の周辺語彙
- 主要論点:
  - `apply` は CLI / GUI で同義であるべきか
  - CLI 既定を dry-run のまま残すのか
  - `--do-it` の名称と概念を維持するか、改名するか、廃するか
  - `optimize` と `apply` の責務分離は残すか、入口体験だけ整理するか
  - `--left-file` / `--right-file` による explicit mapping を、CLI 専用の低露出な escape hatch として残すか、さらに目立たない傍流へ下げるか
  - CLI では `-r` に実画面より小さい解像度を意図的に与え、アスペクト比や画角を優先した生成物を後段 `apply` で monitor 別に振り分ける使い方をどう位置づけるか
  - デスクトップ貼り付け結果で疑義の出た組み合わせを、語彙差の問題として扱うのか、実処理整合性の問題として扱うのか
  - 4096x1280 の optimize 結果に対して `Default` を選んだとき、それは「plugin 実装部の通常 apply 経路へ 1 枚の最終成果物をそのまま渡す」意味なのか、「現在の画面構成に応じて暗黙分割される」期待を伴っていたのか
  - `Auto-split` は、単なる表示 mode 名なのか、それとも「合成済み 1 ファイルから monitor 名付きの `left-file` / `right-file` 相当を内部生成して適用する」機能名として十分に読めるのか
  - XFCE 手動設定の「縦横比を維持せず全画面化」と一致する現象を、GUI 側でどう説明し、どこまで mode 名や補助文言で予防するか
  - `Default` という語が、user default / OS default / plugin default のどれを指すのか曖昧になっていないか
  - XFCE の style が single-file / auto-split の両方の見え方へ影響し得る前提で、何を生成物の正本とし、何を desktop 依存の参考観測とするか
- 成果物:
  - 操作語彙ポリシーメモ
  - CLI / GUI の命名ルール案

### 3. watch の責務再定義

- 2026-04-19 時点では、CLI watch と GUI watch の責務差の整理、timer event 接続、single-source / dual-source apply、生成物 cleanup 方針、出力先表示まで揃っており、Workstream 3 は close 前の文言整理と manual validation を残す段階に入っている。

- 対象:
  - CLI `watch`
  - GUI watch tab / srcdir / interval / start-stop
  - plugin apply と継続切替の責務境界
- 主要論点:
  - GUI watch は CLI watch の front-end として扱うか
  - GUI が独自 orchestration を持つ理由があるか
  - watch の実切替を `Apply` 責務の延長として扱うか
  - failure-continue policy を GUI へ持ち込むか
- 成果物:
  - watch responsibility memo
  - GUI watch の縮退 / 接続 / Phase8 候補の判断表

### 4. GUI 候補機能の再読

- 対象:
  - `Prefs` content / grouping / auto-detect exposure
  - margin info embedding / `embed-text`
  - monitor split / per-monitor apply
  - preview / visual assist 候補
  - `Color` など GUI 側 deferred 項目
- 主要論点:
  - `Prefs` のどの項目を main 画面へ残し、どれを設定ダイアログへ寄せるか
  - 既存の値同期・事前埋め込み・auto-detect を、どの粒度で可視化するか
  - `Apply` 結果の疑義が、visible な選択肢の意味づけの問題か、内部処理組み合わせの問題か
  - `Default` / `Auto-split` の visible 2 択が、2 画面連結 optimize 結果に対して十分に誤読なく読めるか
  - `Default` の補助文言が「normal apply」だけで足りるのか、それとも plugin 実装部の通常 apply 経路であることや desktop 側表示モード依存を示すべきか
  - Phase6 で GUI に出さなかった explicit mapping を、今後も「ユーザ意識に上がりにくい CLI 専用の低露出機能」として扱うのか、それとも product 上の欠落とみなすのか
  - CLI 側にある「実画面ぴったりではなく、意図的に小さめ解像度で optimize した生成物を apply 側で使う」発想を GUI に持ち込む必要があるのか
  - GUI に持ち込むと意味が増える機能か
  - CLI 専用のままでもよい機能か
  - 既存 UI 構造へ自然に乗るか
  - Phase8 へ送る価値があるか
- 成果物:
  - GUI 候補機能リスト
  - Phase8 候補バックログの素案

### Workstream 4 の進め方メモ

- `feature/phase7-gui-candidate-recheck` では、実装に先立って docs 先行で論点整理を進める。
- 進め方の単位は、内部実装単位ではなく、GUI 上で user が触る入口や機能群を基準とする。
- したがって Workstream 4 では、まず「どのボタンや設定項目が main 画面に残るべきか」「どれが settings dialog へ寄るべきか」「どれが CLI 専用または Phase8 候補か」を、入口単位で比較・判断する。

### Workstream 4 で先に立てる論点単位

- 第1優先: `Prefs` / settings dialog と main 画面の責務境界
- 第2優先: `Apply` 周辺の visible 語彙と補助文言
- 第3優先: `embed-text` / margin info embedding 系の GUI 露出方針
- 第4優先: preview / visual assist 候補
- 第5優先: `Color` など deferred 項目

- ここでいう「論点単位」は、個別 widget を 1 個ずつ孤立して論じることではなく、user から見て 1 つの操作意図として読まれる入口群をまとめて扱う単位を指す。
- ただし `Prefs` の中身を再読する際は、最終的に button / field 単位まで分解しても、判断の書式は揃えたまま維持する。

### 各論点で固定する比較観点

- current GUI 上の入口は何か。
- current GUI での責務は何か。
- 母体プログラムでは何が相当機能だったか、または相当機能が存在しなかったか。
- `Harite v0.1.2` ではどう露出していたか。
- current 実装やこれまでの改修で、何が揃い、何が意図差として残ったか。
- 実機確認や過去の不具合修正から見えている制約は何か。
- Phase7 の判断として、main に残す / settings へ寄せる / CLI 専用のまま残す / Phase8 候補へ送る / 落とす、のどれに置くか。

- これにより Workstream 4 の文書は、感覚的な UI 要望の列挙ではなく、比較可能な product alignment メモとして残す。

### 文書化の順序

- まず `Prefs` と main 画面の責務境界を整理する。
- 次に `Apply` 周辺の visible 語彙と補助文言を、Workstream 2 の結論と接続して再確認する。
- その後に `embed-text` / margin info embedding を、制作機能として GUI に持ち込む価値の観点から再読する。
- 続いて preview / visual assist を、Phase8 backlog 候補として扱うかを判断する。
- 最後に `Color` など deferred 項目を、維持 / 削除 / Phase8 候補のいずれへ置くか決める。

### このブランチで先に欲しい成果物

- Workstream 4 の比較観点を固定したメモ
- `Prefs` と main/settings 境界についての整理メモ
- GUI 候補機能リストの初版
- Phase8 候補へ送る項目の素案

### PR 区切りの想定

- 最初の区切りは、`Prefs` と main/settings 境界、および Workstream 4 の比較観点が文書として一巡した時点とする。
- その後、`embed-text` / preview / deferred 項目まで含めて候補機能リストが揃った時点で、必要なら別 PR または同ブランチ後半の区切りとして扱う。
- しばらくは docs-only の短枝を別に切らず、この feature branch の先頭で前段整理と feature 接続をまとめて扱う。

### `Prefs` と main/settings 境界の現時点整理

- current 実装の `Prefs` は、config / dataclass ベースで optimize・apply・watch の一部既定値を保存し、dialog から apply / load / save できる入口として成立している。
- 一方で main 画面や watch tab でその場の作業状態として保持している値のうち、`Prefs` にまだ入っていないものも多い。
- したがって Workstream 4 の第一論点は、「`Prefs` を何でも入る箱として広げる」ことではなく、「既定値として持つべきもの」と「今この作業だけの状態」を分け直すことにある。

### current 実装から読める事実

- `preferences.py` で保存対象になっているのは、optimize 系設定、plugin / apply mode、watch interval である。
- `MainWindow.on_apply_preferences()` / `export_preferences_config()` でも、実際に反映・往復しているのは resolution / layout / scaling / two-screen / margin 系 / embed 系 / plugin / apply mode / watch interval に限られる。
- 現時点では、少なくとも次の値は `Prefs` の保存対象に入っていない。
  - current input path L/R
  - `output_dir`
  - `save_path`
  - watch source dir L/R
  - watch current 表示や watch 実行状態
- このため current `Prefs` は「GUI / CLI 共有 config の入口」としては成立しているが、「起動のたびに選び直したくない値の全体」をまだ扱ってはいない。

### 母体比較と Phase6 からの継承知見

- Phase6 時点の整理では、`Prefs` は残す前提であり、CLI / GUI 間の config 共有入口として意味があると判断している。
- その整理では、watch source は元来 `Prefs` 側にあり、interval だけが main window 側に残っていたという読みを採っている。
- つまり `Prefs` は、単なる補助 dialog ではなく、「作業前提や既定値をまとめる入口」として読む方が、母体比較とこれまでの修正履歴の両方に整合しやすい。

### Phase7 の暫定境界案

- settings dialog に寄せるもの:
  - 起動をまたいで保持したい既定値
  - optimize の品質・構図・two-screen 既定
  - plugin / apply mode の既定
  - watch interval の既定値
  - 将来的には `output_dir` のような再入力コストの高い既定パス候補
- main 画面に残すもの:
  - その場の作業対象そのもの
  - input path L/R
  - watch source dir L/R
  - watch start / stop や current 状態表示
  - save 実行直前の保存先選択
  - `Apply` / `Optimize` の即時操作
- 二重性を許すもの:
  - watch interval
  - 理由: `Prefs` では既定値として保持したい一方、watch tab 上ではその作業回で即変更したい runtime parameter としても自然だからである。

### この時点での暫定判断

- `Prefs` は残す。
- ただし main 画面の操作を settings dialog へ吸い込み過ぎず、「既定値」と「今この作業の状態」を分ける方向で整理する。
- `output_dir` は current 実装では `Prefs` に入っていないが、起動ごとに再指定する負担が高いため、config 連動候補として Workstream 4 の主論点に含める。
- watch source dir L/R は、作業対象そのものとしては main / watch tab に残す方が自然だが、再起動後の利便性まで見るなら config 連動候補として再検討余地がある。
- `save_path` は作業ごとの確定先であり、既定値より直前選択の意味が強いため、現時点では `Prefs` に寄せない読みを優先する。

### 次に詰める問い

- `output_dir` を `Prefs` の正式保存対象へ上げるか。
- watch source dir L/R を「既定フォルダ」として持つか、それとも current task 専用値に留めるか。
- watch interval を main と `Prefs` の両方に持つ現在の二重性を、既定値と runtime override の関係として明文化するか。
- `Prefs` dialog の項目 grouping を optimize / apply / watch / path defaults の 4 群へ整理するか。

### `Apply` 周辺の visible 語彙メモ

- current GUI の main 画面では、apply mode の visible 2 択は `Default` / `Auto-split` であり、補助ラベルは `Default: normal apply` になっている。
- current `Prefs` dialog 側でも、apply mode は `Apply Default` / `Apply Auto-split` として露出している。
- したがって current runtime は内部実装では `single-file` / `per-monitor-auto-split` を持ちながら、visible 語彙ではなお `Default` を残している。

### current 実装から読めること

- main 画面の `Apply` は即時実行であり、`do-it` 切替は UI に持ち込んでいない。
- visible な `Default` は current 実装上 `single-file` と同義であり、2 画面文脈を見て暗黙分割する mode ではない。
- `Auto-split` は、追加処理として monitor 別 apply target を生成して apply する mode を指す。
- にもかかわらず、`Default` という語は user default / OS default / plugin default のいずれとも読めてしまい、`single-file` の意味を直接は示していない。
- 補助ラベル `normal apply` も、「通常」の基準が何かを user に渡しておらず、plugin 実装部の通常 apply 経路という意味を十分に固定できていない。

### 母体比較

- 母体プログラムでは `Apply` は即時変更の 1 動作であり、`Default` / `Auto-split` の mode 語彙自体が存在しなかった。
- したがって母体比較の観点では、current GUI の問題は「mode が多いこと」そのものより、「mode を追加した結果、`Default` が曖昧語になったこと」にある。

### Harite v0.1.2 比較

- `Harite v0.1.2` では GUI 側に `Default` 語彙はなく、`dry-run` / `do-it` が前面に出ていた。
- そのため曖昧語としての `Default` は現世代 GUI で生まれた問題であり、母体から受け継いだものでも、v0.1.2 からそのまま来たものでもない。
- current CLI は `single-file` / `per-monitor-explicit` / `per-monitor-auto-split` の 3 経路を保っているため、語彙の基準線は CLI / core 側の方がむしろ明確である。

### これまでの検証知見から見えること

- XFCE 実機観測では、`Default` 適用は monitor-aware な既定ではなく、single-file の通常 apply 経路として読む方が整合する。
- watch 接続でも、single-source は通常 apply、dual-source は auto-split apply として接続しており、current product の主導線はすでにこの二分で動いている。
- したがって `Apply` 周辺語彙で必要なのは、新しい概念を増やすことではなく、現に存在する 2 経路を誤読なく言い表すことである。

### Phase7 の暫定判断

- `Auto-split` は Harite 独自価値として主導線に置く。
- `Default` は最終的には残さない方向を優先し、`分割せず適用` 系の非曖昧語へ寄せる。
- ただし current 実装やテストには `Default` がまだ残っているため、現段階では「current visible label は `Default` だが、読むべき意味は `single-file`」と文書で先に固定する。
- 補助文言も `normal apply` のままでは弱く、少なくとも「追加分割なし」「1 ファイルをそのまま apply」「desktop 表示結果は plugin / OS style に依存し得る」のどれかを含む方向で再検討する。

### 現時点で自然な表示語候補

- main 画面候補:
  - `分割せず適用`
  - `自動分割して適用`
- 設定ダイアログ候補:
  - `適用: 分割なし`
  - `適用: Auto-split`
- 補助文言候補:
  - `追加分割なしで適用`
  - `1ファイルをそのまま適用`

- ここではまだ最終文言を fix しないが、少なくとも `Default` / `normal apply` をそのまま正本語彙として残す判断は採らない。

### 次に詰める問い

- main 画面では英語ラベルを維持するのか、日本語寄り説明へ寄せるのか。
- `Auto-split` は固有名として残すのか、`自動分割` へさらに言い換えるのか。
- main 画面の短いラベルと、補助ラベル / tooltip 相当の説明責務をどう分担するか。
- `Prefs` dialog の apply mode 表示を main 画面と完全一致させるか、設定項目として少しだけ技術的な語を残すか。

### `embed-text` / margin info embedding の再読メモ

- current core / CLI では、margin info embedding はすでに正本機能として成立している。
- 一方で current GUI では、state と `Prefs` 保存対象には入っているが、main 画面の主導線 widget としては立っていない。
- したがってこの論点は「未実装機能を新規導入するか」ではなく、「既存機能を GUI のどの深さまで露出するか」を判断する論点である。

### current 実装から読めること

- core 側には、余白領域にだけ情報を描く `embed_info` / `embed_text` / `embed_position` / `embed_max_lines` の処理がある。
- GUI state model と optimize controller も、この 4 項目を内部状態として保持し、optimize 実行へ渡せる。
- `Prefs` dialog にはこれらの entry / spin が存在し、保存・読込・適用の対象にもなっている。
- ただし main 画面側には、少なくとも current GTK runtime backend 上、これらを直接編集する専用 widget は見えていない。
- GUI test でも、`embed-text` は form_state や CLI preview 文字列で確認されており、user が main 画面で制作機能として使う導線まではまだ作られていない。

### core 仕様から読めること

- core spec の基本方針は、margin info embedding を「余白のみ」「デフォルト無効」「可読性優先」「壊れにくさ優先」の MVP として扱うことにある。
- `params` / `free` / `combo` の 3 系統は、装飾機能というより、生成物へ最小限の付加情報を残すための機能として読める。
- 絶対パスやユーザ名などの機微情報を出さない方針も明記されており、制作支援機能であっても無制限に情報を増やす方向は採っていない。

### 母体比較

- 母体プログラムには、少なくとも current product alignment の比較対象として、margin info embedding に相当する GUI 主導線は見えていない。
- したがってこの機能は「母体の責務を戻す」話ではなく、Harite で追加された optimize 拡張を GUI へどこまで持ち込むかの判断になる。

### Harite v0.1.2 比較

- `Harite v0.1.2` と current core / CLI の系譜では、embed 系は optimize オプションとして扱われている。
- ただし current GUI では、それが `Prefs` に入った一方で main 画面の主導線までは上がっておらず、現在は「内部にはあるが front では弱い」中間状態にある。

### これまでの整理と整合すること

- Workstream 4 の第1論点で整理した `Prefs` の役割は、「既定値を持つ入口」であって、「user が毎回触る制作操作をすべて押し込む箱」ではない。
- この観点から見ると、embed 系を `Prefs` に置けること自体は自然だが、それだけで GUI 主導線になったとは言えない。
- 逆に、現在の main 画面へ理由なく細かな embed controls を増やすと、Phase6 で落とした複雑さを戻す危険がある。

### Phase7 の暫定判断

- margin info embedding は、current Phase7 の main 主導線へ今すぐ昇格させるより、Phase8 候補として扱う方が自然である。
- ただし完全に後回しにするのではなく、「core / CLI では成立済み」「GUI では state / prefs までは接続済み」という現在地を先に明文化しておく価値がある。
- 現時点では、main 画面に常設の詳細 controls を増やすより、将来の制作支援機能群としてまとめて再設計する読みを優先する。
- そのため Phase7 では「主導線へ入れる」より、「Phase8 backlog に送る際の比較材料を揃える」ことを優先する。

### GUI に持ち込む場合の価値

- optimize 生成物に意図や条件を残せるため、制作機能としての意味が増す。
- `free` や `combo` は、壁紙を単なる貼付対象ではなく、軽い注記付き成果物として扱える入口になる。
- 一方で見せ方を誤ると、main 画面の目的が「最短で optimize / apply すること」から逸れやすい。

### 現時点で自然な扱い

- Phase7: `Prefs` と内部 state で保持可能な準備済み機能として扱う。
- Phase8 候補: preview / visual assist と合わせて、「制作支援」群として再設計する。
- GUI main 画面: 常設 controls の追加はまだ採らない。

### 次に詰める問い

- embed 系を将来 main 画面へ出すとき、常設 controls とするのか、詳細 dialog / advanced section に寄せるのか。
- `embed_info` の mode 語彙を、そのまま `none|params|free|combo` で見せるのか、user 向け表現へ言い換えるのか。
- preview / visual assist が弱い現状で、埋め込み機能だけを先に強く出しても user が結果を把握できるか。
- `Prefs` に残す「既定値」と、作業ごとに変えたい埋め込み内容をどう分けるか。

### preview / visual assist の再読メモ

- current GUI には、CLI 対応の見える化としての command preview はある。
- しかし、画像そのものの visual preview や配置確認用 assist は、current product ではまだ常設機能になっていない。
- したがってこの論点も、未実装の新機能をいきなり足す話というより、「どの種の確認支援を GUI 主導線へ持ち込むか」を整理する論点である。

### current 実装から読めること

- `MainWindow.build_optimize_cli_preview()` は存在し、current form state から `harite optimize ...` の preview 文字列を組み立ててログへ残せる。
- `last_saved_files` によって optimize 結果ファイル群は保持され、apply 対象候補として再利用できる。
- 一方で current GUI 実装には、専用の preview pane / preview window / preview service は見当たらない。
- current GTK runtime backend にも、画像サムネイルや配置矩形を見せる専用 widget は確認できない。
- したがって current GUI が持っているのは「CLI preview 文字列」と「生成後ファイルの保持」であり、「生成前後の見た目確認」はまだ弱い。

### 過去 docs との整合

- Phase5 系 docs では、中央プレビューは現状無しと整理済みであり、preview は後続タスクとして扱われていた。
- standalone design では PreviewPane や `preview_service.py` が構想されていたが、current 実装にはまだ接続されていない。
- したがって preview は「一度捨てた機能」ではなく、「早い段階から後続実装扱いだった候補」が未着手のまま残っている、という理解が自然である。

### 母体比較

- 母体比較で確定しているのは、少なくとも current product alignment の検証対象として、中央常設 preview は存在しないという点である。
- このため preview を追加する場合、それは母体忠実化ではなく、Harite 側の制作支援拡張として扱うべきである。

### 現在地の読み方

- current GUI は、最短で optimize / save / apply / watch へ進む front-end としては成立している。
- しかし制作支援の観点では、「どう出力されるか」「埋め込みがどう見えるか」「two-screen 合成がどう収まるか」を事前確認する導線が弱い。
- その弱さは、embed 系を main 画面へ上げるかどうかの判断にも影響している。

### Phase7 の暫定判断

- preview / visual assist は、Phase7 で主導線へ無理にねじ込むより、Phase8 候補として扱う方が自然である。
- ただし単なる wishlist にせず、current GUI がすでに持つ `CLI preview` と `last_saved_files` を基点に、どの確認支援が不足しているかを比較可能な形で残す。
- Phase7 では「画像 preview を実装する」より、「preview 不在がどの判断に影響しているか」を明文化することを優先する。

### Phase8 候補としての価値

- optimize 前に CLI 対応だけでなく見た目の予測も示せれば、two-screen / margins / embed 系の理解コストを下げられる。
- optimize 後の結果確認を GUI 内で行えれば、apply 前の確認導線が強くなる。
- watch や auto-split と組み合わせる将来を考えても、visual assist は単発機能ではなく GUI 制作支援の共通基盤になり得る。

### 現時点で自然な扱い

- Phase7: `CLI preview` を現行の最低限の可視化として扱う。
- Phase8 候補: 画像 preview、配置要約、埋め込み結果確認を含む visual assist 群として再設計する。
- main 画面: 現段階では preview 不在を前提に、controls の追加判断を過剰に進めない。

### 次に詰める問い

- Phase8 で最初に必要なのは、生成前 preview か、生成後結果 preview か。
- two-screen / embed / auto-split のうち、どの結果確認を最優先で可視化すべきか。
- preview を main 画面の中央常設 pane とするのか、別 dialog / subwindow とするのか。
- CLI preview 文字列と visual preview の責務をどう分けるか。

### `Color` など deferred 項目の再読メモ

- current GUI には `Color` ボタンと close handler の痕跡があるが、正本機能としてはまだ成立していない。
- この論点では、legacy 由来のボタンを残すかどうかではなく、「Phase7 の product alignment 上、何を正本機能として扱うか」を決める。

### current 実装から読めること

- `MainWindow.on_set_color()` は、実機能を呼ばず `color picker is deferred to phase7` を status に出すだけのプレースホルダである。
- GUI test も、その deferred status が出ること自体を確認している。
- GTK runtime backend 側でも `Color` ボタン押下は `Color: deferred` 表示へ落ちるだけで、color selection の実処理には接続されていない。
- core / CLI 側には、少なくとも GUI の color picker に対応する正本機能は見当たらない。

### 母体比較

- legacy glade には `btnSetColor` と `ColorSelectionDialog` が存在するため、Color は上流資産としての痕跡は持つ。
- ただし current product alignment の観点では、それは「復元すべきコア導線」であることを直接は意味しない。

### Phase6 までの整理との整合

- Phase6 の lower controls responsibility では、`Color` は core 下部コントロールから外し、Phase7 候補へ送る整理を採っている。
- その理由は、`Color` が Optimize / Apply / watch の正本確認と結び付いておらず、planned のまま main command bar に残すと未完機能と主導線が混線するためだった。
- current 実装を読み直しても、この整理を覆す新しい根拠は増えていない。

### Phase7 の暫定判断

- `Color` は Phase7 の主導線へ戻さない。
- 現時点では、deferred プレースホルダ以上の意味を持っていないため、正本機能として数えない。
- したがって扱いとしては「維持」ではなく、「Phase8 候補として保留」または「削除候補として再判定」の中間ではなく、まずは主導線から外したままにする判断を優先する。
- 少なくとも Phase7 では、`Color` を理由に main 画面構成や controls grouping を揺らさない。

### deferred 項目全体としての読み

- deferred 項目は、legacy 由来の痕跡があることと、current product の必要機能であることを分けて読む必要がある。
- `Color` はその典型であり、上流痕跡はあるが core / CLI / current GUI 主導線のどれとも強く接続していない。
- この種の項目は、Phase7 では「表示上の余地を残す」以上の意味を持たせない方が整合的である。

### 次に詰める問い

- `Color` を本当に Phase8 backlog に残すのか、それとも削除候補として close するのか。
- もし残すなら、background color 指定なのか、余白色や canvas 色の調整なのか、機能定義をどこから切り直すのか。
- deferred 項目のうち、legacy 痕跡だけで残っているものを backlog として維持する基準をどう置くか。

### 5. Phase8 候補の選別

- 対象:
  - Phase7 で承認された新機能候補
  - 実装より先に仕様化が必要なもの
- 主要論点:
  - Phase8 に送ってよい順序は何か
  - 構造負債の再導入を避けられるか
  - owner 実機確認を前提にどの粒度で切るか
- 成果物:
  - Phase8 backlog
  - feature group ごとの優先順

## 機能棚卸し表（Workstream 1 初版）

- 分類メモ: `意図差` は product 上その差を残す前提、`接続済み` は GUI / CLI / core の責務整理と実接続まで完了した項目、`未接続` は土台はあるが GUI / CLI / core の接続が未完、`CLI 専用` は GUI 主導線へ持ち込まない前提、`Phase8 候補` は将来 backlog として送る候補を指す。

| 項目 | core | CLI | GUI | 現時点の分類 | 現時点メモ | 次に詰めること |
| --- | --- | --- | --- | --- | --- | --- |
| `optimize` / `two_screen` 合成 | 実装済み | 実装済み | 2入力 + 2画面検出時に自動投入 | 意図差 | optimize 側の主導線として最も揃っている。apply 側の monitor-aware 挙動とは別レイヤー。 | この理解を棚卸し表の基準線として固定する |
| `Apply` の基本責務 | plugin apply は可能 | dry-run 既定 + `--do-it` | 即時実行 | 意図差 | CLI と GUI で実行ポリシーが異なるが、語彙差を除けば同じ plugin apply を指している。 | この差を残すか、将来さらに寄せるかを別途判断する |
| `Default` / `single-file` apply | `single-file` 経路あり | 既定 apply は `single-file` | visible には `Default` 相当で露出 | 意図差 | 現在の理解では `Default` は monitor-aware 既定ではなく、追加分割なしの通常 apply 経路を指す。 | GUI 表示語を `分割せず適用` 系へ寄せる整理を維持する |
| `Auto-split` | split / monitor-aware apply の土台あり | 実装済み | apply mode として露出済み | 意図差 | Harite 独自価値として `Apply` の主導線に置く判断まで到達した。 | GUI 上でどの程度前面に出すかを UI/文言へ落とす |
| explicit mapping (`--left-file` / `--right-file`) | mapping を受ける土台あり | 実装済み | 未露出 | CLI 専用 | CLI 側の低露出 escape hatch として残す。Harite の主導線とは扱わない。 | GUI 非対象のまま固定するかを棚卸し結果として明記する |
| `watch` 継続ループ | watch runner あり | 実装済み | srcdir / interval / start-stop、timer event 駆動、状態表示、apply 接続あり | 接続済み | GUI は same-process の watch front-end として接続済みであり、`run_watch_cycle()` を刻んで反復 apply を扱う。 | close 判定用の manual validation と文言調整へ進む |
| watch failure-continue / 実切替 | plugin apply と組み合わせ可能 | 実装済み | 既定挙動として継承、詳細 option は未露出 | 意図差 | GUI は CLI と同じ詳細 option 群を広く露出せず、watch 実切替の front-end として必要最小限の責務に留める。 | GUI 非露出のまま維持する語彙境界を確定する |
| `Prefs` / 設定同期 | config / dataclass 基盤あり | config 読み込みあり | dialog 開閉、適用、保存、読込あり | 未接続 | Phase6 で入口と同期基盤は復旧した。内容 grouping と main 画面との責務分担はまだ再設計対象。 | Workstream 4 で main と settings の境界を再整理する |
| `embed-text` / margin info | 実装済み | 実装済み | form / preferences には入るが主導線では未露出 | Phase8 候補 | core / CLI では既に使える一方、GUI では制作機能としてまだ立ち上げきっていない。 | GUI へ送る価値と露出方法を Workstream 4 で判断する |
| per-monitor apply / auto-split の GUI 露出 | 実装済み | 実装済み | `Auto-split` のみ露出、explicit は未露出 | 意図差 | `Auto-split` を主導線、explicit mapping を非主導線とする方向で整理済み。 | GUI に出す apply mode の最終語彙を固める |
| visual preview / assist | 画像 preview の専用基盤は未成熟 | なし | CLI preview 文字列はあるが画像 preview は未成熟 | Phase8 候補 | GUI には optimize CLI preview 相当はあるが、制作支援としての visual preview はまだ候補段階。 | Workstream 4 で backlog 化するか判断する |
| `Color` | core 根拠なし | なし | deferred のまま | Phase8 候補 | 現状は `phase7 deferred` を示すプレースホルダに留まり、正本機能ではない。 | 維持 / 削除 / Phase8 候補のいずれに置くか決める |

## watch responsibility memo（Workstream 3 終盤整理）

- CLI `watch` は、すでに `watch.py` の runner と `cli.py` の command によって、入力検証、列挙戦略、反復実行、`dry-run` / `do-it`、failure-continue、完了サマリまでを一体で持っている。
- GUI の watch tab は、Phase7 実装で source dir 選択、interval 設定、start / stop、直近選択画像の表示に加え、timer event 駆動の 1 cycle 実行、plugin apply、watch 状態表示、出力先表示まで接続した。
- したがって current GUI watch は、独立した watch engine ではなく「same-process の watch runner を利用する front-end」と読むのが自然である。
- 現時点で自然な責務分担は次のとおりである。
  - CLI / watch runner 側が持つもの: 画像列挙、反復実行、`dry-run` / `do-it` の実行、failure-continue、ログ/サマリ。
  - GUI 側が持つもの: source dir / interval などの入力収集、start / stop の入口、timer event による tick 駆動、状態表示、出力先表示、single-source / dual-source の apply 分岐。
- この整理に従い、GUI watch を将来実切替へ接続する場合の基本方針は、「GUI が独自 orchestration を再実装する」のではなく、「CLI watch もしくは watch runner を front-end として呼ぶ」に置く。
- `Apply` との責務境界については、単発の `Apply` と watch の継続実行を同一 UI 群に置くことはあり得るが、内部責務は分けて読むべきである。
  - `Apply` は 1 回の確定実行。
  - `watch` は 反復選択 + 反復 apply を含む継続制御。
- したがって watch 実切替は `Apply` の単純延長ではなく、「plugin apply を内部で利用する別責務」として整理する。
- GUI watch の位置づけは、ターミナルを開かずとも watch を取り扱える front-end とする。

### 接続方式メモ

- 旧導線の再読と現実装確認の範囲では、GUI から CLI `watch` をサブプロセスとして起動することを正本に置いた痕跡は見当たらない。
- upstream / legacy 側で見えるのは、`btnDaemonize` / `btnCancelDaemonize` / `spnInterval` が watch 導線の入口であり、start/stop 自体は caller 側責務として分かれている、という構図である。
- Harite の current GUI 実装も、すでに `collect_watch_input_images` / `select_next_image` を直接使って source dir 検証と初回選択表示を行っており、watch 専用 state も GUI 内に保持している。
- このため、Phase7 で自然な接続方式は「GUI から CLI command をサブプロセス起動する」より、「GUI から watch runner あるいは共有 watch service を同一 process 内で呼ぶ」に寄る。
- ただし current `run_watch_cycles()` は `time.sleep()` を含む blocking ループであり、そのまま GUI main thread から呼ぶのは不適切である。

### 確定した接続方針

- GUI から CLI `watch` command をサブプロセス起動する案は採らない。
- GUI は watch runner あるいは共有 watch service を同一 process 内で利用する front-end とする。
- `run_watch_cycles()` の blocking ループは GUI main thread へそのまま載せず、watch runner を 1 cycle 単位で呼べる形へ分け、GUI timer event で刻む方式を第一案として採る。
- worker thread 方式は代替案としては残り得るが、現時点では interval を GUI が保持し、ターミナルなしで watch を扱う front-end として見せる product の読みと、timer event 方式の方が整合しやすい。

### 現時点の整理結果

- GUI watch は、CLI watch の front-end として扱う。
- GUI が独自の watch orchestration を持つ理由は弱く、独自 engine は採らない。
- failure-continue policy は GUI 独自に再設計せず、CLI watch の既存方針を既定挙動として継承する。
- Phase7 では、GUI watch を timer event 駆動の front-end として実際に接続した。
- 実装上は、`run_watch_cycle()` を `MainWindow.on_watch_tick()` から呼び、GTK runtime backend が timer source の登録/解除を持つ構成で進める。
- GUI 非対象と決めた explicit mapping には踏み込まない。
- そのため L/R 同時 watch は explicit mapping ではなく、2 入力 compose -> `per-monitor-auto-split` の主導線へ落とす。
- watch 中の plugin apply は、single-source では通常 apply、L/R 同時 watch では auto-split apply として接続する。
- watch の生成物は、GUI の current `output_dir` 配下へ出力する。合成画像は `harite_output_####.jpg`、split 後画像はその stem から派生した monitor 別ファイルとして扱う。
- watch が生成した中間ファイル/分割ファイルの cleanup は、次世代 apply が成功した時だけ前世代を掃除する方針とする。
- `Watch Stop` 時は、保持中の現世代を削除せず、そのまま残す。
- apply / prepare 失敗時にできた生成物は、自動 cleanup の対象とせず、そのまま残す。必要な情報は「どこへ出力されるか」を user に伝えることで担保する。
- GUI 上では watch detail に current `output_dir` を表示し、「どこへ出力されるか」を明示する。

### Workstream 3 close 前メモ

- GUI watch の `Start` は、CLI watch の実行開始に対応する正式入口とする。
- GUI には mode / iterations / log level を広く持ち込まず、秒数入力は `interval-sec` 相当の指定として扱う。mode は重複なしの既定挙動に寄せ、選択肢としては前面に出さない。
- watch は Phase8 backlog へ送らず、Phase7 の接続対象として扱う。
- failed artifact は自動 cleanup せず残置し、その代わり watch detail の出力先表示を運用上の手掛かりとする。
- Workstream 3 の残作業は、manual validation と close 文面の確定が中心であり、新たな責務分割の再検討は行わない。

### `watch.py` API 分割案

- current `watch.py` の責務は、次の 3 層に分けて読むと整理しやすい。
  - 入力列挙: `collect_watch_input_images()`
  - 次画像選択: `select_next_image()`
  - 反復制御: `run_watch_cycles()`
- CLI だけを見るなら current API でも成立しているが、GUI timer event 方式へ接続するには、3 層目の反復制御が粗すぎる。
- 問題は `run_watch_cycles()` が `time.sleep()` を内包した blocking loop であり、GUI 側からは「1 cycle だけ進める」単位で呼びにくいことである。

### 分割の基本方針

- `collect_watch_input_images()` はそのまま残す。
- `select_next_image()` も純関数としてそのまま残す。
- `run_watch_cycles()` は CLI 用の薄い orchestration として残しつつ、その内部で使う 1 cycle 単位 API を新設する。

### 新しい最小 API 案

```python
@dataclass
class WatchCycleState:
    index: int = 0
    previous_selected: Path | None = None
    completed: int = 0


def run_watch_cycle(
    images: list[Path],
    mode: str,
    state: WatchCycleState,
) -> tuple[Path, WatchCycleState]:
    ...
```

- `WatchCycleState` は、current `run_watch_cycles()` が内部で握っている `index` / `previous_selected` / `completed` を外へ出した最小状態とする。
- `run_watch_cycle()` は 1 回だけ `select_next_image()` を進め、選ばれた `Path` と更新済み state を返す。
- GUI はこの API を timer event ごとに 1 回呼び、選択結果を受けて plugin apply と UI 更新を行う。
- CLI は `run_watch_cycles()` の中で `run_watch_cycle()` を繰り返し呼ぶだけの薄い wrapper に整理する。

### GUI 側から見た呼び方

- `Watch Start`
  - source dir 検証
  - 画像一覧読み込み
  - `WatchCycleState` 初期化
  - timer event 登録
- timer event 1 tick ごと
  - `run_watch_cycle()` を 1 回呼ぶ
  - 選択画像を plugin apply へ渡す
  - 成功/失敗を UI 状態へ反映する
- `Watch Stop`
  - timer event を解除
  - state を停止状態へ戻す

### CLI 側から見た呼び方

- current `watch()` command の public 仕様は維持する。
- 内部では `run_watch_cycles()` が `run_watch_cycle()` を反復し、`sleep_fn(interval_sec)` を挟む構造へ整理する。
- これにより CLI と GUI が同じ選択ロジックを共有しつつ、反復制御だけをそれぞれの実行文脈に合わせて持てる。

### この案の利点

- 選択ロジックの正本を CLI / GUI で共有できる。
- GUI は blocking loop を持たず、timer event 駆動へ自然に落とせる。
- CLI は既存仕様をほぼ崩さずに内部整理だけで済む。
- テストも `run_watch_cycle()` を中心に増やせるため、GUI 接続前に 1 cycle 単位の正しさを固定しやすい。

### 実装時の注意

- plugin apply は `run_watch_cycle()` の責務へ入れず、呼び出し側責務に残す。
- 失敗継続 policy も cycle 選択ロジックではなく、CLI / GUI それぞれの orchestration 側で扱う。
- 左右 source dir を GUI が別々に持つ場合は、状態も `L` / `R` で分けて保持する。

### 実装前に固定するテスト観点

- current test coverage は、`select_next_image()` の選択規則と、`run_watch_cycles()` の反復・sleep 回数までは見ている。
- 一方で、API 分割後にもっとも壊れやすい `1 cycle` 単位の状態遷移と、GUI 側の停止性はまだ固定できていない。
- したがって実装前の追加観点は、次の順で起こす。

### 1 cycle API の unit test 観点

- `WatchCycleState` 初期状態から 1 回進めると、`completed` が 1 増え、`previous_selected` が選択結果へ更新されること。
- sequential では、`index` が 1 ずつ進み、周回時も選択順が current `select_next_image()` と一致すること。
- random では、`index` を不必要に進めず、`previous_selected` があるときは可能な限り重複回避すること。
- single image の random では、重複回避不能でも正常終了すること。
- 空配列や未知 mode は current と同じく `ValueError` を返すこと。

### CLI wrapper の回帰観点

- `run_watch_cycles()` の public 挙動は維持し、iterations 指定時の完了回数が変わらないこと。
- `sleep_fn()` は「次 cycle があるときだけ呼ぶ」という current 挙動を維持すること。
- `on_cycle(path, completed_index)` に渡る index の意味が変わらないこと。
- interval / iterations の入力検証が current と同じ条件で落ちること。

### GUI 接続前提の観点

- GUI からは `run_watch_cycle()` を 1 tick ごとに呼んでも、main thread を blocking しないこと。
- `Watch Stop` 相当では、次 tick を止めれば watch が停止でき、追加の sleep 待ちが不要であること。
- start 後 1 tick 目で current 表示が更新され、stop 後は state が停止状態へ戻ること。
- 左右 source dir を別管理する場合、片側の state 更新が他方を壊さないこと。

### failure / apply 境界の観点

- cycle 選択そのものは plugin apply の成功失敗に依存しないこと。
- apply 失敗時の継続/停止判断は、`run_watch_cycle()` ではなく orchestration 側で扱えること。
- これにより、CLI の failure-continue policy と GUI の status 表示 policy を分離してテストできること。

### 先に起こすテストの優先順

- まず `tests/watch/test_watch_runner.py` に `run_watch_cycle()` と `WatchCycleState` の unit test を足す。
- 次に既存 `run_watch_cycles()` テストを、新 API を内部利用しても public 挙動が変わらない回帰テストとして残す。
- その後に `tests/gui/test_gtk_runtime_backend.py` で timer/event 接続後の start/stop と current 表示更新を確認する。

## 現時点の読み解きメモ (2026-04-19)

- 現行実装では `two_screen` と `apply_mode` は別レイヤーの概念である。`two_screen` は optimize 時に「2入力と表示構成に応じて 1 枚の合成結果をどう作るか」を決め、`apply_mode` は optimize 後の 1 枚を「そのまま貼るか、apply 時点で分割するか」を決める。
- したがって CLI `apply --file <4096x1280>` の既定動作は、次のように読むべきである。
  - 2 画面文脈を見て暗黙分割することではない。
  - `single-file` として plugin 実装部へそのまま渡す。
  - 暗黙分割は現行では存在せず、明示的な `--auto-split` を指定した場合だけ `per-monitor-auto-split` へ入る。
- GUI は `MainWindow` 側で 2 入力かつ 2 画面検出時に `two_screen` を自動で有効化し、virtual resolution を自動投入する。
  - そのため user から見ると、optimize と apply が 1 本の two-screen workflow に見えやすい。
  - 一方で apply 側は `Default` / `Auto-split` の 2 択しかなく、`Default` は `single-file` のままで `two_screen` 文脈を参照しない。
- 現行の直接原因としては、`monitor-split` 導入後に「optimize で two-screen 合成が自動化されたこと」と「apply に auto-split が追加されたこと」が並立し、GUI 上で `Default` という語がその差を隠してしまった点が大きい。
- `src/harite/plugins.py` の helper 抽出・`xfconf` 候補照合の整理は monitor ごとの割当精度と実行経路の整理であり、上位の apply semantics 自体を変えた主因とは見なしにくい。
- 今回の論点を作った主な転換点と、`Default` の位置づけの揺れは、以下の 3 世代比較でまとめて扱う。

## 3世代比較メモ (母体 / Harite v0.1.2 / 現在)

### 1. 母体プログラム

- 母体では `Apply` は独立した mode 切替ではなく、`WindowBase.btnSetWall_clicked()` から `Core.singlerun()` を呼び、その中で `option.setWall=True` のときだけ `_setWall()` へ進む即時実行である。
- したがって母体の `Apply` は `dry-run` / `do-it` / `Default` / `Auto-split` のような語彙を持たない。`Save` は保存、`Apply` は即時変更、`Daemonize` は継続切替という責務分離である。
- 母体の `two_screen` 相当の関心は optimize / compose 側にあり、左右ディスプレイサイズ・`fixed`・margin を使って「1 枚の最終壁紙をどう作るか」を決める。`Apply` 自体は生成済みの 1 枚を WM command (`setWall`) に渡すだけで、apply 時点の暗黙分割は持たない。
- XFCE command でも `Xfce41Command.setWall(path)` は primary monitor 系の `last-image` に 1 パスを書き込む構造であり、母体に `Default` vs `Auto-split` の対立は存在しない。

### 2. Harite v0.1.2

- `v0.1.2` では母体の即時 `Apply` から離れ、CLI に独立した `apply` command と `dry-run` / `--do-it` を導入している。ここで `apply` は「plugin 呼び出しの安全なラッパー」として設計され、既定は dry-run になった。
- さらに `--per-monitor` / `--left-file` / `--right-file` / `--auto-split` が入り、apply 時点で単一ファイル適用と monitor 別適用を切り替える語彙が追加された。
  - `--left-file` / `--right-file` は explicit mapping として、monitor ごとの適用対象を user が直接与える経路である。
  - `--auto-split` は、その対応付けを Harite 側で自動生成する経路である。
  - つまり `v0.1.2` で初めて、母体にはなかった `apply` semantics の分岐が生まれた。
- 一方で `v0.1.2` GUI はまだ `on_apply_dry_run()` / `on_apply_do_it()` の 2 段で、現行の `Default` という語は存在しない。ここでは曖昧語ではなく `dry-run` / `do-it` が前面に出ていた。
- この世代では `two_screen` は optimize 引数であり、`apply` の `auto-split` とは別概念だが、GUI 上で両者を接続する見せ方はまだ弱かった。

### 3. 現在

- 現在の CLI は `v0.1.2` の semantics を概ね保持したまま、`apply_settings.py` と `display_context.py` によって `single-file` / `per-monitor-explicit` / `per-monitor-auto-split` を明示化している。
- つまり current CLI の本質的意味は `v0.1.2` から大きく変わっていない。
  - 変化したのは helper 化・display ordering・GUI からも使えるようにした整理である。
  - `single-file` / `per-monitor-explicit` / `per-monitor-auto-split` の 3 経路は維持されている。
- いまの曖昧さは、GUI が optimize 側で `two_screen` を自動化しつつ、apply 側では `Default` / `Auto-split` の 2 択へ言い換えたことで発生している。
  - `Default` という語が、母体の即時 apply、CLI の single-file apply、desktop/plugin default のどれを指すのかを隠してしまった。
- その結果、user は「2画面 optimize の流れの延長として `Default` でも何らかの monitor-aware apply が起きる」と期待しやすいが、実際には current CLI / GUI とも `Default` = `single-file` であり、2画面文脈を apply 時に参照しない。
- 一方で `per-monitor-explicit` は GUI には露出していない。Phase6 では「user の意識に上がりにくく、`Optimize` で何を作れるかという主導線とも離れる」という理由で UI 表には出さなかったが、CLI では依然として expert 機能として残っている。
- さらに CLI には、`-r` へ実画面より小さい解像度を意図的に与え、アスペクト比や画角を優先した生成物を作ったうえで、後段の `per-monitor-explicit` や `auto-split` で monitor 別適用へつなぐ発想がある。
  - これは「最終的に desktop がどう表示するか」と「Harite がどの寸法の生成物を作るか」をあえて切り離す使い方である。
  - 現行 GUI の自然導線には存在しない。
- この発想の動機には、見せたい構図の維持だけでなく、保存する JPG のサイズをあえて抑えることも含まれる。
  - ただしこれは、主流の user が強く求める導線というより、成立し得るニッチな運用である。
  - つまり CLI では、生成物の寸法・容量・desktop style・後段 apply を組み合わせて最終結果を作る workflow は存在するが、product の主導線として強く押し出す性質のものではない。

### 比較表

| 観点 | 母体プログラム | Harite v0.1.2 | 現在 |
| --- | --- | --- | --- |
| `Apply` の基本責務 | 即時に壁紙変更 | plugin apply command 呼び出し | plugin apply command 呼び出し |
| 既定動作 | 即時実行 | dry-run | GUI は即時、CLI は dry-run |
| `Default` 語彙 | なし | なし | GUI にのみ存在 |
| `two_screen` の位置づけ | optimize/compose 側 | optimize 側 | optimize 側 |
| explicit mapping (`left/right-file`) | なし | CLI にあり | CLI にあり、GUI にはなし |
| `auto-split` の位置づけ | なし | apply 時の明示機能 | apply 時の明示機能 |
| apply 時の暗黙 monitor 分割 | なし | なし | なし |
| watch / daemonize との関係 | 別責務 | `watch` + plugin apply | `watch` + plugin apply |

## 具体シナリオメモ（left-A / right-B を貼りたいとき）

- 前提: left, right の 2 画面があり、画像 A, B をそれぞれ `left-A`, `right-B` として貼りたいケースを考える。
- このとき論点は「Harite に何を作らせるか」と「最後にどう apply するか」を分けて読むことにある。

### 1. `apply` のみで `per-monitor-explicit` を使う

- 既に `left-A` と `right-B` が手元にあるなら、`optimize` を使わず `apply --left-file ... --right-file ...` だけで monitor 別適用できる。
- この経路では Harite は新しい最終成果物を作らない。責務は「既存の 2 ファイルを monitor 名付き mapping として plugin に渡すこと」である。
- したがってこれは `optimize` workflow ではなく、apply 側の expert 経路として読むのが自然である。

### 2. 左右を別々に `optimize` して、最後に `per-monitor-explicit` で貼る

- `left` 用解像度で A を optimize して `left-A` を作り、同様に `right` 用解像度で B を optimize して `right-B` を作り、最後に `apply --left-file ... --right-file ...` で貼ることもできる。
- ただしこれは 2 画面横断の `two_screen optimize` ではない。single-screen optimize を 2 回行い、最後だけ explicit mapping を使う構成である。
- つまり `optimize` は使っているが、「2 入力から 1 枚の合成成果物を作る」という Harite の主導線とは別の使い方になる。
- また CLI では、ここで `-r` に実画面ぴったりではない小さめ解像度を意図的に与え、アスペクト比や見せたい構図を優先した `left-A` / `right-B` を作る使い方もあり得る。この場合 `optimize` は desktop 解像度への厳密適合ではなく、「後段 apply に渡すための望ましい素材生成」として使われる。
- このとき最終的な desktop 結果は、「小さめ解像度で作った JPG」「desktop 側の style 指定」「最後の per-monitor apply」の合わせ技で決まる。したがって user の意図は「画面解像度どおりの完成画像を作る」よりも、「容量や見せ方を含めて運用しやすい素材を作る」に近い。

### 3. 2 入力で `optimize` し、最後に `auto-split` で貼る

- `left-A`, `right-B` として 2 入力を与え、`two_screen optimize` で 1 枚の合成結果を作り、それを `apply --auto-split` で monitor 別に割り当てることもできる。
- これは「Harite に 2 画面横断の最終成果物を作らせ、その成果物から monitor ごとの apply target を自動生成する」流れである。
- GUI の現在の導線はこの考え方に最も近い。GUI は `Default` / `Auto-split` の 2 択しか持たず、explicit mapping は露出していないためである。

### 4. `Default` を選んだときに起きること

- 上の 3 番の流れでも、最後に `Default` を選んだ場合は monitor 別割当にはならない。`Default` は current 実装上 `single-file` であり、合成済み 1 ファイルを plugin 実装部へそのまま渡すだけである。
- monitor 別 apply が起きるのは `per-monitor-explicit` または `per-monitor-auto-split` を選んだときだけである。

### 5. 前提条件と caveat

- `per-monitor-explicit` は思想上は plugin / desktop 側の制約を補う apply mode だが、現行実装で monitor 名付き mapping を実際に扱っているのは Linux plugin である。
- そのため 1 番と 2 番は、現状では主に Linux / XFCE 系の expert path として理解するのが正確である。
- `auto-split` も current 実装では Linux plugin と 2 画面検出を前提とするため、任意の plugin で一般化された monitor-aware apply とはまだ言い切れない。
- さらに CLI では、生成物の解像度を実画面サイズに一致させること自体を必須としない expert な運用があり得る。ここでは `optimize` の目的が「検出済み display にぴったり合わせること」ではなく、「アスペクト比や画角を保ったまま apply 用素材を作ること」へ寄る。
- そこでは保存される JPG 自体のサイズを抑えることも目的になり得るため、GUI の「検出した画面に対して最終成果物を作る」発想とはかなり異なる。
- この発想は GUI の current runtime にはほぼ存在しない。GUI は auto-detect と two-screen workflow に寄っており、user に「実画面と生成解像度を意図的にずらして設計する」操作語彙を提示していないためである。
- XFCE は style の選択肢が比較的多く、single-file では横長 1 枚の解釈に、auto-split では各 monitor 用画像の拡大縮小・配置に影響し得る。そのため desktop 上の見え方だけで `optimize` / `split` の正否を判定しない。
- 少なくとも Phase7 の検証では、まず `optimize` で生成された 4096x1280 JPG や `auto-split` で生成された monitor 別 JPG 自体を確認し、その後に XFCE 上の表示を「plugin + desktop style を含む総合結果」として読む。
- 逆に 3 番は、`optimize` と `apply` の責務分離を最も素直に保つ。`optimize` は最終成果物を作り、`apply` はその成果物をどう貼るかを決める、という分離である。

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

## Phase7 で決めるべき問い（3世代比較を踏まえて）

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

## 現時点の読み解きメモ (2026-04-19)

- 現行実装では `two_screen` と `apply_mode` は別レイヤーの概念である。`two_screen` は optimize 時に「2入力と表示構成に応じて 1 枚の合成結果をどう作るか」を決め、`apply_mode` は optimize 後の 1 枚を「そのまま貼るか、apply 時点で分割するか」を決める。
- したがって CLI `apply --file <4096x1280>` の既定動作は、次のように読むべきである。
  - 2 画面文脈を見て暗黙分割することではない。
  - `single-file` として plugin 実装部へそのまま渡す。
  - 暗黙分割は現行では存在せず、明示的な `--auto-split` を指定した場合だけ `per-monitor-auto-split` へ入る。
- GUI は `MainWindow` 側で 2 入力かつ 2 画面検出時に `two_screen` を自動で有効化し、virtual resolution を自動投入する。
  - そのため user から見ると、optimize と apply が 1 本の two-screen workflow に見えやすい。
  - 一方で apply 側は `Default` / `Auto-split` の 2 択しかなく、`Default` は `single-file` のままで `two_screen` 文脈を参照しない。
- 現行の直接原因としては、`monitor-split` 導入後に「optimize で two-screen 合成が自動化されたこと」と「apply に auto-split が追加されたこと」が並立し、GUI 上で `Default` という語がその差を隠してしまった点が大きい。
- `src/harite/plugins.py` の helper 抽出・`xfconf` 候補照合の整理は monitor ごとの割当精度と実行経路の整理であり、上位の apply semantics 自体を変えた主因とは見なしにくい。
- 今回の論点を作った主な転換点と、`Default` の位置づけの揺れは、以下の 3 世代比較でまとめて扱う。

## 3世代比較メモ (母体 / Harite v0.1.2 / 現在)

### 1. 母体プログラム

- 母体では `Apply` は独立した mode 切替ではなく、`WindowBase.btnSetWall_clicked()` から `Core.singlerun()` を呼び、その中で `option.setWall=True` のときだけ `_setWall()` へ進む即時実行である。
- したがって母体の `Apply` は `dry-run` / `do-it` / `Default` / `Auto-split` のような語彙を持たない。`Save` は保存、`Apply` は即時変更、`Daemonize` は継続切替という責務分離である。
- 母体の `two_screen` 相当の関心は optimize / compose 側にあり、左右ディスプレイサイズ・`fixed`・margin を使って「1 枚の最終壁紙をどう作るか」を決める。`Apply` 自体は生成済みの 1 枚を WM command (`setWall`) に渡すだけで、apply 時点の暗黙分割は持たない。
- XFCE command でも `Xfce41Command.setWall(path)` は primary monitor 系の `last-image` に 1 パスを書き込む構造であり、母体に `Default` vs `Auto-split` の対立は存在しない。

### 2. Harite v0.1.2

- `v0.1.2` では母体の即時 `Apply` から離れ、CLI に独立した `apply` command と `dry-run` / `--do-it` を導入している。ここで `apply` は「plugin 呼び出しの安全なラッパー」として設計され、既定は dry-run になった。
- さらに `--per-monitor` / `--left-file` / `--right-file` / `--auto-split` が入り、apply 時点で単一ファイル適用と monitor 別適用を切り替える語彙が追加された。
  - `--left-file` / `--right-file` は explicit mapping として、monitor ごとの適用対象を user が直接与える経路である。
  - `--auto-split` は、その対応付けを Harite 側で自動生成する経路である。
  - つまり `v0.1.2` で初めて、母体にはなかった `apply` semantics の分岐が生まれた。
- 一方で `v0.1.2` GUI はまだ `on_apply_dry_run()` / `on_apply_do_it()` の 2 段で、現行の `Default` という語は存在しない。ここでは曖昧語ではなく `dry-run` / `do-it` が前面に出ていた。
- この世代では `two_screen` は optimize 引数であり、`apply` の `auto-split` とは別概念だが、GUI 上で両者を接続する見せ方はまだ弱かった。

### 3. 現在

- 現在の CLI は `v0.1.2` の semantics を概ね保持したまま、`apply_settings.py` と `display_context.py` によって `single-file` / `per-monitor-explicit` / `per-monitor-auto-split` を明示化している。
- つまり current CLI の本質的意味は `v0.1.2` から大きく変わっていない。
  - 変化したのは helper 化・display ordering・GUI からも使えるようにした整理である。
  - `single-file` / `per-monitor-explicit` / `per-monitor-auto-split` の 3 経路は維持されている。
- いまの曖昧さは、GUI が optimize 側で `two_screen` を自動化しつつ、apply 側では `Default` / `Auto-split` の 2 択へ言い換えたことで発生している。
  - `Default` という語が、母体の即時 apply、CLI の single-file apply、desktop/plugin default のどれを指すのかを隠してしまった。
- その結果、user は「2画面 optimize の流れの延長として `Default` でも何らかの monitor-aware apply が起きる」と期待しやすいが、実際には current CLI / GUI とも `Default` = `single-file` であり、2画面文脈を apply 時に参照しない。
- 一方で `per-monitor-explicit` は GUI には露出していない。Phase6 では「user の意識に上がりにくく、`Optimize` で何を作れるかという主導線とも離れる」という理由で UI 表には出さなかったが、CLI では依然として expert 機能として残っている。
- さらに CLI には、`-r` へ実画面より小さい解像度を意図的に与え、アスペクト比や画角を優先した生成物を作ったうえで、後段の `per-monitor-explicit` や `auto-split` で monitor 別適用へつなぐ発想がある。
  - これは「最終的に desktop がどう表示するか」と「Harite がどの寸法の生成物を作るか」をあえて切り離す使い方である。
  - 現行 GUI の自然導線には存在しない。
- この発想の動機には、見せたい構図の維持だけでなく、保存する JPG のサイズをあえて抑えることも含まれる。
  - ただしこれは、主流の user が強く求める導線というより、成立し得るニッチな運用である。
  - つまり CLI では、生成物の寸法・容量・desktop style・後段 apply を組み合わせて最終結果を作る workflow は存在するが、product の主導線として強く押し出す性質のものではない。

### 比較表

| 観点 | 母体プログラム | Harite v0.1.2 | 現在 |
| --- | --- | --- | --- |
| `Apply` の基本責務 | 即時に壁紙変更 | plugin apply command 呼び出し | plugin apply command 呼び出し |
| 既定動作 | 即時実行 | dry-run | GUI は即時、CLI は dry-run |
| `Default` 語彙 | なし | なし | GUI にのみ存在 |
| `two_screen` の位置づけ | optimize/compose 側 | optimize 側 | optimize 側 |
| explicit mapping (`left/right-file`) | なし | CLI にあり | CLI にあり、GUI にはなし |
| `auto-split` の位置づけ | なし | apply 時の明示機能 | apply 時の明示機能 |
| apply 時の暗黙 monitor 分割 | なし | なし | なし |
| watch / daemonize との関係 | 別責務 | `watch` + plugin apply | `watch` + plugin apply |

## 具体シナリオメモ（left-A / right-B を貼りたいとき）

- 前提: left, right の 2 画面があり、画像 A, B をそれぞれ `left-A`, `right-B` として貼りたいケースを考える。
- このとき論点は「Harite に何を作らせるか」と「最後にどう apply するか」を分けて読むことにある。

### 1. `apply` のみで `per-monitor-explicit` を使う

- 既に `left-A` と `right-B` が手元にあるなら、`optimize` を使わず `apply --left-file ... --right-file ...` だけで monitor 別適用できる。
- この経路では Harite は新しい最終成果物を作らない。責務は「既存の 2 ファイルを monitor 名付き mapping として plugin に渡すこと」である。
- したがってこれは `optimize` workflow ではなく、apply 側の expert 経路として読むのが自然である。

### 2. 左右を別々に `optimize` して、最後に `per-monitor-explicit` で貼る

- `left` 用解像度で A を optimize して `left-A` を作り、同様に `right` 用解像度で B を optimize して `right-B` を作り、最後に `apply --left-file ... --right-file ...` で貼ることもできる。
- ただしこれは 2 画面横断の `two_screen optimize` ではない。single-screen optimize を 2 回行い、最後だけ explicit mapping を使う構成である。
- つまり `optimize` は使っているが、「2 入力から 1 枚の合成成果物を作る」という Harite の主導線とは別の使い方になる。
- また CLI では、ここで `-r` に実画面ぴったりではない小さめ解像度を意図的に与え、アスペクト比や見せたい構図を優先した `left-A` / `right-B` を作る使い方もあり得る。この場合 `optimize` は desktop 解像度への厳密適合ではなく、「後段 apply に渡すための望ましい素材生成」として使われる。
- このとき最終的な desktop 結果は、「小さめ解像度で作った JPG」「desktop 側の style 指定」「最後の per-monitor apply」の合わせ技で決まる。したがって user の意図は「画面解像度どおりの完成画像を作る」よりも、「容量や見せ方を含めて運用しやすい素材を作る」に近い。

### 3. 2 入力で `optimize` し、最後に `auto-split` で貼る

- `left-A`, `right-B` として 2 入力を与え、`two_screen optimize` で 1 枚の合成結果を作り、それを `apply --auto-split` で monitor 別に割り当てることもできる。
- これは「Harite に 2 画面横断の最終成果物を作らせ、その成果物から monitor ごとの apply target を自動生成する」流れである。
- GUI の現在の導線はこの考え方に最も近い。GUI は `Default` / `Auto-split` の 2 択しか持たず、explicit mapping は露出していないためである。

### 4. `Default` を選んだときに起きること

- 上の 3 番の流れでも、最後に `Default` を選んだ場合は monitor 別割当にはならない。`Default` は current 実装上 `single-file` であり、合成済み 1 ファイルを plugin 実装部へそのまま渡すだけである。
- monitor 別 apply が起きるのは `per-monitor-explicit` または `per-monitor-auto-split` を選んだときだけである。

### 5. 前提条件と caveat

- `per-monitor-explicit` は思想上は plugin / desktop 側の制約を補う apply mode だが、現行実装で monitor 名付き mapping を実際に扱っているのは Linux plugin である。
- そのため 1 番と 2 番は、現状では主に Linux / XFCE 系の expert path として理解するのが正確である。
- `auto-split` も current 実装では Linux plugin と 2 画面検出を前提とするため、任意の plugin で一般化された monitor-aware apply とはまだ言い切れない。
- さらに CLI では、生成物の解像度を実画面サイズに一致させること自体を必須としない expert な運用があり得る。ここでは `optimize` の目的が「検出済み display にぴったり合わせること」ではなく、「アスペクト比や画角を保ったまま apply 用素材を作ること」へ寄る。
- そこでは保存される JPG 自体のサイズを抑えることも目的になり得るため、GUI の「検出した画面に対して最終成果物を作る」発想とはかなり異なる。
- この発想は GUI の current runtime にはほぼ存在しない。GUI は auto-detect と two-screen workflow に寄っており、user に「実画面と生成解像度を意図的にずらして設計する」操作語彙を提示していないためである。
- XFCE は style の選択肢が比較的多く、single-file では横長 1 枚の解釈に、auto-split では各 monitor 用画像の拡大縮小・配置に影響し得る。そのため desktop 上の見え方だけで `optimize` / `split` の正否を判定しない。
- 少なくとも Phase7 の検証では、まず `optimize` で生成された 4096x1280 JPG や `auto-split` で生成された monitor 別 JPG 自体を確認し、その後に XFCE 上の表示を「plugin + desktop style を含む総合結果」として読む。
- 逆に 3 番は、`optimize` と `apply` の責務分離を最も素直に保つ。`optimize` は最終成果物を作り、`apply` はその成果物をどう貼るかを決める、という分離である。

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

## Phase7 で決めるべき問い（3世代比較を踏まえて）

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

## 完了条件

- CLI / GUI / core の差分が、`意図差` / `抜け漏れ` / `削除候補` / `Phase8 候補` に分類されている。
- `optimize` / `apply` / `dry-run` / `do-it` / `watch` の語彙と責務境界について、owner 判断に必要な材料が揃っている。
- GUI に入れる候補機能が、単なる思いつきではなく Phase8 backlog として列挙されている。
- Phase8 に送る新機能と、Phase7 内で閉じる設計整理が分離されている。
- 少なくとも `do-it` の扱いについて、維持 / 改名 / 廃止の比較が文書化されている。

## 判断メモ

- `do-it` は単なるオプション名ではなく、CLI の安全設計と GUI の即時実行ポリシーの衝突点である。
- したがって `do-it` の再整理は、CLI UX だけでなく manual gate / docs / plugin apply の説明にも波及する。
- `watch` の不足補完は新機能追加に見えるが、実際には CLI 先行機能との整合性整理でもある。
- `embed-text` のような margin 利用機能は、GUI に持ち込むと制作画面としての意味が増すため、Phase8 候補として価値が高い。
- `Auto-split` は、現時点では `Apply` の主導線に最も近い Harite 独自機能として扱うのが自然である。
- `per-monitor-explicit` は残すとしても、`auto-split` より前面に出すのではなく CLI 側の低露出な escape hatch に留める。
- 逆に、GUI に理由なく CLI 専用機能をそのまま移植すると、Phase6 で落とした暫定 UI の複雑さを戻す危険がある。

## 初動タスク

### T7-1. 機能棚卸し表の作成

- CLI / GUI / core の機能差分を 1 表へまとめる。

### T7-2. 操作語彙比較メモの作成

- `optimize` / `apply` / `dry-run` / `do-it` / `watch` の意味を並べ、候補案を比較する。

### T7-3. watch responsibility memo の作成

- GUI watch を CLI watch の front-end として扱うかを中心に、責務境界を再定義する。

### T7-4. GUI 候補機能バックログの作成

- `embed-text`、per-monitor apply、preview、deferred 項目などを Phase8 候補として整理する。

## Phase8 の位置づけ

- Phase8 は、Phase7 で承認された候補機能だけを実装するフェーズとする。
- したがって Phase8 は探索フェーズではなく、仕様化済み backlog の実装フェーズとして扱う。
- Phase7 で整合性整理が終わらない限り、Phase8 の着手条件は満たさない。

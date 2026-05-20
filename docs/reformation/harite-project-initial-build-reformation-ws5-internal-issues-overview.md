# Harite Project Initial Build Reformation WS5 Internal Issues Overview

最終更新: 2026-05-20

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 5 を具体化する子文書である。
- 主題は、`1.0.0` 後に扱う現行機能まわりの内部 issue 解決と surface 整理の overview 作成である。
- 本書は `1.0.0` gate ではなく、その後に開く cleanup / rename / consistency planning の入口として扱う。

関連子文書:

- 用語ぶれ一覧: [docs/reformation/harite-project-initial-build-reformation-ws5-terminology-drift-inventory.md](docs/reformation/harite-project-initial-build-reformation-ws5-terminology-drift-inventory.md)

## この stream で固定すること

- 現行機能に残る内部 issue を inventory 化する。
- rename 候補、弱い surface、責務ずれ、用語不一致を粗く切り分ける。
- 丸く書かれている計算過程を、式と決定規則まで含めて記述し直す論点を固定する。
- 後続 cleanup planning の入口文書として、論点の土台を作る。
- WS4 の抽出・事実記載を受けて、どう直すか、どこまで直すかを扱う working の入口を作る。
- 今後の内部整理では、正本を先に直し、その変更を前提に実装を直す運用を採る。

## 対象

- watch / CLI / core / plugin の surface 不一致
- 実装・help・正本のずれ
- 命名、責務、観測面の再整理候補
- 計算過程と入力値利用規則の明文化不足
- 現行機能の未成立 command / option / helper

## 非対象

- `1.0.0` 前に実装を始めること
- release / packaging 整理
- docs 再編そのもの
- 新規 feature 構想の棚卸し

## WS5 の運用原則

- WS5 は、WS4 で整えた正本を起点にして進める。
- 以後、内部整理や rename、surface 整理を実施する場合は、先に正本の該当箇所を更新し、その差分を根拠として実装を更新する。
- したがって「正本を直さないまま実装だけ先に変える」進め方は採らない。
- これは厳密な意味での formal な仕様駆動開発ではなく、その簡易運用として「正本先行」を固定するものである。
- ただし WS5 前半では、正本を書き換える前提条件として、どの論点を積極維持するか、rename・cleanup するか、削除・縮退するかを inventory と working で切り分ける。
- 今回の WS5 は、過去 2 回の大きめの refactoring と同等規模を許容する前提で進める。
- 対象は表層の wording や help だけに留めず、必要ならテスト、source、責務分割、module 境界まで掘り下げて揃える。
- 「一部は影響が小さいから残す」という局所妥協は採らず、根まで辿って不一致を閉じる方針を優先する。
- 提供者側の都合として「直せないから放置する」という答えは採らない。時間とコストを要しても、公開アプリとして出す以上は維持・rename・削除縮退の能動判断に落とす。
- 変更順は `仕様書 -> テスト -> ソース` を原則とし、3 面を揃えて `1.0.0` 後に運用不能な残債が残る可能性を極力下げる。

## 推奨作業順

### 1. 判断枠の固定

- 各論へ入る前に、論点を `積極維持 / rename・cleanup / 削除・縮退候補` に切る基準を先に揃える。
- あわせて、文書のみ直す論点か、source / tests まで追う論点か、挙動変更を伴う論点かを区別する。
- この段階の branch は実装修正を混ぜない計画 branch として閉じ、後続では論点束ごとの fix branch を並べて追跡可能にする。

判断基準:

- 今回は小修正前提ではなく、大きめの refactoring を許容する前提で基準を置く。
- 正系語や user-facing 概念は、repo 内の慣習よりも、公開アプリとして一般的に通じる標準的な語彙と観念を優先する。
- user-visible な妙な仕様、命名ずれ、責務ずれ、弱い surface は、表層だけでなく根の設計要因まで追う。
- 部分的に直して残りを温存する進め方は採らず、関連する仕様書、tests、source を一体で閉じる。
- したがって `積極維持` は「手を付けない」の意味ではなく、公開アプリとして妥当な状態にあるため、現行仕様として積極的に維持すると判断したものだけに使う。
- `直せないから放置する` は分類に含めず、維持・rename・削除縮退のいずれかへ必ず落とす。
- `rename・cleanup` は wording 修正に限らず、分割、移送、責務再配置、tests 追随を含む。
- `削除・縮退候補` は user-visible な導線、command、option、helper を含めて判定対象にする。

### 2. watch 系の整理

- 最優先は watch 系とする。
- 対象は、`watch` の実体名、`スライドショー` への public naming、`interval / cycle / サイクル`、`実行メッセージ / ステータス / メッセージ履歴 / ロガー`、`mode`、`iterations`、GUI 非対応を含む。
- watch は命名、観測面、CLI / GUI 差、未成立 surface が密集しているため、他論点より先に扱う。

### 3. CLI 未成立 surface の棚卸し

- 次に CLI command / option のうち、存在はするが未成立または効きが弱いものを整理する。
- 代表例は `compute-placement`、watch の `mode` / `iterations`、CLI 実行メッセージ粒度の名称、`scaling`、`random-seed`、弱い helper 群である。

### 4. 設定 / config / preferences 系の整理

- その次に、`設定 / 設定ファイル / config / preferences / harite-preferences.json` の関係をまとめて扱う。
- 正系語は `設定` を主語に固定し、`config` は設定ファイルや設定入出力の補助語に下げ、`preferences` は rename 対象として扱う。
- 文書語、媒体名、source 上の file / module / class / handler 名の 4 層を分けて判断する。
- したがってこの段では、関数名や class 名だけでなく、実装モジュール名とファイル名の rename も対象に含める。

### 5. apply target / monitor map / plugin fallback の整理

- apply 側の上位概念と Linux plugin 側の受け口名のずれをここで扱う。
- あわせて plugin fallback (`xfconf-query`, `gsettings`, `feh`) の正本記述と command surface のずれも棚卸対象にする。

### 6. 低波及の残件回収

- 最後に、GUI watch 表示名、`Save Settings / Export Image`、README 軽追随、弱い helper の扱いなどを回収する。
- この段では、前段で決めた語彙と責務境界に従って小さく閉じる。

## fix ブランチ列の簡易ロードマップ

- 現在の branch は、WS5 の判断基準、正本先行ルール、作業順を固定する計画 branch として扱う。
- この計画 branch を閉じた後、後続では fix branch 相当を論点束ごとに並べる。
- 各 fix branch では、`正本更新 -> 実装更新 -> tests 追随` の順を原則とする。
- 「全部直す」前提で進めるため、優先順位は「着手するか否か」の選別ではなく、依存関係に沿った分割順として使う。

### 計画 branch

- 候補名: `ws5-plan-canonical-first`
- 役割: WS5 の対象範囲、分類基準、正本先行ルール、後続 fix branch 列を固定する。
- この branch では実装修正を進めず、計画と trace の基準だけを確定する。

### 後続 fix branch 列

1. `ws5-fix-watch-surface`
   - 対象: watch の実体名、`スライドショー` への public naming、`interval / cycle / サイクル`、`実行メッセージ / ステータス / メッセージ履歴 / ロガー`、`mode`、`iterations`、GUI 非対応
   - 位置づけ: user-visible な違和感と命名ずれが最も密集しているため最初に扱う

2. `ws5-fix-cli-weak-surface`
   - 対象: `compute-placement`、watch の CLI 偏在 option、CLI 実行メッセージ粒度の名称、`scaling`、`random-seed`、弱い helper 群
   - 位置づけ: watch 系の整理結果を受けて、CLI surface の成立性を切り分ける

3. `ws5-fix-config-preferences-terms`
   - 対象: `設定 / 設定ファイル / config / preferences / harite-preferences.json`
   - 位置づけ: `設定` を主語に固定しつつ、媒体名と source 上の file / module / class / handler naming を跨いで `config` と `preferences` の残滓を閉じるため、前段の命名整理後に扱う

4. `ws5-fix-apply-target-plugin-boundary`
   - 対象: `apply target / monitor map / mapping`、plugin fallback (`xfconf-query`, `gsettings`, `feh`)
   - 位置づけ: apply 側の上位概念と plugin 側の受け口のずれをまとめて閉じる

5. `ws5-fix-low-impact-followups`
   - 対象: GUI watch 表示名、設定保存と画像保存の語、README 軽追随、弱い残件
   - 位置づけ: 前段で決めた語彙と責務境界に従って低波及の残件を回収する

### トレースの考え方

- 1 論点束 1 branch を原則にし、どの正本変更がどの実装修正を導いたかを branch 単位で辿れるようにする。
- 大きな rename や user-visible 変更は、複数論点を 1 branch に混ぜず、正本差分と実装差分の対応が読める単位で閉じる。
- したがって、WS5 の前半では branch 数を減らすことより、後から trace しやすい分割を優先する。

## 現時点の論点

### 1. 内部 issue の棚卸し方

- 断片的な違和感や不一致を、その場しのぎで直すのではなく一覧として集約する必要がある。
- ただし、いまは優先順位の精密化より inventory 化を優先する。
- 正本側の事実記載 working と、WS5 での「どう直すか / どこまで直すか」の判断 working を混ぜないように、一覧化と意思決定を段階分離する必要がある。

### 2. 分類の粒度

- 積極維持する項目
- rename / cleanup 候補
- 削除または縮退候補

### 3. 次期 planning への渡し方

- overview から次の cleanup / rename planning へどう送るか。
- 単発メモを増やしすぎず、入口文書で受ける必要がある。

### 4. 計算過程の明文化候補

- 現行の正本では、特に core を中心に「xx と yy を計算し、zz に収まるかを判断する」「margin 内の表示領域へ解決する」のような丸い説明が残っている。
- しかし optimize / placement / auto-split / embed では、user が投入した `resolution`, `margins`, `align`, `valign`, `two_screen`, `l_display`, `r_display` などが最終的にどの式へ入るかを追える必要がある。
- そのため WS5 では、まず core 正本を最優先に、各入力値がどの中間値へ変換され、どの比較や判定に使われ、どの出力値へ落ちるかを式と決定規則で明文化する。
- その後、CLI / watch / plugin / GUI は、core の計算規則を前提にしつつ、自分たちの分冊で必要な追加計算や値解決だけを追記する。
- 特に `margins`、有効描画領域、fit / fill 系の scale 決定、two-screen 時の左右割当、auto-split 時の切り出し範囲、embed 位置解決は、文章要約だけでなく式または段階列として記述する候補に含める。
- ただし WS4 で事実記載の一巡は終えているため、WS5 初動では再度この論点へ広く戻らず、命名・surface・責務整理の中で不足が再度見えた場合に限って補修対象として扱う。

### 5. 用語と責務の再整理方針

- CLI watch の `log_level` は実態として stdout 出力粒度の切り替えであり、一般的な「ログ」機能として読むと誤解しやすい。
- したがって観測面をまたぐ `log` 総称は正系語にせず、CLI は `実行メッセージ`、GUI は `ステータス` と `メッセージ履歴`、plugin は `ロガー` へ分離して扱う。
- WS5 では名称だけでなく、保存先の有無、観測面、tests 上の観測語まで含めて揃える。

### 6. watch の整理方針

- watch helper と CLI watch には `sequential` / `random` の選択モードがある。
- 一方で GUI watch は現状 `sequential` 固定で、対応する mode 選択 UI を持たない。
- `iterations` は現行 CLI watch と helper には存在するが、GUI と母体相当の操作面には対応概念がない。
- `iterations` は changer としての通常利用では直感的でなく、回数制限付きの実行確認やテスト補助寄りの性格が強い。
- 現行の `watch` は filesystem event 監視ではなく、一定間隔で画像候補を巡回して次画像を選ぶ changer / rotation 的な継続実行である。
- そのため public surface では `watch` を主語にせず、`スライドショー` を正系語として扱う。
- watch 関連の用語として `interval`, `cycle`, `サイクル` が併存しており、特に watch 間隔と 1 回分処理の単位が文脈ごとに揺れている。
- 日本語の正系語では `周期` を極力使わず、時間量は `間隔`、1 回分処理は `サイクル` を優先する。
- 以上を踏まえ、watch mode と `iterations` は、GUI へ露出するか、CLI 専用概念として残すか、あるいは削除・整理するかを残論点として扱う。

### 7. CLI `compute-placement` の棚卸候補

- `compute-placement` は command 名としては残っているが、現行 CLI では受理した値を表示するだけで、placement 計算機能を提供していない。
- core 層には `compute_placement(...)` 関数が存在する一方、CLI command はその実体へ接続されていない。
- 用途が不明瞭で常用 command surface として未成立であるため、WS5 では廃止候補として扱う。

### 8. CLI surface 全体の棚卸候補

- CLI には、command 名や option 名は存在するが、実際の効き方や役割が弱い項目がまだ残っている可能性がある。
- 直近で見えている代表例は、`compute-placement` の未接続、watch の `mode` / `iterations` の CLI 偏在、CLI 実行メッセージ粒度の名称と実態のずれである。
- `optimize` 側でも `scaling` や `random-seed` は help 上で「効きが限定的」とされており、surface の強さに対して実体が弱い可能性がある。
- core 側でも `PlacementResult.to_dict()` のように、実装には残っているが現行の主要 surface では使い所が弱く見える helper があるため、WS5 で整理候補として棚卸対象に含める。
- Linux plugin の apply fallback (`xfconf-query`, `gsettings`, `feh`) は履歴上の説明と現行 dry-run / 実適用の実装がずれて見えるため、WS5 で command surface と正本記述の両方を棚卸対象とする。
- WS5 では CLI command / option を「主力として成立しているもの」「存在はするが未成立または効きが弱いもの」「削除または整理候補」に棚卸しする。

### 9. 設定ファイル名の整理方針

- 現行の設定ファイル名は `harite-preferences.json` で、foundation / core などの正本にもこの名称で記載されている。
- ただし媒体上のファイル名としては `preferences` が残っており、`prefs` をやめた後の残滓として不一致感がある。
- `設定` / `設定ファイル` という現在の呼び方に揃えるため、ファイル名も含めて命名を見直す。
- したがって `harite-preferences.json` は、`preferences` 残滓を閉じる rename 対象として扱う。
- 同様に、`config.py`, `preferences.py` のような実装モジュール名も、文書語固定後の naming へ合わせて rename 対象に含める。

### 10. `config` と `設定` の用語整理方針

- GUI / foundation / core の正本では `設定` / `設定ファイル` を主語にしている一方、CLI help と CLI 実装では `config` が前面に出ている。
- 母体側では `config` で揃っていた認識に対して、現行文書群では `設定` と `config` が混在しており、呼び方の統一が崩れている。
- そのため WS5 では、文書と user-facing surface では `設定` を軸に固定する。
- `config` は help / option 名 / module 名のうち、設定ファイル入出力や形式名に関わる箇所へ用途限定する。

## 初動タスク

1. 判断枠を固定し、各論点を `積極維持 / rename・cleanup / 削除・縮退候補` に粗く分類する。
2. watch 系を最優先に、命名、単位語、観測面、CLI / GUI 差、未成立 surface をまとめて棚卸しする。
3. CLI の未成立 surface を洗い出し、主力・弱い surface・廃止候補を切り分ける。
4. 設定 / config / preferences 系と apply target / monitor map 系を、正本・実装・tests を跨いで整理する。
5. 以上の判断を正本先行の変更順へ落とし、post-`1.0.0` cleanup の入口となる最小構造を定める。

## 完了条件

- internal issue inventory の枠組みが説明可能になっている。
- `1.0.0` gate の外に置く理由が説明可能になっている。
- cleanup / rename の受け皿として overview を置く理由が説明可能になっている。
- Workstream 1・3・4・6 と混線せずに次段へ送れる状態になっている。

# GUI Phase 7 計画（プロダクト整合性の再設計フェーズ）

最終更新: 2026-04-18

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
- 確認済みの具体例として、XFCE 2 画面（2048x1280 x 2、連続 4096x1280）で `700x1244.jpg` と `700x394.jpg` から作った 4096x1280 の optimize 結果を `Default` で適用すると、各 2048x1280 画面へ同一ワイド画像を当てに行くような圧縮表示に見える。一方、同じ画像を XFCE で手動選択し、日本語 UI 上の「縦横比を維持せず全画面化」として表示した場合も同じ見た目になるため、単純な内部不整合ではなく、plugin 実装部が持つ通常 apply 経路の意味と GUI の `Default` 語彙の整合問題である可能性が高い。`Auto-split` は想定どおりに見える。
- CLI 側には `apply --do-it` と `watch --dry-run/--do-it` が残っている。
- core / CLI には margin 情報埋め込みや monitor split など、GUI 未露出の機能が既に存在する。
- watch は CLI が loop / apply / failure-continue を持ち、GUI は source dir / interval / start-stop 表示の前段だけを持つ。

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
  - デスクトップ貼り付け結果で疑義の出た組み合わせを、語彙差の問題として扱うのか、実処理整合性の問題として扱うのか
  - 4096x1280 の optimize 結果に対して `Default` を選んだとき、それは「plugin 実装部の通常 apply 経路へ 1 枚の最終成果物をそのまま渡す」意味なのか、「現在の画面構成に応じて暗黙分割される」期待を伴っていたのか
  - XFCE 手動設定の「縦横比を維持せず全画面化」と一致する現象を、GUI 側でどう説明し、どこまで mode 名や補助文言で予防するか
  - `Default` という語が、user default / OS default / plugin default のどれを指すのか曖昧になっていないか
- 成果物:
  - 操作語彙ポリシーメモ
  - CLI / GUI の命名ルール案

### 3. watch の責務再定義

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
  - GUI に持ち込むと意味が増える機能か
  - CLI 専用のままでもよい機能か
  - 既存 UI 構造へ自然に乗るか
  - Phase8 へ送る価値があるか
- 成果物:
  - GUI 候補機能リスト
  - Phase8 候補バックログの素案

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

## 初期棚卸しのたたき台

| 項目 | core | CLI | GUI | 暫定評価 | Phase7 で決めること |
| --- | --- | --- | --- | --- | --- |
| `apply` 即時実行 | plugin apply は可能 | dry-run 既定 + `--do-it` | 即時実行 | 語彙差が大きい | 同義化するか、意図差として固定するか |
| `Apply` 結果の疑義 | plugin / split / paste 条件に依存し得る | 組み合わせにより意味差が出る可能性 | 画面上は `Default` / `Auto-split` の 2 択 | Phase6 で具体例を確認済み | XFCE 2 画面 4096x1280 optimize 結果を `Default` 適用したときの圧縮表示が、plugin 実装部の通常 apply どおりか、語彙誤読か、内部処理不整合かを切り分ける |
| `watch` 継続ループ | watch runner あり | 実装済み | 未接続 | CLI 先行 | GUI front-end 化か、別仕様か |
| watch failure-continue | plugin apply と組み合わせ可 | 実装済み | 未接続 | CLI 先行 | GUI に必要か |
| `embed-text` / margin info | 実装済み | 実装済み | 未露出 | GUI 候補の抜け | Phase8 候補化するか |
| per-monitor apply / auto-split | 実装済み | 実装済み | 未露出 | CLI 先行 | GUI に出す意味を再判定 |
| `Color` | core 根拠なし | なし | deferred | GUI 側 only | 維持 / 削除 / Phase8 候補 |

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

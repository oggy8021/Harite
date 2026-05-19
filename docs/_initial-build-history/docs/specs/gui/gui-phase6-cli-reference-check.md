# GUI Phase 6 CLI 正本確認メモ

最終更新: 2026-04-16

## 目的

- GUI の責務整理より先に、CLI の `apply` / `watch` / plugin apply を正本として確認する。
- 現仕様と現実装のズレを先に見つけ、GUI が誤った前提に乗らないようにする。
- Phase6 の `Apply` 議論を、GUI の見た目や暫定配置ではなく CLI 正本から始める。
- ここでいう CLI への疑いとは、GUI の外で 0.1.2 release までに仕上げてきたコマンドライン版について、各オプションが本当に対応機能を実現しているか、不一致がないかを確認することを指す。

## 一次参照

- [src/harite/cli.py](src/harite/cli.py)
- [src/harite/watch.py](src/harite/watch.py)
- [src/harite/plugins.py](src/harite/plugins.py)
- [docs/specs/watch/harite-watch-minimum-spec.md](docs/specs/watch/harite-watch-minimum-spec.md)
- [docs/manual-validation-gate.md](docs/manual-validation-gate.md)

## 結論サマリ

- CLI の `apply` は既に正本として成立している。
- CLI の `watch` は GUI より進んでおり、plugin apply、継続実行、失敗継続ポリシーまで持っている。
- GUI の watch は CLI watch の「source dir 選択」と「初回選択結果表示」だけを先に取り込んだ状態であり、CLI watch の apply / 継続実行責務とは未接続である。
- Decision 1 により、`do-it` は不要とし、`Apply` は旧プログラムどおり即時変更前提へ戻す。
- ただし Phase6 の CLI 正本確認は「現時点で問題なしと断定する」ことではない。0.1.2 までに積み上げた CLI の各オプションについて、期待機能と実装が本当に一致しているかを再点検する必要がある。

## 現仕様と現実装

### 1. `apply` コマンド

#### 現仕様

- 現 CLI 実装では `apply` に dry-run / `--do-it` がある。
- plugin を介して OS ごとの壁紙変更を行う。
- `--per-monitor` / `--left-file` / `--right-file` / `--auto-split` によりモニタ別適用も扱う。

#### 現実装

- [src/harite/cli.py](src/harite/cli.py#L370) の `apply()` は `do_it: bool = False` を受け、plugin には `dry_run=not do_it` を渡す。
- 単一ファイルだけでなく、`dict` による per-monitor mapping も plugin へ渡せる。
- 失敗時は exit code `3`、unknown plugin 等の入力不正は exit code `2` で終了する。

#### GUI への含意

- Decision 1 により、GUI は `Apply` を即時実行前提で扱う。
- したがって GUI 側では `Apply dry-run` と `Apply do-it` の二段表示を正本にしない。
- CLI 側に残る dry-run / `--do-it` は、Phase6 で整理対象とみなす。

### 2. plugin apply

#### 現仕様

- plugin は `apply(path, dry_run=True)` の責務を持つ。
- 現実装では `dry_run=False` のときだけ実際の OS 変更を試みる。

#### 現実装

- [src/harite/plugins.py](src/harite/plugins.py#L444) に registry があり、`windows` / `macos` / `linux` plugin を返す。
- Windows plugin は `SystemParametersInfoW`、macOS plugin は `osascript`、Linux plugin は `xfconf-query` / `gsettings` / `feh` を試行する。
- Linux plugin は dry-run 時、候補コマンドのシミュレーションだけでも success を返し得る。
- Linux plugin は per-monitor mapping `dict` を受け取れる。

#### GUI への含意

- `Apply` を即時実行で扱うとしても、実際の副作用境界が plugin apply である点は変わらない。
- watch の「実切替」も、独自ロジックではなく plugin apply の繰り返しとして扱うのが自然である。

### 3. `watch` コマンド

#### 現仕様

- [docs/specs/watch/harite-watch-minimum-spec.md](docs/specs/watch/harite-watch-minimum-spec.md) では、`watch` は CLI 単体の最小仕様として定義されている。
- `--iterations`、`sequential/random`、失敗継続、Ctrl+C 正常終了が定義済み。
- 非対象として「GUI からの watch 制御」が明記されている。

#### 現実装

- [src/harite/cli.py](src/harite/cli.py#L435) の `watch()` は、入力検証後に [src/harite/watch.py](src/harite/watch.py) の `run_watch_cycles()` を使う。
- dry-run では選択ログのみ、`--do-it` では plugin apply を毎サイクル呼ぶ。
- plugin が `False` を返しても例外を投げても watch は継続する。
- `log-level=normal/detail` も実装済み。

#### GUI への含意

- GUI watch は CLI watch のサブセットと考えるべきで、先に GUI 独自仕様を増やすべきではない。
- GUI watch に実切替を入れるなら、CLI watch の apply / 継続 / 失敗継続ポリシーを再利用する方向が望ましい。

### 4. `do-it` の扱い

#### 現仕様

- 現 CLI 実装には `--do-it` がある。
- ただし Decision 1 により、Phase6 の方針としては `do-it` を不要とみなす。

#### 現実装

- `apply` では `--do-it` 実装済み。
- `watch` でも `--dry-run/--do-it` 切替が実装済み。
- GUI では `Apply do-it` は長く planned 扱いで、watch 実切替にも接続されていない。

#### Phase6 への含意

- `do-it` は追加実装候補ではなく、削減・整理対象として扱う。
- GUI では `Apply` を即時実行前提に戻す。
- CLI 側も 2 段階 apply が妥当かを再整理対象に含める。

## 差分一覧

| 論点 | CLI 正本 | GUI 現状 | 差分評価 | Phase6 での扱い |
| --- | --- | --- | --- | --- |
| Apply dry-run | 実装済み | 実装済み | 小 | 維持 |
| Apply do-it | 実装済み | planned | 大 | 削減候補 |
| Watch dry-run | 実装済み | 状態表示のみ | 大 | 要整理 |
| Watch do-it | 実装済み | 未接続 | 大 | 削減候補 |
| Watch 継続ループ | 実装済み | 未接続 | 大 | 要整理 |
| Watch 失敗継続 | 実装済み | 未接続 | 大 | CLI 正本を再利用検討 |
| per-monitor apply | 実装済み | GUI 未露出 | 中 | GUI へ出すか未定 |
| `do-it` 概念 | docs / CLI で概念あり | GUI 未整理 | 大 | Phase6 で整理対象 |

## CLI 疑義の見方

- 疑う対象は CLI の存在そのものではなく、オプションと実機能の対応である。
- 具体的には、help や docs に見えているオプションが、実際にその意味どおりの機能を提供しているかを確認する。
- 「面白い機能が入った」ことと「既存の機能が正しく残っている」ことは別問題として扱う。
- GUI Phase6 では、CLI 正本確認を通じて「GUI が依存してよい CLI 機能」と「CLI 自体が再点検対象の機能」を切り分ける。

## 判断メモ

- GUI watch に実切替を入れるかどうかは、CLI watch を GUI から呼ぶのか、GUI が独自に watch orchestration を持つのかで大きく変わる。
- 現時点では GUI が独自に watch orchestration を持つ理由は薄い。既に CLI が loop / mode / error handling を持っているからである。
- `do-it` は増やす対象ではなく、旧 `Apply` の即時性へ戻すうえで整理対象とみなす。
- `Prefs` や `Color` と違い、`do-it` は一度入り込むと CLI / GUI 両方の操作モデルを複雑にする。

## Phase6 で先に決めること

1. CLI 側に残る `--do-it` を Phase6 でどう整理するか。
2. GUI watch は CLI watch の front-end として扱うのか。
3. `Apply` を即時実行前提に戻したとき、watch 実切替を同じ apply 責務の延長として扱うのか。
4. 下部コントロール群の中で `Apply` をどの位置と語彙で見せるのか。

## 次アクション

1. 本ファイルを T6-2 の初版として固定する。
2. T6-3 で下部コントロール責務表を作成する。
3. T6-3 では `Prefs` / `Color` / `Save Confirm` / `Save Cancel` / `Save` / `Optimize` / `Apply` を一括で再判断する。

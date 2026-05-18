# Harite Project Initial Build Reformation WS1 Cleanup And Owner Readiness

最終更新: 2026-05-18

## 位置づけ

- 本書は [docs/reformation/harite-project-initial-build-reformation.md](docs/reformation/harite-project-initial-build-reformation.md) の Workstream 1 を具体化する子文書である。
- 主題は、初期製造を `1.0.0` 前に閉じるための仕上げ、掃除、code residue cleanup、owner 判定前整理である。
- docs 再編や仕様書本文の執筆は本書の主責務ではない。

## この stream で固定すること

- 出荷前に消すもの、隠すもの、残すものを区別する。
- 出荷前の起動ノイズと code residue の境界を明示する。
- owner 判定前に必要な最小確認を定める。
- 別紙の大部 checklist を増やさず、この WS 文書と chat 上の判断記録で回せる形にする。

## 対象

- 起動時メッセージ
- 出荷時に不要な debug / 暫定表示
- `1.0.0` 前に落とすべき code residue / skeleton / placeholder / legacy alias
- owner が release 判定前に確認する対象と残論点

## 非対象

- packaging / resource / license 成立
- version / CHANGELOG / release notes / 配布説明の整合
- docs 全体の情報設計
- 常設仕様書の章立て設計
- post-1.0.0 機能棚卸し

## 現時点の論点

### 1. 起動時メッセージをどう扱うか

- 削除でよいもの
- 開発時のみ見せるもの
- 通常利用でも残すべきもの

### 2. owner 判定前に何を残すか

- owner が実施するテスト・実機確認・Git 操作の対象を過不足なく見える形にする。
- agent 側で不足確認を列挙できる状態にする。
- packaging / release 整合は [docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) へ分離する。

### 3. `1.0.0` 前に消す code residue をどこまで扱うか

- docs 再編や仕様書化ではなく、製品を閉じる前の掃除として扱う。
- 「敢えて残してきたが、今の current Harite には不要寄り」のものは WS1 で扱う。
- WS3 / WS4 へ送らず、`1.0.0` 前に消す・残すを明示する。
- 利用者根拠のない互換層への退避は採らない。不要な legacy / residue は、互換のために温存するのではなく削除前提で扱う。

## 現時点の観測

### 1. 起動時メッセージの主要発生箇所

- [src/harite/gui/app.py](src/harite/gui/app.py) と [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の通常起動に関わる `print(...)` は削除済みである。
- これにより、release build 前提では GUI 起動時の常設 stdout ノイズは解消済みとみなしてよい。
- 一方で `MainWindow` の通常状態通知は status row / feedback として内部状態へ寄せており、WS1 では「CLI/stdout に出す必要があるもの」と「GUI 内 state 表示で足りるもの」を分ける必要がある。

#### 棚卸し対象一覧

`app.py` の出力:

- 現在、常設の `print(...)` は残っていない。

`main_window.py` の出力:

- 現在、常設の `print(...)` は残っていない。

#### 暫定分類

- 出荷前に削除候補:
  - 現時点の主対象は解消済みであり、`show()` 末尾の skeleton/debug 出力 5 件、`app.py` の `... ready` 系 3 件、`... skipped` 系 5 件は削除済み。
- 条件付き保持候補:
  - 現時点では常設 stdout 出力として残している項目はない。

### 2. owner 判定前整理の現状

- 起動ノイズ整理と code residue cleanup の判断は、WS1 本文と [docs/reformation/harite-project-initial-build-reformation-ws1-code-residue-inventory.md](docs/reformation/harite-project-initial-build-reformation-ws1-code-residue-inventory.md) へ集約済みである。
- packaging / resource / release 整合は、話題が異なるため [docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) へ分離した。
- したがって WS1 の主残論点は、「何を出荷前 cleanup とみなすか」と「owner 判定前に何を見える状態へしておくか」に寄っている。

### 3. code residue の現状観測

- marker ベース検索では、当初 `skeleton` / `placeholder` / `legacy` / `WallPosit` / `Debug:` 系の名残が複数箇所に見えていたが、product surface に近いものは段階的に解消している。
- この中には「単なる docstring 上の古語」と「実際の product surface に見えてしまう残骸」が混在しているため、WS1 では後者を優先して消す。

#### 現時点の候補

- product surface に見えるため優先度が高い候補:
  - 現時点では、product surface に直接見える大きな residue はおおむね一巡した。
- product の読みを濁すため次点で整理したい候補:
  - legacy Glade / fallback / debug overlay のように、実装安全策と残骸が近接している層
- すぐ消すとは限らない候補:
  - legacy Glade 互換や debug overlay のように、runtime safety / 開発補助として役割が残っているもの

#### 解消済み

- 解消済みの詳細一覧、総合見解、件数評価、ファイル別内訳は [docs/reformation/harite-project-initial-build-reformation-ws1-code-residue-inventory.md](docs/reformation/harite-project-initial-build-reformation-ws1-code-residue-inventory.md) に切り出した。
- 別紙では、対象 53 件を 19 file reference 単位に再編し、source file ごとの変更内容と関連 test 増分を追えるようにした。
- 記録上の中心は、[src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py)、[src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py)、[src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py](src/harite/gui/adapters/gtk_runtime_file_dialog_flow.py)、[src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) の 4 file group である。
- WS1 本文では、「product surface に見える residue を落とす」「legacy contract へ戻さない」「unexpected runtime failure を握り潰さない」という判断だけを正本として維持する。

#### 現時点の扱い方針

- 現時点の候補は、原則として `1.0.0` 前に削除対象として扱う。
- 「互換層へ閉じ込める」は、実利用者や保守上の必然が確認できる場合だけに限る。
- 現時点ではその根拠が見えていないため、残っている residue 候補も温存ではなく削除側で読む。
- ただし WS1 closing の停止条件は「候補を 0 件にすること」ではなく、残る broad catch 候補それぞれについて `intentional wrapper` か `要修正` かを説明可能にすることとする。
- 2026-05-18 時点で GUI 配下の broad catch 候補は 7 か所まで減っており、[src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) と [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の status / feedback wrapper に集中している。

#### 次の主候補

- active code よりも test / comment / historical wording 側に残る legacy 前提を落とす層
- runtime safety と residue が近接していて、削除境界を切りたい層
- preview / tray adapter 以外に残る capability fallback や historical wording が、本当に runtime safety として必要かを切り分ける層

## `1.0.0` 少数 gate

### Gate 1. 起動ノイズと暫定表示の整理

- 通常利用の GUI 起動で、skeleton/debug 出力が stdout に残っていない。
- `ready` 系の起動メッセージは release build 前提では外れている。
- 例外的に残す診断がある場合も、通常利用時の常設ノイズではなく、必要性を説明できる。
- product surface に見える code residue も、`1.0.0` 前に整理対象へ含める。
- 証跡の置き場:
  - 本文中の整理判断
  - 必要なら chat 上の owner/agent 判断ログ

- Gate 2 と Gate 3 は、話題が異なるため [docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) へ分離した。

### Gate 4. owner 判定に必要な最小確認が揃っている

- owner が実施するテスト・実機確認・Git 操作の対象が過不足なく見えている。
- agent 側では、release 判定前に不足している確認項目を列挙できる。
- 判定に必要な残論点が、WS3 以降の論点と混線していない。
- 証跡の置き場:
  - この WS1 文書
  - 関連する release / manual validation 文書
  - chat 上の最終判断ログ

## WS1 の暫定判断

- 起動時メッセージは、まず [src/harite/gui/app.py](src/harite/gui/app.py) の `print(...)` 群と [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) 末尾の debug 出力を出荷前整理の一次対象とみなす。
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の `show()` 末尾出力は削除済みであり、Gate 1 の一段目は通過済みとみなしてよい。
- [src/harite/gui/app.py](src/harite/gui/app.py) の `ready` 系、`skipped` 系、window presentation skipped は stdout から外したため、Gate 1 の常設起動ノイズ整理は一旦完了扱いでよい。
- `1.0.0` 判定は、WS1 の Gate 1 / Gate 4 と、[docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) の Gate 2 / Gate 3 を合わせて見る。
- code residue の扱いは WS3 / WS4 へ送らず、WS1 の掃除対象として `1.0.0` 前に消す前提で扱う。
- code residue の扱いは「削除」優先であり、利用者不在の互換層温存は採らない。
- [src/harite/gui/app.py](src/harite/gui/app.py) の entrypoint dispatch 接続 fallback は、`ImportError` / `TypeError` だけを非致命 fallback に残す current contract へ揃えたため、WS1 では residual broad catch 候補から外してよい。
- [src/harite/gui/adapters/gtk_runtime_settings_dialogs.py](src/harite/gui/adapters/gtk_runtime_settings_dialogs.py) の settings/color/about open helper も、getter / notice build の expected failure だけを feedback に載せる current contract へ揃えたため、residual broad catch 候補から外してよい。
- 残る 7 か所は plugin apply や position/save feedback の wrapper であり、現時点では「利用者操作を即 crash させず status / feedback に畳む intentional wrapper」候補として読むのが第一候補である。
- 2026-05-18 時点の暫定分類では、残る 7 か所はすべて `intentional wrapper` 側へ置く。内訳は [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) の plugin apply / watch apply 2 か所と、[src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py) の position / save feedback 5 か所である。
- これらは既存回帰でも、apply 失敗時に `status_message` / `last_error` へ畳むこと、toggle/save 失敗時に `Position: error` / `SavePath: error` を出すことが固定されているため、WS1 では追加 narrow を必須条件にしない。
- よって現時点の `要修正` は 0 か所とし、WS1 closing は「残る 7 か所を intentional wrapper として説明可能にした」時点で満たす扱いとする。
- version / packaging / release 証跡の整理は [docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) へ委ねる。

## 当初タスク

1. [src/harite/gui/app.py](src/harite/gui/app.py) と [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py) に残る出荷前整理対象の `print(...)` を棚卸しする。
2. owner 判定前に必要な確認対象と残論点を列挙する。
3. `1.0.0` 判定に必要な Gate 1 / Gate 4 を、この WS 文書内で説明可能な形へ絞る。
4. Gate 2 / Gate 3 は [docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) へ分離する。

## 完了条件

- 出荷前に整理すべき表示と残す表示の境界が説明可能になっている。
- owner 判定前に必要な最小確認が説明可能になっている。
- WS1 が Gate 1 / Gate 4 を受ける文書として読める。
- Gate 2 / Gate 3 が [docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md](docs/reformation/harite-project-initial-build-reformation-ws2-packaging-release.md) と混線せず分離されている。
- 残る broad catch 候補に対して、`intentional wrapper` と `要修正` の分類根拠が示されている。
- Workstream 3-5 に属する論点と混線していない。

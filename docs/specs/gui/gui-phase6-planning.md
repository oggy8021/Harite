# GUI Phase 6 計画（言語モデル負債の改修フェーズ）

最終更新: 2026-04-16

## 位置づけ

- Phase5 は GUI 導線の復旧と暫定整形を優先し、P5-8 から P5-11 で Open / watch / Save の導線を段階復旧した。
- その結果、実用上の前進はあった一方で、見た目だけ通った判定、暫定 UI の残存、CLI/GUI 間の責務ずれ、glade 由来の構造負債が残っている。
- 初期製造時から P5-7 までが中途半端になった主因は、母体プログラム参照を十分に行わず、`docs/upstream-*` 系文書と glade を斜め読みレベルでしか正本として扱えなかった点にある。
- Phase6 は新機能追加ではなく、それらの言語モデル負債と暫定実装を整理し、GUI/CLI の正本を再一致させるフェーズとする。
- Phase7 は、Phase6 で基盤整理を終えた後の新機能フェーズとする。

## 目的

- 初期製造時から P5-7 までを含む GUI 判定のうち、見た目 pass と機能 pass の意味を再点検する。
- CLI 実装を正本として再確認し、GUI が誤った前提に乗っていないかを洗い直す。
- 下部コントロール群を中心に、`Prefs` / `Color` / `Save Confirm` / `Save Cancel` / `Save` / `Optimize` / `Apply` の責務を再定義する。
- glade 依存を repo から撤去する前提で、adapter 層と fallback backend の要否を再判断する。
- 最終的に「新規 GUI の標準形」に近い構造を Phase6 の出口として定義する。
- Phase7 へ新機能を送る前に、「コア機能はここでとどめを刺す」状態まで到達する。

## 非目的

- Phase6 中に新機能を増やすこと。
- `do-it` を実装ありきで進めること。
- 見た目の最終美化だけを単独目的にすること。
- 一度に GUI 全面を書き直すこと。

## 完了条件

- GUI 判定の再点検結果が文書化され、「再検証が必要な pass」と「維持してよい pass」が分離されている。
- CLI 正本と GUI 現実装の差分が列挙され、Phase6 で直すものと Phase7 へ送るものが分離されている。
- 下部コントロール群の残す/消す/後回しにする判断が確定している。
- glade を repo から撤去する方針と、その後に残す adapter 層 / fallback backend の扱いが判断できる材料が揃っている。
- `do-it` を採らず、`Apply` を即時実行として扱う前提が CLI / GUI の両方で整理されている。
- Phase7 へ入る前提として、「新規 GUI を最初から作るなら普通こう置く」という標準形に十分近づいたと説明できる。
- XFCE 実機で、間に合わせインターフェースではない GUI 機能込みの Harite sdist リリースを組める段階に到達している。

## フェーズ方針

- Phase6 は長期化を許容する。その代わり、新要素導入のために Phase6 と別の中間フェーズを増やさない。
- about / help 以外のコア機能は Phase6 で責務整理と実装方針を確定する。
- 先に抽象論へ飛ばず、現実装のどこが暫定かを具体物ベースで切り分ける。
- GUI だけでなく CLI を再読し、GUI 側だけを直して整合した気にならない。
- Phase6-7 境界の一つを「新規 GUI の標準形へどこまで戻せたか」に置く。
- アイコン表現や見た目の細かな記号設計は、Phase6 後半で扱う。
- 画面全体の性格は、Studio 的な制作画面より Commander / gamepad 的な操作面として読む。

## Workstream

### 1. ベースライン再点検

- 対象:
  - 初期製造時から P5-7 までの判定、特に「見た目は通ったが機能は暫定」の項目
  - Phase5 の pass 記録のうち、実装実態との差があり得る箇所
- 主要論点:
  - 母体プログラム参照不足により、上流由来の意味づけを取り違えた箇所がないか
  - どの pass が UI 状態表示ベースだったか
  - どの pass が副作用込みで確認されたか
  - どの項目が「planned のまま pass に見えていた」か
- 成果物:
  - 再点検リスト
  - 再検証が必要な項目一覧

### 2. CLI 正本確認

- 対象:
  - `apply`
  - `watch`
  - plugin apply
  - `--do-it`
- 主要論点:
  - CLI 0.1.2 release までに仕上げてきたコマンドライン版について、オプションに伴う機能実現に不一致がないか
  - CLI に面白い追加機能が入る過程で、潰れた機能や誤った機能がないか
  - GUI が CLI の誤解に乗っていないか
  - `watch` と `apply` の責務境界はどこか
- 成果物:
  - CLI 正本確認メモ
  - GUI への影響一覧

### 3. 下部コントロール群の責務整理

- 対象:
  - `Prefs`
  - `Color`
  - `Save Confirm`
  - `Save Cancel`
  - `Save`
  - `Optimize`
  - `Apply`
- 主要論点:
  - `Prefs` は本当に残すべきか、残すなら何を束ねるのか
  - `Color` はコア機能か、planned のまま退避すべきか
  - `Save Confirm` / `Save Cancel` は native chooser 導入後も必要か
  - `Save` / `Optimize` は下部コントロール群へ再配置すべきか
  - `Apply` を `Optimize` とどう見せ分けるか
- 成果物:
  - 下部コントロール責務表
  - 残す/消す/延期の判断表

### 4. レイアウト再定義

- 対象:
  - glade の hbox / vbox ベース配置との乖離
  - Phase5 で積み上がった間に合わせの位置決め
- 主要論点:
  - どこまで glade の位置再現を追うか
  - 何を「操作意図の再現」とみなし、何を「位置の忠実再現」とみなすか
  - 下部コントロール整理の結果をどうレイアウトへ反映するか
- 成果物:
  - 更新版レイアウト方針
  - 必要なら screen zone / control zone の再定義図

### 5. glade / adapter 再判断

- 対象:
  - glade 依存の残存箇所
  - `ui_adapter` と runtime backend の存在意義
- 主要論点:
  - glade は「参照専用 legacy 資産」として repo に残さず、Phase6 のうちに撤去前提で進めてよいか
  - adapter 層は責務分離に寄与しているか、それとも暫定互換層として複雑化要因になっているか
  - controller / view / backend の境界を引き直す必要があるか
- 成果物:
  - glade 撤去方針
  - adapter 層の維持/縮退/撤去判断メモ

## 優先順

1. ベースライン再点検
2. CLI 正本確認
3. 下部コントロール群の責務整理
4. レイアウト再定義
5. glade / adapter 再判断

上から順に進める。後段は前段の判断結果を前提にする。

## `Apply` の扱い

- Decision 1 により、`do-it` は不要とする。
- 旧プログラムどおり、`Apply` は即時変更でよい前提を採る。
- CLI / GUI の両方で、`Apply` を 2 段階に分ける方向は採らない。
- Phase6 では `Apply` を安全導線として細分化するより、`Apply` の責務と配置を単純化する。

## 論点メモ

- `Prefs` 未実装をどう扱うか
- `Color` planned をコアから外すか
- `Save Confirm` / `Save Cancel` を削除して chooser 主体に寄せるか
- `Save` / `Optimize` / `Apply` を下部コントロール帯へ戻すか
- glade hbox 再現をどの粒度で追うか
- glade 実ファイルを repo から消した後、既存 docs 参照だけで足りるか
- GUI が CLI より先に概念を生やしていないか

## Phase6 の出口

- Phase6 でコア機能の責務と構造を確定させる。
- Phase6 の出口では、glade / adapter / fallback backend に引きずられた構造ではなく、「新規 GUI の標準形」に近いと説明できる状態を要求する。
- Phase6 の出口では、XFCE 実機で「間に合わせではない」GUI を含む Harite の sdist リリースを現実的に組める状態を要求する。
- ただし「間に合わせではない」の具体条件は、Phase6 後半の構造整理と実装見通しを踏まえて定義する。
- Phase7 では、それを前提に新機能へ入る。
- Phase7 に送ってよいのは新機能そのものだけで、Phase5/6 由来の構造負債は極力持ち越さない。

## Phase6-7 境界

- Phase6 の責務は、既存 GUI を新機能追加前の標準形へ戻すことにある。
- ここでいう標準形とは、古い signal を読んで変換してから新 signal へ流す多段 adapter を前提にせず、可能な限り単純な接続と責務境界で説明できる構造を指す。
- fallback backend も UI 本体ではなく、安全網としてだけ説明できるところまで落ちている必要がある。
- 加えて、XFCE 実機で「間に合わせではない」GUI 機能を含んだ Harite の sdist リリースを組める段階である必要がある。
- この「間に合わせではない」の具体定義は、Phase6 後半で固める。
- この条件を満たして初めて、Phase7 を新機能フェーズとして切り出す。

## 初動タスク

### T6-1. ベースライン再点検リスト作成

- 目的:
  - 初期製造時から P5-7 までを含む pass 記録の意味を再確認し、見た目 pass と機能 pass を分離する。
- 具体作業:
  - Phase5 tasklist と traceability を再読する。
  - `planned` のまま通っている、または副作用未確認の項目を抜き出す。
  - 「維持してよい pass」「再検証が必要な pass」「誤認 pass の疑い」に分類する。
- 完了条件:
  - 再点検対象一覧が 1 ファイルにまとまっている。
- 成果物:
  - [docs/specs/gui/gui-phase6-baseline-recheck.md](docs/specs/gui/gui-phase6-baseline-recheck.md)

### T6-2. CLI 正本確認メモ作成

- 目的:
  - GUI の議論より先に CLI / plugin apply / watch / `Apply` の正本を確認する。
- 具体作業:
  - `apply`、`watch`、plugin apply 経路を読み、現仕様と実装の差分を列挙する。
  - GUI が依存している前提と、CLI 側の本来責務を分離する。
- 完了条件:
  - GUI へ影響する CLI 差分一覧ができている。
- 成果物:
  - [docs/specs/gui/gui-phase6-cli-reference-check.md](docs/specs/gui/gui-phase6-cli-reference-check.md)

### T6-3. 下部コントロール責務表の作成

- 目的:
  - `Prefs`、`Color`、`Save Confirm`、`Save Cancel`、`Save`、`Optimize`、`Apply` の残す/消す/延期を判断できる状態にする。
- 具体作業:
  - 各コントロールの現状態、上流根拠、CLI 根拠、必要性、危険性を書く。
  - `Save Confirm` / `Save Cancel` の削除可否、`Apply` の即時実行前提をどこへ置くかを判断候補として並べる。
- 完了条件:
  - 下部コントロール責務表が完成している。
- 成果物:
  - [docs/specs/gui/gui-phase6-lower-controls-responsibility.md](docs/specs/gui/gui-phase6-lower-controls-responsibility.md)

### T6-4. レイアウト再定義メモ作成

- 目的:
  - glade hbox / vbox ベース配置をどこまで再現し、どこから操作意図優先に切り替えるかを定義する。
- 具体作業:
  - 現 GUI と glade の差分を zone 単位で比較する。
  - 下部コントロール責務整理の結果を配置案へ反映する。
- 完了条件:
  - 再定義後のレイアウト方針が文書化されている。
- 成果物:
  - [docs/specs/gui/gui-phase6-layout-redefinition.md](docs/specs/gui/gui-phase6-layout-redefinition.md)

### T6-5. glade / adapter 判断メモ作成

- 目的:
  - glade を repo から撤去する前提で、adapter 層と fallback backend の必要性を、責務整理後の構造として判断する。
- 具体作業:
  - glade 依存箇所と adapter 層の吸収責務を列挙する。
  - glade 撤去後に、既存 docs のどれを根拠として使い続けるかを確認する。
  - adapter / backend を中心に維持 / 縮退 / 撤去の比較を行う。
- 完了条件:
  - glade 撤去と adapter / backend 判断の材料が揃っている。
- 成果物:
  - [docs/specs/gui/gui-phase6-glade-adapter-judgement.md](docs/specs/gui/gui-phase6-glade-adapter-judgement.md)

## 着手順（実務）

1. T6-1 ベースライン再点検リスト作成
2. T6-2 CLI 正本確認メモ作成
3. T6-3 下部コントロール責務表の作成
4. T6-4 レイアウト再定義メモ作成
5. T6-5 glade / adapter 判断メモ作成

## 意思決定の挟み方

- Phase6 の文書群は、先にたたき台を並べ、その後に owner 意思決定を挟む前提で進める。
- したがって、各 T6 文書の初版は「決定」ではなく「判断材料の整備」である。
- owner 判断は、次の 3 回に分けて行うのが自然である。

### Decision 1. CLI / `do-it` 方針確認

タイミング:

- T6-2 完了後
- T6-3 着手前

決定結果:

1. `do-it` は不要とする。
2. CLI / GUI ともに `Apply` は即時実行前提とする。
3. watch の実切替も `do-it` 前提ではなく、必要なら `Apply` 責務の延長として整理する。

反映先:

- [docs/specs/gui/gui-phase6-cli-reference-check.md](docs/specs/gui/gui-phase6-cli-reference-check.md)
- 本 planning 文書

### Decision 2. 下部コントロール方針確認

タイミング:

- T6-3 完了後
- T6-4 確定前

決定結果:

1. `Prefs` は残す。CLI / GUI 間で共有する config の入口として意味がある。
2. `Color` は P6 軽減策として Phase7 へ送る。
3. `Save Confirm` / `Save Cancel` は全廃する。
4. `Save` は意味づけ自体を了解し、英語ラベルは `Save As` とする。配置は Flow / Header の右端など標準的な保存位置へ置く。
5. `Optimize` は残す。
6. `Apply` は残し、`Optimize` と隣接させて main tab 右下の主操作として扱う。

反映先:

- [docs/specs/gui/gui-phase6-lower-controls-responsibility.md](docs/specs/gui/gui-phase6-lower-controls-responsibility.md)
- [docs/specs/gui/gui-phase6-layout-redefinition.md](docs/specs/gui/gui-phase6-layout-redefinition.md)
- 本 planning 文書

### Decision 3. 構造方針確認

タイミング:

- T6-4 と T6-5 の初版が揃った後
- 実装着手前

決めること:

1. zone 構成の方向を採るか。
2. glade を Phase6 のうちに repo から撤去する前提でよいか。
3. glade 撤去後、既存 docs 参照と母体プログラム参照を前提にして、「新規 GUI の標準形」に近づくよう、adapter / fallback backend をどこまで落とし、どこをより単純な直結へ寄せるか。
4. Phase6 で「新規 GUI の標準形」まで戻す範囲と、Phase7 へ送る範囲をどこで切るか。
5. XFCE 実機で GUI 機能込みの Harite sdist リリースを組める段階を、Phase6 完了条件に含めるか。
6. 「間に合わせではない GUI」の具体条件を、Phase6 後半でどう定義するか。
7. アイコン表現を既存 docs の記述も踏まえて、Phase6 後半でどう定義するか。

現時点の実質論点:

1. まず owner が決める本丸は zone 構成である。
2. adapter / fallback backend / Phase6 範囲は、その zone 判断に従属して詰める。
3. 「間に合わせではない GUI」の具体条件は Phase6 後半で詰める。

入力資料:

- [docs/specs/gui/gui-phase6-layout-redefinition.md](docs/specs/gui/gui-phase6-layout-redefinition.md)
- T6-5 glade / adapter 判断メモ

実施形態:

- 私が比較表と推奨案を出す。
- owner は「案Aベース」「案Bで一部採用」のように方針を返す。
- その返答をもって Phase6 の実装対象を確定する。

owner 返答テンプレート（簡略版）:

1. zone はどの案を採るか
2. `Prefs` をどこへ置くか
3. `Watch` を独立 zone にするか、別 tab にするか

## 返答形式の想定

- 最短では、番号だけで十分である。
- 例:
  - `Decision 1 は 2`
  - `Decision 2 は Prefs 残す、Color Phase7、Save Confirm/Cancel 全廃`
  - `Decision 3 は案Bベース、adapter はさらに落とす、backend は安全網まで、XFCEでsdistを切れる段階までをP6に含める`
- zone だけ先に返す場合の例:
  - `Decision 3 は Header共通、Prefs は Secondary、Save は右上系の標準位置、Optimize/Apply は右下で隣接、Watch は別tab`
- 細かい条件がある場合だけ、補足を 1-3 行で付ける。

## 判断ゲート

- Gate A:
  - T6-1 完了までは、Phase5 の pass 記録を前提事実として固定しない。
- Gate B:
  - T6-2 完了までは、`Apply` の即時実行前提を CLI / GUI のどちらに寄せるか決めない。
- Gate C:
  - T6-3 完了までは、下部コントロールの削除/再配置を確定しない。
- Gate D:
  - T6-4 と T6-5 完了までは、glade 撤去や adapter 廃止を実装着手しない。

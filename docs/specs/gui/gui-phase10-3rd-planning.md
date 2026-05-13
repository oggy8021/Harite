# GUI Phase10 3rd Planning

最終更新: 2026-05-13

## 位置づけ

- 本書は Phase10 の 3rd planning として、Settings dialog の操作 semantics を独立論点で整理するメモである。
- [docs/specs/gui/gui-phase10-1st-planning.md](docs/specs/gui/gui-phase10-1st-planning.md) では起動導線を扱い、[docs/specs/gui/gui-phase10-2nd-planning.md](docs/specs/gui/gui-phase10-2nd-planning.md) では visual aid / message surface を扱った。
- 本書では、それらとは別に、Settings dialog の `Apply / Save / Close` をどう扱うべきかと、設定読込を dialog action row に置かない前提で何が自然かを扱う。
- ただし dialog の message surface については、2nd planning と Color dialog の実装・実観察で既に固定した前提があるため、本書ではその上に Settings dialog の action semantics を積む。
- icon library の採否や比較は、本書では扱わず Phase10 4th planning へ送る。

## 既決定事項

- dialog 内で直せる corrective error は、まず dialog 内短命 notice で閉じ、Main Window 最下部との往復は避ける。
- 本書でいう `最下段` は content area ではなく surface 全体の最下段を指し、dialog では action row より下を正とする。
- dialog 内 notice は、自前で制御する dialog では surface 全体の最下段専用エリアに置く。
- dialog 内 notice の文言は、surface 最下段 row の左端から読み始められる配置を正とし、右寄せや中央寄せを正としない。
- dialog 内では、現在状態を示す state row と、短命 notice を出す row を分離して持つ。
- Color dialog はこの規約に従って `picker 面 / Hex 入力 / 現在選択色 row / notice 専用最下段 row` の構成へ到達しており、Settings dialog はこれを近い比較基準とする。
- Settings dialog の state row / notice row も、昨晩到達した Color dialog の構成を踏襲する。
- 設定読込は Settings dialog の action row に `Load` として置かず、起動時に設定ファイルがあれば読む、なければ読まないまま開始し、必要時に新規作成する前提とする。
- CUI と GUI で設定運用差が残ることは、この planning の主要制約として扱わない。差分責任は利用者側で負う前提とする。
- `OK` は `Apply` 相当として扱い、dialog の編集中内容を起動中の有効メモリへ反映して閉じる。
- `Save` は永続化専用とし、Main Window の `Save As` に倣って dialog 本文の右上部寄りに置く。
- action row は `OK / Cancel` を標準的な並べ方で持ち、`Cancel` は「何も反映せず戻る」役割を担う。

## 現在地

- current Settings dialog は custom editor dialog であり、native chooser ではない。
- 一方、Save As や一部 dialog は native GTK chooser を使い得るが、Settings dialog 自体は custom semantics を明示的に持てる。
- Color dialog は custom surface 基準へ寄せることで、picker 面を保ちながら state row と notice row の分離まで到達した。
- このため Settings dialog も、「native らしさ」よりも「何を押すと何が起きるか」と「どこに何の message が出るか」を優先してよい。

## 今回 reopen しない点

- dialog local corrective error を dialog 最下段 notice へ閉じる方針そのものは reopen しない。
- state row と notice row を分離する方針そのものは reopen しない。
- `最下段` を surface 全体の最下段と読むことは reopen しない。
- 本書で reopen するのは、Settings dialog の action row を `Apply / Save / Close` のまま持つべきか、その責務をどう整理するかである。

## 母体プログラム再観察結果

- 母体 `WallpaperOptimizer/Widget/SettingDialog.py` では、dialog 本体に `Load` は存在しない。
- 母体 Glade の action row は `Cancel / OK` の 2 ボタンだけである。
- 母体 dialog 本文には `Clear` と `Save` が別置きされている。
- 母体 `Save` は dialog を閉じず、その場で `.walloptrc` へ即ファイル書込する。
- 母体 `OK` は dialog 内容を caller へ返し、caller `WindowBase.btnSetting_clicked()` 側で current state へ反映する。
- 母体 `Cancel` は `(False, False, False)` を返し、caller 側で current state を更新しない。
- したがって母体 semantics は「`Load` なし」「body-side `Save` と action-row `OK/Cancel` の併存」であり、Harite 側の比較候補はこの差分を意識して読む必要がある。

## 問題の見立て

### 1. `Close` は責務が弱い

- `Close` は設定反映もファイル操作も持たず、単に dialog を閉じるだけである。
- その役割は右肩の `×` と重複しており、action row 上の常設ボタンとしては弱い。
- よって `Close` は削除候補とする。

### 2. `Save` と `Apply` の責務分離に違和感がある

- 一般的な editor / settings UI では、保存がそのまま反映に近い挙動へ見えることが多い。
- ただし owner 判断では、ここは `OK=Apply`、`Save=永続化` の分離を維持する。
- 母体でも `Save` と `OK` は分かれており、`Save` は file write、`OK` は current state 反映として役割が分かれていた。
- したがって本段の論点は「分離をやめるか」ではなく、「分離した責務をどう自然に見せるか」へ移る。

### 3. `Load` は dialog action row に置かない方がよい

- 設定読込は起動時に自動で行い、読める設定がなければそのまま開始し、必要時に新規作成する方が筋が良い。
- したがって `Load` を dialog action row に常設する必然はない。
- CUI と GUI の設定運用差は残り得るが、ここでは button semantics を優先し、その差分は利用者責任として扱う。

### 4. `Cancel` は明示価値がある

- 他の面で native dialog が `Cancel` を持つなら、Settings dialog にも「何も反映せず戻る」動作を明示する価値がある。
- `×` と同じ結果でも、action row 上の `Cancel` は役割が分かりやすい。
- 母体でも action row は `Cancel / OK` で構成されており、`Cancel` は upstream 整合のある候補である。
- owner 判断としても、`Cancel` は action row に残す。

### 5. action semantics と message surface を混線させない方がよい

- 3rd planning では action row の責務整理が本題だが、Settings dialog 側の notice surface が未整理だと、失敗時文言をどこに出すかの都合で button semantics までぶれやすい。
- 既決定事項として、state row と notice row は分離し、corrective error は notice 専用最下段 row に閉じる前提で進める方が論点を減らせる。
- したがって `Apply` / `Load` / `Save` / `Cancel` の比較は、message surface 未確定のままではなく、dialog 最下段 notice を持つ前提で読む。

## 比較候補

### 母体準拠の基準形

- action row: `OK / Cancel`
- body-side secondary action: `Save`、必要なら `Clear`
- `Save`: dialog を閉じずに設定ファイルへ書く
- `OK`: dialog 内容を current session へ反映して閉じる
- `Cancel`: current session を変えずに閉じる

読み方:

- これは Harite がそのまま再現すべき確定案ではなく、母体が実際にどう責務を分けていたかの基準形である。
- Harite ではこの基準形を土台にしつつ、`Save` を本文右上部へ寄せ、action row は `OK / Cancel` の標準配置へ揃える差分を採る。

### 採用方針

- action row: `OK / Cancel`
- `OK`: `Apply` 相当。dialog 内容を起動中の有効メモリへ反映して閉じる。
- `Cancel`: 何も反映せず閉じる。
- `Save`: 永続化専用。dialog 本文の右上部に置き、現在内容を設定ファイルへ書く。

利点:

- 母体の `OK / Cancel` と整合しつつ、Harite 側で `Apply` 語を action row から外せる。
- `Save` を永続化専用の本文側操作へ寄せることで、action row の責務が dialog の確定/破棄に揃う。
- Main Window の `Save As` と同様に、file operation を本文側の独立操作として読ませやすい。

懸念:

- `OK=Apply` と `Save=永続化` の二系統を利用者へ短く理解させる必要がある。
- 本文右上部の `Save` を、単なる補助操作ではなく独立責務として見せる配置整理が必要である。

## 現時点の暫定落としどころ

- owner 判断として、Settings dialog の採用方針は `OK=Apply`、`Cancel` 維持、`Save=永続化専用` とする。
- `Load` は dialog に置かないことを既定とし、起動時自動読込・無ければ未読込開始・`OK` では自動新規作成しない・`Save` 時に必要なら新規作成する前提にする。
- 母体再観察の結果、upstream は `OK / Cancel` + body-side `Save` であり、Harite も大筋はこの責務分離に沿う。
- したがって以後の主論点は、「`Apply` 語を `OK` に吸収したうえで、`Save` を本文右上部の永続化操作としてどう自然に見せるか」である。
- したがって本書の目的は、直ちにラベルだけを置換することではなく、Settings dialog の責務を `Close` 削除前提で再整理し、あわせて state row / notice row 分離前提の surface semantics に載せ直すことにある。

## Settings dialog で先に置く surface 前提

- action row の上側に、編集中の current state を読むための state row を置く余地を持つ。
- action row の近傍には `OK / Cancel` のみを置き、本文右上部に永続化専用の `Save` を置く。
- 設定ファイルの保存先は利用者に選ばせず、一意に決まる既定パスを使う。少なくとも Linux では XDG 規約に沿う固定パスを前提にする。
- action row の下側には、短命 corrective error や file operation の失敗を出す notice 専用最下段 row を置く。
- 設定ファイルがまだ存在しない間は、notice row に「現在は未保存です」を出し、`OK` では自動生成しないことを利用者へ明示する。
- `Save` / `Apply` / `OK` のような成否を Main Window へ往復させるのではなく、まず Settings dialog 内で閉じる。
- Settings dialog では Color dialog と違って picker 面は不要だが、「現在状態 row と notice row を分離する」という骨格はそのまま踏襲する。

## 3rd planning で再確認する点

1. `Save` を本文右上部へ置いたとき、file write 専用操作として十分に読めるか。
2. `OK=Apply` を action row で自然に読ませるために、Color dialog 踏襲の state row へ何を常時見せるか。
3. `Cancel` を action row の明示 button として維持したうえで、window close とどう整合させるか。
4. current Harite dialog が file operation と state mutation をどこで結びつけているか。
5. Settings dialog の state row に何を常時見せ、notice row に何を短命表示として閉じるか。

## 非目的

- icon library の採否や比較をここで扱うこと。
- Settings dialog 全項目のレイアウト全面改修をここで確定すること。
- native chooser 群まで同じ語彙に寄せること。
- 2nd planning と Color dialog で既に固定した notice surface 規約そのものを再議論すること。

## 完了条件

- Settings dialog の action row が、利用者の視点で何をするボタン群か説明可能になっている。
- `Close` を削除するか否か、その理由が説明可能になっている。
- `Load` を dialog に置かない理由と、`OK=Apply`、`Save=永続化`、`Cancel=無変更終了` の役割分担が説明可能になっている。
- Settings dialog の state row と notice row が Color dialog 踏襲である前提で、どの message をどこへ出すか説明可能になっている。
- icon 論点を後段へ送る境界が明記されている。

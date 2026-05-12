# GUI Phase10 3rd Planning

最終更新: 2026-05-12

## 位置づけ

- 本書は Phase10 の 3rd planning として、Settings dialog の操作 semantics を独立論点で整理するメモである。
- [docs/specs/gui/gui-phase10-1st-planning.md](docs/specs/gui/gui-phase10-1st-planning.md) では起動導線を扱い、[docs/specs/gui/gui-phase10-2nd-planning.md](docs/specs/gui/gui-phase10-2nd-planning.md) では visual aid / message surface を扱った。
- 本書では、それらとは別に、Settings dialog の `Apply / Load / Save / Close` が利用者にどう見えるべきかを扱う。
- icon library の採否や比較は、本書では扱わず Phase10 4th planning へ送る。

## 現在地

- current Settings dialog は custom editor dialog であり、native chooser ではない。
- 一方、Save As や color chooser など一部 dialog は native GTK chooser を使い得るため、Settings だけが custom semantics を明示的に持つ。
- このため Settings dialog は、「native らしさ」よりも「何を押すと何が起きるか」が優先される。

## 問題の見立て

### 1. `Close` は責務が弱い

- `Close` は設定反映もファイル操作も持たず、単に dialog を閉じるだけである。
- その役割は右肩の `×` と重複しており、action row 上の常設ボタンとしては弱い。
- よって `Close` は削除候補とする。

### 2. `Save` と `Apply` の責務分離に違和感がある

- 一般的な editor / settings UI では、保存がそのまま反映に近い挙動へ見えることが多い。
- current dialog で `Save` と `Apply` を分ける場合、利用者には「なぜ二段階なのか」の説明責任が発生する。
- 特に `Save` が export 相当、`Apply` が session 反映相当であるなら、語彙だけではその差が読みづらい。

### 3. `Load` も後付けに見えやすい

- 設定ファイルの読み込みは自然な要求だが、dialog 文脈に `Load` を常設する必然は再点検が必要である。
- もし読み込み後にそのまま現在状態へ効くなら、単なる import でも preview でもなく、操作 semantics を明示する必要がある。

### 4. `Cancel` は明示価値がある

- 他の面で native dialog が `Cancel` を持つなら、Settings dialog にも「何も反映せず戻る」動作を明示する価値がある。
- `×` と同じ結果でも、action row 上の `Cancel` は役割が分かりやすい。

## 比較候補

### 案1: 二段階維持

- `Apply / Load / Save / Cancel`
- `Apply`: dialog 内容を current session へ反映
- `Load`: 設定ファイルを読む
- `Save`: 現在内容を設定ファイルへ書く
- `Cancel`: 何も反映せず閉じる

懸念:

- `Apply` と `Save` の分離理由が利用者へ見えにくい。
- `Load` も file operation と state mutation の境界が曖昧になりやすい。

### 案2: 単段階整理

- `Load / Save / Cancel`
- `Save` は現在の設定内容を保存し、その結果 current session にも整合する前提へ寄せる。
- `Load` は file operation と current session 更新を一体で扱う。
- `Cancel` は無変更で戻ることを明示する。

利点:

- `Save` と `Apply` の二段階感を解消できる。
- action row の意味が file operation 中心で読みやすい。
- `Close` を廃しても操作の意図が残る。

懸念:

- 母体プログラムが本当にこの整理に近かったかを再観察する必要がある。
- `Load` の語彙が適切か、`Import` 相当へ寄せるべきかは保留である。

## 現時点の暫定落としどころ

- 3rd planning の初期結論は案2を第一候補とする。
- ただし `Load` の語彙と、母体プログラム側で本当に file operation がどう見えていたかは、この planning 内で再観察してから最終固定する。
- したがって本書の目的は、直ちにラベルだけを置換することではなく、Settings dialog の責務を `Close` 削除前提で再整理することにある。

## 3rd planning で再確認する点

1. 母体プログラムの Settings / Prefs 相当 dialog に、`Load` または import 相当があったか。
2. `Save` が export 相当だったのか、それとも current state 反映まで一体で担っていたか。
3. `Cancel` が custom button として存在していたか、あるいは window close に委譲していたか。
4. current Harite dialog が file operation と state mutation をどこで結びつけているか。

## 非目的

- icon library の採否や比較をここで扱うこと。
- Settings dialog 全項目のレイアウト全面改修をここで確定すること。
- native chooser 群まで同じ語彙に寄せること。

## 完了条件

- Settings dialog の action row が、利用者の視点で何をするボタン群か説明可能になっている。
- `Close` を削除するか否か、その理由が説明可能になっている。
- `Load` / `Save` / `Apply` の役割分担、または統合方針が説明可能になっている。
- icon 論点を後段へ送る境界が明記されている。

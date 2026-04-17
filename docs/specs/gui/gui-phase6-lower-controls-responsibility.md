# GUI Phase 6 下部コントロール責務表

最終更新: 2026-04-16

## 目的

- 下部コントロール群の各要素について、上流根拠、現 GUI 実態、CLI 根拠、危険性を並べて責務を再定義する。
- 「機能を残すか」と「下部コントロール帯に残すか」を分離して判断する。
- T6-4 のレイアウト再定義で、どの操作を main command bar から外すかを決められる状態にする。

## この文書の位置づけ

- 本書は意思決定の記録ではなく、Phase6 の判断前に読むためのたたき台である。
- `暫定判断` は確定事項ではなく、「この論点なら今はこう読むのが自然ではないか」という初期案を示す。
- owner 判断や後続実機確認で覆ることを前提に読む。

## 一次参照

- [docs/legacy-ui/wallpositapplet.glade](docs/legacy-ui/wallpositapplet.glade)
- [docs/manual-validation-gate.md](docs/manual-validation-gate.md)
- [docs/specs/gui/gui-phase6-planning.md](docs/specs/gui/gui-phase6-planning.md)
- [docs/specs/gui/gui-phase6-cli-reference-check.md](docs/specs/gui/gui-phase6-cli-reference-check.md)
- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py)
- [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py)
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py)

## 前提

- 上流 glade の下部コントロール帯には、`Prefs`、`Color`、`Save`、`Apply`、watch interval、watch start/stop、`About`、`Help` が並んでいた。
- 現 GUI は上流の並びをそのまま復元しておらず、`Save` / `Optimize` / `Apply` は別セクション化され、fallback command bar には `Prefs`、`Color`、`Save Confirm`、`Save Cancel`、watch 系、`About`、`Help` が残っている。
- Phase6 では「昔そこにあったから残す」ではなく、現責務に照らして残す/外す/延期を判断する。

## 責務表

| コントロール | 上流根拠 | 現 GUI 実態 | CLI 根拠 | 現責務の評価 | 暫定判断 |
| --- | --- | --- | --- | --- | --- |
| Prefs | glade に `btnSetting` と `SettingDialog` がある | MainWindow に対応 handler は未整備だが、fallback に入口が残る | CLI は `--config` を持ち、GUI / CLI で共有 config を持つ前提がある | owner 判断では意味がある。config 共有の入口であり、watch source も元はここにあった。interval だけが main window に残っていた | 残す。Zone 6 Secondary / Meta に置く |
| Color | glade に `btnSetColor` と `ColorSelectionDialog` がある | MainWindow では `planned` のまま | CLI に対応機能なし | 現コア導線の一部ではなく、Optimize / Apply / watch の正本確認とも結び付いていない | コア下部コントロールから外し、Phase7 候補へ送る |
| Save Confirm | 上流 glade の恒常ボタンではなく、現 fallback 運用で追加された confirm 操作 | native save chooser の confirm 代理。chooser open 中のみ有効 | CLI に直接対応機能なし | 恒常ボタンではなく、save path chooser 内部の確定操作を表面に露出したもの。正式 UI では常設責務を持たない | 全廃 |
| Save Cancel | 上流 glade の恒常ボタンではなく、現 fallback 運用で追加された cancel 操作 | native save chooser の cancel 代理。chooser open 中のみ有効 | CLI に直接対応機能なし | Save Confirm と同じく chooser 内部責務であり、常設コントロールの責務ではない | 全廃 |
| Save | glade に `btnSave` がある | MainWindow では save path chooser を開くだけで、生成は選択確定後に進む | CLI `optimize` の出力先指定に対応するが、独立の `save` コマンドはない | 現責務は「保存先を選ぶ前段操作」であり、Optimize 実行そのものではない。ラベルと期待挙動が混線しやすい | 意味づけは了解。英語ラベルは `Save As`、配置は Flow / Header の標準保存位置 |
| Optimize | glade 下部帯には独立ボタンではなく、現 GUI が modern action として追加した | MainWindow の主機能として実装済み。fallback でも別セクション化済み | CLI `optimize` は正本として存在 | コア主機能であり、補助帯ではなく主操作面に置くのが妥当 | 機能維持。下部コントロール帯へ戻さない候補 |
| Apply | glade に `btnSetWall` がある | 現 GUI では dry-run / do-it に分かれており、旧 `Apply` の即時性から離れている | CLI `apply` は正本として存在するが、現実装は dry-run / `--do-it` に分かれる | owner 判断では `do-it` は不要で、旧プログラムどおり `Apply` は即時変更でよい。一方で `Optimize` との見せ方は近接した主操作として整理するのが自然である | 残す。`Optimize` と隣接配置する |

## コントロール別メモ

### Prefs

- owner 判断では `Prefs` は残す。
- 理由は、CLI / GUI 間で config を共有する仕組みの入口として意味があるためである。
- watch source も元はここにあり、interval だけが main window に残っていたという整理を採る。
- Zone 6 Secondary / Meta に置く前提で読む。

### Color

- `ColorSelectionDialog` は上流資産として存在するが、現 CLI / GUI のコアフローには接続されていない。
- planned のまま main command bar に残すと、コア機能の未完と新機能候補が混線する。

### Save Confirm / Save Cancel

- [docs/manual-validation-gate.md](docs/manual-validation-gate.md) では fallback 運用のために明示されているが、これは常設 UI としての正当化ではなく、暫定運用ルールである。
- owner 判断により、両方とも全廃とする。

### Save

- [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py#L296) の `on_save()` は保存を実行せず、save path chooser を開くだけである。
- 保存先確定後に [src/harite/gui/views/main_window.py](src/harite/gui/views/main_window.py#L395) の save path 選択確定が optimize 実行へ進むため、現責務は「Save」より「Choose Save Target」に近い。
- owner 判断では、この意味づけはいったん了承する。
- 一方で `Save` は `Optimize` / `Apply` と同列の主操作には置かず、Flow / Header の右端など標準的な保存位置へ分けて置く読みでよい。
- glade でも保存アイコンがあり、使用頻度が薄くてもシステム説明上は残す価値がある、という読みを採る。
- 現時点の英語ラベルは `Save As` を採る。
- 多言語化は i18n 企画時に再検討する。

### Optimize

- 現 GUI では既に main flow の中心であり、fallback でも独立セクションに分離済みである。
- 下部コントロール帯へ戻すと、Save の前提操作と Apply の結果操作の間に挟まり、責務が見えにくくなる。

### Apply

- owner 判断では、`do-it` は不要であり、`Apply` は即時変更でよい。
- したがって Phase6 では `Apply dry-run` / `Apply do-it` の二段構えを正本としない。
- ただし owner 認識では `Optimize` と `Apply` は本来かなり近い意味を持つ。
- owner 判断では、`Optimize` と `Apply` は隣り合わせでよい。
- したがって、構造判断では両者を近接配置する前提で読む。

## 現時点のたたき台

- 下部コントロール帯に残す理由が現時点で強いのは watch 系だけである。
- `Prefs` は残し、Zone 6 Secondary / Meta に置く。
- `Color` は Phase7 へ送る。
- `Save Confirm`、`Save Cancel` は全廃する。
- `Save`、`Optimize`、`Apply` はコア機能として扱う。
- `Save` は `Save As` として標準的な保存位置へ分けて置く。
- `Optimize` と `Apply` は近接配置する。

## T6-4 への引き継ぎ

1. main command bar から外す候補案:
   - `Color`
   - `Save Confirm`
   - `Save Cancel`
2. セクション再配置候補案:
   - `Save` は Flow / Header の右端など標準的な保存位置へ
   - `Optimize` は main flow の主機能として維持
   - `Apply` は `Optimize` に近接配置
3. 要再定義論点:
   - `Apply` と watch 実切替の関係

## 次アクション

1. 本ファイルを T6-3 の初版として固定する。
2. T6-4 で zone 単位の再配置案を作る。
3. T6-4 では「watch 系だけ command bar に残すのか」も含めて再判断する。

# GUI Phase 6 glade / adapter 判断メモ

最終更新: 2026-04-17

## 目的

- glade、`ui_adapter`、runtime fallback backend の現責務を切り分ける。
- 「Phase6 のうちに repo から撤去するもの」と「撤去後に既存 docs / 母体プログラム参照へ戻すもの」を分ける。
- Phase6 の構造判断に必要な維持 / 縮退 / 撤去の比較材料を整える。
- 最終的に「新規 GUI の標準形」に近い構造を Phase6 の出口として定義する。

## この文書の位置づけ

- 本書は最終判断の記録ではなく、owner 判断前のたたき台である。
- `有力` や `候補` は採択済みを意味しない。
- 目的は、Phase5 暫定事情で残った層を、現責務ベースで読み直すことにある。

## 一次参照

- [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py)
- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py)
- [src/harite/gui/app.py](src/harite/gui/app.py)
- [docs/specs/gui/gui-signal-mapping.md](docs/specs/gui/gui-signal-mapping.md) 旧 glade signal の履歴証跡
- [docs/specs/gui/gui-phase6-layout-redefinition.md](docs/specs/gui/gui-phase6-layout-redefinition.md)

## 現状の整理

### 1. glade

現状の役割:

- signal 一覧と widget ID の参照元
- 旧 UI の配置意図を読むための一次資料
- GTK runtime では `Gtk.Builder.add_from_file()` の入力候補

観察:

- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py#L1630) では、旧 glade schema のため `Gtk.Builder` で消費できない可能性を前提に fallback している。
- owner 判断では、legacy と呼ぶ以上 repo に保険的に残す理由は弱い。
- したがって論点は「参照資産として残すか」ではなく、「既存 docs と母体プログラム参照で足りる状態にしたうえで repo と current code path から消せるか」である。

### 2. `ui_adapter`

現状の役割:

- legacy signal 名から `MainWindow` メソッドへ対応づける
- GTK 由来の引数形を `MainWindow` の簡潔なシグネチャへ正規化する
- glade を読んだ場合も、runtime fallback を使う場合も、同じ dispatch を作る

観察:

- [src/harite/gui/adapters/ui_adapter.py](src/harite/gui/adapters/ui_adapter.py) の実質責務は「互換 signal dispatcher」である。
- glade がなくても runtime fallback に対して dispatch を張れるので、`ui_adapter` 自体は glade 専用層ではない。
- 一方で、legacy signal 名に強く引っ張られており、`MainWindow` の現責務をそのまま表現する層にはなっていない。
- 2026-04-17 時点では、save 系は `on_save_path_selected` / `on_save_path_selection_canceled` / `on_close_save_path_dialog` を controller 正本とし、current runtime の adapter / backend も同じ save path 名へそろえている。
- app の glade prototype 前提を外したことで、save 系の旧 button 名 / destroy 名は current runtime の互換入口からも削除可能になった。
- したがって save 系の signal 名刷新は current runtime では完了し、残る旧名は glade resource 自体の証跡または撤去対象として扱う。
- owner 判断では、これは移植慎重化の結果として冗長化した層であり、「読んで古い signal を見つけ、変換し、新 signal へつなぐ」構造自体が残す実装に見えない。
- 解析性の向上よりも複雑さの温存に寄っており、すでに削減を始めている流れを Phase6 で正式方針化するのが自然である。

### 3. runtime fallback backend

現状の役割:

- `Gtk.Builder` が glade を読めない環境でも present/bind を成立させる
- P5 の実機確認や fallback 運用のため、Glade-like な代替 window を生成する
- Save/Open/Srcdir dialog の proxy も持つ

観察:

- [src/harite/gui/adapters/gtk_backend.py](src/harite/gui/adapters/gtk_backend.py#L405) にあるとおり、これは `Gtk.Builder` 非依存の最小 GTK backend として作られている。
- しかし Phase5 の復旧過程で、単なる fallback を超えて、暫定 UI 本体に近い責務を抱えた。
- T6-4 の zone 構成から見ると、現在の fallback backend は command bar と provisional labels を多く抱えすぎている。
- 2026-04-17 時点では、save chooser 周辺の object key は `SavePathDialog` / `lblSavePathState` を正本としている。destroy signal も `on_SavePathDialog_destroy` を正本とし、current runtime では旧名を吸収しない。
- したがって save 系の次の削減単位は glade resource / signal mapping 側であり、current runtime からはすでに legacy save object id 解決を追い出している。

### 4. app 起動導線

現状の役割:

- `--bind-ui-backend` で GTK backend / fallback backend を準備
- `--present-ui-window` で GTK window を出す

観察:

- [src/harite/gui/app.py](src/harite/gui/app.py) は glade prototype 読み込み分岐を持たない形へ移行し、signal backend 準備と window 表示だけを段階的オプションとして残している。
- つまり app 自体は glade prototype を前提にせず、runtime backend / fallback backend を既定経路として読む。
- 現在の実行可能性は、glade より fallback backend に強く依存している。

## 何が負債か

- glade は runtime で読める前提が弱いうえ、repo に残すこと自体が legacy 保持コストになる。
- `ui_adapter` は互換層として導入されたが、古い signal 発見 -> 変換 -> 新 signal 接続という多段処理を抱え、解析性より冗長さを残す設計になっている。
- fallback backend は安全網として必要だったが、P5 で暫定 UI 本体の責務まで背負い込み、構造判断を遅らせる原因になっている。

## 比較軸

- glade は repo から撤去前提とする。
- signal 一覧や layout 骨格のために、新しい一覧表は増やさない前提とする。
- 比較対象は、glade 撤去後に `ui_adapter` と fallback backend をどこまで簡素化できるかである。
- 判断基準は「いまの実装を守れるか」ではなく、「新規 GUI の標準形にどこまで近づくか」である。

## glade 削除前に残す記録

- 新しい表は作らない。
- signal 対応は [docs/specs/gui/gui-signal-mapping.md](docs/specs/gui/gui-signal-mapping.md) を旧 glade signal の既存証跡として使う。
- layout 骨格は [docs/specs/gui/gui-glade-layout-reconstruction.md](docs/specs/gui/gui-glade-layout-reconstruction.md) を旧 Glade レイアウトの履歴根拠として使う。
- これで足りない場合だけ、repo 内の複製ではなく母体プログラムを参照して確認する。
- したがって T6-5 の論点は「削除前に新規の保存用一覧を増やすこと」ではなく、「既存 docs 参照で削除可能か」を確認することにある。

## 3案比較

### 案A: 維持

内容:

- glade を repo から撤去する
- `ui_adapter` を現状に近い形で維持する
- fallback backend も大きく残す

利点:

- glade 実ファイルは消せる
- 既存の present/bind フローを大きく崩さない
- Phase5 の回帰観点を保持しやすい

欠点:

- T6-4 で再定義した zone 構成へ寄せにくい
- legacy signal 名と provisional UI が残り続ける
- glade 撤去の効果が code 構造へ十分波及しない
- owner が問題視している冗長変換層を温存してしまう

読み筋:

- 比較用には残すが、owner 判断を踏まえると主案にはなりにくい

### 案B: 縮退

内容:

- glade を repo から撤去する
- `ui_adapter` は削減前提とし、どうしても残る最小の正規化だけ残す
- fallback backend は present/bind の安全網に限定し、暫定 command bar や provisional 要素を減らす

利点:

- glade の repo 残存をやめつつ、既存 docs をそのまま根拠に使える
- `MainWindow` / 新 zone 構成を正本へ寄せやすい
- 既存の fallback 安全網は残せる
- adapter の多段変換を削り、接続の読みやすさを上げやすい

欠点:

- どこまでを「どうしても残る正規化」とみなすかの整理が必要
- Phase6 実装で adapter/backend の責務棚卸しが発生する

読み筋:

- 現時点で最も筋が良い候補
- Phase5 の資産を活かしつつ、adapter を落とし始めている現状にも連続している
- Phase6 の出口を「新規 GUI の標準形へ寄せること」と置くなら、この案が最も現実的である

### 案C: 撤去

内容:

- glade を repo から撤去する
- `ui_adapter` を廃止する
- fallback backend も撤去し、`MainWindow` 直結の新 UI 構造へ寄せる

利点:

- 構造は最も単純になる
- legacy signal 名から切り離せる

欠点:

- Phase5 で積み上げた実機 fallback 導線を一気に捨てることになる
- いまある present/bind 検証経路を再構築する必要がある
- docs-only planning の次段としては着地が急すぎる

読み筋:

- 将来的な到達点候補ではあるが、Phase6 の直近判断としては強すぎる
- ただし adapter については、部位によってはこの案に近い直結化を先行採用し得る

## 部位ごとの読み筋

### glade

- repo 内に legacy 実体として残す価値は低い
- runtime 正本としての価値も低い
- signal 対応表と layout 再構成 docs はすでに存在する
- したがって「新規の保存表は増やさず、既存 docs と母体プログラム参照を前提に撤去する」が前提になる

### `ui_adapter`

- 現行の多段変換構造は残す実装として弱い
- 必要なのは「adapter を守ること」ではなく、「直結へ寄せながら、どうしても残る正規化だけを見極めること」である
- したがって「さらに落とす。部位によっては直結化する」が有力
- これは新規 GUI なら最初から避ける構造であり、Phase6 はそこへ戻す工程とみなせる

### fallback backend

- いまは安全網以上の責務を持っている
- zone 再定義後は、command bar 暫定本体ではなく「最小 present/bind backend」へ戻す方が自然
- したがって「安全網まで縮退」が有力
- これも新規 GUI の標準形では本体責務を持たないので、Phase6 の出口条件に含めるのが自然である

## 残存互換入口の棚卸し

- 2026-04-17 時点で `ui_adapter` の `LEGACY_HANDLER_MAP` は、glade 由来の signal 名を入口互換としてまだ保持している。
- save 系の current runtime 入口は `on_save_path_selected`、`on_save_path_selection_canceled`、`on_SavePathDialog_destroy` にそろっており、controller 正本 `on_close_save_path_dialog` へ直結する。
- `gtk_backend` 側も同じく、save chooser では正本名だけを受ける。
- fallback backend の object key も `SavePathDialog` / `lblSavePathState` に固定している。
- save 以外の dialog destroy signal は、`on_ErrorDialog_destroy`、`on_ImgOpenDialog_destroy`、`on_SrcdirDialog_destroy`、`on_ColorSelectionDialog_destroy`、`on_SettingDialog_destroy` など、glade 由来の名前をまだ保持しているが、現在は close handler への 1:1 対応であり、save 系ほど独自の暫定 semantics は抱えていない。
- したがって正本名を新設する基準は「close 以上の独自 semantics を持ち、内部 state / object key / status wording まで再編していること」と置くのが妥当であり、この基準では現状 save 系だけが該当する。

## Phase6 の最終縮退線メモ

- Phase6 の縮退線は「legacy 名を完全にゼロにすること」ではなく、「glade 由来の入口互換だけに限定し、内部状態・正本 method・正本 object key からは追い出すこと」と読むのが妥当である。
- したがって、これ以上 legacy 名を増やさないこと、正本名を docs / tests / backend internals の既定表現にすることが最低線になる。
- glade 撤去後に優先して落とす候補は、glade resource 側にだけ残る save legacy signal 名と save legacy object id である。
- save 系の legacy signal 名は glade が唯一の供給元になったため、ここを落とす順序は「glade 更新または撤去」→「signal mapping 証跡の整理」で足りる。
- 2026-04-17 時点の実装順では、current runtime からは save legacy object id 解決と save legacy signal 名吸収を先に除去できた。
- 一方で、Phase6 の間は runtime fallback を安全網として維持する都合上、glade 由来 signal 名の入口互換を最小限だけ残す判断には合理性がある。

## 互換入口の分類

### Phase6 中に残す互換入口

- dialog destroy 系の glade 由来 signal 名
- `on_ErrorDialog_destroy`
- `on_ImgOpenDialog_destroy`
- `on_SrcdirDialog_destroy`
- `on_ColorSelectionDialog_destroy`
- `on_SettingDialog_destroy`
- 理由: close handler への 1:1 接続であり、暫定意味づけが薄く、fallback 安全網の維持コストも低い。Phase6 では正本名を増やさず、glade 由来 signal 名のまま入口互換として固定してよい。
- watch / input / toggle / margin などの glade 由来 signal 名
- `on_entPath_insert_text`
- `on_btnGetImg_clicked`
- `on_btnOpenSrcdir_clicked`
- `on_spnInterval_value_changed`
- `on_spnMergin_value_changed`
- `on_tglBtn_pressed` / `on_tglBtn_toggled` / `on_tglBtn_released`
- 理由: まだ Gtk 由来の引数正規化を `ui_adapter` が担っており、Phase6 中は「入口互換」として残す意味がある。

### glade 撤去後に優先して落とす候補

- save 系の旧 button 名 / destroy 名 / object id
- `on_btnOpenSave_clicked`
- `on_btnCancelSave_clicked`
- `on_SaveWallpaperDialog_destroy`
- `SaveWallpaperDialog`
- 理由: current runtime からは削除済みであり、残っているなら glade resource 側の証跡または撤去対象としてだけ扱えばよい。

### save legacy 削除の順序

- 第1段: runtime fallback の旧 object key を除去する
- 現状: `lblSaveDialogState` は除去済みで、fallback 側は `SavePathDialog` / `lblSavePathState` を正本 expose としている。
- 第2段: docs / tests の正本表現を `save_path` 系へ寄せる
- 現状: Phase6 planning / judgement / runtime backend test は追随済みで、旧 object key を前提にしない説明へ寄っている。
- 第3段: current runtime の adapter / backend から save legacy signal 吸収と save legacy object id 解決を削除する
- 現状: `on_btnOpenSave_clicked` / `on_btnCancelSave_clicked` / `on_SaveWallpaperDialog_destroy` / `SaveWallpaperDialog` は current runtime から除去済みである。
- 第4段: glade resource の save path chooser id / handler 名を更新または撤去する
- 到達条件: repo 内に save legacy 名を残す理由が証跡だけになっていること。

### save legacy 削除 checklist

- 着手前: runtime fallback が `SavePathDialog` / `lblSavePathState` のみを expose していること
- 着手前: docs と tests が `save_path` 系の正本表現を前提にしていること
- 着手前: glade resource に残る save legacy 名を列挙できていること
- 着手前: `SaveWallpaperDialog`
- 着手前: `on_btnOpenSave_clicked`
- 着手前: `on_btnCancelSave_clicked`
- 着手前: `on_SaveWallpaperDialog_destroy`
- glade 更新時: save path chooser id を `SavePathDialog` へそろえる、または chooser 自体を撤去すること
- glade 更新時: save button handler を `on_save_path_selected` / `on_save_path_selection_canceled` へ更新すること
- glade 更新時: destroy handler を `on_SavePathDialog_destroy` へ更新すること
- current runtime 確認: adapter / backend に save legacy 名吸収が再導入されていないこと
- 削除後確認: save path 選択が文字列引数と dialog object の両経路で崩れていないこと
- 削除後確認: save path chooser close が `MainWindow.on_close_save_path_dialog` へ一意に流れること
- 削除後確認: runtime fallback が旧 object key を再 expose していないこと

### 直結化の優先候補

- save chooser acceptance / cancel / destroy
- `on_save_path_selected`
- `on_save_path_selection_canceled`
- `on_close_save_path_dialog`
- 理由: 正本名と object key がすでに揃っており、adapter を介さない説明に最も寄せやすい。逆に言えば、この条件を満たさない dialog close 系には正本名を増やさない。
- apply / optimize の主操作
- `on_apply`
- `on_optimize`
- 理由: Phase6 で責務がかなり単純化しており、「legacy signal を読んでから変換する」必要性が save 系よりさらに薄い。

## 現時点の確定方針

- glade は repo 内の参照資産として残さず、Phase6 のうちに撤去する前提で読む
- app の glade prototype 前提は完全に撤去し、起動導線は runtime backend / fallback backend を既定とする
- `ui_adapter` は維持対象ではなく、さらに落とし、必要箇所は直結へ寄せる読みが有力
- fallback backend は維持ではなく、暫定 UI 本体責務を下ろして安全網まで縮退する読みが有力
- 直近の実装到達点として、save 系は status / open-state / dialog key / destroy signal の正本名が `save_path` 系へ寄っており、残存 legacy は主に glade 由来の signal 名と object key alias に限られつつある
- したがって、Phase6 では app -> adapter -> backend の順に glade prototype 依存を切り離し、Phase6-7 境界は owner の XFCE 実機承認で切る

## owner 判断で決めること

1. 既存 docs 参照だけで glade を撤去してよいか
2. app 起動導線から glade prototype 前提をどの順序で撤去するか
3. `ui_adapter` をどこまで落とし、どの部位を直結へ寄せるか
4. fallback backend を安全網へ戻すか、当面の実働 UI として残すか

## 実施形態の想定

- glade prototype 前提の撤去は owner 決定済みとする
- 以後は app 起動導線から順に実装を落とし、残る論点は adapter / backend の縮退線に絞る

## 次アクション

1. 本ファイルを T6-5 の初版として固定する
2. owner 判断後、Phase6 planning の `Decision 3` と整合する形で実装対象を確定する

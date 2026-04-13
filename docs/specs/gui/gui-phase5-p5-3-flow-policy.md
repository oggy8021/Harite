# GUI Phase5 P5-3 フロー分離・優先順位仕様

最終更新: 2026-04-13
対象: P5-3 feat(gui)

## 目的

- Optimize と Apply を視覚・操作の両面で明確に分離する。
- 位置トグル（`tgl*`）と margin 指定の競合時の優先順位を固定する。

## 1. フロー分離方針

- Optimize は「生成フェーズ」、Apply は「反映フェーズ」として分離表示する。
- Apply は Optimize 成功後にのみ活性化する。
- `Apply dry-run` を既定とし、`do-it` は確認導線を通した場合のみ実行可能にする（P5-3で導線定義、実装は段階導入）。
- 旧MainWindowの `on_btnSave_clicked` は Save 導線（保存先選択 + 生成）として扱い、独立した旧Optimizeボタンは存在しない前提で設計する。
- 現行UIでは移行安全策として `Optimize (provisional)` を Save 近傍に仮置きし、旧Save導線と並走させる。
- 実装状況: Core/Controller は `save_path`（`output_path`）直指定を受ける。未指定時は従来どおり `output_dir` 自動命名を維持する。
- 実装状況: SaveDialog confirm で保存先が渡された場合、入力準備済みなら旧Save導線（選択+生成）をそのまま続行する。
- 実装状況: SaveDialog cancel は `save_path` を変更しない（既存値を維持）。
- 実装状況: GTK fallback では `SaveWallpaperDialog` プロキシと `btnOpenSave` / `btnCancelSave` を持ち、confirm/cancel signal を実発火できる。
- 実装状況: GTK fallback では `btnSave` クリック時に SaveDialog プロキシを open、confirm/cancel で hide する可視状態遷移を持つ。
- 実装状況: GTK fallback では `btnSave` は dialog open 専用、生成は confirm（`on_btnOpenSave_clicked`）経由で続行する。
- 実装状況: SaveDialog 状態は専用ラベル（`SaveDialog: open/closed(...)`）で表示し、Optimize/Apply のステータス表示と干渉しない。
- 実装状況: SaveDialog の confirm/cancel ボタンは dialog open 中のみ活性化し、closed では非活性に戻す。
- 実装状況: confirm 時に保存先未選択なら `path-required` を表示して dialog を閉じない（誤確定防止）。
- 実装状況: MainWindow でも confirm の保存先必須を適用し、空confirmは `save path is required` として失敗させる。
- 実装状況: MainWindow の confirm は既存 `save_path` がある場合、引数なしでも既存値で続行可能（再試行時の透過性向上）。
- 実装状況: MainWindow の `on_save` は SaveDialog open 専用、生成実行は confirm 経由（`on_save_dialog_confirm -> on_optimize`）へ統一。
- 実装状況: confirm/cancel が closed 状態で呼ばれた場合は `ignored-closed` として無視し、副作用を起こさない。
- 実装状況: MainWindow でも closed 状態の confirm/cancel は `save dialog ignored (closed)` として無視する。
- 実装状況: 入力が空へ戻った場合は SaveDialog を自動で closed に戻し、confirm/cancel を非活性化する。
- 実装状況: MainWindow でも入力が空へ戻ると SaveDialog 状態を closed として扱い、再選択を要求する。
- 実装状況: dialog open 中でも保存先未選択なら confirm は非活性、保存先選択後のみ活性化する。
- 残ギャップ: 実GTKのファイル選択ダイアログUI（show/hide とユーザー選択体験）および失敗時リトライ体験の磨き込みは段階導入を継続する。
- 方針合意: 旧互換シグナル/Glade依存は P5-3 完了までの暫定維持とし、完了後は P5-8 で段階撤去へ移行する。
- `watch` 系（旧 `btnDaemonize` / `btnCancelDaemonize` / `spnInterval`）は P5-3 では導線命名のみ固定し、実処理は後続で段階導入する。
  - `on_watch_start` / `on_watch_stop` / `on_watch_interval_change` を planned 名として扱う。

## 2. 位置決め優先順位（暫定確定）

競合時は以下の順で解決する。

1. 固定モード（`radFixed`）
2. margin（`spnTopMergin`, `spnLMergin`, `spnRMergin`, `spnBtmMergin`）
3. 位置トグル（`tglUpper*`, `tglLower*`, `tglPush*`）

補足:

- margin が明示されている場合、トグルの見た目状態は保持しても、最終配置は margin を優先する。
- 競合が発生した場合は UI 上に優先解決ルールを表示する（例: `margin overrides alignment toggles`）。

## 3. P5-3 受け入れ観点

### 3-1. 回帰必須（既存保証）

- `Apply` は Optimize 未実行時に非活性である。
- `Apply dry-run` が既定である。
- 旧Save導線（`on_btnSave_clicked`）は維持され、Save意味が Optimize 同義へ崩れない。

### 3-2. P5-3 新規成果

- Optimize と Apply のセクションが視覚的に別ブロックとして認識できる。
- 優先順位ルールが Notes またはヘルプ文言で確認できる。
- `do-it` は未実装の場合、UI上で「未提供」または「planned」と明示される。
- `watch` は未実装の場合、UI上で「planned」であることが明示され、誤って既実装に見えない。

## 4. 後続への引き継ぎ

- P5-4: 文言/配色/余白トークンを最終統一。
- P5-4以降: preview window（入力画像/Optimize結果）と color picker, watch 導線を段階実装。
- P5-4以降: SaveDialog確定イベントから Optimize 実行までの一連導線を仕上げ、旧Save導線の体験一致を完成させる。

## 5. 透過性ルール（CLI準拠とGUI拡張の境界）

- `harite optimize` の引数体系（`--output` など）を CLI 準拠の基底契約とする。
- `save_path` / `output_path` は GUI 側の拡張契約として扱う。
  - 旧 `argparse` 由来の公開オプションではなく、SaveDialog で選ばれた保存先を損なわないための GUI 専用導線。
  - CLI からは `--output`（ディレクトリ）を使い、GUI からは必要に応じてファイル直指定を使う。
- 未実装または段階導入中の項目は、UI上で必ず `planned` と明示する。
  - 対象: `Color`, `watch`, `do-it`。
  - 禁止: 実行可能に見える表示のまま、内部で何も起きない状態を放置すること。

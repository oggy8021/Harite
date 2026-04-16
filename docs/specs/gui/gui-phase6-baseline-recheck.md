# GUI Phase 6 ベースライン再点検リスト

最終更新: 2026-04-16

## 目的

- Phase5 までの `pass` 記録を、そのまま前提事実として固定せず再点検する。
- 「見た目 pass」「機能 pass」「誤認 pass の疑い」を分離する。
- Phase6 の後続 workstream が誤った前提に乗らないよう、再検証が必要な項目を先に明文化する。
- 特に初期製造時から P5-7 までについては、母体プログラム参照不足により、`docs/upstream-*` 系文書や glade を十分な正本として扱えなかったことを前提に再点検する。

## 判定区分

- `維持してよい pass`
  - 現時点で pass 記録を維持してよく、Phase6 の前提にしてよい項目。
- `再検証が必要な pass`
  - 当時の判定自体は妥当でも、現実装や周辺仕様の変化により再確認したい項目。
- `誤認 pass の疑い`
  - pass 記録はあるが、実装実態を見ると「状態表示だけ進んだ」「planned のまま見えていた」可能性がある項目。

## 一次参照

- [docs/specs/gui/gui-phase5-tasklist.md](docs/specs/gui/gui-phase5-tasklist.md)
- [docs/specs/gui/gui-phase5-upstream-traceability-checklist.md](docs/specs/gui/gui-phase5-upstream-traceability-checklist.md)
- [docs/specs/gui/gui-phase4-diff-checklist.md](docs/specs/gui/gui-phase4-diff-checklist.md)
- [docs/manual-validation-gate.md](docs/manual-validation-gate.md)

## 再点検リスト

| 項目 | 直近の記録 | 暫定判定 | 理由 | Phase6 での扱い |
| --- | --- | --- | --- | --- |
| P5-1 見た目再現チェックリスト定義 | docs 成果物として完了 | 維持してよい pass | docs 作成タスクであり、後続の基準文書としては有効 | 基準文書として維持 |
| P5-5 視覚回帰テスト | visual token / blueprint / smoke を固定 | 維持してよい pass | テストの存在自体は事実で、視覚トークン固定にも価値がある | ただし「機能保証」には使わない |
| P5-6 manual gate 同期 | docs / tests / 実機記録の突合ルールを同期 | 再検証が必要な pass | manual gate は整備されたが、GUI 実装が暫定のまま進んだ箇所がある | Phase6 で gate 文言を再調整 |
| P5-7 XFCE 実機最終判定 | tasklist 上は未完了 | 再検証が必要な pass | Phase5 全体の総合ゲートとしては未完了のまま。P5-8 以降の個別 pass が積み上がっている | Phase6 で「最終判定」概念を再整理 |
| Phase4 B-5 dry-run と do-it の表示差 | checklist 上の必須項目 | 誤認 pass の疑い | GUI では `do-it` が planned のままの期間が長く、表示差を十分確認できていない | `do-it` 論点に統合 |
| P5-4 visual tier / Commands / Flow 表示 | style tier と見た目語彙を整備 | 維持してよい pass | 見た目整理としては有効で、誤認ではない | ただし配置再定義時に再評価 |
| P5-9 Open dialog 復元 | chooser 起動、confirm/cancel、path 表示、filter UI を確認 | 維持してよい pass | 実機確認と upstream traceability が揃っている | Phase6 では維持前提 |
| P5-10 watch srcdir / interval / start-stop 表示 | srcdir chooser、左右反映、status 表示、interval 更新を確認 | 再検証が必要な pass | 判定自体は妥当だが、実切替や apply は範囲外だった | Phase6 では apply 責務と切り分ける |
| P5-10 watch 実動作 | 「たぶん動いている」段階 | 誤認 pass の疑い | 状態表示は進むが、実装上は壁紙 apply / 継続切替未接続 | watch と apply の責務を再定義 |
| P5-11 Save UX | chooser 起動、confirm/cancel、save target、overwrite を確認 | 維持してよい pass | 実機確認と docs が揃っている | 下部コントロール責務整理で confirm/cancel UI だけ再検討 |
| 下部コントロール群全体 | P5 で暫定配置のまま積み上がり | 再検証が必要な pass | `Prefs` 未実装、`Color` planned、Save/Optimize 配置の暫定性が残る | Phase6 Workstream 3 へ送る |
| glade 位置再現 | Phase5 で大枠整形 | 再検証が必要な pass | 視線導線は改善したが、元の hbox/vbox 位置再現には遠い | Phase6 Workstream 4 へ送る |
| adapter / fallback backend の複雑化 | Phase5 では必要悪として拡張 | 再検証が必要な pass | 導線復旧に有効だった一方、複雑化も生んだ | Phase6 Workstream 5 へ送る |

## 誤認しやすい論点

- `pass` は常に「最終仕様を満たした」ではなく、「その PR の受け入れ条件を満たした」に過ぎない。
- 初期製造時から P5-7 まででは、母体プログラムそのものより `docs/upstream-*` 系文書や glade の斜め読みに依存したため、上流の責務や挙動意味を取り違えた可能性がある。
- P5-10 の watch はその典型で、srcdir 選択と status 表示の pass は、実壁紙切替の pass ではない。
- `do-it` は Phase4 / Phase5 で繰り返し参照されているが、GUI 上では長く planned 扱いであり、表示差や安全策の議論が未完了。
- `manual-validation-gate.md` の apply do-it 項目は CLI/実機運用としては有効だが、GUI 実装の到達点と同一視しない。

## Phase6 への引き継ぎ

### Workstream 1 で直ちに扱うもの

- P5-7 の「最終判定」の意味整理
- P5-10 watch pass の再定義
- `do-it` を含む表示差 / 実機差の棚卸し

### Workstream 2 へ送るもの

- CLI `apply`
- CLI `watch`
- plugin apply
- `--do-it`

### Workstream 3 以降へ送るもの

- 下部コントロールの残す/消す/延期
- `Save Confirm` / `Save Cancel` の GUI 上の必要性
- `Save` / `Optimize` / `do-it` の配置再定義
- glade / adapter の最終判断

## 次アクション

1. 本ファイルを T6-1 の初版として固定する。
2. T6-2 で CLI 正本確認メモを起こす。
3. T6-2 の結果を踏まえて、`do-it` と watch 実切替の責務境界を明文化する。

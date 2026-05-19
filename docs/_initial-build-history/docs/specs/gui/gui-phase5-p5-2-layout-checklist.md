# GUI Phase5 P5-2 MainWindow 大胆再構成チェックリスト

最終更新: 2026-04-13
対象: P5-2 feat(gui)

## 目的

- MainWindow の情報構造を再設計し、第一印象で主操作が分かる状態にする。
- Glade 時代のレイアウト意図を保ちながら、現行の可読性を引き上げる。
- 中央領域は「3列固定」より「十字配置再現 + 実装しやすさ」を優先し、列/行増減を許容する。

## 判定ルール

- 各項目は `pass` / `fail` / `not-available` で判定する。
- `fail` は 1 行以上の再現メモを残す。
- 受け入れは必須項目がすべて `pass` であること。

## A。構造再設計（必須）

- [x] A-1 主操作（Optimize / Apply）が画面上で最初に視認できる
- [x] A-2 入力群（input/resolution/output）が機能単位でまとまっている
- [x] A-3 情報の主従（見出し/補助説明/入力）が視覚的に区別できる
- [x] A-4 旧版で重要だった操作ブロックが欠落していない
- [x] A-5 中央領域は十字配置（上下左右の独立指示 + 中央操作）の意味を保持し、実装都合で列/行構成を調整してもよい

## B。余白と視線導線（必須）

- [x] B-1 セクション間余白が統一され、詰まり/空き過ぎがない
- [x] B-2 ラベル、入力、主要ボタンの整列軸が揃っている
- [x] B-3 視線が左上から主要操作へ自然に流れる
- [x] B-4 誤操作を誘発する近接配置がない

## C。体験差分の可視化（必須）

- [x] C-1 before/after 画像で構造差分が一目で分かる
- [x] C-2 変更理由を 3 行以内で説明できる
- [x] C-3 変更により「次に押す場所」が迷いにくくなっている

## D。品質運用（必須）

- [x] D-1 関連 GUI テスト結果が記録されている
- [x] D-2 XFCE 実機で MainWindow スクリーンショットを取得している
- [x] D-3 PR本文に判定結果と差分説明を貼り付けている

## E。上流制約の見直し（必須）

- [x] E-1 `docs/specs/upstream-full-analysis.md` を参照し、P5-2 で採用するUI制約を明記している
- [x] E-2 Window は `resizable=True` を採用し、旧Glade（False）との差分理由を記録している
- [x] E-3 旧Glade資産で重要な操作制約（誤操作防止、操作到達性）の維持/変更理由を記録している

進捗メモ（2026-04-13）:

- `resizable=True` は `src/harite/gui/adapters/gtk_backend.py` に反映済み。
- E-3 は PR本文の最終Notesで維持/変更理由を明文化して完了とする。

## 手動検証メモ反映（PR5-2）

参照: `out/manual-validation/gui-phase5-pr2-memo.md`

今回の判断（受け入れ）:

- `Glade-like layout (Phase5 P5-2)` は仮置きとして許容。
- `Optimize result: not-run` / `Apply target: not-ready` はデバッグ表示として許容。
- `about` / `help` は優先度低として後続対応。
- Optimize は `Save` ボタン割り当てで運用する。
- Apply は `dry-run` 割り当てで運用する。
- `do-it` 操作は P5-2 時点では未実装として扱う。

証跡運用（P5-2）:

- JSON 生成は任意。スクリーンショットと手動メモ（パス記録）を正本として扱う。
- JSON 出力は P5-7 最終判定で必須化する。

後続PRへ送る項目:

- P5-3: `tglUpper*`、`tglLower*`、`tglPush*` と margin の優先順位仕様を確定。
- P5-3: `OpenL/OpenR` など GUI 固有コントロールの有効化方針を具体化。
- P5-3: `Apply do-it` の導線/安全策（確認ダイアログ、誤操作防止）を設計する。
- P5-4: 中央2段目の `Wallpaper Optimizer` 表示の要否を最終決定。
- P5-4以降: color picker / watch（Execute、Stop + 秒指定）/ preview window の実装設計を段階化。

## 証跡テンプレート（PR貼り付け用）

```md
### P5-2 MainWindow Layout Delta
- Scope: [OS/desktop]
- A. 構造再設計: pass/fail/not-available
- B. 余白と視線導線: pass/fail/not-available
- C. 体験差分の可視化: pass/fail/not-available
- D. 品質運用: pass/fail/not-available
- E. 上流制約の見直し: pass/fail/not-available
- Before/After: attached
- Notes: [差分要点・再現メモ]
```

## Exit Criteria

- [x] A〜E 必須項目がすべて `pass`
- [x] MainWindow before/after 添付済み
- [x] PR本文にテンプレート記録済み

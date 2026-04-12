# GUI Phase 4 差分チェックリスト（旧画面比較）

最終更新: 2026-04-12
対象: P4-1 docs

## 目的

- 旧画面（Glade運用時）と現行画面の差分を、実装前にチェック項目として固定する。
- Phase4 の受け入れ判定を主観ではなくチェックリストで統一する。

## 判定ルール

- 各項目は `pass` / `fail` / `not-available` のいずれかで記録する。
- `fail` は再現手順を 1 行以上記録する。
- `not-available` は理由（環境制約、対象外）を必ず記録する。
- 最終受け入れは必須項目がすべて `pass` であること。

## 比較対象

- 旧画面: Glade運用時の操作導線（オーナー記録に基づく）
- 新画面: `python -m harite.gui.app --load-ui-prototype --bind-ui-backend --present-ui-window`

## A. 画面構造（必須）

- [ ] A-1 MainWindow の主要操作（Optimize / Apply）が初見で視認できる位置にある
- [ ] A-2 入力群（input/resolution/output）が論理的にグルーピングされている
- [ ] A-3 余白・間隔が過密/過疎でなく、誤操作を誘発しない
- [ ] A-4 画面上の視線導線が上から下、左から右で自然に追える
- [ ] A-5 旧画面で存在した主要操作が新画面で欠落していない

## B. 状態表示（必須）

- [ ] B-1 実行中ステータスが視認できる（無応答に見えない）
- [ ] B-2 成功時メッセージが明確で、次操作の判断ができる
- [ ] B-3 失敗時メッセージが明確で、原因追跡の入口がある
- [ ] B-4 エラー表示の場所と書式が一貫している
- [ ] B-5 dry-run と do-it の違いが表示上で判別できる

## C. 操作効率（必須）

- [ ] C-1 主要シナリオ（入力 -> Optimize -> Apply dry-run）で不要クリックがない
- [ ] C-2 主要操作に到達するまでの迷いが旧画面より減っている
- [ ] C-3 入力更新後の反映が把握しやすい（値変更の見落としが少ない）
- [ ] C-4 失敗時の再試行導線が明確（何を直せばよいか分かる）

## D. 品質運用（必須）

- [ ] D-1 関連回帰テストが実行され、結果が記録されている
- [ ] D-2 XFCE 実機証跡（JSON / Report / PR Comment）が揃っている
- [ ] D-3 MainWindow / Optimize / Apply の画面証跡が添付されている
- [ ] D-4 `docs/manual-validation-gate.md` の判定項目と不整合がない

## 主要シナリオ（判定用）

1. GUI 起動（実ウィンドウ表示）
2. 入力更新（path/resolution/output）
3. Optimize 実行
4. Apply dry-run 実行
5. 必要時のみ Apply do-it 実行

## 記録テンプレート（PR コメント貼り付け用）

```md
### Phase4 UI Diff Checklist
- Scope: [OS/desktop]
- A. 画面構造: pass/fail/not-available
- B. 状態表示: pass/fail/not-available
- C. 操作効率: pass/fail/not-available
- D. 品質運用: pass/fail/not-available
- Notes: [差分・課題・再現手順]
```

## Exit Criteria（P4-1 完了条件）

- [ ] 本ファイルが `docs/specs/gui/` に配置されている
- [ ] A〜D の必須項目が定義済み
- [ ] 判定ルール（pass/fail/not-available）が明記されている
- [ ] PR コメント用テンプレートが用意されている

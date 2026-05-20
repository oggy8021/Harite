# GUI Phase5 Visual Checklist

最終更新: 2026-04-13
対象: P5-1 docs

## 目的

- MainWindow / Optimize / Apply の見た目比較観点を固定する。
- PRレビュー時に、主観だけでなく同一項目で判定できる状態にする。

## 運用ルール

- 1評価セッションで MainWindow / Optimize / Apply を通し確認する。
- 各項目は pass / warn / fail で判定する。
- warn は理由を記録し、後続タスクへ引き継ぐ。
- fail が1つでもあれば、そのPRの視覚判定は未完了とする。

## 必須証跡

- before/after スクリーンショット
- 変更対象の要点メモ
- 固定回帰コマンド実行結果（Owner実行）

## MainWindow 観点

- セクション構造が視線導線に沿って上から読める。
- 方向トグル語彙が対称で、意味誤読が起きにくい。
- Open-L/Open-R と入力欄の関係が一目で分かる。
- 主操作と副操作の階層差が見た目で識別できる。
- planned 導線が実装済み導線に見えない。

## Optimize 観点

- Optimize セクションの開始位置が明確。
- Save と Optimize の役割差が視覚的に分かる。
- 結果表示ラベルが操作結果と整合している。
- Apply との境界が明確で、誤操作導線が少ない。

## Apply 観点

- Apply セクションの開始位置が明確。
- dry-run が既定であることが読み取れる。
- Optimize 未実行時の非活性状態が分かる。
- 実行後の対象状態表示が整合している。

## スタイル統一観点

- 同種ボタンの語尾ルールが統一されている。
- primary / secondary / planned の語彙が一貫している。
- ラベル文言の粒度が揃っている。
- 英語語彙と日本語語彙の混在が意図的に管理されている。

## 判定テンプレート

- 対象PR:
- 評価日:
- 評価者:
- MainWindow: pass / warn / fail
- Optimize: pass / warn / fail
- Apply: pass / warn / fail
- スタイル統一: pass / warn / fail
- 総合判定: pass / fail
- 備考:

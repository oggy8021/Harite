# Premium request savings（プレミアムリクエストの節約）

## 目的

Copilot Chat / Premium リクエストの消費を抑え、予算内で効率的に開発支援を受けるための運用方針と具体的な節約策の草案。

## 契約

Owner は、 Github Copilot Pro を契約中。

- 2026/3/9より、Free Trial 開始。2026/4/7 Free Trial 終了
- 2026/4/8より、300 requests/Month/USD $10

## 課金の現状

### Copilot Premium Request

- 3/18  11 requests 初回発生
- 3/19   7 requests
- 3/20  65 requests
- 3/21 204 requests
- 3/22  13 requests 上限到達

対応する commit 履歴は、次の通り。

```gitlog
2026-03-18 00:15:31 — commit: test: add align/valign unit tests
2026-03-21 10:47:44 — commit: chore: release v0.1.1
2026-03-21 18:04:11 — commit: feat(gui): add phase3 ui loader prototype
2026-03-21 21:16:42 — commit: feat(gui): auto-generate manual validation artifacts
```

### 内訳

- GPT-5.3-Codex 299 req
- GPT-5.2         1 req

### Action Storae

- 2026/4/7 現在
    Billing and licensing > Usage を確認すると、0.25 GB-hr使用中（ 現状、 $0 なので問題ない ）

## 背景

5日間で 300 requests を使い果たしたため、今後の継続的な開発を実施するにも リクエスト規模を 1/6 ペースに近づける必要がある。

## git操作を Owner 自ずから実施することで節約できないか

該当の目論見の下、以下の手順書を用意した。

- docs/git-operation-help/draft-to-branch.md
- docs/git-operation-help/release-and-tag.md
- docs/git-operation-help/safe-squash-merge.md

## 即効の節約策（Quick wins）

- 会話のバッチ化：小さな質問はまとめて1回で依頼する。
- 出力長の制限：要点のみ（例：「要点3行で」）や差分のみを指定する。
- テンプレート化：レビュー、PR本文、コマンド生成の定型文を再利用する。

## 運用パラメータ（2026-04）

- 週次上限: 75 req（ハード上限）
- 日次目安: 平日 10 req / 土日 12 req（ソフト上限）
- リザーブ: 週 15 req を GUI の難所対応用に確保
- Usage確認タイミング:
  - VS Code 起動後の作業開始時
  - 作業終了時
- 例外時の予算超過: Owner 判断で実施（事前固定ルールは設けない）

## プロンプト運用ルール

- 1回のリクエストで必要な前提を全て含める（過去会話の再送を避ける）。
- デバッグや大きな解析はローカルで済ませ、失敗ログの要点のみ送る。
- 返答形式を明示（例: `- 要点のみ`, `- コマンドのみ`, `- diff のみ`）。
- 高コストモデルは GUI 実装に関する重要タスクへ優先配分する。

## ワークフローのローカル化

- 定型処理はスクリプト／Makefile／PowerShell スクリプト化してチャット依存を減らす（tests, lint, format, release 等）。
- ローカルツールで可能な検査（pytest、flake8、mypy など）は先に実行し、結果の要点のみ共有する。
- Owner も実装・検証を行い、AI への依頼は論点整理済みの内容に限定する。

## コミュニケーション習慣の改善

- 作業開始時に「本日の予算」と「必達タスク」を1メモにまとめる。
- 同じ文脈の繰り返しは避け、参照キー（コミットハッシュやファイルパス）で参照する。
- 作業終了時に Usage を記録し、翌日の目安を調整する。

## 出力コントロールと品質トレードオフ

- 高品質な設計や複雑なタスクは高性能モデルに限定し、草案や雑務は低コストモデルで処理する。
- 特に注意が必要な操作（git の破壊的操作等）は常に Owner 承認を挟む。
- Git 操作は原則 Owner 実施とし、AI はコマンド草案・レビュー・PR本文生成を担当する。

## git操作手順書の運用

- 以下の手順書は Owner が実行時に参照する教科書として利用する。
  - docs/git-operation-help/draft-to-branch.md
  - docs/git-operation-help/release-and-tag.md
  - docs/git-operation-help/safe-squash-merge.md

## 監視・指標（測定）

- 週次で実績 req を記録し、上限 75 req に対する消化率を確認する。
- 高消費だった問いを週末に3件だけ振り返り、テンプレ化して再利用する。
- 月次目標はまず「上限超過ゼロ」を優先し、削減率目標は運用安定後に再設定する。

## 実践テンプレ（短縮プロンプト例）

- レビュー要請（要点）: "レビュー要点3つで: <ファイル/関数名>"
- PR本文作成: "PR本文: 1行要約, 3行説明, チェックリスト"
- コマンド生成: "必要コマンドのみ出力。余計な説明は不要。"

## 運用上の注意

- 節約策が生産性や品質に与える影響を定期評価する。
- 節約のためにセキュリティやレビューを省略しない。

## 次のステップ（提案）

- 上記パラメータで1週間試行し、週末に実績値で見直す。
- 必要に応じて、プロジェクト固有の短縮プロンプトセットを `docs/` に追加する。

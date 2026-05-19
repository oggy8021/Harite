# Enumerator fixes applied

## docs\agent-rules.md

```diff
--- docs\agent-rules.md
+++ docs\agent-rules.md (fixed)
@@ -47,19 +47,19 @@
  - ドキュメント: `docs/<短い説明>`
 - 既存のブランチを流用して「別テーマ」を追加しないでください。別テーマや別用途の資材をそのまま同一ブランチに追加することを禁止します。
 - 前ブランチが未マージで残っている場合は、以下のいずれかを行ってから新しい作業を始めてください：
- 1。そのブランチを `main` にマージしてクローズする（PRを通じてレビュー・マージ）。
- 2。ブランチを明確にアーカイブ（例: `archive/<name>` にリネーム）し、再利用しない旨をコミットメッセージで記録する。
- 3。本当に継続が必要な場合は、そのブランチでの作業範囲を限定し、必ずオーナーの明示的承認を得る。
+ 1.そのブランチを `main` にマージしてクローズする（PRを通じてレビュー・マージ）。
+ 2.ブランチを明確にアーカイブ（例: `archive/<name>` にリネーム）し、再利用しない旨をコミットメッセージで記録する。
+ 3.本当に継続が必要な場合は、そのブランチでの作業範囲を限定し、必ずオーナーの明示的承認を得る。
 
 ## パッケージング（Deb/.deb）決定プロセス（合意手順）
 
 パッケージング方針は技術的影響が大きいため、以下の順序で合意を得ます。
 
-1。Issue を作成して目的と選択肢を整理する（例: `fpm` 試作、`dh-python` ネイティブ、`dh-virtualenv` バンドル）。
-2。各オプションのメリット・デメリットと前提（必要な Python バージョン、配布サイズ、メンテナンス負荷など）を `docs/` に短い比較表で記載する。
-3。プロトタイプ案を1つ選び、小さな PoC ブランチで実装して実機（または VM）で動作確認をする。PoC は `feature/packaging-poc-<method>` のようなブランチ名で行う。
-4。PoC の結果を Issue に報告し、オーナーと関係者の合意を得る。
-5。合意された方式に基づき、正式実装を別ブランチで行い、PR を通じてレビューして `main` にマージする。
+1.Issue を作成して目的と選択肢を整理する（例: `fpm` 試作、`dh-python` ネイティブ、`dh-virtualenv` バンドル）。
+2.各オプションのメリット・デメリットと前提（必要な Python バージョン、配布サイズ、メンテナンス負荷など）を `docs/` に短い比較表で記載する。
+3.プロトタイプ案を1つ選び、小さな PoC ブランチで実装して実機（または VM）で動作確認をする。PoC は `feature/packaging-poc-<method>` のようなブランチ名で行う。
+4.PoC の結果を Issue に報告し、オーナーと関係者の合意を得る。
+5.合意された方式に基づき、正式実装を別ブランチで行い、PR を通じてレビューして `main` にマージする。
 
 各段階で合意がない場合は、作業を中断し、必ずオーナーへ相談してください。
 

```

## docs\branch-policy.md

```diff
--- docs\branch-policy.md
+++ docs\branch-policy.md (fixed)
@@ -2,26 +2,26 @@
 
 目的: ブランチ運用の共通ルールを明示し、レビュー・CI の品質を担保する。
 
-1。ブランチ命名
+1.ブランチ命名
    - 機能: `feature/<短い説明>`
    - 修正: `fix/<短い説明>`
    - 雑務: `chore/<短い説明>`
 
-2。ワークフロー
+2.ワークフロー
    - 機能ごとにブランチを作成し、実装→PR作成→レビュー→CI通過→`main` にマージ。
    - 小規模ドキュメントは `main` へ直接コミット可（合意済み）。
    
    [注記: 現在は `docs/` の一括整備を `feature/docs-consolidate-001` 上で進める方針です。`main` への直接コミットと運用が競合しないか確認してください。]
 
-3。PR 要件
+3.PR 要件
    - PR には必ず仕様書（`docs/specs/*.md`）へのリンクを含めること。
    - CI が緑（テスト・Lint）になるまでマージ不可。
    - 少なくとも1回のオーナー承認（レビュー）を要する。
 
-4。マージ戦略
+4.マージ戦略
    - Squash マージを推奨。履歴をシンプルに保つ。チームで別戦略を使う場合はここを更新。
 
-5。ブランチ保護（推奨設定）
+5.ブランチ保護（推奨設定）
    - `main` ブランチに対して以下を有効化することを推奨:
      - Force push 禁止
      - PR によるマージのみ許可

```

## docs\branch-protection.md

```diff
--- docs\branch-protection.md
+++ docs\branch-protection.md (fixed)
@@ -17,9 +17,9 @@
   - 小さな試案（仕様メモ等）は削除しても問題ない場合は `git revert` で取り消し、履歴を残すことを推奨。
 
 - 設定手順（管理者が行う）:
-  1。GitHub → Settings → Branches → Branch protection rules を開く
-  2。`main` のルールを編集し、上記の内容になるよう調整
-  3。必要ならこのファイル（`.github/branch-protection.json`）を参照して設定を確認
+  1.GitHub → Settings → Branches → Branch protection rules を開く
+  2.`main` のルールを編集し、上記の内容になるよう調整
+  3.必要ならこのファイル（`.github/branch-protection.json`）を参照して設定を確認
 
 - 変更履歴:
   - 2026-03-14: 簡素化ルールを適用（作成者: repo maintainer）

```

## docs\development-checklist.md

```diff
--- docs\development-checklist.md
+++ docs\development-checklist.md (fixed)
@@ -26,9 +26,9 @@
 - レビューはオーナー承認が原則。Automerge禁止。
 
 ## 仕様・設計フロー
-1。機能要求を記載した仕様書（Markdown）を `docs/specs/` に作成する。テンプレートを利用。
-2。オーナー承認（ファイル内コメントまたは承認レスポンス）を得る。
-3。実装用タスクを作成し、PRに仕様リンクを貼る。
+1.機能要求を記載した仕様書（Markdown）を `docs/specs/` に作成する。テンプレートを利用。
+2.オーナー承認（ファイル内コメントまたは承認レスポンス）を得る。
+3.実装用タスクを作成し、PRに仕様リンクを貼る。
 
 ## テスト方針
 - 単体テスト: `pytest`。

```

## docs\docs-consolidation-actions.md

```diff
--- docs\docs-consolidation-actions.md
+++ docs\docs-consolidation-actions.md (fixed)
@@ -3,10 +3,10 @@
 目的: 句読点・全角/半角スペース・コマンド表記の正規化を行い、日本語ドキュメントの可読性と一貫性を高める。
 
 作業（ローカルで実行、未コミット）:
-1。主要ファイル順に句読点と不要スペースの正規化（`docs/` 下の README 相当ファイルを優先）。
-2。コマンド例の表記確認と統一（`git`/`gh` の使用例を検証）。
-3。用語統一の最終スイープ（`main`、`feature/`、`タイプミス` 等）。
-4。`docs/docs-consolidation-scan.md` と `docs/docs-consolidation-progress.md` を更新して作業ログを残す。
+1.主要ファイル順に句読点と不要スペースの正規化（`docs/` 下の README 相当ファイルを優先）。
+2.コマンド例の表記確認と統一（`git`/`gh` の使用例を検証）。
+3.用語統一の最終スイープ（`main`、`feature/`、`タイプミス` 等）。
+4.`docs/docs-consolidation-scan.md` と `docs/docs-consolidation-progress.md` を更新して作業ログを残す。
 
 ワークフロー:
 - 全てワーキングツリーでドラフト編集 → あなたがローカルで確認 → 承認を受けて commit→push→PR を実行。

```

## docs\docs-consolidation-plan.md

```diff
--- docs\docs-consolidation-plan.md
+++ docs\docs-consolidation-plan.md (fixed)
@@ -4,10 +4,10 @@
 - `docs/` フォルダ内の重複・表記ゆれ・古い情報を段階的に整理し、レビューしやすい小さな PR に分割して適用する。
 
 アプローチ（段階）
-1。スキャン: 重複や表記ゆれ候補をリストアップ（ファイルと短い説明）。
-2。優先付け: 重要度と影響範囲でタスクを並べ替え（タイプミス → 用語統一 → 構造変更）。
-3。実装: `feature/docs-consolidate-001` など `feature/` プレフィックスで小さな PR を順次作成。
-4。レビュー & マージ: CI 通過後に squash マージ、マージ後の最終確認を実施。
+1.スキャン: 重複や表記ゆれ候補をリストアップ（ファイルと短い説明）。
+2.優先付け: 重要度と影響範囲でタスクを並べ替え（タイプミス → 用語統一 → 構造変更）。
+3.実装: `feature/docs-consolidate-001` など `feature/` プレフィックスで小さな PR を順次作成。
+4.レビュー & マージ: CI 通過後に squash マージ、マージ後の最終確認を実施。
 
 短期タスク例（最初のラウンド）
 - `feature/docs-consolidate-001`: 小さなタイプミスと表記ゆれ修正（複数ファイル、1 PR）
@@ -32,9 +32,9 @@
  - 用語の統一（例: `main` の表記に統一、`docs` 表記の一貫化）
  - 見出しの句読点・スペース調整
 - ワークフロー（ローカル確認→確定→push）:
- 1。私がこのブランチ上で小さなタイプミスを数件修正してローカル状態にします（この作業は未コミットにしておきます／もしくはコミットするが push は行いません—どちらがよいですか？）。
-2。あなたがローカルで内容を確認し、修正追加や却下を指示してください。
-3。確定後、あなたの合図で私が commit → push → PR 作成します。
+ 1.私がこのブランチ上で小さなタイプミスを数件修正してローカル状態にします（この作業は未コミットにしておきます／もしくはコミットするが push は行いません—どちらがよいですか？）。
+2.あなたがローカルで内容を確認し、修正追加や却下を指示してください。
+3.確定後、あなたの合図で私が commit → push → PR 作成します。
 
 
 作成日: 2026-03-14

```

## docs\docs-consolidation-progress.md

```diff
--- docs\docs-consolidation-progress.md
+++ docs\docs-consolidation-progress.md (fixed)
@@ -12,10 +12,10 @@
 - `docs/docs-consolidation-scan.md` にスキャン結果をまとめた（ローカル）
 
 次バッチ（予定・ローカルで実行）
-1。句読点・全角/半角スペースの整備（主要ファイル優先）
-2。コマンド例の実行可能性チェックと表記統一（`gh` / `git` コマンド）
-3。`docs/agent-rules.md` と `docs/branch-policy.md` のポリシー齟齬リスト作成
-4。ローカルでの最終確認後、あなたの承認で commit→push→PR を実行
+1.句読点・全角/半角スペースの整備（主要ファイル優先）
+2.コマンド例の実行可能性チェックと表記統一（`gh` / `git` コマンド）
+3.`docs/agent-rules.md` と `docs/branch-policy.md` のポリシー齟齬リスト作成
+4.ローカルでの最終確認後、あなたの承認で commit→push→PR を実行
 
 備考
 - このファイルはローカルドラフトです。必要なら省略・追記します。

```

## docs\docs-consolidation-replacement-preview.md

```diff
--- docs\docs-consolidation-replacement-preview.md
+++ docs\docs-consolidation-replacement-preview.md (fixed)
@@ -27,8 +27,8 @@
   - "これまでの主な処理\n- `typo` → `タイプミス` など日本語表記の統一" → 文脈により句点追加の検討
 
 提案される次手順:
-1。プレビューを確認してよければ、上記ルールでワーキングツリーへ自動置換を実行します（コードブロック除外）。
-2。置換後、差分を表示してあなたに確認を求めます（必要なら個別ファイルごとにロールバック可能）。
+1.プレビューを確認してよければ、上記ルールでワーキングツリーへ自動置換を実行します（コードブロック除外）。
+2.置換後、差分を表示してあなたに確認を求めます（必要なら個別ファイルごとにロールバック可能）。
 
 注記: 本プレビューは抽出サンプルです。実際の置換はファイル全体を解析して適用します。
 

```

## docs\docs-consolidation-scan.md

```diff
--- docs\docs-consolidation-scan.md
+++ docs\docs-consolidation-scan.md (fixed)
@@ -10,13 +10,13 @@
 検出結果の抜粋（ファイル: 該当箇所の要約）
 
 優先度（提案）
-1。用語統一（`main` の表記、`タイプミス` 等） — 小PRで速攻対応
-2。ポリシー整合（agent-rules と branch-policy の齟齬確認） — レビュー必要
-3。コマンド例と手順の検証（dev-environment 等） — テスト/検証推奨
+1.用語統一（`main` の表記、`タイプミス` 等） — 小PRで速攻対応
+2.ポリシー整合（agent-rules と branch-policy の齟齬確認） — レビュー必要
+3.コマンド例と手順の検証（dev-environment 等） — テスト/検証推奨
 
 次アクション（私が行うローカルドラフト作業）
-1。小PR向けに `docs/TODOs_jp.md` と `docs/docs-consolidation-plan.md` のタイプミス・表記統一を完了（ワーキングツリーで保持）。
-2。`docs/agent-rules.md` と `docs/branch-policy.md` のポリシー齟齬候補をリスト化（ドラフト）。
-3。あなたの確認後、確定分をコミット → push → PR 作成。
+1.小PR向けに `docs/TODOs_jp.md` と `docs/docs-consolidation-plan.md` のタイプミス・表記統一を完了（ワーキングツリーで保持）。
+2.`docs/agent-rules.md` と `docs/branch-policy.md` のポリシー齟齬候補をリスト化（ドラフト）。
+3.あなたの確認後、確定分をコミット → push → PR 作成。
 
 メモ: これはローカルドラフトです。コミット／push は行っていません。

```

## docs\initial-task.md

```diff
--- docs\initial-task.md
+++ docs\initial-task.md (fixed)
@@ -3,12 +3,12 @@
 目的: 母体プログラムの仕様をリバースエンジニアリングし、Harite のコア設計（I/Oシグネチャ）を確定する。
 
 ステップ:
-1。母体プログラム `wallpaperoptimizer` をクローン/参照し、主要な計算フローを抽出する。
-2。コアの入力/出力（シグネチャ）を洗い出し、`docs/specs/core-io.md` を作成する。
-3。`pyproject.toml` とパッケージ骨格 (`src/harite/__init__.py`) を作成する。
-4。最小の CLI スケルトン（`typer` 推奨）を作成し、`harite --version` を実装する。
-5。単体テストの雛形を作成（`tests/test_core.py`）と GitHub Actions の最小CIを設定。
-6。仕様書（`docs/specs/core-io.md`）をオーナーに提出して承認を得る。
+1.母体プログラム `wallpaperoptimizer` をクローン/参照し、主要な計算フローを抽出する。
+2.コアの入力/出力（シグネチャ）を洗い出し、`docs/specs/core-io.md` を作成する。
+3.`pyproject.toml` とパッケージ骨格 (`src/harite/__init__.py`) を作成する。
+4.最小の CLI スケルトン（`typer` 推奨）を作成し、`harite --version` を実装する。
+5.単体テストの雛形を作成（`tests/test_core.py`）と GitHub Actions の最小CIを設定。
+6.仕様書（`docs/specs/core-io.md`）をオーナーに提出して承認を得る。
 
 推定所要時間: 1~3日（解析量による）。
 

```

## docs\owner-questions.md

```diff
--- docs\owner-questions.md
+++ docs\owner-questions.md (fixed)
@@ -6,14 +6,14 @@
     全質問の前提に 母体プログラム の解析を行い、同プログラムの仕様書をリバースエンジニアリングすることにより、議論の起点に立ちます。
     各回答はそのあとで精査・見直しとさせてください。一部、未回答としています。
 
-1。同一性（互換性）の受け入れ基準
+1.同一性（互換性）の受け入れ基準
    - コアロジックの入力/出力（シグネチャ）で必ず保持すべきメソッド一覧を教えてください。
    - 出力の許容差（数値の誤差やレイアウト差）についての合格基準はありますか？
 
-2。CLI互換性の範囲
+2.CLI互換性の範囲
    - 旧版の全コマンドラインオプションから「必須で残すもの」と「改善して良いもの」を指定してください。
 
-3。テスト基準と受け入れ方法
+3.テスト基準と受け入れ方法
    - 旧テストを参考にするのはコア計算ロジックのみで良いですか？
 
     回答（oggy8021 / 2026.03.11）：
@@ -25,7 +25,7 @@
      - 元のテストコードもあまり努力はしていなく無理せず試験ができるところしか実施していません。現代的なテストの実施やカバレッジ達成を期待します。私製なので 100% は求めません。
     
 
-4。使用ライブラリ／実装選好
+4.使用ライブラリ／実装選好
    - CLIフレームワークの好み（`click` / `typer` / その他）はありますか？
    - GUIの技術選定（例: GTK、Qt、Electron など）について指示はありますか？
 
@@ -35,7 +35,7 @@
      - GUIの技術選定
         同様です。
 
-5。配布・パッケージ方針
+5.配布・パッケージ方針
    - PyPI 配布を継続しますか？パッケージ名やメンテナ方針の希望はありますか？
 
    回答（oggy8021 / 2026.03.11）：
@@ -46,18 +46,18 @@
     - メンテナ方針
         Copilotと私だけの開発を想定しているため、議論ポイントが不明、用例などを示すこと
 
-6。サポート対象環境
+6.サポート対象環境
    - 最優先は Linux Mint (Xfce) で問題ありませんか？他の環境対応の優先順位があれば教えてください。
 
    回答（oggy8021 / 2026.03.11）：相違なし
 
-7。ドキュメント／言語
+7.ドキュメント／言語
    - 仕様書・README は日本語で作成する方針で良いですね（ファイルは別途英訳するか）。
 
    回答（oggy8021 / 2026.03.11）：
     ある程度揃って、仕様にブレが無いタイミングで英訳を作ります。例えば、CLI版完成などのマイルストーン毎がよいでしょう。
 
-8。承認フロー
+8.承認フロー
    - 仕様書の提出→承認の具体的な連絡方法と目安となる応答時間を教えてください。
 
    回答（oggy8021 / 2026.03.11）：

```

## docs\TODOs_jp.md

```diff
--- docs\TODOs_jp.md
+++ docs\TODOs_jp.md (fixed)
@@ -4,9 +4,9 @@
 - このファイルは `discuss/todo-planning` 上で私（アシスタント）とあなた（リポジトリ管理者）が合意・調整するための起点です。合意した作業は `main` から派生した `feature/` ブランチで実装します。
 
 短い合意手順
-1。私がこのファイルを `discuss/todo-planning` に置きました（既済）。
-2。あなたが内容を確認し、コメントや修正要求を返してください。
-3。合意したら私に作業開始を指示してください。私は小さな PR に分割して実装します。
+1.私がこのファイルを `discuss/todo-planning` に置きました（既済）。
+2.あなたが内容を確認し、コメントや修正要求を返してください。
+3.合意したら私に作業開始を指示してください。私は小さな PR に分割して実装します。
 
 重要な運用ルール（要点）
 - PR は原則 `feature/|fix/|docs/|chore/` プレフィックスで作成してください。
@@ -14,23 +14,23 @@
 - `save/*` はバックアップ扱いで PR チェックをスキップします（既設定）。
 
 合意済み作業項目（優先度順）
-1。ドキュメント整理（Docs consolidation） — `docs/` の重複・表記ゆれの統合。小さな PR に分割。
-2。`docs` 統合用 PR の作成（レビュー用）。
-3。バックアップとブランチ運用ポリシーのドキュメント化。
-4。`Improve XFCE heuristics` の調査開始（実装は別ブランチ `feature/`）。
-5。テスト強化（Docs 作成→優先ケース追加 → CI 組合せ）
+1.ドキュメント整理（Docs consolidation） — `docs/` の重複・表記ゆれの統合。小さな PR に分割。
+2.`docs` 統合用 PR の作成（レビュー用）。
+3.バックアップとブランチ運用ポリシーのドキュメント化。
+4.`Improve XFCE heuristics` の調査開始（実装は別ブランチ `feature/`）。
+5.テスト強化（Docs 作成→優先ケース追加 → CI 組合せ）
    - `docs/tests-overview.md` を作成して現状と未カバー領域を明示。
    - 優先ケースに対し parametrize した `pytest` を追加。
    - 必要なら限定的な CI ジョブを追加。
-6。CI: sdist/wheel ビルド job の追加。
-7。リリース準備チェックリスト作成。
-8。ブランチ保護・PR フローのペアセッション（スケジュール）。
-9。定期的なブランチクリーンアップ（運用ルール化）。
+6.CI: sdist/wheel ビルド job の追加。
+7.リリース準備チェックリスト作成。
+8.ブランチ保護・PR フローのペアセッション（スケジュール）。
+9.定期的なブランチクリーンアップ（運用ルール化）。
 
 短い作業フロー提案
-1。この `docs/TODOs_jp.md` を基点に `docs` の小タスクを洗い出す。
-2。各タスクを `feature/docs-consolidate-xxx` 等で実装し、PR を作成。
-3。CI 通過 → あなたが squash マージ → 私がマージ後の最終確認を実施。
+1.この `docs/TODOs_jp.md` を基点に `docs` の小タスクを洗い出す。
+2.各タスクを `feature/docs-consolidate-xxx` 等で実装し、PR を作成。
+3.CI 通過 → あなたが squash マージ → 私がマージ後の最終確認を実施。
 
 承認リクエスト（短く）
 - この文書をスタート地点として合意しますか？【yes】
@@ -45,15 +45,15 @@
 - 主な作業: 実環境の失敗再現、既存テストで再現できないケースの洗い出し、追加テストの作成、改善案の実装（`feature/xfce-heuristics-001` 等）。
 
 テスト強化の具体提案
-1。`docs/tests-overview.md` を作成: 現状のテスト一覧、目的、未カバー領域、推奨優先度をまとめる。
-2。CLI や環境依存パラメータの行列を作成し、優先度の高い組合せを決定する。
-3。優先組合せに対して `pytest.mark.parametrize` を使ったテストを追加する（小さな PR 単位で）。
-4。CI には限定数の組合せジョブを追加し、その他はローカル/オンデマンドで実行する方針を検討する。
+1.`docs/tests-overview.md` を作成: 現状のテスト一覧、目的、未カバー領域、推奨優先度をまとめる。
+2.CLI や環境依存パラメータの行列を作成し、優先度の高い組合せを決定する。
+3.優先組合せに対して `pytest.mark.parametrize` を使ったテストを追加する（小さな PR 単位で）。
+4.CI には限定数の組合せジョブを追加し、その他はローカル/オンデマンドで実行する方針を検討する。
 
 次のアクション候補（優先順）
-1。あなたがこの文書を承認 → 私が `docs/tests-overview.md` を作成して `discuss/todo-planning` に置きます（提案）。
-2。あなたが優先するテストケース群を選定 → 私が `feature/tests-coverage-001` を `main` から切ってテスト追加 PR を作成します。
-3。小さな タイプミス修正等は `feature/docs-consolidate-001` で私が作業します。
+1.あなたがこの文書を承認 → 私が `docs/tests-overview.md` を作成して `discuss/todo-planning` に置きます（提案）。
+2.あなたが優先するテストケース群を選定 → 私が `feature/tests-coverage-001` を `main` から切ってテスト追加 PR を作成します。
+3.小さな タイプミス修正等は `feature/docs-consolidate-001` で私が作業します。
 
 （補足）このファイルは `discuss/todo-planning` 上に置かれ、合意が得られ次第 `main` 起点で順次実装します。
 

```

## docs\xfce-testing.md

```diff
--- docs\xfce-testing.md
+++ docs\xfce-testing.md (fixed)
@@ -32,7 +32,7 @@
 
 セットアップ（ローカル）
 --
-1。仮想環境作成・依存インストール:
+1.仮想環境作成・依存インストール:
 ```bash
 python -m venv .venv
 source .venv/bin/activate
@@ -41,32 +41,32 @@
 python -m pip install pytest
 ```

-2。テスト実行（全体）:
+2.テスト実行（全体）:

 ```bash
 .venv/bin/python -m pytest -q
 ```

基本的な検証手順
 --

-1。表示検出の確認:
+1.表示検出の確認:

 ```bash
 .venv/bin/python -c 'from harite import workspace; print(workspace.detect_displays())'
 ```

 期待: `xrandr` が使える場合は `[(幅, 高さ), ...]` のリストが返ります。`xrandr` が無い場合は `xfconf-query` のフォールバックが試行されます。

-2。最適化処理のサンプル実行（出力ファイル確認）:
+2.最適化処理のサンプル実行（出力ファイル確認）:

 ```bash
 .venv/bin/python -m harite optimize --input tests/data --resolution 3840x1080 --output out --two-screen --l-display 1920x1080 --r-display 1920x1080
 ```

 出力例: `out/harite_wallopt_<id>.jpg`

-3。プラグイン経由での dry-run（壁紙を変更しない）:
+3.プラグイン経由での dry-run（壁紙を変更しない）:

 ```bash
 .venv/bin/python -m harite apply --plugin linux --file out/harite_wallopt_<id>.jpg
 ```

 ログに、実行されるコマンド（例: `xfconf-query` / `gsettings` / `feh`）が表示されます。

-4。XFCE の実際の適用（最終確認、自己責任）:
+4.XFCE の実際の適用（最終確認、自己責任）:

- まずプロパティ一覧を確認:

 ```bash
 xfconf-query -c xfce4-desktop -l
@@ -95,7 +95,7 @@
 
 次の手順
 --
-1。上記手順を実行のうえ結果を共有してください（成功なら次に PR マージの調整を進めます）。
-2。追加で自動化したい項目（例: `xfconf-query` のプロパティ自動検出、複数モニタの優先設定など）があれば教えてください。必要に応じて tests/ に追加のインテグレーションスクリプトを作成します。
+1.上記手順を実行のうえ結果を共有してください（成功なら次に PR マージの調整を進めます）。
+2.追加で自動化したい項目（例: `xfconf-query` のプロパティ自動検出、複数モニタの優先設定など）があれば教えてください。必要に応じて tests/ に追加のインテグレーションスクリプトを作成します。
 
 作成: Harite チーム

```

## docs\specs\core-io.md

```diff
--- docs\specs\core-io.md
+++ docs\specs\core-io.md (fixed)
@@ -105,9 +105,9 @@
 - 入出力のフォーマットテスト（JSON）を用意する。
 
 ## 次のアクション
-1。母体プログラムの該当ソース（`wallpaperoptimizer`）を解析し、代表的な入力/出力例を収集する。
-2。本ファイルを基に `tests/test_core.py` のサンプルケースを作成する。
-3。オーナーに本草案のレビューを依頼し、許容差やレイアウトモードの細部を決定する。
+1.母体プログラムの該当ソース（`wallpaperoptimizer`）を解析し、代表的な入力/出力例を収集する。
+2.本ファイルを基に `tests/test_core.py` のサンプルケースを作成する。
+3.オーナーに本草案のレビューを依頼し、許容差やレイアウトモードの細部を決定する。
 
 ---
 

```

## docs\specs\harite-foundation-spec.md

```diff
--- docs\specs\harite-foundation-spec.md
+++ docs\specs\harite-foundation-spec.md (fixed)
@@ -64,6 +64,6 @@
 - 既存の `src/harite/core.py` の two_screen パッチと合わせる形で API を整備する。まずは仕様にある最小限の振る舞いを満たし、テストを追加してからより複雑な割当ロジックを段階的に追加する。
 
 次の手順
-1。この仕様に基づき `tests/test_core_twoscreen.py` を追加してユニットテストを実装する。  
-2。`src/harite` に `workspace.py`/`imgfile.py`/`changerdir.py` の骨格を追加（必要なら単体ファイルで実装）。  
-3。CI 上でテストを実行し、挙動を確認して実装を調整する。
+1.この仕様に基づき `tests/test_core_twoscreen.py` を追加してユニットテストを実装する。  
+2.`src/harite` に `workspace.py`/`imgfile.py`/`changerdir.py` の骨格を追加（必要なら単体ファイルで実装）。  
+3.CI 上でテストを実行し、挙動を確認して実装を調整する。

```

## docs\specs\monitor-split-design.md

```diff
--- docs\specs\monitor-split-design.md
+++ docs\specs\monitor-split-design.md (fixed)
@@ -44,13 +44,13 @@
   - `apply(path_or_map, *, dry_run=True)` を受け、`path_or_map` が dict のときはキーをモニタ識別子（xrandr の `name`）として扱う。
   - 文字列のときは従来の全体適用。
 - XFCE プロパティの割当アルゴリズム
-  1.`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
-  2.`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
-  3.優先ルール:
+  1.`xrandr` で得た `Display.name`（例: `DP-1`）をモニタ候補表示名として使用。候補として `monitor{NAME}`（例: `monitorDP-1`）をプロパティ名にマッチさせる。
+  2.`xfconf-query -c xfce4-desktop -l` の出力からプロパティリストを得る（既存処理）。
+  3.優先ルール:
      - monitor 固有 (/monitor.../) にマッチするプロパティへまず書き込む。
      - 次に workspace ベースの `.../workspaceX/last-image` へ書き込む（各ワークスペースに対して同じファイルを設定）。
      - どのプロパティも見つからない場合は `last-image` / `last-single-image` の一般エントリへフォールバック。
-  4.書き込み実行:
+  4.書き込み実行:
      - `dry_run=True` の場合は実行予定コマンドをログに残すのみ。
      - `dry_run=False` の場合は、モニタ別に見つかったすべてのプロパティに対して `xfconf-query -p <prop> -s <path>` を実行し、個別の成功/失敗をログに残す。最終的には一つでも成功すれば True を返すが、個別失敗は debug/info ログで確認できるようにする。
 
@@ -76,11 +76,11 @@
 - `apply --per-monitor`（または `apply --file <composite> --auto-split --do-it`）で、linux/xfc e プラグインがモニタ別に `xfconf-query` を呼び出し、両方の画面に意図した画像が設定される（dry-run および実行時ログで確認可能）。
 
 移行計画 / 実装順序（推奨）
-1。`workspace.detect_displays()` の堅牢化（xrandr パースユニットテストを追加）
-2。画像分割ユーティリティ実装（`harite.core.split_composite_for_displays()`）とテスト
-3。CLI フラグの追加（`apply` に `--auto-split` / `--per-monitor` / `--left-file` / `--right-file`）
-4。Linux プラグインの `apply` 拡張（dict 受け取り対応）とモックベースのテスト
-5。実機検証（ユーザ）と docs 更新
+1.`workspace.detect_displays()` の堅牢化（xrandr パースユニットテストを追加）
+2.画像分割ユーティリティ実装（`harite.core.split_composite_for_displays()`）とテスト
+3.CLI フラグの追加（`apply` に `--auto-split` / `--per-monitor` / `--left-file` / `--right-file`）
+4.Linux プラグインの `apply` 拡張（dict 受け取り対応）とモックベースのテスト
+5.実機検証（ユーザ）と docs 更新
 
 セキュリティと安全性
 - `--do-it` は明示的に指定しない限り何もしない（dry-run）。

```

## docs\specs\upstream-core-mapping.md

```diff
--- docs\specs\upstream-core-mapping.md
+++ docs\specs\upstream-core-mapping.md (fixed)
@@ -46,9 +46,9 @@
 - margins が与えられた場合に貼付け位置が margin を反映していること（単純数値比較）。
 
 次の作業（優先順）
-1。`tests/test_core.py` に Two-screen のユニットテストを追加して CI を通す。テストケースは小さなダミー画像を使用する。  
-2。CLI 側で `--two-screen` / `--margins` オプションを受け取れるよう `src/harite/cli.py` を調整する。  
-3。より詳細な割当ロジック（アスペクト優先、画面タイプ照合）を仕様化し、追加テストを作成する。
+1.`tests/test_core.py` に Two-screen のユニットテストを追加して CI を通す。テストケースは小さなダミー画像を使用する。  
+2.CLI 側で `--two-screen` / `--margins` オプションを受け取れるよう `src/harite/cli.py` を調整する。  
+3.より詳細な割当ロジック（アスペクト優先、画面タイプ照合）を仕様化し、追加テストを作成する。
 
 参照: 母体の実装は `wallpaperoptimizer/WallpaperOptimizer/Core.py` を参照のこと。
 

```

## docs\specs\upstream-full-analysis.md

```diff
--- docs\specs\upstream-full-analysis.md
+++ docs\specs\upstream-full-analysis.md (fixed)
@@ -63,19 +63,19 @@
   - 密結合（Core が WorkSpace、ChangerDir、Command を直接呼ぶ）によりライブラリ化が難しい。
 
 移植方針（推奨）
-1。設計の抽象化: 上流のドメイン知識（スクリーン分割、アスペクト判定、余白ルール、配置順序）をインタフェースとして抽出する。
-2。実装は現代的な Python3 + PIL（Pillow） + pure 関数／小クラスで再実装。副作用（壁紙セット等）は CLI プラグイン層に委譲する。
-3。`WorkSpace` は `xdpyinfo` に依存しない API を提供（例: 明示的にスクリーン解像度を渡せるようにする）。
-4。GUI コードは参考実装に留め、Harite 本体はライブラリとしてテスト可能に保つ。
+1.設計の抽象化: 上流のドメイン知識（スクリーン分割、アスペクト判定、余白ルール、配置順序）をインタフェースとして抽出する。
+2.実装は現代的な Python3 + PIL（Pillow） + pure 関数／小クラスで再実装。副作用（壁紙セット等）は CLI プラグイン層に委譲する。
+3.`WorkSpace` は `xdpyinfo` に依存しない API を提供（例: 明示的にスクリーン解像度を渡せるようにする）。
+4.GUI コードは参考実装に留め、Harite 本体はライブラリとしてテスト可能に保つ。
 
 受け入れ基準（移植の成功判定）
 - Harite の再実装が母体の代表ケース（左右 2 画面、マージンあり、fixed オプションなど）で期待値（配置矩形）とスケールが許容差内で一致すること。
 - 副作用（壁紙変更）は明示的オプションで有効化でき、デフォルトでは副作用がないこと。
 
 次の具体作業（A→B→C の流れ）
-1。A (完了): 上流の全主要モジュールを解析しレポート化（本ファイル）。
-2。B (これから): Harite 側で再実装すべき基盤 API（WorkSpace/ImgFile/Bounds/Config/ChangerDir）を仕様化し、テストケースを設計する。
-3。C (後続): 仕様に基づき Harite に実装を追加、ユニットテストと CI を通じて検証する。
+1.A (完了): 上流の全主要モジュールを解析しレポート化（本ファイル）。
+2.B (これから): Harite 側で再実装すべき基盤 API（WorkSpace/ImgFile/Bounds/Config/ChangerDir）を仕様化し、テストケースを設計する。
+3.C (後続): 仕様に基づき Harite に実装を追加、ユニットテストと CI を通じて検証する。
 
 付記
 - 解析はソース読取ベースでの静的解析です。実行時の挙動（例: xprop の出力バリエーションや外部コマンドの挙動）は実環境での確認を推奨します。

```

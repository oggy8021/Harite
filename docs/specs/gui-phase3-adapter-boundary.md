# GUI Phase 3 Adapter Boundary（実UI依存の分離方針）

最終更新: 2026-03-21

## 目的

- 実UIフレームワーク依存を adapter 層に隔離し、既存ロジックの再利用性を維持する。
- headless CI でも import/run が壊れない構成を明確化する。

## 設計原則

- `src/harite/gui/views/main_window.py` は framework-neutral のまま維持する。
- UIフレームワーク依存コードは `src/harite/gui/adapters/` 配下に限定する。
- adapter は View state の入出力だけを担い、core 実行や validation を持たない。
- `src/harite/gui/app.py` は adapter の起動点になるが、adapter 不在時は現行 skeleton へフォールバック可能とする。

## レイヤ責務

1. Domain/Controller 層

- 対象: `OptimizeController`, `OptimizeFormState`, `MainWindow` ロジック
- 役割: 入力検証、最適化実行、apply導線、ログ/エラー状態管理
- 制約: UIライブラリ（GTK/PySide 等）を import しない

1. Adapter 層（新設）

- 対象: 例 `src/harite/gui/adapters/gtk_main_window.py`
- 役割: UIイベントを `MainWindow` ハンドラへ中継、View state を widget へ反映
- 制約: business logic を持たない

1. Entrypoint 層

- 対象: `src/harite/gui/app.py`
- 役割: 実行モード選択（headless-safe / adapter enabled）
- 制約: adapter import 失敗時にクラッシュしない

## Adapter インターフェース（最小）

- `initialize()` : UI初期化（widget生成、signal接続）
- `render(state)` : `MainWindow` の状態（can_optimize, last_error, logs など）を反映
- `bind_handlers(main_window)` : signal -> handler の接続
- `run_loop()` : フレームワークのメインループ開始

## headless CI 継続条件

- `python -m harite.gui.app` 相当の import/run が GUI backend 未導入環境で失敗しない。
- `tests/gui/test_app_entrypoint.py` を維持し、adapter 導入後も同等スモークを通す。
- adapter 実装自体のテストは optional に分離し、backend 未導入環境では skip 可能にする。

## 実装順（Step 1 以降）

1. adapter 境界文書の確定（本書）
2. `gui-signal-mapping` の dropped 項目再分類（Phase 3対象決定）
3. state/render バインド仕様の明文化
4. adapter 読み込みのみの最小プロトタイプ追加

## 非目標

- Phase 3 で tray/indicator/daemon を復活させない。
- Glade レイアウトの完全互換を要求しない。

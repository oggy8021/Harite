# GUI Phase 2 タスクリスト（実行制御と品質強化）

最終更新: 2026-03-21

## 目的

- Phase 1 で実装した signal 受け口を、実運用向けに堅牢化する。
- GUI の入力検証・CLIプレビュー・適用導線をテストで固定する。

## スコープ

- `src/harite/gui/controllers/optimize_controller.py`
- `src/harite/gui/services/cli_mapper.py`
- `src/harite/gui/views/main_window.py`
- `tests/gui/`

## タスク

- [x] Step 1: `OptimizeController` の入力検証強化（margins 形式・値の検証）
- [x] Step 1: `OptimizeController` と `cli_mapper` の専用ユニットテスト追加
- [x] Step 2: `MainWindow` のフォーム更新系ハンドラで境界値の挙動を追加テスト
- [x] Step 3: `on_apply_dry_run` / `on_apply_do_it` の失敗パターン（plugin失敗/未登録）を拡充テスト
- [x] Step 4: GUI起動エントリからの最小スモーク（import/run）確認をCI向けに整理

## DoD

- Phase 2 で追加した検証ロジックに対してユニットテストがある。
- GUI経由の optimize/apply の代表失敗パターンが再現テスト化されている。
- `docs/specs/gui-signal-mapping.md` と矛盾しない。

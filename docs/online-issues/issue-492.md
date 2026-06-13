# Issue #492

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/492>
- opened: 2026-06-13
- title: `QtsystemTrayIconからの settings や color ダイアログ呼び出しにおいて main window も表示されてしまう`
- labels: `bug`
- 報告: v2.0.0 リリース直後（オーナー実機）

## 事象

- システムトレイ（`QSystemTrayIcon`）のコンテキストメニューから **Settings** または **BaseColor** を選ぶと、対応ダイアログに加えて **Main Window も一緒に表示** される。
- GTK 時代は対処済みだった挙動が、Qt 移行後に再発している（オーナー認識）。

## 期待

- トレイからの各操作では **該当ダイアログのみ** が開く。Main Window を道連れに表示しない。

## 分類

- `bug` — tray 導線の回帰（GTK 修正の Qt 未移植）

## 関連

- 正本: [harite-gui-spec.md §7](../specs/gui/harite-gui-spec.md) — tray menu 項目（Settings / BaseColor / About は dialog open 補助導線）。**main window 同時表示の可否は未記載** → 修正時に spec 追記候補。
- 実装:
  - `src/harite/gui/adapters_qt/qt_tray_adapter.py` — `_on_open_settings`, `_on_open_color`, `_present_main_window`, `_invoke_backend`
  - `src/harite/gui/adapters_qt/qt_dialogs.py` — Color ダイアログ
  - `src/harite/gui/adapters/gui_runtime_settings_dialogs.py` — Settings ダイアログ open 経路
- テスト: `tests/gui/test_qt_tray_adapter.py`（backend 呼び出しのみ検証。**main window 非表示は未検証**）
- 他 Issue: （なし）

## 取り込み方針

- 現時点の判断: **近端着手**（単純な flag 修正で直る見込み。v2.0.0 後の最初の tray 回帰）
- スコープ: Settings / BaseColor の tray 導線。**About も同型**（`present_main_window=True`）のため一緒に確認する。
- 次: 調査メモの修正方針で impl → `test_qt_tray_adapter` に window 非表示 assertion 追加 → gui-spec §7 に期待挙動を1行追記。

## 調査メモ

### 原因（コード上ほぼ確定）

`qt_tray_adapter.py` で Settings / Color（および About）の handler が **`present_main_window=True`** を渡している。

```409:416:src/harite/gui/adapters_qt/qt_tray_adapter.py
    def _on_open_settings(self, *_args: Any) -> None:
        self._invoke_backend("_on_settings_clicked", present_main_window=True)

    def _on_open_color(self, *_args: Any) -> None:
        self._invoke_backend("_on_color_clicked", present_main_window=True)

    def _on_open_about(self, *_args: Any) -> None:
        self._invoke_backend("_on_about_clicked", present_main_window=True)
```

`_invoke_backend` は `present_main_window` が真のとき `_present_main_window()`（`show` / `raise_` / `activateWindow`）を **ダイアログ open 前** に実行する。

### GTK 側

- v2.0.0 で GTK backend / `tasktray_adapter` は削除済み。比較用の現行コードはリポジトリ内に残っていない。
- オーナー報告どおり GTK では「ダイアログのみ」が正だったとする。

### 修正の当たり

| 操作 | 現行 `present_main_window` | 期待 |
| --- | --- | --- |
| Visible / ダブルクリック toggle | 必要（意図的に window 表示） | 現状維持 |
| Start / Stop slideshow | `False` | 現状維持 |
| Settings / BaseColor / About | `True` ← **問題** | **`False`** に変更 |

### テストギャップ

- `test_on_settings_calls_backend` / `test_on_color_calls_backend` は `_StubWindow` を渡すが、`show` が呼ばれないことは assert していない。

### memo（オーナー）

- 挙動: 道連れに Main Window が表示される。
- GTK で対処済みだった内容が Qt 側で再現されていなかった。

## resolution

（未解決）

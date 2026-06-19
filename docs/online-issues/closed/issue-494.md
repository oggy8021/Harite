# Issue #494

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/494>
- opened: 2026-06-13
- title: `QtsystemTrayIconから見える Slideshow実行状態が Main Windowと異なっている／ステータスアイコンも斜線入りでずれている`
- labels: （なし）
- 報告: v2.0.0 リリース直後（オーナー実機・XFCE）
- 関連セッション: [#493](issue-493.md) の tick 失敗（OP_LOG **12:53** 頃）**後の状態**と見られる

## 事象

[#493](issue-493.md) で slideshow tick が失敗したあと、**同一セッション内**で表示が食い違う。

| 表面 | 見え方 | 解釈 |
| --- | --- | --- |
| **Tray メニュー** | Start Slideshow が有効、Stop が無効 | **stopped** 扱い |
| **Tray アイコン** | 斜線入り（`harite_off` 系） | **stopped** 扱い |
| **Slideshow タブ** | Start 無効・Stop 有効 | **running** 扱い |
| **Main Window 下部** | `Slideshow: running` | **running** 扱い |

スクリーンショット: [GitHub Issue #494](https://github.com/oggy8021/Harite/issues/494) 添付画像。

## 期待

- Tray / タブ / footer / Start-Stop ボタン / トレイアイコンが **同一の slideshow 状態** を示す。
- stopped なら全体が stopped（斜線アイコン含む）。running なら全体が running。

## 分類

- `bug` — owner（MainWindow モデル）と Qt backend（ラベル・ボタン）の **二重状態** の同期漏れ
- `investigation` — #493 失敗経路がトリガーか（ほぼ確実）

## 関連

- [#493](issue-493.md) — tick 失敗で `main_window.slideshow_running = False` になるが backend 未同期
- [MAT-02](../maturation-20260609-qt-common.md#mat-02--slideshow-タブ-stopped-と-footer-running-の不一致) — タブ vs footer 不一致（#445 で表示整合修正済みだが **別経路の desync**）
- 実装:
  - `src/harite/gui/adapters_qt/qt_tray_adapter.py` — `refresh`, `_slideshow_running`（**owner 参照**）
  - `src/harite/gui/adapters_qt/qt_widget_helpers.py` — `_slideshow_display_state`（**backend._slideshow_running 参照**）
  - `src/harite/gui/adapters_qt/qt_backend.py` — `_on_slideshow_timer_event`（tick 失敗時 sync なし）
  - `src/harite/gui/tray_icon_theme.py` — running/off アイコン切替
  - `src/harite/gui/adapters/gui_runtime_sync.py` — `sync_slideshow_state_from_owner`
- 他 Issue: [#492](issue-492.md)（tray 別件）

## 取り込み方針

- 現時点の判断: **#493 とセットで着手**（tick 失敗時の状態同期が根）
- スコープ:
  1. `on_slideshow_tick` が `False` を返したとき `qt_backend` へ `sync_slideshow_state_with_feedback_from_owner`（または stop 相当の一括同期）
  2. 回帰テスト: tick 失敗後に tray / tab / footer / ボタンが一致すること
- 次: #493 修正方針確定後に本件を同 PR または直後 PR で閉じる

## 調査メモ

### 状態の読み取り元が二系統

| コンポーネント | 参照先 |
| --- | --- |
| Tray（1s poll） | `_get_connected_owner()` → **`owner.slideshow_running`** |
| Tab title / footer / Stop ボタン | **`backend._slideshow_running`**（`sync_slideshow_state_from_owner` 経由で更新） |

### #493 失敗後のコード経路

```text
on_slideshow_tick → apply 失敗
  → owner.slideshow_running = False
  → owner._update_slideshow_summary_display()  （モデル文字列のみ "stopped"）
  → return False

qt_backend._on_slideshow_timer_event
  → callback() が False
  → _stop_slideshow_timer() のみ
  → sync_slideshow_state_from_owner なし  ← backend._slideshow_running は True のまま
```

Tray は owner が `False` なので **stopped + 斜線アイコン**。  
タブ / footer / Stop ボタンは backend が `True` のままなので **running**。

### トレイアイコンの斜線について

`tray_product_icon_basename(slideshow_running=False)` → `harite_off.svg`（斜線入り）。  
**アイコン単体のバグではなく**、owner が stopped・UI が running という **状態不整合の症状** と読む。

### MAT-02 との違い

- MAT-02: タブ `(stopped)` vs footer `running`（両方 backend 系の更新タイミングずれ）
- 本件: **Tray（owner）vs Main UI（backend）** — Qt 移行後の tray poll 設計と timer 失敗ハンドラの組み合わせ

### 修正の当たり（実装時メモ・未着手）

```python
# qt_backend._on_slideshow_timer_event 内、result is False のとき例:
owner = self._get_handler_owner("on_slideshow_tick")
if owner is not None:
    self._sync_slideshow_state_with_feedback_from_owner(owner)
```

または tick 失敗を「停止」ではなく pause（#493 方針）に変える場合は、owner / backend 両方の意味を揃えてから同期。

### memo（オーナー）

- #493 関連。issue 記載 12:53 なので先の tick 失敗の状態影響と見える。
- Tray: Start 有効 = stopped。Tab: Stop 有効 = running。Footer: running。

## resolution

- **2026-06-19 — v2.0.1（PR #499）**
- tick 失敗時に `owner` から `_sync_slideshow_state_with_feedback_from_owner` を呼び tray / main / footer を同期。

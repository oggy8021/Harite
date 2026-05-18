# Harite Watch XFCE Stability Incident 2026-05-18

最終更新: 2026-05-18

## 位置づけ

- 本書は XFCE 実機での watch 安定化試験中に観測した overnight 事象の切り分けメモである。
- WS2 packaging / release の論点ではなく、GUI watch の runtime behavior と error presentation の局所不具合として扱う。
- watch の常設仕様本体は docs/specs/watch/harite-watch-minimum-spec.md を参照する。

## 観測事象

- XFCE 実機で watch interval を 1800s に設定し、一晩連続動作させた。
- 翌朝、Main Window 下端に次の 2 行が出ていた。
  - 1 行目: `Watch: watch tick auto-split prepare failed`
  - 2 行目: `Error: watch tick auto-split prepare failed`
- 同時に Watch Start が無効のままとなり、その場では再開できない状態に見えた。

## 切り分け結果

### 1. 同じ文言が 2 行に出る理由

- src/harite/gui/views/main_window.py の `_set_status()` は `status_message` と `last_error` を別で持つ。
- ただし watch tick 失敗時は、同じ文字列を `message` と `error` の両方へ入れている。
- GTK runtime 側では src/harite/gui/adapters/gtk_runtime_sync.py の `sync_feedback_from_owner()` が `status_message` を 1 行目、`last_error` を 2 行目へ流し、src/harite/gui/adapters/gtk_runtime_widget_access.py が 2 行目へ `Error:` を付けて表示する。
- したがって、今回の 2 行同文は偶発ではなく、現在の状態同期と表示仕様の組み合わせで起きる。

### 2. Watch Start が無効のままになる理由

- watch tick 失敗時は `watch_running = False` に戻している。
- しかし同じ失敗経路で `_refresh_action_availability()` を呼んでいない。
- Watch Start の有効条件は `watch_running` を参照して再計算されるため、内部状態は停止済みでも UI 側のボタン状態だけ古いまま残る可能性が高い。
- これは local UI state synchronization bug とみなしてよい。

### 3. `watch tick auto-split prepare failed` の意味

- この文言は watch tick 中の auto-split 準備段で発生した `ValueError` をまとめて吸い、固定文言へ畳んだものである。
- 現状の画面文言だけでは根因は確定できず、元の `ValueError` 文言が失われている。
- 発生源候補は次の 3 点である。
  - `_build_watch_two_screen_state()`
  - `controller.run_optimize()`
  - `resolve_apply_settings(..., apply_mode="per-monitor-auto-split")`

## 現時点で最も疑わしい原因

- overnight の XFCE 実機という条件では、display 検出の変動が第一候補である。
- `resolve_apply_settings()` は `per-monitor-auto-split` 時に「検出 display が 2 枚未満なら失敗」とする。
- watch start 時は通っても、watch tick 時に display 状態が変化すると `per-monitor apply requires at least two detected displays` 側で落ちうる。
- ただし現状は固定文言へ畳んでいるため、これが実際の根因かどうかを UI だけでは判別できない。

## 製品品質上の論点

- 2 行同文は error presentation として質が低い。
- tick という語は owner / end user 観点では分かりにくく、失敗理由の理解に寄与しない。
- watch tick failure 後に再開ボタンが戻らない挙動は、単なる文言問題ではなく操作継続性の欠陥である。
- 固定文言によって元の `ValueError` 理由が失われるため、実機異常の再判定が難しい。

## 修正方針

- 本件は WS2 へ送らず、watch hotfix として扱う。
- 用語方針として、user-facing な画面文言では `tick` を使わず `cycle` を使う。日本語説明では「定期更新」または「周期処理」と読む。
- 優先度は次の順とする。
  - watch tick failure 後に Watch Start を再有効化する。
  - auto-split prepare failed を根因つきの文言へ寄せる。
  - 同タイミングの 2 行同文を抑制する。
- 直す主対象は src/harite/gui/views/main_window.py とする。
- 必要に応じて src/harite/gui/adapters/gtk_runtime_sync.py または src/harite/gui/adapters/gtk_runtime_widget_access.py の表示同期も調整対象に含める。

## この hotfix で採る表示方針

- watch cycle 中に display 検出が一時的に崩れた場合は、即停止ではなく `paused` として継続待機し、次周期で自動再試行する。
- watch cycle failure 後の停止系ケースでは Watch Start を再有効化し、その場で再開できる状態へ戻す。
- user-facing な watch 失敗文言は `watch cycle ...` へ寄せる。
- auto-split 準備失敗では固定文言だけで終えず、元の `ValueError` 理由を後ろに残す。
- owner 同期で `status_message` と `last_error` が同文の場合は、2 行目の `Error:` 側を抑制する。

## 作業区分

- 分類: hotfix 候補
- 主責務: GUI watch runtime / error presentation
- 非該当: WS2 packaging / release evidence

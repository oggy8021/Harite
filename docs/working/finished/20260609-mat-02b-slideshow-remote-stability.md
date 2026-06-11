# MAT-02b — NDL / CODH slideshow 不安定（壁紙未更新・tick 不発）

親: [maturation §MAT-02b](../online-issues/maturation-20260609-qt-common.md)  
前提: [MAT-08 viper3 観測](20260609-mat-08-viper3-slideshow-op-observation.md)（2026-06-09）

## 事象（オーナー確定）

**JMA のみ安定。** NDL / CODH は JSONL 上 GET 成功でも、実機では期待 tick で壁紙が更新されない・tick 自体が来ない。

| 区分 | 実機 |
| --- | --- |
| JMA | 問題なし |
| NDL / CODH | 不安定（20:04 / 20:20 / 20:49 不発、CODH 20:37 GET OK だが未反映 等） |

## 根因整理（コード照合）

### 1. `--none--` が path を残す（観測汚染・HIGH）

- **旧仕様:** gui-spec §4.2 — `— none —` は source id のみクリア、path 維持
- **実害:** `— none —` でも当該 side の `slideshow_srcdir_*` が残り、Start / tick が **幽霊 side** で動く（viper3 では R で観測、L でも同操作は起こりうる）
- **対応:** `on_select_slideshow_source` で **L/R 対称**に none 時 path もクリア（`Clear-L/R` と同型）
- **follow-up（#464 後）:** Profile combo を `— none —` にしても L/R path が残る — `on_select_slideshow_profile(None)` で **両 Srcdir を Clear-L/R 同型**にクリア（`fix/profile-none-clears-srcdir-lr`）

### 2. op log が GET まで（観測限界・HIGH）

- v0 は remote HTTP のみ。`on_slideshow_tick` 発火・optimize・apply 成否が見えない
- **対応:** `SLIDESHOW_TICK` / `SLIDESHOW_APPLY` ステップを追加

### 3. Linux 同一出力 path の DE キャッシュ（CODH 乖離・HIGH）

- tick 毎に `harite_slideshow.jpg` へ上書き。XFCE `xfconf-query` / `gsettings` は **同一 path** 再設定で再描画しないことがある
- **対応:** apply 直前に出力ファイルを `touch` して mtime を更新（feh / xfconf の再読込促進）

### 4. tick apply 失敗で timer 停止（tick 不発・MEDIUM）

- `on_slideshow_tick` が `False` → Qt timer stop → 以降の 10 分 tick が来ない
- 1 回の apply 失敗がセッション全体を止める。NDL「20:04 が来ない」の説明になりうる
- **現状維持**（今回は観測強化を優先）。再発時は op log で apply 層を確認

### 5. NDL は tick で画像取得しない（設計ギャップ → 改修）

- 旧 source-spec §12.4 — NDL は Start/Refresh のみ sync。tick は **同一 `latest.jpg` の再 apply**
- op2（2026-06-10）で再確認。[op2 観測メモ](20260610-mat-08-viper3-slideshow-op2-observation.md)
- **対応:** `ndl_slideshow_tick`（`fix/ndl-slideshow-tick-sync`）。tick 不発とは別軸

## 本 PR（`fix/mat-02b-slideshow-stability`）

| 変更 | ファイル |
| --- | --- |
| none → path クリア | `main_window.py`、gui-spec §4.2 |
| op log tick/apply | `main_window.py`、`slideshow_op_log` 利用 |
| Linux touch before apply | `plugins.py` |
| テスト | `test_c02_source_registry_gui.py`、`test_slideshow_op_log.py` |

## follow-up

| 項目 | 状態 |
| --- | --- |
| NDL sync-on-tick | **実装中** — `fix/ndl-slideshow-tick-sync` |
| tick apply 失敗時の pause 継続 vs 完全 stop | 未着手 |
- XFCE で touch 不足時の二段 set（空→path）

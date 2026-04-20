# GUI Phase 7 Workstream 3: watch の責務再定義

最終更新: 2026-04-20

## 位置づけ

- 本書は Phase7 product alignment における Workstream 3 の詳細メモである。
- 目的は、CLI watch と GUI watch の責務境界、接続方式、close 前に残る論点を固定することにある。
- index は [docs/specs/gui/gui-phase7-product-alignment-planning.md](docs/specs/gui/gui-phase7-product-alignment-planning.md) を参照する。

## 現時点の整理結果

- GUI watch は、CLI watch の front-end として扱う。
- GUI が独自の watch orchestration を持つ理由は弱く、独自 engine は採らない。
- failure-continue policy は GUI 独自に再設計せず、CLI watch の既存方針を既定挙動として継承する。
- L/R 同時 watch は explicit mapping ではなく、2 入力 compose -> `per-monitor-auto-split` の主導線へ落とす。
- watch 中の plugin apply は、single-source では通常 apply、L/R 同時 watch では auto-split apply として接続する。
- watch の生成物は current `output_dir` 配下へ出力し、出力先表示を GUI 上に明示する。
- cleanup は「次世代 apply 成功時だけ前世代を掃除」「stop 時は現世代を保持」「失敗生成物は残置」とする。

## 接続方式メモ

- GUI から CLI `watch` command をサブプロセス起動する案は採らない。
- watch runner あるいは共有 watch service を同一 process 内で利用する front-end とする。
- `run_watch_cycles()` の blocking ループは GUI main thread へ載せず、1 cycle API を GUI timer event で刻む方式を採る。

## `watch.py` API 分割案

- 責務を次の 3 層に分けて読む。
  - 入力列挙: `collect_watch_input_images()`
  - 次画像選択: `select_next_image()`
  - 反復制御: `run_watch_cycles()`
- GUI timer event 方式へ接続するため、CLI 用の薄い orchestration は残しつつ、その内部で使う 1 cycle 単位 API を持つ構成が自然である。

```python
@dataclass
class WatchCycleState:
    index: int = 0
    previous_selected: Path | None = None
    completed: int = 0


def run_watch_cycle(
    images: list[Path],
    mode: str,
    state: WatchCycleState,
) -> tuple[Path, WatchCycleState]:
    ...
```

## GUI / CLI から見た呼び方

- GUI:
  - `Watch Start` で source dir 検証、画像一覧読み込み、state 初期化、timer 登録。
  - 1 tick ごとに `run_watch_cycle()` を 1 回呼び、plugin apply と UI 更新を行う。
  - `Watch Stop` で timer を解除し、state を停止状態へ戻す。
- CLI:
  - current `watch()` command の public 仕様を維持しつつ、内部では `run_watch_cycle()` を反復する薄い wrapper に整理する。

## テスト観点

- `WatchCycleState` 初期状態から 1 回進めたときの状態遷移。
- sequential / random / single-image / 空配列 / 未知 mode の挙動。
- `run_watch_cycles()` の public 挙動維持。
- GUI start/stop の停止性、current 表示更新、apply failure との境界。

## 残作業

- manual validation と close 文面の確定が中心。
- 新たな責務分割の再検討は行わない。
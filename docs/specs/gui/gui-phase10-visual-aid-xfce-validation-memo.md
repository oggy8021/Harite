# GUI Phase10 Visual Aid XFCE Validation Memo

最終更新: 2026-05-12
対象: Phase10 visual aid implementation

## 目的

- Phase10 2nd planning で決めた message surface の初回実装を、XFCE 実機で短時間に確認する。
- Windows 上の静的確認や import 疎通では代替できない見た目差分を、owner が正本環境で判定する。

## 前提

- 実機確認の正本は XFCE 実ウィンドウとする。
- Windows は今回の visual aid 判定の正本に使わない。
- 今回の確認対象は icon library や全面的な再装飾ではなく、message surface と disabled 条件の初回導入である。
- Settings dialog の 4 操作の意味づけは [docs/specs/gui/gui-phase10-3rd-planning.md](docs/specs/gui/gui-phase10-3rd-planning.md) で扱う。
- Settings dialog notice は今回の visual aid 実機確認対象から外し、Phase10 3rd planning 側へ先送りする。

## 確認対象

1. MainWindow 最下部に dedicated messaging row が追加され、footer summary と視覚的に分離されていること。
2. Color dialog は native GTK chooser を許容し、fallback custom dialog が使われる場合に限り最下部 notice エリアが読めること。
3. watch summary が footer summary 側に残り、message row と役割分担できていること。
4. resolution 未確定時に Optimize が進めないこと。
5. Watch Start が SrcdirL / SrcdirR の両方と正の interval が揃うまで進めないこと。

## 事前メモ

- 今回の実装は first visible pass であり、色・余白・文言の最終調整は実画面を見た後に行う。
- したがって今回は pass/fail だけでなく、違和感があれば Notes に短く残す。

## 任意の事前回帰

必要なら実機起動前に次だけ実行する。

```PowerShell
python.exe -m pytest -q tests/gui/test_main_window_signals.py tests/gui/test_gtk_runtime_backend.py
```

見る点:

- 追加した disabled 条件の回帰が落ちていないこと。
- fake GTK backend の構築が separator 追加で壊れていないこと。

## XFCE 実機確認手順

1. GUI 起動

```PowerShell
python -m harite.gui.app --bind-ui-backend --present-ui-window
```

補足:

- `harite-gui` でも起動確認してよい。
- 正本確認では module 起動と script 起動のどちらでもよいが、記録時は実際に使った方を Notes に残す。
- color dialog は native GTK chooser が使える環境では native 表示を許容する。
- owner 実観察では `python -m harite.gui.app` と `harite-gui` の両方で起動確認している。

期待:

- MainWindow が起動する。
- 起動直後に footer summary と dedicated messaging row が上下 2 段として見える。

1. MainWindow の message surface 確認

- footer summary 側で Status と Watch summary が読めることを確認する。
- その直上に message 専用 1 行があり、summary 行と混ざって見えないことを確認する。
- 区切り線または視覚的な切れ目があり、message row が footer summary の続きに見えすぎないことを確認する。

1. Optimize disabled 条件

- resolution が未確定になる条件を作れる場合、その状態で Optimize が押せないか、少なくとも先へ進まないことを確認する。
- 正本環境で自動検出や close 時復帰により再現困難な場合は、その事実自体を guard 済みとして Notes に残してよい。
- owner 実観察では、正本環境で自動検出してしまい、Settings で空にしても close 背景で値を復帰させるため、未確定状態の再現は困難だった。
- ここでいう Notes は、本メモの `### Notes` 欄または PR コメント短縮版の `Notes:` 行を指す。

1. Settings dialog notice

- Settings dialog notice は今回の実機確認対象から外す。
- owner 実観察では `Settings: open` 相当だけが見えているが、notice 行なのか action row なのかの切り分けも含めて、visual aid 実装としては本段では追わない。
- Settings dialog の surface / state 表示 / action semantics は [docs/specs/gui/gui-phase10-3rd-planning.md](docs/specs/gui/gui-phase10-3rd-planning.md) 側で再整理する。

1. Color dialog notice

- Color を開く。
- native GTK chooser が開く環境では、その native dialog が開くことを確認する。
- owner 実観察では native chooser 下端には `キャンセル` と `選択` ボタンだけが見え、custom notice 行は見えていない。この時点では visual aid として未解消扱いであり、ここから先へ進めない。
- fallback custom dialog が開く環境での dialog 最下部 state/notice 行の確認は、color 向け messaging 実装を積んだ 2 回目の commit/push 後に再実機確認する。
- native chooser の入力欄に `red`、`black`、`hoge`、`#FFFF00000` などを入れたときは、無視を許容観察にせず、`invalid background color` 等の message が main status / color state に出ることを次回確認する。
- native / fallback のどちらが使われたかを Notes に残す。

1. Watch start disabled 条件

- 起動直後は Watch Start が押せないことを確認する。
- SrcdirL のみ設定した状態では、まだ Watch Start が押せないことを確認する。
- SrcdirL / SrcdirR の両方を設定し、interval が正なら Watch Start が押せることを確認する。
- watch 起動後は Watch Stop が押せることを確認する。
- owner 実観察では上記はすべて OK で、interval の上限値は 86400 で丸め込みが入ることも確認されている。
- 現時点では、watch は今回の確認項目の中で唯一素直に pass と言ってよい。

## スクリーンショット推奨

- MainWindow 全景 1 枚
- Settings dialog 1 枚
- Color dialog 1 枚
- Watch start disabled の状態が分かる 1 枚

## 判定テンプレート

- 対象PR: [number]
- 評価日: [YYYY-MM-DD]
- 評価者: owner
- 備考: Color dialog notice は native chooser 利用時 `n/a` としてよい。

### 判定結果

- MainWindow dedicated message row: pass/warn/fail
- Settings dialog notice: n-a
- Color dialog notice: pass/warn/fail/n-a
- Optimize disabled condition: pass/warn/fail
- Watch start disabled condition: pass/warn/fail
- Overall: pass/warn/fail

判定メモ:

- `Overall: pass` は、`MainWindow dedicated message row`、`Color dialog notice`、`Optimize disabled condition`、`Watch start disabled condition` が pass であることを前提とする。
- `Settings dialog notice` は今回 `n/a` とし、Overall 判定には含めない。
- `Color dialog notice` が native chooser 利用で `n/a` の場合は、そのことを Notes に残したうえで pass 判定の妨げにしない。

### Notes

- MainWindow:
- Settings:
- Color:
- Optimize gating:
- Watch gating:

### 2026-05-12 owner 観察メモ

- 起動導線: `python -m harite.gui.app` と `harite-gui` の両方で起動確認済み。
- Optimize gating: 正本環境では resolution 未確定状態の再現が困難。自動検出と close 時復帰により、結果的に guard 済みの挙動として観察された。
- Settings: `Settings: open` 相当のみ視認。ただし本段では完全に先送りし、判定対象から外す。
- Color: native chooser では下端に `キャンセル` / `選択` のみ表示。旧観察では不正文字列や長すぎる色コードが無視されていたため未解消扱いとし、color messaging 実装を積んだ後に再実機確認する。
- Watch gating: 起動直後 / 片側のみ / 両側設定後 / 起動後停止の各条件は OK。interval 上限は 86400 で丸め込みあり。現時点で唯一素直に pass と言える。

## PR コメント短縮版

```md
### Phase10 visual aid XFCE check
- MainWindow dedicated message row: pass/warn/fail
- Settings dialog notice: n-a
- Color dialog notice: pass/warn/fail/n-a
- Optimize gating: pass/warn/fail
- Watch gating: pass/warn/fail
- Notes: [layout impression or repro]
```

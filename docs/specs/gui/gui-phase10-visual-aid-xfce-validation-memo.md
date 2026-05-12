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

## 確認対象

1. MainWindow 最下部に dedicated messaging row が追加され、footer summary と視覚的に分離されていること。
2. Settings dialog 最下部に短命 notice エリアがあり、dialog 内の state が下端で読めること。
3. Color dialog 最下部に短命 notice エリアがあり、dialog 内の state が下端で読めること。
4. watch summary が footer summary 側に残り、message row と役割分担できていること。
5. resolution 未確定時に Optimize が進めないこと。
6. Watch Start が SrcdirL / SrcdirR の両方と正の interval が揃うまで進めないこと。

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

期待:

- MainWindow が起動する。
- 起動直後に footer summary と dedicated messaging row が上下 2 段として見える。

1. MainWindow の message surface 確認

- footer summary 側で Status と Watch summary が読めることを確認する。
- その直上に message 専用 1 行があり、summary 行と混ざって見えないことを確認する。
- 区切り線または視覚的な切れ目があり、message row が footer summary の続きに見えすぎないことを確認する。

1. Optimize disabled 条件

- resolution が未確定になる条件を作れる場合、その状態で Optimize が押せないか、少なくとも先へ進まないことを確認する。
- Notes には、押せない形で予防できているか、押せるが message で止まるかを分けて残す。

1. Settings dialog notice

- Settings を開く。
- dialog 最下部に notice エリアがあり、上の action row と混ざらないことを確認する。
- Load / Save / Close 後に state 文言が最下部で読めることを確認する。

1. Color dialog notice

- Color を開く。
- dialog 最下部に notice エリアがあり、apply/cancel row の直後で読めることを確認する。
- 無効 color を試せるなら、invalid background color 系の state が dialog 内で閉じることを確認する。

1. Watch start disabled 条件

- 起動直後は Watch Start が押せないことを確認する。
- SrcdirL のみ設定した状態では、まだ Watch Start が押せないことを確認する。
- SrcdirL / SrcdirR の両方を設定し、interval が正なら Watch Start が押せることを確認する。
- watch 起動後は Watch Stop が押せることを確認する。

## スクリーンショット推奨

- MainWindow 全景 1 枚
- Settings dialog 1 枚
- Color dialog 1 枚
- Watch start disabled の状態が分かる 1 枚

## 判定テンプレート

- 対象PR: [number]
- 評価日: [YYYY-MM-DD]
- 評価者: owner

### 判定結果

- MainWindow dedicated message row: pass/warn/fail
- Settings dialog notice: pass/warn/fail
- Color dialog notice: pass/warn/fail
- Optimize disabled condition: pass/warn/fail
- Watch start disabled condition: pass/warn/fail
- Overall: pass/warn/fail

### Notes

- MainWindow:
- Settings:
- Color:
- Optimize gating:
- Watch gating:

## PR コメント短縮版

```md
### Phase10 visual aid XFCE check
- MainWindow dedicated message row: pass/warn/fail
- Settings dialog notice: pass/warn/fail
- Color dialog notice: pass/warn/fail
- Optimize gating: pass/warn/fail
- Watch gating: pass/warn/fail
- Notes: [layout impression or repro]
```

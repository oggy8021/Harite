# GUI Phase5 P5-4 スタイル統一メモ（Retrofit + Modernize）

最終更新: 2026-04-13
対象: P5-4 feat(gui)

## 目的

- 旧Gladeの情報密度と操作意図を維持しつつ、現行fallback UIで視認性を上げる。
- 「旧版らしさが説明可能」を文言ベースで固定し、PRレビュー時の判断をぶらさない。

## 旧版らしさの説明軸

1. 方向操作の即時判別

- `tgl*` は上下左右の意味を、読みやすい語彙で左右対称に表示する。
- 現行表現: `Top/Bottom/Left/Right`。

1. 操作階層の明示

- 主操作: `Save/Optimize/Apply`。
- 副操作: `Prefs/About/Help`。
- 未実装導線: `planned` を必ず明示。

1. フロー可視化

- 画面上に `Compose -> Optimize -> Apply` を固定表示し、迷いを減らす。

## 旧->現行 フェイス対応（P5-4時点）

| 旧意図 | 現行fallback表現 | 目的 |
| --- | --- | --- |
| Save系主操作 | `Save` | 主要導線を簡潔に表示 |
| Optimize系主操作 | `Optimize` | 主要導線を簡潔に表示 |
| Apply系主操作 | `Apply (dry-run)` | 安全既定の明示 |
| 設定/補助導線 | `Prefs` / `About (secondary)` / `Help (secondary)` | About/Help のみ補助導線として強調 |
| 未実装導線 | `(... planned)` | 非透過状態の回避 |
| 位置トグル | `Top/Bottom/Left/Right` + `-L/-R` | 左右対称・意味対称 |

## 受け入れ観点（P5-4）

- 同種要素の表記ゆれが無い。
- 主操作と副操作を一目で区別できる。
- 方向トグルを文字だけで誤読しない。
- `planned` 導線が実装済みに見えない。

## アイコンセット選定メモ（将来拡張）

アイコン導入は P5-4 完了後の拡張タスクで扱う。候補は以下。

- <https://lucide.dev/guide/version-1>
- <https://feathericons.com/>
- <https://remixicon.com/>
- <https://fontawesome.com/>

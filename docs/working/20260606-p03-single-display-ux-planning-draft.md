# P-03 — 単 display / monitor まわり UX（計画 draft）

最終更新: 2026-06-06  
ステータス: **planning draft**（採用条件の整理前）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [feature-overview §P-03](20260518-2047-feature-overview.md) | inventory 入口 |
| [issue #359](../online-issues/issue-359.md) | 起票メモ |
| **本書** | 単 display 時の -R 無効化等 — 計画正本 |

**背景:** 物理 1 ディスプレイで R 側操作（path / srcdir / direction 等）の扱いが未整理。旧 K-01 monitor 縁はここに集約（H-08 破棄）。

---

## 1. 問題

- dual-display 前提の UI が、**1 枚検出**環境でも R 側が有効のまま。
- 単 display の **再現手順が未確立**（HDMI 電源 off では枚数維持等）。
- disabled 範囲・spec・GTK/Qt テスト方針が未合意。

---

## 2. 目標（案）

**検出ディスプレイが 1 枚のとき、R 側に関わる操作を無効化または誤操作不能にする。**

| 対象（案） | 操作 |
| --- | --- |
| Slideshow | R saved source combo、R srcdir、direction の R 寄り |
| Optimize / Apply | two-screen / per-monitor の R 寄り（要 spec 切り分け） |

※ 詳細範囲は gate で確定。

---

## 3. 採用条件（issue #359 より）

1. 単 display **再現手順**の確立（開発・CI 用）
2. **disabled 範囲**の spec ストーリー合意
3. **GTK/Qt** 両 backend のテスト方針

---

## 4. 着手 gate checklist（未記入）

| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| P3-1 | 再現手順 | Windows: ケーブル抜き / 仮想 1 枚。CI: mock `detect_displays` | |
| P3-2 | disabled 範囲 | Slideshow R 一式のみ（Optimize は対象外） | |
| P3-3 | 検出タイミング | 起動時 + settings 保存時 + display 変更イベント（あれば） | |
| P3-4 | 1 枚でも dual 意図 | 将来「論理 L/R のみ」ニーズはスコープ外と明記 | |

---

## 5. 実装フェーズ案

| 段 | 内容 |
| --- | --- |
| 0 | 本書 + 再現手順メモ |
| 1 | gui-spec 追記 |
| 2 | Qt Slideshow tab disabled 配線 |
| 3 | テスト（mock display count） |

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-06 | 初版 — C-01-E-KW 完了後のストック着手として起票 |

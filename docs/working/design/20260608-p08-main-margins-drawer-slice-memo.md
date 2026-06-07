# P-08 Main + Margins Drawer — 評価メモ

最終更新: 2026-06-08（gate 全項目 pass — C-04 案 B 先行合意を反映）  
計画正本: [20260608-p08-main-margins-drawer-planning-draft.md](../20260608-p08-main-margins-drawer-planning-draft.md)  
視覚参照: [20260604-c04-slideshow-margins-surface-slice.html](20260604-c04-slideshow-margins-surface-slice.html) §5 **右パネル（案 B）**  
前提: [C-04 slice-memo](20260604-c04-slideshow-margins-surface-slice-memo.md) 案 B 表（操作削減なし）

## 目的

- C-04 で保留だった **案 B** を P-08 として具体化する。
- impl 前に **Main 正面 / Drawer 内 / 廃止する tab** を固定する。

## 使い方

1. C-04 HTML §5 右（案 B）で全体像を確認する（概念図。spin 実体は本メモ §配置）。
2. 下記 checklist に pass / revise / reject を記入（オーナー）。
3. 全 pass → planning 正本 gate 通過 → gui-spec §3 改訂へ。

## Main tab 配置（提案）

```text
┌─────────────────────────────────────────────┐
│  [top margin spin]                          │
│  [L spin]  compose grid (L|ctr|R)  [R spin] │
│  [bottom margin spin]                       │
│  preview | optimize | apply  (P-04 済み)    │
│  [ More margin options… ▼ ]                 │
│  ┌─ Drawer（開時・P-07 スタイル）──────────┐  │
│  │ embed pattern radios                   │  │
│  │ margin text notebook (Settings/Text)   │  │
│  │ position L/R Top/Bottom                │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

- 4 spin は **cross-grid の外周のみ**を Main 正面へ。center stack は Drawer 内。
- compose と action cluster の **相対順序**は現行 Main と同型（compose 上、action 下）。

## §P-08 — 合意 checklist

| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| P8-1 | notebook を Main + Slideshow の **2 tab** | Margins tab 廃止 | **pass** |
| P8-2 | 4 margin spin を Main 正面 **常設** | compose 外周 | **pass** |
| P8-3 | embed / margin text / position は **Drawer 内** | 操作は現 Margins tab と同じ | **pass** |
| P8-4 | トリガ `More margin options…` | Slideshow と対称（rename 可） | **pass** |
| P8-5 | Drawer 開閉視認性 | P-07 同型（palette chrome tint + 上辺線 + chevron） | **pass** |
| P8-6 | position と Main direction 十字 | **統合しない**（別 widget） | **pass** |
| P8-7 | margin tooltip 3 件 | 現 gui-spec §3 Margins 表のまま載せ替え | **pass** |

**gate 通過:** P8-1〜P8-7 すべて **pass**（2026-06-08。C-04 slice 案 B 先行合意を含む）。

## 合意後の出口

1. ~~checklist~~ → **完了**（planning 正本 §7 へ反映）。
2. gui-spec §3 — notebook 2 tab、Main + Margins Drawer 節を新設。
3. impl — Qt → GTK → tests（§8 フェーズ）。

# C-01-E-KW — Manage dialog keyword 行 slice 評価メモ

最終更新: 2026-06-05（オーナー K6 記入 → 合意確定）  
mock: [20260605-c01-e-kw-manage-keyword-slice.html](20260605-c01-e-kw-manage-keyword-slice.html)  
計画正本: [20260605-c01-e-kw-codh-keyword-planning-draft.md](../20260605-c01-e-kw-codh-keyword-planning-draft.md) §4 / §7

## 目的

- Manage sources and profiles… に **CODH keyword 入力行 1 本分**の配置・ラベルを固定する（C-04 S6 の中身）。
- **現フェーズは暫定配置**。local / preset の面板分割は [P-05](../20260518-2047-feature-overview.md) 理想像として別途。

## 使い方

1. HTML をブラウザで開く（file:// 可）。
2. **左=現行** / **右=暫定案**（keyword 行追加）を見比べる。
3. 下記 checklist — オーナー記入済み。

## 配置 — 現フェーズ（暫定）

| 項目 | 合意 |
| --- | --- |
| 位置 | **Refresh 近傍** — source リスト直下、Refresh/Delete 行の **直上**に 1 行 |
| 理由 | 空きが少ない。P-05 の preset 面板へ移すのは **後続** |
| P-05 との関係 | **今回触らない**（自動ソート + グループ見出しも P-05） |

## 配置 — 理想（P-05 ストック・参考）

Sources を **ALL なし**で二系統に分ける想定（impl は P-05 時）:

| 面板 | 持つ操作 |
| --- | --- |
| **local** | Delete、name、path、Browse、Add local |
| **preset** | Refresh、**keyword(CODH)**（暫定配置の行がここへ移る） |

## K6 checklist


| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| K6a | 暫定位置 | Refresh 直上 1 行 | **pass** |
| K6b | ラベル | `keyword(CODH)` | **pass** |
| K6c | 初期値 | テキスト `桜` | **pass** |
| K6d | 表示 | 常設（非表示にしない） | **pass** |

**補足（impl 時）:** 常設表示のまま、選択 source が keyword 非対応（local / 非 CODH keyword preset）のときは **入力 disabled** または notes 未更新とする（振る舞いは spec で 1 行固定）。

## 次の段階

1. ~~slice 合意~~ → **完了**。
2. gui-spec §4.2 + source-spec §15.7 改訂 PR。
3. core tests → impl（Qt Manage dialog）。

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-05 | 初版 — オーナー K6 pass。暫定配置 + P-05 理想像を分離記載 |

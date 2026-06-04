# glade2 母体解釈メモ — `out/wallpositapplet.glade`

最終更新: 2026-06-04  
入力: `wallpositapplet.glade`（Glade2 / Gtk+ 2.6、2026-06-04 に `out/` へ一時配置・**読解後オーナー削除**）。以下は読解時点の記録。  
計画正本: [20260604-c04-gui-surface-planning-draft.md](../20260604-c04-gui-surface-planning-draft.md) §7.1

---

## 1. ファイル概要

| 項目 | 内容 |
| --- | --- |
| タイトル | `Wallpaper Optimizer`（`WallPosit_MainWindow`） |
| 行数 | 約 1393 行 XML |
| トップレベル | **単一 `GtkWindow` のみ** — **`GtkNotebook` なし** |
| 副ダイアログ | Color、Settings、ImgOpen、Srcdir、Save、**Error（TextView）** |
| 技術 | GTK2 stock icon（`gtk-open`, `gtk-apply`, `gtk-execute` 等） |

**結論（一行）:** 母体は **1 画面に margin 十字・L/R 画像操作・保存/適用・slideshow（daemonize）・設定系ボタンを縦積み**した高密度 UI。現 Harite の Main / Margins / Slideshow **3 tab + registry は機能拡張の結果**であり、glade をそのまま戻す対象ではない。

---

## 2. メインウィンドウ構造（`vbox1`）

上から下へ:

```
[hbox11]  上マージン (lblTopMergin + spnTopMergin)
[hbox2]   ┌ 左マージン列 ┬ 中央 compose ┬ 右マージン列 ┐
          │ spnL         │ L/R 十字toggle│ spnR         │
          │               │ Open/Clear   │              │
          │               │ path entry   │              │
          │               │ 入替不可/可   │              │
[hbox12]  下マージン (lblBtmMergin + spnBtmMergin)
[hbox14]  横一列アクションバー（後述）
[statusbar] GtkStatusbar（単一ステータスバー）
```

### 2.1 中央 compose（現 Harite Main tab に相当）

| glade id | 役割 | 現 Harite |
| --- | --- | --- |
| `tglUpperL/R`, `tglLowerL/R` | 上下配置（stock top/bottom） | direction toggle 群 |
| `tglPushLeftL/R`, `tglPushRightL/R` | 左右配置 | 同上 |
| `btnGetImgL/R` | gtk-open | Open-L/R |
| `entPathL/R`, `btnClrPathL/R` | path + clear | 同型 |
| `radFixed` / `radNoFixed` | 入替不可 / 入替可 | 2 画面入替ポリシー相当（現 UI とは配置・文言が異なる） |

**ないもの（母体）:** Preview 左右、Optimize ボタン、Apply mode row（No Split / Span）、header の Color/Settings/About 分離、flow legend。

### 2.2 マージン（現 Harite Margins tab に相当）

| glade | 配置 |
| --- | --- |
| `spnTopMergin`, `spnBtmMergin`, `spnLMergin`, `spnRMergin` | **compose を物理的に囲む十字**（spin のみ、align 文字列ラベルなし） |

**ないもの:** `embed pattern`、`margin text` notebook、`Position` L/R Top/Bottom、3 行 Rule/Line limits 注釈、`Main Window Current alignment` 系 summary。

→ 現 Margins タブの **情報過多は reformation 以降の積み上げ**。母体は **数値 spin だけで視覚的に十分**だった。

---

## 3. 底辺アクションバー `hbox14`（重要）

**1 行に並べているもの（position 順）:**

| pos | id | stock / 意味 |
| --- | --- | --- |
| 0 | label50 | スペーサ/装飾 |
| 1 | `btnSetting` | 設定 |
| 2 | `btnSetColor` | 色 |
| 3 | `btnSave` | 保存 |
| 4 | `btnSetWall` | **gtk-apply（壁紙適用）** |
| 5–6 | `spnInterval` + `lblInterval`（秒） | slideshow 間隔 |
| 7 | `btnDaemonize` | **gtk-execute（開始）** |
| 8 | `btnCancelDaemonize` | gtk-stop |
| 9 | `btnAbout` | About |
| 10 | `btnHelp` | Help |

**解釈:**

- **Optimize / Apply / Slideshow が同じ帯に同居** — 現 Harite で Preview+Optimize+Apply を Main、Slideshow を別 tab に分けたのは **正しい緩和**。
- 母体の slideshow は **Settings ではなくメイン底辺** — 現行の Slideshow tab + Manage dialog は **機能増加後の再配置**（registry / profile / remote source は glade に存在しない）。
- **About/Help が apply の隣** — 現行の header command bar へ移したのは改善。底辺に戻す必要はない。

---

## 4. エラー・フィードバック

| 母体 | 現 Harite |
| --- | --- |
| `GtkStatusbar` | footer `Status` + `Slideshow summary` + `Error` 行 |
| `ErrorDialog` + `tviewError`（別モーダル） | インライン `lblError`（色分離は C-04 Wave 0） |

**示唆:** エラーを **別ダイアログに戻す**必要はない。footer Error の **視覚強調**で母体より日常利用向き。`{Phase}: {state}` 機械語は母体の statusbar より **さらに開発者向け**なので削る（計画 draft §3.2）。

---

## 5. Settings ダイアログ（`SettingDialog`）

含まれるもの（抜粋）:

- ディスプレイ解像度 entry 群（`entDisplayWL/HL/WR/HR`）
- **srcdir L/R**（`entSrcdirL/R`, `btnOpenSrcdirL/R`）
- Save / Clear / OK / Cancel

**解釈:** slideshow 用 srcdir は **設定画面の一部**だった。現 Harite は **Slideshow tab 正面 + registry dialog** へ移動 — 正しいが、**Manage・preset・remote** で Settings 時代より重くなった → C-04 Drawer の根拠。

---

## 6. 現 Harite との対応表

| 母体（1 window） | 現 Harite | 関係 |
| --- | --- | --- |
| margin 十字 spin | Margins tab cross-grid + 冗長 label | **分離は維持、label 削減**（§5 draft） |
| compose 十字 + path | Main tab | 維持 |
| btnSave + btnSetWall | Export + Apply（+ Optimize） | 機能分割済み |
| interval + daemonize | Slideshow tab | **tab 分離は維持**、tab 内を Drawer で軽く |
| btnSetting/Color/About | header + dialogs | 維持 |
| srcdir in Settings | Slideshow + Manage | 進化；密度問題は Manage 側 |
| ErrorDialog | footer Error | 維持＋色 |

---

## 7. A12 / A13 への推奨（エージェント解釈）

### A13 — glade2 の扱い

| 判断 | 推奨 |
| --- | --- |
| glade2 を実装正本に戻す | **非採択**（不変） |
| glade2 を design 参照 | **採択** — 本メモで十分。repo に glade を常設する必要は低い（`out/` 参照で可） |
| 底辺 1 行バーへの回帰 | **非採択** — 機能数が母体の数倍 |

### A12 — Margins の載せ方（2026-06-04 オーナー追記）

| 案 | 推奨 |
| --- | --- |
| Main + Margins **全面 tab 統合** | **非採択** — 機能増で母体の底辺 1 行より混雑 |
| **Margins 専用 tab を永久とする** | **非永久** — 変更余地あり |
| **Main から Drawer 等で margin 意味論**（十字が compose を囲む） | **採択余地** — 伝わりやすければ C-04a で slice 比較 |

**C-04 共通（載せ方に依存しない）:** spin 十字中心、文字列 summary・3 行 notes 削減。Slideshow は tab 維持＋Drawer で補助を逃がす。

---

## 8. オーナー確認（2026-06-04）

- [x] 底辺 hbox14・margin 十字・認識 — **相違なし**
- [x] 全面 tab 統合は出しにくい — **維持**
- [x] Margins は **Main Drawer 等もあり** — 専用 tab は永久ではない（[計画正本 §7.2](../20260604-c04-gui-surface-planning-draft.md)）
- [x] 生 glade — **再参照しない**。原本はオーナー手元、`out/` から削除

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-04 | 初版 — wallpositapplet.glade 読解、A12/A13 推奨 |
| 2026-06-04 | オーナー確認 — A12 Drawer 余地、glade ファイル削除方針 |

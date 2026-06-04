# C-04 GUI Surface Planning Draft（計画正本）

最終更新: 2026-06-04  
ステータス: **planning draft**（採択・非採択の熟読用。gui-spec §3 は 2026-06-04 合意反映済み。impl は Wave 0 → b → a）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [20260518-2047-feature-overview.md](20260518-2047-feature-overview.md) | WS10 **inventory 入口**（ID の置き場・優先順のみ） |
| **本書** | **C-04 + 近接 polish の計画正本**（オーナー気づきのダンプ、採択表、widget 切り分け、波分け） |
| [harite-gui-spec.md](../specs/gui/harite-gui-spec.md) | 実装正本（本書合意後に差分 PR で更新） |

**C-03（plugin capability 可視化）** は本書の主題から外す。必要なら C-04 内の「短い環境 help」に吸収する（§6 参照）。

**関連 inventory:** [C-01-E-KW](20260518-2047-feature-overview.md)（CODH キーワード UI）は **Slideshow / Manage 面の余白** が本書の成果指標の一つ。

---

## 1. オーナー観測ダンプ（原文趣旨）

以下は 2026-06-04 時点の気づきを、熟読用にそのまま構造化したもの。

### 1.1 密度・導線

- **Slideshow タブ**とその配下ダイアログ（Manage sources and profiles…）が混み合い、キーワード検索などを載せる余裕がない（[C-01-E-KW](20260518-2047-feature-overview.md) の先送りと直結）。
- Slideshow では **中核操作**（source 選定 → Start）と **補助操作**（registry 管理、preset 体験、mode help、output 表示）の流れが悪い。§4 の切り分けで整理したい。
- 補助・付帯操作は **Drawer**（側面／下段の開閉パネル等）に追い出す案がある。
- **Margin タブ**は Copilot 時代に分離したが、**永久の 3 tab 構成ではない**。意味論（margin 十字）が伝わりやすければ **Main から Drawer 等で開く**案もある（§7.2）。

### 1.2 フィードバック・エラー

- **エラーメッセージ**は footer 下段に出る配置はよいが、通常 Status と同系色で区別がつきにくい。**赤色など視覚分離**を検討。
- **注意喚起**は Preset Refresh の `"Refresh applies to remote sources only."` のように **OK ダイアログ**でよいパターンがある（稀な誤操作向け）。
- footer の **`{Phase}: {state}`**（例: `Slideshow: planned`, `Margins: updated`, `Input: cleared`）は、開発時の trace としては有用だが、**日常ユーザー視点の有用性は低い**（オーナーも操作に慣れて気づきにくいが、第三者には「not ready」系に見える）。→ §3.2 で確定扱い。

### 1.3 表示しない・減らす

- デバッグ目的の **plugin 名・実行基盤の常設表示**（footer や欄外）は **不要**。Windows 上なら「Windows で動いている」ことは自明で、**今の単一 plugin 前提**では「今どの plugin か」を日常 UI に出す価値は薄い（§2 A4 補足）。
- 開発経緯で入った **icon 非表示時の label 冗長補完**、「見ればわかる」系統は **削除方向**。代替は **tooltip / hoobar**（既存で効果があった手法）の拡張。
- **視覚サインだけ**（色・点滅のみ）での通知は単独では不採用（§5）。

### 1.4 Margins タブの失敗感

- `Main Window Current alignment:` と `align=center,center/center,center` の **二重・冗長**列挙は失敗。操作できない十字と **どれが active か**の小さな示しで足りる。
- `margin=0,0,0,0` 列挙も冗長。
- Bottom margin 上の **3 行注釈**（`Line limits…`, `Rule:…`, `Current behavior:…`）がデザインを崩している → tooltip / 1 行要約 / Drawer へ。
- `embed pattern:` / `Position:` は **暫定配置**。center stack 全体のバランス見直しが必要。

### 1.5 維持・強化

- **ボタン enable/disable** は効果的で好印象 → 拡張（[P-03](20260518-2047-feature-overview.md) / #359 と同系）。
- **hoobar / Tooltip** はうまい手 → 情報逃がし先として拡張。

### 1.6 ゴール（product）

- 上記整理で **Harite 独自 preset データの強化**や **CODH 検索へのユーザー関与**（C-01-E-KW）に使える **UI 余白と導線**を確保する。

---

## 2. 採択・非採択・保留（計画判断）

| # | テーマ | 判断 | ID / 波 | 備考 |
| --- | --- | --- | --- | --- |
| A1 | Error 行の視覚分離（赤系等） | **採択** | P-04 / Wave 0 | gui-spec footer § + Qt `#errorLabel` / GTK 同期 |
| A2 | Refresh 型 OK ダイアログ（注意） | **採択** | C-04 パターン | 破壊的操作・誤解しやすい操作に限定 |
| A3 | `{Phase}: {state}` footer 常設 | **採択（縮小・人間語化）** | C-04c | §3.2。開発 trace は log / 詳細パネルへ |
| A4 | plugin / OS の常設表示（「今何者が動いているか」） | **非採択（現行 product）** | — | §2.1。Settings の Plugin 行は expert 用として残してよい |
| A5 | icon 冗長 label の段階削除 | **採択** | C-04c | tooltip/hoobar とセットで |
| A6 | 全面 icon-only 化 | **非採択** | — | Phase10: 初手は icon+label |
| A7 | enable/disable 拡張 | **採択** | P-03 + C-04 | 単 display -R、Start 条件など |
| A8 | hoobar / Tooltip 拡張 | **採択** | C-04 | Margins 3 行注釈の移設先 |
| A9 | Slideshow 中核/補助分離 + Drawer | **採択** | C-04b | §4 |
| A10 | Margins 冗長 state 削除 | **採択** | C-04a | §5 |
| A11 | embed pattern / Position 再配置 | **採択** | C-04a | design slice 後 |
| A12 | Margins の載せ方（専用 tab vs Main+Drawer） | **再検討可** | C-04a | §7.2。glade 解釈後: **全面 tab 統合は非推奨**のまま。Drawer で margin 意味論を Main に寄せる案は採択余地あり |
| A13 | 母体 glade2 の扱い | **完了（参照のみ）** | — | [解釈メモ](design/20260604-glade2-legacy-interpretation-memo.md) で足りる。`out/*.glade` はオーナー削除可 |
| A14 | C-03 独立パネル（capability 一覧） | **保留→縮小** | — | §6。本波では出さない |
| A15 | C-01-E-KW UI | **依存** | C-04b 後 | Manage 面の余白が前提 |
| A16 | 色だけの状態通知 | **非採択（単独）** | — | 色+文言+disable |

### 2.1 A4 補足 — plugin 表示（オーナー 2026-06-04）

**意図:** footer 等に「linux plugin 動作中」のような **常設の plugin 名表示**は不要。Windows 実機なら **OS 文脈は自明**（Span / 単一ファイル apply 等は別の help で足りる）。

| 条件 | 判断 |
| --- | --- |
| 現行（plugin 実質 1 択、Settings に Plugin 文字列） | **日常 UI に plugin  identity を出さない** — A4 非採択 |
| plugin が細分化・複数化し、ユーザーが **選ぶ・切り替える** | そのとき初めて「どれが active か」の表示を再検討 |
| [K-04](20260518-2047-feature-overview.md) plugin 拡張パック + コミュニティ MR 受け入れ | **再検討のゲート**。それまでは capability パネルも「何者か」常設も不要 |
| C-03 型の capability 可視化パネル | 上記ゲートなしでは **出さない**（§6） |

**残してよいもの:** Settings の `Plugin` 行（設定ファイル・上級者向け）。Apply mode help の Span/Auto-Split 説明（plugin 名ではなく **挙動**の説明）。

---

## 3. フィードバック設計（確定メモ）

### 3.1 現状（実装）

- `set_feedback(phase, state, error)` → `lblStatus` = `"{phase}: {state}"`, `lblError` = error 文字列。
- Qt 初期表示: `Status: ready`, `Error: none`。stylesheet 上 status/error が同系 `#555` になりやすい（`qt_stylesheet.py` の `#statusLabel` / `#errorLabel` と builder の objectName 不一致の可能性あり）。

### 3.2 `{Phase}: {state}` について（オーナー確認済み）

**対象は footer の Status 行の機械語**（`Slideshow: planned`, `Input: dialog-unavailable`, `Margins: updated` 等）。タブ内に literal `"not ready"` ラベルがあるわけではないが、ユーザーには **未準備・開発中** に読める。

| 観点 | 判断 |
| --- | --- |
| 開発者（慣れ） | 操作 trace としては読める |
| 日常ユーザー | **有用性低**。視点が向かない |
| 計画 | **常設 Status から phase 名を外す**方向。成功は短い人間語または空、失敗は Error 行、進行中は Slideshow summary 右側など **文脈に近い 1 箇所** |

**案（draft）:**

| 旧 state | ユーザー向け（案） | 表示面 |
| --- | --- | --- |
| `planned` | （出さない）または tooltip | — |
| `updated` / `cleared` | 短い toast 相当 1 秒 or 何も出さない | — |
| `error` | Error 行 + 色 | footer Error |
| `dialog-unavailable` | `Could not open file dialog` | Error |
| slideshow 実行中 | `Slideshow: running` 等 | footer 右 `slideshow_summary` のみ |

**テスト:** `test_main_window_signals` / gtk runtime の `lblStatus` 文字列期待値は Wave ごとに更新。

---

## 4. Slideshow 面 — 中核 / 補助 / Drawer

### 4.1 現行 widget  inventory（Qt ビルダー基準）

| 区分 | widget / 行 | 現配置 |
| --- | --- | --- |
| **中核** | `combo_slideshow_profile` + Profile | profile row |
| **中核** | `combo_slideshow_source_l/r`, Srcdir-L/R, path label, Clear-L/R, Swap | srcdir row |
| **中核** | Interval, Start, Stop | controls row |
| **補助** | `btn_manage_source_registry` | manage row → **dialog**（Refresh, CRUD, preset） |
| **補助** | Mode sequential/random + mode help | controls 上段 |
| **補助** | current / output labels | detail row |
| **補助** | `Applies L/R together` help | profile row |

### 4.2 目標配置（**確定** 2026-06-04）

mock: [surface-slice.html](design/20260604-c04-slideshow-margins-surface-slice.html) §4 — 合意: [slice-memo](design/20260604-c04-slideshow-margins-surface-slice-memo.md)（S1–S6 pass）。

**Slideshow tab — 正面（中核）**

- `combo_slideshow_profile`（`Applies L/R together` は **削除** → tooltip 可）
- L/R: saved source combo + Srcdir + path + Clear + Swap（Main 同型）
- Interval + **Slideshow Start / Stop**（視線の終点）

**Drawer — 「More slideshow options…」（ラベル rename 可）**

- Mode sequential/random + 短い help（1 行まで）
- **Manage sources and profiles…** のみ（正面からは除去）
- current / output（detail row 削除；path は tooltip / 要約）
- 将来: C-01-E-KW は **Manage dialog 内**（Drawer 経由）

**Dialog（既存）**

- registry / remote **Refresh**（OK 注意維持）

### 4.3 C-01-E-KW との関係

[C-01-E-KW](20260518-2047-feature-overview.md) 先送り理由は「Manage 周りが込み入り」。**C-04b で Manage を Drawer 化または tab 正面の行数削減**できれば、KW 入力は dialog 内 1 フィールド追加で再評価可能。

---

## 5. Margins 面 — 削減・再配置

**確定（Wave a）:** **案 A** — 専用 **Margins tab 維持**・スリム化（M1–M6 pass）。mock §5 左/右。

**将来オプション:** **案 B** — Main + Margins Drawer（§7.2）。操作削減なし・載せ替えのみ。B は A 後に spec オプション比較。

### 5.1 削る（確定）

| 現物 | 問題 | draft 対応 |
| --- | --- | --- |
| `Main Window Current alignment:` + summary `align=...` | 冗長 | 十字 active + L/R 短ラベルのみ（Main `lblCurrentState*` と役割分担） |
| `margin=0,0,0,0` 風列挙 | 冗長 | cross-grid 編集で足りる → tooltip |
| 3 行 notes（Line limits / Rule / Current behavior） | レイアウト破壊 | 1 行 + 残り tooltip / Drawer |
| `embed pattern:` row | 暫定感 | center stack 順序: cross-grid → pattern → position → （notes は最下または外） |
| `Position:` row | 暫定配置 | **維持** — tab 内 sub-panel（embed とグループ化） |

### 5.2 維持（確定 — 削除しない）

- 4 辺 margin spin + cross-grid。
- embed pattern（4 radio）、margin text notebook（Settings/Text）、Position L/R Top/Bottom、max-lines spin。
- 案 B 採用時のみ載せ場所を Main 外周 + Drawer へ **移設**（§7.2）。

---

## 6. C-03 の扱い（縮小）

| 旧 C-03 イメージ | 本計画 |
| --- | --- |
| plugin ごとの capability パネル | **出さない** — A4 / §2.1。OS 自明・単一 plugin 前提では「何者か」は不要 |
| Span vs Auto-Split の説明不足 | Main `apply mode help` / slideshow mode help の **文言整理**（C-04a/c）— **挙動**の説明であり plugin 名表示ではない |
| 「Linux だけ per-monitor」 | K-04 級の複数 plugin 時代まで **常設説明は不要**。必要なら Settings/About に 1 段落（オプション） |

独立 feature としての C-03 は **着手しない**。overview 上は構想保持のままでも、実務は **本書 C-04 に吸収**でよい。**K-04 + コミュニティ受け入れ**が具体化するまで C-03 を inventory から外してもよい（overview はオーナー判断待ち）。

---

## 7. 母体 glade2 参照

| 項目 | 方針 |
| --- | --- |
| 配置 | 解釈済み — [20260604-glade2-legacy-interpretation-memo.md](design/20260604-glade2-legacy-interpretation-memo.md)。生 XML（`out/wallpositapplet.glade`）はオーナー原本保持のため **repo から削除可** |
| 用途 | Main+Margins 同一 surface だった頃の **操作密度・近接関係**の参照 |
| 非用途 | レイアウトのコピー元、glade2 を Harite 正本に戻すこと |
| design 成果物 | 解釈後: `docs/working/design/` に **解釈メモ 1 枚**（screenshot 可）。glade 本体の repo 取り込みは必須ではない |

### 7.1 A12 / A13 — glade2 レビュー（2026-06-04 実施）

**解釈メモ:** [design/20260604-glade2-legacy-interpretation-memo.md](design/20260604-glade2-legacy-interpretation-memo.md)（2026-06-04 読了・オーナー **認識相違なし**）

**ステータス:** **クローズ**（生 glade は再参照しない。原本はオーナー手元）

**解釈サマリ:**

- 母体は 1 窗口・margin 十字・slideshow 底辺 1 行。現 product へ glade コピーは非現実的。
- **全面 tab 統合（旧 A12 厳格版）は非推奨** — 機能増で hbox14 より悪化。
- **Margins 専用 tab は永久ではない** — §7.2。

### 7.2 A12 改訂 — Margins を Main Drawer に寄せる（オーナー 2026-06-04）

| 案 | 判断 |
| --- | --- |
| Main + Margins を 1 tab に戻す（全面統合） | **非採択** — glade 解釈どおり密度・parity 的に不利 |
| **Margins 専用 tab 維持（案 A）** | **確定 — Wave a**（slice M5/M6 pass） |
| **Main から Margins Drawer（案 B）** | **保留** — A 後に spec オプション。操作は削減しない |

**C-04a でやること:** Margins tab の冗長 label 削除は **どちらの載せ方でも共通**。Drawer 案を採る場合は gui-spec の tab 一覧と §3 Margins の **移設 or 縮小**を同じ PR ブロックで書く。

---

## 8. 実装波（**確定順** 2026-06-04）

| 順 | 波 | スコープ | 根拠 |
| --- | --- | --- | --- |
| 1 | **0** | Error 赤系 + `Phase: state` 廃止（F1/F2） | slice-memo |
| 2 | **b** | Slideshow §4.2 — More… Drawer、Manage/Mode/output 移動 | S1–S6 pass |
| 3 | **a** | Margins 案 A — 専用 tab スリム化 | M1–M6 pass |
| 4 | **c** | icon/tooltip 整理（A5/A8） | 任意で b/a と同 PR でも可 |
| — | **並行** | P-03 単 display -R | #359 |

**採用条件:** ~~§4–§5 mock 合意~~ **達成**（[slice-memo](design/20260604-c04-slideshow-margins-surface-slice-memo.md)）。次は gui-spec 差分 PR。

---

## 9. C-04 rough ideas（overview から移管）

overview §2 にあった参考案は **本書で運用**する。

- **task 3 系統:** 作る（Main） / 適用する（Main Apply） / 回す（Slideshow）— **タブは維持**し、tab 内を task 順に並べ替え。
- **scenario:** 単画面 1 枚 / 2 画面合成 / すぐ Apply / slideshow 開始 — onboarding 文案・初回 highlight の材料（全面 wizard はしない）。
- **progressive disclosure:** 中核だけ正面、補助は Drawer / dialog / tooltip。
- **Wallpaperoptimizer 強み:** optimize→apply→slideshow の直列は壊さない。

---

## 10. 次のステップ

1. ~~§4–§5 mock 合意~~ **完了**（2026-06-04）。
2. **gui-spec** §3 Slideshow / Margins / footer — design→spec PR（§4.2・§5 確定版を反映）。
3. impl: Wave **0 → b → a**（必要なら c）。

**overview への反映:** C-04 行は「計画正本 → 本書」リンクのみ。詳細の二重管理はしない。

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-04 | 初版。オーナー観測ダンプ + 採択表 + phase:state 確定 + widget 切り分け |
| 2026-06-04 | A4 補足 — OS 自明・単一 plugin。K-04 / 複数化まで常設 identity 非採択 |
| 2026-06-04 | A12/A13 保留 — glade2 共有・解釈メモ後に判断。戻す強度は出しにくい（オーナー） |
| 2026-06-04 | glade 読解完了・オーナー確認。A13 クローズ。A12 → §7.2（Margins Drawer 余地、専用 tab 非永久） |
| 2026-06-04 | slice-memo 合意 — §4.2/§5/§8 確定。Wave 0→b→a。案 A 先行、案 B 保留 |

# P-04 — Main action cluster 整理（計画 draft）

最終更新: 2026-06-08  
ステータス: **完了**（#429 — gui-spec §3/§4 改訂、GTK/Qt layout・sync・テスト）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [feature-overview §P-04](20260518-2047-feature-overview.md) | inventory 入口 |
| **本書** | Main tab **action cluster**（Preview / Optimize / Apply）の密度整理 |
| [C-04 計画正本](20260604-c04-gui-surface-planning-draft.md) | Slideshow/Margins/footer は完了。**Main cluster はスコープ外のまま残存** |
| [harite-gui-spec.md](../../specs/gui/harite-gui-spec.md) | 実装正本（本書合意後に §3 Main tab を改訂） |

**きっかけ:** C-04 後も Main の Preview 群が idle 時から文字だらけ。enable/disable とサムネで誘導は足りる。

---

## 1. 現状（うるさい面）

Qt `qt_tab_main.py` 基準。compose 十字は C-04c で icon-only 済み。

| 群 | 常設 label / 文言 | 件数感 |
| --- | --- | --- |
| **Preview** | セクション見出し `Preview` | 1 |
| | L/R: assignment、サムネ上 `Preview *: not-ready`、Result | 6 |
| | 下段: `Preview:` / `Preview source:` / `Assist:` | 3 |
| **Optimize** | セクション見出し、`Optimize result: not-run` | 2 |
| **Apply** | セクション見出し、`Apply target: not-ready`、mode radio 2、**help 行** | 4+ |

`not-ready` / `not-run` 系は **未操作の自明状態**を繰り返し説明している。

---

## 2. オーナー方針（2026-06-07 確定）

| # | 論点 | 判断 |
| --- | --- | --- |
| **P4-2** | Optimize result / Apply target の常設 label | **確定** — 廃止。`footer Status` または widget **tooltip** へ（Margins line limit と同型） |
| **P4-1** | Preview idle 時の補助 label | **減らす** — 本人は困らないが、enable/disable で誘導できているので常設文は削減方向。具体度は §3 で段階化 |
| **P4-3** | `apply mode help row` | **廃止** — プレビューが視覚的に補う。radio 群へ **tooltip** |
| **P4-4** | セクション見出し（`Preview` / `Optimize` / `Apply`） | **廃止** — ボタン label で足りる |
| **P4-5** | `not-ready` / `not-run` 常設 | **極力廃止** — 未操作は空表示または視覚のみ（枠・disable）。成功・失敗・進行中だけ人間語を出す |

---

## 3. Preview idle — どこまで減らすか（提案）

オーナーは「減らしてみる」。実装前に **案 A を既定**とし、実機で足りなければ tooltip へ1段戻す。

| 区分 | 案 A（既定・推奨） | 案 B（最小） | 案 C（攻め） |
| --- | --- | --- | --- |
| サムネ | 常設。idle は **枠のみ**（中央テキストなし） | 同左 | 同左 |
| L/R assignment | **非表示**（optimize 後のみ短く出してもよい） | idle 非表示 | 常に非表示 → tooltip |
| L/R Result | **非表示** | 非表示 | 非表示 |
| 下段 `Preview:` / `source` / `Assist` | **すべて非表示** | 下段3行のみ削除 | 同左 |
| 情報の逃がし先 | optimize 後: サムネ + 必要なら footer `Status` | tooltip on サムネ群 | footer のみ |

**案 A を採る理由:** 操作補助は compose disable + Optimize/Apply enable 列で足りる。プレビュー画像そのものが主フィードバック。

---

## 4. 目標配置（tab 正面）

### Preview 群

- セクション見出し **なし**
- L/R サムネ 2 枚のみ（横並び）
- idle: 空枠。optimize 後: 画像表示。overlay 文言は出さない
- assignment / result / state / source / assist の **常設 label 行は持たない**

### Optimize 群

- セクション見出し **なし**
- `Optimize` button（現行 icon+label 維持 — C-04 A6）
- `Optimize result:` label **なし** — 成功・失敗は footer `Status` / `Error`

### Apply 群

- セクション見出し **なし**
- `Apply` button
- `Apply target:` label **なし**
- `No Split` / `Span|Auto-Split` radio は **維持**
- `apply mode help row` **なし** — radio 群または Apply button へ `apply_mode_help_text(...)` を tooltip

### 補助説明の載せ先（§2 P4-2 確定）

| 旧常設 | 新載せ先 |
| --- | --- |
| `Optimize result: ...` | footer `Status`（成功短句）/ `Error`（失敗） |
| `Apply target: ...` | footer `Status`（apply 直後）または Apply button tooltip |
| `apply mode help` | Apply mode radio 群 tooltip（mode 切替で文言更新） |
| Preview assignment / assist 等 | 原則出さない。必要ならサムネ tooltip または footer |

---

## 5. `not-ready` 方針（P4-5）

| 状況 | 表示 |
| --- | --- |
| 未 optimize | サムネ空枠、label 行は **空**（`not-ready` 文字列を出さない） |
| optimize 成功 | サムネに画像。footer に短い成功句（既存 `status_message` 流用可） |
| optimize 失敗 | footer `Error` |
| apply 前 | Apply disabled — 文言不要 |
| apply 後 | footer `Status` のみ（`last applied` 等） |

テスト・sync コードの期待文字列 `Preview L: not-ready` 等は **本波で更新**する。

---

## 6. spec 改訂タッチポイント

| 正本 | 変更 |
| --- | --- |
| [gui-spec §3 Main tab](../../specs/gui/harite-gui-spec.md) | action cluster からセクション見出し・result/target/help 常設を削除 |
| gui-spec §3 補助説明面一覧 | Main tab tooltip / footer へ追記（Margins 表と同型でよい） |
| [gui-spec §9 footer](../../specs/gui/harite-gui-spec.md) | optimize / apply 結果の読み面として明記（既存を補強） |

---

## 7. スコープ / スコープ外

| 含む | 含まない |
| --- | --- |
| Main action cluster の label 削減 | Slideshow / Margins の再整理 |
| Qt + GTK parity | Preview 群の折りたたみ Drawer 化 |
| `apply_surface` の not-ready 既定値整理 | action button の icon-only 化（C-04 A6 非採択のまま） |
| footer / tooltip への情報移設 | compose grid（path 表示）の変更 |

---

## 8. 着手 gate checklist

| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| P4-1 | Preview idle（§3 案 A） | サムネのみ常設。assignment/result/下段3行は非表示 | **pass** — 減らしてみる |
| P4-2 | Optimize/Apply result・target | footer / tooltip へ | **pass** |
| P4-3 | apply mode help row | tooltip へ | **pass** |
| P4-4 | セクション見出し 3 つ | 削除 | **pass** |
| P4-5 | `not-ready` 常設 | 極力廃止（§5） | **pass** |

**gate 通過:** P4-1〜P4-5 すべて **pass**（2026-06-07）。

---

## 9. 実装フェーズ案

| 段 | 内容 |
| --- | --- |
| 0 | 本書 + gui-spec §3 改訂 PR |
| 1 | `qt_tab_main` / `gtk_tab_builders` — widget 削減・layout |
| 2 | `gtk_runtime_preview` / Qt preview sync — 空表示・footer 寄せ |
| 3 | `apply_surface` / action handlers — `not-ready` 除去 |
| 4 | テスト期待値更新（preview label 文字列） |

widget slice は **任意**（差分が layout 中心のため、実機スクショ注釈でも可）。

---

## 10. 関連 ID

| ID | 関係 |
| --- | --- |
| C-04 | Main cluster を残した後続 |
| C-03 縮小 | apply mode 説明は tooltip 化で充足 |
| P-03 | 単 display 時 Preview-R 非表示 — 本波と両立 |

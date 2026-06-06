# P-03 — 単 display / monitor まわり UX（計画 draft）

最終更新: 2026-06-06  
ステータス: **planning draft**（P3-1 観測・再現手順の肉付け中）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [feature-overview §P-03](20260518-2047-feature-overview.md) | inventory 入口 |
| [issue #359](../online-issues/issue-359.md) | 起票メモ |
| [gui-spec § Main / Slideshow](../specs/gui/harite-gui-spec.md) | dual-display 前提 UI |
| [slideshow-spec §6](../specs/slideshow/harite-slideshow-spec.md) | Linux per-monitor / pause |
| `src/harite/workspace.py` | **`detect_displays()`** 実装（本 issue の検出正本） |
| **本書** | 単 display 時の -R 無効化等 — 計画正本 |

**背景:** 物理 1 ディスプレイで R 側操作（path / srcdir / direction 等）の扱いが未整理。旧 K-01 monitor 縁はここに集約（H-08 破棄）。

---

## 1. 問題

- dual-display 前提の UI が、**1 枚検出**環境でも R 側が有効のまま。
- 単 display の **再現手順が未確立**（モニター電源 off だけでは枚数が減らない等 — [#359](../online-issues/issue-359.md)）。
- disabled 範囲・spec・GTK/Qt テスト方針が未合意。
- **Linux（XFCE / xrandr）と Windows（EnumDisplayMonitors）で「1 枚」の作り方と product 影響が異なる**が、planning に未整理だった。

### 1.1 現行 product との関係（観測前に押さえる）

| 層 | 現行契約 | 単 display での痛み |
| --- | --- | --- |
| **検出** | `harite.workspace.detect_displays()` — Linux=`xrandr --query`、Windows=`EnumDisplayMonitors` | OS が 2 枚と数える限り Harite も 2 枚 |
| **Main tab** | L/R 各 panel（path / direction / picker） | R も操作可能のまま |
| **Slideshow** | **L/R 両方 srcdir 必須**で Start 可（[gui-spec](../specs/gui/harite-gui-spec.md)） | 1 枚でも dual-source 前提は維持 |
| **Linux slideshow** | dual-source 時 **per-monitor-auto-split** + `xfconf-query` path（[slideshow-spec](../specs/slideshow/harite-slideshow-spec.md)） | 実行中 2→1 枚は **pause**（別問題） |
| **Windows slideshow** | dual-source 時 **Span**（composite 1 枚） | 2 枚検出が前提の整理が多い |

P-03 の主眼は **「検出 1 枚のとき R 側 UI を誤操作不能にする」**。Slideshow の L/R 両方必須を緩めるかは **P3-2 gate**（本波のスコープ外にできる）。

---

## 2. 目標（案）

**検出ディスプレイが 1 枚のとき、R 側に関わる操作を無効化または誤操作不能にする。**

| 対象（案） | 操作 |
| --- | --- |
| Slideshow | R saved source combo、R srcdir、direction の R 寄り |
| Main | R path / direction / picker（要 P3-2） |
| Optimize / Apply | two-screen / per-monitor の R 寄り（**本波は対象外候補**） |

※ 詳細範囲は gate で確定。

---

## 3. 採用条件（issue #359 より）

1. 単 display **再現手順**の確立（開発・CI 用）— **§4 P3-1**
2. **disabled 範囲**の spec ストーリー合意 — P3-2
3. **GTK/Qt** 両 backend のテスト方針 — P3-3

---

## 4. 着手 gate checklist

| # | 論点 | 提案 | オーナー |
| --- | --- | --- | --- |
| P3-1 | 再現手順 | §4.1–4.3 の観測を **2 台×2 枚環境**で実施し、§5 テンプレに記録。pass = Harite が **1 枚**と数える操作が **OS ごとに 1 つ以上**確定 | |
| P3-2 | disabled 範囲 | Slideshow R 一式のみ（Main R / Optimize は対象外） | |
| P3-3 | 検出タイミング | 起動時 + Slideshow/Main タブ表示時 +（可能なら）display 変更後の再評価 | |
| P3-4 | 1 枚でも dual 意図 | 将来「論理 L/R のみ」ニーズはスコープ外と明記 | |
| P3-5 | DP / HDMI | §4.4 の癖を観測メモに 1 行以上残す（同じ操作でも端子で差が出うる） | |

### 4.1 Harite が見ているもの（共通）

product が参照するのは **OS API 経由の接続モニタ列挙のみ**（XFCE 設定 UI や Win 設定アプリの表示と **必ずしも一致しない**）。

**観測時の Harite 側ログ（両 OS 共通）:**

```bash
python -c "from harite.workspace import detect_displays; d=detect_displays(); print(len(d), d)"
```

- 第 1 数値 = `len(detect_displays())` — **P-03 の閾値はここ**（`< 2` で単 display 扱いの案）。
- 各 `Display`: `name`, `width`, `height`, `x_offset`, `y_offset`, `primary`（Windows は `scale_percent` あり）。

backend（`harite-qt` / `harite-gtk`）は同じ core を使う。**観測は GUI 起動前後どちらでも可**（まず上記 one-liner で足りる）。

### 4.2 Linux（XFCE / X11）— 再現手順案

**正本:** `xrandr --query` の ` connected ` 行を数える（`workspace._detect_linux`）。

#### ベースライン（2 枚）

```bash
xrandr --query | grep " connected "
python -c "from harite.workspace import detect_displays; print(len(detect_displays()))"
```

両方 **2** であることを記録。

#### 1 枚へ落とす操作（優先順 — 上から試す）

| 順 | 操作 | 期待 | 備考 |
| --- | --- | --- | --- |
| L1 | `xrandr --output <副次出力名> --off` | `connected` 行が 1、Harite `len==1` | **CI / 開発再現の第一候補**。出力名は `xrandr --query` 先頭列（例: `DP-1`, `HDMI-1`） |
| L2 | XFCE **設定 → ディスプレイ** で副次を無効化 | L1 と同型 | GUI 操作の実機メモ用 |
| L3 | 副次モニターの **ケーブル物理抜き**（DP または HDMI） | `connected` が `disconnected` に変わり `len==1` | **推奨の実機再現**（[#359](../online-issues/issue-359.md)） |
| L4 | 副次モニターの **電源 off のみ**（ケーブル接続のまま） | 多くの環境で **2 枚のまま** | **再現に使わない**（負例として記録） |

復帰: `xrandr --output <名> --auto` またはケーブル再接続 → 再び 2 枚。

#### XFCE で見る UI（観測メモ用）

- Slideshow / Main の **R 側 widget が有効か**
- dual-source slideshow 実行中に L1 で 2→1 にしたとき **pause するか**（P-03 スコープ外だが §5 に一行残す価値あり）

### 4.3 Windows — 再現手順案

**正本:** `EnumDisplayMonitors` + `MONITORINFOEXW`（`workspace._detect_windows`）。`Display.name` は `\\.\DISPLAYn` 形式。

Windows は Linux より **「設定 UI で見える世界」**と Harite の対応が直感しづらい。観測は **常に §4.1 one-liner を軸**に、OS 操作はラベル付きで記録する。

#### ベースライン（2 枚）

1. **設定 → システム → ディスプレイ** でディスプレイが 2 つ並ぶことを確認。
2. §4.1 one-liner → `len == 2` を記録。
3. （任意）`Win + P` が **拡張** であること。

#### 1 枚へ落とす操作（優先順）

| 順 | 操作 | 記録すること | 備考 |
| --- | --- | --- | --- |
| W1 | **設定 → ディスプレイ → 副次 → 「このディスプレイを切断」**（Win11 一部環境） | 設定上 1 枚になったか + Harite `len` | UI に無い環境あり → W2′ へ |
| W2 | `Win + P` → **PC 画面のみ** | 同上 | ノート + 外付けでよく使う |
| W2′ | **設定 → ディスプレイ → 「1 のみに表示する」**（日本語 Win11 実機 2026-06-06） | 同上 | W1 代替。**HDMI 副次を論理 off → Harite `len==1` 確認済み**（§5.2–5.3） |
| W3 | 副次の **ケーブル物理抜き**（DP / HDMI） | 同上 | **推奨の実機再現** |
| W4 | 副次モニター **電源 off のみ** | Harite `len` が 2 のままか | **負例**（HDMI/DP とも EDID 残存しうる） |

復帰: ケーブル再接続 / 設定でディスプレイを検出 / `Win + P` → 拡張。

#### Windows 観測で迷いやすい点

| 項目 | 説明 |
| --- | --- |
| 設定アプリの「1 画面」 | ユーザーには 1 枚に見えても **Harite が 2 と数える**ことがある（切断前の幽霊モニタ等）。**必ず one-liner** |
| **3 種類の番号はずれる** | 下記 §4.3.1。**設定の「ディスプレイ 1」≠ `DISPLAY1` ≠ Python の `0`** |
| Span / 拡張 | slideshow dual-source は **2 枚検出**前提の経路が多い（[gui-spec §6](../specs/gui/harite-gui-spec.md)）。1 枚時の Span 意味は P3-2 と別 |
| DPI / スケール | `scale_percent` が付くが P-03 の 1 枚判定には **使わない**（枚数のみ） |

#### 4.3.1 Windows の「ディスプレイ 1/2」と Harite `DISPLAYn` / Python index

**ずれています。** 3 層を混同しないこと。

| 層 | 例 | 意味 |
| --- | --- | --- |
| **Windows 設定 UI** | 「ディスプレイ **1**」「ディスプレイ **2**」 | 設定アプリの 1 始まりラベル。しばしば **主ディスプレイ = 1** |
| **Win32 / Harite `name`** | `\\.\DISPLAY**1**`, `DISPLAY**2**` | GDI デバイス名。**設定の番号と無関係**（`DISPLAY1` が「1 番目」とは限らない） |
| **Python one-liner の index** | `0`, `1` | `detect_displays()` リストの添字 = `EnumDisplayMonitors` の列挙順 |

**`win-cursor-dev` 実測（2026-06-06・Cursor を HDMI2 側へ移動後）:**

| Python index | Harite `name` | primary | 位置 | 物理端子 |
| --- | --- | --- | --- | --- |
| `0` | `DISPLAY2` | Yes | 左 (0,0) | **HDMI2** |
| `1` | `DISPLAY1` | No | 右 (3840,0) | **DisplayPort** |

→ 設定で「**ディスプレイ 1**」と表示されるのは多くの場合 **主＝HDMI2＝Harite `DISPLAY2`**。一方 **DP 物理端子**は Harite では **`DISPLAY1`**（index `1`）。**「Windows の 1」と「DISPLAY1」は逆に感じることがある。**

**観測記録のルール:** 設定 UI では **「ディスプレイ N」だけ書かない**。必ず **端子（HDMI/DP）・左右・主/副・one-liner 生 dump** をセットで残す。

### 4.4 DisplayPort / HDMI の観測メモ（P3-5）

端子ごとに **同じ「電源 off」でも Harite の `len` が変わらない**ことがある。2 台の観測では **ケーブル種別を必ず記録**する。

| 端子 | よくある癖 | 観測で確認すること |
| --- | --- | --- |
| **HDMI** | 電源 off でも `connected` / `EnumDisplayMonitors` が 2 のまま | L4 / W4 の負例として記録 |
| **DisplayPort** | 上に加え **DP MST ハブ・ドッキング**で出力名と物理モニタの対応が分かりにくい | `--off` した出力名がどの物理端子かメモ |
| **DP** | ノート内蔵 + 外付け DP で、内蔵を off にしないと 2 枚のまま | `xrandr` / 設定で **どちらを off したか** |

**実務:** 「1 枚再現」の正手は **OS 論理切断（L1/L2/W1/W2）または物理抜き（L3/W3）**。電源 off のみは **単 display UX の再現手段としては不採用**（負例記録のみ）。

---

## 5. 観測記録テンプレート（オーナー記入用）

各マシン・各状態で 1 行。観測後に本節を埋めるか、`docs/working/design/` または `finished/` に切り出してよい。

### 5.1 マシン識別

| フィールド | 値（win-cursor-dev） |
| --- | --- |
| ラベル | `win-cursor-dev` |
| OS | Windows（26200 系） |
| Harite backend | CLI one-liner（`harite.workspace`） |
| 構成 | デスクトップ 2 枚・横並び拡張。副次=右・**HDMI** |

### 5.2 状態 A — ベースライン（2 枚）

| 項目 | 記入 |
| --- | --- |
| 物理接続 | 左 primary + 右 **HDMI** |
| `xrandr --query` 要約（Linux） | — |
| 設定アプリ（Windows） | ディスプレイ 2 |
| `len(detect_displays())` | **2** |
| `detect_displays()` 生 dump | `DISPLAY1` 3840×2160 primary (0,0); `DISPLAY2` 3840×2160 (3840,0); scale 150% |

### 5.3 状態 B — 1 枚再現（操作ごとに 1 行）

| 操作 ID | 操作 | 端子 | `len` | R 側 UI（Slideshow） | メモ |
| --- | --- | --- | --- | --- | --- |
| W2′ | 設定 → **「1 のみに表示する」** | HDMI（副次） | **1** | **有効のまま** | `DISPLAY1` のみ残存。切断メニュー無し環境の正手 |
| 復帰 | 拡張（2 画面）に戻す | HDMI | **2** | — | W2′ の逆操作。ベースライン再確認 |
| W4 | 副次 **HDMI 電源 off のみ**（ケーブル接続維持） | HDMI | **2** | **有効のまま** | **負例確定** — EDID 残存で `EnumDisplayMonitors` も 2。単 display 再現に使わない |
| — | `harite-qt` Slideshow（P-03 未実装） | — | — | **R 一式まだ操作可** | `len==1` でも無効化なし。§2 の問題どおり |

### 5.4 P3-1 進捗（Windows `win-cursor-dev`）

| 項目 | 状態 |
| --- | --- |
| 1 枚再現の正手 | **W2′ 確定** |
| 電源 off のみ（負例） | **W4 確定**（HDMI・`len==2` 維持） |
| Linux 観測 | **未実施**（保留） |

**pass 判定（P3-1）:** 各 OS で、Harite `len==1` になる操作が **文書化済み**で、かつ **電源 off のみでは再現しない**ことがログで確認できる。**Windows は上表で半分 pass**（Linux 待ち）。

---

## 6. 実装フェーズ案（観測後）

| 段 | 内容 |
| --- | --- |
| 0 | 本書 + §5 観測記録 |
| 1 | gui-spec § 単 display disabled 追記 |
| 2 | Qt Slideshow tab（+ Main R?）disabled 配線 |
| 3 | テスト — `detect_displays` mock で `len<2` |
| 4 | GTK parity（XFCE 実機確認） |

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-06 | 初版 — C-01-E-KW 完了後のストック着手として起票 |
| 2026-06-06 | §4 Linux xrandr / Windows / DP・HDMI、§5 観測テンプレ、§1.1 現行 product 整理 |
| 2026-06-06 | Windows 実機観測 — W2′（1 のみに表示）で `len==1`（HDMI 副次） |
| 2026-06-06 | Windows 続き — 復帰 `len==2`、W4 HDMI 電源 off は `len==2`、qt R 側未無効化確認 |
| 2026-06-06 | §4.3.1 — 設定「ディスプレイ 1/2」と `DISPLAYn` / Python index のずれを明記 |

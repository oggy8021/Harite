# P-03 — 単 display / monitor まわり UX（計画正本）

最終更新: 2026-06-06  
ステータス: **完了**（#420 merge、#359 close、オーナー実機 OK — [3層比較](20260606-p03-3layer-audit.md)）

## 位置づけ

| 文書 | 役割 |
| --- | --- |
| [feature-overview §P-03](20260518-2047-feature-overview.md) | inventory 入口 |
| [issue #359](../../online-issues/closed/issue-359.md) | 起票メモ（クローズ済み） |
| [gui-spec § Main / Slideshow](../../specs/gui/harite-gui-spec.md) | dual-display 前提 UI + §4.3 P-03 |
| [slideshow-spec §2 / §6](../../specs/slideshow/harite-slideshow-spec.md) | start 条件 / per-monitor / pause |
| `src/harite/workspace.py` | **`detect_displays()`** 実装（本 issue の検出正本） |
| **本書** | 単 display 時の -R 無効化等 — 計画正本 |

**背景:** 物理 1 ディスプレイで R 側操作（path / srcdir / direction 等）の扱いが未整理。旧 K-01 monitor 縁はここに集約（H-08 破棄）。

---

## 1. 問題

- dual-display 前提の UI が、**1 枚検出**環境でも R 側が有効のまま。
- 単 display の **再現手順が未確立**（モニター電源 off だけでは枚数が減らない等 — [#359](../../online-issues/closed/issue-359.md)）。
- disabled 範囲・spec・GTK/Qt テスト方針が未合意。
- **Linux（XFCE / xrandr）と Windows（EnumDisplayMonitors）で「1 枚」の作り方と product 影響が異なる**が、planning に未整理だった。

### 1.1 現行 product との関係（観測前に押さえる）

| 層 | 現行契約 | 単 display での痛み |
| --- | --- | --- |
| **検出** | `harite.workspace.detect_displays()` — Linux=`xrandr --query`、Windows=`EnumDisplayMonitors` | OS が 2 枚と数える限り Harite も 2 枚 |
| **Main tab** | L/R 各 panel（path / direction / picker） | R も操作可能のまま |
| **Slideshow** | **L/R 両方 srcdir 必須**で Start 可（[gui-spec](../../specs/gui/harite-gui-spec.md)） | 1 枚でも dual-source 前提は維持 |
| **Linux slideshow** | dual-source 時 **per-monitor-auto-split** + `xfconf-query` path（[slideshow-spec](../../specs/slideshow/harite-slideshow-spec.md)） | 実行中 2→1 枚は **pause**（別問題） |
| **Windows slideshow** | dual-source 時 **Span**（composite 1 枚） | 2 枚検出が前提の整理が多い |

P-03 の主眼は **「検出 1 枚のとき R 側 UI を誤操作不能にする」**。Slideshow の L/R 両方必須を緩めるかは **P3-2 gate**（本波のスコープ外にできる）。

### 1.2 観測メモ — 活線・幽霊 `len==2` と auto-split（**現状維持**）

**Win / XFCE 共通:** ケーブル活線のまま OS が **2 枚と数える**（Linux L1 の `connected` 幽霊、Windows W4-HDMI 等）とき、Harite も **`len==2`**。現行 product は **OS 列挙をそのまま信じる**（`0x0` 幽霊も 1 枚として数える）— **意図どおり・変更不要**。

| 観測例 | Harite `len` | dual-source / auto-split |
| --- | --- | --- |
| Linux L1（論理 off・幽霊 `0x0` + 実出力） | **2** | **動きうる** |
| Windows W4-HDMI（EDID 幽霊） | **2** | 2 枚前提の経路のまま |

→ P-03 は **素直に `len==1` のときだけ** R 無効化する。**「見た目 1 画面だが OS は 2 枚」** は観測で把握済みだが、product 方針として **そのまま**（幽霊対策・`width>0` フィルタ等は本 issue のスコープ外）。**GTK / Qt 共通**（core 正本）。

---

## 2. 目標（`len==1` 時）

**検出 1 枚のとき、UI 第二スロット（現ラベル **R** 側）を誤操作不能にする**（§2.1）。判定は `len(detect_displays()) < 2` のみ。

### 2.2 無効化（塞ぐ）対象 — P3-2 合意（2026-06-06）

**Surface（widget）で `disabled` にするもの:**

| Tab | 第二スロット（R 側）で塞ぐもの |
| --- | --- |
| **Main** | 十字 **寄せ direction 群**（R 列）。**`Open-R` / `Clear-R` / `Preview-R`**。可能なら中央 **`Swap L/R`** |
| **Slideshow** | **R に対応する操作群** — `combo_slideshow_source_r`、`Srcdir-R`、`Clear-R`、path 表示まわり。中央 **`Swap L/R`** |

**訂正（impl）:** Margins の **Position** 行（Left/Right × Top/Bottom）は **合成画像の埋め込み角** であり第二スロットではない。単 display でも **4 角すべて有効**（P-03 初版で Right 列を誤って disabled にしていたのを撤回）。

**Surface は弄らない（棚卸し時に再評価可）:**

| 領域 | 方針 |
| --- | --- |
| **`combo_slideshow_profile`**（profile row） | widget はそのまま。**profile に R slot があっても実行時に無視** |
| **`More slideshow options…`（Drawer 内）** | Surface 変更なし。第二スロット向けの指定が残っていても **owner 側で無視** |
| **Manage sources and profiles…（dialog）** | 本波では dialog 内の L/R slot 編集は **塞がない**（設定は残せるが `len==1` 実行では効かない） |

**本波対象外（塞がない）:** Main の **`Optimize` / `Apply`** ボタン群、CODH chip、interval/start/stop、Drawer の mode/help 等。細部は実装棚卸しで追記可。

**実行時の無視（UI 以外）:** Start / optimize / apply 経路で第二スロット相当の path・source id・profile の R メンバーは **参照しない**（単一出力として L スロットのみ）。既存の「両 srcdir 必須」は `len==1` では緩和（L のみで Start 可にするかは impl 時に gui-spec 追記）。

### 2.1 用語 — 「R 無効化」の意味（P3-2 向け）

issue [#359](../../online-issues/closed/issue-359.md) は **「右パネル」** と書いているが、これは **2 枚運用時の UI 配置**（Main / Slideshow の **右カラム＝第二スロット**）に由来する。**物理の左右や OS の「ディスプレイ 1/2」とは一致しない**（観測: Windows 設定番号 ≠ Harite 順序 ≠ `DISPLAYn` / `xrandr` 名）。

| 文脈 | 正確な読み |
| --- | --- |
| **`len==1`（物理 1 台）** | そもそも **左右 2 出力がない**。UI の L/R は **論理スロットの名残** — 「右を無効化」≒ **第二出力用の操作を誤操作不能にする** |
| **`len==2`（現行 UI 前提）** | Harite の L/R は `order_displays`（**x_offset 昇順**）の **先頭＝L スロット、次＝R スロット**。ユーザーがケーブル・設定で左右や 1/2 を揃えているかは **任意**（オーナー環境は偶然揃っているだけ） |
| **計画文書の「R 無効化」** | 実装・spec 上の **現 UI ラベル（`Srcdir-R` 等）に紐づく第二スロット**を指す略称。**地理的 Right の保証ではない** |

**将来別案（本波外）:** 検出済み出力名（`HDMI-1` / `DP-1` 等）をパネルにラベル表示し、**存在しない出力スロット**を無効化する — その場合「常に R」ではなく **どちらのカラムを gray out するかは検出結果次第**になりうる。P-03 本波は **既存 L/R レイアウトのまま第二スロットのみ disabled** で足りる（P3-2 gate）。

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
| P3-2 | disabled 範囲 | **合意済み** — §2.2。Profile / More options は Surface 据え置き・実行時無視 | |
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
| L1 | `xrandr --output <副次出力名> --off` | 画面は 1 枚だが **`connected` 行は残りうる** → Harite **`len==2` のまま**（§4.2.2 実測） | xrandr / XFCE GUI の論理 off。**P-03 単 display 判定には使えない**可能性が高い |
| L2 | XFCE **設定 → ディスプレイ** で副次を無効化 | L1 と同型 | GUI 操作の実機メモ用 |
| L3 | 副次モニターの **ケーブル物理抜き**（DP または HDMI） | `connected` が `disconnected` に変わり `len==1` | `linux-xfce` では **未実施**（L4 で `disconnected` 確認済み・§5.6） |
| L4 | 副次モニターの **電源 off のみ**（ケーブル接続のまま） | 環境依存 — **幽霊のまま**または **`disconnected`** | `linux-xfce` 実測: R/DP 電源 off → **`len==1`**（§4.2.2） |

復帰: ケーブル再接続、または **明示レイアウト**（§4.2.3）。`--auto` 単体は **縮小解像度の拡張配置を復元しない**ことがある。

#### 4.2.1 実機ラボ構成 — `linux-xfce`（Windows とは別世界）

**共有ディスプレイ:** モニター操作パネルで入力（HDMI / DP 等）を切り替え、**同一物理画面を Windows 機と XFCE 機で共有**する。観測時は **モニター入力を Linux 側に合わせてから** one-liner を取る（Windows の §4.3.2・§5 は **流用しない**）。

**端子対応は Windows と逆:** `win-cursor-dev` では設定 **1＝DP（主）・2＝HDMI** だったが、XFCE 実機では **主副・左右の DP/HDMI の割当が逆**になりうる。Linux では **`xrandr --query` の出力名（`DP-1` / `HDMI-1` 等）＋ primary ＋ 座標**だけを正本に記録する。

| 層 | `win-cursor-dev`（参考・Linux に持ち込まない） | `linux-xfce` 実機 |
| --- | --- | --- |
| 設定 UI の番号 | 1＝DP、2＝HDMI | XFCE ディスプレイ設定は **実機で都度確認** |
| Harite / OS の識別子 | `DISPLAYn`（信用しない） | **`xrandr` 先頭列**（`DP-1` 等 — Harite `Display.name` と一致） |
| 観測の見え方 | 2 画面同時 | **入力切替で 1 画面ずつ見える**が、`xrandr` / Harite は **接続中の出力を列挙**（見えている入力と無関係） |

**P3-1 の前提:** Linux 側でも **2 出力が `connected`** のベースラインが必要（副次は別モニターでもダミーでもよいが、`xrandr` が 2 行返すこと）。共有モニター 1 台だけでは `len==1` 固定になりうる — その場合は **2 本目の接続**を確認してから観測開始。

#### 4.2.2 Harite `_detect_linux` の癖（`linux-xfce` 実測 2026-06-06）

`workspace._detect_linux` は `xrandr --query` の **` connected ` を含む行をすべて数える**。解像度が無い（`--off` 後の `DP-1 connected (normal …)` のみ）出力も **1 枚として列挙**する。

| 操作 | xrandr | Harite |
| --- | --- | --- |
| ベースライン | `HDMI-1` primary 2048×1280 + `DP-1` 2048×1280 | `len==2` |
| **L1** `xrandr --output DP-1 --off` | `HDMI-1` は従来どおり。**`DP-1 connected`（モード行なし）が残る** | **`len==2`** — `DP-1` は `0x0` @ (0,0) |

→ **論理 off（L1/L2）だけでは「ユーザーには 1 画面」でも Harite は 2 枚**（`0x0` 幽霊）。Windows の設定「○のみに表示」（`len==1`）とは **非対称**。

**`linux-xfce` まとめ（P3-1）:**

| 区分 | 操作 | Harite |
| --- | --- | --- |
| **正例** `len==1` | L4（R モニター DP 電源 off） | `DP-1 disconnected` |
| **負例** `len==2` | L1（`xrandr --off`・主/副とも） | `connected` 幽霊維持 |
| **スキップ** | L3 ケーブル抜き | L4 で `disconnected` 経路は確認済み。物理 1 台運用も別枠で想定済み（§4.2.4） |

#### 4.2.4 物理モニター 1 台のユーザー（P-03 の本丸）

**ケーブル 1 本・出力 1 つ**だけ接続している環境では、最初から `xrandr` / Harite とも **`len==1`**。2 枚観測ラボ（`linux-xfce`）は **「論理 off が効かない」負例**と **「電源 off / 論理切断の差」**のための補助実験。product 上の単 display UX は **この 1 台構成が主**で、P-03 の `len < 2` 判定は素直に効く。

#### 4.2.3 復帰 — `--auto` の罠（`linux-xfce` 実測）

ローパワー用途で **縮小解像度（2048×1280）・拡張（DP 右）** で運用している環境では、L1 後の `xrandr --output DP-1 --auto` が **以前のレイアウトに戻らない**ことがある。

| 項目 | ベースライン（観測前） | `--auto` 復帰後（実測） |
| --- | --- | --- |
| `HDMI-1` | primary 2048×1280 @ (0,0) | 同左 |
| `DP-1` | 2048×1280 @ (2048,0) | **3840×2160 @ (0,0)** — ネイティブ解像度・**主と座標重複** |
| Harite `len` | 2 | **2**（枚数は変わらず、幾何だけ壊れる） |

**観測後の復帰（本マシン向け）:** モードが存在すれば明示指定する。

```bash
xrandr --output HDMI-1 --mode 2048x1280 --pos 0x0 --primary
xrandr --output DP-1 --mode 2048x1280 --pos 2048x0
```

`2048x1280` が `DP-1` のモード一覧に無い場合は `xrandr --query` で利用可能モードを確認。P-03 の `len` 判定には座標重複は **影響しない**（枚数のみ）。

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
| Span / 拡張 | slideshow dual-source は **2 枚検出**前提の経路が多い（[gui-spec §6](../../specs/gui/harite-gui-spec.md)）。1 枚時の Span 意味は P3-2 と別 |
| DPI / スケール | `scale_percent` が付くが P-03 の 1 枚判定には **使わない**（枚数のみ） |

#### 4.3.1 Windows — 設定 UI・GDI 名・列挙 index（信用できるものの切り分け）

**結論（2026-06-06 実機）:** `Display.name`（`\\.\DISPLAYn`）は **product / 観測の対応づけに使わない**。GDI 名は **再起動 vs サインアウトで同じ物理 1 枚でも変わる**（下記 DP-only 実験）。設定の「ディスプレイ 1/2」や primary の印とも無関係。

| 層 | 信用 | 説明 |
| --- | --- | --- |
| **Windows 設定 UI**「ディスプレイ 1/2」 | ○（ユーザー操作の記録用） | **本マシン固定対応（§4.3.2）**。主＝設定 **1**＝**DP**（弄らない） |
| **`Display.name` / `DISPLAYn`** | **×** | Win32 `MONITORINFOEX.szDevice`。**再起動で `DISPLAY1`、サインアウトのみでは `DISPLAY2`**（同一 DP 単独接続でも不一致）。識別子として使えない |
| **Python list index `0`,`1`** | △ | `EnumDisplayMonitors` の**その回の**列挙順。セッション内の同定には `primary` + 座標の方がマシ |
| **`primary` + `x_offset`/`y_offset` + 解像度** | ○ | P-03 実装・観測で使う Harite 側の安定した信号 |
| **`len(detect_displays())`** | ○ | **単 display 判定の正本**（`< 2`） |

#### 4.3.2 `win-cursor-dev` — 設定番号と物理端子（観測正本・弄らない）

| 設定 UI | 物理端子 | primary |
| --- | --- | --- |
| **ディスプレイ 1** | **DisplayPort** | **Yes**（固定） |
| **ディスプレイ 2** | **HDMI** | No |

**W2′ の読み（本マシン）:**

| 設定操作 | 意味 |
| --- | --- |
| **「1 のみに表示する」** | **DP のみ** — HDMI を Windows から論理切断 |
| **「2 のみに表示する」** | **HDMI のみ** — DP を Windows から論理切断 |

GDI `DISPLAYn` は設定番号・端子と無関係（下記 2 枚 dump は参考のみ）。

**2 枚・拡張復帰後の dump 例（2026-06-06）:** `0: DISPLAY1 primary (0,0)` + `1: DISPLAY2 (3840,0)` — **左＝設定1＝DP、右＝設定2＝HDMI** と座標で同定（`name` は信用しない）。

**P-03 impl 契約（案）:** Windows では `len(detect_displays()) < 2` のみで R 無効化を判定。`Display.name` によるマッチングは **行わない**（Linux の per-monitor ファイル名用途とは切り離す — [slideshow-spec §6](../../specs/slideshow/harite-slideshow-spec.md) は Linux `HDMI-1` 等が正本）。

**DP 単独接続・`len==1` の GDI 名比較（物理 DP のみ・HDMI 未接続）:**

| セッション操作 | `name` | `primary` | 解釈 |
| --- | --- | --- | --- |
| **サインアウト → ログイン**（電源落とさず） | `DISPLAY2` | True | 前セッションの列挙/アダプタ状態が残る様子 |
| **再起動後** | `DISPLAY1` | True | 起動時に見えていた出力に別番号が振られる |

→ **同じ 1 枚・同じ端子でも `DISPLAYn` は安定しない。** P-03 は **`len` のみ**でよい。

**`len==1` 時の `primary`:** **どちらが止められたかの判定には使えない**（2026-06-06 DP「2のみ」実測）。残存 1 枚だけになると Windows が **その出力を primary に昇格**させる（`2のみ` でも `primary=True`）。**止めた側は操作メモ（「1のみ」「2のみ」）で記録**する。

**2 枚復帰後も GDI 名は入れ替わる:** DP-only 再起動→拡張復帰後、同一物理でも以前の 2 枚観測（`DISPLAY2`=主左）から **`DISPLAY1`=主左 / `DISPLAY2`=右** に変化（§5.2 後半）。**名前でモニターを追跡しない。**

**観測記録のルール:** 設定は **「ディスプレイ N（主/副）」+ 端子（HDMI/DP）+ 左右**。one-liner は **`len` / `primary` / 座標**を貼る。`DISPLAYn` は参考脚注程度。

### 4.4 DisplayPort / HDMI の観測メモ（P3-5）

端子ごとに **同じ「電源 off」でも Harite の `len` が変わらない**ことがある。2 台の観測では **ケーブル種別を必ず記録**する。

| 端子 | よくある癖 | 観測で確認すること |
| --- | --- | --- |
| **HDMI（設定 2・副次）** | 電源 off のみでも `EnumDisplayMonitors` が **2 のまま**（EDID 幽霊） | **W4-HDMI 負例** — 単 display 再現に使わない |
| **DisplayPort（設定 1・主）** | 電源 off で **`len==1`**（ケーブル接続でも枚数維持しない） | **W4-DP ではない** — DP off で単 display になりうる（再現手順としては電源依存） |
| **DP** | MST ハブ・ドックで出力名と物理の対応が分かりにくい | 操作は **設定ディスプレイ N + 端子**で記録 |

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
| 構成 | 2 枚・拡張。設定 **1＝DP（主・固定）** + **2＝HDMI**（§4.3.2） |

### 5.2 状態 A — ベースライン（2 枚）

| 項目 | 初回（2 枚） | 復帰（DP-only 再起動後・拡張に戻す） |
| --- | --- | --- |
| 物理接続 | 左 **DP（設定1・主）** + 右 **HDMI（設定2）** | 同左（拡張復帰） |
| 設定アプリ | ディスプレイ 2 | ディスプレイ 2 |
| `len` | **2** | **2** |
| `primary` 左 | Yes（`DISPLAY2` ※名のみ） | Yes（`DISPLAY1` ※名のみ） |
| 生 dump（参考） | `0: DISPLAY2 primary (0,0)`; `1: DISPLAY1 (3840,0)` | `0: DISPLAY1 primary (0,0)`; `1: DISPLAY2 (3840,0)` |

→ **GDI 名はセッションで入れ替わる。`len`/`primary`/座標は 2 枚復帰として一致。**

### 5.3 状態 B — 1 枚再現（操作ごとに 1 行）

| 操作 ID | 操作 | 端子 | `len` | R 側 UI（Slideshow） | メモ |
| --- | --- | --- | --- | --- | --- |
| W2′-DP | 設定 → **「1 のみに表示する」**（DP のみ・HDMI 論理 off） | DP | **1** | **有効のまま** | 初回セッション。正手は W2′-HDMI も可 |
| 復帰 | 拡張（2 画面）に戻す | HDMI+DP | **2** | — | W2′ 後の復帰 |
| 復帰2 | DP-only 再起動後・拡張に戻す | HDMI+DP | **2** | — | GDI 名が初回 2 枚時と **入れ替わり**（§5.2） |
| W4-HDMI | **設定 2（HDMI）電源 off のみ**（ケーブル維持） | HDMI | **2** | **有効のまま** | **負例確定** — EDID 幽霊。単 display 再現に使わない |
| — | `harite-qt` Slideshow（P-03 未実装） | — | — | **R 一式まだ操作可** | `len==1` でも無効化なし。§2 の問題どおり |
| DP-only | **サインアウト → ログイン**（DP のみ接続） | DP | **1** | — | `name=DISPLAY2` primary — GDI 名は信用不可の決定打 |
| DP-only | **再起動**（DP のみ接続） | DP | **1** | — | `name=DISPLAY1` primary — **同一 1 枚で名が変わる** |
| W2′-HDMI | 設定 **「2 のみに表示する」**（**HDMI のみ**・DP 論理 off） | HDMI | **1** | — | 残存 `DISPLAY2` (0,0) `primary=True`（単独昇格） |
| DP-off | **設定 1（DP）電源 off**（ケーブル維持） | DP | **1** | — | **HDMI のみ残存**（`DISPLAY2`）。DP は枚数維持しない ≠ W4-HDMI |

### 5.4 P3-1 進捗（Windows `win-cursor-dev`）

| 項目 | 状態 |
| --- | --- |
| 1 枚再現の正手 | **W2′ 確定** |
| 電源 off のみ | **W4-HDMI 負例**（HDMI off→`len==2`）。**DP off→`len==1`**（非対称） |
| GDI 名 | **信用不可確定**（再起動/サインアウト/復帰で変動） |
| 2 枚復帰 | **復帰2 確認**（`len==2`） |
| 観測クローズ | **2026-06-06 完了** — 再起動後もケーブル抜き不要。以降の作業は **設定 1/2＋端子**のみ記録し **`DISPLAYn` に同定しない** |
| Linux 観測 | **完了**（`linux-xfce` — §5.6） |

**pass 判定（P3-1）:** 各 OS で Harite `len==1` / `len==2` 維持の **場合分けが文書化済み**であること。

| OS | `len==1` の例 | `len==2` 維持の負例 | 状態 |
| --- | --- | --- | --- |
| Windows | W2′（設定「○のみ」）、DP 電源 off | W4-HDMI（HDMI 電源 off 幽霊） | **pass** |
| Linux | L4（DP 電源 off）、物理 1 台（§4.2.4） | L1（`xrandr --off` 幽霊） | **pass** |

※ 「電源 off のみは常に負例」ではない — **OS・端子で非対称**。再現手順の正本は OS ごとに §5 に記載。

### 5.5 Linux（XFCE）— `linux-xfce`

| フィールド | 値 |
| --- | --- |
| ラベル | `linux-xfce`（仮） |
| OS | Linux / XFCE / X11 |
| ラボ | モニター入力切替で Windows と画面共有。**端子対応は Windows と逆**（§4.2.1） |
| 物理 | **L**＝`HDMI-1`。**R** モニターは **3 端子**（Linux は `DP-1` 使用。`HDMI-2` は未使用で常時 `disconnected`） |
| Harite backend | CLI one-liner（`harite.workspace`） |

**状態 A — ベースライン（2 枚）:**

| 出力 | primary | 位置 | 備考 |
| --- | --- | --- | --- |
| `HDMI-1` | Yes | 左 (0,0) 2048×1280 | **主** — Windows 実機と逆（§4.2.1） |
| `DP-1` | No | 右 (2048,0) 2048×1280 | 副次 |

Harite: `len==2`（名前・座標は xrandr と一致）

**状態 B — 1 枚再現:**

| 操作 ID | 操作 | `xrandr connected` 行数 | Harite `len` | メモ |
| --- | --- | --- | --- | --- |
| L1-DP | `xrandr --output DP-1 --off` | **2**（`DP-1 connected` モードなしで残存） | **2** | `DP-1` は `0x0`。**負例** — 論理 off では P-03 閾値に届かない |
| L1-HDMI | `xrandr --output HDMI-1 --off` | **2**（`HDMI-1 connected` モードなしで残存） | **2** | `HDMI-1` は `0x0`・`primary=True` のまま。DP のみ 2048×1280。**副次/主を問わず負例** |
| L1-HDMI復帰 | L 側復帰（明示 xrandr） | **2** | **2** | ベースラインどおり — `HDMI-1` 主左 / `DP-1` @(2048,0) |
| L1復帰 | `xrandr --output DP-1 --auto` | 2 | **2** | **レイアウト崩れ** — DP が 3840×2160@(0,0) に。§4.2.3 の明示復帰を使う |
| L4 | **R モニター DP 側のみ電源 off**（`DP-1` ケーブル維持） | **1**（`DP-1 disconnected`） | **1** | `HDMI-1` のみ残存。L1（論理 off）とは **対照** — 電源 off で `disconnected` 化 |
| L4復帰 | R モニター電源 on | **2** | **2** | ベースラインどおり — `HDMI-1` 主左 / `DP-1` 2048×1280@(2048,0) |

### 5.6 P3-1 進捗（Linux `linux-xfce`）

| 項目 | 状態 |
| --- | --- |
| ベースライン | **確定** `len==2`（HDMI-1 主左 / DP-1 副右） |
| L1 論理 off | **負例確定** — `DP-1` / `HDMI-1` とも `len==2` 維持（§4.2.2） |
| L4 電源 off | **実施** — R モニター DP 側 off → `len==1`。**復帰確認済み** → `len==2` |
| L3 ケーブル抜き | **スキップ** — L4 で `disconnected` 確認済み。物理 1 台想定で十分（§4.2.4） |
| L2 XFCE GUI | **未実施**（L1 と同型の見込み） |
| `harite-gtk` R UI | **未実施** — core 共通のため Qt と同型と見做す（§1.2） |
| 観測クローズ | **2026-06-06 完了** |

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
| 2026-06-06 | Windows 実機観測 — W2′-DP（「1 のみ」＝DP 残し）で `len==1` |
| 2026-06-06 | Windows 続き — 復帰 `len==2`、W4-HDMI（設定2 電源 off）は `len==2`、qt R 未無効化 |
| 2026-06-06 | §4.3.1 — 設定「ディスプレイ 1/2」と `DISPLAYn` / Python index のずれを明記 |
| 2026-06-06 | §4.3.1 改訂 — GDI `DISPLAYn` は電源 on 順で信用不可。P-03 は `len` + `primary`/座標のみ |
| 2026-06-06 | DP-only 実験 — サインアウト=`DISPLAY2`、再起動=`DISPLAY1`（いずれも `len==1`） |
| 2026-06-06 | 拡張復帰2 — `len==2`、`DISPLAY1`=主左（GDI 名は初回 2 枚時と入替） |
| 2026-06-06 | W2′-HDMI「2のみ」— `len==1`、`DISPLAY2` 残存・`primary=True`（単独昇格） |
| 2026-06-06 | DP-off（設定1 電源 off）— `len==1`、HDMI 残存。DP は枚数維持しない（≠ W4-HDMI） |
| 2026-06-06 | §4.3.2 — 設定対応正本化：**1＝DP（主）、2＝HDMI**（従来メモの逆転を訂正） |
| 2026-06-06 | 設定対応修正 — **1＝DP（主）、2＝HDMI**。W2′-HDMI「2のみ」・DP 電源 off→`len==1` |
| 2026-06-06 | Windows 観測クローズ — 再起動後もケーブル維持可。`DISPLAYn` は実装・記録の同定に使わない |
| 2026-06-06 | §4.2.1 — XFCE 実機は共有モニター・端子逆。Windows §4.3.2 を Linux に持ち込まない |
| 2026-06-06 | §4.2.2 — L1 `DP-1 --off` でも `connected` 残存 → Harite `len==2`（`0x0` 幽霊） |
| 2026-06-06 | §4.2.3 — `--auto` 復帰で縮小解像度・拡張レイアウトが崩れる（DP 4K@(0,0)） |
| 2026-06-06 | L4 — R モニター DP 電源 off → `DP-1 disconnected`、`len==1`（L1 負例と対照） |
| 2026-06-06 | L4 復帰 — 電源 on でベースライン復帰（2048×1280 拡張・`len==2`） |
| 2026-06-06 | L1-HDMI — `HDMI-1 --off` でも `connected` 残存・`primary` 維持 → `len==2` |
| 2026-06-06 | L1-HDMI 復帰 — 明示 xrandr でベースライン復帰（`len==2`） |
| 2026-06-06 | L3 スキップ・Linux 観測クローズ — §4.2.4 物理 1 台想定。P3-1 pass（両 OS） |
| 2026-06-06 | §1.2 — 活線幽霊 `len==2` でも auto-split 動きうる。**現状維持**（変更不要） |
| 2026-06-06 | §2.1 — 「R 無効化」＝第二出力 UI スロット。物理左右・OS 1/2 とは無関係 |
| 2026-06-06 | §2.2 — P3-2 塞ぐ対象列挙。Profile / Drawer は Surface 不変・実行時無視 |

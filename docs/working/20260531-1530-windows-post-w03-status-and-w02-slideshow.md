# Windows 到達状況精査 — post W-03（B-lite マージ後）と W-02 スライドショー

作成: 2026-05-31  
起点: PR #352（W-03-B-lite）マージ後。W-02（#341）spec 化の前段整理。  
**追記 2026-05-31:** W-02 完了（#355 + #356、#341 クローズ）。本メモは planning 時点の記録として残す。

## 1. サマリ

| バックログ | Issue | 状態 | マージ / 備考 |
| --- | --- | --- | --- |
| W-01 | #342 | **完了** | #346 — Qt action cluster レイアウト |
| W-03-C | #343 | **完了** | #349 — EnumDisplayMonitors、two-screen 解像度 |
| W-03-B-lite | #343 | **完了** | #350（docs）+ **#352**（impl）— Span UI / Apply / `windows_apply_span` |
| W-02 | #341 | **完了** | #355（spec）+ **#356**（impl）— dual-source start、Interval / current UX |

**結論（更新）:** W-02-A 採用により Windows dual-source slideshow は **start から tick まで B-lite Span 経路で動作**。旧事象 `dual-source slideshow requires linux plugin` は解消。

---

## 2. W-03 完了内容（実装到達点）

### 2.1 コア / Apply

| 能力 | 実装 | テスト |
| --- | --- | --- |
| Win32 `per-monitor-auto-split` → single-file + `windows_span` | `apply_settings.resolve_apply_settings` | `test_resolve_apply_settings_windows_span_mode_uses_single_file` |
| HKCU Span（opt-in） | `windows_wallpaper.ensure_span_style` | `test_windows_wallpaper.py` |
| Settings `windows_apply_span` | `ApplySettings` | `test_settings_apply.py` |
| 2+ display 既定 Span | `AppSettings._default_apply_mode` | 同上 |
| 作業ディレクトリ（Pictures） | `_resolve_default_output_dir`（Win32 SHGetFolderPathW） | 間接（main_window signals） |

### 2.2 GUI

| 面 | 内容 |
| --- | --- |
| Main タブ | ラベル **Span** / **No Split**（`apply_surface`） |
| Settings | `windows_apply_span` チェックボックス（Qt + GTK） |
| Apply 前 | opt-in 時 `ensure_span_style()` |
| Preview | Optimize 後 sync（Qt QPixmap 経路 — #352 追補） |
| Settings Save | `Path` 受け付け（#352 追補） |

### 2.3 正本

| 文書 | 反映 |
| --- | --- |
| `harite-gui-spec.md` | Span / opt-in / プレビュー B'（#350） |
| `harite-plugin-spec.md` §4.1 | B-lite：core が single-file に解決（#352） |
| `issue-343.md` resolution | W-03-C + B-lite 方針 |

### 2.4 意図的に未実装（#343 合意）

- WallpaperStyle **自動復元**（slideshow 中の registry 書き戻し）
- Fit / Fill / Tile の Harite 制御（B-full 不採用）
- Windows per-monitor map apply

---

## 3. スライドショー現状（コード vs spec）

### 3.1 仕様どおりの挙動（Windows Qt 実機）

- Srcdir-L + Srcdir-R を指定して Start → **`dual-source slideshow requires linux plugin`**
- これは [slideshow-spec §9](specs/slideshow/harite-slideshow-spec.md) および `_prepare_slideshow_apply` の **linux plugin ゲート** に一致（#341 spec-as-designed）。

### 3.2 既に存在する Windows Span 経路（未接続）

`_apply_slideshow_selection`（dual-source tick）は B-lite マージで **Apply と同型** の処理を含む:

```text
run_slideshow_optimize → composite
  → resolve_apply_settings(per-monitor-auto-split)
  → windows_span なら single-file target + ensure_span_style(opt-in)
  → plugin.apply(target)
```

参照: `main_window.py` — `_apply_slideshow_selection`（`effective_apply.windows_span` 分岐）。

### 3.3 実際のブロッカー（1 箇所）

`_prepare_slideshow_apply(source_count > 1)`:

```python
if self.plugin_name != "linux":
    message = "dual-source slideshow requires linux plugin"
    return False
```

→ **Windows + dual-source は start 前に拒否**。tick 内の Span 経路には到達しない。

### 3.4 その他のギャップ

| 項目 | Linux 現行 | Windows 現行 | W-02 で決めること |
| --- | --- | --- | --- |
| dual-source start | linux + 2 displays | **拒否** | windows + 2 displays で **Span 経路を許可**するか |
| single-srcdir start | GUI は L/R **両方必須** | 同左（Start 不可） | Windows で **単一 srcdir** を許すか（CLI は可） |
| 作業ディレクトリ | `{Pictures}/Harite/slideshow/` | **同型**（SHGetFolderPathW） | spec に Windows 節を明記するだけで可 |
| スロットファイル | composite + per-monitor 分割 | Span 時は **composite のみ** | R2 を Windows Span 向けに読み替え（分割ファイル不要） |
| pause 条件 | display 2 枚喪失 | 未検証（ゲートで未到達） | Windows でも two-screen context 喪失時 pause 要否 |
| GUI 説明 | エラーメッセージのみ | 同上 | disabled 理由 / ヘルプ行（#341 UX） |

---

## 4. W-02 方針たたき台（B-lite 後）

オーナー合意（#343 resolution）: **slideshow = wide composite + Span**（opt-in 時 registry 維持）。Linux Auto-Split **見え方** に揃える。

### 4.1 推奨: W-02-A（B-lite 拡張 — dual-source on Windows）

| 項目 | 内容 |
| --- | --- |
| start 条件 | `plugin_name == windows` かつ display 2+ → dual-source **許可**（linux 限定を撤廃） |
| apply 経路 | 既存 `_apply_slideshow_selection` の `windows_span` 分岐をそのまま使用 |
| optimize | 既存 `run_slideshow_optimize` + two-screen context（W-03-C 済） |
| registry | Main Apply と同様 `windows_apply_span` opt-in |
| spec 変更 | `harite-slideshow-spec.md` §9、`harite-gui-spec.md` §6 Windows 注記、`issue-341` resolution |

**実装規模（見込）:** `_prepare_slideshow_apply` の条件分岐 + テスト数本 + spec PR。新 plugin 契約は不要。

### 4.2 ~~オプション~~ W-02-B（single-srcdir on Windows GUI）— **見送り**

- CLI は single-source 可（[cli-spec §6](../specs/cli/harite-cli-spec.md)）。GUI のみ L/R 両方必須（[gui-spec §6](../specs/gui/harite-gui-spec.md)）。
- **2026-05-31 不採用:** source 1 件は display 1 枚が通例。GUI 片方 Start は Not-Split 等の決めごとが増える。single display / single source は **別整理機会**。
- 代替: `harite slideshow --input <dir> ...`（single-file apply、CLI と同型）。

### 4.3 非推奨: 現状維持 + メッセージのみ

- spec-as-designed のまま。Qt で tab が見えるだけ改善。
- オーナー目標（左右別 srcdir スライドショー）と逆行。

---

## 5. spec 改訂チェックリスト（W-02 spec PR 用）

### 5.1 `harite-slideshow-spec.md`

- [ ] §9: 「dual-source は linux plugin 必須」→ **Windows は Span（single-file apply）経路** を追記
- [ ] §6.2 固定スロット: Windows Span 時は **composite スロットのみ**（per-monitor 分割ファイル非生成）
- [ ] §6.1 作業ディレクトリ: Windows Pictures 解決（`SHGetFolderPathW`）を明記
- [ ] シーケンス図 §3: Windows 分岐（composite → resolve → single apply）

### 5.2 `harite-gui-spec.md` §6

- [ ] Windows dual-source slideshow を **Span 前提** で起動可能と記載
- [ ] `windows_apply_span` が slideshow tick にも及ぶこと（#343 resolution 整合）
- [ ] Start ボタン enabled 条件（Windows 2+ display 時）の更新
- [ ] （任意）slideshow tab ヘルプ — Span / OS 設定の説明

### 5.3 `issue-341.md`

- [ ] resolution 節: W-02-A 採択案と spec PR / impl PR の順序

### 5.4 実装 PR（spec マージ後）

- [ ] `_prepare_slideshow_apply`: windows + 2 displays → `_slideshow_dual_auto_split_enabled = True`（名称は legacy のまま可）
- [ ] slideshow Windows 統合テスト（mock plugin / win32 platform）
- [ ] 実機: L/R srcdir → Start → 周期 Apply + Span 見え方

---

## 6. 3 層ざっくり（W-02 着手前）

| 層 | dual-source Windows slideshow |
| --- | --- |
| **spec** | linux 必須と明記。Span 経路なし |
| **tests** | linux plugin 拒否の間接テストのみ。Windows slideshow 成功路径なし |
| **impl** | tick 内 Span **あり** / start ゲート **linux のみ** → **不整合** |

→ W-02 は **spec を先に B-lite 整合** → **start ゲート修正** の順が .cursorrules に沿う。

---

## 7. 推奨 PR 順（これ以降）

1. **docs PR（本ブランチ）** — backlog / issue 更新 + 本文書
2. **spec PR（W-02）** — slideshow-spec + gui-spec + issue-341 resolution
3. **test PR** — Windows slideshow start / tick の期待値
4. **impl PR** — `_prepare_slideshow_apply` 解除 + 実機確認

---

## 関連

- [20260531-1200-windows-qt-validation-backlog.md](20260531-1200-windows-qt-validation-backlog.md)
- [20260531-w-03-b-lite-3layer-audit.md](20260531-w-03-b-lite-3layer-audit.md)
- [#341](../online-issues/issue-341.md) / [#343](../online-issues/issue-343.md)

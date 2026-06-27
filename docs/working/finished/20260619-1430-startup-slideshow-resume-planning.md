# #518 — スタートアップ時 Slideshow 再開 planning

**作成:** 2026-06-19  
**Issue:** [#518](../online-issues/issue-518.md)  
**分類:** enhancement  
**対象版:** **v2.0.2**  
**目標:** OS ログイン autostart で Harite が立ち上がったとき、ユーザー設定に従い **前回 exit 時に running だった Slideshow を再開**する。手動起動の挙動は変えない。

---

## 1. 背景と現状ギャップ

```text
現状フロー（いずれの起動経路も同じ）:
  app_qt.run()
    → MainWindow()
    → _load_default_settings_on_startup()  # interval, srcdir, mode 復元
    → connect_signals / tray 初期化
    → slideshow_running == False のまま待機
    → main window × ボタン → QMainWindow クローズ → アプリ終了（slideshow 停止）

要望フロー（autostart のみ）:
  ... 同上 ...
    → settings.startup_slideshow == true
    → AND --startup-launch
    → AND slideshow_was_running_at_exit == true  # 前回 exit 時に running
    → deferred: on_slideshow_start() + timer 開始
```

| レイヤ | 現状 | ギャップ |
| --- | --- | --- |
| settings JSON | slideshow 運用設定のみ | **startup フラグ・exit 時 running 永続化なし** |
| GUI | Start/Stop 手動 | **autostart 時の条件付き再開なし** |
| main window × | **ウィンドウ閉じ = アプリ終了** | 母体は **Invisible（hide）** 相当 |
| CLI / 入口 | `--present-ui-window` のみ | **`--startup-launch` なし** |
| OS 登録 CLI | なし | **提供しない**（README 手順のみ — オーナー確定） |

---

## 2. 要件（v2.0.2 確定）

### 2.1 機能要件

| ID | 要件 |
| --- | --- |
| R1 | settings に bool **`startup_slideshow`**（スタートアップ時に Slideshow を再開）を追加。既定 **false**。Slideshow タブ checkbox。 |
| R2 | **手動起動**（`--startup-launch` なし）では、フラグ ON でも **自動 Start しない**。 |
| R3 | **解釈 B（確定）:** autostart 時の自動 Start は **`slideshow_was_running_at_exit == true`** のときのみ（前回 **意図的 Stop または未 running で exit** した場合は Start しない）。 |
| R4 | **`slideshow_was_running_at_exit`** を `harite-settings.json` に永続化。`on_slideshow_stop` / 正常 Stop 経路で **false**。アプリ **Quit** 時に `slideshow_running` なら **true** を書き込む。 |
| R5 | 起動コンテキストは **`--startup-launch`**（または `HARITE_STARTUP_LAUNCH=1`）必須。 |
| R6 | 自動 Start は **`on_slideshow_start()` 同一経路**。失敗時は既存 error UI。 |
| R7 | autostart 推奨: **`--no-present-ui-window --startup-launch`**（README 記載。強制しない）。 |
| R8 | **sequential の cycle index** ログイン跨ぎ永続化は **v2.0.2 外**（running 意図のみ。index は start 時の既存規則どおり）。 |

### 2.2 自動 Start 条件（確定）

```text
should_auto_start_slideshow =
    settings.startup_slideshow
    AND launch_context.is_startup_launch
    AND settings.slideshow_was_running_at_exit
    AND NOT slideshow_running   # 起動直後
```

### 2.3 プラットフォーム

| プラットフォーム | v2.0.2 | 備考 |
| --- | --- | --- |
| **Windows** | ✓ | README に Startup ショートカット手順 |
| **XFCE** | ✓ | ユーザーが「セッションと起動」へ `.desktop` 配置 |
| **他 Linux** | パス | XFCE 手順を参考に autostart `.desktop` 自前配置 |

### 2.4 非要件

- xfce4-session 等の **ヒューリスティック自動検知のみ**
- シングルインスタンス
- `install-startup-entry` / `install-autostart-desktop` **CLI**（オーナー確定: 取り下げ）
- sequential cycle index のセッション跨ぎ JSON 保存

---

## 3. 設計

### 3.1 settings キー

| キー | 型 | 既定 | 保存タイミング |
| --- | --- | --- | --- |
| `startup_slideshow` | bool | `false` | ユーザー checkbox → 通常 save |
| `slideshow_was_running_at_exit` | bool | `false` | **アプリ Quit** / **Stop** 時に自動更新（ユーザー UI なし） |

- 論理グループ: slideshow 面（core-spec §6.3 追記）。
- `false` は JSON 省略可。
- `slideshow_was_running_at_exit` は **runtime 永続フラグ**（Settings dialog には出さない）。

**Quit 時書き込み（案）:**

```text
aboutToQuit / tray Quit:
  slideshow_was_running_at_exit = slideshow_running
  save_settings(default_path, merge=True)   # 他キーは維持
```

**Stop 時:**

```text
on_slideshow_stop（正常 Stop）:
  slideshow_was_running_at_exit = false
  save_settings(...)   # 即時 or 次回 quit まで — spec で統一
```

### 3.2 起動コンテキスト

| 手段 | 用途 |
| --- | --- |
| CLI **`--startup-launch`** | autostart `.desktop` / Startup `.lnk` の Exec |
| **`HARITE_STARTUP_LAUNCH=1`** | 環境変数代替 |

### 3.3 自動 Start タイミング

`connect_signals` + tray 初期化 + catalog 同期 **後**、`QTimer.singleShot(0, try_startup_slideshow)`。

### 3.4 失敗・エッジ

| ケース | 期待 |
| --- | --- |
| 前回 Stop 後に shutdown | `was_running_at_exit=false` → autostart **Start しない** |
| 前回 running のまま Quit | `true` → autostart **Start する** |
| srcdir 未設定 | Start 失敗 → error UI |
| display 未準備 | #493 pause 系と同型 |
| クラッシュ | 前回保存値が残る（許容） |

---

## 4. GUI / ドキュメント

### 4.1 Slideshow タブ checkbox（design slice 要）

| 要素 | 内容 |
| --- | --- |
| Checkbox | `Resume slideshow on session startup` / `セッション起動時に Slideshow を再開` |
| Help | `前回終了時に Slideshow が動いていれば、--startup-launch 付き起動で再開します。` |

### 4.2 README / release-delivery（CLI 登録は書かない）

**XFCE 例:**

```ini
# ~/.config/autostart/harite-slideshow.desktop
Exec=harite-qt --no-present-ui-window --startup-launch
```

**Windows 例:** Startup フォルダに `harite-qt.exe` ショートカット。引数に `--no-present-ui-window --startup-launch`。

---

## 5. 関連 UX — main window × ボタン（**判断待ち**）

### 現状（Qt）

| 操作 | 挙動 |
| --- | --- |
| tray **Invisible** | `window.hide()` — slideshow **継続** |
| tray **Quit** | `qapp.quit()` — slideshow **停止** |
| main window **×** | `QMainWindow` クローズ → 最後の window なので **`QApplication` 終了**（`setQuitOnLastWindowClosed` 未設定 = 既定 true） |

→ **× = 終了 = slideshow 停止**。母体（GTK 期）は × ≒ Invisible だった。

### 揃える場合（母体同型）

| 変更 | 内容 |
| --- | --- |
| `closeEvent` | `event.ignore()` + `hide()` + tray refresh |
| `QApplication.setQuitOnLastWindowClosed(False)` | window 非表示でもプロセス存続 |
| 終了 | **tray → Quit のみ** |

**#518 との関係:** autostart + tray 常駐では × で殺すと Slideshow 体感を損ねる。**同じ v2.0.2 で揃えるのが自然**（別 PR でも同一リリース可）。

### 選択肢

| 案 | 内容 | メリット | デメリット |
| --- | --- | --- | --- |
| **S1（母体同型）** | × = hide。Quit のみ終了 | Slideshow 継続。tray 中心 UX と一致 | Windows 慣習（×=終了）とズレ。初回ユーザーが tray に気づく必要 |
| **S2（現状維持）** | × = 終了 | 一般的な Windows UX | autostart / 常駐運用と矛盾。× 誤操作で slideshow 停止 |
| **S3（条件付き）** | running 中のみ ×=hide、停止中は quit | 折衷 | 状態で × の意味が変わり混乱しやすい |
| **S4（設定化）** | settings で × 動作を選択 | 柔軟 | 複雑。v2.0.2 には過剰の可能性 |

**planning 上の推奨:** **S1** を #518 と同梱候補として spec に載せる。README に「× はトレイへ格納。終了は tray → Quit」と明記。

**オーナー判断:** **S1 確定（2026-06-19）** — v2.0.2 同梱。gui-spec §7 反映済み。

---

## 6. 実装波（PR 分割案）

| 波 | 内容 |
| --- | --- |
| **0** | planning 確定 + design slice（checkbox + × 挙動注釈） |
| **1** | spec 改定（core §6.3, gui-spec §5–§7, cli `--startup-launch`） |
| **2** | テストのみ |
| **3** | settings キー + 永続化 + checkbox + `--startup-launch` + deferred start |
| **4** | × → hide + QuitOnLastWindowClosed（**S1 — 確定**） |
| **5** | README / release-delivery autostart + × 挙動 |

---

## 7. オーナー判断（確定 2026-06-19）

| # | 論点 | 決定 |
| --- | --- | --- |
| 1 | 「停止時より再開」 | **B:** 前回 exit 時 running なら autostart で再開 |
| 2 | 設定 UI | **Slideshow タブ checkbox** |
| 3 | Windows Startup 登録 CLI | **取り下げ** — README 等の説明のみ |
| 4 | Linux autostart desktop CLI | **取り下げ** — README 等の説明のみ |
| 5 | 対象版 | **v2.0.2** |
| 6 | × ボタン = hide vs quit | **S1 確定** — §5 |

---

## 8. 検証計画

| # | シナリオ | 期待 |
| --- | --- | --- |
| 1 | Stop → Quit → autostart | **Start しない** |
| 2 | running → Quit → autostart + フラグ ON | **Start する** |
| 3 | フラグ ON + 手動起動 | **Start しない** |
| 4 | running + ×（S1 時） | **hide、slideshow 継続** |
| 5 | tray Quit | 終了 + `was_running_at_exit` 更新 |
| 6 | `--no-present-ui-window --startup-launch` | tray のみ + 条件付き Start |

---

## 9. 関連リンク

- [#518](../online-issues/closed/issue-518.md)
- gui-spec §7 tray（Invisible / Quit）
- `MainWindow.on_slideshow_start` / `on_slideshow_stop`
- `qt_tray_adapter._on_toggle_visibility` / `_on_quit`

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-19 | 初版 |
| 2026-06-19 | オーナー判断反映（B / v2.0.2 / CLI 登録取り下げ）。× ボタン §5 追加 |
| 2026-06-21 | v2.0.2 リリース完了（PR #519, #521, #522）。`finished/` へ移動 |

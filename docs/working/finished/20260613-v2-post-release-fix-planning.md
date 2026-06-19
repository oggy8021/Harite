# v2.0.0 直後 — online-issues #492–#497 修正 planning

**作成:** 2026-06-13  
**ブランチ:** `docs/v2-1st-online-issue-listing-20260613`（本メモ + issue 索引まで）  
**親:** [online-issues/README.md](../online-issues/README.md) — v2.0.0 post-release 6件  
**目標:** bug 5件 + enhancement 1件の **着手順・PR 分割・spec/テスト方針** を固定し、実装 PR に渡す。

---

## サマリ

| # | 題材 | 分類 | 波 | 依存 |
| --- | --- | --- | --- | --- |
| [#492](../online-issues/issue-492.md) | Tray → Settings/Color で Main Window も表示 | bug（tray 回帰） | **1** | なし |
| [#494](../online-issues/issue-494.md) | tick 失敗後 Tray vs Main desync + 赤文字エラー不出 | bug（sync） | **1** | なし（**他 tick 系の前提**） |
| [#493](../online-issues/issue-493.md) | JMA 更新なし tick で optimize 走り停止 | bug + OP_LOG | **2** | #494 推奨（検証しやすくする） |
| [#497](../online-issues/issue-497.md) | 縦長 NDL + display scale で optimize fit 失敗 | bug（core/GUI） | **2** | #494 推奨 |
| [#496](../online-issues/issue-496.md) | Settings Save で keyword 消える | bug（settings） | **3** | なし |
| [#495](../online-issues/issue-495.md) | running 中の変更を次 tick に適用 | enhancement | **4** | #493 skip 設計と整合 |

**方針:** まず **観測可能にする（#494）** と **単独で閉じられる（#492）** を先に。slideshow tick の本体（#493 / #497）は同じ層（`on_slideshow_tick` / optimize）なので **1 PR にまとめてもよい** が、レビュー負荷を見て **2 PR（infra + JMA / fit）** に割ってもよい。

---

## 確定順序（実装波）

```text
Wave 1 — tray + tick 失敗の見え方（調査の前提）
  (1a) #492  tray present_main_window=False
  (1b) #494  timer tick 失敗時 sync + feedback（MAT-13 赤文字）

Wave 2 — slideshow tick 継続性
  (2a) #493  JMA filename_unchanged → tick skip + transient pause 拡張 + OP_LOG
  (2b) #497  intentional upscale 後 fit 不能 → down-only フォールバック（案 A）

Wave 3 — settings
  (3)  #496  Save 時 keyword マージ

Wave 4 — UX enhancement（v2.0.1 同梱）
  (4)  #495  gui-spec 改訂 → deferred apply（interval / slideshow auto scale）
```

**バージョン:** bug 修正 + #495 を **`v2.0.1`** にまとめる（patch リビジョン）。まだ issue が出続ける間は版番を先走らせないが、**出すなら v2.0.1 で #492–#497 を一式**。

---

## Wave 1

### #492 — Tray ダイアログのみ

| 項目 | 内容 |
| --- | --- |
| 変更 | `qt_tray_adapter.py`: Settings / BaseColor / About の `present_main_window=True` → **`False`** |
| spec | [harite-gui-spec.md §7](../specs/gui/harite-gui-spec.md) — tray からの dialog 導線は **main window を raise しない** を 1 段落 |
| テスト | `tests/gui/test_qt_tray_adapter.py` — `_StubWindow.show` / `raise_` が **呼ばれない** assertion |
| 完了定義 | Xfce 実機: tray → Settings / Color で main window が出ない |

**見積:** 小（単独 PR 可）。

### #494 — tick 失敗時の owner→backend 同期 + エラー表示

| 項目 | 内容 |
| --- | --- |
| 変更 | `qt_backend._on_slideshow_timer_event`: `result is False` のとき `owner` を取得し **`_sync_slideshow_state_with_feedback_from_owner(owner)`** |
| 副効果 | `sync_feedback_from_owner` 経由で **footer 赤文字**（`last_error`）が出る — #497 調査の前提 |
| テスト | timer callback が `False` を返す stub owner で `backend._slideshow_running is False`、`_set_feedback` に error が渡る |
| 完了定義 | #493 / #497 再現後: Tray・タブ・footer が **stopped + Error: …** で一致 |

**見積:** 小。#492 と **同一 PR（Wave 1）** でよい。

```python
# 当たり（qt_backend._on_slideshow_timer_event）
if result is False:
    self._stop_slideshow_timer()
    owner = self._get_handler_owner("on_slideshow_tick")
    if owner is not None:
        self._sync_slideshow_state_with_feedback_from_owner(owner)
```

**PR 案:** `fix/tray-and-tick-fail-sync` — #492 + #494

---

## Wave 2

### #493 — JMA 更新なし tick

| 項目 | 内容 |
| --- | --- |
| 問題 | `jma_slideshow_tick` は fetch を skip するが **`_apply_slideshow_selection` は毎 tick 実行** → 不要 optimize + display 瞬間失敗で停止 |
| 変更 1 | **tick short-circuit:** L/R とも remote が「更新なし」（JMA: `filename_unchanged`）なら optimize/apply を **省略**し `SLIDESHOW_TICK ok=true`, `skip_reason=no_remote_update` |
| 変更 2 | `_is_transient_slideshow_cycle_error` に `DUAL_INPUT_REQUIRES_TWO_DISPLAYS` を追加 → **pause**（hard stop 回避）。#494 後は pause 時も UI 一致が必要 |
| 変更 3 | OP_LOG: `on_slideshow_start` / `on_slideshow_stop` に `SLIDESHOW_START` / `SLIDESHOW_STOP`；tick エラー時 `detected_display_count` + 名前一覧 |
| spec | [harite-source-spec.md §15.1.3](../specs/source/harite-source-spec.md) — 更新なし tick は apply を skip；[slideshow-spec](../specs/slideshow/harite-slideshow-spec.md) §6 — 同上 |
| テスト | mock JMA tick が `filename_unchanged` ×2 → optimize 未呼び出し / `ok=true`；`detect_displays` 1 台 mock → **pause** で `slideshow_running` 維持 |

**設計判断（確定 2026-06-13）:**

- **skip 優先:** 更新なしは apply しない。
- **display 失敗（モニター検知）:** **pause** — `DUAL_INPUT_REQUIRES_TWO_DISPLAYS` 等、`detect_displays()` が 2 未満になった瞬間失敗は hard stop せず再検出待ち。

### #497 — 縦長 NDL + auto display scale

| 項目 | 内容 |
| --- | --- |
| 問題 | `_resolve_intentional_image_dimensions` が factor>1 で高さ超過時に `ValueError` → hard stop（OP_LOG: `878x3048` vs `2048x1280`） |
| **確定修正** | intentional upscale 後に fit しない場合、**同一 tick 内で `_resolve_native_dimensions`（down-only）へフォールバック**。OP_LOG に `display_scale_fallback: down_only` |
| spec | MAT-14b 節 — 「拡大後に収まらない場合は down-only で fit」追記（[maturation MAT-14b](../online-issues/maturation-20260609-qt-common.md)） |
| テスト | 縦長小画像 fixture + auto scale on + 2048×1280 slot → optimize 成功、エラーなし |

**PR 案:** `fix/slideshow-tick-skip-and-fit` — #493 + #497（同一ファイル `main_window.py` / `core.py` 触るため）

---

## Wave 3

### #496 — Settings Save で keyword 保持

| 項目 | 内容 |
| --- | --- |
| 問題 | Manage は `patch_settings_value`、Settings Save は `save_settings(export_settings())` で **keyword キーが落ちる** |
| 推奨修正 | `on_save_settings_file` で既存 JSON を読み、**preserve keys**（最低 `codh_keyword`, `ndl_keyword`）を payload にマージしてから `save_settings` |
| 代替 | `AppSettings` に keyword フィールドを追加（round-trip 重い） |
| spec | [harite-source-spec.md §15](../specs/source/harite-source-spec.md) — Settings Save でも keyword を保持 |
| テスト | tmp settings に keyword あり → Manage 相当 patch → `export_settings` 相当 save → keyword 残存 |

**PR 案:** `fix/settings-save-preserve-keywords` — #496 単独

---

## Wave 4 — #495（v2.0.1 同梱）

### #495 — running 中の変更を次 tick に

**位置づけ:** 現仕様の延長（大規模機能ではない）。**v2.0.1 に #492–#497 と同梱** — PR は Wave 2 完了後でもよいが、リリース単位では同一 patch。

| 項目 | 内容 |
| --- | --- |
| 現状 | interval: 次 **Start** まで；auto scale: **即時** `_reapply_slideshow_if_running` |
| 方針 | **spec 先行** — gui-spec §6.2 に「running 中の変更 → 次 tick 適用」表 |
| 実装案 | `_slideshow_pending_interval` / pending auto scale を tick 入口で消化；interval は次 tick **前** に timer 再設定 |
| 注意 | #493 skip と両立 — pending 消化は **skip 判定の後** または skip 時も interval だけ更新するか要整理 |
| テスト | running 中 interval 変更 → 現 tick 完了まで旧 interval、次 tick から新 interval |

**PR 案:** `docs/slideshow-deferred-apply` → `feature/slideshow-deferred-tick-apply`（#495 単独 PR、**v2.0.1 リリースに同梱**）

---

## PR / ブランチ案（まとめ）

| PR | branch 例 | Issues | 触る主なファイル |
| --- | --- | --- | --- |
| 1 | `fix/post-release-tray-tick-sync` | #492, #494 | `qt_tray_adapter.py`, `qt_backend.py`, `test_qt_tray_adapter.py`, gui-spec §7 |
| 2 | `fix/slideshow-tick-continuity` | #493, #497 | `main_window.py`, `sources_remote_jma.py`, `core.py`, `slideshow_op_log.py`, source/slideshow spec |
| 3 | `fix/settings-keyword-preserve` | #496 | `main_window.py` or `settings_file.py`, `test_*settings*` |
| 4a | `docs/slideshow-deferred-apply` | #495 | gui-spec §6 のみ |
| 4b | `feature/slideshow-deferred-apply` | #495 | `main_window.py`, `qt_backend.py`, gui-runtime |

---

## spec 改訂チェックリスト（.cursorrules 手順 2）

| タイミング | 正本 | 内容 |
| --- | --- | --- |
| PR 1 | gui-spec §7 | tray dialog は main window 非表示 |
| PR 2 | source-spec §15.1.3, slideshow-spec §6 | JMA 更新なし tick skip；OP_LOG ステップ |
| PR 2 | maturation 参照 or core 節 | MAT-14b fit フォールバック |
| PR 3 | source-spec §15 | Settings Save と keyword 共存 |
| PR 4a | gui-spec §6.2 | running 中 interval / auto scale → 次 tick |

---

## 検証計画（オーナー実機）

| 順 | シナリオ | 期待 | Issue |
| --- | --- | --- | --- |
| 1 | tray → Settings | main window 出ない | #492 |
| 2 | 意図的 tick 失敗（mock でも可） | footer 赤文字 + Tray/Main 一致 stopped | #494 |
| 3 | JMA デュアル・更新なし 10分 | skip、停止しない | #493 |
| 4 | NDL illust + CODH keyword、L auto scale on、縦長が来るまで | 停止しない（または fallback ログ） | #497 |
| 5 | Manage keyword → Settings Save → 再起動 | keyword 維持 | #496 |
| 6 | running 中 interval 変更 | 次 tick から新 interval | #495 |

**OP_LOG:** Wave 2 以降は `HARITE_SLIDESHOW_OP_LOG` 付きで viper3 再採取（MAT-08 継続）。

---

## オーナー判断（確定 2026-06-13）

| # | 論点 | 決定 |
| --- | --- | --- |
| 版番 | patch のタイミング | 出すなら **`v2.0.1`** で **#492–#497 一式**（#495 含む） |
| 1 | #493 display 失敗 | **モニター検知**由来なら **pause** |
| 2 | #497 fit 不能 | **down-only フォールバック**で実施 |
| 3 | #495 | **v2.0.1 同梱**（現仕様の延長） |

---

## 本ブランチの完了定義（planning フェーズ）

- [x] `docs/online-issues/issue-492.md` … `issue-497.md` 作成
- [x] `docs/online-issues/README.md` 索引
- [x] 本 planning メモ
- [ ] git commit + push（docs ブランチ）— オーナー確認後
- [ ] Wave 1 実装ブランチ `fix/post-release-tray-tick-sync` を `main` から分岐

---

## 関連リンク

- Issue 索引: [online-issues/README.md](../online-issues/README.md)
- OP_LOG 観測: `out/slideshow-op-v2-jma-001.jsonl`（#493）、`out/slideshow-op-v2-002.jsonl`（#497）
- 先行修正先例: MAT-02b #462–#465（NDL/CODH tick 安定化）

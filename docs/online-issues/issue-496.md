# Issue #496

## 管理情報

- URL: <https://github.com/oggy8021/Harite/issues/496>
- opened: 2026-06-13
- title: `CODHキーワード Preset について、キーワードが設定ファイルに保存されない`
- labels: `bug`
- 報告: v2.0.0 リリース直後（オーナー実機）
- 対象: **NDL図版（キーワード）** / **CODHキーワード** — 同一経路

## 事象

1. **Manage Presets** でキーワードを編集 → `harite-settings.json` へ書き込まれる（確認済み）。
2. その後 **Settings ダイアログ** を開き **Save Settings** を実行すると、キーワードが消える。
3. 再起動のたびに既定値に戻る:
   - CODH: **`桜`**（`CODH_KEYWORD_DEFAULT`）
   - NDL: **`妖怪`**（`NDL_KEYWORD_DEFAULT`）

## 期待

- Manage で保存した `codh_keyword` / `ndl_keyword` が、Settings ダイアログの Save 後も **維持** される。
- Settings Save は optimize / apply / slideshow 各キーを保存しつつ、**既存の keyword キーを落とさない**。

## 分類

- `bug` — settings 保存の **フル上書き** が keyword キーを消す（データロス）

## 関連

- 正本:
  - [harite-source-spec.md §15](../specs/source/harite-source-spec.md) — `codh_keyword` / `ndl_keyword` は `harite-settings.json` トップレベル
  - [harite-gui-spec.md §Manage Presets](../specs/gui/harite-gui-spec.md) — keyword フィールドは Manage 経由で settings へ反映
- [MAT-05](../online-issues/maturation-20260609-qt-common.md) — CODH キーワード Close 確定（別角度だが同一 `codh_keyword` キー）
- 実装:
  - `src/harite/gui/views/main_window.py` — `on_save_settings_file`, `export_settings`, `_build_settings_dialog_settings`
  - `src/harite/settings.py` — `AppSettings.to_settings_dict`（**keyword 非含有**）
  - `src/harite/settings_file.py` — `save_settings`（全上書き）vs `patch_settings_value`（マージ）
  - `src/harite/gui/adapters_qt/qt_source_registry_dialog.py` — `_flush_codh_keyword_to_settings`, `_flush_ndl_keyword_to_settings`
  - `src/harite/sources_remote.py` — `CODH_KEYWORD_SETTINGS_KEY`, `NDL_KEYWORD_SETTINGS_KEY`, 既定値
- 他 Issue: [#495](issue-495.md)（slideshow UX — 別件）

## 取り込み方針

- 現時点の判断: **近端着手**（単純なマージ保存で直る見込み）
- スコープ: `codh_keyword` / `ndl_keyword` の保持。他の patch-only キー（将来追加）も同様に検討。
- 修正候補（いずれか）:
  1. `on_save_settings_file` で既存 JSON を読み、payload と **マージ** してから `save_settings`
  2. `AppSettings` / `export_settings` に keyword フィールドを追加し round-trip
  3. Settings Save を `patch_settings_value` 系の複数キー更新に変更
- 次: 再現テスト（Manage 保存 → Settings Save → JSON に keyword 残存）→ impl

## 調査メモ

### 原因（コード上ほぼ確定）

**2 つの保存経路が衝突している。**

| 経路 | API | 挙動 |
| --- | --- | --- |
| **Manage Presets** | `patch_settings_value` | 既存 JSON を読み、`codh_keyword` / `ndl_keyword` **1 キーだけ更新** |
| **Settings → Save** | `save_settings` | `export_settings()` の dict で **ファイル全体を上書き** |

`AppSettings.to_settings_dict()` は optimize / apply / slideshow のみで、**keyword キーを含まない**:

```206:211:src/harite/settings.py
    def to_settings_dict(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        merged.update(self.optimize.to_settings_dict())
        merged.update(self.apply.to_settings_dict())
        merged.update(self.slideshow.to_settings_dict())
        return merged
```

```1078:1086:src/harite/gui/views/main_window.py
    def on_save_settings_file(...):
        payload = ... self._build_settings_dialog_config()  # → export_settings()
        save_settings(target_path, payload)  # 全上書き
```

### 既定値に戻る理由

キーが JSON から消えると `codh_keyword_from_settings` / `ndl_keyword_from_settings` が **default** を返す:

```292:298:src/harite/sources_remote.py
def codh_keyword_from_settings(settings: dict[str, Any]) -> str:
    raw = settings.get(CODH_KEYWORD_SETTINGS_KEY)
    if raw is None:
        return CODH_KEYWORD_DEFAULT  # "桜"
```

NDL も同型（`NDL_KEYWORD_DEFAULT = "妖怪"`）。

### 再現手順（オーナー報告）

1. Manage で CODH/NDL keyword を編集・保存（`harite-settings.json` に `codh_keyword` / `ndl_keyword` あり）
2. Settings ダイアログ → Save Settings
3. JSON から keyword キーが消える → 次回起動で 桜 / 妖怪

### テストギャップ

- Manage の keyword flush はあるが、**Settings Save 後の keyword 残存** は未カバーと思われる。

### memo（オーナー）

- Manage では編集・settings.json 書き込みを確認したが、Settings Save で消える。
- NDL図版(キーワード)・CODHキーワードとも同じ。
- 起動ごとに桜と妖怪に戻る。

## resolution

（未解決）

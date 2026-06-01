# C-02 Slideshow source registry — 評価メモ

- mock: [20260601-c02-slideshow-source-registry-slice.html](20260601-c02-slideshow-source-registry-slice.html)
- 第4波（C-02）段4: GUI 最小
- 段階: design slice **マージ済**（#376）→ gui-spec **起票中** → tests → impl

## オーナー合意（2026-06-01）

- design slice #376 **マージ済**
- チェックリスト #4（Saved / Srcdir 併存）: **memo 提案どおり採用** — `— none —` は id のみクリア・path 維持；Srcdir ブラウズは combo を `— none —` に（gui-spec §4.2）

## 目的

Slideshow タブから **登録済み source / profile** を選び、`slideshow_srcdir_l/r` へ path を展開する。
Main タブ・CLI・専用 Sources タブは **対象外**（[source-spec](../../specs/source/harite-source-spec.md)）。

## レイアウト変更（案）

現行 Slideshow タブは `srcdir row`（3 列）→ spacer → controls → detail。
**side panel が combo 1 行分背丈を増やす**ため、タブ全体の縦構成を次のとおり拡張する。

| 順序 | ブロック | 新/既 |
| --- | --- | --- |
| 1 | vertical stretch | 既存 |
| 2 | **Profile row**（中央、combo 1 本） | **新規** |
| 3 | srcdir 3 列 grid（side panel 内に Saved combo 追加） | 拡張 |
| 4 | **Manage sources and profiles…**（中央リンク） | **新規** |
| 5 | spacer ~54px | 既存 |
| 6 | controls shell（Mode / Interval / Start/Stop） | 既存 |
| 7 | spacer ~54px | 既存 |
| 8 | detail shell（current / output） | 既存 |
| 9 | vertical stretch | 既存 |

### side panel 内（L / R 共通）

上から:

1. **Saved source** — `QComboBox`（`— none —` + catalog 名一覧）
2. **Srcdir-L/R** — 既存フォルダブラウズ
3. **path label** — 既存（basename 省略）
4. **Clear-L/R** — 既存

center 列: Swap L/R のみ（P-01 維持）。

## Widget 名（spec 草案）

| Widget | 用途 |
| --- | --- |
| `combo_slideshow_profile` | profile 一括適用 |
| `combo_slideshow_source_l` / `_r` | 側別 saved source |
| `btn_manage_source_registry` | Manage dialog を開く |
| `source_registry_dialog` | Sources + Profiles CRUD |

## 振る舞い（spec 化予定）

### Saved source combo（L / R）

- 選択 → `resolve_source` → owner `slideshow_srcdir_*` + label 更新 + 任意 `slideshow_source_id_*`
- `— none —` → source id tracking をクリア（path は Clear まで維持、または spec で明記）
- **提案:** `— none —` は id のみクリア。path は Srcdir ブラウズ / profile 適用で上書きされるまで表示維持

### Profile combo

- 選択 → `resolve_profile_members` → L/R 両 combo + path + owner を一括更新 + 任意 `slideshow_profile_id`
- profile 周回なし。ordered list なし

### Srcdir-L/R（既存）

- ブラウズ確定 → path 直書き（従来）。当該 side の saved combo を `— none —` に（registry 外 path）

### Swap / Clear（P-01/P-02 拡張）

- Swap: path **と** `slideshow_source_id_l/r`（および profile id が L/R 対応なら profile tracking も）を swap
- Clear: 当該 side の path + source id を clear

### Manage dialog

- Sources: list / add（name + browse dir）/ delete（参照中は拒否）
- Profiles: list / L・R slot combo / add / delete
- Close 後: タブ上 combo を catalog から再構築

### Start ガード

- 両 srcdir 非空 — **変更なし**（gui-spec §6 維持）

## スコープ外（C-02 GUI）

- Main input registry
- CLI `harite source`
- profile / source の ordered list・周回
- settings dialog への registry editor 統合

## 評価チェックリスト（オーナー）

- [x] Profile 行が srcdir grid の上で自然か（#376 マージ）
- [x] side panel に Saved combo + Srcdir + path + Clear が収まるか
- [x] Manage dialog 1 枚で sources + profiles が足りるか（専用タブ不要）
- [x] Srcdir ブラウズと registry 選択の併存 — **§4.2 併存表で spec 化**

## 合意後の次ステップ

1. ~~design PR マージ~~（#376 済）
2. ~~`harite-gui-spec.md` §4.2 / §6.3~~ — PR 起票中
3. tests → Qt impl（GTK parity は spec に明記）

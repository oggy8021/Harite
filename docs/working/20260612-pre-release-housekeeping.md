# v2.0.0 前 — リリース準備 housekeeping

**作成:** 2026-06-12  
**親 planning:** [20260611-1200-cli-v2-roadmap.md](20260611-1200-cli-v2-roadmap.md)（MAT-20 / MAT-24 の間）  
**方針:** 開発チケット番号（MAT-xx）は **正本（`docs/specs/`）に残さない**。変更経緯は本メモと `working/` / CHANGELOG に置く。

---

## 確定順序（オーナー 2026-06-12）

```text
(1) requirements 点検・ドキュメント整備  ← **完了**（GTK 停止後の XFCE 環境再構成）
(2) トレイ 2 アイコン + Windows タスクバー配色検出
(3) MAT-20（embed-info 整理・重畳・文字色自動）
(4) 回帰テスト（オーナー実施: CLI → GUI → Windows → XFCE）
(5) 正本から MAT-xx 除去（回帰後・bump 直前）
(6) MAT-24（CHANGELOG・版 bump・パッケージング・ビルド・リリース）
```

---

## (1) requirements / XFCE 環境再現 — **完了**（2026-06-12）

**背景:** Q-01（GTK 廃止）後、XFCE 実機の venv / apt 構成が未整備だった。IME 自体は fcitx 改修時に確認済み — 今回は **環境再構成の再現手順** を正本化した。

**ブランチ:** `feature/pre-release-req-docs-20260612`（PR 待ち）

### 目的

- `requirements-linux-qt.txt` が「全部コメント」に見えず、**XFCE 上で distro PyQt6 + fcitx 前提の `harite-qt` 環境を再現できる手順書**として読めること。
- pip PyQt6 と distro fcitx プラグインの非互換を踏まえ、**誤インストールを防ぐ**。

### 正本ファイル

| ファイル | 役割 |
| --- | --- |
| [requirements.txt](../../requirements.txt) | pip 入口（`-e .`）。Linux は `requirements-linux-qt.txt` へ誘導 |
| [requirements-linux-qt.txt](../../requirements-linux-qt.txt) | XFCE / Mint / Ubuntu: apt + venv 手順（**コメントのみ＝意図的**） |
| [requirements-dev.txt](../../requirements-dev.txt) | pytest 等の開発依存 |
| [docs/dev/dev-environment.md](../dev/dev-environment.md) | 開発者向け統合手順 |
| [scripts/verify_linux_qt_env.py](../../scripts/verify_linux_qt_env.py) | 構築後の一発検証 |

### 完了の目安

- [x] XFCE 実機で venv 再構成 → `verify_linux_qt_env.py` exit 0（distro PyQt6 / SVG / fcitx すべて OK）
- [x] fcitx IME — 改修時に確認済み（今回のスコープ外だが再構成後も env 整合）
- [x] SVG アイコン — `verify_linux_qt_env` の packaged SVG probe で OK

### 技術前提（コード正本）

- `prepare_qt_input_method_env()` — GTK/XMODIFIERS から `QT_IM_MODULE` 補完（[gui-spec §Linux IME](../specs/gui/harite-gui-spec.md)）
- **pip PyQt6 は fcitx Qt6 プラグインと ABI 非互換** → distro `python3-pyqt6` + `--system-site-packages` venv
- `python3-pyqt6.qtsvg` — パッケージ内 SVG アイコン用

---

## (2) システムトレイ — 2 アイコン + 配色検出 — **未着手**

### 目的

Windows ライトテーマのタスクバーで現行 `#F5F7FA` ストロークアイコンが埋もれないこと。

### 方針（オーナー OK）

| 項目 | 内容 |
| --- | --- |
| アセット | 明背景用（暗ストローク）/ 暗背景用（現行明ストローク）の 2 種 |
| Windows | レジストリ `SystemUsesLightTheme` でタスクバー明暗を判定 |
| フォールバック | `QStyleHints.colorScheme()`、不明時は明背景用（暗アイコン） |
| XFCE | 統一 API 弱い → フォールバック優先 |
| 共有 | embed 文字色（MAT-20 C2）と輝度ユーティリティ共有を検討 |

### 触るコード（予定）

- `src/harite/gui/adapters_qt/qt_tray_adapter.py` — `_make_icon`
- `src/harite/gui/resources/icons/product/` — 新 SVG
- 新規: `resolve_tray_icon_variant()` 等（Windows registry + Qt hints）

---

## (3) MAT-20 — embed-info — **未着手**

roadmap §MAT-20 参照。重畳ガード（一部 spec 済）、`params`→`settings`、輝度ベース文字色。

---

## (4) 回帰テスト — **オーナー実施予定**

MAT-24 チェックリスト（roadmap §6）と連動。幾何変更後の Slideshow CLI 実機再確認含む。

---

## (5) 正本 MAT-xx 除去 — **回帰後・bump 直前**

### 対象

`docs/specs/` 5 ファイル、約 50 箇所の `MAT-xx` 参照。

### 方針

- **残す:** 挙動・制約・廃止事項（製品仕様として読める文）
- **除く:** チケット番号・「MAT-xx で〜」の開発メモ調文言
- **移す:** 変更理由・時系列 → `working/` / CHANGELOG

---

## (6) MAT-24 — **未着手**

CHANGELOG、`pyproject.toml` bump、パッケージング、ビルド、リリース。

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-12 | 初版。順序確定、(1) requirements 着手 |
| 2026-06-12 | (1) 完了。XFCE 実機で verify 通過（GTK 停止後の環境再構成） |

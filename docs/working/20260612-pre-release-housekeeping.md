# v2.0.0 前 — リリース準備 housekeeping

**作成:** 2026-06-12  
**親 planning:** [finished/20260611-1200-cli-v2-roadmap.md](finished/20260611-1200-cli-v2-roadmap.md)  
**方針:** 開発チケット番号（MAT-xx）は **正本（`docs/specs/`）に残さない**。変更経緯は本メモと `working/` / CHANGELOG に置く。

---

## 確定順序（オーナー 2026-06-12）

```text
(1) requirements 点検・ドキュメント整備  ← **完了**（#482）
(2) トレイ 2 アイコン + Windows タスクバー配色検出  ← **完了**（#483）
(3) embed-info 整理・重畳・文字色自動  ← **完了**（#484, #485）
(4) 回帰テスト（オーナー実施: CLI → GUI → Windows → XFCE）  ← **実施中・大きな齟齬なし**
(5) 正本から MAT-xx 除去  ← **完了**（docs/pre-release-spec-cleanup ブランチ）
(6) 版 bump・パッケージング・ビルド・リリース  ← **次**
```

---

## (1) requirements / XFCE 環境再現 — **完了**（#482）

[requirements-linux-qt.txt](../../requirements-linux-qt.txt)、[dev-environment.md](../dev/dev-environment.md)、`scripts/verify_linux_qt_env.py`、`scripts/rinji.py`（tray 診断）。

---

## (2) システムトレイ — **完了**（#483, #488）

| 項目 | 内容 |
| --- | --- |
| Windows | `harite_light_bg.svg` 系 + `SystemUsesLightTheme` 検出（#483） |
| XFCE | ラスター pixmap + Linux 既定は明ストローク `harite.svg`（#488） |
| 診断 | `scripts/rinji.py`、パネル **ステータストレイプラグイン** |

手動確認: Windows ライト/ダーク OK、XFCE 白アイコン OK（2026-06-13）。

---

## (3) embed-info — **完了**（#484, #485）

`params`→`settings`、重畳ガード、文字色自動、`canvas=` / `L=` / `R=` 行、GUI preview refresh。

---

## (4) 回帰テスト — **オーナー実施中**

v2 幾何・apply・canvas-scale ポストダウンスケール（#487）確認済み。Slideshow / GUI 薄い層は継続。

---

## (5) 正本 MAT-xx 除去 — **完了**（2026-06-13）

`docs/specs/` 5 ファイルから MAT-xx 参照を除去。挙動・制約・廃止事項は維持。

---

## (6) 版 bump・リリース — **次**

CHANGELOG、`pyproject.toml` bump、パッケージング希望の反映、リリースブランチ。

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-12 | 初版。順序確定 |
| 2026-06-13 | #484–#488 反映。正本 MAT 除去完了。XFCE tray 確認 OK |

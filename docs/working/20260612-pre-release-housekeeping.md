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
(5) 正本から MAT-xx 除去  ← **完了**（#489）
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

CHANGELOG、`pyproject.toml` bump（`2.0.0`）、リリースブランチ、下記パッケージ方針の実装。

### パッケージ方針（オーナー 2026-06-13 確定）

| プラットフォーム | 配布形態 | 備考 |
| --- | --- | --- |
| **Windows** | **PyInstaller `onedir`** | 母体は onefile ではなく onedir を推奨（起動・デバッグ・同梱のバランス）。**Python ロゴ（`python.ico`）の露出は避ける** |
| **Linux** | **sdist + wheel**（ビルド成果物） | バイナリ化・AppImage は **訴求があれば検討**。**PyPI 公開（v2.0.0 で復活するか）は未決** — 母体 `wallpaperoptimizer` は PyPI **登録削除済み**で現状残っていない |

### Windows アイコン

- ウィンドウ左上・タスクバーグループ等の product identity に **`harite_app.svg`** を用いる（GUI 実装は `setWindowIcon` で同 SVG を既に参照）。
- PyInstaller の EXE/ショートカット用には、ビルド時に **SVG → `.ico` 変換** が必要になる想定（`--icon` は `.ico` 前提）。
- トレイは slideshow 用 product icon（`harite.svg` / `harite_light_bg.svg` 等）— #483 / #488 済み。Windows バイナリ同梱時も package resources を PyInstaller datas で含める。

### Linux 配布

- 開発・実機: `pip install -e .` または wheel からのローカル install + [requirements-linux-qt.txt](../../requirements-linux-qt.txt)（distro `python3-pyqt6`、`--system-site-packages` venv）。
- リリース時: `python -m build` で **sdist/wheel を生成**（CI `build-check` 再確認）。配布先は **GitHub Release 添付・git clone 等**を想定し、**PyPI upload は v2.0.0 時点ではオプション**（要判断）。

### リリースブランチでやること（チェックリスト）

- [x] `CHANGELOG`（CLI 破壊的変更を明示）
- [x] `pyproject.toml` version `2.0.0`
- [x] PyInstaller spec / ビルド手順（Windows onedir、`harite` + `harite-qt` の EXE 構成を確定）— `packaging/windows/`, `scripts/build_windows_pyinstaller.py`
- [x] `python -m build` → sdist/wheel（Linux 成果物；PyPI 公開するかは別判断）— `harite-2.0.0-py3-none-any.whl`, `harite-2.0.0.tar.gz` 生成確認済み（2026-06-13）
- [ ] GitHub Release アーティファクト（Windows フォルダ zip 等）

---

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-06-12 | 初版。順序確定 |
| 2026-06-13 | #484–#488 反映。正本 MAT 除去完了（#489）。XFCE tray 確認 OK |
| 2026-06-13 | §6 パッケージ方針追記（Windows onedir / Linux sdist+wheel） |
| 2026-06-13 | §6 チェックリスト: CHANGELOG / version bump / PyInstaller 手順を実装 |

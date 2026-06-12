# 開発環境（開発者向けメモ）

作成日: 2026-03-12

このファイルは、本プロジェクトの開発・テストを行う環境と手順の簡易メモです。

## 開発環境（実機・ターゲット）

- OS: Linux Mint 22.3 (zena) + XFCE — 実機 / テスト用
- アクセス: VS Code の Microsoft Remote - SSH 経由でリモート開発

## ローカル開発マシン

- 開発者は Windows 上の VS Code から Remote-SSH で接続して作業する想定

## 必須ランタイム

- Python 3.12+

## 推奨パッケージ（Ubuntu/Mint 系）

- git
- python3-venv
- python3-pip
- build-essential
- libjpeg-dev
- libpng-dev
- xvfb（GUI/ヘッドレス検証用）

### Qt 版 GUI（`harite-qt`）+ fcitx IME — XFCE 再現手順

pip の `PyQt6` は distro fcitx プラグインと非互換のため、**Linux では apt の PyQt6 を使う**。正本手順は [requirements-linux-qt.txt](../../requirements-linux-qt.txt)（コメントのみの意図的設計）。

**なぜ別経路か:** 日本語入力のため fcitx の Qt6 プラグインが必要だが、pip 同梱 Qt6 では `Qt_6_PRIVATE_API` 不一致でロードできない。Harite は distro `python3-pyqt6` + `--system-site-packages` venv を前提とする（[gui-spec §Linux IME](../specs/gui/harite-gui-spec.md)）。

#### 一発セットアップ（Mint 22 / Ubuntu 24.04 系の例）

```bash
# 0) OS パッケージ（初回のみ）
sudo apt update
sudo apt install -y \
  git python3 python3-venv python3-pip \
  python3-pyqt6 \
  python3-pyqt6.qtsvg \
  fcitx5 fcitx5-frontend-qt6

# 1) venv（必ず --system-site-packages）
cd Harite
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt

# 2) 検証
python scripts/verify_linux_qt_env.py

# 3) 起動
harite-qt
```

**してはいけないこと:** `pip install PyQt6`、`pip install 'harite[gui-qt]'`（Linux では pip PyQt6 を引く）。

**XFCE セッション:** Input Method で fcitx5 を有効化。`GTK_IM_MODULE=fcitx` / `XMODIFIERS=@im=fcitx` が入っていれば、起動時 `prepare_qt_input_method_env()` が `QT_IM_MODULE` を補完する。

**IME 動作確認:** Slideshow タブの `keyword(CODH)` 欄で日本語入力が切り替わること。

必須 apt パッケージ（再掲）:

- `python3-pyqt6`
- `python3-pyqt6.qtsvg`（SVG アイコン表示）
- `fcitx5-frontend-qt6`（Qt6 向け fcitx IM フロントエンド）

### Preset slideshow 操作ログ（MAT-08 / CODH・NDL 観測）

```bash
export HARITE_SLIDESHOW_OP_LOG=~/.cache/harite/slideshow-op.jsonl
harite-qt
```

Slideshow Start / Manage Refresh / CODH tick 時に JSONL が追記される（未設定時は出力なし）。詳細: [source-spec §12.4.3](../specs/source/harite-source-spec.md)。

## 初期セットアップ手順（接続先で実行）

**GUI + 日本語入力（XFCE）を使う場合**は上記「Qt 版 GUI + fcitx IME」節を優先する。以下は **CLI / ヘッドレス pytest 中心**の最小手順。

```
sudo apt update
sudo apt install -y git python3-venv python3-pip build-essential libjpeg-dev libpng-dev xvfb

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
# 開発依存: pip install -r requirements-dev.txt

python -m pytest -q
```

## GUI / 表示テスト（ヘッドレス環境例）

```
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
python -m pytest tests/gui_tests.py
```

## Remote-SSH の注意点

- 接続先に Python 3.12 とビルド依存が揃っていることを確認してください。
- VS Code で仮想環境（`.venv`）を選択してから開発してください。

## 備考

- 実際のパッケージ構成や CI 設定は実装に合わせて更新します。

## GitHub CLI (`gh`)

- `gh` (GitHub CLI) を導入済みの場合、リポジトリ操作や PR 作成をコマンドラインで行えます。
- 初回ログイン例:

```
gh auth login --web
```

- ブランチ作成〜PR作成の一例:

```
git checkout -b feature/cli-optimize
git add .
git commit -m "feat: add CLI skeleton"
git push -u origin feature/cli-optimize
gh pr create --fill --base main --head feature/cli-optimize

[注記: コマンド例の `main` 表記は小文字で統一しています。]
```

- CI や自動化でトークンが必要な場合は、`GH_TOKEN` 環境変数を設定してください。

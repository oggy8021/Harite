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

## 初期セットアップ手順（接続先で実行）
```
sudo apt update
sudo apt install -y git python3-venv python3-pip build-essential libjpeg-dev libpng-dev xvfb

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
# 開発依存があれば別途インストール: pip install -r requirements-dev.txt

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

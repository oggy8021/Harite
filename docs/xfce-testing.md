# XFCE 実機検証手順

目的
--
このドキュメントは、XFCE 環境で `harite` の表示検出と壁紙適用（dry-run / 実適用）の動作確認を行うための手順をまとめます。実機での確認用チェックリストとコマンドを短く記載しています。

前提
--
- 対象マシンは XFCE デスクトップを稼働していること
- `xrandr` と `xfconf-query` を利用できると想定（無ければインストールする）
- Python 3.12 がインストール済みで、プロジェクトをクローン済みであること

必須/推奨ツール
--
- 必須: Python 3.12+, `pip`
- 推奨（環境によって使用）:
  - `xrandr`（ディスプレイ検出）
  - `xfconf-query`（XFCE のプロパティ操作）
  - `feh`（代替の壁紙設定コマンド）

インストール例（Debian/Ubuntu）
```bash
sudo apt update
sudo apt install x11-xserver-utils xfce4-settings xfconf4-tools feh
```

セットアップ（ローカル）
--
1. 仮想環境作成・依存インストール:
```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m pip install pytest
```

2. テスト実行（全体）:
```powershell
.venv\Scripts\python -m pytest -q
```

基本的な検証手順
--
1. 表示検出の確認:
```powershell
.venv\Scripts\python -c "from harite import workspace; print(workspace.detect_displays())"
```
期待: `xrandr` が使える場合は `[(幅, 高さ), ...]` のリストが返ります。`xrandr` が無い場合は `xfconf-query` のフォールバックが試行されます。

2. 最適化処理のサンプル実行（出力ファイル確認）:
```powershell
.venv\Scripts\harite optimize --input tests/data --resolution 3840x1080 --output out --two-screen --l-display 1920x1080 --r-display 1920x1080
```
出力例: `out/harite_wallopt_<id>.jpg`

3. プラグイン経由での dry-run（壁紙を変更しない）:
```powershell
.venv\Scripts\harite apply --plugin linux --file out/harite_wallopt_<id>.jpg
```
ログに、実行されるコマンド（例: `xfconf-query` / `gsettings` / `feh`）が表示されます。

4. XFCE の実際の適用（最終確認、自己責任）:
 - まずプロパティ一覧を確認:
```bash
xfconf-query -c xfce4-desktop -l
```
 - ドライラン結果を確認し、問題なければ `--do-it` を付けて実行:
```powershell
.venv\Scripts\harite apply --plugin linux --file out/harite_wallopt_<id>.jpg --do-it
```

トラブルシュート
--
- `detect_displays()` が空リストを返す場合:
  - `xrandr --query` を手動で実行して結果を確認する。
  - `xfconf-query -c xfce4-desktop -l -v` の出力に WxH パターンが含まれるか確認する。
- `harite apply` で期待するプロパティが見つからない場合:
  - `xfconf-query -c xfce4-desktop -l` の出力をコピーして共有してください。どのプロパティを設定すべきかを一緒に特定します。
- 実適用で設定されない/表示が変わらない場合:
  - XFCE のキャッシュやロックが影響する場合があります。`xfdesktop --replace` の再起動やログアウト／ログインを試してください。

ログ共有のお願い
--
検証で問題が発生した場合、以下情報を提供してください。
- `xfconf-query -c xfce4-desktop -l` の出力
- `harite apply` の dry-run 出力（コンソールログ）
- `detect_displays()` の出力

次の手順
--
1. 上記手順を実行のうえ結果を共有してください（成功なら次に PR マージの調整を進めます）。
2. 追加で自動化したい項目（例: `xfconf-query` のプロパティ自動検出、複数モニタの優先設定など）があれば教えてください。必要に応じて tests/ に追加のインテグレーションスクリプトを作成します。

作成: Harite チーム

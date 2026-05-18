# Harite

Harite — 壁紙最適化ツール（リファクタリング版）

## 概要

Harite は複数の入力画像からデスクトップ用壁紙画像を生成する小さなユーティリティです。複数ディスプレイ対応（左右分割）や余白、固定配置などのオプションを備えています。

## CLI 例

基本的なモザイク配置:

```bash
harite optimize --input ./imgs --resolution 3840x2160 --output ./out --quality 90
```

左右二画面構成:

```bash
harite optimize --input left.jpg,right.jpg --resolution 3840x1080 \
 --two-screen --l-display 1920x1080 --r-display 1920x1080 \
 --margins 10,10,5,5 --fixed --output ./out
```

JSON メタデータを保存:

```bash
harite optimize --input ./imgs --resolution 1920x1080 --output ./out --format json
```

日本語テキストを余白に埋め込む（自動フォント判定）:

```bash
harite optimize --input ./imgs --resolution 1920x1080 --output ./out \
  --embed-info free --embed-text "こんにちは Harite"
```

必要な場合のみフォントを明示指定:

```bash
harite optimize --input ./imgs --resolution 1920x1080 --output ./out \
  --embed-info free --embed-text "こんにちは Harite" \
  --embed-font "C:\\Windows\\Fonts\\meiryo.ttc"
```

`--embed-font` を指定しない場合は、システムの一般的なCJKフォント候補を順に試し、見つからなければ Pillow のデフォルトフォントへフォールバックします。

詳細オプションは `harite optimize --help` を参照してください。

## GUI 起動

current GUI の通常起動導線は `harite-gui` です。

```bash
harite-gui
```

モジュール経由でも起動できます。

```bash
python -m harite.gui.app
```

- 通常利用では追加 option は不要です。
- `--bind-ui-backend` / `--present-ui-window` とその `--no-*` 版は、開発時の切り分けや挙動確認用 override として残しています。
- README 上の正本導線は `harite-gui` とし、`python -m harite.gui.app` は補助導線として扱います。

### `apply` の安全な使い方

`apply` コマンドはデフォルトでドライランです。実際に壁紙を設定するには `--do-it` を指定してください。`--dry-run/--do-it` の切り替えで明示的に扱えます。

`--do-it` はプラットフォーム依存かつシステム設定を変更するため慎重に扱ってください。使用前の手順:

- 適切なプラグイン（`windows`, `macos`, `linux`）を選択しているか確認する。
- Linux/XFCE では `xfconf-query` のプロパティ名が環境により異なります。`xfconf-query -c xfce4-desktop -l` で確認してください。
- まずはドライランで動作を確認する。
- 内容に問題なければ `--do-it` を使って適用する。

### XFCE での手元 smoke 検証

インターバル適用の本実装を CLI 本体に入れる前に、外側ループで手元検証するための補助スクリプトを用意しています。

```bash
python scripts/xfce_smoke_runner.py --input ./wallpapers --iterations 20 --interval-min 10 --interval-max 60
```

- デフォルトは dry-run です（実際には壁紙を変更しません）。
- 実適用する場合のみ `--do-it` を付けてください。
- XFCE 実機適用時は `--input` に絶対パスを使ってください（相対パスだと黒背景化する環境があります）。
- ログは `xfce-smoke.log` に追記されます（`--log-file` で変更可能）。

## 外部依存（システムツール）

Harite 本体は Python パッケージですが、プラットフォーム固有の壁紙設定やディスプレイ検出には外部ツールを利用します。主要な外部依存は以下の通りです。

- 必須:
  - Python 3.12+（pyproject.toml に指定）
  - Python パッケージ: `typer`, `Pillow`（`pip install -e .` でインストール）

- 任意（環境に応じて利用されます）:
  - `xrandr` — Linux でディスプレイ情報を取得するため推奨（XFCE でも一般的に使用可能）。
  - `xfconf-query` — XFCE 環境で壁紙を設定する場合に使用します（`xfce4-desktop` チャンネル）。
  - `gsettings` — GNOME 系デスクトップで壁紙設定に利用されます。
  - `feh` — 軽量ビューアとして壁紙設定の代替手段として使用可能。

これらは必須ではありませんが、Linux 向けプラグインは PATH 上のこれらツールを探索して利用します。必要に応じて対象マシンへインストールしてください。Debian/Ubuntu 系の例:

```bash
sudo apt update
sudo apt install x11-xserver-utils xfce4-tools feh gsettings-desktop-schemas
```

Fedora 系の例:

```bash
sudo dnf install xorg-x11-server-utils xfce4-settings feh dconf
```

macOS では `osascript` がシステムに標準搭載されています。Windows は Win32 API を直接呼び出すため追加ツールは不要です。

## Contributing

- **ブランチ命名**: PR 用ブランチは `feature/`、`fix/`、`docs/`、`chore/` のいずれかの接頭辞を付け、続けて小文字英数字と `-._` を使った短い説明を付けてください。例: `feature/cli-compatibility-20260318`。
- **PR チェック**: `.github/workflows/pr-checks.yml` によりブランチ名と PR 本文が検証されます。PR 作成時は簡潔な概要と動作確認手順を PR 本文に記載してください。
- **実機確認メモ**: apply / GUI / 環境依存の変更で手元確認が必要な場合は `docs/manual-validation-gate.md` を参照してください。現時点では常に強い制約としては扱っていません。
- **ドキュメント**: CLI 互換性の仕様は `docs/specs/cli-compatibility.md` にまとめています（旧 WallpaperOptimizer とのマッピングと優先復元項目）。
- **ローカルでのテスト**: 開発用仮想環境を有効にして `pytest` を実行してください。テスト実行手順は `pyproject.toml` / `tox` 等の設定を参照してください。

## License

Harite 本体は MIT License です。配布物には [LICENSE](LICENSE) を含めます。

GUI で同梱している Lucide SVG icon については upstream notice を別途保持します。詳細は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。

ご協力ありがとうございます。小さな変更は PR で送ってください。

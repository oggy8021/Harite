# Harite

Harite — 壁紙最適化ツール（v2.0.2）

## 概要

Harite は、マルチディスプレイ環境で壁紙画像を生成・配置・適用するためのツールです。複数の入力画像から壁紙を作成し、画面ごとの配置、余白、スライドショー、壁紙適用を扱えます。

- **CLI:** `harite optimize` / `apply` / `slideshow`
- **GUI:** Qt 6（`harite-qt` / `harite-gui` — 同一入口）

## インストール

### Python パッケージ（Linux / 開発環境）

```bash
pip install harite-2.0.2-py3-none-any.whl   # または pip install -e ".[gui-qt]"
```

Linux で GUI を使う場合は [requirements-linux-qt.txt](requirements-linux-qt.txt) を参照（distro の `python3-pyqt6` 等）。

### Windows（バイナリ zip）

GitHub Release 添付の onedir フォルダを任意の場所に展開します（インストーラは付きません）。

| フォルダ | EXE | 用途 |
| --- | --- | --- |
| `harite/` | `harite.exe` | CLI |
| `harite-qt/` | `harite-qt.exe` | GUI |

詳細は [packaging/windows/README.md](packaging/windows/README.md)。

#### スタートメニュー・ショートカット

**自動では何も追加されません。** PyInstaller onedir はフォルダ展開のみで、スタートメニュー登録やデスクトップショートカット作成は行いません（`install-desktop-entry` は **Linux/XDG 専用**）。

GUI をスタートメニューから起動したい場合は、利用者が手動で行います。

- `harite-qt.exe` をスタートメニューへピン留めする
- または `harite-qt.exe` へのショートカット（`.lnk`）を作成し、スタートメニュー / デスクトップに置く

#### CLI と PATH（任意）

`harite.exe` をどのディレクトリからも `harite` コマンドで呼びたい場合は、展開先の `harite` フォルダを **ユーザー環境変数 `Path`** に追加します（必須ではありません。フルパス指定でも可）。

```powershell
# 例: C:\Apps\harite\harite.exe を Path に載せる場合
# 設定 → システム → 詳細情報 → 環境変数 → Path に C:\Apps\harite を追加
C:\Apps\harite\harite.exe optimize --help
```

`harite-qt` フォルダを Path に入れる必要は通常ありません（GUI は EXE を直接起動）。

## アップデート（既存利用者向け）

v2.0.1 から v2.0.2 へは **設定・CLI の移行作業は不要**です（`startup_slideshow` は既定 `false`）。パッケージ本体だけ差し替え、`harite-qt` / `harite.exe` を再起動してください。

**v2.0.2 の挙動変更:** main window の **×** は終了ではなく **tray へ格納**します。終了は tray **Quit** から。autostart で Slideshow 再開を使う場合は [§セッション自動起動](#セッション自動起動slideshow-再開) を参照してください。

**設定ファイルは上書きしません。** 既定の保存場所は次のとおりです（詳細は [core-spec §6.1](docs/specs/core/harite-core-spec.md)）。

| プラットフォーム | settings / sources |
| --- | --- |
| Linux / XFCE | `~/.config/harite/harite-settings.json`, `harite-sources.json` |
| Windows | `%APPDATA%\harite\harite-settings.json`, `harite-sources.json` |

### Linux / XFCE（wheel）

1. 実行中の `harite-qt` / `harite-gui` を終了する。
2. GitHub Release から `harite-2.0.2-py3-none-any.whl` を取得する。
3. 初回インストールと同じ経路で上書きする。

```bash
# pipx（推奨）
pipx install --force /abs/path/to/harite-2.0.2-py3-none-any.whl
# distro の python3-pyqt6 を使っている場合は初回と同様に:
# pipx install --system-site-packages --force /abs/path/to/harite-2.0.2-py3-none-any.whl

# pip --user
python3 -m pip install --user --upgrade /abs/path/to/harite-2.0.2-py3-none-any.whl
```

4. 版確認: `harite --version` → `2.0.2`
5. `harite install-desktop-entry` の再実行は **不要**（`.desktop` はそのまま利用可）。

### Windows（onedir zip）

1. 実行中の `harite-qt.exe` / `harite.exe` を終了する。
2. GitHub Release から CLI / GUI の onedir zip を取得し、**既存の展開先フォルダを上書き**する（`harite/` と `harite-qt/` をそれぞれ差し替え）。
3. 展開先パスを変えない限り、スタートメニューのショートカットや `Path` の変更は **不要**。
4. 版確認:

```powershell
C:\Apps\harite\harite.exe --version
```

## CLI 例（v2）

作業解像度はワークスペース検出で自動決定します。出力 JPEG の縮小のみ `--canvas-scale` で指定します。

```bash
harite optimize --input left.jpg,right.jpg \
  --margins 10,10,5,5 --output ./out
```

2 枚入力時はデュアル配置（検出失敗時はエラー）。ファイルサイズを抑えたい場合:

```bash
harite optimize --input left.jpg,right.jpg --canvas-scale 50 -o ./out
```

`apply` のプラグインや適用モードは settings JSON（`-c`）で指定します。v1 の `--resolution` / `--two-screen` / `--plugin` は **v2 では廃止** です。

詳細は `harite optimize --help` と [CHANGELOG.md](CHANGELOG.md) を参照してください。

## GUI 起動

```bash
harite-qt
# または
harite-gui
```

v2 の GUI は **Qt 6 のみ** です。GTK / `python3-gi` は不要です。

Linux / XFCE でアプリケーションメニューから起動したい場合:

```bash
harite install-desktop-entry
```

（`~/.local/share/applications/` に `.desktop` を生成。Windows では使えません。）

### セッション自動起動（Slideshow 再開）

Slideshow タブの **「Resume slideshow on session startup」** を ON にすると、OS のログイン自動起動から Harite を起動したとき、**前回終了時に Slideshow が動作中だった場合のみ** 自動で Start します（手動 Stop 後や、停止中に終了した場合は再開しません）。

起動コマンドには **`--startup-launch`**（または環境変数 `HARITE_STARTUP_LAUNCH=1`）が必要です。tray 常駐のみにする場合は **`--no-present-ui-window`** も併用します。

**Linux（XFCE 等）** — `~/.config/autostart/harite.desktop` の例:

```ini
[Desktop Entry]
Type=Application
Name=Harite
Exec=harite-qt --no-present-ui-window --startup-launch
X-GNOME-Autostart-enabled=true
```

**Windows** — スタートアップフォルダにショートカットを置き、リンク先を次のようにします:

```text
harite-qt.exe --no-present-ui-window --startup-launch
```

メインウィンドウの **×** は終了ではなく **トレイへ格納** します。完全終了は tray メニューの **Quit** から行ってください。

## 外部依存（システムツール）

Harite 本体は Python パッケージ（または Windows では同梱バイナリ）ですが、壁紙設定やディスプレイ検出で外部ツールを使うことがあります。

- **共通（Python 配布）:**
  - Python 3.12+（`pyproject.toml` に指定）
  - `typer`, `Pillow`（wheel / editable install で同梱）

- **GUI（Qt）:**
  - `PyQt6` または distro の `python3-pyqt6`（[requirements-linux-qt.txt](requirements-linux-qt.txt)）

- **XFCE 利用時:**
  - `xrandr` — ディスプレイ情報の取得
  - `xfconf-query` — 壁紙設定（xfce プラグイン使用時）

## 配布・リリース

- Linux: `harite-<version>-py3-none-any.whl` / `.tar.gz`（[docs/release-delivery.md](docs/release-delivery.md)）
- Windows: onedir zip（CLI + GUI）
- PyPI 公開は未決（GitHub Release 添付・git clone を想定）

## License

Harite 本体は MIT License です。配布物には [LICENSE](LICENSE) を含めます。

GUI で同梱している Lucide SVG icon については upstream notice を別途保持します。詳細は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。

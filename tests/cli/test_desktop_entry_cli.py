from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from harite import cli
from harite.linux_xdg_launcher import build_desktop_entry_text


def test_build_desktop_entry_text_includes_gui_module_exec() -> None:
    desktop_text = build_desktop_entry_text()

    assert "[Desktop Entry]" in desktop_text
    assert "Type=Application" in desktop_text
    assert "Name=Harite" in desktop_text
    assert "-m harite.gui.app" in desktop_text
    assert "Terminal=false" in desktop_text


def test_install_desktop_entry_command_writes_desktop_file(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    output_path = tmp_path / "applications" / "harite.desktop"

    monkeypatch.setattr(cli.sys, "platform", "linux")

    result = runner.invoke(
        cli.app,
        [
            "install-desktop-entry",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "[Desktop Entry]" in content
    assert "Exec=" in content
    assert "-m harite.gui.app" in content


def test_install_desktop_entry_command_rejects_existing_file_without_force(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    output_path = tmp_path / "applications" / "harite.desktop"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("existing\n", encoding="utf-8")

    monkeypatch.setattr(cli.sys, "platform", "linux")

    result = runner.invoke(
        cli.app,
        [
            "install-desktop-entry",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 2
    assert f"Desktop entry already exists: {output_path}" in result.output


def test_install_desktop_entry_command_supports_force_overwrite(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    output_path = tmp_path / "applications" / "harite.desktop"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("existing\n", encoding="utf-8")

    monkeypatch.setattr(cli.sys, "platform", "linux")

    result = runner.invoke(
        cli.app,
        [
            "install-desktop-entry",
            "--output",
            str(output_path),
            "--force",
        ],
    )

    assert result.exit_code == 0
    content = output_path.read_text(encoding="utf-8")
    assert "[Desktop Entry]" in content


def test_install_desktop_entry_command_rejects_non_linux(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    output_path = tmp_path / "harite.desktop"

    monkeypatch.setattr(cli.sys, "platform", "win32")

    result = runner.invoke(
        cli.app,
        [
            "install-desktop-entry",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 2
    assert "only supported on Linux/XDG" in result.output
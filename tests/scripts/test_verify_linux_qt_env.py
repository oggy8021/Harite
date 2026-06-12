"""Smoke tests for scripts/verify_linux_qt_env.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_verify_linux_qt_env_script_runs():
    script = Path(__file__).resolve().parents[2] / "scripts" / "verify_linux_qt_env.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    if sys.platform.startswith("linux"):
        assert result.returncode in (0, 1)
    else:
        assert result.returncode == 0
        assert "skip" in (result.stdout + result.stderr).lower()

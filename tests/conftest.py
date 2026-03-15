import pytest
from PIL import Image


@pytest.fixture
def make_image(tmp_path):
    """Return a helper that creates an image file inside the test's tmp_path.

    Usage:
        path = make_image(name="bg.png", size=(800,600))
    """

    def _make(name="img.png", size=(100, 100), color=(255, 0, 0, 255)):
        p = tmp_path / name
        img = Image.new("RGBA", size, color)
        img.save(str(p))
        return str(p)

    return _make
import base64
from pathlib import Path


def pytest_sessionstart(session):
    data_dir = Path(__file__).parent / "data"
    if not data_dir.exists():
        return

    for b64_path in data_dir.glob("*.b64"):
        target_name = b64_path.name.replace(".b64", "")
        target_path = b64_path.with_name(target_name)
        if target_path.exists():
            continue
        try:
            content = b64_path.read_text(encoding="utf-8")
            decoded = base64.b64decode(content)
            target_path.write_bytes(decoded)
        except Exception:
            # If decoding fails, tests that depend on these files will skip
            continue

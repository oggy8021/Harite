import base64
from pathlib import Path


def main():
    p = Path("tests/data")
    if not p.exists():
        print("tests/data not found")
        return

    for b in p.glob("*.b64"):
        out = b.with_suffix("")
        if out.exists():
            print("exists", out)
            continue
        try:
            decoded = base64.b64decode(b.read_text(encoding="utf-8"))
            out.write_bytes(decoded)
            print("wrote", out)
        except Exception as e:
            print("failed", b, e)


if __name__ == "__main__":
    main()

from PIL import Image

paths = [
    "tests/data/img_wide.jpg",
    "tests/data/left.jpg",
    "tests/data/right.jpg",
]

for p in paths:
    try:
        with Image.open(p) as im:
            im.load()
            print(p, "OK", im.size)
    except Exception as e:
        print(p, "ERR", type(e).__name__, e)

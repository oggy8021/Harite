import os
from pathlib import Path
base = Path('harite-xfce-logs')
if not base.exists():
    print('no harite-xfce-logs dir')
    raise SystemExit(1)
for p in sorted(base.iterdir()):
    if p.is_dir():
        print('==', p)
        for child in p.iterdir():
            print('  -', child.name)
        env = p / 'env.txt'
        if env.exists():
            print('--- env.txt ---')
            print(env.read_text(errors='replace')[:1000])
        else:
            print('env.txt: missing')

from pathlib import Path
base = Path('harite-xfce-logs')
for p in sorted(base.iterdir()):
    if p.is_dir():
        print('==', p)
        hl = p / 'harite.log'
        if hl.exists():
            print(hl.read_text(errors='replace'))
        else:
            print('harite.log: missing')

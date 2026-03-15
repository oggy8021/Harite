import tarfile
import os
import sys

import argparse

parser = argparse.ArgumentParser(description='Extract and show XFCE log archive')
parser.add_argument('archive', nargs='?', default='harite-xfce-logs_20260315_1923.tar.gz')
parser.add_argument('--outdir', default='harite-xfce-logs')
args = parser.parse_args()

ARCHIVE = args.archive
OUTDIR = args.outdir

if not os.path.exists(ARCHIVE):
    print('archive not found:', ARCHIVE)
    sys.exit(2)

os.makedirs(OUTDIR, exist_ok=True)

try:
    with tarfile.open(ARCHIVE, 'r:gz') as tf:
        tf.extractall(OUTDIR)
    print('extracted to', OUTDIR)
except Exception as e:
    print('extract failed:', e)
    sys.exit(3)

base = os.path.splitext(os.path.basename(ARCHIVE))[0]
candidate = os.path.join(OUTDIR, base)
if os.path.isdir(candidate):
    D = candidate
else:
    # fallback: pick the first directory under OUTDIR
    D = None
    for entry in os.listdir(OUTDIR):
        p = os.path.join(OUTDIR, entry)
        if os.path.isdir(p):
            D = p
            break
    if D is None:
        print('expected directory not found under', OUTDIR)
        sys.exit(0)

print('using directory:', D)

for fname in ['env.txt','xrandr.txt','display_info.txt','harite.log','xorg.log','display-manager.log']:
    p = os.path.join(D, fname)
    print('\n----', fname, '----')
    if os.path.exists(p):
        try:
            with open(p, 'r', encoding='utf-8', errors='replace') as f:
                data = f.read()
                print(data[:10000])
        except Exception as e:
            print('failed to read', fname, e)
    else:
        print('missing')

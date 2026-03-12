import pathlib
bad=[]
for p in pathlib.Path('.').rglob('*'):
    if p.is_file():
        try:
            # skip common binary files by extension to speed up
            if p.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.bmp','.ico'}:
                continue
            p.read_text(encoding='utf-8')
        except Exception as e:
            bad.append((str(p), str(e)))
for f,e in bad:
    print(f + ' : ' + e)
print('TOTAL_BAD:', len(bad))

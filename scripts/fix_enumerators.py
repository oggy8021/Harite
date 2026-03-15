#!/usr/bin/env python3
import re
from pathlib import Path
import difflib

DOCS_DIR = Path('docs')
REPORT = DOCS_DIR / 'docs-consolidation-enumerator-fix.md'

md_files = list(DOCS_DIR.rglob('*.md'))
changes = []
pattern = re.compile(r'(?m)^(\s*[-*]?\s*)(\d+)。')

for fp in md_files:
    text = fp.read_text(encoding='utf-8')
    new_text = pattern.sub(r"\1\2.", text)
    if new_text != text:
        diff = ''.join(difflib.unified_diff(text.splitlines(True), new_text.splitlines(True), fromfile=str(fp), tofile=str(fp) + ' (fixed)'))
        changes.append((fp, diff))
        fp.write_text(new_text, encoding='utf-8')

with REPORT.open('w', encoding='utf-8') as f:
    if not changes:
        f.write('# No enumerator fixes applied\n')
    else:
        f.write('# Enumerator fixes applied\n\n')
        for fp, diff in changes:
            f.write(f'## {fp}\n\n')
            f.write('```diff\n')
            f.write(diff)
            f.write('\n```\n\n')

print(f'Processed {len(md_files)} files, fixes in {len(changes)} files. Report: {REPORT}')

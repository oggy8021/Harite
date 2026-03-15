#!/usr/bin/env python3
import re
from pathlib import Path
import difflib

DOCS_DIR = Path('docs')
REPORT = DOCS_DIR / 'docs-consolidation-replacements-applied.md'

md_files = list(DOCS_DIR.rglob('*.md'))
replacements = []

for fp in md_files:
    text = fp.read_text(encoding='utf-8')
    original = text

    # extract code blocks (```...```)
    blocks = re.findall(r'```.*?```', text, flags=re.DOTALL)
    for i, b in enumerate(blocks):
        text = text.replace(b, f'__BLOCK_{i}__')

    # extract inline code (`...`), after code blocks removed
    inline_codes = re.findall(r'`[^`]*`', text)
    for i, c in enumerate(inline_codes):
        text = text.replace(c, f'__CODE_{i}__')

    # perform replacements on remaining text
    new_text = text
    # replace comma + whitespace with Japanese 読点
    new_text = re.sub(r',\s+', '、', new_text)
    # replace period + whitespace with Japanese 句点
    new_text = re.sub(r'\.\s+', '。', new_text)

    # restore inline codes
    for i, c in enumerate(inline_codes):
        new_text = new_text.replace(f'__CODE_{i}__', c)
    # restore code blocks
    for i, b in enumerate(blocks):
        new_text = new_text.replace(f'__BLOCK_{i}__', b)

    if new_text != original:
        diff = ''.join(difflib.unified_diff(original.splitlines(True), new_text.splitlines(True), fromfile=str(fp), tofile=str(fp) + ' (modified)'))
        replacements.append((fp, diff))
        fp.write_text(new_text, encoding='utf-8')

# write report
with REPORT.open('w', encoding='utf-8') as f:
    if not replacements:
        f.write('# No replacements applied\n')
    else:
        f.write('# Replacements applied\n\n')
        for fp, diff in replacements:
            f.write(f'## {fp}\n\n')
            f.write('```diff\n')
            f.write(diff)
            f.write('\n```\n\n')

print(f'Processed {len(md_files)} files, replacements in {len(replacements)} files. Report: {REPORT}')

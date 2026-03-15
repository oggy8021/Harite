#!/usr/bin/env python3
"""Apply a small set of automated replacements across `docs/` markdown files.

Features:
- Skips fenced code blocks and inline code spans.
- Produces a unified-diff report.
- `--dry-run` will not write changes to files (report still produced).

Intended use: run locally on a feature branch, review the report, then commit/PR.
"""

import argparse
import re
from pathlib import Path
import difflib


REPLACEMENTS = [
    (re.compile(r',\s+'), '、'),
    (re.compile(r'\.\s+'), '。'),
]


def process_file(fp: Path):
    text = fp.read_text(encoding='utf-8')
    original = text

    # extract fenced code blocks (```...```) and replace with placeholders
    blocks = re.findall(r'```.*?```', text, flags=re.DOTALL)
    for i, b in enumerate(blocks):
        text = text.replace(b, f'__BLOCK_{i}__')

    # extract inline code (`...`) after code blocks removed
    inline_codes = re.findall(r'`[^`]*`', text)
    for i, c in enumerate(inline_codes):
        text = text.replace(c, f'__CODE_{i}__')

    new_text = text
    for pattern, repl in REPLACEMENTS:
        new_text = pattern.sub(repl, new_text)

    # restore inline codes and code blocks
    for i, c in enumerate(inline_codes):
        new_text = new_text.replace(f'__CODE_{i}__', c)
    for i, b in enumerate(blocks):
        new_text = new_text.replace(f'__BLOCK_{i}__', b)

    return original, new_text


def main(argv=None):
    p = argparse.ArgumentParser(description='Apply doc replacements (safe, with dry-run).')
    p.add_argument('--docs-dir', default='docs', help='Docs directory (default: docs)')
    p.add_argument('--report', default=None, help='Path to write the unified-diff report (default: docs/docs-consolidation-replacements-applied.md)')
    p.add_argument('--dry-run', action='store_true', help='Do not write changes, only show/write report')
    args = p.parse_args(argv)

    DOCS_DIR = Path(args.docs_dir)
    if args.report:
        REPORT = Path(args.report)
    else:
        REPORT = DOCS_DIR / 'docs-consolidation-replacements-applied.md'

    md_files = list(DOCS_DIR.rglob('*.md'))
    replacements = []

    for fp in md_files:
        original, new_text = process_file(fp)
        if new_text != original:
            diff = ''.join(difflib.unified_diff(original.splitlines(True), new_text.splitlines(True), fromfile=str(fp), tofile=str(fp) + ' (modified)'))
            replacements.append((fp, diff))
            if not args.dry_run:
                fp.write_text(new_text, encoding='utf-8')

    REPORT.parent.mkdir(parents=True, exist_ok=True)
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


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Fix numeric enumerators that were accidentally converted to full-width punctuation.

Adds a `--dry-run` flag and `--report` path so maintainers can preview changes.
"""

import argparse
import re
from pathlib import Path
import difflib


def main(argv=None):
    p = argparse.ArgumentParser(description='Fix enumerator terminators (with dry-run).')
    p.add_argument('--docs-dir', default='docs', help='Docs directory (default: docs)')
    p.add_argument('--report', default=None, help='Path to write the unified-diff report (default: docs/docs-consolidation-enumerator-fix.md)')
    p.add_argument('--dry-run', action='store_true', help='Do not write changes, only show/write report')
    args = p.parse_args(argv)

    DOCS_DIR = Path(args.docs_dir)
    if args.report:
        REPORT = Path(args.report)
    else:
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
            if not args.dry_run:
                fp.write_text(new_text, encoding='utf-8')

    REPORT.parent.mkdir(parents=True, exist_ok=True)
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


if __name__ == '__main__':
    main()

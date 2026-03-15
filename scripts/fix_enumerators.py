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
    # Conservative pattern: only convert when the line is a list item (has a list marker
    # like '-', '*', '+', or an ASCII numbered list like '1. ') followed by a fullwidth dot.
    pattern = re.compile(r'(?m)^(\s*(?:[-*+]\s*|\d+\.\s*))(\d+)。')

    for fp in md_files:
        text = fp.read_text(encoding='utf-8')
        # remove fenced code blocks and inline code to avoid accidental changes inside code
        blocks = re.findall(r'```.*?```', text, flags=re.DOTALL)
        tmp = text
        for i, b in enumerate(blocks):
            tmp = tmp.replace(b, f'__BLOCK_{i}__')

        inline_codes = re.findall(r'`[^`]*`', tmp)
        for i, c in enumerate(inline_codes):
            tmp = tmp.replace(c, f'__CODE_{i}__')

        # perform conservative, line-by-line replacement
        lines = tmp.splitlines(True)
        out_lines = []
        for line in lines:
            # skip markdown table rows
            if '|' in line:
                out_lines.append(line)
                continue
            # skip diff-like lines that start with '+' or '-' without a following space
            stripped = line.lstrip()
            if stripped.startswith(('+', '-')) and not stripped.startswith(('+ ', '- ')):
                out_lines.append(line)
                continue
            m = pattern.match(line)
            if m:
                prefix = m.group(1)
                num = m.group(2)
                new_line = f"{prefix}{num}." + line[m.end():]
                out_lines.append(new_line)
            else:
                out_lines.append(line)

        new_tmp = ''.join(out_lines)

        # restore inline codes and code blocks
        for i, c in enumerate(inline_codes):
            new_tmp = new_tmp.replace(f'__CODE_{i}__', c)
        for i, b in enumerate(blocks):
            new_tmp = new_tmp.replace(f'__BLOCK_{i}__', b)

        new_text = new_tmp
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

import subprocess
import sys
from pathlib import Path
import tempfile


def run_script(script_path, args, cwd=None):
    cmd = [sys.executable, str(script_path)] + args
    subprocess.check_call(cmd, cwd=cwd)


def test_apply_docs_replacements_no_change():
    script = Path('scripts/apply_docs_replacements.py')
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        docs = td_path / 'docs'
        docs.mkdir()
        # copy fixture
        src = Path('tests/fixtures/sample_no_change.md')
        dst = docs / 'sample_no_change.md'
        dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')

        report = td_path / 'report.md'
        run_script(script, ['--docs-dir', str(docs), '--report', str(report), '--dry-run'])
        assert report.exists()
        content = report.read_text(encoding='utf-8')
        assert 'No replacements applied' in content


def test_fix_enumerators_detects_and_reports():
    script = Path('scripts/fix_enumerators.py')
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        docs = td_path / 'docs'
        docs.mkdir()
        src = Path('tests/fixtures/sample_enumerators.md')
        dst = docs / 'sample_enumerators.md'
        dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')

        report = td_path / 'enumerator_report.md'
        run_script(script, ['--docs-dir', str(docs), '--report', str(report), '--dry-run'])
        assert report.exists()
        content = report.read_text(encoding='utf-8')
        # report should indicate a fix or changes
        assert 'Enumerator fixes applied' in content or 'fixed' in content or '1.' in content

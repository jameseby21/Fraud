"""Full checkpoint verification; requires optional vault dependencies and Node."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verification import test_run_passes


def main():
    if importlib.util.find_spec('cryptography') is None:
        print('Full verification requires requirements-vault.txt; skipped security tests are not accepted.', file=sys.stderr)
        return 2
    if shutil.which('node') is None:
        print('Full verification requires Node for JavaScript syntax checks.', file=sys.stderr)
        return 2
    commands = [
        [sys.executable, 'scripts/check_publication.py', '--all'],
        [sys.executable, 'scripts/check_staged_data.py'],
        [sys.executable, 'intake.py', 'verify'],
        [sys.executable, 'documentation.py'],
        [sys.executable, 'learning_fixture.py', 'verify'],
        [sys.executable, 'scripts/build_courses.py', '--verify'],
        ['node', '--check', 'web/library.js'],
        ['node', '--check', 'web/learn.js'],
        ['node', '--check', 'scripts/browser_smoke.mjs'],
    ]
    for command in commands:
        if subprocess.run(command, cwd=ROOT).returncode:
            return 1
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not test_run_passes(result):
        print('Full verification failed: tests must execute with zero skips, expected failures, failures, or errors.', file=sys.stderr)
        return 1
    print(f'PASS: {result.testsRun} tests, zero skips; publication, source-byte, and syntax checks passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

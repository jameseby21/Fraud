"""Pre-commit check: staged data bytes must match the verified working copies."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    listed = subprocess.check_output(['git', 'ls-files', '-z', '--', 'data'], cwd=ROOT).decode().split('\0')
    mismatches = []
    count = 0
    for name in filter(None, listed):
        # Only the actual staged blob is checked; no checkout or mutation occurs.
        staged = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT)
        working = (ROOT / name).read_bytes()
        count += 1
        if hashlib.sha256(staged).digest() != hashlib.sha256(working).digest():
            mismatches.append(name)
    if mismatches:
        print('FAIL: Git would store different data bytes for ' + str(len(mismatches)) + ' artifact(s):')
        for name in mismatches:
            print(name)
        return 1
    print(f'PASS: {count} staged data files preserve their verified bytes.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

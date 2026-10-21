"""Local pre-commit gates; Git/crypto data remain unchanged."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for script in ('check_publication.py', 'check_staged_data.py'):
    result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script)], cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)

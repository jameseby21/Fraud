"""Inspect actual staged Git blobs without printing matched credentials."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from publication_guard import scan_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', help='Check every tracked index blob, not only staged changes')
    args = parser.parse_args()
    try:
        result = scan_index(all_files=args.all)
    except (OSError, subprocess.SubprocessError, ValueError):
        print('Publication review failed; Git index was not fully inspected.', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result['safe_to_publish'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

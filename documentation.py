"""Validate the README-rooted documentation graph; no claim of semantic drift detection."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent


def documents(root):
    return sorted(p for p in root.rglob('*.md') if not any(part.startswith('.') or part in ('output', 'node_modules') for part in p.relative_to(root).parts))


def verify_docs(root=ROOT):
    root = root.resolve()
    docs = documents(root)
    graph, broken = {}, []
    for path in docs:
        content = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
        graph[path] = []
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', content):
            target = target.strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                broken.append(f'{path.relative_to(root).as_posix()}: {target}')
            elif resolved.suffix.lower() == '.md':
                graph[path].append(resolved)
    seen, pending = set(), [root / 'README.md']
    while pending:
        path = pending.pop()
        if path not in seen:
            seen.add(path)
            pending.extend(graph.get(path, []))
    return dict(documents=len(docs), broken_links=sorted(broken),
                unreachable=[p.relative_to(root).as_posix() for p in docs if p not in seen])


def write_tree():
    path = ROOT / 'docs/DOCTREE.md'
    path.parent.mkdir(exist_ok=True)
    path.touch(exist_ok=True)
    content = '''# Documentation tree and change map

[Root README: canonical project state](../README.md). Update that entry point whenever behavior, setup, datasets or validation limits change. This index is regenerated with `python documentation.py --write-tree`; verify with `python documentation.py`.

## Required updates by change

| Change | Update before committing |
| --- | --- |
| Routes or UI | Root README, course guide, HTTP/browser tests, checkpoint and troubleshooting |
| Data intake or library schema | Root README, DATA_SOURCES, library guide, intake/verification tests and checkpoint |
| Fixtures or planted patterns | Root README, dataset guide, instructor lineage, fraud-instance library, affected lessons and tests |
| Course structure or tool code | Root README, course guide, generated lessons/notebooks, R/Power BI guides, course tests and checkpoint |
| Models or statistical criteria | MODEL_CARD, pattern assumptions/controls, lessons, regression tests and root README |
| Private storage or publication | SECURITY, CONTRIBUTING, relevant tests, checkpoint and root README |
| New documentation | Link it here, fix local links, run the documentation graph check |

For every function or behavior: failing acceptance tests first, implementation, focused checks, regression tests for discoveries, then union/integration tests and full verification before stage/commit/push. A passing leaf test does not substitute for integration. Record what actually ran and what remains manual.

The check detects missing local targets and Markdown pages unreachable from README. It does not prove factual correctness, detect every stale statement, or validate external availability/anchors. Authors must review this change map and the linked documents for semantic drift.

## Linked document inventory

'''
    for doc in documents(ROOT):
        relative = doc.relative_to(ROOT).as_posix()
        target = '../' + relative
        content += f'- [{relative}]({target})\n'
    path.write_text(content, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-tree', action='store_true')
    if parser.parse_args().write_tree:
        write_tree()
    report = verify_docs()
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report['broken_links'] or report['unreachable']))

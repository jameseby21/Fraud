"""Heuristic public-repository guard. Never prints matched secret values."""
from pathlib import Path, PurePosixPath
import json
import re
import subprocess

MAX_REVIEW_BYTES = 20 * 1024 * 1024
PATTERNS = (
    ('private_key_material', re.compile(rb'(?m)^\s*-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
    ('github_credential', re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b')),
    ('cloud_access_key', re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
)


def inspect_public_file(name, content):
    path = PurePosixPath(name.replace('\\', '/'))
    parts = [part.lower() for part in path.parts]
    filename = parts[-1] if parts else ''
    findings = []
    forbidden = (path.is_absolute() or '..' in parts or
                 any(p in {'private', '.private', '.ssh', 'vault-data', '.vault', '.vaults'} for p in parts) or
                 filename.endswith(('.fvault', '.fvault.lock', '.key', '.pem', '.p12', '.pfx')) or
                 filename in {'id_rsa', 'id_ed25519', '.env'} or
                 (filename.startswith('.env.') and filename != '.env.example'))
    if forbidden:
        findings.append(dict(path=name, rule='private_artifact_path', message='Private artifacts must remain outside the public repository.'))
    if len(content) > MAX_REVIEW_BYTES:
        findings.append(dict(path=name, rule='review_size_limit', message='File exceeds the automatic publication-review size limit.'))
        return findings
    for rule, pattern in PATTERNS:
        if pattern.search(content):
            findings.append(dict(path=name, rule=rule, message='Potential credential or key material; matched values are redacted.'))
    try:
        parsed = json.loads(content)
    except (ValueError, UnicodeError, RecursionError):
        parsed = None
    if isinstance(parsed, dict):
        header = parsed.get('header')
        encrypted = isinstance(header, dict) and header.get('cipher') == 'AES-256-GCM' and 'ciphertext' in parsed
        plaintext = parsed.get('schema_version') == 1 and isinstance(parsed.get('notes'), list) and 'revision' in parsed
        if encrypted or plaintext:
            findings.append(dict(path=name, rule='vault_document_content', message='Recognized vault document content must remain outside the public repository.'))
    return findings


def scan_index(root=None, all_files=False):
    root = Path(root) if root else Path(__file__).resolve().parent
    command = ['git', 'ls-files', '-z'] if all_files else ['git', 'diff', '--cached', '--name-only', '-z', '--diff-filter=ACMR']
    listed = subprocess.check_output(command, cwd=root, stderr=subprocess.PIPE).decode('utf-8').split('\0')
    findings, count = [], 0
    for name in filter(None, listed):
        count += 1
        size = int(subprocess.check_output(['git', 'cat-file', '-s', ':' + name], cwd=root, stderr=subprocess.PIPE))
        if size > MAX_REVIEW_BYTES:
            findings.append(dict(path=name, rule='review_size_limit', message='File exceeds the automatic publication-review size limit.'))
            continue
        content = subprocess.check_output(['git', 'show', ':' + name], cwd=root, stderr=subprocess.PIPE)
        findings.extend(inspect_public_file(name, content))
    return dict(files_checked=count, safe_to_publish=not findings, findings=findings,
                limitation='Heuristic path/credential checks cannot detect every secret or sensitive statement; manual staged-diff review is required.')

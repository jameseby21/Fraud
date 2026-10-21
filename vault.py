"""Optional encrypted local storage. Never imported or served by the web app."""
import argparse
import base64
from contextlib import contextmanager
import csv
import getpass
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

MAX_BLOB_BYTES = 4 * 1024 * 1024
MAX_PLAINTEXT_BYTES = 1024 * 1024
KDF = dict(name='argon2id', iterations=3, lanes=4, memory_kib=65536)


class VaultError(Exception):
    """A safe-to-display error without secret contents."""


def _crypto():
    try:
        from cryptography.exceptions import InvalidTag
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
    except ImportError:
        raise VaultError('Install the optional hash-pinned requirements-vault.txt in a virtual environment.') from None
    return AESGCM, Argon2id, InvalidTag


def _phrase_bytes(phrase):
    if not isinstance(phrase, str) or not 16 <= len(phrase) <= 4096:
        raise VaultError('Use a long, unique passphrase of at least 16 characters (maximum 4096).')
    return phrase.encode('utf-8')


def _derive(phrase, salt):
    _, Argon2id, _ = _crypto()
    return Argon2id(salt=salt, length=32, iterations=KDF['iterations'], lanes=KDF['lanes'],
                    memory_cost=KDF['memory_kib']).derive(_phrase_bytes(phrase))


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _b64(value):
    return base64.b64encode(value).decode('ascii')


def encrypt_document(document, passphrase):
    _phrase_bytes(passphrase)
    if not isinstance(document, dict):
        raise VaultError('Vault documents must be JSON objects.')
    try:
        plaintext = _canonical(document)
    except (ValueError, TypeError):
        raise VaultError('Vault document is not valid finite JSON.') from None
    if len(plaintext) > MAX_PLAINTEXT_BYTES:
        raise VaultError('Vault document exceeds the one-MiB plaintext limit.')
    salt, nonce = os.urandom(16), os.urandom(12)
    header = dict(version=1, cipher='AES-256-GCM', kdf=dict(KDF), salt=_b64(salt), nonce=_b64(nonce))
    AESGCM, _, _ = _crypto()
    ciphertext = AESGCM(_derive(passphrase, salt)).encrypt(nonce, plaintext, _canonical(header))
    return _canonical(dict(header=header, ciphertext=_b64(ciphertext))) + b'\n'


def decrypt_document(blob, passphrase):
    _phrase_bytes(passphrase)
    if not isinstance(blob, bytes) or len(blob) > MAX_BLOB_BYTES:
        raise VaultError('Invalid or oversized encrypted vault.')
    try:
        envelope = json.loads(blob)
        if not isinstance(envelope, dict) or set(envelope) != {'header', 'ciphertext'}:
            raise ValueError('Envelope')
        header = envelope['header']
        if not isinstance(header, dict) or set(header) != {'version', 'cipher', 'kdf', 'salt', 'nonce'}:
            raise ValueError('Header')
        if type(header['version']) is not int or header['version'] != 1 or header['cipher'] != 'AES-256-GCM':
            raise ValueError('Version')
        if header['kdf'] != KDF or any(type(header['kdf'][key]) is not int for key in ('iterations', 'lanes', 'memory_kib')):
            raise ValueError('KDF')
        salt = base64.b64decode(header['salt'], validate=True)
        nonce = base64.b64decode(header['nonce'], validate=True)
        ciphertext = base64.b64decode(envelope['ciphertext'], validate=True)
        if len(salt) != 16 or len(nonce) != 12 or len(ciphertext) < 16 or len(ciphertext) > MAX_PLAINTEXT_BYTES + 16:
            raise ValueError('Lengths')
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise VaultError('Invalid encrypted vault format or unsupported parameters.') from None
    AESGCM, _, InvalidTag = _crypto()
    try:
        plaintext = AESGCM(_derive(passphrase, salt)).decrypt(nonce, ciphertext, _canonical(header))
        document = json.loads(plaintext)
        if not isinstance(document, dict):
            raise ValueError('Document')
        return document
    except (InvalidTag, ValueError, TypeError, UnicodeError):
        raise VaultError('Unlock failed: wrong passphrase or modified vault.') from None


def _restrict_path(path, directory=False):
    if os.name == 'posix':
        os.chmod(path, 0o700 if directory else 0o600)
        return
    if os.name != 'nt':
        raise VaultError('OS permission enforcement is unavailable on this platform.')
    # Replace the DACL, retaining only the current user and LocalSystem. Do not
    # claim protection against administrators who can take ownership.
    import ctypes
    from ctypes import wintypes
    system = Path(os.environ['SystemRoot']) / 'System32'
    result = subprocess.run([str(system / 'whoami.exe'), '/user', '/fo', 'csv', '/nh'],
                            capture_output=True, text=True, check=True)
    sid = next(csv.reader(io.StringIO(result.stdout)))[1]
    if not re.fullmatch(r'S-1-[0-9-]+', sid):
        raise VaultError('Unable to establish the current user security identifier.')
    inheritance = 'OICI' if directory else ''
    sddl = f'D:P(A;{inheritance};FA;;;{sid})(A;{inheritance};FA;;;SY)'
    advapi = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    descriptor = ctypes.c_void_p()
    convert = advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW
    convert.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
    convert.restype = wintypes.BOOL
    set_security = advapi.SetFileSecurityW
    set_security.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_void_p]
    set_security.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if not convert(sddl, 1, ctypes.byref(descriptor), None):
        raise VaultError('Unable to prepare private OS permissions.')
    try:
        if not set_security(str(path), 0x80000004, descriptor):
            raise VaultError('Unable to enforce private OS permissions.')
    finally:
        kernel.LocalFree(descriptor)


class VaultFile:
    def __init__(self, path):
        original = Path(path).expanduser()
        if original.is_symlink():
            raise VaultError('Vault file must not be a symbolic link.')
        self.path = original.resolve()
        root = Path(__file__).resolve().parent
        if self.path.is_relative_to(root) or any((p / '.git').exists() for p in self.path.parents):
            raise VaultError('Store the vault outside every Git worktree, including this repository.')
        if self.path.suffix != '.fvault':
            raise VaultError('Use the .fvault extension for encrypted vault files.')

    @contextmanager
    def _lock(self):
        self.path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        _restrict_path(self.path.parent, directory=True)
        lock = self.path.with_suffix('.fvault.lock')
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            raise VaultError('Vault is locked or its private directory is inaccessible.') from None
        os.close(descriptor)
        try:
            yield
        finally:
            lock.unlink(missing_ok=True)

    def create(self, passphrase):
        document = dict(schema_version=1, revision=0, notes=[])
        blob = encrypt_document(document, passphrase)
        try:
            with self._lock():
                created = False
                try:
                    descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                    created = True
                    with os.fdopen(descriptor, 'wb') as stream:
                        _restrict_path(self.path)
                        stream.write(blob)
                        stream.flush()
                        os.fsync(stream.fileno())
                except (OSError, VaultError):
                    if created:
                        self.path.unlink(missing_ok=True)
                    raise
        except OSError:
            raise VaultError('Vault creation failed; an existing vault is never overwritten.') from None

    def read(self, passphrase):
        try:
            if self.path.is_symlink() or self.path.stat().st_size > MAX_BLOB_BYTES:
                raise VaultError('Invalid vault file or size.')
            document = decrypt_document(self.path.read_bytes(), passphrase)
        except OSError:
            raise VaultError('Vault is missing or inaccessible.') from None
        if document.get('schema_version') != 1 or type(document.get('revision')) is not int or not isinstance(document.get('notes'), list):
            raise VaultError('Unsupported vault document schema.')
        return document

    def _replace(self, blob):
        temporary = None
        try:
            descriptor, name = tempfile.mkstemp(prefix='.vault-', suffix='.tmp', dir=self.path.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, 'wb') as stream:
                _restrict_path(temporary)
                stream.write(blob)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        except OSError:
            raise VaultError('Vault update failed; previous ciphertext was retained.') from None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def update(self, passphrase, document, expected_revision):
        if type(expected_revision) is not int:
            raise VaultError('An explicit integer revision is required.')
        with self._lock():
            current = self.read(passphrase)
            if current['revision'] != expected_revision:
                raise VaultError('Vault changed; reload before saving to avoid a lost update.')
            if not isinstance(document, dict) or not isinstance(document.get('notes'), list):
                raise VaultError('Invalid vault document.')
            updated = dict(document, schema_version=1, revision=expected_revision+1)
            self._replace(encrypt_document(updated, passphrase))

    def rotate(self, old_passphrase, new_passphrase):
        _phrase_bytes(new_passphrase)
        with self._lock():
            current = self.read(old_passphrase)
            current['revision'] += 1
            self._replace(encrypt_document(current, new_passphrase))


def default_vault_path():
    base = Path(os.environ.get('LOCALAPPDATA') or Path.home() / '.local' / 'share')
    return base / 'FraudVault' / 'records.fvault'


def _prompt(label):
    if not sys.stdin.isatty():
        raise VaultError('Vault unlock requires an interactive terminal; passphrases are never accepted in command-line arguments.')
    return getpass.getpass(label)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'summary', 'rotate'))
    parser.add_argument('--path', type=Path, default=default_vault_path())
    args = parser.parse_args(argv)
    try:
        store = VaultFile(args.path)
        phrase = _prompt('Vault passphrase: ')
        if args.command == 'init':
            if phrase != _prompt('Confirm passphrase: '):
                raise VaultError('Passphrases did not match.')
            store.create(phrase)
            print('Encrypted local vault created outside Git. Keep a secure backup; there is no password recovery.')
        elif args.command == 'summary':
            doc = store.read(phrase)
            print(json.dumps(dict(revision=doc['revision'], notes=len(doc['notes']))))
        else:
            new_phrase = _prompt('New passphrase: ')
            if new_phrase != _prompt('Confirm new passphrase: '):
                raise VaultError('Passphrases did not match.')
            store.rotate(phrase, new_phrase)
            print('Current vault re-encrypted. Older backups still require their original passphrases.')
        return 0
    except (VaultError, OSError, subprocess.SubprocessError):
        # A stable generic CLI error does not reveal private paths or payloads.
        print('Vault operation failed. Check the passphrase, external path, permissions, or lock state.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

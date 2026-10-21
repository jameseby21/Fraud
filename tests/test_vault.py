import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

CRYPTO_AVAILABLE = importlib.util.find_spec('cryptography') is not None
if CRYPTO_AVAILABLE:
    from vault import VaultError, VaultFile, decrypt_document, encrypt_document

TEST_PHRASE = 'Synthetic QA phrase - never a real password'
OTHER_PHRASE = 'Different synthetic QA phrase for testing'


@unittest.skipUnless(CRYPTO_AVAILABLE, 'Install requirements-vault.txt to run the vault security tests')
class EncryptionTests(unittest.TestCase):
    def test_roundtrip_never_contains_plaintext(self):
        document = {'note': 'Synthetic QA content', 'revision': 0}
        blob = encrypt_document(document, TEST_PHRASE)
        self.assertNotIn(b'Synthetic QA content', blob)
        self.assertNotIn(TEST_PHRASE.encode(), blob)
        self.assertEqual(decrypt_document(blob, TEST_PHRASE), document)

    def test_salt_and_nonce_are_fresh_on_every_encryption(self):
        first = json.loads(encrypt_document({'x': 1}, TEST_PHRASE))
        second = json.loads(encrypt_document({'x': 1}, TEST_PHRASE))
        self.assertNotEqual(first['header']['salt'], second['header']['salt'])
        self.assertNotEqual(first['header']['nonce'], second['header']['nonce'])

    def test_wrong_key_and_tampering_fail_closed(self):
        blob = encrypt_document({'note': 'Synthetic QA content'}, TEST_PHRASE)
        with self.assertRaises(VaultError):
            decrypt_document(blob, OTHER_PHRASE)
        changed = json.loads(blob)
        changed['ciphertext'] = ('A' if changed['ciphertext'][0] != 'A' else 'B') + changed['ciphertext'][1:]
        with self.assertRaises(VaultError):
            decrypt_document(json.dumps(changed).encode(), TEST_PHRASE)

    def test_modified_header_and_kdf_parameters_are_rejected(self):
        blob = json.loads(encrypt_document({'x': 1}, TEST_PHRASE))
        blob['header']['kdf']['memory_kib'] = 9999999999
        with patch('vault._derive') as derive, self.assertRaises(VaultError):
            decrypt_document(json.dumps(blob).encode(), TEST_PHRASE)
        derive.assert_not_called()

    def test_short_passphrases_and_non_json_documents_rejected(self):
        for phrase in ('', 'short'):
            with self.assertRaises(VaultError):
                encrypt_document({'x': 1}, phrase)
        with self.assertRaises(VaultError):
            encrypt_document({'bad': float('nan')}, TEST_PHRASE)

    def test_malformed_and_oversized_inputs_are_rejected(self):
        for blob in (b'', b'not-json', b'{}', b'[]', b'x' * (4 * 1024 * 1024 + 1)):
            with self.assertRaises(VaultError):
                decrypt_document(blob, TEST_PHRASE)


@unittest.skipUnless(CRYPTO_AVAILABLE, 'Install requirements-vault.txt to run the vault security tests')
class VaultFileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fraud-vault-qa-')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.path = self.directory / 'store' / 'records.fvault'
        self.store = VaultFile(self.path)

    def test_refuses_paths_inside_the_public_repository(self):
        root = Path(__file__).resolve().parents[1]
        with self.assertRaises(VaultError):
            VaultFile(root / 'data' / 'private' / 'records.fvault')

    def test_refuses_any_other_git_worktree(self):
        repo = self.directory / 'other-repo'
        repo.mkdir()
        (repo / '.git').mkdir()
        with self.assertRaises(VaultError):
            VaultFile(repo / 'records.fvault')

    def test_create_persist_and_refuse_overwrite(self):
        self.store.create(TEST_PHRASE)
        self.assertEqual(self.store.read(TEST_PHRASE)['revision'], 0)
        with self.assertRaises(VaultError):
            self.store.create(TEST_PHRASE)
        self.assertNotIn(TEST_PHRASE.encode(), self.path.read_bytes())

    def test_revision_guard_prevents_lost_updates(self):
        self.store.create(TEST_PHRASE)
        document = self.store.read(TEST_PHRASE)
        document['notes'].append({'body': 'Synthetic QA record'})
        self.store.update(TEST_PHRASE, document, expected_revision=0)
        self.assertEqual(self.store.read(TEST_PHRASE)['revision'], 1)
        with self.assertRaises(VaultError):
            self.store.update(TEST_PHRASE, document, expected_revision=0)

    def test_wrong_key_update_does_not_change_file(self):
        self.store.create(TEST_PHRASE)
        original = self.path.read_bytes()
        with self.assertRaises(VaultError):
            self.store.update(OTHER_PHRASE, {'notes': []}, expected_revision=0)
        self.assertEqual(self.path.read_bytes(), original)

    def test_failed_initial_file_permissions_leave_no_broken_vault(self):
        from vault import _restrict_path
        def permissions(path, directory=False):
            if not directory:
                raise VaultError('Synthetic QA permission failure')
            return _restrict_path(path, directory=True)
        with patch('vault._restrict_path', side_effect=permissions), self.assertRaises(VaultError):
            self.store.create(TEST_PHRASE)
        self.assertFalse(self.path.exists())

    def test_cli_does_not_read_passphrases_without_interactive_terminal(self):
        import io
        from vault import main
        error = io.StringIO()
        with patch('vault.sys.stdin.isatty', return_value=False), patch('vault.getpass.getpass') as prompt, patch('vault.sys.stderr', error):
            self.assertEqual(main(['summary', '--path', str(self.path)]), 1)
        prompt.assert_not_called()
        self.assertNotIn(str(self.path), error.getvalue())

    def test_replace_failure_keeps_previous_ciphertext(self):
        self.store.create(TEST_PHRASE)
        before = self.path.read_bytes()
        document = self.store.read(TEST_PHRASE)
        with patch('vault.os.replace', side_effect=OSError('Synthetic QA failure')), self.assertRaises(VaultError):
            self.store.update(TEST_PHRASE, document, expected_revision=0)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob('*.tmp')), [])

    def test_lock_conflict_fails_without_altering_vault(self):
        self.store.create(TEST_PHRASE)
        self.path.with_suffix('.fvault.lock').touch()
        with self.assertRaises(VaultError):
            self.store.update(TEST_PHRASE, self.store.read(TEST_PHRASE), expected_revision=0)

    def test_rotation_preserves_records_and_invalidates_old_phrase(self):
        self.store.create(TEST_PHRASE)
        self.store.rotate(TEST_PHRASE, OTHER_PHRASE)
        self.assertEqual(self.store.read(OTHER_PHRASE)['notes'], [])
        with self.assertRaises(VaultError):
            self.store.read(TEST_PHRASE)

    def test_os_permissions_are_restricted(self):
        self.store.create(TEST_PHRASE)
        if os.name == 'posix':
            self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.path.parent.stat().st_mode & 0o777, 0o700)
        else:
            import subprocess
            acl = subprocess.check_output(['icacls', str(self.path.parent)], text=True)
            self.assertNotIn('BUILTIN\\Users:', acl)
            self.assertNotIn('Everyone:', acl)

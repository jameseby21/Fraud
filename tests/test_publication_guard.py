import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from publication_guard import inspect_public_file, scan_index


class PublicationGuardTests(unittest.TestCase):
    def test_public_source_and_synthetic_fixture_are_allowed(self):
        self.assertEqual(inspect_public_file('data/cases.json', b'{"synthetic": false}'), [])
        self.assertEqual(inspect_public_file('tests/test_vault.py', b'TEST_PHRASE = "Synthetic QA phrase"'), [])

    def test_private_locations_are_rejected_even_if_force_added(self):
        for path in ('data/private/notes.json', '.env', '.env.local', 'records.fvault', 'nested/key.pem',
                     '.ssh/id_ed25519', 'vault-data/notes.json'):
            with self.subTest(path=path):
                self.assertTrue(inspect_public_file(path, b'Synthetic QA content'))

    def test_credential_patterns_are_reported_without_echoing_values(self):
        tokens = [b'ghp_' + b'A' * 36, b'AKIA' + b'A' * 16,
                  b'-----BEGIN ' + b'PRIVATE KEY-----\nSynthetic QA\n']
        for token in tokens:
            with self.subTest(kind=token[:4]):
                findings = inspect_public_file('example.txt', token)
                self.assertTrue(findings)
                self.assertNotIn(token.decode(), json.dumps(findings))

    def test_env_example_without_real_secret_is_allowed(self):
        self.assertEqual(inspect_public_file('.env.example', b'SERVICE_TOKEN=replace-me'), [])

    def test_indented_private_key_material_is_not_missed(self):
        content = b'  -----BEGIN ' + b'PRIVATE KEY-----\nSynthetic QA\n'
        self.assertTrue(inspect_public_file('example.txt', content))

    def test_renamed_encrypted_and_plaintext_vault_snapshots_are_blocked(self):
        for payload in ({'header': {'cipher': 'AES-256-GCM'}, 'ciphertext': 'Synthetic QA'},
                        {'schema_version': 1, 'revision': 0, 'notes': []}):
            with self.subTest(payload=payload):
                self.assertTrue(inspect_public_file('renamed.json', json.dumps(payload).encode()))

    def test_only_staged_bytes_are_inspected(self):
        with tempfile.TemporaryDirectory(prefix='fraud-publication-qa-') as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)
            path = root / 'example.txt'
            path.write_text('Synthetic public fixture', encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', 'example.txt'], check=True, capture_output=True)
            path.write_bytes(b'ghp_' + b'A' * 36)
            self.assertEqual(scan_index(root, all_files=True)['findings'], [])
            subprocess.run(['git', '-C', str(root), 'add', 'example.txt'], check=True, capture_output=True)
            result = scan_index(root, all_files=True)
            self.assertEqual(len(result['findings']), 1)
            self.assertFalse(result['safe_to_publish'])

    def test_force_added_vault_is_blocked(self):
        with tempfile.TemporaryDirectory(prefix='fraud-publication-qa-') as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)
            (root / '.gitignore').write_text('*.fvault\n')
            (root / 'example.fvault').write_text('Synthetic QA ciphertext placeholder')
            subprocess.run(['git', '-C', str(root), 'add', '-f', 'example.fvault'], check=True, capture_output=True)
            self.assertFalse(scan_index(root, all_files=True)['safe_to_publish'])

from datetime import datetime, timezone
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

CRYPTO_AVAILABLE = importlib.util.find_spec('cryptography') is not None
if CRYPTO_AVAILABLE:
    from vault import VaultFile, VaultError
    from vault_notes import add_note, revise_note, read_note, list_notes, main

PHRASE = 'Synthetic QA phrase - never a real password'
NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)


@unittest.skipUnless(CRYPTO_AVAILABLE, 'Install the optional vault dependencies')
class EncryptedNotesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fraud-notes-qa-')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'store' / 'records.fvault'
        self.store = VaultFile(self.path)
        self.store.create(PHRASE)

    def add(self, **changes):
        args = dict(case_id='synthetic-qa', kind='hypothesis', title='Synthetic QA title', body='Synthetic QA body', now=NOW)
        args.update(changes)
        return add_note(self.store, PHRASE, **args)

    def test_note_survives_restart_without_plaintext_files(self):
        identifier = self.add()
        reloaded = VaultFile(self.path)
        note = read_note(reloaded, PHRASE, identifier)
        self.assertEqual(note['revisions'][0]['body'], 'Synthetic QA body')
        self.assertNotIn(b'Synthetic QA', self.path.read_bytes())
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ['records.fvault'])

    def test_correction_preserves_original_and_reason(self):
        identifier = self.add()
        revise_note(self.store, PHRASE, identifier, 'Revised synthetic QA body', 'Synthetic QA correction', expected_revision=1, now=NOW)
        note = read_note(self.store, PHRASE, identifier)
        self.assertEqual([r['number'] for r in note['revisions']], [1, 2])
        self.assertEqual(note['revisions'][0]['body'], 'Synthetic QA body')
        self.assertEqual(note['revisions'][1]['reason'], 'Synthetic QA correction')

    def test_stale_note_revision_is_rejected(self):
        identifier = self.add()
        revise_note(self.store, PHRASE, identifier, 'Second version', 'QA correction', expected_revision=1, now=NOW)
        before = self.path.read_bytes()
        with self.assertRaises(VaultError):
            revise_note(self.store, PHRASE, identifier, 'Stale version', 'QA stale write', expected_revision=1, now=NOW)
        self.assertEqual(self.path.read_bytes(), before)

    def test_notes_keep_claim_types_distinct(self):
        for kind in ('observation', 'hypothesis', 'counterevidence', 'review_note'):
            identifier = self.add(kind=kind)
            self.assertEqual(read_note(self.store, PHRASE, identifier)['kind'], kind)
        with self.assertRaises(VaultError):
            self.add(kind='proven_fraud')

    def test_empty_invalid_or_terminal_control_text_is_rejected(self):
        for change in ({'title': ''}, {'body': ''}, {'case_id': '../bad'}, {'body': '\x1b[31mQA'}, {'body': '\u009b31mQA'}, {'title': 'x' * 201}):
            with self.subTest(change=change), self.assertRaises(VaultError):
                self.add(**change)

    def test_list_omits_body_and_correction_reasons(self):
        identifier = self.add()
        listed = list_notes(self.store, PHRASE)
        self.assertEqual(listed[0]['id'], identifier)
        self.assertNotIn('body', str(listed))
        self.assertNotIn('revisions', listed[0])

    def test_unknown_note_and_wrong_key_do_not_change_data(self):
        self.add()
        before = self.path.read_bytes()
        with self.assertRaises(VaultError):
            read_note(self.store, PHRASE, 'unknown')
        with self.assertRaises(VaultError):
            list_notes(self.store, 'Different synthetic QA phrase')
        self.assertEqual(before, self.path.read_bytes())

    def test_explicit_utc_time_and_revision_reason_are_required(self):
        with self.assertRaises(VaultError):
            self.add(now=datetime(2026, 10, 21))
        identifier = self.add()
        with self.assertRaises(VaultError):
            revise_note(self.store, PHRASE, identifier, 'QA update', '', expected_revision=1, now=NOW)

    def test_add_cli_uses_hidden_prompts_and_does_not_print_content(self):
        output = io.StringIO()
        with patch('vault_notes._prompt', side_effect=[PHRASE, 'synthetic-qa', 'review_note', 'Synthetic QA title', 'Synthetic QA body']), patch('vault_notes.sys.stdout', output):
            self.assertEqual(main(['add', '--path', str(self.path)]), 0)
        self.assertNotIn('Synthetic QA', output.getvalue())
        self.assertNotIn(PHRASE, output.getvalue())

    def test_cli_errors_are_generic_and_do_not_echo_inputs(self):
        output = io.StringIO()
        with patch('vault_notes._prompt', return_value='Different synthetic QA phrase'), patch('vault_notes.sys.stderr', output):
            self.assertEqual(main(['list', '--path', str(self.path)]), 1)
        self.assertNotIn(str(self.path), output.getvalue())

    def test_read_cli_displays_only_current_body_unless_history_requested(self):
        identifier = self.add()
        revise_note(self.store, PHRASE, identifier, 'Current QA content', 'QA correction', expected_revision=1, now=NOW)
        for history in (False, True):
            output = io.StringIO()
            args = ['read', identifier, '--path', str(self.path)] + (['--history'] if history else [])
            with patch('vault_notes._prompt', return_value=PHRASE), patch('vault_notes.sys.stdout', output):
                self.assertEqual(main(args), 0)
            self.assertIn('Current QA content', output.getvalue())
            self.assertEqual('Synthetic QA body' in output.getvalue(), history)

    def test_malformed_persisted_revision_sequence_is_rejected(self):
        self.add()
        document = self.store.read(PHRASE)
        document['notes'][0]['revisions'][0]['number'] = 2
        self.store.update(PHRASE, document, expected_revision=document['revision'])
        with self.assertRaises(VaultError):
            list_notes(self.store, PHRASE)

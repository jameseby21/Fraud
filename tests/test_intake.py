import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import intake


class IntakeTests(unittest.TestCase):
    def award(self, amount='10.29'):
        return {'generated_internal_id': 'CONT_AWD_EXAMPLE', 'Award ID': 'EXAMPLE',
                'Recipient Name': 'Example', 'Awarding Agency': 'Example agency', 'Award Amount': amount,
                'Start Date': '2025-01-01', 'End Date': None}

    def test_money_preserves_exact_cents_and_unlabeled_status(self):
        rows = intake.normalize_awards({'results': [self.award(Decimal('10000000000.29'))]})
        self.assertEqual(rows[0]['total_award_obligation_cents'], 1000000000029)
        self.assertEqual(rows[0]['fraud_label'], 'unlabeled')
        self.assertFalse(rows[0]['synthetic'])

    def test_bad_amounts_are_rejected(self):
        for value in ('NaN', 'Infinity', 'bad', '0.001'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                intake.normalize_awards({'results': [self.award(value)]})

    def test_missing_fields_duplicates_and_bad_dates_are_rejected(self):
        rows = [self.award(), self.award()]
        with self.assertRaises(ValueError):
            intake.normalize_awards({'results': rows})
        for field, value in [('Recipient Name', None), ('generated_internal_id', ''), ('Start Date', '2025-99-99')]:
            row = self.award()
            row[field] = value
            with self.assertRaises(ValueError):
                intake.normalize_awards({'results': [row]})
        for value in ({}, {'results': []}, {'results': 'not a list'}):
            with self.assertRaises(ValueError):
                intake.normalize_awards(value)

    def test_only_public_allowlisted_https_sources(self):
        intake.check_url(intake.SPENDING_URL)
        for url in ('http://www.justice.gov/page', 'https://127.0.0.1/x', 'https://www.justice.gov.evil.test/',
                    'https://user:secret@www.justice.gov/x', 'file:///secret', 'https://www.justice.gov:8080/x'):
            with self.assertRaises(ValueError):
                intake.check_url(url)

    def test_challenge_pages_and_invalid_documents_are_rejected(self):
        for content, kind in ((b'<html>triggerInterstitialChallenge</html>', 'text/html'),
                              (b'not pdf', 'application/pdf'), (b'{broken', 'application/json'),
                              (b'', 'text/html'), (b'anything', 'text/plain')):
            with self.assertRaises(ValueError):
                intake.validate_payload(content, kind)

    def test_failed_download_logged_without_fabricated_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with patch.object(intake, 'DATA', target), patch.object(intake, 'download', side_effect=OSError('403 blocked')):
                self.assertEqual(intake.fetch_sources('madoff'), 1)
            record = json.loads((target / 'intake_log.jsonl').read_text())
            self.assertEqual(record['status'], 'unavailable')
            self.assertNotIn('artifact', record)
            self.assertFalse((target / 'raw').exists())

    def test_committed_data_reproduces_offline(self):
        result = intake.verify()
        self.assertTrue(result['valid'])
        provenance = json.loads((intake.DATA / 'spending' / 'provenance.json').read_text())
        self.assertEqual(result['public_awards'], provenance['rows'])

    def test_curated_evidence_and_synthetic_observations_are_separate(self):
        files = intake.derived_files()
        evidence = [json.loads(line) for line in files['evidence.jsonl'].splitlines()]
        simulated = [json.loads(line) for line in files['synthetic_replays.jsonl'].splitlines()]
        self.assertEqual(len(evidence), 31)
        self.assertTrue(all(not row['synthetic'] for row in evidence))
        self.assertEqual(len(simulated), 78)
        self.assertTrue(all(row['synthetic'] for row in simulated))

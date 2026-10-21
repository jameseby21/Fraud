import csv
import hashlib
import io
import json
from pathlib import Path
import unittest

from learning_fixture import build_fixture, artifacts

ROOT = Path(__file__).resolve().parents[1]


class LearningFixtureTests(unittest.TestCase):
    def test_repeatable_and_source_sensitive(self):
        source = (ROOT / 'data/spending/awards.csv').read_bytes()
        self.assertEqual(build_fixture(source), build_fixture(source))
        self.assertNotEqual(build_fixture(source)[2]['source_sha256'],
                            build_fixture(source.replace(b'HUMANA', b'SAMPLE'))[2]['source_sha256'])

    def test_large_fictional_dataset_has_no_answer_leakage(self):
        rows, answers, manifest = build_fixture((ROOT / 'data/spending/awards.csv').read_bytes())
        self.assertGreaterEqual(len(rows), 5000)
        self.assertTrue(all(r['synthetic'] == 'True' for r in rows))
        self.assertTrue(all(r['supplier'].startswith('Practice supplier ') for r in rows))
        self.assertFalse({'fraud_label', 'scenario', 'answer', 'source_award_key'} & rows[0].keys())
        self.assertEqual(manifest['bootstrap_unit'], 'award obligation magnitude, sampled with replacement')
        self.assertEqual(len({r['transaction_id'] for r in rows}), len(rows))

    def test_planted_patterns_and_benign_counterexample_are_traceable(self):
        rows, answers, _ = build_fixture((ROOT / 'data/spending/awards.csv').read_bytes())
        indexed = {r['transaction_id']: r for r in rows}
        self.assertEqual({a['pattern'] for a in answers},
                         {'duplicate_invoice', 'threshold_split', 'amount_outlier', 'late_payment', 'benign_recurring'})
        for answer in answers:
            self.assertTrue(all(i in indexed for i in answer['transaction_ids']))
            self.assertTrue(answer['explanation'])
        duplicate = next(a for a in answers if a['pattern'] == 'duplicate_invoice')
        pair = [indexed[i] for i in duplicate['transaction_ids']]
        self.assertEqual(pair[0]['invoice_id'], pair[1]['invoice_id'])
        self.assertEqual(pair[0]['amount_cents'], pair[1]['amount_cents'])
        split = next(a for a in answers if a['pattern'] == 'threshold_split')
        self.assertTrue(all(int(indexed[i]['amount_cents']) < 1000000 for i in split['transaction_ids']))
        self.assertGreater(sum(int(indexed[i]['amount_cents']) for i in split['transaction_ids']), 1000000)
        self.assertEqual(next(a for a in answers if a['pattern'] == 'benign_recurring')['disposition'], 'benign_control')

    def test_committed_artifacts_reproduce_byte_for_byte(self):
        for relative, expected in artifacts(ROOT).items():
            self.assertEqual((ROOT / relative).read_bytes(), expected, relative)

    def test_empty_source_rejected(self):
        with self.assertRaises(ValueError):
            build_fixture(b'award_key,total_award_obligation_cents\n')

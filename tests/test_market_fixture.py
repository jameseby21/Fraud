import json
from pathlib import Path
import unittest

from market_fixture import (artifacts, build_case, load_public_reference,
                            open_interest_candidates, trade_volume_candidates)

ROOT = Path(__file__).resolve().parents[1]


class MarketFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = load_public_reference()
        cls.case = build_case(cls.reference)

    def test_public_reference_is_exact_small_and_traceable(self):
        self.assertEqual(len(self.reference['rows']), 15)
        self.assertEqual(self.reference['source_id'], 'cftc-tff-2022-09-13')
        self.assertEqual(self.reference['rows'][0]['open_interest_all'], 1376168)
        self.assertEqual(self.reference['rows'][0]['cftc_contract_market_code'], '020601')
        self.assertTrue(self.reference['sha256'])

    def test_large_background_and_fictional_identities_hide_two_group_signals(self):
        self.assertEqual(len(self.case['confirmations']), 8000)
        self.assertEqual(len(self.case['positions']), 4000)
        self.assertEqual(len(self.case['accounts']), 240)
        self.assertTrue(all(row['synthetic'] == 'True' for row in self.case['confirmations'] + self.case['positions']))
        self.assertFalse(any('Madoff' in account['account_name'] for account in self.case['accounts']))
        self.assertTrue(all(row['gross_cents'] == row['quantity'] * row['price_cents'] for row in self.case['confirmations']))
        self.assertTrue(all(row['cash_movement_cents'] == -row['gross_cents'] for row in self.case['confirmations']))

    def test_statement_lines_only_fail_when_compared_to_market_tape(self):
        candidates = trade_volume_candidates(self.case['confirmations'], self.case['market_context'])
        planted = [row for row in candidates if row['exceeds_market_volume']]
        self.assertEqual(len(planted), 1)
        self.assertLess(planted[0]['excess_ratio'], .02)
        self.assertGreater(planted[0]['claimed_quantity'], planted[0]['market_volume'])
        target_ids = set(self.case['answers'][0]['confirmation_ids'])
        target_rows = [row for row in self.case['confirmations'] if row['confirmation_id'] in target_ids]
        self.assertGreater(len(self.case['confirmations']) / len(target_rows), 100)
        self.assertTrue(all(row['quantity'] < planted[0]['market_volume'] * .04 for row in target_rows))

    def test_public_open_interest_proves_group_inconsistency_not_row_guilt(self):
        candidates = open_interest_candidates(self.case['positions'], self.reference['rows'])
        over = [row for row in candidates if row['exceeds_open_interest']]
        self.assertEqual(len(over), 1)
        self.assertEqual(over[0]['cftc_contract_market_code'], '020601')
        self.assertLess(over[0]['excess_ratio'], .02)
        self.assertNotIn('false_confirmation_ids', over[0])
        answer = next(item for item in self.case['answers'] if item['pattern'] == 'public_open_interest_capacity')
        self.assertIn('cannot identify which', answer['explanation'])

    def test_generated_market_files_reproduce(self):
        for path, payload in artifacts().items():
            self.assertEqual((ROOT / path).read_bytes(), payload, path)

    def test_invalid_market_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            trade_volume_candidates([], [])
        with self.assertRaises(ValueError):
            open_interest_candidates([], [])

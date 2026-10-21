import json
from pathlib import Path
import unittest
from forensic_fixture import build_case, artifacts, round_groups, digit_profile, distribution_comparison

ROOT=Path(__file__).resolve().parents[1]


class ForensicFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool=json.loads((ROOT/'data/library/amount_pool.json').read_text())
        cls.case=build_case(cls.pool)

    def test_repeatable_relational_and_plausible_names(self):
        self.assertEqual(self.case,build_case(self.pool))
        self.assertEqual(len(self.case['payments']),12000)
        self.assertEqual(sum(p['amount_cents'] for p in self.case['payments']),30341455858)
        entities={e['supplier_id']:e for e in self.case['entities']}
        self.assertEqual(len(entities),120)
        self.assertEqual(len({e['business_name'] for e in entities.values()}),120)
        self.assertTrue(all('Practice supplier' not in e['business_name'] and ' ' in e['contact_name'] for e in entities.values()))
        self.assertTrue(all(p['supplier_id'] in entities for p in self.case['payments']))
        self.assertEqual(len({p['transaction_id'] for p in self.case['payments']}),12000)
        self.assertFalse({'pattern','fraud_label','source_row'} & self.case['payments'][0].keys())

    def test_exact_source_values_have_verifiable_lineage(self):
        source={(r['source_id'],r['source_row']):r for r in self.pool['rows']}
        payments={p['transaction_id']:p for p in self.case['payments']}
        copied=[r for r in self.case['lineage'] if r['transformation']=='exact_value_reassigned']
        self.assertGreater(len(copied),11000)
        for r in copied:
            original=source[(r['source_id'],r['source_row'])]
            self.assertEqual(payments[r['transaction_id']]['amount_cents'],original['amount_cents'])
            self.assertEqual(r['source_sha256'],original['source_sha256'])

    def test_round_groups_hide_nonround_individual_values(self):
        found=round_groups(self.case['payments'])
        expected=next(a for a in self.case['answers'] if a['pattern']=='round_sum_groups')
        self.assertEqual(len(expected['groups']),12)
        positions={r['transaction_id']:i for i,r in enumerate(self.case['payments'])}
        self.assertGreater(min(positions[i] for ids in expected['groups'] for i in ids),1000)
        found_ids={tuple(sorted(g['transaction_ids'])) for g in found}
        for ids in expected['groups']:
            self.assertIn(tuple(sorted(ids)),found_ids)
            rows=[p for p in self.case['payments'] if p['transaction_id'] in ids]
            self.assertEqual(sum(p['amount_cents'] for p in rows),1000000)
            self.assertTrue(all(p['amount_cents']%100 for p in rows))

    def test_distribution_shift_is_descriptive_not_guilt_score(self):
        result=distribution_comparison(self.case['payments'])
        self.assertGreater(result['ks_distance'],0.15)
        self.assertNotIn('fraud_probability',result)
        self.assertIn('not',result['interpretation'])
        self.assertEqual(sum(digit_profile([10,25,99,0,-1])['counts']),3)
        with self.assertRaises(ValueError):
            distribution_comparison([])
        for invalid in (True,0.5,'123'):
            with self.assertRaises(ValueError):
                digit_profile([invalid])

    def test_as_of_view_excludes_unavailable_rows_and_answers(self):
        from forensic_fixture import public_case
        view=public_case('2024-02-01')
        self.assertTrue(all(r['available_on']<='2024-02-01' for r in view['payments']))
        self.assertLess(len(view['payments']),12000)
        self.assertNotIn('answers',view)
        self.assertNotIn('lineage',view)
        with self.assertRaises(ValueError):
            public_case('yesterday')

    def test_document_joins_and_bank_variance_are_deliberate(self):
        payments={p['transaction_id']:p for p in self.case['payments']}
        invoices={r['invoice_id'] for r in self.case['invoices']}
        self.assertTrue(all(p['invoice_id'] in invoices for p in payments.values()))
        mismatches=[r for r in self.case['bank_entries'] if -r['signed_amount_cents'] != payments[r['transaction_id']]['amount_cents']]
        self.assertEqual(len(mismatches),1)
        self.assertTrue(any(a['disposition']=='benign_control' for a in self.case['answers']))

    def test_committed_files_reproduce(self):
        for path,payload in artifacts().items():
            self.assertEqual((ROOT/path).read_bytes(),payload,path)

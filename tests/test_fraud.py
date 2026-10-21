import unittest
from fraud import analyze, fixtures, report


class DetectionTests(unittest.TestCase):
    def test_reproducible_and_traceable(self):
        a, b = report(), report()
        self.assertEqual(a, b)
        ids = {r['id'] for r in a['transactions']}
        self.assertEqual(len(ids), len(a['transactions']))
        self.assertTrue(all(set(x['evidence_ids']) <= ids for x in a['alerts']))

    def test_suspicious_patterns_and_benign_lookalike(self):
        r = report()
        self.assertEqual(r['evaluation']['true_positives'], 2)
        self.assertEqual(r['evaluation']['false_positives'], 1)
        self.assertEqual(r['evaluation']['false_negatives'], 2)
        self.assertNotIn('Ordinary-Shop', {a['entity'] for a in r['alerts']})

    def test_no_cycle_when_time_or_amount_breaks_pattern(self):
        rows, _ = fixtures()
        cycle = [dict(r) for r in rows if r['sender'].startswith('Settlement')]
        cycle[-1]['amount_cents'] = 100
        self.assertEqual(analyze(cycle), [])
        cycle[-1]['amount_cents'] = 100000
        cycle[-1]['timestamp'] = '2026-03-01T00:00:00+00:00'
        self.assertEqual(analyze(cycle), [])

    def test_empty_input(self):
        self.assertEqual(analyze([]), [])


if __name__ == '__main__':
    unittest.main()

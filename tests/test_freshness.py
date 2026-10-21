import unittest
from datetime import date

from freshness import assess_freshness, library_freshness


class FreshnessTests(unittest.TestCase):
    def test_publication_and_retrieval_have_independent_ages(self):
        report = assess_freshness('2009-06-29', '2026-10-21T04:47:10+00:00', date(2026, 10, 21))
        self.assertGreater(report['publication']['age_days'], 6000)
        self.assertEqual(report['retrieval']['age_days'], 0)
        self.assertEqual(report['retrieval']['status'], 'recent')
        self.assertIn('does not', report['interpretation'])

    def test_unknown_dates_are_not_inferred_from_each_other(self):
        a = assess_freshness(None, '2026-10-21T00:00:00Z', date(2026, 10, 21))
        b = assess_freshness('2009-06-29', None, date(2026, 10, 21))
        self.assertEqual(a['publication']['status'], 'unknown')
        self.assertIsNone(a['publication']['age_days'])
        self.assertEqual(b['retrieval']['status'], 'unknown')

    def test_stale_threshold_is_explicit_and_boundary_is_stable(self):
        recent = assess_freshness(None, '2026-09-21T00:00:00Z', date(2026, 10, 21), stale_after_days=30)
        stale = assess_freshness(None, '2026-09-20T00:00:00Z', date(2026, 10, 21), stale_after_days=30)
        self.assertEqual(recent['retrieval']['status'], 'recent')
        self.assertEqual(stale['retrieval']['status'], 'refresh_recommended')
        self.assertEqual(stale['stale_after_days'], 30)

    def test_invalid_and_future_dates_do_not_appear_recent(self):
        invalid = assess_freshness('nonsense', 'nonsense', date(2026, 10, 21))
        future = assess_freshness('2026-10-22', '2026-10-22T00:00:00Z', date(2026, 10, 21))
        self.assertEqual(invalid['publication']['status'], 'invalid')
        self.assertEqual(invalid['retrieval']['status'], 'invalid')
        self.assertEqual(future['publication']['status'], 'future_date')
        self.assertEqual(future['retrieval']['status'], 'future_date')
        self.assertIsNone(future['retrieval']['age_days'])

    def test_timestamp_uses_utc_day_and_requires_timezone(self):
        report = assess_freshness(None, '2026-10-20T23:30:00-05:00', date(2026, 10, 21))
        self.assertEqual(report['retrieval']['age_days'], 0)
        self.assertEqual(assess_freshness(None, '2026-10-21T12:00:00', date(2026, 10, 21))['retrieval']['status'], 'invalid')

    def test_bad_threshold_is_rejected(self):
        for threshold in (-1, True, '30'):
            with self.assertRaises(ValueError):
                assess_freshness(None, None, date(2026, 10, 21), stale_after_days=threshold)

    def test_failed_refresh_does_not_reset_last_successful_download(self):
        catalog = {'cases': [{'id': 'example', 'source': {'published_on': None}}]}
        attempts = [{'case_id': 'example', 'status': 'downloaded', 'retrieved_at': '2026-01-01T00:00:00Z'},
                    {'case_id': 'example', 'status': 'unavailable', 'retrieved_at': '2026-10-21T00:00:00Z'}]
        report = library_freshness(catalog, attempts, None, date(2026, 10, 21))
        self.assertEqual(report['cases']['example']['retrieval']['status'], 'refresh_recommended')
        self.assertEqual(report['cases']['example']['retrieval']['value'], '2026-01-01T00:00:00Z')
        self.assertEqual(report['awards']['publication']['status'], 'unknown')

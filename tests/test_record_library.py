import json
from pathlib import Path
import tempfile
import unittest
from record_library import ingest, verify_library, check_source, normalize_amounts


class RecordLibraryTests(unittest.TestCase):
    def source(self):
        return dict(id='example', case_id='madoff', url='https://www.justice.gov/example',
                    record_type='official_case_report', reuse_basis='DOJ public domain default',
                    reuse_url='https://www.justice.gov/legalpolicies', title='Example', publication_date=None)

    def test_append_only_versions_idempotency_and_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = ingest(self.source(), b'<html>first government record</html>', 'text/html', root)
            again = ingest(self.source(), b'<html>first government record</html>', 'text/html', root)
            second = ingest(self.source(), b'<html>corrected record</html>', 'text/html', root)
            self.assertEqual(first['revision'], again['revision'])
            self.assertEqual(second['revision'], 2)
            self.assertEqual(second['supersedes'], first['sha256'])
            self.assertEqual(verify_library(root)['revisions'], 2)
            (root / first['artifact']).write_bytes(b'tampered')
            with self.assertRaises(ValueError):
                verify_library(root)

    def test_unknown_hosts_missing_reuse_and_path_ids_rejected(self):
        for changes in ({'url':'https://example.com/a'}, {'id':'../vault'}, {'reuse_basis':''}, {'record_type':'proven_fraud'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                check_source(dict(self.source(), **changes))

    def test_same_bytes_different_sources_retain_distinct_lineage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            a = ingest(self.source(), b'{}', 'application/json', root)
            b = ingest(dict(self.source(), id='other'), b'{}', 'application/json', root)
            self.assertEqual(a['artifact'], b['artifact'])
            self.assertEqual(verify_library(root)['sources'], 2)

    def test_money_preserves_decimal_values_without_float_rounding(self):
        payload = {'results':[{'Award ID':'A', 'Award Amount':'123.45'}, {'Award ID':'B', 'Award Amount':'900.00'}]}
        self.assertEqual([r['amount_cents'] for r in normalize_amounts(payload)], [12345,90000])
        with self.assertRaises(ValueError):
            normalize_amounts({'results':[{'Award ID':'C','Award Amount':'1.001'}]})

    def test_same_endpoint_with_different_request_is_not_imported(self):
        from record_library import reuse_existing
        source=dict(self.source(),request={'filters':{'new':'query'}})
        self.assertFalse(reuse_existing(source,[dict(requested_url=source['url'],status='downloaded',artifact='missing')]))

    def test_download_failure_recorded_without_fake_success(self):
        from record_library import refresh
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory, patch('record_library.fetch', side_effect=OSError('offline')):
            root = Path(directory)
            self.assertFalse(refresh(self.source(), root))
            attempt = json.loads((root/'data/library/attempts.jsonl').read_text())
            self.assertEqual(attempt['status'], 'unavailable')
            self.assertFalse((root/'data/library/revisions.jsonl').exists())

    def test_derived_values_cannot_silently_drift_from_raw_source(self):
        from record_library import rebuild, encode
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = dict(self.source(),id='learning-award-values',record_type='financial_records')
            ingest(source, encode({'results':[{'Award ID':'A','Award Amount':'123.45'}]}), 'application/json',root)
            (root/'data/library/sources.json').write_bytes(encode({'schema_version':1,'sources':[source]}))
            rebuild(root)
            self.assertTrue(verify_library(root)['valid'])
            (root/'data/library/amount_pool.json').write_text('{}')
            with self.assertRaises(ValueError):
                verify_library(root)

    def test_cftc_public_host_and_market_reference_type_are_allowlisted(self):
        source = dict(self.source(), id='cftc-sample', case_id=None,
                      url='https://publicreporting.cftc.gov/resource/yw9f-hn96.json?%24limit=1',
                      record_type='market_reference', reuse_basis='CFTC public reporting data',
                      reuse_url='https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm')
        check_source(source)

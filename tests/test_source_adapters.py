import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

import record_library as library


class SourceAdapterTests(unittest.TestCase):
    def test_existing_identical_source_can_learn_http_validators_without_new_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=dict(self.source(),adapter='direct')
            library.ingest(source,b'pitch,speed\n1,90\n','text/csv',root)
            def response(request):
                request['_response_validators']={'etag':'"learned"'}
                return b'pitch,speed\n1,90\n','text/csv'
            with patch('record_library.fetch',side_effect=response):self.assertTrue(library.refresh(source,root))
            with patch('record_library.fetch',side_effect=HTTPError(source['url'],304,'Not Modified',{},None)) as fetch:
                self.assertTrue(library.refresh(source,root))
                self.assertEqual(fetch.call_args.args[0]['_conditional_headers']['If-None-Match'],'"learned"')
            self.assertEqual(library.verify_library(root)['revisions'],1)

    def test_direct_sources_revalidate_with_http_validators(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            source=dict(self.source(),adapter='direct',_response_validators={'etag':'"revision-one"'})
            library.ingest(source,b'pitch,speed\n1,90\n','text/csv',root)
            with patch('record_library.fetch',side_effect=HTTPError(source['url'],304,'Not Modified',{},None)) as fetch:
                self.assertTrue(library.refresh(source,root))
                self.assertEqual(fetch.call_args.args[0]['_conditional_headers']['If-None-Match'],'"revision-one"')
            self.assertEqual(library.verify_library(root)['revisions'],1)
            self.assertEqual(json.loads((root/'data/library/attempts.jsonl').read_text())['status'],'unchanged')

    def source(self):
        return dict(id='sports-sample',case_id=None,title='Example',record_type='sports_records',
            url='https://data.mendeley.com/public-files/example',publication_date='2024-09-16',
            reuse_basis='CC BY 4.0, attributed research data',reuse_url='https://creativecommons.org/licenses/by/4.0/',
            adapter='mendeley-file-list',metadata_url='https://data.mendeley.com/public-api/example',file_id='csv-file',
            csv_schema={'required_columns':['pitch','speed'],'row_count':1})

    def test_csv_source_schema_hash_and_deduplication(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); source=self.source()
            first=library.ingest(source,b'pitch,speed\n1,90\n','text/csv',root)
            second=library.ingest(source,b'pitch,speed\n1,90\n','text/csv',root)
            self.assertEqual(first,second)
            self.assertEqual(library.verify_library(root)['revisions'],1)
            for data in (b'<html>blocked</html>',b'pitch,wrong\n1,90\n',b'pitch,speed\n'):
                with self.assertRaises(ValueError):library.ingest(source,data,'text/csv',root)

    def test_incremental_metadata_skips_unchanged_downloads_but_verifies_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); source=self.source()
            record=library.ingest(source,b'pitch,speed\n1,90\n','text/csv',root)
            metadata=[{'id':'csv-file','content_details':{'sha256_hash':record['sha256']}}]
            with patch('record_library.fetch_metadata',return_value=metadata),patch('record_library.fetch') as fetch:
                self.assertTrue(library.refresh(source,root))
                fetch.assert_not_called()
                attempt=json.loads((root/'data/library/attempts.jsonl').read_text().splitlines()[-1])
                self.assertEqual(attempt['status'],'unchanged')
            (root/record['artifact']).write_bytes(b'corrupted')
            with patch('record_library.fetch_metadata',return_value=metadata):
                self.assertFalse(library.refresh(source,root))

    def test_changed_source_appends_revision_and_pinned_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); source=self.source()
            first=library.ingest(source,b'pitch,speed\n1,90\n','text/csv',root)
            second=library.ingest(source,b'pitch,speed\n1,91\n','text/csv',root)
            self.assertEqual(second['supersedes'],first['sha256'])
            self.assertEqual(second['revision'],2)
            with self.assertRaises(ValueError):
                library.ingest(dict(source,expected_sha256=first['sha256']),b'pitch,speed\n1,91\n','text/csv',root)
            self.assertEqual(library.verify_library(root)['revisions'],2)

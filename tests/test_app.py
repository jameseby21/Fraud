import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from app import Handler


class QuietHandler(Handler):
    def log_message(self, *args):
        pass


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, path):
        return urllib.request.urlopen(self.base+path, timeout=3)

    def post_json(self, path, payload):
        body = json.dumps(payload).encode()
        request = urllib.request.Request(self.base+path, data=body, method='POST',
                                         headers={'Content-Type': 'application/json'})
        return urllib.request.urlopen(request, timeout=3)

    def test_pages_and_assets_serve(self):
        for path in ('/', '/library', '/library.js', '/library.css'):
            with self.subTest(path=path), self.request(path) as r:
                self.assertEqual(r.status, 200)
                self.assertGreater(len(r.read()), 100)

    def test_catalog_and_real_data(self):
        with self.request('/api/catalog') as r:
            self.assertEqual(len(json.load(r)['cases']), 25)
        with self.request('/api/data') as r:
            data = json.load(r)
            self.assertGreater(len(data['awards']), 0)
            self.assertEqual(len(data['awards']), data['provenance']['rows'])

    def test_freshness_separates_source_clocks(self):
        with self.request('/api/data') as r:
            report = json.load(r)['freshness']
            self.assertIn('retrieval', report['awards'])
            self.assertEqual(report['cases']['adelphia']['publication']['status'], 'unknown')
            self.assertIn('age_days', report['cases']['madoff']['retrieval'])

    def test_replay_and_download(self):
        with self.request('/api/replay?case=madoff&step=1') as r:
            self.assertEqual(json.load(r)['trace']['result'], 'no_rule_trigger')
        with self.request('/api/download?name=awards') as r:
            self.assertIn('attachment', r.headers['Content-Disposition'])
            self.assertIn(b'total_award_obligation_cents', r.read())
        with self.request('/api/source?case=madoff') as r:
            self.assertIn('attachment', r.headers['Content-Disposition'])
            self.assertGreater(len(r.read()), 1000)

    def test_public_data_quality_has_traceable_json_and_download(self):
        with self.request('/api/quality') as r:
            report = json.load(r)
            self.assertGreater(report['row_count'], 0)
            self.assertIn('input_sha256', report)
            self.assertIn('source_sha256', report)
        with self.request('/api/quality?download=1') as r:
            self.assertIn('attachment', r.headers['Content-Disposition'])
            self.assertEqual(json.load(r), report)

    def test_bad_inputs_and_traversal_are_rejected(self):
        for path, status in (('/api/replay?case=madoff&step=99', 400),
                             ('/api/replay?case=uber-one&step=3', 400),
                             ('/api/replay?case=madoff&mode=public&as_of=nope', 400),
                             ('/api/replay?case=unknown&step=0', 404),
                             ('/api/download?name=../../app.py', 404), ('/api/source?case=../../app.py', 404), ('/../app.py', 404)):
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                self.request(path)
            self.assertEqual(error.exception.code, status)

    def test_web_server_has_no_private_vault_access(self):
        for path in ('/api/vault', '/vault', '/api/download?name=vault', '/data/private/records.fvault'):
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                self.request(path)
            self.assertEqual(error.exception.code, 404)

    def test_course_pages_and_allowlisted_material(self):
        with self.request('/learn') as r:
            self.assertIn(b'Data analysis studio', r.read())
        with self.request('/api/learning/catalog') as r:
            self.assertEqual(len(json.load(r)['courses']), 3)
        with self.request('/api/learning/lesson?course=payment-lab&lesson=orientation') as r:
            self.assertIn('Question', json.load(r)['markdown'])
        for path in ('/api/learning/chart?name=bar', '/api/learning/download?name=dataset',
                     '/api/learning/download?name=notebook&course=payment-lab&lesson=quality',
                     '/api/learning/download?name=r', '/api/learning/download?name=powerbi'):
            with self.request(path) as r:
                self.assertEqual(r.status, 200)
        for path in ('/api/learning/download?name=../../vault.py',
                     '/api/learning/lesson?course=payment-lab&lesson=../../vault',
                     '/api/learning/chart?name=unknown'):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.request(path)
            self.assertEqual(error.exception.code, 404)

    def test_glossary_and_quiz_interactions(self):
        with self.request('/api/learning/glossary') as response:
            glossary = json.load(response)
            self.assertGreaterEqual(len(glossary['terms']), 30)
            self.assertTrue(any(term['id'] == 'statement' for term in glossary['terms']))
        with self.post_json('/api/learning/quiz', {'quiz_id': 'operations-summaries-try-it', 'answer': '2258.49'}) as response:
            result = json.load(response)
            self.assertFalse(result['correct'])
            self.assertIn('filter', result['suggestion'].lower())
        with self.post_json('/api/learning/quiz', {'quiz_id': 'operations-summaries-try-it', 'answer': '2203.76'}) as response:
            self.assertTrue(json.load(response)['correct'])
        for payload in ({'quiz_id': '../../vault', 'answer': 'x'}, {'quiz_id': 'operations-summaries-try-it', 'answer': ['x']}):
            with self.subTest(payload=payload), self.assertRaises(urllib.error.HTTPError) as error:
                self.post_json('/api/learning/quiz', payload)
            self.assertIn(error.exception.code, (400, 404))

    def test_pasted_course_url_with_trailing_comma_redirects(self):
        for path in ('/learn,', '/learn%2C', '/learn/'):
            with self.request(path) as response:
                self.assertEqual(response.geturl(), self.base + '/learn')
                self.assertIn(b'Data analysis studio', response.read())

    def test_real_record_library_and_safe_downloads(self):
        with self.request('/records') as response:
            self.assertIn(b'Public record library',response.read())
        with self.request('/api/records') as response:
            records=json.load(response)['sources']
            self.assertGreater(len(records),20)
        with self.request('/api/record?source=madoff-peter-information') as response:
            self.assertTrue(response.read().startswith(b'%PDF-'))
        with self.assertRaises(urllib.error.HTTPError):
            self.request('/api/record?source=../../vault.py')

    def test_forensic_course_uses_its_own_dataset_and_asof_gate(self):
        with self.request('/api/learning/lesson?course=forensic-practicum&lesson=round-sums') as response:
            doc=json.load(response)
            self.assertEqual(doc['dataset'],'forensic-v2')
            self.assertIn('forensic',doc['tracks']['r'])
        with self.request('/api/forensic?as_of=2024-02-01') as response:
            data=json.load(response)
            self.assertTrue(all(r['available_on']<='2024-02-01' for r in data['payments']))
            self.assertNotIn('answers',data)
        with self.request('/api/learning/summary?dataset=forensic-v2') as response:
            self.assertEqual(json.load(response)['row_count'],12000)
        with self.request('/api/learning/download?name=forensic-payments') as response:
            self.assertIn(b'supplier_id',response.read())

    def test_market_context_lessons_and_downloads(self):
        for lesson, marker in (('statement-capacity', 'market volume'), ('public-corroboration', 'cftc')):
            with self.request('/api/learning/lesson?course=forensic-practicum&lesson='+lesson) as response:
                doc = json.load(response)
                self.assertEqual(len(doc['quizzes']), 5)
                self.assertIn(marker, doc['markdown'].lower())
        for name, marker in (('market-confirmations', b'confirmation_id'),
                             ('market-positions', b'position_id'),
                             ('market-context', b'market_volume'),
                             ('market-reference', b'open_interest_all')):
            with self.request('/api/learning/download?name='+name) as response:
                self.assertIn(marker, response.read())

    def test_madoff_catalog_uses_accessible_doj_landing_page(self):
        with self.request('/api/catalog') as response:
            case = next(item for item in json.load(response)['cases'] if item['id'] == 'madoff')
        self.assertEqual(case['source']['publisher'], 'DOJ')
        self.assertIn('/united-states-v-bernard-l-madoff-and-related-cases', case['source']['url'])
        self.assertNotIn('archives.fbi.gov', case['source']['url'])

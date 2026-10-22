import json
from pathlib import Path
import subprocess
import sys
import unittest
from learning import (load_catalog, lesson_document, render_markdown, analyze,
                      render_chart, load_glossary, glossary_markdown,
                      evaluate_quiz, load_common_errors)

ROOT = Path(__file__).resolve().parents[1]


class LearningTests(unittest.TestCase):
    def test_glossary_is_valid_and_documentation_is_generated_from_it(self):
        glossary = load_glossary()
        self.assertGreaterEqual(len(glossary['terms']), 30)
        ids = [term['id'] for term in glossary['terms']]
        self.assertEqual(len(ids), len(set(ids)))
        for term in glossary['terms']:
            self.assertTrue({'id', 'term', 'aliases', 'definition', 'context', 'implications'} <= set(term))
            self.assertTrue(all(term[field].strip() for field in ('term', 'definition', 'context', 'implications')))
        self.assertEqual((ROOT / 'docs' / 'glossary.md').read_text(encoding='utf-8'), glossary_markdown(glossary))

    def test_every_lesson_section_has_a_quiz_without_publishing_answers(self):
        expected_sections = {'Question', 'Try it', 'Check your work', 'Debugging', 'Reflection'}
        quiz_ids = []
        for course in load_catalog()['courses']:
            for lesson in course['lessons']:
                doc = lesson_document(course['id'], lesson['id'])
                self.assertEqual({quiz['section'] for quiz in doc['quizzes']}, expected_sections)
                self.assertEqual(len(doc['quizzes']), 5)
                for quiz in doc['quizzes']:
                    quiz_ids.append(quiz['id'])
                    self.assertNotIn('answer', quiz)
                    self.assertNotIn('tolerance', quiz)
        self.assertEqual(len(quiz_ids), len(set(quiz_ids)))

    def test_quiz_feedback_recognizes_filter_and_unit_errors(self):
        correct = evaluate_quiz('operations-summaries-try-it', '2203.76')
        self.assertTrue(correct['correct'])
        filtered = evaluate_quiz('operations-summaries-try-it', '2258.49')
        self.assertFalse(filtered['correct'])
        self.assertEqual(filtered['suggestion_id'], 'overall-instead-of-filtered-average')
        units = evaluate_quiz('operations-summaries-try-it', '220375.95')
        self.assertFalse(units['correct'])
        self.assertEqual(units['suggestion_id'], 'cents-instead-of-dollars')
        errors = load_common_errors()['errors']
        self.assertGreaterEqual(len(errors), 6)
        self.assertEqual(len({item['id'] for item in errors}), len(errors))
        with self.assertRaises(KeyError):
            evaluate_quiz('../../vault', 'anything')

    def test_catalog_is_modular_and_all_lessons_have_course_material(self):
        catalog = load_catalog()
        self.assertGreaterEqual(len(catalog['courses']), 2)
        self.assertTrue(any(c['topic'] != 'fraud' for c in catalog['courses']))
        ids = []
        for course in catalog['courses']:
            for lesson in course['lessons']:
                ids.append(lesson['id'])
                doc = lesson_document(course['id'], lesson['id'])
                for heading in ('## Question', '## Try it', '## Check your work', '## Debugging', '## Reflection'):
                    self.assertIn(heading, doc['markdown'])
                self.assertEqual(set(doc['tracks']), {'python', 'r', 'powerbi', 'excel'} if course['topic']=='sports' else {'python', 'r', 'powerbi'})
        self.assertEqual(len(ids), len(set(ids)))

    def test_routes_are_allowlisted(self):
        for course, lesson in [('../vault', 'init'), ('payment-lab', '../../vault'), ('missing', 'missing')]:
            with self.assertRaises(KeyError):
                lesson_document(course, lesson)

    def test_markdown_escapes_html_and_unsafe_links(self):
        html = render_markdown('# Test\n\n<script>alert(1)</script>\n\n[x](javascript:alert(1))\n\n```python\nprint("<unsafe>")\n```')
        self.assertNotIn('<script>', html)
        self.assertNotIn('href="javascript:', html)
        self.assertIn('<pre><code', html)

    def test_track_tables_render_with_headers_and_escaped_cells(self):
        rendered = render_markdown('| Tool | Check |\n| --- | --- |\n| R | <script> |\n')
        self.assertIn('<table>', rendered)
        self.assertIn('<th scope="col">Tool</th>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)

    def test_analysis_known_patterns_and_totals(self):
        result = analyze()
        self.assertEqual(result['row_count'], 6000)
        self.assertEqual(result['total_cents'], 1355092995)
        self.assertEqual(result['duplicate_groups'][0]['transaction_ids'], ['TX-000001', 'TX-000002'])
        self.assertEqual(len(result['supplier_days_over_threshold']), 5)
        self.assertEqual(sum(g['transaction_ids'] == ['TX-000003', 'TX-000004', 'TX-000005'] for g in result['supplier_days_over_threshold']), 1)
        self.assertEqual(result['late_payments'], ['TX-000007'])
        self.assertEqual(sum(r['count'] for r in result['histogram']), 6000)
        self.assertEqual(sum(r['amount_cents'] for r in result['monthly']), result['total_cents'])

    def test_chart_family_accessible_and_unknown_rejected(self):
        for name in ('bar', 'line', 'histogram', 'scatter', 'box', 'heatmap', 'pareto'):
            svg = render_chart(name)
            self.assertIn('<title id=', svg)
            self.assertIn('<desc id=', svg)
            self.assertIn('role="img"', svg)
        with self.assertRaises(KeyError):
            render_chart('../vault')

    def test_notebooks_are_clean_executable_lessons(self):
        for path in sorted((ROOT / 'courses').rglob('*.ipynb')):
            notebook = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(notebook['nbformat'], 4)
            namespace = {'__name__': '__course_test__'}
            for cell in notebook['cells']:
                if cell['cell_type'] == 'code':
                    self.assertEqual(cell['outputs'], [])
                    self.assertIsNone(cell['execution_count'])
                    exec(compile(''.join(cell['source']), str(path), 'exec'), namespace)
        self.assertGreaterEqual(len(list((ROOT / 'courses').rglob('*.ipynb'))), 8)

    def test_historical_guides_match_the_reviewed_catalog(self):
        from scripts.build_case_guides import artifacts
        expected=artifacts()
        self.assertEqual(len(expected),27)
        for relative,payload in expected.items():
            self.assertEqual((ROOT/relative).read_bytes(),payload)

import json
from pathlib import Path
import unittest

import baseball

ROOT = Path(__file__).resolve().parents[1]


class BaseballTests(unittest.TestCase):
    def test_fixture_grain_background_and_consistency(self):
        rows = baseball.build_rows()
        self.assertEqual(len(rows), 3600)
        self.assertEqual(len({r['pitch_id'] for r in rows}), 3600)
        self.assertEqual(len({r['pitcher'] for r in rows}), 6)
        self.assertTrue(all(r['synthetic'] for r in rows))
        self.assertTrue(all(not r['whiff'] or r['swing'] for r in rows))
        self.assertTrue(all(not r['in_play'] or r['swing'] and not r['whiff'] for r in rows))
        self.assertTrue(all((r['exit_speed_mph'] is not None) == bool(r['in_play']) for r in rows))
        self.assertTrue(all(1 <= r['inning'] <= 7 for r in rows))

    def test_planted_mix_velocity_and_batter_patterns_have_controls(self):
        rows = baseball.build_rows()
        summary = baseball.summarize(rows)
        self.assertEqual(summary['row_count'], 3600)
        mixes = {(r['pitcher'],r['period'],r['pitch_type']):r for r in summary['pitch_mix']}
        self.assertEqual(mixes['Rowan Ellis','early','FF']['count'], 180)
        self.assertEqual(mixes['Rowan Ellis','late','FF']['count'], 120)
        self.assertEqual(mixes['Theo Bennett','early','FF']['count'], mixes['Theo Bennett','late','FF']['count'])
        fastballs = [r for r in rows if r['pitcher'] == 'Mateo Brooks' and r['pitch_type'] == 'FF']
        early = [r['speed_mph'] for r in fastballs if r['inning'] <= 2]
        late = [r['speed_mph'] for r in fastballs if r['inning'] >= 6]
        self.assertGreater(sum(early)/len(early) - sum(late)/len(late), 1.5)
        hitter = [r for r in summary['contact'] if r['batter'] == 'Casey Morgan']
        by_period = {r['period']:r for r in hitter}
        self.assertGreater(by_period['late']['mean_exit_speed_mph'] - by_period['early']['mean_exit_speed_mph'], 3)

    def test_denominators_empty_groups_and_filters(self):
        subset = baseball.select(baseball.build_rows(), pitcher='Rowan Ellis', pitch_type='SL', batter='Casey Morgan')
        self.assertTrue(subset)
        self.assertTrue(all(r['pitcher']=='Rowan Ellis' and r['pitch_type']=='SL' and r['batter']=='Casey Morgan' for r in subset))
        self.assertEqual(baseball.summarize([])['row_count'], 0)
        self.assertIsNone(baseball.rate(0,0))
        with self.assertRaises(ValueError):
            baseball.select(baseball.build_rows(), pitcher='../../vault')
        for group in baseball.summarize(baseball.build_rows())['whiff_by_zone']:
            self.assertAlmostEqual(group['whiff_rate'], group['whiffs']/group['swings'] if group['swings'] else None)

    def test_all_chart_families_have_sports_units_and_accessible_titles(self):
        for name in baseball.CHARTS:
            svg = baseball.render_chart(name, pitcher='Rowan Ellis')
            self.assertIn('role="img"', svg)
            self.assertIn('<title', svg)
            self.assertNotIn('USD', svg)
        with self.assertRaises(KeyError):
            baseball.render_chart('../../vault')

    def test_committed_artifacts_reproduce(self):
        for path, payload in baseball.artifacts().items():
            self.assertEqual((ROOT/path).read_bytes(),payload,path)

    def test_course_reuses_generic_lesson_and_quiz_contract(self):
        import learning
        course = next(c for c in learning.load_catalog()['courses'] if c['id']=='baseball-lab')
        self.assertEqual(len(course['lessons']),5)
        for lesson in course['lessons']:
            doc = learning.lesson_document('baseball-lab',lesson['id'])
            self.assertEqual(doc['dataset'],'baseball-v1')
            self.assertEqual(len(doc['quizzes']),5)
            self.assertIn('baseball',doc['tracks']['r'])
        wrong = learning.evaluate_quiz('baseball-lab-whiff-zones-try-it','0.5')
        self.assertFalse(wrong['correct'])
        self.assertIn('swings',wrong['suggestion'].lower())
        self.assertTrue(learning.evaluate_quiz('baseball-lab-whiff-zones-try-it','50')['correct'])

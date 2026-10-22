from pathlib import Path
import unittest

import baseball_real

ROOT=Path(__file__).resolve().parents[1]


class RealBaseballTests(unittest.TestCase):
    def test_real_source_counts_values_and_whiff_denominator(self):
        rows=baseball_real.read_rows()
        self.assertEqual(len(rows),3344)
        self.assertEqual(rows[0]['RelSpeed'],'80.06796')
        summary=baseball_real.summarize(rows)
        self.assertEqual(summary['pitch_types']['Fastball'],1745)
        self.assertEqual(summary['whiffs'],381)
        self.assertEqual(summary['swings'],1432)
        self.assertAlmostEqual(summary['whiff_rate'],381/1432)
        self.assertFalse(summary['synthetic'])
        self.assertEqual(summary['anonymous_pitchers'],32)
        self.assertEqual(summary['anonymous_batters'],50)
        self.assertEqual(summary['measured_in_play_exit_speeds'],505)

    def test_source_hash_and_derived_artifacts(self):
        self.assertTrue(baseball_real.verify()['valid'])
        for path,content in baseball_real.artifacts().items():
            self.assertEqual((ROOT/path).read_bytes(),content)

    def test_filters_empty_groups_and_missing_contact_are_honest(self):
        rows=baseball_real.read_rows()
        subset=baseball_real.select(rows,pitcher='1000036206',pitch_type='Slider')
        self.assertTrue(subset)
        self.assertTrue(all(r['PitcherId']=='1000036206' and r['TaggedPitchType']=='Slider' for r in subset))
        self.assertIsNone(baseball_real.summarize([])['whiff_rate'])
        with self.assertRaises(ValueError):baseball_real.select(rows,pitcher='unknown')
        self.assertEqual(baseball_real.number(''),None)

    def test_real_charts_and_course_contract(self):
        import learning
        for chart in baseball_real.CHARTS:
            self.assertIn('role="img"',baseball_real.render_chart(chart,pitcher='1000036206'))
        doc=learning.lesson_document('baseball-fieldwork','real-arsenal')
        self.assertEqual(doc['dataset'],'baseball-real-v1')
        self.assertEqual(len(doc['quizzes']),5)
        self.assertIn('excel',doc['tracks'])

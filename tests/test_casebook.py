import copy
import unittest
from datetime import date, timedelta
from unittest.mock import patch

from casebook import MODELS, get_case, load_catalog, mechanism_replay, public_replay, source_events, validate_catalog


class CasebookTests(unittest.TestCase):
    def test_twenty_distinct_documented_cases_and_five_questions(self):
        result = validate_catalog()
        self.assertEqual(result['historical'], 20)
        self.assertEqual(result['modern'], 5)
        cases = load_catalog()['cases']
        self.assertEqual(len({c['source']['url'] for c in cases}), 25)

    def test_all_historical_replays_are_reproducible_and_point_in_time(self):
        for c in load_catalog()['cases']:
            if c['kind'] != 'historical':
                continue
            with self.subTest(case=c['id']):
                for step in range(4):
                    r = mechanism_replay(c['id'], step)
                    self.assertEqual(r, mechanism_replay(c['id'], step))
                    self.assertEqual(len(r['observations']), step)
                    self.assertTrue(all(o['available_step'] <= step and o['synthetic'] for o in r['observations']))
                    self.assertTrue(set(r['trace']['evidence_ids']) <= {o['id'] for o in r['observations']})
                    self.assertNotIn('outcome', r)
                self.assertEqual(mechanism_replay(c['id'], 0)['trace']['result'], 'insufficient_data')
                self.assertEqual(mechanism_replay(c['id'], 1)['trace']['result'], 'no_rule_trigger')
                self.assertEqual(mechanism_replay(c['id'], 3)['trace']['result'], 'review')

    def test_later_observation_cannot_change_earlier_replay(self):
        before = mechanism_replay('madoff', 1)
        changed = copy.deepcopy(MODELS)
        profile = list(changed['balance_confirmation'])
        profile[4][-1] = (999999, 0)
        changed['balance_confirmation'] = tuple(profile)
        with patch.dict(MODELS, changed):
            self.assertEqual(before, mechanism_replay('madoff', 1))

    def test_retrospective_source_never_leaks_before_publication(self):
        for c in load_catalog()['cases']:
            available = source_events(c)[0]['available_on']
            prior = (date.fromisoformat(available)-timedelta(days=1)).isoformat()
            before = public_replay(c['id'], prior)
            self.assertEqual(before['events'], [])
            self.assertIsNone(before['outcome'])
            self.assertEqual(len(public_replay(c['id'], available)['events']), 1)

    def test_event_date_and_availability_date_are_distinct(self):
        event = source_events(get_case('tyco'))[0]
        self.assertLess(event['occurred_on'], event['available_on'])
        self.assertIsNone(public_replay('tyco', '2005-06-17')['outcome'])

    def test_unknown_publication_dates_are_conservatively_gated(self):
        c = get_case('adelphia')
        self.assertIsNone(c['source']['published_on'])
        self.assertEqual(source_events(c)[0]['available_on'], load_catalog()['reviewed_on'])

    def test_modern_entries_cannot_have_fabricated_incriminating_replay(self):
        for c in load_catalog()['cases']:
            if c['kind'] == 'modern':
                with self.assertRaises(ValueError):
                    mechanism_replay(c['id'], 3)
                self.assertIsNone(c['outcome'])

    def test_invalid_steps_dates_and_ids(self):
        for step in (-1, 4, True, '1'):
            with self.assertRaises(ValueError):
                mechanism_replay('madoff', step)
        with self.assertRaises(ValueError):
            public_replay('madoff', 'not-a-date')
        with self.assertRaises(KeyError):
            get_case('../../outside')

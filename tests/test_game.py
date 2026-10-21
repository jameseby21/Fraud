import json
import unittest
from pathlib import Path

from game_fixture import artifacts, build_game, public_case, score_case, verify

ROOT = Path(__file__).resolve().parents[1]


class GameFixtureTests(unittest.TestCase):
    def test_player_candidates_do_not_leak_scoring_weights(self):
        for case_id in build_game()['players']:
            self.assertTrue(all(set(candidate) == {'id', 'label'}
                                for candidate in public_case(case_id)['candidates']))

    def test_no_supported_findings_earn_no_time_points(self):
        for selections in ([], ['C-ROUND-03']):
            result = score_case('round-total', selections, 0)
            self.assertEqual(result['speed_bonus'], 0)
            self.assertEqual(result['points'], 0)

    def test_expense_exposure_matches_cents_in_the_ledger(self):
        game = build_game()
        total = sum(row['amount_or_quantity'] for row in game['players']['number-pattern']['ledger']
                    if row['review_group'] == 'TEAM-WEST')
        self.assertEqual(total, 70110)
        self.assertEqual(game['answers']['number-pattern']['exposure'], '701.10 fictional USD')

    def test_four_small_fictional_cases_have_printable_player_material(self):
        game = build_game()
        self.assertEqual(len(game['catalog']['cases']), 4)
        for case in game['catalog']['cases']:
            with self.subTest(case=case['id']):
                player = public_case(case['id'], game)
                self.assertLessEqual(len(player['ledger']), 18)
                self.assertGreaterEqual(len(player['ledger']), 12)
                self.assertGreaterEqual(len(player['candidates']), 3)
                self.assertNotIn('answers', json.dumps(player).lower())
                self.assertTrue(all(row['identity_status'] == 'fictional' for row in player['ledger']))
                answer = game['answers'][case['id']]
                self.assertLessEqual(len(answer['target_ids']), len(player['ledger']) // 4)

    def test_scoring_rewards_true_findings_and_penalizes_unsupported_calls(self):
        game = build_game()
        case_id = 'round-total'
        targets = game['answers'][case_id]['target_ids']
        perfect = score_case(case_id, targets, 60, game)
        noisy = score_case(case_id, targets + ['C-ROUND-03'], 60, game)
        missed = score_case(case_id, [], 60, game)
        self.assertEqual(perfect['true_positives'], len(targets))
        self.assertEqual(perfect['false_positives'], 0)
        self.assertGreater(perfect['points'], noisy['points'])
        self.assertGreater(noisy['points'], missed['points'])
        self.assertEqual(perfect, score_case(case_id, targets, 60, game))

    def test_invalid_case_score_and_selection_are_rejected(self):
        with self.assertRaises(KeyError):
            public_case('../../vault')
        with self.assertRaises(ValueError):
            score_case('round-total', ['not-a-candidate'], 1)
        with self.assertRaises(ValueError):
            score_case('round-total', [], -1)

    def test_committed_game_pack_reproduces_exactly(self):
        expected = artifacts()
        self.assertGreaterEqual(len(expected), 12)
        for path, payload in expected.items():
            self.assertEqual((ROOT / path).read_bytes(), payload, path)
        self.assertTrue(verify()['valid'])

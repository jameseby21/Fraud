import copy
import unittest

from quality import audit_awards, public_award_quality
import tempfile


class AwardQualityTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(award_key='AWD-1', award_id='CONTRACT-1', recipient='Example supplier',
                   agency='Example agency', total_award_obligation_cents='10029', currency='USD',
                   start_date='2025-01-01', end_date='2025-12-31', synthetic='False', fraud_label='unlabeled')
        row.update(changes)
        return row

    def test_clean_data_passes_without_claiming_no_fraud(self):
        result = audit_awards([self.row()])
        self.assertEqual(result['status'], 'checks_passed')
        self.assertEqual(result['issues'], [])
        self.assertEqual(result['row_count'], 1)
        self.assertNotIn('fraud_score', result)
        self.assertIn('not evidence', result['interpretation'].lower())

    def test_empty_data_is_not_a_clean_bill_of_health(self):
        result = audit_awards([])
        self.assertEqual(result['status'], 'empty')
        self.assertEqual(result['row_count'], 0)

    def test_duplicate_ids_trace_every_affected_csv_row(self):
        result = audit_awards([self.row(), self.row()])
        issue = next(i for i in result['issues'] if i['code'] == 'DUPLICATE_AWARD_KEY')
        self.assertEqual(issue['row_numbers'], [2, 3])
        self.assertEqual(result['affected_rows'], 2)
        self.assertEqual(result['status'], 'needs_review')

    def test_missing_fields_are_not_silently_ignored(self):
        result = audit_awards([self.row(recipient='  ', award_key='')])
        fields = {i['field'] for i in result['issues'] if i['code'] == 'MISSING_REQUIRED_FIELD'}
        self.assertEqual(fields, {'recipient', 'award_key'})

    def test_money_uses_integer_cents_and_never_float_coercion(self):
        for amount in ('1.2', 'NaN', 'Infinity', '1e3', True):
            with self.subTest(amount=amount):
                result = audit_awards([self.row(total_award_obligation_cents=amount)])
                self.assertIn('INVALID_CENTS', {i['code'] for i in result['issues']})
        self.assertEqual(audit_awards([self.row(total_award_obligation_cents='999999999999999999999')])['issues'], [])

    def test_negative_obligation_is_context_not_fraud(self):
        result = audit_awards([self.row(total_award_obligation_cents='-500')])
        issue = next(i for i in result['issues'] if i['code'] == 'NEGATIVE_OBLIGATION')
        self.assertEqual(issue['severity'], 'info')
        self.assertIn('adjustment', issue['message'])
        self.assertEqual(result['status'], 'checks_passed')

    def test_dates_validate_and_reverse_ranges_are_traced(self):
        for start, end, code in [('2025-02-30', '', 'INVALID_DATE'),
                                  ('', '', 'MISSING_START_DATE'),
                                  ('2025-12-31', '2025-01-01', 'REVERSED_DATE_RANGE')]:
            with self.subTest(code=code):
                result = audit_awards([self.row(start_date=start, end_date=end)])
                self.assertIn(code, {i['code'] for i in result['issues']})
        self.assertEqual(audit_awards([self.row(end_date='')])['issues'], [])

    def test_currency_synthetic_and_label_boundaries_are_explicit(self):
        result = audit_awards([self.row(currency='EUR', synthetic='True', fraud_label='fraud')])
        self.assertTrue({'UNSUPPORTED_CURRENCY', 'SYNTHETIC_IN_PUBLIC_SAMPLE', 'UNEXPECTED_LABEL'} <= {i['code'] for i in result['issues']})

    def test_repeatable_report_does_not_mutate_input(self):
        rows = [self.row(), self.row(recipient=None, end_date='bad')]
        original = copy.deepcopy(rows)
        self.assertEqual(audit_awards(rows), audit_awards(rows))
        self.assertEqual(rows, original)

    def test_malformed_shapes_are_rejected(self):
        for rows in (None, {}, [None], ['not a record']):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                audit_awards(rows)

    def test_nontext_identifiers_and_names_are_reported(self):
        for field in ('award_key', 'award_id', 'recipient', 'agency'):
            with self.subTest(field=field):
                report = audit_awards([self.row(**{field: 123})])
                self.assertIn('INVALID_TEXT_FIELD', {i['code'] for i in report['issues']})

    def test_missing_local_sample_is_explicitly_empty(self):
        with tempfile.TemporaryDirectory() as root:
            report = public_award_quality(root)
        self.assertEqual(report['status'], 'empty')
        self.assertIsNone(report['source_sha256'])

import unittest
from verification import test_run_passes


class StrictVerificationTests(unittest.TestCase):
    def result(self):
        result = unittest.TestResult()
        result.testsRun = 3
        return result

    def test_nonempty_successful_run_passes(self):
        self.assertTrue(test_run_passes(self.result()))

    def test_zero_executed_tests_fail(self):
        self.assertFalse(test_run_passes(unittest.TestResult()))

    def test_skipped_security_test_cannot_look_green(self):
        result = self.result()
        result.skipped.append((None, 'Synthetic missing dependency'))
        self.assertFalse(test_run_passes(result))

    def test_expected_failures_are_not_silent_success(self):
        result = self.result()
        result.expectedFailures.append((None, 'Synthetic known defect'))
        self.assertFalse(test_run_passes(result))

    def test_failures_errors_and_unexpected_success_fail(self):
        for field in ('failures', 'errors', 'unexpectedSuccesses'):
            result = self.result()
            getattr(result, field).append((None, 'Synthetic QA outcome'))
            self.assertFalse(test_run_passes(result))

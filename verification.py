"""Strict test-result policy: missing coverage cannot count as a pass."""


def test_run_passes(result):
    return (result.testsRun > 0 and result.wasSuccessful() and
            not result.skipped and not result.expectedFailures)

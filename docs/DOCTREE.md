# Documentation tree and change map

[Root README: canonical project state](../README.md). Update that entry point whenever behavior, setup, datasets or validation limits change. This index is regenerated with `python documentation.py --write-tree`; verify with `python documentation.py`.

## Required updates by change

| Change | Update before committing |
| --- | --- |
| Routes or UI | Root README, course guide, HTTP/browser tests, checkpoint and troubleshooting |
| Data intake or library schema | Root README, DATA_SOURCES, library guide, intake/verification tests and checkpoint |
| Fixtures or planted patterns | Root README, dataset guide, instructor lineage, fraud-instance library, affected lessons and tests |
| Course structure or tool code | Root README, course guide, generated lessons/notebooks, R/Power BI guides, course tests and checkpoint |
| Models or statistical criteria | MODEL_CARD, pattern assumptions/controls, lessons, regression tests and root README |
| Private storage or publication | SECURITY, CONTRIBUTING, relevant tests, checkpoint and root README |
| New documentation | Link it here, fix local links, run the documentation graph check |

For every function or behavior: failing acceptance tests first, implementation, focused checks, regression tests for discoveries, then union/integration tests and full verification before stage/commit/push. A passing leaf test does not substitute for integration. Record what actually ran and what remains manual.

The check detects missing local targets and Markdown pages unreachable from README. It does not prove factual correctness, detect every stale statement, or validate external availability/anchors. Authors must review this change map and the linked documents for semantic drift.

## Linked document inventory

- [CHANGELOG.md](../CHANGELOG.md)
- [CHECKPOINTS.md](../CHECKPOINTS.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [courses/forensic-practicum/distribution-shift.md](../courses/forensic-practicum/distribution-shift.md)
- [courses/forensic-practicum/evidence-brief.md](../courses/forensic-practicum/evidence-brief.md)
- [courses/forensic-practicum/round-sums.md](../courses/forensic-practicum/round-sums.md)
- [courses/operations/capacity.md](../courses/operations/capacity.md)
- [courses/operations/summaries.md](../courses/operations/summaries.md)
- [courses/payment-lab/comparison.md](../courses/payment-lab/comparison.md)
- [courses/payment-lab/orientation.md](../courses/payment-lab/orientation.md)
- [courses/payment-lab/quality.md](../courses/payment-lab/quality.md)
- [courses/payment-lab/review.md](../courses/payment-lab/review.md)
- [courses/payment-lab/thresholds.md](../courses/payment-lab/thresholds.md)
- [courses/payment-lab/timing.md](../courses/payment-lab/timing.md)
- [courses/README.md](../courses/README.md)
- [courses/templates/feedback.md](../courses/templates/feedback.md)
- [courses/templates/review.md](../courses/templates/review.md)
- [courses/tracks/forensic-powerbi.md](../courses/tracks/forensic-powerbi.md)
- [courses/tracks/forensic-r.md](../courses/tracks/forensic-r.md)
- [courses/tracks/powerbi.md](../courses/tracks/powerbi.md)
- [courses/tracks/r.md](../courses/tracks/r.md)
- [data/forensic/v2/README.md](../data/forensic/v2/README.md)
- [data/learning/README.md](../data/learning/README.md)
- [data/LICENSE.md](../data/LICENSE.md)
- [DATA_SOURCES.md](../DATA_SOURCES.md)
- [docs/cases/adelphia.md](../docs/cases/adelphia.md)
- [docs/cases/bayou.md](../docs/cases/bayou.md)
- [docs/cases/bitconnect.md](../docs/cases/bitconnect.md)
- [docs/cases/enron.md](../docs/cases/enron.md)
- [docs/cases/ftx.md](../docs/cases/ftx.md)
- [docs/cases/galleon.md](../docs/cases/galleon.md)
- [docs/cases/madoff.md](../docs/cases/madoff.md)
- [docs/cases/onecoin.md](../docs/cases/onecoin.md)
- [docs/cases/peregrine.md](../docs/cases/peregrine.md)
- [docs/cases/petters.md](../docs/cases/petters.md)
- [docs/cases/README.md](../docs/cases/README.md)
- [docs/cases/refco.md](../docs/cases/refco.md)
- [docs/cases/rothstein.md](../docs/cases/rothstein.md)
- [docs/cases/shkreli.md](../docs/cases/shkreli.md)
- [docs/cases/stanford.md](../docs/cases/stanford.md)
- [docs/cases/telexfree.md](../docs/cases/telexfree.md)
- [docs/cases/theranos.md](../docs/cases/theranos.md)
- [docs/cases/tyco.md](../docs/cases/tyco.md)
- [docs/cases/volkswagen.md](../docs/cases/volkswagen.md)
- [docs/cases/worldcom.md](../docs/cases/worldcom.md)
- [docs/cases/zeekrewards.md](../docs/cases/zeekrewards.md)
- [docs/checkpoints/CP-001.md](../docs/checkpoints/CP-001.md)
- [docs/checkpoints/CP-002.md](../docs/checkpoints/CP-002.md)
- [docs/checkpoints/CP-003.md](../docs/checkpoints/CP-003.md)
- [docs/checkpoints/CP-004.md](../docs/checkpoints/CP-004.md)
- [docs/checkpoints/CP-005.md](../docs/checkpoints/CP-005.md)
- [docs/checkpoints/CP-006.md](../docs/checkpoints/CP-006.md)
- [docs/checkpoints/CP-007.md](../docs/checkpoints/CP-007.md)
- [docs/checkpoints/CP-008.md](../docs/checkpoints/CP-008.md)
- [docs/checkpoints/CP-009.md](../docs/checkpoints/CP-009.md)
- [docs/checkpoints/CP-010.md](../docs/checkpoints/CP-010.md)
- [docs/checkpoints/CP-011.md](../docs/checkpoints/CP-011.md)
- [docs/DOCTREE.md](../docs/DOCTREE.md)
- [docs/fraud_instances/bank-reconciliation.md](../docs/fraud_instances/bank-reconciliation.md)
- [docs/fraud_instances/benign-recurring.md](../docs/fraud_instances/benign-recurring.md)
- [docs/fraud_instances/distribution-shift.md](../docs/fraud_instances/distribution-shift.md)
- [docs/fraud_instances/introductory-patterns.md](../docs/fraud_instances/introductory-patterns.md)
- [docs/fraud_instances/README.md](../docs/fraud_instances/README.md)
- [docs/fraud_instances/repeated-invoice.md](../docs/fraud_instances/repeated-invoice.md)
- [docs/fraud_instances/round-individual.md](../docs/fraud_instances/round-individual.md)
- [docs/fraud_instances/round-sums.md](../docs/fraud_instances/round-sums.md)
- [docs/library/README.md](../docs/library/README.md)
- [FEATURE_BACKLOG.md](../FEATURE_BACKLOG.md)
- [MODEL_CARD.md](../MODEL_CARD.md)
- [README.md](../README.md)
- [ROADMAP.md](../ROADMAP.md)
- [SECURITY.md](../SECURITY.md)

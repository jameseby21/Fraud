# Mechanism replay model card

This prototype teaches interpretable screening, temporal isolation, provenance, and evidence communication. It is not a production fraud classifier.

## Two clocks

The source view separates `occurred_on` from `available_on`: a later report is unavailable at an earlier date. Unknown publication dates use the catalog review date conservatively. Web pages may be edited; recorded publication/update metadata is not an independently authenticated archive.

The lab uses simulated steps, not historical dates. Step 0 has no observations; steps 1-3 reveal fabricated normalized snapshots. Each rule uses the latest available snapshot, displaying operands, formula, threshold, evidence IDs, model version, and input hash. Historical outcomes are not inputs to numerical rules.

There is currently one curated source report per case. This sparse chronology is not a complete pre-exposure record or proof that public-data early detection was possible. Do not present the exercises as historical out-of-sample performance.

## Rules

Eleven families cover balance confirmation, invoice confirmation, customer-asset coverage, claim validation, earnings/cash gaps, related-party approvals, reporting-window gaps, recruitment dependence, payout coverage, lab/road differences, and pre-announcement trading patterns.

Each computes `(total - corroborated) / total` using mechanism-specific fields and an illustrative threshold. This shared formula makes arithmetic inspectable; it does not make the mechanisms statistically equivalent. Case-to-rule mappings are educational choices, not proof that a ratio detected the historical offense.

Inputs are invented normalized units, not actual dollars or estimated historical measurements. Baseline steps pass; the last step triggers by construction. Repeated profiles are not independent validation samples. No fitting, calibrated probabilities, or empirical accuracy estimates are claimed.

Every trigger has alternatives: incomplete records, lawful redemptions, working capital, ordinary settlements, or unmatched test conditions. Missing corroboration is not falsity. Modern entries reject numerical replay entirely to avoid attaching fabricated observations to unresolved subjects.

## Validation

Tests cover temporal isolation, future-input invariance, outcome gating, provenance, repeatability, malformed data, decimal monetary conversion, intake failure handling, and HTTP behavior. These establish software properties, not detection power.

Real validation requires historical observations with defensible availability dates, benign comparators, temporal and entity-disjoint holdouts, independent labels, and analysis of selective-label bias. Measure precision at a review budget, false positives, missed participants, detection delay, and coverage. Publish errors and negative results.

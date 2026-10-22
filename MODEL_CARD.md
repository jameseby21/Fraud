# Mechanism replay model card

The baseball courses use descriptive summaries rather than fraud rules or predictive models. The primary real-data course retains the measured CC BY source unchanged; its whiff denominator includes StrikeSwinging, FoulBall and InPlay, and contact-speed means include only measured InPlay records. Source-specific units, anonymous IDs and altered dates remain explicit. The separate synthetic practice lab has planted arsenal, within-pitch velocity, location/whiff and contact patterns with ordinary background variation. Neither course estimates causal effects, injury risk or out-of-sample performance. See [real baseball provenance](data/baseball/real-v1/README.md), [practice assumptions](data/baseball/v1/README.md) and [research](docs/sports/research.md).

This prototype teaches interpretable screening, temporal isolation, provenance, and evidence communication. It is not a production fraud classifier.

## Two clocks

The source view separates `occurred_on` from `available_on`: a later report is unavailable at an earlier date. Unknown publication dates use the catalog review date conservatively. Web pages may be edited; recorded publication/update metadata is not an independently authenticated archive.

The lab uses simulated steps, not historical dates. Step 0 has no observations; steps 1-3 reveal fabricated normalized snapshots. Each rule uses the latest available snapshot, displaying operands, formula, threshold, evidence IDs, model version, and input hash. Historical outcomes are not inputs to numerical rules.

There is currently one curated source report per case. This sparse chronology is not a complete pre-exposure record or proof that public-data early detection was possible. Do not present the exercises as historical out-of-sample performance.

## Rules

Thirteen families cover balance confirmation, invoice confirmation, customer-asset coverage, claim validation, earnings/cash gaps, related-party approvals, reporting-window gaps, recruitment dependence, payout coverage, lab/road differences, pre-announcement trading patterns, affirmative authorization, and post-escalation intervention.

Each computes `(total - corroborated) / total` using mechanism-specific fields and an illustrative threshold. This shared formula makes arithmetic inspectable; it does not make the mechanisms statistically equivalent. Case-to-rule mappings are educational choices, not proof that a ratio detected the historical offense.

Inputs are invented normalized units, not actual dollars or estimated historical measurements. Baseline steps pass; the last step triggers by construction. Repeated profiles are not independent validation samples. No fitting, calibrated probabilities, or empirical accuracy estimates are claimed.

Every trigger has alternatives: incomplete records, lawful redemptions, working capital, ordinary settlements, or unmatched test conditions. Missing corroboration is not falsity. Modern entries reject numerical replay entirely to avoid attaching fabricated observations to unresolved subjects.

The resolved-case catalog includes criminal convictions and pleas, an acquittal, mixed verdicts, a partial reversal, a civil judgment, an administrative consent order, and deferred prosecution agreements. These labels describe different burdens, procedures, and findings. They are curriculum metadata and never target labels for the mechanism rules. Monetary remedies retain their source label; the app does not convert a penalty, forfeiture, restitution, disgorgement, or coordinated payment into a common damages measure.

## Validation

Tests cover temporal isolation, future-input invariance, outcome gating, provenance, repeatability, malformed data, decimal monetary conversion, intake failure handling, and HTTP behavior. These establish software properties, not detection power.

Real validation requires historical observations with defensible availability dates, benign comparators, temporal and entity-disjoint holdouts, independent labels, and analysis of selective-label bias. Measure precision at a review budget, false positives, missed participants, detection delay, and coverage. Publish errors and negative results.

## Forensic-v2 descriptive review

See [instance definitions](docs/fraud_instances/README.md) and the [v2 model/data guide](data/forensic/v2/README.md). Background amounts are exact resampled federal obligations with inverse-square-root weights, reassigned to fictional activity. This is a teaching model, not a representative payment simulator. Round-total rules and descriptive empirical-CDF/leading-digit comparisons have no calibrated false-positive rate, significance or guilt probability. Bounded values, repeated draws, selection, cohorts and fixed-price controls complicate distribution assumptions; no automatic Benford null is asserted. Twelve planted round groups are confirmed in tests, but broad round-dollar searches also flag legitimate-looking source values. Legal sources motivate corroboration without reconstructing real-case transactions.

## Market-capacity review

The [market-context case](data/market/v1/README.md) contains two deterministic group-capacity contradictions. One compares fabricated confirmations with a complete fabricated exchange tape; the other compares fabricated final positions with 15 exact retained CFTC TFF combined open-interest values. Each excess is below 1%, and each target is surrounded by substantially more control data. Arithmetic and internal statement consistency deliberately pass.

The rule is `sum(scoped claims) > matching aggregate capacity`. It requires identical instrument or contract code, date, units, report type, venue scope, and availability. Duplicate joins can create false excesses. CFTC open interest is a position aggregate, not daily trade volume or customer-level execution evidence. A capacity conflict establishes that the scoped claims cannot all be true; it does not select a false row, identify a person, establish intent, or estimate a fraud probability. Fourteen below-capacity CFTC groups and all other synthetic tape groups are controls, but staying below capacity does not confirm a trade.

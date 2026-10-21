# 5. Check statement positions with public CFTC data

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/forensic/v2/payments.csv, version 2.0.0. Every record is synthetic.

## Question

What can a public aggregate prove about private statement positions, and what remains unknowable?

## Try it

Load positions.csv and public_reference.csv. Confirm the retained source hash in manifest.json, then group final long_contracts by provider, CFTC contract code, and report date. Compare the fictional totals with CFTC open_interest_all for the exact same code and date. In /records review the registered CFTC source and its scope before interpreting a mismatch.

Choose Python (the adjacent notebook), R (courses/tracks/forensic.R), or Power BI (courses/tracks/forensic-powerbi.md). The shared track guides cover this lesson by ID: `public-corroboration`. Save your working files in ignored output/, not beside public course assets.

## Check your work

The 4,000 fictional position rows cover 15 exact CFTC reference groups. Code 020601 totals 1,388,003 claimed long contracts versus public combined open interest of 1,376,168, an excess below 1%. At least one scoped claim cannot be true, but aggregate public data cannot identify which confirmation is false. The other 14 groups are capacity controls, not proof of execution.

## Debugging

CFTC open interest is a Tuesday aggregate released later; use available_on 2022-09-16 in an as-of analysis. Combined futures-and-options data, contract units, codes and dates must match. Public aggregates do not replace customer-level broker, clearing, or custody records.

## Reflection

Write one sentence that the public data establishes and one it cannot establish. Which next record would move the review from a group inconsistency toward a specific finding?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

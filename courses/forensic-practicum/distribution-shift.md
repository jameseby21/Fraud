# 3. Challenge fabricated randomness and write the memo

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/forensic/v2/payments.csv, version 2.0.0. Every record is synthetic.

## Question

Can a change in an amount distribution guide evidence requests without becoming a guilt score?

## Try it

Compare each supplier over time. Use histograms and empirical CDFs, preserve amount-range context, and examine leading digits descriptively. The worked example compares VEN-0088 before/after 2025-10-01. Explain business-mix and selection alternatives. Inspect the instructor key only after recording your observations and proposed evidence requests.

Choose Python (the adjacent notebook), R (courses/tracks/forensic.R), or Power BI (courses/tracks/forensic-powerbi.md). The shared track guides cover this lesson by ID: `distribution-shift`. Save your working files in ignored output/, not beside public course assets.

## Check your work

The planted cohort has 180 fabricated near-uniform amounts mixed with ordinary activity. The worked empirical CDF distance exceeds 0.15. This is descriptive, not a calibrated p-value or fraud probability. Bounded awards, resampling, fixed-price services and minimum/maximum selection do not establish Benford assumptions. The recurring-service control repeats legitimate-looking values.

## Debugging

A first-digit deviation alone cannot establish manipulation. Compare raw amounts, range, category, dates, sample sizes and dependence. Use all records in your selected tool; the browser scatter preview is only 500 rows. Save your memo and feedback in ignored output/.

## Reflection

Which further document would distinguish a change in procurement mix from fabricated transactions? What would falsify your preferred explanation?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

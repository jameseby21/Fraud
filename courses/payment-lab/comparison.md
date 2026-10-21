# 3. Compare amounts and category spread

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

Which amounts deserve contextual review, and which chart reveals the contrast?

## Try it

Build category-total bars, an amount histogram, and category box summaries. Compare the full USD scale with a zoomed background view. Retain the full-scale chart alongside any zoom. Inspect the highest amount and explain a benign alternative.

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `comparison`. Save your working files in ignored output/, not beside public course assets.

## Check your work

The largest synthetic transaction is USD 275,000. The histogram contains 6,000 observations. Category totals reconcile to the full total. A large capital purchase is a possible benign explanation.

## Debugging

Divide cents by 100 exactly once. The supplied histogram uses unequal-width categorical bins; bar heights are counts, not probability densities. Supplied box whiskers are min/max, not the default Tukey rule.

## Reflection

How could aggregation by category hide a large transaction? What changes when the outlier is retained versus excluded?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

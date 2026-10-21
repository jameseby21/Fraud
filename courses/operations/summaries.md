# 1. Compare allocation without a misconduct hypothesis

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

How is synthetic spending allocated across categories and regions?

## Try it

Reuse the same transactions with a different analytical purpose. Create category bars and sorted regional bars with cumulative share. Compare total and average amounts; report denominators and filter context. Filter category to Travel and calculate the mean transaction amount in USD, rounding only the final value to cents.

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `summaries`. Save your working files in ignored output/, not beside public course assets.

## Check your work

Four categories and four regions are present. Sorted regional cumulative share ends at 100%. Totals reconcile to the same 6,000-row input. The Travel-filtered mean is USD 2,203.76; the unfiltered mean is USD 2,258.49. Allocation does not measure efficiency or fairness.

## Debugging

Power BI measures respond to slicers. Reset filters before comparing against Python or R totals. Sorted bars plus cumulative share use two distinct axes.

## Reflection

What additional exposure denominator would make comparisons more meaningful?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

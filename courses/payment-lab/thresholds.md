# 5. Investigate groups, thresholds, and benign controls

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

Can aggregation reveal a review pattern invisible in individual rows?

## Try it

Use a fictional review threshold of USD 10,000. Group by supplier and invoice_date. Select groups with at least three rows, each below the threshold, and combined amount above it. Compare with equal-amount monthly recurring services. Keep the criteria explicit.

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `thresholds`. Save your working files in ignored output/, not beside public course assets.

## Check your work

Five supplier-days meet this exact rule; only one was deliberately planted: three USD 9,900 rows total USD 29,700. Four incidental background matches are also review candidates. Equal amounts on distinct monthly invoices are a benign control. Neither rule output is a guilt label.

## Debugging

Filter individual amounts before grouping and count rows as well as totals. Do not confuse 10,000 dollars with 10,000 cents. The fictional threshold is an exercise parameter, not a real procurement rule.

## Reflection

What false positives could staged work generate? How would you tune the time window without using the answer key?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

# 4. Explore time and relationships

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

Does a delay or a monthly change justify a causal explanation?

## Try it

Create an invoice-month total line chart. Calculate payment_date minus invoice_date in days. Plot amount versus delay. Filter delays over 90 days and inspect each row. Compare invoice-month and payment-month definitions.

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `timing`. Save your working files in ignored output/, not beside public course assets.

## Check your work

One transaction has a delay over 90 days: 181 days. Monthly invoice totals reconcile to all amounts. Some December invoices are paid in 2026; do not drop them with a 2025 payment-date filter.

## Debugging

ISO date text must become a date before subtraction. Browser scatter previews show the first 500 records only; use the full CSV in your selected tool. Correlation is not causation.

## Reflection

List a dispute, processing delay, and recording error as competing explanations. What time field would you need for an as-of investigation?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

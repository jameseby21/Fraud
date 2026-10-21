# 2. Validate types, grain, and repeated invoices

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

Are repeated records necessarily duplicate payments?

## Try it

Keep transaction_id as text and amount_cents as a whole number. Group by supplier and invoice_id, count rows, then inspect groups with more than one row. Preserve both transaction IDs. Compare dates and amounts. Do not deduplicate first.

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `quality`. Save your working files in ignored output/, not beside public course assets.

## Check your work

One repeated supplier-invoice group has two transaction rows. Record the IDs and a request for supporting documentation. A repeated invoice reference alone cannot establish that money moved twice.

## Debugging

Grouping by amount alone produces false positives, including recurring services. Grouping by transaction_id hides invoice repetition because transaction IDs are unique.

## Reflection

What additional record would distinguish a duplicate extraction from a duplicate disbursement?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

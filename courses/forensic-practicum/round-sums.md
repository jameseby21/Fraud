# 2. Find hidden round totals without accusing everyone

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/forensic/v2/payments.csv, version 2.0.0. Every record is synthetic.

## Question

Which aggregate pattern is invisible when every line looks irregular?

## Try it

Group the v2 payments by supplier_id and payment_date. Require at least three members and test total_cents modulo 1000000 equals zero. Keep individual cents visible. Compare individual round-dollar payments and monthly recurring invoices. Trace the group back to invoices and bank entries, then request contractual context.

Choose Python (the adjacent notebook), R (courses/tracks/forensic.R), or Power BI (courses/tracks/forensic-powerbi.md). The shared track guides cover this lesson by ID: `round-sums`. Save your working files in ignored output/, not beside public course assets.

## Check your work

Twelve deliberately planted groups each contain four nonround values totaling USD 10,000. No planted row is marked in learner tables, and transaction IDs/chronology do not put the answers first. The USD 10,000 modulus is fictional, not an asserted legal reporting threshold. Other incidental matches must also be reviewed.

## Debugging

Do all modular arithmetic in integer cents. Group by the stated grain; supplier/month may erase the designed daily pattern. Whole dollars are common in legitimate contracts; test benign controls before describing a signal as useful.

## Reflection

How would changing the grouping window or testing many round totals inflate your candidate list?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

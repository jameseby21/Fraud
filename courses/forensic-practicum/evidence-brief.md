# 1. Take the analyst brief and inspect evidence

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/forensic/v2/payments.csv, version 2.0.0. Every record is synthetic.

## Question

What can a polished statement establish without independent corroboration?

## Try it

Your fictional client is reviewing supplier payments. Load entities, payments, invoices and bank entries from data/forensic/v2. Define primary/foreign keys and availability dates. In /records open the Peter Madoff plea transcript, printed pages 42-43, and criminal information paragraphs 20-31. Record the speaker/document type and distinguish an allegation, a prosecutor statement and a plea. These sources motivate corroboration; the fictional supplier case is not a recreation of Madoff transactions.

Choose Python (the adjacent notebook), R (courses/tracks/forensic.R), or Power BI (courses/tracks/forensic-powerbi.md). The shared track guides cover this lesson by ID: `evidence-brief`. Save your working files in ignored output/, not beside public course assets.

## Check your work

There are 12,000 payments, 120 fictional suppliers, 11,999 invoice records and 12,000 bank entries. One invoice has two payment rows. Joining ledger and bank on transaction_id reveals one USD 5 discrepancy. As-of views must exclude records unavailable on the review date.

## Debugging

The legal source concerns Peter Madoff. Do not attribute it to Bernard or treat a charging document as a judgment. Double-check invoice grain before joining: repeated payments can multiply rows. The public award values are obligations reassigned to a fictional payment model.

## Reflection

What independent evidence could show that a reported review or a transaction actually occurred?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

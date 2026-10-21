# 4. Test polished statements against market capacity

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/forensic/v2/payments.csv, version 2.0.0. Every record is synthetic.

## Question

Can a statement be internally perfect and still describe trades that could not all have occurred?

## Try it

Load data/market/v1/confirmations.csv and market_context.csv. First verify every gross_cents value equals quantity times price_cents, every cash movement is its negative, and settlement follows trade date. Then group BUY quantities by security_id and trade_date and compare each total with the matching complete synthetic market volume. Keep the market scope and availability date beside every comparison.

Choose Python (the adjacent notebook), R (courses/tracks/forensic.R), or Power BI (courses/tracks/forensic-powerbi.md). The shared track guides cover this lesson by ID: `statement-capacity`. Save your working files in ignored output/, not beside public course assets.

## Check your work

All 8,000 confirmations pass the arithmetic and cash checks. One group contains 40 individually plausible lines totaling 2,521,337 units against complete synthetic market volume of 2,500,000, an excess below 1%. The contradiction is real inside the fixture, but the aggregate does not identify which line is false.

## Debugging

Join on both security_id and trade_date. Do not compare holdings with trading volume or combine market scopes. If many groups exceed volume, inspect duplicate joins and whether volume was repeated across account rows.

## Reflection

What independent custody, venue, clearing, or counterparty record could identify the false claim? Why does perfect statement arithmetic fail to answer that question?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

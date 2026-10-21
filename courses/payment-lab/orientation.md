# 1. Define the question and inspect provenance

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

What does one row mean, and which claims can these records support?

## Try it

Read data/learning/README.md. Import only transactions.csv. Count rows, distinct transaction IDs, suppliers, currencies, and missing values. Record the dataset hash before analysis. Do not open instructor answers yet.

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `orientation`. Save your working files in ignored output/, not beside public course assets.

## Check your work

There are 6,000 rows, 6,000 distinct transaction IDs, one currency (USD), and every synthetic flag is True. Dates and supplier identities are fictional. The original records are award obligations, not payment histories.

## Debugging

A missing file usually means the working directory is not the repository root. A changed hash means your input differs; run python learning_fixture.py verify before continuing.

## Reflection

Write a sentence separating a data-quality issue, an analytical anomaly, and evidence of misconduct.

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

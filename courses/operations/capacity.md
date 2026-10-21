# 2. Explore workload and timing

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

Which view helps plan review workload rather than accuse a supplier?

## Try it

Count invoice rows by month and compare counts with monthly amounts. Make a department-category heatmap. Compare delay distributions by category. Explain why monetary volume and transaction count answer different questions.

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `capacity`. Save your working files in ignored output/, not beside public course assets.

## Check your work

The department-category grid has 16 populated cells. There are 12 invoice months. The demonstration uses fabricated dates and cannot support a real staffing recommendation.

## Debugging

A sum of amount is not a transaction count. A minimum/maximum box differs from R default boxplot whiskers; label your method and compare quartile values separately.

## Reflection

How would seasonality, missing workload, or changes in staffing affect your interpretation?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

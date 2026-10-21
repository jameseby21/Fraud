# 6. Write a reproducible review memo

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

Can another analyst reproduce your observations and challenge your explanation?

## Try it

Write a memo using courses/templates/review.md. Include input hash, tool version, filters, transaction IDs, alternative explanations, and a next-evidence request. Only then compare with the public instructor key. Use courses/templates/feedback.md to report your experience.

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `review`. Save your working files in ignored output/, not beside public course assets.

## Check your work

Your memo separates observations from hypotheses and covers the four planted review patterns plus the benign control. State missed items and false positives. This is an open-book deterministic exercise, not an independent model evaluation.

## Debugging

If your totals differ, reset filters, check cents conversion and row counts, and record which input version you used. Opening the key early is fine for learning; disclose it when describing performance.

## Reflection

Which step was unclear or frustrating? What could you reproduce without the guide, and what evidence would you request next?

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.

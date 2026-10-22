# 2. Compare a pitcher arsenal with a PivotTable

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters and averages; no modeling or special library required. Dataset: data/baseball/v1/pitches.csv, version 1.0.0. All player identities and observations are fictional.

## Question

Did Rowan Ellis change pitch selection between the early and late sample periods?

## Try it

Filter pitcher to Rowan Ellis. In a PivotTable put period in rows, pitch_type in columns and count of pitch_id in values. Show values as percentage of row total. Draw grouped or 100-percent-stacked bars with sample counts beside percentages. Repeat for Theo Bennett as the control. Use the pitcher and pitch-type selectors in the reference preview to explore movement and location; chart the full CSV in your spreadsheet to compare periods.

Use the Excel / spreadsheet track first, or the adjacent Python notebook, courses/tracks/baseball.R, or the baseball Power BI guide. All tracks use the same CSV, grain and units. Save work in ignored output/.

## Check your work

Rowan Ellis throws 180 FF pitches out of 300 early pitches (60%) and 120 out of 300 late pitches (40%). That is a 20 percentage-point decrease, or a one-third relative decrease. Theo Bennett stays at 50% in both periods. The change is deliberately planted; equal sample sizes make this an easy first comparison.

## Debugging

Percentage of grand total answers a different question from percentage of each period row. Keep all pitch types in the denominator. Filter to one pitch type after computing a full arsenal share only when your measure preserves that denominator.

## Reflection

Does changing the pitch mix prove better performance? What would opponent handedness, count and score context add?

## Record your learning

Record lesson ID, tool, input hash, filters, numerator/denominator, observed result and one issue in courses/templates/feedback.md copied to ignored output/. Consult docs/sports/research.md for procedural sources and docs/sports/archive-review.md for the original project adaptation.

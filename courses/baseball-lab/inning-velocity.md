# 3. Separate pitch mix from velocity by inning

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters and averages; no modeling or special library required. Dataset: data/baseball/v1/pitches.csv, version 1.0.0. All player identities and observations are fictional.

## Question

Is Mateo Brooks throwing the same pitch more slowly in later innings?

## Try it

Filter pitcher to Mateo Brooks and pitch_type to FF. Pivot by inning with average speed_mph and count of pitch_id. Make a line chart with markers; label the mph axis and show group sizes. Compare innings 1-2 pooled against innings 6-7 pooled using the underlying pitches. Repeat for Theo Bennett. Then remove the pitch-type filter and explain why a changing arsenal can change the overall mean even without a within-type speed change.

Use the Excel / spreadsheet track first, or the adjacent Python notebook, courses/tracks/baseball.R, or the baseball Power BI guide. All tracks use the same CSV, grain and units. Save work in ignored output/.

## Check your work

Mateo Brooks has a programmed within-FF decline: the pooled innings 1-2 mean exceeds innings 6-7 by more than 1.5 mph. The control pitcher has no programmed inning trend, but ordinary jitter remains. Means must be weighted by pitch counts when combining groups.

## Debugging

Do not average inning means without weights when counts differ. Pitch velocity is mph; movement is inches and location is feet. A truncated mph axis can reveal a small change, but label its limits rather than implying a zero baseline.

## Reflection

Could selection into later innings, workload, weather, or measurement explain a real pattern? Why is this fixture insufficient for an injury diagnosis?

## Record your learning

Record lesson ID, tool, input hash, filters, numerator/denominator, observed result and one issue in courses/templates/feedback.md copied to ignored output/. Consult docs/sports/research.md for procedural sources and docs/sports/archive-review.md for the original project adaptation.

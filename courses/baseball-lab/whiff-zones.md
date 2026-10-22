# 4. Map pitch locations and calculate whiffs per swing

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters and averages; no modeling or special library required. Dataset: data/baseball/v1/pitches.csv, version 1.0.0. All player identities and observations are fictional.

## Question

Does the observed slider whiff rate differ inside and outside the teaching zone?

## Try it

Filter pitch_type to SL. Plot plate_x_ft versus plate_z_ft from the catcher perspective, with equal physical scales. The fixed teaching zone is -0.83 to 0.83 feet horizontally and 1.5 to 3.5 feet vertically, inclusive. Pivot by in_zone and sum swing and whiff. Divide total whiffs by total swings in each group. For a warm-up, 12 misses in 24 swings is what percentage? Repeat with pitcher and batter-hand filters, always retaining group counts.

Use the Excel / spreadsheet track first, or the adjacent Python notebook, courses/tracks/baseball.R, or the baseball Power BI guide. All tracks use the same CSV, grain and units. Save work in ignored output/.

## Check your work

The warm-up whiff rate is 50%, because 12 divided by 24 equals 0.5. In the fixture, SL is programmed to miss more often per swing outside the teaching zone. Exact observed counts are in the numeric summary and instructor key. Whiffs divided by pitches is a different rate. A fixed rectangle is a teaching classification, not an umpire-call model.

## Debugging

A zero-swing group has an undefined rate, not 0%. Use SUM(whiff)/SUM(swing); do not average subgroup percentages. Keep the catcher viewpoint and equal coordinate scales when comparing pitchers. Batters have different real strike-zone heights; the fixture uses one reference rectangle.

## Reflection

Why does a high out-of-zone whiff rate fail to prove that throwing every pitch outside is a good strategy?

## Record your learning

Record lesson ID, tool, input hash, filters, numerator/denominator, observed result and one issue in courses/templates/feedback.md copied to ignored output/. Consult docs/sports/research.md for procedural sources and docs/sports/archive-review.md for the original project adaptation.

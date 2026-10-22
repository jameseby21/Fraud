# 5. Compare hitter contact and write a scouting note

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters and averages; no modeling or special library required. Dataset: data/baseball/v1/pitches.csv, version 1.0.0. All player identities and observations are fictional.

## Question

Did Casey Morgan recorded contact change, and what can a small batted-ball sample establish?

## Try it

Filter batter to Casey Morgan and in_play to 1. Pivot period with average exit_speed_mph, average launch_angle_deg and count of pitch_id. Draw an exit-speed histogram and period comparison. Repeat for another batter and keep sample sizes visible. Write a one-page note with source/version, filters, counts, units, two observations, an alternative explanation and a next-data request. Follow the Excel guide for exact formulas and the R track for a restored side-by-side pitcher plot.

Use the Excel / spreadsheet track first, or the adjacent Python notebook, courses/tracks/baseball.R, or the baseball Power BI guide. All tracks use the same CSV, grain and units. Save work in ignored output/.

## Check your work

Casey Morgan has a deliberately planted late-period contact-speed increase greater than 3 mph in the realized sample. Contact fields are populated only for tracked balls in play. The observed shift does not measure batting average, home-run probability or a causal swing improvement. Other batters show ordinary variation without a programmed period effect.

## Debugging

Use only nonblank contact observations. Never turn missing exit speed on a taken pitch or swing-and-miss into 0 mph. A mean of per-game means differs from the pitch-weighted mean when contact counts vary.

## Reflection

Which finding survives a reasonable filter change, and what new sample would you collect before giving a coach advice?

## Record your learning

Record lesson ID, tool, input hash, filters, numerator/denominator, observed result and one issue in courses/templates/feedback.md copied to ignored output/. Consult docs/sports/research.md for procedural sources and docs/sports/archive-review.md for the original project adaptation.

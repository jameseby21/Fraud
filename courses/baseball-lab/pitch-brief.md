# 1. Take the baseball analyst brief and inspect the file

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters and averages; no modeling or special library required. Dataset: data/baseball/v1/pitches.csv, version 1.0.0. All player identities and observations are fictional.

## Question

What does one pitch row represent, and which baseball questions can a small sample answer?

## Try it

Start in Excel or LibreOffice with data/baseball/v1/pitches.csv. Format it as a table called Pitches. Count pitch_id, distinct pitcher and batter names, pitch types, game IDs and missing contact fields. Compare the file hash with manifest.json. This is an independent-pitch teaching sample, not complete games or valid sequences of plate appearances. Read docs/sports/research.md and the archive review before drawing a baseball conclusion.

Use the Excel / spreadsheet track first, or the adjacent Python notebook, courses/tracks/baseball.R, or the baseball Power BI guide. All tracks use the same CSV, grain and units. Save work in ignored output/.

## Check your work

There are 3,600 unique pitch rows, six fictional pitchers, twelve fictional batters and three pitch types: FF, SL and CH. Each pitcher has six sampled outings with 100 pitches each. Contact speed and launch angle are blank on pitches not put in play. No numeric observation comes from an MLB player.

## Debugging

A .R filename in an old archive may contain serialized data rather than source code. Use the supplied plain CSV for this course. Do not fill missing contact speeds with zero or treat one pitch as one at-bat.

## Reflection

Which statement belongs in a scouting memo, and which would require complete games, opponent context, or independent observation?

## Record your learning

Record lesson ID, tool, input hash, filters, numerator/denominator, observed result and one issue in courses/templates/feedback.md copied to ignored output/. Consult docs/sports/research.md for procedural sources and docs/sports/archive-review.md for the original project adaptation.

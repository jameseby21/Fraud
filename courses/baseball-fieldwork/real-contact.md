# 3. Calculate real whiff rates and compare tracked contact

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters, counts and averages. Dataset: real college TrackMan observations, DOI 10.17632/xfnz6mkdzm.3. CC BY 4.0. Source CSV is unchanged; anonymous IDs and altered dates are retained.

## Question

What do the observed misses and batted-ball speeds show after choosing the correct denominator?

## Try it

Create a PivotTable by TaggedPitchType and PitchCall. Count StrikeSwinging as whiffs; count StrikeSwinging, FoulBall and InPlay as swings. Divide misses by swings. For contact, filter PitchCall to InPlay and retain nonblank ExitSpeed and Angle. Compare means and sample counts by anonymous BatterId. Pick a hitter with a reasonable sample, make a histogram and write a short scouting note with source, filters, denominators, observed result and limits. Try the separate synthetic baseball practice lab afterward for known-answer pattern detection.

Use the Excel/spreadsheet guide first, or the adjacent Python notebook, base-R or Power BI track. The real dataset is separate from the optional 3,600-row synthetic practice fixture. Attribution: Nathan David Pifer (2024), Optical Tracking Data from College Baseball Scrimmages, Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0. No endorsement implied.

## Check your work

Across the full real CSV there are 381 swinging strikes in 1,432 recorded swings, a whiff rate of about 26.61%. InPlay has 549 rows, but only 505 have measured ExitSpeed: 44 records lack a speed measurement. The contact mean therefore uses 505 values, not 549 zero-filled values. Real values are not altered to make an insight appear. A small anonymous hitter sample does not establish a causal skill change.

## Debugging

FoulBall counts as a swing and contact but not InPlay in this definition. Do not treat BallCalled, StrikeCalled or HitByPitch as swings. Empty ExitSpeed is not zero. Do not average subgroup whiff percentages; pool misses and swings.

## Reflection

Which descriptive observation is robust to a reasonable filter change, and which new evidence would improve confidence?

## Record your learning

Record source DOI/version, CSV SHA-256, tool, selected anonymous IDs, all filters, counts, units and one limitation. See docs/sports/research.md and courses/templates/feedback.md; keep working files in ignored output/.

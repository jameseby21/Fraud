# Baseball with Excel or LibreOffice

No code, database, cloud account, paid feed or add-in is needed. Open data/baseball/v1/pitches.csv using Data > From Text/CSV (comma delimiter), then format the range as a table named Pitches. Keep pitch_id, game_id, player names, period and pitch_type as text; speed/location/movement as decimals; swing, whiff, in_play and in_zone as whole numbers. Preserve blank contact fields. Keep a copy of the original CSV.

## 1. Pitch brief

Count pitch_id with a PivotTable; expect 3,600. Rows are pitches, not at-bats. Put pitcher, then batter in PivotTable rows to inspect six pitchers and twelve batters. Each pitcher has 600 pitches. FF means four-seam fastball, SL slider, CH changeup. The file represents selected pitches rather than complete playable games.

## 2. Pitch mix

Filter pitcher to Rowan Ellis. Put period in rows, pitch_type in columns, count of pitch_id in values. Right-click a value > Show Values As > % of Row Total. Keep a second count field so denominators remain visible. FF is 180/300 early (60%) and 120/300 late (40%). Compare Theo Bennett, whose FF share stays at 50%. Use grouped or 100% stacked bars. A row-total share differs from percentage of grand total; do not filter out SL and CH before calculating FF share.

## 3. Inning velocity

Filter Mateo Brooks and FF. Put inning in rows, average speed_mph and count of pitch_id in values. Draw a line with markers and a labeled mph axis. For pooled innings, use the underlying table, not an unweighted average of inning means. These Excel formulas use structured references; local installations may use semicolons instead of commas:

```text
=AVERAGEIFS(Pitches[speed_mph],Pitches[pitcher],"Mateo Brooks",Pitches[pitch_type],"FF",Pitches[inning],"<=2")
=AVERAGEIFS(Pitches[speed_mph],Pitches[pitcher],"Mateo Brooks",Pitches[pitch_type],"FF",Pitches[inning],">=6")
```

The early-minus-late difference exceeds 1.5 mph. Theo Bennett has no programmed inning effect. Do not infer injury from a descriptive plot.

## 4. Whiffs and location

Filter SL, put in_zone in rows, and sum whiff and swing in values. Divide the two sums in cells beside the PivotTable. Format as percentage. A toy example of 12 misses / 24 swings is 50%, not 0.5% and not misses divided by pitches. A blank or undefined denominator stays blank.

```text
=IF(SUMIFS(Pitches[swing],Pitches[pitch_type],"SL",Pitches[in_zone],0)=0,"",SUMIFS(Pitches[whiff],Pitches[pitch_type],"SL",Pitches[in_zone],0)/SUMIFS(Pitches[swing],Pitches[pitch_type],"SL",Pitches[in_zone],0))
```

For a location scatter, copy the filtered visible rows to a working sheet and plot plate_x_ft horizontally versus plate_z_ft vertically. Confirm the chart includes the intended filtered rows; charts and PivotTables do not always inherit the same filters. Use -2.5 to 2.5 and 0 to 5 feet, equal width and height, and one series per pitch type. The catcher sees negative x on the left. Movement uses movement_x_in and movement_z_in instead; these are already inches, so do not multiply them by 12.

## 5. Hitter contact and memo

Filter Casey Morgan and in_play = 1. Put period in rows, average exit_speed_mph, average launch_angle_deg and count of pitch_id in values. The late mean exceeds early by more than 3 mph. Compare another batter as a control. Missing contact on taken pitches or misses is not 0 mph. The course does not supply hit outcomes and cannot calculate batting average or home-run probability.

Write the input version/hash, numerator/denominator, player/type/period filters, group counts, chart units, observation, alternative explanation and one new-data request. Use the instructor key only after trying the task. Ordinary variation among controls is part of the exercise.

## Common issues

- A whole column imports as text: inspect delimiter and decimal locale; convert the numeric columns only.
- A mean is unchanged after a table filter: AVERAGEIFS uses its own explicit criteria; it does not follow worksheet visibility. Update the formula criteria or use the same PivotTable slicers throughout.
- A share is 100%: restore the other pitch types before calculating the period denominator.
- A blank result becomes zero: keep no-swings or no-contact groups undefined rather than filling them.

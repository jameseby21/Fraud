# Baseball with Power BI Desktop

Get Data > Text/CSV > data/baseball/v1/pitches.csv. Keep IDs as text, speed/location/movement as decimal numbers, and binary indicators as whole numbers. Keep blank contact fields null. Name the table Pitches. This is one pitch per row, not one at-bat; all records are fictional.

Create slicers for pitcher, batter, pitch_type and period. A count of pitch_id supplies sample size. Use these measures:

```dax
Pitch count = COUNTROWS(Pitches)
Pitch share = DIVIDE([Pitch count], CALCULATE([Pitch count], REMOVEFILTERS(Pitches[pitch_type])))
Whiff rate = DIVIDE(SUM(Pitches[whiff]), SUM(Pitches[swing]))
Mean pitch mph = AVERAGE(Pitches[speed_mph])
Contact count = CALCULATE([Pitch count], Pitches[in_play] = 1)
Mean exit mph = CALCULATE(AVERAGE(Pitches[exit_speed_mph]), Pitches[in_play] = 1)
```

Put period in matrix rows, pitch_type in columns, and Pitch share plus Pitch count in values. Rowan Ellis FF is 60% early and 40% late. REMOVEFILTERS removes the pitch-type filter while retaining player and period context. Test each slicer deliberately.

For Mateo Brooks, filter FF and plot Mean pitch mph against inning with Pitch count in the tooltip. Compare pooled innings 1-2 versus 6-7 using the raw pitches, not the average of displayed means. The difference exceeds 1.5 mph.

For location, use a scatter with plate_x_ft on X, plate_z_ft on Y, pitch_id as detail and pitch_type as legend. Fix X to -2.5..2.5 and Y to 0..5 and make equal drawing scales. Review the visual's row limits before claiming every pitch is shown. The fixed reference rectangle is -0.83..0.83 by 1.5..3.5 feet, catcher view. Movement uses the already-inch fields, without another conversion.

For whiffs, filter SL and compare Whiff rate by in_zone, with summed swing and whiff beside the rate. A no-swings slice stays blank through DIVIDE. For contact, filter Casey Morgan and in_play = 1, compare Mean exit mph and Contact count by period, then inspect another batter as control. Blanks on non-contact pitches must never become zero-mph contact.

Power BI Desktop report creation and visual acceptance are manual; no PBIX is supplied. Compare the matrix values with the Python numeric summary or instructor key before writing a scouting note. The no-code Excel track is the simpler default.

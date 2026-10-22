# Real baseball with Power BI

Import the real Track_Combo.csv source and name the table RealPitches. Keep PitcherId and BatterId as text; RelSpeed, ExitSpeed, PlateLocSide and PlateLocHeight as decimal numbers; blanks stay null. Source: Nathan David Pifer (2024), Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0. Input bytes are unchanged; visuals are derived.

Create player, TaggedPitchType and Date slicers. Date is an anonymized label, not the original calendar date. These measures preserve explicit denominators:

```dax
Pitches = COUNTROWS(RealPitches)
Pitch share = DIVIDE([Pitches], CALCULATE([Pitches], REMOVEFILTERS(RealPitches[TaggedPitchType])))
Swings = CALCULATE([Pitches], RealPitches[PitchCall] IN {"StrikeSwinging", "FoulBall", "InPlay"})
Whiffs = CALCULATE([Pitches], RealPitches[PitchCall] = "StrikeSwinging")
Whiff rate = DIVIDE([Whiffs], [Swings])
Release mph = AVERAGE(RealPitches[RelSpeed])
Contact mph = CALCULATE(AVERAGE(RealPitches[ExitSpeed]), RealPitches[PitchCall] = "InPlay")
```

Use a pitch-type matrix with Pitches, Pitch share and Release mph. Pitcher 1000036206 has 193 rows. Use RelSpeed by inning only after choosing player/type/date filters and retaining counts. Location scatter uses source feet without a Savant sign flip. The full-data whiff rate is 381/1432; InPlay has 549 rows. Compare tracked ExitSpeed counts before ranking anonymous hitters.

Desktop report construction and visual row-limit checks remain manual. No PBIX is claimed tested. Preserve the CC BY attribution on exported figures and document all filters.

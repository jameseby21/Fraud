# Real baseball in Excel / LibreOffice

Start with the real source CSV download, Track_Combo.csv, not the synthetic pitches.csv. Source: Nathan David Pifer (2024), Optical Tracking Data from College Baseball Scrimmages, Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0. The downloaded source bytes are unchanged. All tables/charts below are derived views.

Use Data > From Text/CSV, comma delimiter. Keep PitcherId and BatterId as text. Format the range as a table named RealPitches. RelSpeed and ExitSpeed are mph; PlateLocSide and PlateLocHeight are source feet. Do not convert or reverse source coordinates using a Baseball Savant recipe. There are 3,344 rows and 141 columns. The Date labels are anonymized and must not be treated as original calendar dates.

## Real brief

Count PitchNo with a PivotTable. Put TaggedPitchType in rows: Fastball has 1,745 rows. Count distinct Date labels separately: 20 labels is not a reliable game count. Missing measurements stay blank. TaggedPitchType is the operator tag; AutoPitchType is an independent automatic tag. Neither should be renamed into MLB pitch categories by guesswork.

## Real arsenal and velocity

Filter PitcherId to 1000036206, yielding 193 recorded pitches. Pivot TaggedPitchType in rows, count of PitchNo and average RelSpeed in values. Add a second count field shown as % of Grand Total after applying the pitcher filter. Draw bars with counts. Compare against another pitcher and retain sample sizes.

For the published example, select pitcher 1000103199, Fastball, Date label 11/6/2022. Copy these filtered rows to a working sheet and chart PitchNo versus RelSpeed. Do not claim a trend before inspecting it. Compare with the course preview's inning means, which may pool different samples unless the same filters are selected.

For pitch locations, plot PlateLocSide versus PlateLocHeight and use equal physical scales. Keep source signs and units. This source is TrackMan college data, not Statcast MLB data; a source-specific coordinate check comes before interpreting inside/outside or comparing systems.

## Real whiffs and contact

Add a column named Swing and enter the first formula; add a column named Whiff and enter the second:

```text
=--OR([@PitchCall]="StrikeSwinging",[@PitchCall]="FoulBall",[@PitchCall]="InPlay")
=--([@PitchCall]="StrikeSwinging")
```

Pivot by TaggedPitchType and sum the helper columns. Divide the sum of Whiff by sum of Swing. Across all rows, 381/1432 is about 26.61%. Do not count StrikeCalled or BallCalled as a swing. A no-swings group has no defined rate.

For hitter contact, filter PitchCall to InPlay, then exclude blank ExitSpeed. Pivot BatterId in rows with average ExitSpeed, average Angle and count of measured ExitSpeed. There are 549 InPlay rows, but tracked-contact counts must be measured separately. A foul ball is a swing without being InPlay under this definition.

Write a one-page note with source DOI/hash, anonymous player ID, all filters, counts and units, an observed result, a plausible alternative and a next-data request. These are real observations without planted answers. The separate synthetic practice lab lets you practice detecting known patterns afterward.

## Debugging

CSV import and formula separators depend on locale. AVERAGEIFS has its own criteria and does not follow hidden worksheet rows. A blank tracking field is not zero; inspect type conversion before interpreting an unusually low average. ID strings preserve the publisher's anonymization without pretending they are known MLB players.

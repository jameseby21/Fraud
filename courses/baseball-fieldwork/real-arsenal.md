# 2. Explore an actual pitcher arsenal and speed profile

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters, counts and averages. Dataset: real college TrackMan observations, DOI 10.17632/xfnz6mkdzm.3. CC BY 4.0. Source CSV is unchanged; anonymous IDs and altered dates are retained.

## Question

Which pitches does anonymous pitcher 1000036206 throw, and how do their observed speeds differ?

## Try it

Filter PitcherId to 1000036206. Pivot TaggedPitchType in rows with count of PitchNo and average RelSpeed in values. Add percentage of pitcher total and a pitch-count bar chart. Make a PlateLocSide versus PlateLocHeight scatter from the same rows. Then compare pitcher 1000103199, tagged Fastball, altered Date label 11/6/2022: chart average RelSpeed by inning with counts, and inspect raw PitchNo versus RelSpeed in Excel. Preserve the source coordinate convention; do not apply a Baseball Savant sign flip.

Use the Excel/spreadsheet guide first, or the adjacent Python notebook, base-R or Power BI track. The real dataset is separate from the optional 3,600-row synthetic practice fixture. Attribution: Nathan David Pifer (2024), Optical Tracking Data from College Baseball Scrimmages, Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0. No endorsement implied.

## Check your work

Pitcher 1000036206 contributes 193 recorded pitches across the retained sample. Pitch tags and measured release speeds can be compared directly in the filtered numeric summary. A pooled inning profile changes when player, pitch type or date filters change. There is no designed improvement or decline in this real dataset; report the observed direction and counts rather than looking for a promised planted result.

## Debugging

Keep all pitch types in the arsenal denominator. Filter a single pitcher, pitch type and anonymized date before interpreting a within-outing speed change. A low-count pitch tag is not an estimate of a reliable arsenal feature.

## Reflection

How much does the pattern change when you isolate one outing instead of pooling all records?

## Record your learning

Record source DOI/version, CSV SHA-256, tool, selected anonymous IDs, all filters, counts, units and one limitation. See docs/sports/research.md and courses/templates/feedback.md; keep working files in ignored output/.

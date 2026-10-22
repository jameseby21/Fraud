# 1. Inspect real college pitch-tracking data

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters, counts and averages. Dataset: real college TrackMan observations, DOI 10.17632/xfnz6mkdzm.3. CC BY 4.0. Source CSV is unchanged; anonymous IDs and altered dates are retained.

## Question

What is measured, what was anonymized, and what does one row represent?

## Try it

Start with the real pitch CSV download, Track_Combo.csv. Read data/baseball/real-v1/README.md and the source attribution. In Excel format the data as a table called RealPitches. Keep PitcherId and BatterId as text. Count rows, distinct IDs, pitch tags and PitchCall values. Do not interpret Date as the original date: the publisher altered it. Compare the retained file hash with manifest.json.

Use the Excel/spreadsheet guide first, or the adjacent Python notebook, base-R or Power BI track. The real dataset is separate from the optional 3,600-row synthetic practice fixture. Attribution: Nathan David Pifer (2024), Optical Tracking Data from College Baseball Scrimmages, Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0. No endorsement implied.

## Check your work

The retained source contains 3,344 real pitch observations and 141 columns. It has 1,745 manually tagged Fastball pitches. The publisher describes 21 scrimmages, while the retained file has 20 distinct altered Date labels; do not silently equate distinct dates with game count. Players have persistent anonymous IDs, not invented measurements.

## Debugging

Do not relabel Fastball as a known four-seam type or confuse operator tags with automatic tags. Missing tracking values remain missing. No archive record, fixture value or resampled observation was mixed into the source.

## Reflection

What can this exhibition-game sample support, and which conclusions would need a representative season?

## Record your learning

Record source DOI/version, CSV SHA-256, tool, selected anonymous IDs, all filters, counts, units and one limitation. See docs/sports/research.md and courses/templates/feedback.md; keep working files in ignored output/.

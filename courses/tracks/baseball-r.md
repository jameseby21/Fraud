# Baseball with base R

From the repository root run `Rscript courses/tracks/baseball.R`. No R package install is required. The script verifies 3,600 pitches, full-arsenal shares, pooled FF velocity and contact patterns, writes summary CSV files, and creates output/baseball-course.pdf. The notebook/Excel/Power BI tracks use the identical fixture.

The location-comparison function adapts the owner-supplied Ballpark Estimates project: filter a named pitcher, plot px against pz, and distinguish pitch types. It removes the first-500-row shortcut, uses equal coordinate scales, adds an explicit reference zone and handles empty samples. The original density layer is an optional extension because bandwidth choice can hide sample-size differences. See docs/sports/archive-review.md for the recovered-code mapping and defects.

Choose two pitchers by editing the two function calls near the plotting section. Use `subset(pitch, batter == "Casey Morgan")` for a hitter view. FF/SL/CH colors have a text legend; figures show sample sizes, units and catcher perspective. The first three rows of the PDF repeat the basic comparison rather than using MDS or model fitting.

If R cannot find the CSV, run from the cloned repository root. If rates differ, compare the exact player, pitch type, period, zone and swings denominator. Contact NAs are structural missingness; they are not zeros. R execution is included in Linux CI; interactive local R availability is reported in the checkpoint.

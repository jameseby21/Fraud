# Real baseball with base R

Run `Rscript courses/tracks/baseball-real.R` from the repository root. It reads the unchanged, hash-identified public CSV, verifies 3,344 observations and the 381/1,432 whiff calculation, and writes ignored PDF/CSV summaries. No package installation is required.

The shared baseball-plots.R function adapts the supplied 2016 project's pitcher filtering and px/pz comparison to actual anonymous PitcherId values. It retains all measured locations and source signs, uses equal scales, supports all observed pitch tags, and labels the real source. The raw IDs and date labels were anonymized by the publisher; this script does not invent values or identify players.

Source attribution: Nathan David Pifer (2024), Optical Tracking Data from College Baseball Scrimmages, Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0. Original input unchanged; plots and summary tables are derived. Use the Excel guide for the same analysis without code. R execution is included in Linux CI and the local checkpoint.

# R track

Use an installed R distribution, then run from the repository root:

```sh
Rscript courses/tracks/analysis.R
```

No external packages or downloads are required. Work section by section in RStudio if preferred. Sections match the eight lesson IDs. Predict results before running the assertions. The script creates seven chart families in ignored `output/course-r.pdf`; the PDF is a portable local artifact.

Expected checks: 6,000 rows; one repeated supplier/invoice group (two rows); five supplier-day threshold candidates, one deliberately planted; one payment delay over 90 days. R uses exact integer-valued doubles within this fixture's range. Do not extend that assumption to arbitrarily large currency data.

R histograms use equal-width bins here and R boxplots use default Tukey whiskers. The browser uses explicitly labeled categorical count bins and min/max whiskers. These are distinct display conventions, not conflicting source records. Reconcile raw row counts and totals before comparing display conventions.

Troubleshooting: `cannot open file` means the working directory is wrong; run `getwd()` and `setwd()` to the repository root. A stale or incomplete PDF may mean a previous graphics device was not closed; run `dev.off()` or restart the R session and rerun. A failed assertion requires an input/version check before editing the expected value.

Official references: [R introduction](https://stat.ethz.ch/CRAN/doc/manuals/R-intro.html), [histogram definitions](https://stat.ethz.ch/R-manual/R-patched/library/graphics/html/hist.html), [boxplot definitions](https://stat.ethz.ch/R-manual/R-devel/library/graphics/html/boxplot.html).

Validation status: the script executed successfully on Linux in [CI run 39647219305](https://github.com/jameseby21/Fraud/actions/runs/39647219305), including its reconciliation assertions and seven-page chart PDF. Rscript is not installed in the local Windows workspace; local Windows R execution and visual review of the PDF remain separate checks. Passing Python tests alone does not validate R.

# Forensic practicum in R

From the repository root run `Rscript courses/tracks/forensic.R`, or execute the matching evidence-brief, round-sums and distribution-shift sections in RStudio. The script uses base R, joins four fictional tables, calculates group sums and before/after empirical CDFs, and exports ignored output/forensic-r.pdf.

Expected: 12,000 payments; 120 suppliers; 11,999 invoices; 12,000 bank entries; at least twelve round-total candidate groups; one USD 5 bank difference. The worked supplier CDF distance exceeds 0.15. Do not interpret that distance as a p-value or fraud probability. The PDF contains full-population distribution, cohort CDF and leading-digit charts; no Benford fit is asserted.

If CSV files are missing, use `getwd()` and open the repository root. If joins multiply rows, check invoice uniqueness versus payment grain. Subtract dates as Date objects; ISO strings are used only for the explicitly formatted cohort comparison. Whole cents and these sums remain exactly representable within this fixture's numeric range. Inspect any failed assertion before editing an expectation.

Run the task before revealing the worked checks; use the memo and feedback templates. The course is a fictional supplier review inspired by corroboration questions in real legal records, not a real Madoff ledger.

Execution status is recorded in the checkpoint note. Python tests do not establish R execution; CI has a separate R step.

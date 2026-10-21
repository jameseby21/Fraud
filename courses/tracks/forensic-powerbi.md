# Forensic practicum in Power BI Desktop

Manual Desktop acceptance remains required. These are editable source/build instructions, not a tested PBIX.

Create a text parameter `CaseFolder` pointing to your local data/forensic/v2 folder. Name a blank query `ForensicCase` and paste forensic.pq into Advanced Editor. It returns a record of four tables. Create four reference queries with `= ForensicCase[Payments]`, `= ForensicCase[Entities]`, `= ForensicCase[Invoices]`, and `= ForensicCase[BankEntries]`. Disable load for the container query if offered. Do not commit a private machine path.

## evidence-brief

- Confirm 12,000 payments, 120 entities, 11,999 invoices and 12,000 bank entries.
- Use Entities[supplier_id] on the one side of a relationship to Payments[supplier_id]. Use Invoices[invoice_id] on the one side to Payments[invoice_id]. Both keys must be unique on the one side.
- BankEntries[transaction_id] and Payments[transaction_id] are unique here. For the exercise, merge them by transaction_id in Power Query and expand signed_amount_cents; add a whole-number variance column `-[signed_amount_cents] - [amount_cents]`. Exactly one difference is 500 cents.
- Filter Payments[available_on] and BankEntries[posted_date] to the review date before claiming a record was available. An invoice's availability does not make its later payment available.

## round-sums

Reference Payments. Group by supplier_id and payment_date; add Count Rows and Sum amount_cents. Filter count >= 3 and `Number.Mod([TotalCents],1000000) = 0`. Join candidate keys back to payments and show transaction ID, fictional supplier name, amount cents and invoice ID. Twelve deliberately planted four-member groups each total USD 10,000, even though members have nonzero cents. Inspect incidental candidates as well.

Use a supplier/day matrix with count and totals, then conditional formatting with printed values. Add detail tables and slicers. Do not treat every whole-dollar payment as fraudulent: copied public values and recurring-service controls also contain round amounts.

## distribution-shift

Select VEN-0088 and split payment_date at 2025-10-01. Use identical fixed amount bins for both cohorts; compare counts and fractions, not just totals. Use a sorted AmountUSD table with cumulative proportions for an empirical CDF, or export this cohort to the supplied R/Python calculation. Record cohort sizes, range and business category. A first-digit chart should be labeled descriptive; do not attach a Benford or guilt score.

The general seven-family recipes remain in powerbi.md; choose Payments as the source and derive AmountUSD = amount_cents / 100 and DelayDays from the dates. Histograms/CDFs and detail tables are the most relevant views here. Save under ignored output/. Record Desktop version and actual results in feedback, including any query errors.

## statement-capacity

Import `data/market/v1/confirmations.csv` and `market_context.csv` as whole-number tables. Add `ExpectedGross = confirmations[quantity] * confirmations[price_cents]` and `ExpectedCash = -confirmations[gross_cents]`; both variances should be zero. Build a summary by security_id and trade_date, sum quantity, relate it to the unique matching market-context key, and calculate claimed quantity minus market volume. Preserve a detail drill-through. Exactly one group exceeds the complete synthetic tape, by less than 1%; no formula identifies a false row.

## public-corroboration

Import `positions.csv` and `public_reference.csv`; keep the CFTC contract code as text so leading zeros survive. Group final long contracts by provider_id, report date and contract code. Compare with open_interest_all only after confirming the code, date, combined-report scope, units, source hash, and `available_on`. Exactly one of 15 groups exceeds public open interest by less than 1%. Label the result a group inconsistency. Public CFTC aggregates cannot confirm an individual customer execution.

Common issues: multiply-by-100 currency mistakes, lost leading zeros in contract codes, ambiguous relationships, invoice-join fan-out, repeated market capacity after a many-side join, stale filters, incorrect path separator, and mixing all-time totals with as-of availability. Reset filters and reconcile row grain before changing formulas. Review source hashes through the public library; fictional entity names do not anonymize or identify original vendors.

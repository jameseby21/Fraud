# Power BI Desktop track

These are reproducible build instructions and editable M/DAX sources, not a prebuilt or validated PBIX. Power BI Desktop is a separate application; the web app does not execute it. Use the same CSV and lesson checks as Python/R. Save local PBIX files under ignored output/.

## Import and model (orientation, quality)

Get Data > Text/CSV > select data/learning/transactions.csv > Transform Data. Name the query `Transactions`. Set IDs, supplier, dimensions, currency and synthetic to Text; amount_cents to Whole Number; dates to Date. Import the dates using ISO/year-month-day parsing. Confirm 6,000 rows. Keep all rows until the exercise asks you to filter. Do not remove duplicates.

Alternatively create a text parameter `FixturePath` with the absolute CSV path, then paste `transactions.pq` into a blank query's Advanced Editor. The path is local and machine-specific; do not commit a private absolute path. The query adds AmountUSD, DelayDays and InvoiceMonth. Add measures from measures.dax to the Transactions model table. There are no relationships to define for this single-table introduction.

Create a table with supplier, invoice_id, and Row Count. Use a visual filter Row Count > 1. Include transaction_id in a separate detail table so learners can inspect the two records without changing the grouping grain.

## Visual recipes (comparison, timing, summaries, capacity)

| Family | Field wells and choices | Question / check |
| --- | --- | --- |
| Bar | category axis, Total USD values; start axis at zero | Compare category totals; reconcile to grand total |
| Line | InvoiceMonth axis, Total USD values; sort ascending | Invoice timing; 12 months, not a payment-year filter |
| Distribution | Create AmountUSD bins with a chosen fixed size, count transaction_id | Count totals must sum to 6,000; record bin size |
| Scatter | X AmountUSD, Y DelayDays, transaction_id as detail/Values depending on version; do not summarize individual coordinates | Highest amount USD 275,000; one delay above 90 days |
| Box summary | Matrix by category with Min USD, Q1 USD, Median USD, Q3 USD, Max USD | Native table fallback avoids a third-party visual; compare spread |
| Heatmap | Matrix rows department, columns category, Total USD; background conditional formatting plus printed values | 16 populated cells; label color scale and units |
| Pareto | Line and clustered column: region axis, Total USD columns, Cumulative Region Share line; sort descending Total USD; line percent on secondary axis | Final cumulative share 100%; note ranking context |

Use supplier/category/date slicers and a detail table. Include a reset-filters bookmark after configuring default filters. Titles must state USD, invoice-month vs payment-month, and active filter context. Use labels plus color, readable text, and keyboard-friendly ordering. A box-summary matrix is supplied instead of claiming a native boxplot.

## Threshold review (thresholds)

Duplicate the Transactions query. Group by supplier and invoice_date with Count Rows, Sum amount_cents, and Max amount_cents. Keep Count Rows >= 3, Sum > 1000000, Max < 1000000. The result has five supplier-days: one planted group totaling USD 29,700, plus four incidental background candidates. Join back on supplier and invoice_date to inspect transaction IDs. Distinct invoices on different months with the same amount are not repeated invoices.

## Memo and feedback (review)

Export or copy filtered transaction IDs into a memo with the source hash, tool version, exact grouping/filter criteria, benign alternatives and next-evidence request. Use ../templates/review.md and ../templates/feedback.md. A screenshot alone does not preserve a reproducible filter definition.

## Common issues

- Values 100 times too large: divide cents by 100 once, then format as currency. Currency formatting alone does not perform conversion.
- Wrong count: check Count vs Distinct Count, filters, auto date hierarchy, and visual grain. A table with transaction_id cannot expose repeated invoice groups by count.
- Locale errors: use explicit ISO date parsing in the supplied query. Avoid guessing month/day order.
- Pareto curve differs: Cumulative Region Share respects region selections; reset slicers for comparison. Ties use alphabetical region order.
- R/Python totals differ: compare 6,000 rows, input hash and cents totals before changing formulas.
- UI names differ by Desktop version: use the field purpose described above and record your installed version in feedback.

Official reference: [Microsoft file imports](https://learn.microsoft.com/en-us/power-bi/connect-data/service-get-data-from-files). Desktop execution and visual usability require manual validation; no successful Power BI run is claimed yet.

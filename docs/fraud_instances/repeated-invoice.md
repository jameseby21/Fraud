# Repeated invoices (forensic-v2 and payments-v1)

Group by supplier identity plus invoice_id, not transaction_id or amount alone. Each dataset contains a deliberately repeated invoice with two payment rows; invoices remain a separate one-row-per-invoice table in v2. Reconcile grain before joins and preserve both payment IDs.

Possible explanations include duplicated extraction, staged payments, credit/rebill activity or actual double disbursement. Independent bank records and invoice versions distinguish these. A duplicate reference is a data-quality/review issue until corroborated. See the quality and evidence-brief lessons and separate version-specific answer keys.

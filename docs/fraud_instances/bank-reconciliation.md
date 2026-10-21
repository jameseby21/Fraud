# Bank reconciliation (forensic-v2)

Join payments and bank_entries on transaction_id. Their keys are unique. Compute -signed_amount_cents minus amount_cents; exactly one fictional pair differs by 500 cents. Bank entries use negative debits and become available on posted_date; payment records have a separate available_on field.

The two synthetic tables are independently shaped for a reconciliation exercise, not independently authenticated real sources. Fees, timing, reversals or data-entry errors are alternatives. Show unmatched IDs as well as numeric differences. This pattern is inspired by the need for corroboration, not asserted as a measured Madoff payment.

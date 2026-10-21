# Hidden round sums (forensic-v2)

Grain: supplier_id + payment_date. Count >= 3 and sum(amount_cents) modulo 1,000,000 equals zero. Twelve planted four-payment groups each total USD 10,000; individual members have nonzero cents. They are distributed through the chronological table with random transaction IDs. The round modulus is fictional, not a legal threshold.

Run `from forensic_fixture import public_case, round_groups; groups = round_groups(public_case()['payments'])`. Join candidate keys back to invoices and bank entries. See the round-sums lesson and the separate instructor answers for exact IDs. Do not search for answer labels in learner data.

Controls/limits: fixed contracts, settlement batches and aggregation choices can produce round totals. Compare whole-dollar source values and recurring services. Searching many moduli/windows creates more accidental matches; retain all tested criteria. No calibrated false-positive rate or guilt score is supplied. Required next evidence includes contracts, delivery records and independently obtained settlement support.

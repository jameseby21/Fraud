# Forensic practice case, version 2.0.0

[Root README](../../../README.md) is canonical. Business/contact names are invented; resemblance to real identities is coincidental. Exact public numeric facts are reassigned to fictional objects, not anonymized real transactions. No allegation concerns the source organizations.

| Table | Rows / key | Purpose |
| --- | --- | --- |
| entities.csv | 120 / supplier_id | Persistent fictional business/contact names, category, region, terms and account |
| payments.csv | 12,000 / transaction_id | Ledger-like rows, supplier/invoice keys, cents and date availability |
| invoices.csv | 11,999 / invoice_id | One invoice may have multiple payment rows |
| bank_entries.csv | 12,000 / bank_entry_id | Signed debits, transaction/account keys and posting date |

Unfiltered payment total: **30,341,455,858 cents (USD 303,414,558.58)**, including planted patterns and apparent repeats. Do not delete rows merely to reach that number.

Background amounts are copied exactly from 1,000 retained federal award records, sampled with replacement and inverse-square-root-of-cents weights. This creates a small-value-heavy long tail while preserving selected numeric facts. Names, pairings, dates, categories, terms, methods and IDs are fabricated. Dates are weekday-aware; delays vary with terms. This is not a representative fitted payment model.

`instructor/lineage.json` maps each payment to source ID, row, record ID and raw hash, or marks fabricated changes. The duplicated payment has a separate transformation label. `manifest.json` records version, seed, pool hash and assumptions. Refreshing the pool requires reviewed dataset, lesson, documentation and expectation changes. The simple payments-v1 fixture remains unchanged.

The separate public key lists round sums/individuals, a uniform cohort, repeated invoices, one bank mismatch and a benign recurring-service control. It is educational separation, not secrecy. Random IDs and ordinary date ordering keep targets away from a conspicuous answer block. The [instance library](../../../docs/fraud_instances/README.md) documents criteria and controls. Round figures/digit changes are review signals only; the CDF distance is descriptive, not a p-value. Benford assumptions are not established.

```sh
python record_library.py verify
python forensic_fixture.py build
python forensic_fixture.py verify
```

Run offline from the root. For mismatched hashes/totals inspect source revisions and diffs before rebuilding. Use integer cents; avoid invoice-join fan-out; bank debits are negative. `public_case('2024-02-01')` excludes unavailable records and never loads instructor answers/lineage.

The [practicum](../../../courses/forensic-practicum/evidence-brief.md) combines real documentary review and fictional joins. Legal sources motivate corroboration; these tables do not reconstruct actual Madoff activity. Original documents and reuse are documented in the [record library](../../../docs/library/README.md).

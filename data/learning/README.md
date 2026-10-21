# Practice transactions, version 1.0.0

6,000 entirely synthetic payment-like records. Start with `transactions.csv`; the `instructor/` folder contains spoilers, provenance, and bootstrap lineage. None of these fabricated transactions describes a real organization or real misconduct.

Run `python learning_fixture.py verify` from the repository root. Rebuild offline with `python learning_fixture.py build`. The retained input is `data/spending/awards.csv`, whose original public API bytes and reuse documentation are described in [DATA_SOURCES.md](../../DATA_SOURCES.md). No new download is needed. Sampling uses obligation magnitudes from a nonrepresentative top-award snapshot, with replacement; it does not reconstruct real invoices, preserve economic distributions, or estimate prevalence. It is a pedagogical bootstrap, not inferential resampling of a representative payment population.

| Field | Meaning |
| --- | --- |
| transaction_id | Unique synthetic row identifier; use in review notes |
| invoice_id | Synthetic invoice reference; repeated references may need review |
| supplier | Fictional supplier, unrelated to the source recipient |
| department, category, region | Fabricated categorical dimensions |
| invoice_date, payment_date | ISO dates; payment may occur in the next calendar year |
| amount_cents | Integer USD cents; no floating-point currency storage |
| currency | USD throughout; no currency conversion needed |
| synthetic | Always True; preserve this field in exports |

Rows are transaction records, not necessarily unique invoices. Never delete apparent duplicates before establishing what the row represents. The deliberately visible row ordering makes this an introductory exercise; randomized blind evaluation belongs in a later dataset version. The public key is not a hidden exam or a model validation set.

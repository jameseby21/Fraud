# Public record library

[Root README](../../README.md) is canonical. Browse http://127.0.0.1:8765/records. `data/library/sources.json` is the reviewed registry; `index.json` is the generated latest-view catalog. The existing 20 historical findings and five modern priorities remain in `data/cases.json`; this supplement preserves their evidence standards.

## Intake and supplementation

```sh
python record_library.py import-existing
python record_library.py fetch
python record_library.py fetch --source madoff-peter-information --refresh
python record_library.py build
python record_library.py verify
```

`fetch` skips retained IDs by default. `--refresh` appends a revision for changed bytes/request identity; unchanged input is idempotent. Previous hashes and bytes remain. Failed attempts create no evidence revision. A single-writer lock prevents concurrent ingestion; inspect a stale lock after interruption rather than deleting it automatically.

`seed` recreates the starter registry, so review its diff before replacing manual extensions. To supplement a case, add a stable source ID, case ID, document type, title, official HTTPS URL, publication date or null, reuse basis and policy URL; fetch that ID and rebuild. Host extensions need access/reuse review and tests. No authentication, CAPTCHA bypass, private databases or unreviewed mirrors are used.

## Structure

- `raw/<sha256>.<type>`: original bytes, never normalized in place.
- `revisions.jsonl`: source, request body/digest, type, URL, retrieval/recording time, reuse basis, hash and predecessor.
- `attempts.jsonl`: successful and unavailable network attempts.
- `index.json`: registered records, including unavailable sources, and latest retained revision.
- `amount_pool.json`: exact positive financial amounts with source ID/hash, raw row index and source record ID.

GET records can import previously hashed bytes. POST records cannot reuse a response just because URLs match. Each financial page has its own source ID and request identity. Verification checks raw hashes, revision chains and byte-for-byte reproduction of derived index/value pool.

## Meaning, coverage and reuse

The library distinguishes official reports, government pleadings, court transcripts and financial records. The Peter Madoff plea transcript and information supplement the broader Madoff case; they are not Bernard Madoff's own plea. A charging instrument establishes allegations at filing. A transcript records proceedings, not a reconstructed transaction ledger.

Retained: 15 prior reports, two new legal PDFs and ten financial API pages. Ten registered report URLs remain unavailable; see the index and attempt log. This is not complete financial-ledger coverage for every case.

The pool contains 1,000 federal contract obligation records (977 distinct amounts) from ten 100-row pages, a 2025 activity filter, and USD 10-250,000 amount bounds. They are total award obligations, not invoices or calendar-year cash spending. Ordering by Award ID is nonrepresentative; upstream changes can shift pagination. Preserve the snapshot rather than claiming a natural payment population. Fictional reassignment of exact values must retain lineage and does not reconstruct an original transaction.

[DOJ's policy](https://www.justice.gov/legalpolicies) permits copying/distribution by default unless otherwise indicated. No contrary copyright notice was found in the reviewed transcript text. Preserve original notices; court/third-party materials are not relicensed as project CC0. Public accessibility alone does not authorize every future exhibit or reporter product. [GovInfo](https://www.govinfo.gov/about/policies) also warns that government publications may contain copyrighted inserts. New sources require individual review.

## Debugging and course trajectory

HTTP 422 may indicate a page-size error; the reviewed financial endpoint accepts at most 100 rows. HTTP 403/challenges remain unavailable. Never archive an error page as evidence. A verification failure needs review of hashes, requests and predecessor chains, not edited expected hashes. Rebuild only after reviewing input changes.

Learners first identify document type/date/author and a precise page/paragraph locator, then distinguish the recorded fact from an inference. Use the mechanism to design a fictional financial exercise and benign counterexample. Real facts remain here; fictional sequences and altered measurements remain in the exercise library. No automated legal-outcome inference is performed.

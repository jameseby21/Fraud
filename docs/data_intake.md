# Reusable source intake contract

[Root README](../README.md) is canonical. All new data sources require an explicit registry entry, provenance, tests, reuse review and documented incremental behavior. The shared engine is `record_library.py`; sports sources are configuration in `data/library/supplemental_sources.json`, merged into the standard registry by `seed`. The original government-record workflows continue using that engine.

## Modular boundaries

| Component | Responsibility |
| --- | --- |
| Source registry | Stable source ID, URL, publication/version/DOI, reuse basis and license, optional request payload, expected checksum and CSV contract |
| Direct adapter | Bounded HTTPS request with timeout, checked redirects and conditional HTTP validators where supplied |
| Mendeley file-list adapter | Small version/file-ID metadata request; compares published checksum before downloading a changed file |
| Shared validation | HTTPS allowlist, response size/type, declared CSV columns/row count, optional pinned digest, retained-byte verification |
| Shared storage | Content-addressed original files, per-source revision chain, UTC retrieval/recording timestamps and append-only attempt log |
| Dataset module | Source-specific interpretation, finite-value parsing, missingness, denominators and reproducible derived tables; never mutates raw data |

New documented sources belong in the registry, not ad-hoc network calls in lessons or notebooks. Switch URL, version, file ID, schema and attribution in configuration when the existing adapter fits. A new protocol needs a small adapter and failing contract tests before implementation. Never silently accept an unknown type, redirect host, changed pinned version or schema drift.

## Incremental behavior and limits

By default direct sources already retained are skipped. Explicit refresh sends stored ETag/Last-Modified validators for the same GET URL when available; HTTP 304 reuses locally verified bytes and logs `unchanged`. The file-list adapter checks metadata even on normal fetch and skips unchanged payloads. Changed bytes append a revision with a superseded hash; prior files remain intact. Identical bytes do not produce duplicate revisions.

Incremental means source-file/page granularity here. Sources without validators or a published checksum require a bounded download on refresh to discover whether content changed. The existing paginated USAspending value sample has bounded request pages; it is not a transaction-level CDC pipeline. No source is claimed to support row-level deltas, deletions or live monitoring unless its adapter explicitly implements and tests them.

The retained source-file view and dataset builds are separate. Raw bytes are never overwritten by a transformed CSV; every derived artifact identifies source ID/hash and transformation rules. New source versions and changed analytical definitions require reviewed rebuilds, updated lessons, known checks and docs. Intake failures preserve the latest successful revision without pretending it was refreshed.

## Tests and operational checks

Run `python -m unittest tests.test_source_adapters tests.test_record_library` for CSV schema checks, pinned digest failure, source change/revision chains, idempotence, metadata-only refresh, cache corruption, HTTP-304 reuse and logged failure. Dataset tests independently verify row grain, observed values, derived summaries, empty groups, missing data and reproducibility.

Run `python record_library.py verify` offline and the full repository checks before publishing. Review the staged raw-data and registry diff manually, preserve attribution, and inspect the append-only attempt log for unavailable sources. The write lock prevents concurrent revision writers; a stale lock needs inspection. The engine is a local research library, not a multiworker queue.

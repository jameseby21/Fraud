# Public data and provenance

Only public government records, original curated factual metadata, and clearly marked synthetic exercises are included. No paid feeds, credentials, private account records, or confidential investigation material are required.

| Artifact | Contents | Interpretation |
| --- | --- | --- |
| `data/cases.json` | 20 distinct historical cases and 5 modern research priorities with official sources | Curated factual paraphrases, not original court datasets |
| `data/evidence.jsonl` | 25 source-backed statements, event dates, and availability dates | Generated from the catalog; `synthetic: false` identifies a statement about a real source, not independently verified underlying transactions |
| `data/synthetic_replays.jsonl` | 60 fabricated observations across 20 exercises | Explicitly synthetic; numeric values and thresholds are invented |
| `data/raw/` | Successful source downloads named by SHA-256 | Exact retrieved bytes; not all sources were downloadable |
| `data/intake_log.jsonl` | Successful and unsuccessful download attempts | Append-only history with timestamps and failure reasons |
| `data/spending/awards.csv` | 50 actual public federal contract awards | Unlabeled, nonrepresentative sample; no fraud inference |
| `data/spending/provenance.json` | API request, retrieval time, response hash, interpretation | Future responses may change as agencies revise data |
| `data/build_manifest.json` | Catalog and derived-artifact hashes | Detects changes; does not establish source truth |

The first full intake archived 15 of 25 case sources; 10 were unavailable. See the log for exact results. Curated statements were researched through publicly accessible official pages, including pages the direct downloader could not retrieve. These are recorded as human-curated paraphrases, never as downloaded originals. Re-running intake may change raw coverage.

## Historical evidence

The cases are Madoff, Stanford, Petters, Rothstein, FTX/Bankman-Fried, Theranos/Holmes, Enron/Skilling, WorldCom/Ebbers, Tyco/Kozlowski and Swartz, Adelphia/Rigas, Peregrine/Wasendorf, Refco/Bennett, Bayou/Israel, ZeekRewards/Burks, TelexFree/Merrill, OneCoin/Greenwood, BitConnect/Arcaro, Volkswagen emissions, MSMB/Shkreli, and Galleon/Rajaratnam.

Each entry scopes the criminal finding to the identified subject and cited government source. Settlements without admissions are not used as proof for this historical group. Findings do not extend automatically to every associate, every allegation, or current custody status. Material distinctions include Skilling's revised sentence and reversal of one Rigas bank-fraud count. This is not a complete current appellate docket. URLs and dates appear in the catalog and app; unknown publication dates remain unknown.

## Five modern priorities

These are editorial research selections based on documentation, analytical tractability, and relevance, not a ranking of likely fraud. Source review: October 21, 2026; no continuous legal monitoring is implemented.

1. **Amazon Sponsored Ads pricing:** allegations about auction surcharges. [FTC case](https://www.ftc.gov/legal-library/browse/cases-proceedings/amazon); [company response](https://www.aboutamazon.com/company-news/amazon-ftc-sponsored-ads-lawsuit-response), linked rather than copied.
2. **Uber One:** alleged consent, billing, and cancellation issues. [FTC case and complaints](https://www.ftc.gov/legal-library/browse/cases-proceedings/2423092-uber-ftc-v). Full independent defense collection is incomplete.
3. **JustAnswer:** alleged subscription disclosure and consent issues. [FTC case](https://www.ftc.gov/legal-library/browse/cases-proceedings/justanswer). Full defense collection is incomplete.
4. **LA Fitness:** alleged cancellation obstacles. [FTC announcement](https://www.ftc.gov/news-events/news/press-releases/2025/08/ftc-sues-la-fitness-making-it-difficult-consumers-cancel-gym-memberships) and [dated litigation report](https://www.ftc.gov/system/files/ftc_gov/pdf/litigation-status-report-june-2026.pdf). The company's disagreement and claimed online cancellation option are noted; full defense collection is incomplete.
5. **Personalized pricing transparency:** an industry question, not an allegation against a selected company. [FTC staff update](https://www.ftc.gov/policy/advocacy-research/tech-at-ftc/2025/01/surveillance-pricing-update-work-ahead). Public research summaries use hypothetical examples; confidential firm-level study submissions are not available here.

No fabricated incriminating numbers, fraud labels, or guilt scores are attached to these entries. Each gives a question, proposed method, needed data, alternatives, and coverage gaps. An official complaint supports the existence of allegations, not their truth. Missing defense coverage is a limitation, not evidence against a subject.

## Real public award sample

The script uses the official [USAspending API](https://api.usaspending.gov/docs/intro-tutorial) and [Spending by Award contract](https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/search/spending_by_award.md). The included query selects contract types A-D matching a January-December 2025 activity window, ordered by total award amount, limited to 50 rows. It is neither random nor representative.

`total_award_obligation_cents` is the endpoint's total award obligation, not cash disbursed, contract ceiling, or spending solely during 2025. An award can begin years before the filter window. Values reflect the downloaded snapshot and may be revised upstream. Decimal arithmetic preserves cents. No private customer financial records or personal narratives are collected.

These records support ingestion and quality checks. They are unrelated to the case findings and contain no fraud ground truth. Award size, agency, and recipient names do not establish wrongdoing. Award-level activity is not a transaction stream; a future procurement replay needs an appropriate dated transaction source.

## Reuse

The repository uses GPL-3.0 as selected in its GitHub initialization. The original MIT notice remains in LICENSE-MIT.txt. Original curated metadata and synthetic observations are CC0-1.0; see `data/LICENSE.md`. External documents retain their original status. Public access is not a blanket license for third-party photos, logos, exhibits, or site assets.

The [DOJ copyright policy](https://www.justice.gov/legalpolicies) generally permits copying its information with exceptions for third-party materials and protected seals. Raw HTML is an archival response, not a reusable visual asset library. Government source attribution implies no endorsement. The USAspending API software license concerns its code, not every upstream record; the normalized sample preserves public federal spending facts with attribution and provenance.

## Intake

```powershell
python intake.py verify
python intake.py build
python intake.py spending --limit 50
python intake.py sources --case madoff
python intake.py sources
```

`verify` and `build` work offline. Network commands require internet access. `sources` exits 1 if any source is unavailable, retaining successes and logging failures without bypassing restrictions. It enforces an HTTPS host allowlist, redirect validation, response limits, content checks, content-addressed storage, and bounded retries for transient errors. Forbidden requests are not retried automatically.

Refreshes append history and create new raw artifacts. Current CSV/provenance files reference the latest successful spending response. Offline verification reconstructs the CSV from retained bytes and verifies hashes. Publication dates and legal findings require manual review; fetching a document does not silently change a label.

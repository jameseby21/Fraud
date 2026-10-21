# Investigation and career foundation

## Product principle

Make methods inspectable and evidence traceable. Present what a source records, what analysis suggests, and what remains unknown as separate statements. Avoid unsupported certainty and false balance: well-supported facts can be stated clearly, with scope and attribution. Publish a correction history and explain material disagreements. Apply equal evidence standards to every subject. Code is MIT-licensed; original curated and synthetic data is CC0. Preserve external source terms.

## 1. Reproducible demonstration (implemented)

Deterministic fixture, explainable rules, source references, separate answer key, false-positive and missed-participant examples, local dashboard, and downloadable report. The fixture uses investment-like flows inspired by the general problem of paying contributors from pooled inflows; it does not recreate the Madoff case or assert that the pattern identifies a Ponzi scheme.

The library adds 20 sourced historical findings, 11 illustrative rule families with synthetic replay steps, five modern research priorities, and 50 real unlabeled public awards. Source statements and synthetic inputs remain separate. Complete historical event ledgers and validated live findings remain future work; see DATA_SOURCES.md and MODEL_CARD.md.

## 2. Select one investigable question

Choose a data domain before choosing a complex model. Candidates for research include procurement awards and disclosed supplier relationships, investment solicitation claims compared with official disclosures, or public enforcement cases used as retrospective benchmarks. Confirm current coverage, terms, and available fields before selecting a source. Public records often lack transactions or ultimate ownership, so the current rules may not apply.

Define the target behavior, unit of analysis, observation window, entity resolution approach, lawful data access, alternative explanations, and what evidence could falsify the hypothesis. Prioritize sources with stable identifiers and downloadable records. Do not equate missing registration, unusual returns, shared addresses, or graph proximity with wrongdoing.

## 3. Build real-data infrastructure after source selection

- Immutable raw snapshots outside Git, retrieval timestamps, original URLs, source terms, file hashes, and record-level lineage.
- Explicit schemas, currency handling, duplicate detection, time normalization, coverage checks, and versioned transformations.
- Entity resolution with confidence and reversible merges; retain original names and identifiers.
- Cases with observations separated from hypotheses, corroboration, counterevidence, reviewer notes, and append-only event history.
- Authorized access controls and retention policies before introducing sensitive data. The local demo is not ready for it.

## 4. Validate before pursuing a live lead

Reconstruct a historical case using only information available before public exposure. Use benign comparators, temporal holdouts, and entity-disjoint evaluation. Measure precision at an investigation budget, false-positive burden, detection delay, and missing coverage. Account for selective labels: absence of enforcement does not establish innocence. Compare transparent baselines before ML; assess calibration and distribution shift where probabilities are claimed.

## 5. Investigate and corroborate

Move from a reproducible anomaly to a case only when independent evidence supports a specific hypothesis. Keep a ledger of facts, claims, source reliability, alternative explanations, and unresolved questions. Produce a private, factual dossier suitable for review by an appropriate investigator or authority; an automated flag is not an accusation. No outreach, reports, surveillance, or real-person targeting is implemented in this foundation.

## Career deliverables

Prepare a concise case memo, reproducible analysis, architecture overview, evaluation report showing mistakes, and a walkthrough of one benign explanation. Describe synthetic work as synthetic everywhere. These artifacts can demonstrate SQL/Python analysis, investigative reasoning, graph analysis, model validation, and evidence communication without claiming a fabricated enforcement result.

## Next decision

Choose the first real-data domain and jurisdiction, then verify available official sources and build one retrospective benchmark. That decision determines the ingestion adapter, data model, and relevant detection hypotheses.

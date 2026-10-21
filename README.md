# Fraud

An open-source investigation workbench: transparent methods, traceable evidence, honest uncertainty. It supports public-interest research and a portfolio for fraud analytics or financial intelligence work.

## Public purpose and evidence standard

The intended project is open source and presents evidence without claiming final authority. Every material finding should link to its source and distinguish recorded facts, analytical inferences, hypotheses, and unresolved questions. Show counterevidence, coverage gaps, and corrections alongside findings. An anomaly is a reason to investigate, not a finding of guilt. Synthetic examples must remain visibly labeled.

Apply the same evidence standards regardless of wealth, influence, industry, or affiliation. Code follows the remote repository's [GPL-3.0 license](LICENSE); the initial MIT notice is retained in [LICENSE-MIT.txt](LICENSE-MIT.txt); original curated metadata and synthetic observations are [CC0-1.0](data/LICENSE.md). External documents retain their original status. Public code does not imply that private source data or identifying case material should be published.

## Run

Python 3.12+, no external dependencies:

```powershell
python app.py
```

Open **http://127.0.0.1:8765/library** for the case library, or **http://127.0.0.1:8765/** for the transaction demo. Stop with Ctrl+C. Included data works offline; external citations and refreshes require internet access.

```powershell
python -m unittest discover -s tests -v
python intake.py verify
```

The dashboard offers a searchable alert queue, supporting transaction records, alternative explanations, fixture metrics, and JSON export with a source digest and engine version. The server binds to loopback only. This prototype is not an authenticated multiuser system and must not be exposed to a network.

## Case library and public data

- **20 historical cases:** sourced criminal findings, narrowly scoped outcomes, a date-gated source view, and case-inspired mechanism exercises.
- **Replay controls:** step, back, play/pause, revealed inputs, arithmetic, thresholds, alternatives, model version, and input hashes.
- **Five modern priorities:** public allegations or research questions with proposed methods, sources, counterevidence, and data gaps. No guilt scores.
- **Public intake desk:** 50 real USAspending contract records, search, CSV download, request provenance, and source-download coverage.

Historical findings are real; numeric mechanism observations are fabricated. Each source chronology currently has one curated report, not a complete historical event ledger. The exercises do not establish public-data early detection, real-world model accuracy, or a finding about an active fraudster. The real award sample is unlabeled and unrelated to the case findings.

## Intake and reproducibility

The public-data desk also runs eight read-only quality checks with CSV row references, a semantic status message, and a downloadable JSON report. It checks data readiness rather than predicting fraud. See [CHECKPOINTS.md](CHECKPOINTS.md) for test-first delivery history and [FEATURE_BACKLOG.md](FEATURE_BACKLOG.md) for proposed future checkpoints.

```powershell
python intake.py build
python intake.py verify
python intake.py spending --limit 50
python intake.py sources --case madoff
python intake.py sources
```

`build` regenerates curated evidence and synthetic streams offline. `verify` checks their reproducibility, raw-download hashes, and reconstruction of the award CSV from retained bytes. `spending` refreshes the real public sample. `sources` attempts official downloads, retains successes, logs blocks, and exits nonzero when a source is unavailable. No API key or private data is required. See [DATA_SOURCES.md](DATA_SOURCES.md) for source coverage, field meanings, provenance, and reuse.

After staging data changes, run `python scripts/check_staged_data.py` before committing. The repo preserves original data bytes across operating systems so Git line-ending conversion cannot invalidate source hashes.

## Optional browser usability check

With Node 22+ and Microsoft Edge installed:

```powershell
node --check web/library.js
python scripts/check_browser.py
```

This starts an isolated local server and checks replay, date gating, search, separation of historical and modern entries, public-data filtering, and mobile width. Screenshots and a disposable browser profile go to ignored `output/`. Set `FRAUD_BROWSER_PATH` for another installed Chromium browser. No browser or package download is required.

## What the example establishes

`fraud.py` constructs ordinary retail activity, an investment-like flow, circular transfers, and a benign settlement lookalike. Rules inspect only transactions; synthetic labels are used separately for evaluation. Amounts use integer cents. Rules are illustrative hypotheses, not trained models or calibrated probabilities.

Cycle alerts attach to the temporally first sender, so the entity-level answer key deliberately exposes missed participants. The benign cycle deliberately exposes a false positive. These are useful limitations to inspect, not production performance estimates. Fixtures are designed around the rules and cannot establish generalization.

The SHA-256 identifies the serialized fixture transactions; it is not proof that a real source is authentic. The export includes fabricated answer labels and is a demo artifact, not a legal evidence package. No case state is persisted yet.

## Direction

The longer-term objective is to identify credible, independently corroborated leads about active financial misconduct using public or explicitly authorized data, and prepare material suitable for qualified investigators. Discovery or enforcement outcomes cannot be promised. A second success path is a portfolio demonstrating the skills needed for fraud analytics and financial intelligence roles.

Next, select a public-data domain and build a source-specific historical benchmark with defensible availability dates, benign comparisons, and independent labels. See [ROADMAP.md](ROADMAP.md), [MODEL_CARD.md](MODEL_CARD.md), and [CONTRIBUTING.md](CONTRIBUTING.md). No remote or initial commit has been created; the repo remains on `main` awaiting its remote URL.

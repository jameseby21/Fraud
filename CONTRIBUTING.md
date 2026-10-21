# Contributing

Every development checkpoint must also leave usable course material: document the question, prerequisites, inputs and provenance, exact commands, expected results, reasoning, limitations, debugging steps, and common issues. Record failing acceptance tests, implementation results, regressions, and delivery state in `docs/checkpoints/`. Every lesson needs an exercise, a checkable outcome, hints separated from solutions, and a feedback prompt. Keep learner data separate from instructor answers. Document tool-specific validation honestly; do not call an unexecuted Power BI or R example tested. Course examples must use public or synthetic data and cannot include private research notes.

Apply equal evidence standards regardless of influence, wealth, industry, affiliation, or institutional role. Select specific conduct and relevant public records; do not infer wrongdoing from identity or association.

Each case needs a stable ID, primary public source, publication date or explicit unknown, narrowly scoped finding or allegation, limitations, alternatives, and review date. Preserve acquittals, reversals, dismissals, responses, and corrections. An official complaint establishes what was alleged, not that it occurred.

Only public, reusable data belongs in tracked artifacts. Retain original source terms and attribution. Do not add credentials, private logs, personal contact dossiers, or confidential records. Link third-party responses rather than copying them without a reuse basis. Document access and reuse before extending the intake host allowlist.

Synthetic examples need visible labels and machine-readable flags. Do not generate incriminating measurements for unresolved real subjects. Rules need input IDs, a version, an explanation, benign alternatives, and temporal-leakage tests. Fixture performance is not production accuracy.

After catalog changes:

```powershell
python intake.py build
python intake.py verify
python -m unittest discover -s tests -v
node --check web/library.js
```

Node is optional for Python/data-only changes. Browser changes should run the optional local check in README.md. New findings need human review. Describe material corrections and affected entries in CHANGELOG.md.

Enable local publication gates with `git config core.hooksPath .githooks`. The hooks inspect staged/tracked Git blobs and reject protected private artifacts and selected credential patterns. Run `python scripts/check_publication.py --all` before publishing. Changes to encrypted storage require the full optional-dependency test environment described in SECURITY.md; skipped vault tests are not sufficient validation.

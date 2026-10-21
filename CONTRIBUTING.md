# Contributing

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

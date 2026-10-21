# Data analysis studio

A local course catalog with Markdown lessons, clean Python notebooks, a shared R track, and a Power BI Desktop track. Start the app with `python app.py`, then open http://127.0.0.1:8765/learn. Or read lessons directly on GitHub without running a server.

## Start your first walkthrough

- Choose **Payment review lab**, lesson 1, and Python, R, or Power BI.
- Download or open `data/learning/transactions.csv`. Keep instructor files closed initially.
- Read the question, predict an outcome, complete the task in your chosen tool, then reveal the worked check.
- Use the reference charts to compare your visual choices. Use transaction IDs when recording observations.
- Copy `templates/feedback.md` into ignored `output/` and record what worked, what failed, and what needs clearer teaching. The project owner is the first learner; broader usability remains to be tested.

There are eight introductory lessons: six payment-review lessons and two operational-analysis lessons. The operations course asks allocation and workload questions without a misconduct hypothesis. These are initial course materials, not an accredited curriculum or a claim of learning effectiveness.

Cross-tool reconciliation: unfiltered input has 6,000 rows and totals **1,355,092,995 cents (USD 13,550,929.95)**. The total includes apparent repeats. Use this as an import/filter check, not a target to force by changing the records.

## Choose a tool

Python: Python 3.12 is used by CI. The lesson analysis has no third-party dependencies. Open an `.ipynb` in an existing Jupyter/VS Code environment and select its Python kernel. If you need Jupyter, create a separate course environment (`python -m venv .venv-course`) and install `jupyterlab` there; this optional interactive frontend is outside the hash-pinned vault environment. Do not install course packages into the vault environment. Notebook cells run in the repository root or a nested course directory and contain no saved outputs. The helper analysis uses the full dataset; the SVG scatter preview intentionally displays only 500 rows.

R: see [tracks/r.md](tracks/r.md). The base-R script provides matching exercises and seven chart families in a local PDF. Power BI: see [tracks/powerbi.md](tracks/powerbi.md), with M and DAX sources. A report must still be built and checked in Desktop; no PBIX is supplied or claimed tested.

## Course structure and extension contract

`catalog.json` has a schema version, reusable dataset IDs, course IDs/topics and ordered lessons. A course is a container, a lesson is a question/activity/check/reflection unit, and a track is a tool-specific way to perform it. Dataset versions are independent of UI progress. Add a new dataset rather than hard-coding domain assumptions into navigation. The current analysis/visual adapter in `learning.py` is specific to payments; another domain needs its own adapter and tests, while catalog/navigation/content can be reused.

`scripts/build_courses.py` is the reviewed source of truth for catalog entries, lesson Markdown and notebook cells. Edit it, run `python scripts/build_courses.py`, then review all regenerated diffs. Verify with `python scripts/build_courses.py --verify`. Track guides are separately authored. The app uses a small escaped Markdown subset (headings, paragraphs, lists, tables and fenced code), without raw HTML, remote scripts or a full CommonMark renderer. No notebook code is executed by the web server.

Each lesson requires a question, prerequisites, provenance and grain, an activity, checkable outcomes, debugging help, reflection, and feedback. Include alternative explanations, false positives, and unit/date/filter pitfalls. Separate spoilers from the learner dataset; public answer keys are not secret. Developer checkpoint notes record red/green test evidence and delivery state. Private vault notes never become course content automatically.

## Visualization coverage

| Family | Learning purpose | Current implementation |
| --- | --- | --- |
| Bar | Category comparison, zero baseline | Browser, R, Power BI recipe |
| Line | Time ordering and date-grain choices | Browser, R, Power BI recipe |
| Histogram / bins | Distribution, bin choice and skew | Browser categorical count bins, R histogram, Power BI bins |
| Scatter | Relationship, outliers, limits of causality | Browser 500-row preview, R all rows, Power BI recipe |
| Box / quantile summary | Spread, robust comparison, whisker conventions | Browser min/max box, R Tukey box, Power BI summary matrix |
| Heatmap | Two categorical dimensions | Browser/R chart, Power BI conditional matrix |
| Pareto | Ranking and cumulative composition | Browser/R dual axes, Power BI measures and recipe |
| Detail table | Exact values, row traceability and filtering | CSV/notebook data, Power BI table, existing public-data library |

This is core coverage, not every possible chart. Maps require meaningful geographic coordinates; networks require actual edges; survival, uncertainty bands and model calibration need appropriate outcomes/design. Do not invent those semantics just to add a chart. Additional dataset adapters and lessons should supply them deliberately.

## FAQ and debugging

**Where is my progress?** Only self-reported lesson completion is stored in this browser under a versioned key. It is shared by users of this browser profile and is not a private record. Reset clears it. Browser storage denial makes it temporary; exporting feedback is the durable record.

**The notebook cannot find learning.py.** Open it within the cloned repo, not a detached Downloads folder. The web download is a convenience; it still needs the repo's data and helper module. Check the selected kernel and working directory.

**I see five threshold matches, not one.** Correct. One group is deliberately planted; four background groups happen to match the rule. Investigate the alternatives instead of treating every alert as fraud.

**My totals or counts differ.** Reset filters. Verify 6,000 input rows and the dataset hash. Compare whole cents before currency formatting. Keep invoice-date and payment-date filters distinct. Do not deduplicate before checking the row grain.

**Charts differ between tools.** Check row subsets, bins, axes, aggregation, missing values and boxplot conventions first. Different display defaults can produce different pictures from identical records.

**Can I claim the rule performs well?** You can describe deterministic exercise results and what you learned. There is no representative labeled population or independent holdout, so no generalization or real-world accuracy claim follows.

**How do I report an issue?** Use the feedback template with reproducible steps, sanitized error text, tool version and expected/actual results. Do not paste private research, credentials or confidential data into public issues.

Format reference: [Jupyter notebook format](https://nbformat.readthedocs.io/en/latest/format_description.html). Accessibility choices guide implementation but do not establish blanket WCAG conformance or replace user testing.

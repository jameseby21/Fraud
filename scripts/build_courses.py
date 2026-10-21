"""Generate reviewed Markdown lessons and clean Python notebooks from one source."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

# id, title, question, activity, check, debugging, reflection, chart
COURSES = [
 ('payment-lab', 'Payment review lab', 'fraud', [
 ('orientation', '1. Define the question and inspect provenance',
  'What does one row mean, and which claims can these records support?',
  'Read data/learning/README.md. Import only transactions.csv. Count rows, distinct transaction IDs, suppliers, currencies, and missing values. Record the dataset hash before analysis. Do not open instructor answers yet.',
  'There are 6,000 rows, 6,000 distinct transaction IDs, one currency (USD), and every synthetic flag is True. Dates and supplier identities are fictional. The original records are award obligations, not payment histories.',
  'A missing file usually means the working directory is not the repository root. A changed hash means your input differs; run python learning_fixture.py verify before continuing.',
  'Write a sentence separating a data-quality issue, an analytical anomaly, and evidence of misconduct.', 'bar'),
 ('quality', '2. Validate types, grain, and repeated invoices',
  'Are repeated records necessarily duplicate payments?',
  'Keep transaction_id as text and amount_cents as a whole number. Group by supplier and invoice_id, count rows, then inspect groups with more than one row. Preserve both transaction IDs. Compare dates and amounts. Do not deduplicate first.',
  'One repeated supplier-invoice group has two transaction rows. Record the IDs and a request for supporting documentation. A repeated invoice reference alone cannot establish that money moved twice.',
  'Grouping by amount alone produces false positives, including recurring services. Grouping by transaction_id hides invoice repetition because transaction IDs are unique.',
  'What additional record would distinguish a duplicate extraction from a duplicate disbursement?', 'histogram'),
 ('comparison', '3. Compare amounts and category spread',
  'Which amounts deserve contextual review, and which chart reveals the contrast?',
  'Build category-total bars, an amount histogram, and category box summaries. Compare the full USD scale with a zoomed background view. Retain the full-scale chart alongside any zoom. Inspect the highest amount and explain a benign alternative.',
  'The largest synthetic transaction is USD 275,000. The histogram contains 6,000 observations. Category totals reconcile to the full total. A large capital purchase is a possible benign explanation.',
  'Divide cents by 100 exactly once. The supplied histogram uses unequal-width categorical bins; bar heights are counts, not probability densities. Supplied box whiskers are min/max, not the default Tukey rule.',
  'How could aggregation by category hide a large transaction? What changes when the outlier is retained versus excluded?', 'box'),
 ('timing', '4. Explore time and relationships',
  'Does a delay or a monthly change justify a causal explanation?',
  'Create an invoice-month total line chart. Calculate payment_date minus invoice_date in days. Plot amount versus delay. Filter delays over 90 days and inspect each row. Compare invoice-month and payment-month definitions.',
  'One transaction has a delay over 90 days: 181 days. Monthly invoice totals reconcile to all amounts. Some December invoices are paid in 2026; do not drop them with a 2025 payment-date filter.',
  'ISO date text must become a date before subtraction. Browser scatter previews show the first 500 records only; use the full CSV in your selected tool. Correlation is not causation.',
  'List a dispute, processing delay, and recording error as competing explanations. What time field would you need for an as-of investigation?', 'scatter'),
 ('thresholds', '5. Investigate groups, thresholds, and benign controls',
  'Can aggregation reveal a review pattern invisible in individual rows?',
  'Use a fictional review threshold of USD 10,000. Group by supplier and invoice_date. Select groups with at least three rows, each below the threshold, and combined amount above it. Compare with equal-amount monthly recurring services. Keep the criteria explicit.',
  'Five supplier-days meet this exact rule; only one was deliberately planted: three USD 9,900 rows total USD 29,700. Four incidental background matches are also review candidates. Equal amounts on distinct monthly invoices are a benign control. Neither rule output is a guilt label.',
  'Filter individual amounts before grouping and count rows as well as totals. Do not confuse 10,000 dollars with 10,000 cents. The fictional threshold is an exercise parameter, not a real procurement rule.',
  'What false positives could staged work generate? How would you tune the time window without using the answer key?', 'heatmap'),
 ('review', '6. Write a reproducible review memo',
  'Can another analyst reproduce your observations and challenge your explanation?',
  'Write a memo using courses/templates/review.md. Include input hash, tool version, filters, transaction IDs, alternative explanations, and a next-evidence request. Only then compare with the public instructor key. Use courses/templates/feedback.md to report your experience.',
  'Your memo separates observations from hypotheses and covers the four planted review patterns plus the benign control. State missed items and false positives. This is an open-book deterministic exercise, not an independent model evaluation.',
  'If your totals differ, reset filters, check cents conversion and row counts, and record which input version you used. Opening the key early is fine for learning; disclose it when describing performance.',
  'Which step was unclear or frustrating? What could you reproduce without the guide, and what evidence would you request next?', 'pareto')]),
 ('operations', 'Operational analysis foundations', 'operations', [
 ('summaries', '1. Compare allocation without a misconduct hypothesis',
  'How is synthetic spending allocated across categories and regions?',
  'Reuse the same transactions with a different analytical purpose. Create category bars and sorted regional bars with cumulative share. Compare total and average amounts; report denominators and filter context.',
  'Four categories and four regions are present. Sorted regional cumulative share ends at 100%. Totals reconcile to the same 6,000-row input. Allocation does not measure efficiency or fairness.',
  'Power BI measures respond to slicers. Reset filters before comparing against Python or R totals. Sorted bars plus cumulative share use two distinct axes.',
  'What additional exposure denominator would make comparisons more meaningful?', 'pareto'),
 ('capacity', '2. Explore workload and timing',
  'Which view helps plan review workload rather than accuse a supplier?',
  'Count invoice rows by month and compare counts with monthly amounts. Make a department-category heatmap. Compare delay distributions by category. Explain why monetary volume and transaction count answer different questions.',
  'The department-category grid has 16 populated cells. There are 12 invoice months. The demonstration uses fabricated dates and cannot support a real staffing recommendation.',
  'A sum of amount is not a transaction count. A minimum/maximum box differs from R default boxplot whiskers; label your method and compare quartile values separately.',
  'How would seasonality, missing workload, or changes in staffing affect your interpretation?', 'line')])]

SETUP = '''from pathlib import Path
import sys
root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / "learning.py").exists()), None)
if root is None:
    raise RuntimeError("Open this notebook inside the Fraud repository")
sys.path.insert(0, str(root))
from learning import read_transactions, analyze, render_chart
rows = read_transactions()
summary = analyze()
assert len(rows) == 6000
'''

EXERCISES = {
 'orientation': 'assert len({r["transaction_id"] for r in rows}) == len(rows)\nassert {r["synthetic"] for r in rows} == {"True"}\n',
 'quality': '''from collections import defaultdict
groups = defaultdict(list)
for row in rows:
    groups[(row["supplier"], row["invoice_id"])].append(row["transaction_id"])
repeated = {key: ids for key, ids in groups.items() if len(ids) > 1}
assert len(repeated) == 1
''',
 'comparison': 'largest = max(rows, key=lambda r: r["amount_cents"])\nassert largest["amount_cents"] == 27500000\nassert sum(b["count"] for b in summary["histogram"]) == len(rows)\n',
 'timing': 'late = [r for r in rows if r["payment_delay_days"] > 90]\nassert len(late) == 1 and late[0]["payment_delay_days"] == 181\n',
 'thresholds': '''from collections import defaultdict
groups = defaultdict(list)
for row in rows:
    groups[(row["supplier"], row["invoice_date"])].append(row)
candidates = {key: values for key, values in groups.items() if len(values) >= 3
              and all(r["amount_cents"] < 1000000 for r in values)
              and sum(r["amount_cents"] for r in values) > 1000000}
assert len(candidates) == 5
''',
 'review': 'assert sum(r["amount_cents"] for r in summary["monthly"]) == summary["total_cents"]\n# Write your memo before consulting data/learning/instructor/answers.json.\n',
 'summaries': 'shares = [r["amount_cents"] / summary["total_cents"] for r in summary["pareto"]]\nassert abs(sum(shares) - 1) < 1e-12\n',
 'capacity': 'assert len(summary["heatmap"]) == 16\nassert len(summary["monthly"]) == 12\n'}


def artifacts():
    outputs, courses = {}, []
    for course_id, title, topic, lessons in COURSES:
        entries = []
        for lesson_id, lesson_title, question, activity, check, debug, reflection, chart in lessons:
            md = f'''# {lesson_title}

Estimated time: 20-40 minutes. Prerequisite: basic tables and arithmetic; complete lessons in order. Dataset: data/learning/transactions.csv, version 1.0.0. Every record is synthetic.

## Question

{question}

## Try it

{activity}

Choose Python (the adjacent notebook), R (courses/tracks/analysis.R), or Power BI (courses/tracks/powerbi.md). The shared track guides cover this lesson by ID: `{lesson_id}`. Save your working files in ignored output/, not beside public course assets.

## Check your work

{check}

## Debugging

{debug}

## Reflection

{reflection}

## Record your learning

Copy courses/templates/feedback.md into ignored output/ and record lesson ID, track, expected versus observed result, error text with private values removed, and one improvement. Completion is self-reported; passing a supplied assertion is not evidence of independent mastery.
'''
            outputs[f'courses/{course_id}/{lesson_id}.md'] = md.encode()
            cells = [dict(cell_type='markdown', id='guide', metadata={}, source=md.splitlines(keepends=True)),
                     dict(cell_type='code', id='setup', metadata={}, execution_count=None, outputs=[], source=SETUP.splitlines(keepends=True)),
                     dict(cell_type='markdown', id='practice', metadata={}, source=['Try the task before running the worked check below. Change the criteria, predict the result, then explain the difference.']),
                     dict(cell_type='code', id='worked-check', metadata={}, execution_count=None, outputs=[], source=EXERCISES[lesson_id].splitlines(keepends=True)),
                     dict(cell_type='code', id='visual', metadata={}, execution_count=None, outputs=[], source=[f'svg = render_chart("{chart}")\n', '# Optional in Jupyter: from IPython.display import SVG, display; display(SVG(svg))\n', '# To export: (root / "output").mkdir(exist_ok=True); (root / "output" / "lesson.svg").write_text(svg, encoding="utf-8")\n'])]
            notebook = dict(cells=cells, metadata=dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'), language_info=dict(name='python', version='3.12')), nbformat=4, nbformat_minor=5)
            outputs[f'courses/{course_id}/{lesson_id}.ipynb'] = (json.dumps(notebook, indent=2) + '\n').encode()
            entries.append(dict(id=lesson_id, title=lesson_title, chart=chart, minutes=30))
        courses.append(dict(id=course_id, title=title, topic=topic, dataset='payments-v1', lessons=entries))
    catalog = dict(schema_version=1, title='Data analysis studio', datasets=[dict(id='payments-v1', path='data/learning/transactions.csv', version='1.0.0', synthetic=True)], courses=courses)
    outputs['courses/catalog.json'] = (json.dumps(catalog, indent=2) + '\n').encode()
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    for relative, content in artifacts().items():
        path = ROOT / relative
        if args.verify:
            if not path.exists() or path.read_bytes() != content:
                raise SystemExit(f'Course mismatch: {relative}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print('PASS: 2 courses, 8 Markdown lessons and 8 clean Python notebooks ' + ('verified.' if args.verify else 'built.'))


if __name__ == '__main__':
    main()

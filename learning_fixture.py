"""Versioned, offline teaching fixture. No measurements describe real misconduct."""
import argparse
import csv
from datetime import date, timedelta
import hashlib
import io
import json
from pathlib import Path
import random

VERSION = '1.0.0'
SEED = 20261021
ROOT = Path(__file__).resolve().parent
FIELDS = ['transaction_id', 'invoice_id', 'supplier', 'department', 'category',
          'invoice_date', 'payment_date', 'amount_cents', 'currency', 'region', 'synthetic']


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def build_fixture(source):
    records = list(csv.DictReader(io.StringIO(source.decode('utf-8'))))
    eligible = [r for r in records if int(r['total_award_obligation_cents']) > 0]
    if not eligible:
        raise ValueError('At least one positive source obligation is required')
    rng = random.Random(SEED)
    rows, draws, answers = [], [], []
    start = date(2025, 1, 1)
    for i in range(6000):
        sampled = rng.choice(eligible)
        # Preserve only a bounded magnitude signal, not identities or actual payment histories.
        amount = 10000 + int(sampled['total_award_obligation_cents']) % 440000
        amount += rng.randrange(0, 10000)
        day = start + timedelta(days=rng.randrange(365))
        rows.append(dict(zip(FIELDS, [f'TX-{i+1:06}', f'INV-{i+1:06}',
            f'Practice supplier {rng.randrange(1, 121):03}',
            rng.choice(['Operations', 'Technology', 'Facilities', 'Research']),
            rng.choice(['Services', 'Equipment', 'Supplies', 'Travel']),
            day.isoformat(), (day + timedelta(days=rng.randrange(5, 41))).isoformat(),
            str(amount), 'USD', rng.choice(['North', 'South', 'East', 'West']), 'True'])))
        draws.append({'transaction_id': rows[-1]['transaction_id'], 'source_award_key': sampled['award_key']})

    def mark(pattern, indexes, explanation, disposition='planted_review_pattern'):
        answers.append(dict(pattern=pattern, transaction_ids=[rows[i]['transaction_id'] for i in indexes],
                            explanation=explanation, disposition=disposition))

    for key in FIELDS:
        if key != 'transaction_id':
            rows[1][key] = rows[0][key]
    mark('duplicate_invoice', [0, 1], 'Same supplier, invoice, amount and dates; request supporting documents before interpreting a duplicate as misconduct.')
    for i in [2, 3, 4]:
        rows[i].update(supplier='Practice supplier 121', invoice_date='2025-06-15',
                       payment_date='2025-06-20', amount_cents='990000', department='Operations', category='Services')
    mark('threshold_split', [2, 3, 4], 'Three payments below a fictional USD 10,000 review threshold total USD 29,700 on one supplier-day. Legitimate staged work is an alternative.')
    rows[5].update(amount_cents='27500000', category='Equipment')
    mark('amount_outlier', [5], 'USD 275,000 is deliberately outside the background range; a legitimate capital purchase remains possible.')
    rows[6].update(invoice_date='2025-01-01', payment_date='2025-07-01')
    mark('late_payment', [6], '181 days between invoice and payment; investigate disputes or recording errors before drawing conclusions.')
    for i, day in zip([7, 8, 9], ['2025-03-01', '2025-04-01', '2025-05-01']):
        rows[i].update(supplier='Practice supplier 122', invoice_date=day,
                       payment_date=day, amount_cents='250000', category='Services')
    mark('benign_recurring', [7, 8, 9], 'Distinct monthly invoices for a recurring service have the same amount; amount repetition alone would flag this benign control.', 'benign_control')
    manifest = dict(version=VERSION, seed=SEED, rows=len(rows), synthetic=True,
                    source='data/spending/awards.csv', source_sha256=hashlib.sha256(source).hexdigest(),
                    bootstrap_unit='award obligation magnitude, sampled with replacement',
                    transformation='10000 + (positive obligation cents modulo 440000) + seeded integer jitter [0,9999]; dates and dimensions fabricated; ten rows then edited for exercises',
                    limitations='Nonrepresentative award snapshot, not a fitted financial simulator or real payment data. Seeded patterns are teaching targets, not evidence or estimates of fraud.',
                    draws=draws)
    return rows, answers, manifest


def artifacts(root=ROOT):
    rows, answers, manifest = build_fixture((root / 'data/spending/awards.csv').read_bytes())
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    payload = stream.getvalue().encode()
    manifest['dataset_sha256'] = hashlib.sha256(payload).hexdigest()
    return {'data/learning/transactions.csv': payload,
            'data/learning/instructor/answers.json': json_bytes(answers),
            'data/learning/instructor/manifest.json': json_bytes(manifest)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    args = parser.parse_args()
    for relative, payload in artifacts().items():
        path = ROOT / relative
        if args.command == 'build':
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        elif not path.exists() or path.read_bytes() != payload:
            raise SystemExit(f'Fixture mismatch: {relative}; run python learning_fixture.py build')
    print('PASS: learning fixture ' + args.command + '; 6000 synthetic rows, separate public instructor key.')


if __name__ == '__main__':
    main()

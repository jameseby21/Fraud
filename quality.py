"""Read-only quality checks for the public award sample; never fraud classification."""
import csv
import hashlib
import io
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

VERSION = 'award-quality-1'
CHECKS = [
    ('required_fields', 'Required fields'),
    ('unique_keys', 'Duplicate award identifiers'),
    ('integer_cents', 'Exact integer-cent amounts'),
    ('valid_dates', 'Valid dates and usable start dates'),
    ('date_order', 'Start and end date order'),
    ('currency', 'Supported currency'),
    ('synthetic_boundary', 'Separation of real and synthetic records'),
    ('label_boundary', 'Unlabeled public-data boundary'),
]


def audit_awards(rows):
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        raise ValueError('Expected a list of award records')
    issues, seen = [], defaultdict(list)

    def add(check, code, numbers, field, message, severity='warning'):
        issues.append(dict(id=f'DQ-{len(issues)+1:04}', check=check, code=code,
                           severity=severity, row_numbers=numbers,
                           award_keys=sorted({str(rows[n-2].get('award_key') or '(missing)') for n in numbers}),
                           field=field, message=message))

    for number, row in enumerate(rows, 2):
        for field in ('award_key', 'award_id', 'recipient', 'agency', 'currency', 'total_award_obligation_cents'):
            value = row.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                add('required_fields', 'MISSING_REQUIRED_FIELD', [number], field,
                    f'Missing {field}. Check this CSV row against the retained source before analysis.')
            elif field != 'total_award_obligation_cents' and not isinstance(value, str):
                add('required_fields', 'INVALID_TEXT_FIELD', [number], field,
                    f'{field} must be text; do not silently coerce an identifier or name.')
        key = row.get('award_key')
        if isinstance(key, str) and key.strip():
            seen[key].append(number)
        amount = row.get('total_award_obligation_cents')
        missing_amount = amount is None or (isinstance(amount, str) and not amount.strip())
        if not missing_amount:
            valid_amount = type(amount) is int or (isinstance(amount, str) and re.fullmatch(r'-?[0-9]+', amount) is not None)
            if not valid_amount:
                add('integer_cents', 'INVALID_CENTS', [number], 'total_award_obligation_cents',
                    'Amount must be an integer number of cents; no float, exponent, or nonfinite coercion is performed.')
            elif int(amount) < 0:
                add('integer_cents', 'NEGATIVE_OBLIGATION', [number], 'total_award_obligation_cents',
                    'Negative obligations can reflect a legitimate adjustment. Reconcile the source modification history.', 'info')
        parsed = {}
        for field in ('start_date', 'end_date'):
            value = row.get(field)
            if not value:
                if field == 'start_date':
                    add('valid_dates', 'MISSING_START_DATE', [number], field,
                        'No start date is available for time-based analysis. An absent optional end date is allowed.')
                continue
            try:
                parsed[field] = date.fromisoformat(value)
                if parsed[field].isoformat() != value:
                    raise ValueError('Use YYYY-MM-DD')
            except (ValueError, TypeError):
                parsed.pop(field, None)
                add('valid_dates', 'INVALID_DATE', [number], field, 'Expected an actual calendar date in YYYY-MM-DD format.')
        if parsed.get('start_date') and parsed.get('end_date') and parsed['start_date'] > parsed['end_date']:
            add('date_order', 'REVERSED_DATE_RANGE', [number], 'end_date',
                'End date precedes start date. Review source definitions and revisions rather than assuming misconduct.')
        if row.get('currency') not in (None, '', 'USD'):
            add('currency', 'UNSUPPORTED_CURRENCY', [number], 'currency',
                'This public sample expects USD; other currencies must be handled explicitly, without combining amounts.')
        synthetic = row.get('synthetic')
        if synthetic is True or synthetic in ('True', 'true'):
            add('synthetic_boundary', 'SYNTHETIC_IN_PUBLIC_SAMPLE', [number], 'synthetic',
                'A synthetic record appears in the real public-data sample. Separate it before interpreting results.')
        elif synthetic is not False and synthetic not in ('False', 'false'):
            add('synthetic_boundary', 'UNKNOWN_SYNTHETIC_STATUS', [number], 'synthetic',
                'The real/synthetic status is missing or unrecognized; establish provenance before use.')
        if row.get('fraud_label') != 'unlabeled':
            add('label_boundary', 'UNEXPECTED_LABEL', [number], 'fraud_label',
                'These public award records have no fraud ground truth. Verify any added label independently.')
    for key, numbers in sorted(seen.items()):
        if len(numbers) > 1:
            add('unique_keys', 'DUPLICATE_AWARD_KEY', numbers, 'award_key',
                'Repeated award identifier in this snapshot. Compare records before deduplicating; repetition is not fraud evidence.')
    checks = []
    for code, label in CHECKS:
        related = [i for i in issues if i['check'] == code]
        checks.append(dict(id=code, label=label, warning_count=sum(i['severity'] == 'warning' for i in related),
                           info_count=sum(i['severity'] == 'info' for i in related)))
    warnings = sum(i['severity'] == 'warning' for i in issues)
    serialized = json.dumps(rows, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return dict(version=VERSION, status='empty' if not rows else 'needs_review' if warnings else 'checks_passed',
                row_count=len(rows), warning_count=warnings, info_count=len(issues)-warnings,
                affected_rows=len({n for i in issues for n in i['row_numbers']}),
                row_number_basis='CSV line number: header is line 1; first data row is line 2',
                input_sha256=hashlib.sha256(serialized).hexdigest(), checks=checks, issues=issues,
                interpretation='Data-quality results are not evidence of fraud or innocence. Passing these limited checks does not establish source completeness or accuracy.')


def public_award_quality(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parent
    csv_path = root / 'data' / 'spending' / 'awards.csv'
    raw = csv_path.read_bytes() if csv_path.exists() else b''
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8')))) if raw else []
    report = audit_awards(rows)
    path = root / 'data' / 'spending' / 'provenance.json'
    provenance = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report.update(csv_sha256=hashlib.sha256(raw).hexdigest(), source_sha256=provenance.get('sha256'),
                  source_retrieved_at=provenance.get('retrieved_at'),
                  source='USAspending public award sample', source_hash_basis='Recorded intake metadata; use intake.py verify to check retained raw bytes')
    return report

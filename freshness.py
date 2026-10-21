"""Dated source coverage, distinct from factual/legal verification."""
from datetime import date, datetime, timezone


def assess_freshness(published_on, retrieved_at, as_of, stale_after_days=30):
    if type(as_of) is not date:
        raise ValueError('as_of must be an explicit calendar date')
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError('stale_after_days must be a nonnegative integer')

    def assess(value, timestamp=False):
        if value is None or value == '':
            return dict(value=value, status='unknown', age_days=None)
        try:
            if timestamp:
                parsed = datetime.fromisoformat(value)
                if parsed.tzinfo is None or parsed.utcoffset() is None:
                    raise ValueError('Timezone required')
                day = parsed.astimezone(timezone.utc).date()
            else:
                day = date.fromisoformat(value)
                if day.isoformat() != value:
                    raise ValueError('Expected YYYY-MM-DD')
        except (TypeError, ValueError):
            return dict(value=value, status='invalid', age_days=None)
        age = (as_of - day).days
        if age < 0:
            return dict(value=value, status='future_date', age_days=None)
        status = ('refresh_recommended' if age > stale_after_days else 'recent') if timestamp else 'known'
        return dict(value=value, status=status, age_days=age)

    return dict(evaluated_on=as_of.isoformat(), age_unit='UTC calendar days', stale_after_days=stale_after_days,
                publication=assess(published_on), retrieval=assess(retrieved_at, timestamp=True),
                interpretation='A recent retrieval does not verify a statement, update a legal finding, or establish that an unchanged page is current. Publication/update age and retrieval age are independent.')


def library_freshness(catalog, attempts, provenance, as_of=None):
    as_of = as_of or datetime.now(timezone.utc).date()
    latest_success = {}
    for attempt in attempts:
        if attempt.get('case_id') and attempt.get('status') == 'downloaded':
            latest_success[attempt['case_id']] = attempt.get('retrieved_at')
    return dict(cases={c['id']: assess_freshness(c['source'].get('published_on'), latest_success.get(c['id']), as_of)
                       for c in catalog['cases']},
                awards=assess_freshness(None, (provenance or {}).get('retrieved_at'), as_of))

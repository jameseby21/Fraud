"""Deterministic market-context exercises with a retained CFTC reference."""
from collections import defaultdict
import argparse
import csv
from datetime import date, timedelta
import hashlib
import io
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
VERSION = '1.0.0'
SEED = 904271
SOURCE_ID = 'cftc-tff-2022-09-13'


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def load_public_reference(root=ROOT):
    revisions = [json.loads(line) for line in (root / 'data/library/revisions.jsonl').read_text(encoding='utf-8').splitlines()]
    matches = [row for row in revisions if row['source_id'] == SOURCE_ID]
    if not matches:
        raise ValueError('Retained CFTC market reference is required')
    revision = matches[-1]
    path = root / revision['artifact']
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != revision['sha256']:
        raise ValueError('CFTC reference hash mismatch')
    source_rows = json.loads(payload)
    if len(source_rows) != 15:
        raise ValueError('Expected the reviewed 15-row CFTC slice')
    rows = []
    for row in source_rows:
        if row['report_date_as_yyyy_mm_dd'] != '2022-09-13T00:00:00.000':
            raise ValueError('Unexpected CFTC report date')
        rows.append(dict(source_record_id=row['id'],
                         market_and_exchange_names=row['market_and_exchange_names'],
                         report_date='2022-09-13',
                         available_on='2022-09-16',
                         cftc_contract_market_code=row['cftc_contract_market_code'],
                         open_interest_all=int(row['open_interest_all']),
                         contract_units=row['contract_units'],
                         source_id=SOURCE_ID, source_sha256=revision['sha256']))
    return dict(source_id=SOURCE_ID, sha256=revision['sha256'], rows=rows,
                interpretation='CFTC TFF combined open interest is an aggregate market constraint, not customer-level trade evidence.')


def _allocate(total, count, rng):
    if total < count or count < 1:
        raise ValueError('Allocation requires at least one unit per row')
    weights = [rng.randrange(1, 10001) for _ in range(count)]
    remainder = total - count
    values = [1 + remainder * weight // sum(weights) for weight in weights]
    for index in range(total - sum(values)):
        values[index % count] += 1
    rng.shuffle(values)
    return values


def build_case(reference):
    rng = random.Random(SEED)
    first = ['Amira','Caleb','Daria','Emmett','Farah','Gavin','Hana','Isaac','June','Kiran','Lucia','Miles']
    last = ['Archer','Bishop','Chen','Diaz','Everett','Foster','Gupta','Hughes','Ito','Jordan','Kim','Lopez']
    descriptors = ['Northwind','Juniper','Harborlight','Redwood','Clearwater','Stonebridge','Fairview','Bluecrest','Oakline','Silvermaple']
    forms = ['Family Trust','Retirement Plan','Foundation','Endowment','Holdings LLC','Capital Partners']
    accounts = []
    for index in range(240):
        accounts.append(dict(account_id=f'ACC-{index + 1:04}',
                             account_name=f'{descriptors[index % 10]} {forms[(index // 10) % 6]}',
                             contact_name=f'{first[index % 12]} {last[(index // 12 + index) % 12]}',
                             synthetic='True'))

    start = date(2025, 9, 1)
    business_days = []
    day = start
    while len(business_days) < 50:
        if day.weekday() < 5:
            business_days.append(day.isoformat())
        day += timedelta(days=1)
    securities = [f'MKT-{index:03}' for index in range(1, 41)]
    target_key = ('MKT-017', business_days[35])
    market_context = []
    for security in securities:
        for trade_date in business_days:
            volume = 320000 + rng.randrange(0, 4700000)
            if (security, trade_date) == target_key:
                volume = 2500000
            market_context.append(dict(security_id=security, trade_date=trade_date,
                                       market_volume=volume, source_scope='synthetic complete exchange tape',
                                       available_on=(date.fromisoformat(trade_date) + timedelta(days=1)).isoformat(),
                                       synthetic='True'))

    confirmations = []
    safe_keys = [(security, trade_date) for security in securities for trade_date in business_days if (security, trade_date) != target_key]
    for index in range(7960):
        security, trade_date = safe_keys[index % len(safe_keys)]
        account = accounts[rng.randrange(len(accounts))]
        quantity = rng.randrange(20, 4001)
        price = rng.randrange(1800, 28501)
        gross = quantity * price
        confirmations.append(dict(confirmation_id=f'CNF-{rng.getrandbits(64):016X}', account_id=account['account_id'],
                                  statement_id=f'STM-{account["account_id"][4:]}-{trade_date[:7].replace("-", "")}',
                                  trade_date=trade_date, settlement_date=(date.fromisoformat(trade_date) + timedelta(days=2)).isoformat(),
                                  security_id=security, side='BUY', quantity=quantity, price_cents=price,
                                  gross_cents=gross, cash_movement_cents=-gross, synthetic='True'))
    target_total = 2521337
    target_quantities = [target_total // 40 + (1 if index < target_total % 40 else 0) for index in range(40)]
    rng.shuffle(target_quantities)
    target_ids = []
    for index, quantity in enumerate(target_quantities):
        account = accounts[(index * 17 + 3) % len(accounts)]
        price = 11400 + rng.randrange(-140, 141)
        gross = quantity * price
        confirmation_id = f'CNF-{rng.getrandbits(64):016X}'
        target_ids.append(confirmation_id)
        confirmations.append(dict(confirmation_id=confirmation_id, account_id=account['account_id'],
                                  statement_id=f'STM-{account["account_id"][4:]}-{target_key[1][:7].replace("-", "")}',
                                  trade_date=target_key[1], settlement_date=(date.fromisoformat(target_key[1]) + timedelta(days=2)).isoformat(),
                                  security_id=target_key[0], side='BUY', quantity=quantity, price_cents=price,
                                  gross_cents=gross, cash_movement_cents=-gross, synthetic='True'))
    rng.shuffle(confirmations)

    positions = []
    target_position_ids = []
    counts = [267 if index < 10 else 266 for index in range(15)]
    for ref_index, (source, count) in enumerate(zip(reference['rows'], counts)):
        total = 1388003 if source['cftc_contract_market_code'] == '020601' else max(count, int(source['open_interest_all'] * (.06 + .005 * ref_index)))
        for row_index, quantity in enumerate(_allocate(total, count, rng)):
            account = accounts[(ref_index * 31 + row_index * 7) % len(accounts)]
            position_id = f'POS-{rng.getrandbits(64):016X}'
            if source['cftc_contract_market_code'] == '020601':
                target_position_ids.append(position_id)
            positions.append(dict(position_id=position_id, account_id=account['account_id'], provider_id='ADV-0042',
                                  report_date=source['report_date'], available_on=source['available_on'],
                                  cftc_contract_market_code=source['cftc_contract_market_code'],
                                  long_contracts=quantity, statement_status='final', synthetic='True'))
    rng.shuffle(positions)

    answers = [
        dict(pattern='synthetic_trade_volume_capacity', confirmation_ids=target_ids,
             group=dict(security_id=target_key[0], trade_date=target_key[1]),
             disposition='planted_group_inconsistency',
             explanation='Forty individually plausible confirmations total 2,521,337 units against a complete synthetic tape of 2,500,000. Arithmetic, cash, dates and statements reconcile; external market capacity does not. The group contradiction does not identify a specific false row.'),
        dict(pattern='public_open_interest_capacity', position_ids=target_position_ids,
             group=dict(cftc_contract_market_code='020601', report_date='2022-09-13'),
             disposition='planted_group_inconsistency',
             explanation='Fictional final statements total 1,388,003 long contracts versus CFTC combined open interest of 1,376,168. At least one claim in the scoped group cannot be true, but aggregate public data cannot identify which confirmation is false.'),
        dict(pattern='market_capacity_controls', disposition='benign_control',
             explanation='All other synthetic trade-date and public-reference contract groups remain below their matching aggregate capacity. This does not prove those rows occurred.')
    ]
    manifest = dict(version=VERSION, seed=SEED, synthetic=True,
                    counts=dict(accounts=len(accounts), confirmations=len(confirmations), positions=len(positions), market_context=len(market_context), public_reference=len(reference['rows'])),
                    public_source_id=reference['source_id'], public_source_sha256=reference['sha256'],
                    interpretation='Identities, statements, confirmations, prices and the complete exchange tape are fabricated. Only the retained CFTC aggregate reference facts are real. Capacity contradictions are group-level facts, not row-level guilt labels.')
    return dict(accounts=accounts, confirmations=confirmations, positions=positions, market_context=market_context,
                public_reference=reference['rows'], answers=answers, manifest=manifest)


def trade_volume_candidates(confirmations, market_context):
    if not confirmations or not market_context:
        raise ValueError('Confirmations and matching market context are required')
    capacity = {(row['security_id'], row['trade_date']): int(row['market_volume']) for row in market_context}
    groups = defaultdict(list)
    for row in confirmations:
        groups[(row['security_id'], row['trade_date'])].append(row)
    result = []
    for key, rows in sorted(groups.items()):
        if key not in capacity:
            continue
        claimed, available = sum(int(row['quantity']) for row in rows), capacity[key]
        result.append(dict(security_id=key[0], trade_date=key[1], claimed_quantity=claimed,
                           market_volume=available, excess_ratio=(claimed - available) / available,
                           exceeds_market_volume=claimed > available, confirmation_count=len(rows)))
    return result


def open_interest_candidates(positions, reference_rows):
    if not positions or not reference_rows:
        raise ValueError('Positions and public reference rows are required')
    capacity = {(row['cftc_contract_market_code'], row['report_date']): int(row['open_interest_all']) for row in reference_rows}
    groups = defaultdict(list)
    for row in positions:
        groups[(row['cftc_contract_market_code'], row['report_date'])].append(row)
    result = []
    for key, rows in sorted(groups.items()):
        if key not in capacity:
            continue
        claimed, available = sum(int(row['long_contracts']) for row in rows), capacity[key]
        result.append(dict(cftc_contract_market_code=key[0], report_date=key[1], claimed_long_contracts=claimed,
                           open_interest_all=available, excess_ratio=(claimed - available) / available,
                           exceeds_open_interest=claimed > available, statement_count=len(rows),
                           interpretation='A group total above open interest is inconsistent; this aggregate comparison cannot identify a false row.'))
    return result


def artifacts():
    case = build_case(load_public_reference())
    outputs = {}
    for name in ('accounts', 'confirmations', 'positions', 'market_context', 'public_reference'):
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=list(case[name][0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(case[name])
        outputs[f'data/market/v1/{name}.csv'] = stream.getvalue().encode()
    outputs['data/market/v1/instructor/answers.json'] = encoded(case['answers'])
    outputs['data/market/v1/manifest.json'] = encoded(case['manifest'])
    return outputs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    args = parser.parse_args()
    for relative, payload in artifacts().items():
        path = ROOT / relative
        if args.command == 'build':
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
        elif not path.exists() or path.read_bytes() != payload:
            raise SystemExit('Market fixture mismatch: ' + relative)
    print(f'PASS: market v1 {args.command}; 8000 confirmations, 4000 positions, 15 retained CFTC references.')

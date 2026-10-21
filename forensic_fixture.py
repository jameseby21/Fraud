"""Relational forensic practice case with exact-value resampling and separate truth."""
from collections import defaultdict
import argparse
import csv
from datetime import date, timedelta
import hashlib
import io
import json
import math
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parent
VERSION='2.0.0'
SEED=721406


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


def build_case(pool):
    rng=random.Random(SEED)
    first=['Maya','Elliot','Nora','Julian','Priya','Owen','Elena','Marcus','Ada','Theo','Lena','Samir']
    last=['Bennett','Carver','Delaney','Ellis','Finch','Hayes','Ivers','Keller','Lawson','Mercer','Nolan','Quinn']
    places=['Cedar','Willow','Harbor','Maple','Summit','Orchard','Stone','Silver','Meadow','Elm','Juniper','Brook']
    trades=['Bridge Advisory','Grove Supply','Ridge Engineering','Field Services','Vale Systems','Point Logistics','Lake Equipment','Hill Design','Park Materials','Gate Consulting']
    categories=['Services','Supplies','Equipment','Travel']
    entities=[]
    for i in range(120):
        entities.append(dict(supplier_id=f'VEN-{i+1:04}',business_name=f'{places[i//10]} {trades[i%10]} LLC',
            contact_name=first[i%12]+' '+last[(i//12+i)%12],category=categories[i%4],
            region=['North','South','East','West'][(i//4)%4],payment_terms_days=[15,30,45][i%3],
            bank_account_id=f'ACCT-{rng.getrandbits(40):010X}',synthetic='True'))
    source=pool['rows']
    if not source or any(r['amount_cents']<=0 for r in source): raise ValueError('Positive exact-value pool required')
    # Favor small real amounts while retaining the long upper tail. This is not a fitted population model.
    weights=[1/math.sqrt(r['amount_cents']) for r in source]
    draws=rng.choices(source,weights=weights,k=12000)
    rows=[]
    lineage={}
    for i, sampled in enumerate(draws):
        entity=entities[rng.randrange(120)]
        day=date(2024,1,1)+timedelta(days=rng.randrange(731))
        if day.weekday()>4: day+=timedelta(days=7-day.weekday())
        delay=entity['payment_terms_days']+int(rng.triangular(-2,20,3))
        payment=day+timedelta(days=delay)
        if payment.weekday()>4: payment+=timedelta(days=7-payment.weekday())
        transaction=f'PAY-{rng.getrandbits(64):016X}'
        rows.append(dict(transaction_id=transaction,invoice_id=f'INV-{rng.getrandbits(48):012X}',
            supplier_id=entity['supplier_id'],supplier=entity['business_name'],
            department=['Operations','Technology','Facilities','Research'][i%4],category=entity['category'],
            invoice_date=day.isoformat(),payment_date=payment.isoformat(),amount_cents=sampled['amount_cents'],
            currency='USD',region=entity['region'],synthetic='True',payment_method=rng.choice(['ACH','ACH','ACH','Check','Wire'])))
        lineage[transaction]=dict(transaction_id=transaction,transformation='exact_value_reassigned',
            source_id=sampled['source_id'],source_sha256=sampled['source_sha256'],source_row=sampled['source_row'],
            source_record_id=sampled['source_record_id'])
    reserved=rng.sample(range(12000),245)
    answers=[]

    def altered(index,**changes):
        row=rows[index]; row.update(changes)
        lineage[row['transaction_id']]=dict(transaction_id=row['transaction_id'],transformation='fabricated_pattern_amount',
                                           explanation='No claim this amount or sequence occurred in real records')

    def identity(index,supplier_index):
        entity=entities[supplier_index]
        rows[index].update(supplier_id=entity['supplier_id'],supplier=entity['business_name'],category=entity['category'],region=entity['region'])

    # Twelve groups, hidden among ordinary rows. No individual member is a whole-dollar amount.
    groups=[]
    used={(r['supplier_id'],r['payment_date']) for i,r in enumerate(rows) if i not in reserved[:48]}
    for g in range(12):
        day=date(2025,1,8)+timedelta(days=25*g)
        while ('VEN-0047',day.isoformat()) in used or day.weekday()>4: day+=timedelta(days=1)
        used.add(('VEN-0047',day.isoformat()))
        amounts=[rng.randrange(110000,220000)//100*100+rng.randrange(1,100) for _ in range(3)]
        # Choose a complement with nonzero cents, preserving exactly USD 10,000 per group.
        if sum(amounts)%100==0: amounts[0]+=1
        amounts.append(1000000-sum(amounts))
        ids=[]
        for index,amount in zip(reserved[g*4:g*4+4],amounts):
            identity(index,46)
            altered(index,amount_cents=amount,payment_date=day.isoformat(),invoice_date=(day-timedelta(days=30)).isoformat())
            ids.append(rows[index]['transaction_id'])
        groups.append(ids)
    answers.append(dict(pattern='round_sum_groups',groups=groups,transaction_ids=sum(groups,[]),disposition='planted_review_pattern',
        explanation='Twelve supplier-day totals equal USD 10,000 despite nonround members. This is a designed aggregation signal, not a real legal threshold.'))
    for index in reserved[48:228]:
        identity(index,87)
        day=date(2025,10,1)+timedelta(days=rng.randrange(90))
        altered(index,amount_cents=rng.randrange(100000,10000000),payment_date=day.isoformat(),invoice_date=(day-timedelta(days=30)).isoformat())
    answers.append(dict(pattern='uniform_amount_shift',transaction_ids=[rows[i]['transaction_id'] for i in reserved[48:228]],disposition='planted_review_pattern',
        explanation='180 fabricated near-uniform amounts for one supplier in Q4 differ from its earlier weighted empirical background. Examine scale, selection and business mix, not just first digits.'))
    for index in reserved[228:236]: altered(index,amount_cents=250000)
    answers.append(dict(pattern='round_individual',transaction_ids=[rows[i]['transaction_id'] for i in reserved[228:236]],disposition='planted_review_pattern',explanation='Eight inserted USD 2,500 amounts coexist with legitimate-looking round source values. Whole dollars alone are weak evidence.'))
    a,b=reserved[236:238]
    transaction=rows[b]['transaction_id']; rows[b]=dict(rows[a],transaction_id=transaction)
    lineage[transaction]=dict(lineage[rows[a]['transaction_id']],transaction_id=transaction,transformation='source_value_duplicate_for_exercise')
    answers.append(dict(pattern='repeated_invoice',transaction_ids=[rows[a]['transaction_id'],transaction],disposition='planted_review_pattern',explanation='Two payment rows share one invoice. Extraction duplication and actual double payment require distinct evidence.'))
    variance=reserved[238]
    answers.append(dict(pattern='bank_reconciliation',transaction_ids=[rows[variance]['transaction_id']],disposition='planted_review_pattern',explanation='Ledger payment and bank debit differ by USD 5. Bank fees, timing and errors are alternatives.'))
    for index,month in zip(reserved[239:245],range(1,7)):
        identity(index,4)
        altered(index,amount_cents=180000,invoice_date=f'2025-{month:02}-01',payment_date=f'2025-{month:02}-28')
    answers.append(dict(pattern='benign_subscription',transaction_ids=[rows[i]['transaction_id'] for i in reserved[239:245]],disposition='benign_control',explanation='Six distinct monthly service invoices repeat USD 1,800. Uniform or repeated values can be legitimate.'))
    # Place planted and background records together in normal chronological order, with random IDs.
    rows.sort(key=lambda r:(r['payment_date'],r['transaction_id']))
    invoices={}
    bank=[]
    bank_variance=answers[-2]['transaction_ids'][0]
    for row in rows:
        entity=entities[int(row['supplier_id'][4:])-1]
        row['available_on']=(date.fromisoformat(row['payment_date'])+timedelta(days=2)).isoformat()
        invoices.setdefault(row['invoice_id'],dict(invoice_id=row['invoice_id'],supplier_id=row['supplier_id'],invoice_date=row['invoice_date'],
            invoice_amount_cents=row['amount_cents'],available_on=row['invoice_date'],currency='USD',synthetic='True'))
        bank.append(dict(bank_entry_id='BANK-'+row['transaction_id'][4:],transaction_id=row['transaction_id'],bank_account_id=entity['bank_account_id'],
            posted_date=row['available_on'],signed_amount_cents=-row['amount_cents']-(500 if row['transaction_id']==bank_variance else 0),currency='USD',synthetic='True'))
    return dict(entities=entities,payments=rows,invoices=sorted(invoices.values(),key=lambda r:r['invoice_id']),bank_entries=bank,
                lineage=sorted(lineage.values(),key=lambda r:r['transaction_id']),answers=answers,
                manifest=dict(version=VERSION,seed=SEED,synthetic=True,source_pool_sha256=hashlib.sha256(encoded(pool)).hexdigest(),
                    amount_model='Exact source obligation values sampled with replacement, weights inverse square root of cents; fictional identities and dates; planted changes separately labeled in instructor lineage',
                    interpretation='Real numeric facts are reassigned, not anonymized real transactions. No claim of real case activity or representative invoice distributions.'))


def round_groups(rows,modulus=1000000,min_count=3):
    if modulus<=0 or min_count<2: raise ValueError('Positive modulus and at least two rows required')
    groups=defaultdict(list)
    for row in rows: groups[(row['supplier_id'],row['payment_date'])].append(row)
    return [dict(supplier_id=key[0],payment_date=key[1],total_cents=sum(r['amount_cents'] for r in group),transaction_ids=[r['transaction_id'] for r in group])
            for key,group in sorted(groups.items()) if len(group)>=min_count and sum(r['amount_cents'] for r in group)%modulus==0]


def digit_profile(values):
    counts=[0]*9
    for value in values:
        if type(value) is not int: raise ValueError('Leading-digit input must be integer cents')
        if value>0: counts[int(str(int(value))[0])-1]+=1
    n=sum(counts)
    return dict(counts=counts,n=n,proportions=[v/n if n else 0 for v in counts],
                interpretation='Descriptive leading-digit frequencies only; Benford assumptions are not established for bounded/resampled values.')


def distribution_comparison(rows,supplier_id='VEN-0088',boundary='2025-10-01'):
    a=sorted(r['amount_cents'] for r in rows if r['supplier_id']==supplier_id and r['payment_date']<boundary)
    b=sorted(r['amount_cents'] for r in rows if r['supplier_id']==supplier_id and r['payment_date']>=boundary)
    if not a or not b: raise ValueError('Both before and after cohorts need observations')
    from bisect import bisect_right
    distance=max(abs(bisect_right(a,x)/len(a)-bisect_right(b,x)/len(b)) for x in sorted(set(a+b)))
    return dict(supplier_id=supplier_id,boundary=boundary,before_n=len(a),after_n=len(b),ks_distance=distance,
                before_digits=digit_profile(a),after_digits=digit_profile(b),
                interpretation='Descriptive empirical CDF distance, not a fraud probability or calibrated significance test. Different amount ranges, procurement mix, repeated source values and selection affect the result.')


def public_case(as_of=None):
    if as_of is not None: date.fromisoformat(as_of)
    tables={}
    for name in ('entities','payments','invoices','bank_entries'):
        with (ROOT/f'data/forensic/v2/{name}.csv').open(encoding='utf-8',newline='') as stream:
            rows=list(csv.DictReader(stream))
        for row in rows:
            for key in ('amount_cents','invoice_amount_cents','signed_amount_cents','payment_terms_days'):
                if key in row:row[key]=int(row[key])
        if as_of and name!='entities':
            field='posted_date' if name=='bank_entries' else 'available_on'
            rows=[r for r in rows if r[field]<=as_of]
        tables[name]=rows
    return dict(tables,version=VERSION,as_of=as_of,synthetic=True)


def artifacts():
    pool=json.loads((ROOT/'data/library/amount_pool.json').read_text())
    case=build_case(pool)
    outputs={}
    for name in ('entities','payments','invoices','bank_entries'):
        stream=io.StringIO(newline=''); rows=case[name]
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
        outputs[f'data/forensic/v2/{name}.csv']=stream.getvalue().encode()
    for name in ('lineage','answers','manifest'):
        outputs[f'data/forensic/v2/instructor/{name}.json']=encoded(case[name])
    return outputs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['build','verify'])
    args=parser.parse_args()
    for relative,payload in artifacts().items():
        path=ROOT/relative
        if args.command=='build':path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
        elif not path.exists() or path.read_bytes()!=payload:raise SystemExit('Forensic fixture mismatch: '+relative)
    print('PASS: forensic v2 '+args.command+'; 12000 payments, fictional persistent entities, separate source lineage and answer key.')

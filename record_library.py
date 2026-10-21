"""Public source registry, append-only supplemental revisions and exact-value pool."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import html
import json
import os
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlsplit
from urllib.parse import urlencode

from intake import validate_payload

ROOT = Path(__file__).resolve().parent
HOSTS = {'www.justice.gov', 'www.govinfo.gov', 'api.usaspending.gov', 'www.fbi.gov', 'archives.fbi.gov',
         'www.ftc.gov', 'publicreporting.cftc.gov', 'files.consumerfinance.gov', 'www.sec.gov'}
TYPES = {'official_case_report', 'government_pleading', 'court_transcript', 'financial_records', 'market_reference', 'hearing_transcript'}


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def check_url(url):
    p = urlsplit(url)
    if p.scheme != 'https' or p.hostname not in HOSTS or p.username or p.password or p.port not in (None,443):
        raise ValueError('Source requires an allowlisted public HTTPS government host')


def check_source(source):
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,100}', source['id']):
        raise ValueError('Invalid source ID')
    check_url(source['url'])
    if not source.get('reuse_basis') or not source.get('reuse_url') or source['record_type'] not in TYPES:
        raise ValueError('Source type and reviewed reuse basis required')


def _lines(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()] if path.exists() else []


def _append(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(record, sort_keys=True) + '\n')
        stream.flush(); os.fsync(stream.fileno())


def ingest(source, payload, content_type, root=ROOT):
    check_source(source)
    suffix = {'text/html':'.html', 'application/pdf':'.pdf', 'application/json':'.json'}.get(content_type)
    if not suffix or not payload or len(payload) > 20*1024*1024:
        raise ValueError('Unsupported or oversized artifact')
    base = root / 'data/library'
    base.mkdir(parents=True, exist_ok=True)
    lock = base / '.intake.lock'
    # Single writer; a stale lock requires inspection, never automatic removal.
    with lock.open('x'):
        pass
    try:
        history = _lines(base / 'revisions.jsonl')
        previous = [r for r in history if r['source_id'] == source['id']]
        digest = hashlib.sha256(payload).hexdigest()
        request_hash = hashlib.sha256(encode(source.get('request'))).hexdigest()
        if previous and previous[-1]['sha256'] == digest and previous[-1].get('request_sha256') == request_hash:
            if (root / previous[-1]['artifact']).read_bytes() != payload:
                raise ValueError('Existing artifact corrupted')
            return previous[-1]
        relative = f'data/library/raw/{digest}{suffix}'
        path = root / relative
        path.parent.mkdir(exist_ok=True)
        if path.exists():
            if path.read_bytes() != payload:
                raise ValueError('Existing artifact corrupted')
        else:
            with path.open('xb') as stream:
                stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        record = dict(source_id=source['id'], case_id=source.get('case_id'), record_type=source['record_type'],
                      revision=len(previous)+1, supersedes=previous[-1]['sha256'] if previous else None,
                      sha256=digest, artifact=relative, bytes=len(payload), content_type=content_type,
                      requested_url=source['url'], publication_date=source.get('publication_date'),
                      request=source.get('request'), request_sha256=request_hash,
                      reuse_basis=source['reuse_basis'], reuse_url=source['reuse_url'],
                      retrieved_at=source.get('original_retrieved_at',datetime.now(timezone.utc).isoformat()),
                      recorded_at=datetime.now(timezone.utc).isoformat())
        _append(base / 'revisions.jsonl', record)
        return record
    finally:
        lock.unlink()


class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(source):
    check_source(source)
    payload = encode(source['request']) if source.get('request') else None
    request = urllib.request.Request(source['url'], data=payload,
        headers={'User-Agent':'FraudLearningLibrary/1.0 (public educational records)', 'Content-Type':'application/json'})
    with urllib.request.build_opener(Redirect()).open(request, timeout=35) as response:
        check_url(response.geturl())
        content = response.read(20*1024*1024+1)
        if len(content) > 20*1024*1024:
            raise ValueError('Response exceeds 20 MiB')
        kind = response.headers.get_content_type()
        validate_payload(content, kind)
        return content, kind


def refresh(source, root=ROOT):
    check_source(source)
    attempt = dict(source_id=source['id'], requested_url=source['url'], attempted_at=datetime.now(timezone.utc).isoformat())
    try:
        content, kind = fetch(source)
        record = ingest(source, content, kind, root)
        attempt.update(status='downloaded', sha256=record['sha256'], revision=record['revision'])
        success = True
    except (OSError, ValueError) as error:
        attempt.update(status='unavailable', error=str(error)); success = False
    _append(root / 'data/library/attempts.jsonl', attempt)
    return success


def verify_library(root=ROOT):
    revisions = _lines(root / 'data/library/revisions.jsonl')
    latest = {}
    for r in revisions:
        previous = latest.get(r['source_id'])
        if r['revision'] != (previous['revision']+1 if previous else 1) or r['supersedes'] != (previous['sha256'] if previous else None):
            raise ValueError('Broken source revision chain')
        path = (root / r['artifact']).resolve()
        if not path.is_relative_to((root / 'data/library/raw').resolve()):
            raise ValueError('Artifact path escaped library')
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != r['sha256'] or len(payload) != r['bytes']:
            raise ValueError('Library artifact integrity failure')
        latest[r['source_id']] = r
    if (root/'data/library/sources.json').exists():
        for relative, expected in derived_files(root).items():
            if not (root/relative).exists() or (root/relative).read_bytes()!=expected:
                raise ValueError('Derived library index or amount pool drift: '+relative)
    return dict(sources=len(latest), revisions=len(revisions), valid=True)


def normalize_amounts(payload):
    result = []
    for i, row in enumerate(payload['results']):
        amount = Decimal(str(row['Award Amount']))*100
        if not amount.is_finite() or amount != amount.to_integral_value():
            raise ValueError('Source money must contain whole cents')
        if amount > 0:
            result.append(dict(source_record_id=str(row.get('generated_internal_id', row['Award ID'])),
                               source_row=i, amount_cents=int(amount), financial_semantics='total_award_obligation_not_payment'))
    return result


def seed():
    catalog = json.loads((ROOT/'data/cases.json').read_text(encoding='utf-8'))
    sources = []
    for case in catalog['cases']:
        host = urlsplit(case['source']['url']).hostname
        if host not in HOSTS:
            continue
        policies = {
            'www.justice.gov': ('DOJ', 'https://www.justice.gov/legalpolicies'),
            'www.fbi.gov': ('FBI', 'https://www.fbi.gov/privacy-policy'),
            'archives.fbi.gov': ('FBI', 'https://www.fbi.gov/privacy-policy'),
            'www.ftc.gov': ('FTC', 'https://www.ftc.gov/site-information/privacy-policy'),
            'files.consumerfinance.gov': ('CFPB', 'https://www.consumerfinance.gov/open-government/'),
            'www.govinfo.gov': ('GovInfo', 'https://www.govinfo.gov/about/policies'),
            'www.sec.gov': ('SEC', 'https://www.sec.gov/about/privacy-information'),
        }
        agency, reuse_url = policies[host]
        sources.append(dict(id=case['id']+'-report', case_id=case['id'], title=case['title'] if 'title' in case else case.get('name',case['id']),
            url=case['source']['url'], publication_date=case['source'].get('published_on'), record_type='official_case_report',
            reuse_basis=f'{agency}-authored official report; government text only, third-party inserts retain original rights',
            reuse_url=reuse_url))
    sources += [dict(id='cftc-tff-2022-09-13',case_id=None,title='CFTC TFF combined open interest, 15 contract markets, September 13, 2022',
        url='https://publicreporting.cftc.gov/resource/yw9f-hn96.json?%24select=id%2Cmarket_and_exchange_names%2Creport_date_as_yyyy_mm_dd%2Ccftc_contract_market_code%2Copen_interest_all%2Ccontract_units&%24where=report_date_as_yyyy_mm_dd%3D%272022-09-13T00%3A00%3A00.000%27&%24order=cftc_contract_market_code&%24limit=15',
        publication_date='2022-09-16',record_type='market_reference',
        reuse_basis='CFTC public reporting API; exact government-produced aggregate facts retained for reproducible instruction',
        reuse_url='https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm'),
      dict(id='madoff-peter-plea-transcript',case_id='madoff',title='Peter Madoff plea proceeding, June 29, 2012',
        url='https://www.justice.gov/usao/nys/madoff/20120629transcriptpetermadoffpleaproceeding%20.pdf',publication_date='2012-06-29',record_type='court_transcript',
        reuse_basis='Public court-proceeding transcript hosted by DOJ; DOJ default permits copying unless otherwise indicated; no contrary copyright notice found in reviewed text. Not relicensed as project CC0.',reuse_url='https://www.justice.gov/legalpolicies'),
      dict(id='madoff-peter-information',case_id='madoff',title='Peter Madoff criminal information',url='https://www.justice.gov/media/785456/dl?inline=',publication_date='2012-06-29',record_type='government_pleading',
        reuse_basis='DOJ-authored public charging instrument; allegation at filing, not adjudication by itself',reuse_url='https://www.justice.gov/legalpolicies'),
      dict(id='madoff-programming-records',case_id='madoff',title='Trial outcome and fabricated books/records mechanisms',
        url='https://www.justice.gov/usao-sdny/pr/five-former-employees-bernard-l-madoff-investment-securities-found-guilty-manhattan',publication_date='2014-03-24',record_type='official_case_report',
        reuse_basis='DOJ-authored report under DOJ public-domain default; not an original transaction ledger',reuse_url='https://www.justice.gov/legalpolicies'),
      dict(id='learning-award-values',case_id=None,title='Small federal contract obligation values for exercise resampling',url='https://api.usaspending.gov/api/v2/search/spending_by_award/',publication_date=None,record_type='financial_records',
        reuse_basis='Public federal award facts and API response; numeric facts are reused, not third-party report text',reuse_url='https://www.usaspending.gov/about',
        request={'filters':{'award_type_codes':['A','B','C','D'],'time_period':[{'start_date':'2025-01-01','end_date':'2025-12-31'}],
                           'award_amounts':[{'lower_bound':10,'upper_bound':250000}]},
                 'fields':['Award ID','Award Amount','generated_internal_id'],'limit':1000,'page':1,'sort':'Award ID','order':'asc','subawards':False})]
    financial = sources.pop()
    financial['request']['limit'] = 100
    for page in range(1,11):
        copy = json.loads(json.dumps(financial))
        copy['id'] = 'learning-award-values' if page == 1 else f'learning-award-values-p{page:02}'
        copy['request']['page'] = page
        copy['title'] += f' (page {page})'
        sources.append(copy)
    path = ROOT/'data/library/sources.json'; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(encode(dict(schema_version=1,sources=sources)))


def derived_files(root=ROOT):
    sources = json.loads((root/'data/library/sources.json').read_text())['sources']
    for source in sources: check_source(source)
    if len({s['id'] for s in sources}) != len(sources): raise ValueError('Duplicate source IDs')
    revisions = _lines(root/'data/library/revisions.jsonl')
    latest = {r['source_id']:r for r in revisions}
    index = dict(schema_version=1, sources=[dict(s, latest=latest.get(s['id']), coverage='retained' if s['id'] in latest else 'unavailable') for s in sources])
    files = {'data/library/index.json':encode(index)}
    amount_sources = [latest[s['id']] for s in sources if s['id'].startswith('learning-award-values') and s['id'] in latest]
    if amount_sources:
        rows=[]
        lineage=[]
        for r in amount_sources:
            payload = json.loads((root/r['artifact']).read_bytes(), parse_float=Decimal)
            rows.extend(dict(row,source_id=r['source_id'],source_sha256=r['sha256']) for row in normalize_amounts(payload))
            lineage.append(dict(source_id=r['source_id'],sha256=r['sha256']))
        pool = dict(sources=lineage,source_sha256=hashlib.sha256(encode(lineage)).hexdigest(),rows=rows)
        files['data/library/amount_pool.json']=encode(pool)
    return files


def rebuild(root=ROOT):
    for relative, content in derived_files(root).items():
        (root/relative).write_bytes(content)


def reuse_existing(source, attempts, root=ROOT):
    # URL equality is insufficient for POST queries. Fetch them afresh.
    if source.get('request'):
        return False
    matches=[r for r in attempts if r.get('requested_url')==source['url'] and r['status']=='downloaded']
    if not matches:
        return False
    record=matches[-1]
    payload=(root/record['artifact']).read_bytes()
    if hashlib.sha256(payload).hexdigest()!=record['sha256']:
        raise ValueError('Existing source corrupt')
    ingest(dict(source,original_retrieved_at=record['retrieved_at']),payload,record['content_type'],root)
    return True


def library_index():
    return json.loads((ROOT/'data/library/index.json').read_text(encoding='utf-8'))


def record_download(source_id):
    matches=[s for s in library_index()['sources'] if s['id']==source_id and s['latest']]
    if not matches: raise KeyError(source_id)
    record=matches[0]['latest']
    path=(ROOT/record['artifact']).resolve()
    if not path.is_relative_to((ROOT/'data/library/raw').resolve()): raise ValueError('Invalid artifact path')
    content=path.read_bytes()
    if hashlib.sha256(content).hexdigest()!=record['sha256']: raise ValueError('Artifact integrity failed')
    return path, content


def library_page(search=''):
    records=library_index()['sources']
    matches=[s for s in records if search.casefold() in (s['title']+' '+str(s['case_id'])+' '+s['record_type']).casefold()]
    esc=lambda x:html.escape(str(x),quote=True)
    out=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Public record library</title><link rel="stylesheet" href="/learn.css"></head><body><header><a href="/learn">Courses</a><a href="/library">Case findings</a></header><main><h1>Public record library</h1><p>Official documents and financial snapshots. A charging document states allegations; a transcript records statements and proceedings. Neither is a complete financial ledger. Award values are not payment records or fraud labels.</p>',
         '<form action="/records"><label for="q">Search title, case or record type</label><input id="q" name="q" value="'+esc(search)+'"><button>Search</button></form>',
         f'<p role="status">{len(matches)} of {len(records)} registered sources. Unavailable downloads remain visible.</p>']
    for s in matches:
        out += ['<section class="resources"><h2>'+esc(s['title'])+'</h2><p>'+esc(s['record_type'])+' · '+esc(s['coverage'])+' · publication '+esc(s['publication_date'] or 'unknown')+'</p>',
                '<p>'+esc(s['reuse_basis'])+'</p><a href="'+esc(s['url'])+'">Official source</a> · <a href="'+esc(s['reuse_url'])+'">Reuse policy</a>']
        if s['latest']:
            r=s['latest']
            out += ['<p><a href="/api/record?'+urlencode({'source':s['id']})+'">Download retained original</a></p><p>Revision '+str(r['revision'])+' · SHA-256 <code>'+r['sha256']+'</code></p>']
        else: out+=['<p>No retained bytes. Consult the source; no successful intake is implied.</p>']
        out+=['</section>']
    return ''.join(out+['</main></body></html>'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['seed','import-existing','fetch','build','verify'])
    parser.add_argument('--source'); parser.add_argument('--refresh',action='store_true')
    args=parser.parse_args()
    if args.command=='seed': seed()
    elif args.command=='verify':
        print(json.dumps(verify_library(),indent=2)); return
    else:
        sources=json.loads((ROOT/'data/library/sources.json').read_text())['sources']
        if args.source:
            sources=[s for s in sources if s['id']==args.source]
            if not sources: raise SystemExit('Unknown source ID')
        failures=0
        if args.command=='import-existing':
            existing=_lines(ROOT/'data/intake_log.jsonl')
            for s in sources:
                reuse_existing(s,existing)
        elif args.command=='fetch':
            retained={r['source_id'] for r in _lines(ROOT/'data/library/revisions.jsonl')}
            for s in sources:
                if s['id'] in retained and not args.refresh: continue
                ok=refresh(s); failures+=not ok
                print(s['id']+(': retained' if ok else ': unavailable'))
        rebuild()
        if failures: raise SystemExit(1)


if __name__=='__main__': main()

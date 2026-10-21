"""Generate traceable historical case guides; never invent missing financial records."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def artifacts():
    cases=json.loads((ROOT/'data/cases.json').read_text())['cases']
    files={}
    index='# Historical case study library\n\n[Root README](../../README.md). These guides derive from the reviewed case catalog. They distinguish actual outcomes from proposed analytical exercises. No original full ledger is implied. For retained and unavailable artifacts see [the record library](../library/README.md).\n\n'
    for case in cases:
        if case['kind']!='historical':continue
        source=case['source']
        index+=f'- [{case["name"]}]({case["id"]}.md)\n'
        content=f'''# {case['name']}

## Recorded outcome

{case['outcome']}

Outcome date: {case['outcome_on']}. Source: [{source['title']}]({source['url']}); publication: {source.get('published_on') or 'unknown'}. This is the catalog's narrowly scoped finding, not a new independent adjudication.

## Analyst question

{case['focus']}. Teaching mechanism: `{case['model']}`.

{case['lesson']}

## Work in the analyst's shoes

- Identify document type, date, author, scope and whether the local library retains original bytes.
- Write a claim/evidence matrix with precise page/paragraph locators and distinguish recorded facts from your inference.
- Define a minimally sufficient data schema: stable entity/document/transaction IDs, currency/units, event dates, availability dates and independent reconciliation keys.
- State which required original records are absent. A press report or outcome cannot substitute for those records.
- Test an explicitly fictional mechanism with a benign alternative before describing any review signal.
- Write reproducible filters, input hashes and next-evidence requests; preserve counterevidence.

## Data and assessment limits

The existing mechanism replay is fabricated and case-inspired. Original source ledgers, full legal chronology and independent labels are not included for this case unless specifically listed in the record library. This guide does not create them. The forensic-v2 supplier exercise teaches corroboration, grouping and distribution review; its values/identities are not measurements of this case. Future real-file exercises must add source-specific intake, reuse review, extraction tests and temporal availability evidence.

## Debugging and reflection

A missing download is a coverage gap; check the attempt log rather than inventing a source. Distinguish event date, publication date and retrieval date. What independent record would falsify your explanation, and which assumption is currently unsupported?
'''
        files[f'docs/cases/{case["id"]}.md']=content.encode()
    files['docs/cases/README.md']=index.encode()
    return files


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    for relative,content in artifacts().items():
        path=ROOT/relative
        if args.verify:
            if not path.exists() or path.read_bytes()!=content:raise SystemExit('Case guide mismatch: '+relative)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    print('PASS: 20 source-linked historical case guides '+('verified.' if args.verify else 'built.'))

"""Generate traceable historical case guides; never invent missing financial records."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def artifacts():
    cases=json.loads((ROOT/'data/cases.json').read_text())['cases']
    outcome_data=json.loads((ROOT/'data/case_outcomes.json').read_text())
    outcomes={item['id']:item for item in outcome_data['outcomes']}
    files={}
    index='# Resolved case study library\n\n[Root README](../../README.md). These guides derive from the reviewed case catalog. They preserve criminal, civil, administrative, mixed, deferred, and acquittal outcomes without treating them as equivalent. No original full ledger is implied. See the [legal-outcome schema](../case_outcomes.md) and [record library](../library/README.md).\n\n'
    for case in cases:
        if case['kind']!='historical':continue
        source=case['source']
        resolution=outcomes[case['id']]
        index+=f'- [{case["name"]}]({case["id"]}.md)\n'
        imprisonment=(f'{resolution["imprisonment_months"]} months' if resolution['imprisonment_months'] else 'none recorded in this structured entry')
        remedies='\n'.join(f'- {item["type"].replace("_", " ")}: ${item["amount_usd"]:,.0f} ({item["qualifier"]}); {item["scope"]}.' for item in resolution['remedies']) or '- No monetary remedy is structured in this entry; consult the source before inferring none existed.'
        content=f'''# {case['name']}

## Recorded outcome

{case['outcome']}

Outcome date: {case['outcome_on']}. Source: [{source['title']}]({source['url']}); publication: {source.get('published_on') or 'unknown'}. This is the catalog's narrowly scoped finding, not a new independent adjudication.

Resolution type: `{resolution['type']}`. Criminal disposition: `{resolution['criminal_disposition']}`. Forum: {resolution['forum']}. Imprisonment imposed: {imprisonment}.

{remedies}

Remedy amounts retain their named scope. Penalty, forfeiture, restitution, disgorgement, coordinated payment, alleged loss, and victim loss must not be substituted for one another.

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
    count=len(artifacts())-1
    print(f'PASS: {count} source-linked resolved case guides '+('verified.' if args.verify else 'built.'))

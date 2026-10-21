# MoneyGram anti-fraud program

## Recorded outcome

MoneyGram agreed to extend its deferred prosecution agreement and forfeit $125 million after the government said anti-fraud and anti-money-laundering weaknesses breached its 2012 agreement.

Outcome date: 2018-11-08. Source: [DOJ: MoneyGram extends deferred prosecution agreement](https://www.justice.gov/archives/opa/pr/moneygram-international-inc-agrees-extend-deferred-prosecution-agreement-forfeits-125-million); publication: 2018-11-08. This is the catalog's narrowly scoped finding, not a new independent adjudication.

Resolution type: `deferred_prosecution`. Criminal disposition: `deferred`. Forum: federal criminal agreement. Imprisonment imposed: none recorded in this structured entry.

- forfeiture: $125,000,000 (agreed); 2018 DPA extension forfeiture intended for victims.

Remedy amounts retain their named scope. Penalty, forfeiture, restitution, disgorgement, coordinated payment, alleged loss, and victim loss must not be substituted for one another.

## Analyst question

Reported fraud and high-risk agents versus escalation, termination, and blocked transfers. Teaching mechanism: `monitoring_escalation`.

Use event-time analysis to test whether known high-risk agents or complaint patterns continued after a control should have intervened.

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

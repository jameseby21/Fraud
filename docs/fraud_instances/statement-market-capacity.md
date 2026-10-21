# Statement lines versus market capacity

Dataset: `data/market/v1`, version 1.0.0. Grain: one synthetic confirmation line; comparison grain: security ID and trade date.

Every confirmation passes `gross_cents = quantity * price_cents`, cash-sign, settlement-date, and statement-link checks. Grouping BUY quantity by security and date exposes one group totaling 2,521,337 units against a complete synthetic tape of 2,500,000. The excess is below 1%, and no individual planted line exceeds 4% of market volume. Forty target lines are buried among 7,960 non-target confirmations.

This establishes an aggregate inconsistency inside a fully synthetic world. It does not identify a false line, a responsible person, intent, or a real-world offense. Venue scope, corrections, cancel/bust handling, units, and duplicate joins are necessary controls in a real analysis. A specific conclusion would require broker, venue, clearing, counterparty, or custody records.

The historical motivation is the distinct risk that polished internal records can report activity that never happened. A [2011 SEC enforcement release](https://www.sec.gov/newsroom/press-releases/2011-247-sec-charges-longtime-madoff-employee-creating-fake-trades) describes alleged backdated information used to create fictitious trades on Madoff customer statements and confirmations. The [DOJ case page](https://www.justice.gov/usao-sdny/programs/victim-witness-services/united-states-v-bernard-l-madoff-and-related-cases) records the adjudicated plea and sentence. Neither source is evidence for these fictional records.

Reproduce with `trade_volume_candidates` in `market_fixture.py`, or follow [lesson 4](../../courses/forensic-practicum/statement-capacity.md). The separate instructor key lists designed group membership.

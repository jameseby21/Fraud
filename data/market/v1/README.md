# Market-context practice case, version 1.0.0

[Root README](../../../README.md) is canonical. All account names, confirmations, prices, positions, and synthetic exchange-tape values are fabricated. The 15 CFTC open-interest facts in `public_reference.csv` are exact values derived from a retained public API response and keep the source ID and SHA-256 beside every row.

| Table | Rows | Purpose |
| --- | ---: | --- |
| `accounts.csv` | 240 | Persistent fictional account and contact names |
| `confirmations.csv` | 8,000 | Internally consistent synthetic trade-confirmation lines |
| `market_context.csv` | 2,000 | Complete synthetic daily volume for 40 fictional securities across 50 business days |
| `positions.csv` | 4,000 | Synthetic final long-position statements mapped to CFTC contract codes |
| `public_reference.csv` | 15 | Exact CFTC TFF combined open interest for September 13, 2022 |

The first exercise hides 40 individually plausible confirmations among 7,960 background lines. Their quantities total 2,521,337 units while the matching complete synthetic tape reports 2,500,000, an excess under 1%. Every line’s gross value, cash sign, date sequence, and statement association passes the supplied checks. The group is inconsistent; those checks cannot select a false row.

The second exercise distributes 4,000 fictional positions across 15 real CFTC reference groups. Contract code `020601` totals 1,388,003 claimed long contracts against 1,376,168 public combined open interest, also an excess under 1%. The other fourteen groups remain below capacity. CFTC data proves the scoped aggregate cannot all be true, but it cannot identify a false customer confirmation or prove that any control-group position occurred.

The CFTC describes open interest as outstanding futures or option contracts not yet offset, delivered, or exercised. The TFF combined report is a Tuesday aggregate and this retained slice was available on September 16, 2022. Match report type, contract code, date, units, and availability. Do not compare a position to daily trading volume or treat publication as customer-level custody evidence.

```powershell
python record_library.py fetch --source cftc-tff-2022-09-13 --refresh
python record_library.py verify
python market_fixture.py build
python market_fixture.py verify
```

Refresh is append-only: changed public bytes create a new content-addressed revision. Review the diff and update this version, lessons, answers, and tests before accepting changed facts. Offline verification reads only retained bytes. See [public sources](../../../DATA_SOURCES.md), [market-capacity instance](../../../docs/fraud_instances/statement-market-capacity.md), and [public open-interest instance](../../../docs/fraud_instances/public-open-interest.md).

The historical motivation is documented separately from the exercise. In a [2011 SEC enforcement release](https://www.sec.gov/newsroom/press-releases/2011-247-sec-charges-longtime-madoff-employee-creating-fake-trades), the agency alleged that backdated information was turned into fictitious trades on Madoff customer statements and confirmations. The [DOJ Madoff case page](https://www.justice.gov/usao-sdny/programs/victim-witness-services/united-states-v-bernard-l-madoff-and-related-cases) records the guilty plea and sentence. Those sources do not supply or validate any row in this synthetic exercise.

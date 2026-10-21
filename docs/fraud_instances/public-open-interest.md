# Public open interest versus fictional statements

Dataset: `data/market/v1`, version 1.0.0. Grain: one fictional final position; comparison grain: provider, CFTC contract code, and report date.

The retained [CFTC Commitments of Traders source](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) supplies exact combined open interest and explanatory scope. Fictional statements for contract code `020601` total 1,388,003 long contracts on September 13, 2022, compared with public open interest of 1,376,168. The excess is below 1%. Fourteen other public-reference groups are below their capacity and serve as controls.

The group cannot all be true under the matched scope. Aggregate CFTC data cannot identify which statement is false, confirm any customer execution, or establish intent. It also is unavailable on the Tuesday report date: the fixture uses September 16, 2022 as `available_on`. Combined versus futures-only scope, contract units, leading-zero codes, dates, and data revisions must match.

Reproduce with `open_interest_candidates` in `market_fixture.py`, or follow [lesson 5](../../courses/forensic-practicum/public-corroboration.md). The original 15-row response is retained by hash in the append-only record library; derived rows preserve its source ID and digest.

# Data analysis and forensic review glossary

This index is generated from `data/learning/glossary.json`, the same reviewed source used by the course interface. Terms explain analytical use and limits; they do not turn a screening signal into a finding of misconduct.

## Statement

**Definition:** A periodic record that reports account balances, transactions, positions, or activity for a stated period.

**More context:** Statements help customers and investors understand reported activity, but their appearance is not independent proof that the underlying trades or transfers occurred. In the Madoff fraud, polished customer statements reported securities activity that investigators later established was fictitious.

**Implications:** Reconcile a statement to independent bank, broker, custodian, exchange, issuer, or regulatory records. Treat internal consistency as one check, not external corroboration.

**Also shown as:** statement, bank statement, account statement, statements.

## Transaction

**Definition:** A recorded economic event at the grain defined by the source system.

**More context:** One row may represent an authorization, invoice, obligation, transfer, adjustment, or settled payment rather than the whole event.

**Implications:** Define the row grain and lifecycle before counting, joining, or labeling duplicates.

**Also shown as:** transaction, transactions.

## Trade confirmation

**Definition:** A record of a securities order’s reported execution details, commonly including instrument, side, quantity, price, and time.

**More context:** A confirmation may be checked against custody records and market context, though public data rarely proves a specific private customer’s execution by itself.

**Implications:** Compare identifiers, timestamps, prices, volumes, settlement, and custodian records; document the limits of public corroboration.

**Also shown as:** trade confirmation, trade confirmations.

## Market volume

**Definition:** The quantity of an instrument reported as traded during a defined venue and period.

**More context:** Volume depends on venue coverage, consolidation rules, corrections, and time zone. A plausible-looking fill can still be inconsistent with aggregate activity.

**Implications:** Use the matching instrument, venue scope, date, and unit. A customer’s reported quantity near total market volume is a review signal, not automatic proof.

**Also shown as:** market volume, trading volume, volume.

## Open interest

**Definition:** The total number of derivative contracts that remain open because they have not been offset, delivered, or exercised.

**More context:** For a futures or options market, aggregate long open interest equals aggregate short open interest. Public reports may group traders and publish after the measured date.

**Implications:** Match the contract, report date, unit, and publication lag. A set of claimed positions above total reported open interest proves a group-level inconsistency, but does not identify which individual record is false.

**Also shown as:** open interest.

## Liquidity

**Definition:** The ability to transact in an asset with limited delay and price impact.

**More context:** Liquidity varies by instrument, venue, time, order size, and market conditions.

**Implications:** A claimed execution may be technically possible yet economically implausible once size, spread, and available volume are considered.

**Also shown as:** liquidity, liquid.

## Settlement

**Definition:** The completion stage in which securities and cash are delivered according to the applicable market process.

**More context:** Execution and settlement are separate events with different dates and records.

**Implications:** A trade-looking statement should be reconciled to cash, position, and custody changes on the expected settlement timeline.

**Also shown as:** settlement, settled.

## Custody

**Definition:** Safekeeping and administration of assets by an authorized holder or institution.

**More context:** Independent custody can provide evidence distinct from records produced by an adviser or manager.

**Implications:** Request direct custodian evidence and verify the source rather than relying on forwarded copies alone.

**Also shown as:** custody, custodian.

## Reconciliation

**Definition:** A controlled comparison of records from different systems to explain matches and differences.

**More context:** Differences can arise from timing, fees, corrections, missing data, identifiers, or error as well as misconduct.

**Implications:** Keep unmatched items, tolerances, source timestamps, and explanations traceable.

**Also shown as:** reconciliation, reconcile, reconciled.

## Invoice

**Definition:** A request for payment describing goods, services, quantities, prices, and parties.

**More context:** An invoice is evidence of a claim for payment, not proof that delivery or payment occurred.

**Implications:** Match invoices to approvals, contracts, receiving records, payments, and bank entries at the correct grain.

**Also shown as:** invoice, invoices.

## Obligation

**Definition:** A commitment to spend funds, distinct from an invoice or completed cash payment.

**More context:** The public values bootstrapped into this project originated as award obligations and were reassigned to synthetic payment records.

**Implications:** Do not describe obligation data as bank transaction history without a documented transformation and clear synthetic label.

**Also shown as:** obligation, obligations.

## Payment

**Definition:** A transfer or recorded disbursement intended to satisfy an amount owed.

**More context:** Payment status may refer to initiated, posted, cleared, reversed, or settled stages.

**Implications:** State which stage the data represents and reconcile to independent movement-of-funds evidence where available.

**Also shown as:** payment, payments.

## Ledger

**Definition:** A structured record of financial entries organized by account or entity.

**More context:** Ledgers preserve accounting views but can contain timing entries, adjustments, and errors.

**Implications:** Test balancing logic and reconcile selected entries to source documents and external records.

**Also shown as:** ledger, ledgers.

## Journal entry

**Definition:** A dated accounting record that posts debits and credits to one or more accounts.

**More context:** Manual entries and period-end entries often deserve added review because they can bypass routine flows.

**Implications:** Inspect preparer, approver, timing, account combinations, support, reversals, and access controls.

**Also shown as:** journal entry, journal entries.

## Aggregate

**Definition:** A value formed by grouping and summarizing multiple records.

**More context:** Round totals or concentrated activity can be invisible at row level and visible after grouping.

**Implications:** Declare grouping keys and windows; test how alternate grains change the candidate set.

**Also shown as:** aggregate, aggregation, aggregated.

## Outlier

**Definition:** An observation that is unusual under a stated comparison method.

**More context:** An outlier can reflect rare legitimate activity, data error, population mixture, or manipulation.

**Implications:** Preserve the record, explain the reference population, and seek corroboration before assigning meaning.

**Also shown as:** outlier, outliers, anomaly, anomalies.

## False positive

**Definition:** A flagged item that does not have the target condition under the chosen reference label.

**More context:** Screening rules trade sensitivity against review burden and may flag benign recurring or staged work.

**Implications:** Track disposition evidence and denominator definitions instead of reporting alert counts as accuracy.

**Also shown as:** false positive, false positives.

## Ground truth

**Definition:** The best available reference used to judge an analytical prediction or alert.

**More context:** Legal outcomes, verified records, and synthetic planted labels answer different questions and can each be incomplete.

**Implications:** Document who assigned a label, when, from which evidence, and whether it was available at prediction time.

**Also shown as:** ground truth, reference label, reference labels.

## As-of date

**Definition:** The cutoff that limits analysis to information available by a specified time.

**More context:** Later knowledge can make historical detection look easier than it was.

**Implications:** Enforce availability dates to prevent hindsight leakage and preserve a reproducible decision context.

**Also shown as:** as-of date, as of date, as-of view, as of view.

## Availability date

**Definition:** The earliest defensible date on which a record could have been used by the analyst.

**More context:** Publication, event, retrieval, and database update dates are different clocks.

**Implications:** Choose the clock that matches the claim and retain unknown dates as unknown.

**Also shown as:** availability date, availability dates, available on.

## Cohort

**Definition:** A group of observations selected by shared criteria for comparison.

**More context:** Time, supplier, category, geography, or case status may define a cohort.

**Implications:** Prestate selection rules where possible and inspect size, overlap, missingness, and business-mix differences.

**Also shown as:** cohort, cohorts.

## Empirical CDF

**Definition:** A function giving the observed fraction of values at or below each value.

**More context:** It compares full distributions without selecting histogram bins.

**Implications:** Interpret differences with sample size, dependence, range, and cohort selection; a visual gap is not a fraud probability.

**Also shown as:** empirical CDF, ECDF, empirical cumulative distribution function.

## KS distance

**Definition:** The largest absolute gap between two cumulative distribution functions.

**More context:** The fixture uses it descriptively to compare cohorts.

**Implications:** A distance alone is not a calibrated p-value, causal result, or evidence of manipulation.

**Also shown as:** KS distance, Kolmogorov-Smirnov distance.

## Benford’s law

**Definition:** A leading-digit distribution that can arise for some naturally spanning numerical processes.

**More context:** Fixed prices, assigned ranges, minimums, maximums, identifiers, and selected samples may violate its assumptions.

**Implications:** Use it, if at all, as a documented screen with comparison data and follow-up evidence.

**Also shown as:** Benford’s law, Benford's law, Benford.

## Threshold

**Definition:** A stated cutoff used to route, summarize, or flag records.

**More context:** Testing many cutoffs after seeing answers can inflate apparent discoveries.

**Implications:** Record units, rationale, inclusivity, tuning data, and sensitivity to nearby cutoffs.

**Also shown as:** threshold, thresholds.

## Materiality

**Definition:** The significance of an omission or misstatement in the relevant decision context.

**More context:** Materiality is contextual and may involve qualitative as well as quantitative considerations.

**Implications:** Do not substitute a generic dollar cutoff for the governing accounting, legal, or investigative standard.

**Also shown as:** materiality, material.

## Restitution

**Definition:** A court-ordered payment intended to compensate eligible victims for specified losses.

**More context:** Restitution differs from alleged loss, investor claims, civil damages, forfeiture, penalties, and recovered funds.

**Implications:** Label the amount and procedural stage precisely and cite the controlling public record.

**Also shown as:** restitution.

## Forfeiture

**Definition:** A legal process by which property connected to an offense is surrendered to the government.

**More context:** Forfeiture is not interchangeable with restitution or a fine.

**Implications:** Record whether an amount was sought, ordered, collected, or distributed and avoid double counting remedies.

**Also shown as:** forfeiture, forfeited.

## Indictment

**Definition:** A formal criminal accusation returned by a grand jury in the U.S. federal system.

**More context:** It states allegations and does not establish guilt.

**Implications:** Use allegation language and update the record when a plea, trial, dismissal, sentence, or appeal changes status.

**Also shown as:** indictment, indicted.

## Plea

**Definition:** A defendant’s formal response to criminal charges.

**More context:** A guilty plea may include admitted facts and a plea agreement; a not-guilty plea preserves contest of the charges.

**Implications:** Attribute admissions to the correct defendant and document counts, dates, and later sentencing separately.

**Also shown as:** plea, pleaded guilty, pleaded not guilty, guilty plea.

## Verdict

**Definition:** A fact finder’s decision on charged counts after trial.

**More context:** Different counts can produce different outcomes, and appeals may later alter a judgment.

**Implications:** Record count-level outcomes and the as-of date rather than flattening a case into one label.

**Also shown as:** verdict, convicted, acquitted, acquittal.

## Sentence

**Definition:** The penalty imposed by a criminal court after conviction.

**More context:** A sentence may include imprisonment, supervision, fines, restitution, and forfeiture.

**Implications:** Separate the imposed sentence from time actually served and from civil or administrative remedies.

**Also shown as:** sentence, sentenced, sentencing.

## Civil enforcement

**Definition:** A noncriminal government or private action seeking remedies under civil law.

**More context:** Settlements may resolve claims without admissions, depending on their terms.

**Implications:** Report the forum, claims, disposition, admissions language, and remedies rather than calling every outcome a conviction.

**Also shown as:** civil enforcement, civil case, civil settlement.

## Damages

**Definition:** A monetary measure of legally recognized harm or loss, defined by the relevant claim and proceeding.

**More context:** Estimated loss, proven loss, investor principal, market capitalization change, restitution, and penalties are not interchangeable.

**Implications:** Name the measure, source, time, population, and procedural status before comparing case magnitude.

**Also shown as:** damages, loss, losses.

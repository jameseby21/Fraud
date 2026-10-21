# Fabricated randomness (forensic-v2)

The worked supplier VEN-0088 has 180 fabricated approximately uniform integer-cent values added to ordinary Q4 activity. Compare before/after 2025-10-01 using matched axes, histograms, empirical CDFs and descriptive leading digits. The current cohorts have 86 and 198 rows and a CDF distance about 0.5492. Values and sequence are fabricated, not real-case observations.

Run `distribution_comparison(public_case()['payments'])` from forensic_fixture. It returns cohort sizes and descriptive CDF distance, not a p-value or fraud probability. A supplier's business mix, amount range, minimum/maximum restrictions, dependence and nonrepresentative sampling can change the result. The background samples a bounded award-value pool with inverse-square-root weights; it is not a natural representative invoice distribution.

Benford analysis is not automatic. The exercise reports leading digits without asserting a Benford null. Fixed fees and recurring services are counterexamples to treating regularity as deception. Ask what economic process generated the values and what independent records would support or contradict the apparent change.

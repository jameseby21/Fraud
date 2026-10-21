# Feature backlog

These are proposed small checkpoints, not implemented capabilities or claims that a feature will uncover fraud. Prioritize public-data availability, evidential value, reversibility, and investigator effort. CP-001 is implemented; each subsequent item requires its own failing acceptance test, implementation, regression checks, documented outcome, commit, and verified push.

## Data and provenance

| ID | Feature | Smallest useful acceptance test |
| --- | --- | --- |
| 001 | Public-award quality audit (implemented) | A duplicate record identifies both source CSV rows without a fraud label |
| 002 | Source freshness indicators (implemented) | A fixed clock distinguishes retrieval age from publication age; unknown dates stay unknown |
| 003 | Missing-source coverage view | A blocked download is visible and excluded from archived-source counts |
| 004 | Snapshot comparison | Two retained responses produce added/removed/changed IDs without overwriting either |
| 005 | Field-level change lineage | Every changed field links to both source hashes and values |
| 006 | Intake dry-run | An API request preview writes no data and performs no network request |
| 007 | Public CSV validation preview | Invalid headers return corrective messages before any import |
| 008 | Column mapping preview | A mapping reports ambiguous columns rather than guessing |
| 009 | Duplicate/conflict quarantine | Conflicting stable IDs remain separate until reviewed |
| 010 | Rebuild from raw snapshot | Normalization reproduces output from retained bytes without network access |
| 011 | Source failure recovery | A transient failure does not remove the last successful snapshot |
| 012 | Provenance manifest export | Exported records carry query, retrieval timestamp, source hash, and interpretation |

## Investigator workflow

| ID | Feature | Smallest useful acceptance test |
| --- | --- | --- |
| 013 | Local case notebook | A note survives restart without changing source evidence |
| 014 | Append-only review history | Editing a note adds a revision and preserves the original |
| 015 | Evidence/claim distinction | Observations, allegations, hypotheses, and findings remain distinct in storage and export |
| 016 | Counterevidence log | A case cannot appear fully reviewed while counterevidence remains unaddressed |
| 017 | Lead status workflow | Status transitions are recorded with reasons and can be corrected |
| 018 | Review checklist | Missing independent corroboration remains visible in a draft dossier |
| 019 | Source excerpt locator | Every cited passage includes the document hash and location |
| 020 | Dossier draft export | Facts, uncertainty, alternatives, and missing sources appear together |
| 021 | Correction history | A corrected finding preserves its prior wording and reason |
| 022 | Reviewer disagreement | Conflicting assessments survive without collapsing into a single truth label |
| 023 | Saved investigation filters | Reloading a saved filter reproduces the selected dataset and criteria |
| 024 | Local bookmarks | Bookmarking an award has no effect on its evidence status |

## Statistical screening and validation

| ID | Feature | Smallest useful acceptance test |
| --- | --- | --- |
| 025 | Robust peer-group outliers | Median/MAD scoring abstains for undersized or degenerate groups |
| 026 | Amount-pattern exploration | Heaping is described with denominators and never labeled proof of fraud |
| 027 | Contract modification timeline | A dated event is unavailable before its defensible source availability time |
| 028 | Repeated split-award hypothesis | Nearby awards show the grouping/window and legitimate alternatives |
| 029 | Award concentration measures | Concentration changes are reproducible and qualified by coverage |
| 030 | Entity candidate matching | Similar names generate candidates without automatically merging distinct entities |
| 031 | Reversible entity resolution | Undoing a reviewed merge restores original IDs and relationships |
| 032 | Temporal graph explorer | Every edge has a source record and availability timestamp |
| 033 | Circular-flow controls | Known benign circular settlements demonstrate false-positive behavior |
| 034 | Rule comparison lab | Different rules use the same frozen inputs with versioned parameters |
| 035 | Review-budget evaluation | Precision at K separates unknown labels from confirmed negatives |
| 036 | Temporal holdout runner | No training feature can use information after the cutoff |
| 037 | Entity-disjoint splits | Related projections or resolved entities cannot cross train/test boundaries |
| 038 | Negative-control library | Harmless examples can trigger a rule and remain explicitly benign |
| 039 | Calibration diagnostics | Reliability estimates require adequate labeled data or return insufficient evidence |
| 040 | Drift and coverage checks | Distribution changes are distinguished from changes in record availability |

Statistical checkpoints require suitable public observations and independent labels. The existing top-award sample is not a representative fraud benchmark. No feature should attach fabricated incriminating measurements to unresolved real subjects.

## UI and usability

| ID | Feature | Smallest useful acceptance test |
| --- | --- | --- |
| 041 | URL-addressable views | Reloading a shared local link restores the view and selected case |
| 042 | Clear filters control | One keyboard-accessible action resets all visible filters |
| 043 | Stable table sorting | Equal values retain stable order; headers announce sort state |
| 044 | Pagination with context | Page changes preserve filters and announce the visible result range |
| 045 | Row detail drawer | Opening/closing detail preserves focus and filter state |
| 046 | Keyboard traversal audit | All primary actions are reachable without pointer input |
| 047 | Skip-to-content link | Keyboard users bypass repeated navigation |
| 048 | Loading and recovery states | A failed optional panel does not erase successful neighboring panels |
| 049 | Mobile table alternative | Essential record details remain readable at narrow widths and zoom |
| 050 | Reduced-motion behavior | Replay animation respects the preference and retains manual controls |
| 051 | Accessible status announcements | Search and filter summaries update without stealing focus |
| 052 | Contrast and focus checks | Important text and focus states are checked against stated criteria |
| 053 | Plain-language glossary | Technical terms have contextual explanations without obscuring source facts |
| 054 | Source response comparison | Allegation and response are displayed with dates and coverage gaps |
| 055 | Task-based usability study | Representative users complete defined tasks; time/errors and limitations are recorded |
| 056 | Evidence export preview | Users inspect exactly what is exported, including uncertainty and source coverage |

## Development discipline

| ID | Feature | Smallest useful acceptance test |
| --- | --- | --- |
| 057 | Checkpoint verification command | Missing tests, dirty delivery state, or absent remote is reported rather than silently accepted |
| 058 | CI for offline checks | A clean checkout runs tests and provenance verification without external data access |
| 059 | Browser test separation | Each acceptance flow fails with a scoped diagnostic and cleans up its local server |
| 060 | Reproducible demonstration bundle | A reviewer can run the included example offline from documented steps |

UX decisions should be tied to a task and checked against W3C guidance on [status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html), [keyboard focus](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html), [tables](https://www.w3.org/WAI/tutorials/tables/), and [target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html). These references guide work; they do not substitute for testing with people or establish blanket compliance.

## Local storage extensions

| ID | Feature | Smallest useful acceptance test |
| --- | --- | --- |
| 061 | Encrypted external vault (implemented) | Wrong keys and altered ciphertext fail; a Git-worktree path is rejected |
| 062 | Publication guard (implemented) | A force-added or renamed vault is blocked without printing private values |
| 063 | Encrypted note revisions | Corrections preserve earlier revisions inside encryption and remain absent from public routes |
| 064 | Full optional-dependency CI | Vault tests run rather than being skipped, alongside public-data verification |

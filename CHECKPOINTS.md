# Checkpoint ledger

## Operating rule

One narrowly scoped change at a time: define acceptance, write failing tests, implement, add regression tests for discovered issues, run the relevant checks, record results, review the diff, commit, push, and verify the remote commit before starting the next checkpoint. A missing remote blocks the push gate; it is not permission to silently skip it.

Keep durable state here and in the checkpoint note. At handoff, use a compact summary of verified behavior, remaining risks, commit, and next action. Conversation memory cannot be selectively erased; no claim of memory deletion is made. Avoid carrying abandoned implementation details into the next checkpoint.

## Current checkpoint

| ID | Scope | Validation | Delivery gate |
| --- | --- | --- | --- |
| CP-001 | Public-award quality audit and initial foundation | [Results](docs/checkpoints/CP-001.md) | Pushed and remote verified at 7930f76 |
| CP-002 | Independent publication/retrieval freshness and scoped browser quality checks | [Results](docs/checkpoints/CP-002.md) | Pushed and remote verified at e23ab2d |
| CP-003 | Optional encrypted storage outside Git and web routes | [Results](docs/checkpoints/CP-003.md) | Pushed and remote verified at 4db2c37 |
| CP-004 | Public-repository publication guards and local hooks | [Results](docs/checkpoints/CP-004.md) | Pushed and remote verified at cb30fcf |
| CP-005 | Encrypted local notes and correction history | [Results](docs/checkpoints/CP-005.md) | Pushed and remote verified at 36aa5a8 |
| CP-006 | Full Windows/Linux verification without skipped tests | [Results](docs/checkpoints/CP-006.md) | Pushed and remote verified at 33d7d28; both CI jobs passed |
| CP-007 | Reproducible learning fixture and instructor lineage | [Results](docs/checkpoints/CP-007.md) | Pushed and remote verified at 66baa96; both CI jobs passed |
| CP-008 | Modular courses, notebook lessons, tool tracks and learning UI | [Results](docs/checkpoints/CP-008.md) | Pushed and remote verified at 5bd5367; Windows/Linux CI and Linux R passed |
| CP-009 | Pasted course URL and canonical linked documentation | [Results](docs/checkpoints/CP-009.md) | Pushed and remote verified at 73b6084; CI passed |
| CP-010 | Incremental real-record library and exact-value pool | [Results](docs/checkpoints/CP-010.md) | Pushed and remote verified through 37ced4e; CI passed |
| CP-011 | Relational forensic fixture, instances and analyst lessons | [Results](docs/checkpoints/CP-011.md) | Pushed and remote verified at d821e11; Windows/Linux and both Linux R tracks passed |
| CP-012 | Linked term index, section quizzes and targeted learner suggestions | [Results](docs/checkpoints/CP-012.md) | Pushed and remote verified at 743eb95 |
| CP-013 | Market-capacity statement exercises and retained public corroboration | [Results](docs/checkpoints/CP-013.md) | Pushed and remote verified at 7de33ec |
| CP-014 | Diverse resolved-case outcomes and scoped remedy metadata | [Results](docs/checkpoints/CP-014.md) | Pushed and remote verified at 54768cc |
| CP-015 | Printable cooperative and competitive case-file game | [Results](docs/checkpoints/CP-015.md) | Local implementation and full verification complete; push pending |

The repo had no commits when CP-001 began. Its first commit therefore includes the previously built foundation as well as the quality feature. The 24 existing tests predate this checkpoint; the new quality and API tests were written and observed failing before implementation.

## Next checkpoint, after CP-015

Use owner playtesting feedback to refine wording, pacing, print fit, scoring weights, and the transition from the basic game into Python, R, and Power BI. Power BI Desktop and local Windows R remain manual acceptance checks.

Find the local checkpoint commit with:

```powershell
git log --oneline --grep=CP-001
```

The supplied remote is https://github.com/jameseby21/Fraud. Its initial commit contains a GPL-3.0 license. Integration preserves both histories and that license, retaining the initial local MIT notice in LICENSE-MIT.txt. Do not force-push. Verify the remote ref before marking CP-001 delivered.

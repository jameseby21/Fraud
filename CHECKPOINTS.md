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
| CP-006 | Full Windows/Linux verification without skipped tests | [Results](docs/checkpoints/CP-006.md) | Validated locally; remote CI must pass before next checkpoint |

The repo had no commits when CP-001 began. Its first commit therefore includes the previously built foundation as well as the quality feature. The 24 existing tests predate this checkpoint; the new quality and API tests were written and observed failing before implementation.

## Next checkpoint, after CP-006 passes remote CI

Select the next public research or usability feature from FEATURE_BACKLOG.md. Keep local hooks, source-byte verification, and private storage isolation intact.

Find the local checkpoint commit with:

```powershell
git log --oneline --grep=CP-001
```

The supplied remote is https://github.com/jameseby21/Fraud. Its initial commit contains a GPL-3.0 license. Integration preserves both histories and that license, retaining the initial local MIT notice in LICENSE-MIT.txt. Do not force-push. Verify the remote ref before marking CP-001 delivered.

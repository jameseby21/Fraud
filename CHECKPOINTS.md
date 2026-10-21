# Checkpoint ledger

## Operating rule

One narrowly scoped change at a time: define acceptance, write failing tests, implement, add regression tests for discovered issues, run the relevant checks, record results, review the diff, commit, push, and verify the remote commit before starting the next checkpoint. A missing remote blocks the push gate; it is not permission to silently skip it.

Keep durable state here and in the checkpoint note. At handoff, use a compact summary of verified behavior, remaining risks, commit, and next action. Conversation memory cannot be selectively erased; no claim of memory deletion is made. Avoid carrying abandoned implementation details into the next checkpoint.

## Current checkpoint

| ID | Scope | Validation | Delivery gate |
| --- | --- | --- | --- |
| CP-001 | Read-only public-award quality audit with source-row references and accessible report UI | See [checkpoint note](docs/checkpoints/CP-001.md) | Validated locally; push awaits the repository URL |

The repo had no commits when CP-001 began. Its first commit therefore includes the previously built foundation as well as the quality feature. The 24 existing tests predate this checkpoint; the new quality and API tests were written and observed failing before implementation.

## Next checkpoint, after CP-001 is pushed

CP-002: isolate quality-audit acceptance tests and add source freshness metadata without changing historical findings. Start by reviewing FEATURE_BACKLOG.md and the CP-001 note; do not re-open all raw sources or re-run successful unchanged checks without a reason.

Find the local checkpoint commit with:

```powershell
git log --oneline --grep=CP-001
```

After the user supplies the remote, check its existing history before choosing a push strategy. Do not overwrite an existing remote branch or force-push. Record the actual push result before marking CP-001 delivered.

# Legal outcomes and remedy fields

[Root README](../README.md) is canonical. `data/case_outcomes.json` supplements the sourced narrative in `data/cases.json`. The app merges them by stable case ID and exposes a legal-outcome filter. These fields support comparison and teaching; they are not training labels for a guilt model.

## Outcome fields

| Field | Meaning |
| --- | --- |
| `type` | Procedural resolution category, such as criminal trial, plea, deferred prosecution, consent order, or civil final judgment |
| `criminal_disposition` | Actor-specific criminal result; `not_applicable` is used for a civil or administrative entry, and `deferred` is not a conviction |
| `forum` | Narrow forum description for the recorded outcome |
| `imprisonment_months` | Imprisonment imposed when the cited catalog source and outcome text support it; `null` means this structured entry does not assert a term |
| `remedies` | Named monetary measures with amount, qualifier, and scope |

An acquittal stays an acquittal even when other people in the same broader matter pleaded guilty. A mixed verdict is not flattened into a total conviction. A reversed count stays visible. The HealthSouth catalog deliberately uses separate criminal-acquittal and SEC-civil-judgment records because the parties, burdens, forums, and remedies differ.

## Amounts

The catalog records only a few source-supported remedies needed to demonstrate different legal outcomes. It does not create a common severity score. Restitution, consumer redress, forfeiture, disgorgement, civil penalty, criminal fine, coordinated resolution payment, alleged loss, proven loss, and victim loss answer different questions. Never add or rank them without first resolving overlap, payer, recipient, procedural status, and time.

## Analyst exercise

Filter the library by disposition, then build a table with one row per legal proceeding rather than one row per person or organization. Ask which conclusion the cited record supports, which burden applied, whether the outcome included admissions, and what later appellate or compliance events are missing. Treat those gaps as research tasks rather than negative evidence.

## Debugging

- If a resolved case has no `resolution`, run `python intake.py verify`; catalog validation rejects the mismatch.
- If a monetary amount appears without a scope, reject the record rather than guessing what it represents.
- If two proceedings share a person or organization, keep separate IDs unless one source expressly resolves both.
- If a source page cannot be retained automatically, consult the append-only attempt log and official link. Do not fabricate a local artifact.

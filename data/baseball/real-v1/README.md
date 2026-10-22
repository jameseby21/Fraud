# Real baseball source and analysis v1

[Root README](../../../README.md) is canonical. This is the primary baseball course input. The separate [synthetic practice dataset](../v1/README.md) supplies planted patterns only; none of those records is mixed into this source.

## Attribution and license

Nathan David Pifer (2024), *Optical Tracking Data from College Baseball Scrimmages*, Mendeley Data V3, DOI [10.17632/xfnz6mkdzm.3](https://doi.org/10.17632/xfnz6mkdzm.3), [dataset landing page](https://data.mendeley.com/datasets/xfnz6mkdzm/3). Licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). No endorsement implied. Retain this attribution and license when sharing source data or derived figures.

The original Track_Combo.csv is retained unchanged at `data/library/raw/7b7b8974107be6181dcf1880d609034ef9f7556f9fb13aec021a52d37cd0c190.csv`. Its SHA-256 matches the public repository's file metadata. The file contains 3,344 measured pitch observations and 141 columns. The publisher anonymized player IDs and dates. Those IDs remain consistent, while the Date labels must not be treated as original calendar dates.

## Analysis contract

The learner CSV is the original file, not a normalized or resampled substitute. `baseball_real.py` produces separate descriptive summaries. It parses finite numbers, retains missing values, uses operator TaggedPitchType without guessing an MLB type, defines swings as StrikeSwinging/FoulBall/InPlay and whiffs as StrikeSwinging, and restricts contact-speed summaries to measured InPlay records. Other definitions must be explicitly documented.

Full-file checks: 32 anonymous pitchers and 50 anonymous batters; Fastball has 1,745 rows; there are 381 misses among 1,432 swings (about 26.61%). InPlay has 549 rows, but only 505 have measured ExitSpeed. Those 44 missing values make the contact-mean denominator materially different from the in-play count. The 20 distinct altered Date labels do not reproduce the publisher's stated 21-game count, so this course never infers game count solely from dates. This college-scrimmage sample is not a representative MLB population.

Fields used: PitcherId/BatterId for anonymous player filters, TaggedPitchType for manual classification, RelSpeed for mph, PlateLocSide/PlateLocHeight for source-coordinate feet, ExitSpeed for batted-ball mph, Angle for launch degrees, Inning/PitchNo for within-outing views, and PitchCall for denominators. Source axis signs are preserved; no Statcast sign transformation is applied.

## Incremental intake and reproduction

```powershell
python record_library.py fetch --source baseball-college-trackman-v3
python record_library.py fetch --source baseball-college-trackman-v3 --refresh
python record_library.py verify
python baseball_real.py verify
Rscript courses/tracks/baseball-real.R
```

The configured adapter checks version-3 public file metadata and avoids redownloading the unchanged CSV after verifying retained bytes. A changed pinned hash fails closed and records the attempt. Review and register a new version deliberately; preserve previous raw bytes and append revisions. The [general intake contract](../../../docs/data_intake.md) explains how to add other datasets and adapters. Rebuilding derived summaries does not refresh sources.

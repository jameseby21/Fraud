# Baseball practice pitches v1.0.0

[Root README](../../../README.md) is canonical. `pitches.csv` contains 3,600 entirely fictional selected pitches, six pitchers, twelve batters, three pitch types, six 100-pitch sampled outings per pitcher and two comparison periods. No player name or numeric observation is an actual MLB record. [Research](../../../docs/sports/research.md) and the [2016 archive audit](../../../docs/sports/archive-review.md) inform the workflow and schema, not the numeric values.

## Grain and columns

One row is one independent sampled pitch, identified by pitch_id. The sample does not reconstruct complete games or valid plate-appearance sequences. There are no batting-average, hit, strikeout, home-run, spin or injury labels.

| Fields | Meaning / unit |
| --- | --- |
| pitch_id, game_id, game_date | Fictional stable pitch/outings and dates |
| pitcher, batter, p_throws, stand | Persistent fictional names; pitchers are right-handed, batters alternate L/R |
| period | early or late, three outings per pitcher in each |
| inning, pitch_number | Simplified sampled-outing progression; not an official box score |
| pitch_type | FF four-seam, SL slider, CH changeup |
| speed_mph | Pitch velocity, mph |
| plate_x_ft, plate_z_ft | Plate location, feet, catcher perspective |
| movement_x_in, movement_z_in | Stylized movement, inches, catcher perspective; not total flight displacement |
| in_zone | Inclusive fixed teaching rectangle: x -0.83..0.83, z 1.5..3.5 feet |
| swing, whiff, in_play | Binary indicators; whiff/in_play require swing and are mutually exclusive |
| exit_speed_mph, launch_angle_deg | Fictional tracked contact measurements; blank unless in_play = 1 |
| synthetic | True on every row |

Location is not movement. Movement is already inches; multiplying it by 12 again is an error. Fixed-zone membership is not an umpire call. All pitcher/background identities use the same measurement conventions and no tracking-era pooling is implied.

## Patterns and controls

The separate public instructor key identifies a changing FF share for Rowan Ellis, a within-FF inning-speed decline for Mateo Brooks, location-related SL whiff differences and a late contact-speed increase for Casey Morgan. Four other pitchers have no programmed inning/period trend, and eleven other hitters have no programmed contact-period effect. All have ordinary bounded jitter. Background controls can still show incidental differences.

Whiff rate is sum(whiff)/sum(swing), undefined at zero swings. Mean contact speed uses only tracked balls in play; structural blanks are not zeros. Rate comparisons need counts and matching filters. The course makes no performance, causal, injury or forecasting claim.

```powershell
python baseball.py build
python baseball.py verify
python -m unittest tests.test_baseball
```

The seed is 3152016. The manifest contains generator version, units, grain, row count and CSV SHA-256. Verification reconstructs the CSV, manifest and separate instructor key byte-for-byte; review all changes before rebuilding. Original project-authored fixture records and code follow the repository's data/code licenses; linked articles and archived third-party data are not relicensed.

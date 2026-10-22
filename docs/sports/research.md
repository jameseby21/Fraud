# Baseball course research and design

[Root README](../../README.md) is canonical. Research reviewed October 22, 2026, before selecting the curriculum. Sources are authors' own analyses or official field documentation. The course uses original fictional observations; articles, figures, MLB downloads and archive data are not copied into the learner CSV.

## Projects considered

| Existing example | Procedure worth teaching | Beginner adaptation |
| --- | --- | --- |
| [Petti and Gilani: Using Statcast Pitch Data](https://billpetti.github.io/baseballr/articles/using_statcast_pitch_data.html) | Select a pitcher/date range, validate fields, compare pitch movement, group a single pitch's velocity by inning | Start with a supplied CSV, filter a named player, count the arsenal, scatter movement and pivot mean FF speed by inning. No downloader/package knowledge required |
| [Jim Albert: Pitch Selection, Entropy, and Establishing the Fastball](https://baseballwithr.wordpress.com/2017/05/29/pitch-selection-entropy-and-establishing-the-fastball/) | Describe pitch selection with proportions and compare within-pitcher usage by inning | Use count divided by period total and a control pitcher; leave entropy as an optional extension |
| [Jim Albert: Slider Whiff Rates](https://baseballwithr.wordpress.com/2021/03/01/slider-whiff-rates/) | Compare slider misses per swing inside/outside the zone before more elaborate location models | Make a two-group PivotTable with both numerator and denominator. Omit GAMs, random effects and statistical ranking |
| [Petti and Gilani: Plotting Statcast data](https://billpetti.github.io/baseballr/articles/plotting_statcast.html) | Select a hitter, isolate batted balls, compare contact speed and launch angle across periods | Compare one fictional hitter's period means and contact counts; avoid smoothing and causal claims |
| [Dalpiaz: Reproducing MLB Baseball Savant, CMSAC 2024](https://daviddalpiaz.github.io/cmsac-2024/) | Recreate established baseball displays with transparent data transformations | Useful visual-design reference; not a required package tutorial. The web reader could not ingest the oversized page, so its full procedure was not relied on |

The selected sequence is brief/grain, arsenal mix, within-type velocity, location/whiffs, then hitter contact and a memo. It requires counts, averages, percentages, filters and charts. No regression, MDS, cloud database or specialized baseball package is required.

## Primary real-data walkthrough

The main course now uses the [CC BY 4.0 college tracking dataset by Nathan David Pifer](https://data.mendeley.com/datasets/xfnz6mkdzm/3), with its source [data article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11547889/). The article's visual examples motivate a pitcher-specific speed profile and plate-location display. We retained the actual CSV unchanged, verified the published checksum, and added an incremental adapter. Three real-data lessons cover source/grain, actual anonymous pitcher arsenal and speed, then measured whiffs/contact. The five-lesson synthetic lab is separate practice for known-answer pattern detection, not the default representation of baseball data.

## Field semantics checked

The official [Baseball Savant CSV dictionary](https://baseballsavant.mlb.com/csv-docs) identifies pitch velocity in mph, plate coordinates and movement in feet, catcher-perspective axes, pitch-level descriptions and plate-appearance outcomes. It also distinguishes older PitchF/X-era measurements from current Statcast fields, and documents a 2026 change in plate-location reference. Historical data should not be pooled across tracking conventions without review.

Our fixture stores movement already converted to inches and uses a fixed teaching rectangle. It has no inferred umpire calls, full at-bat sequence, spin measurement, estimated run value, hit outcome or causal label. The columns therefore deliberately differ from a raw Savant export. We retain all selected pitches in the browser plot and show denominators in summaries.

## What is reused

Articles guide the analytical sequence and are linked for further reading. Their prose, code, figures and measured records are not relicensed or bundled. The supplied 2016 project provides the pitcher-filter/px-pz/pitch-color comparison pattern; [the archive audit](archive-review.md) records what was salvageable. The base-R track is an attributed adaptation with fresh offline data and base plotting. The [Excel track](../../courses/tracks/baseball-excel.md) translates every required analysis into spreadsheet actions.

## Rejected initial scope

MDS on unreviewed column positions, live scraping, predictive pitch classification, model-adjusted pitcher rankings, and tracking-system comparisons add prerequisites unrelated to the first course's goals. They can become advanced lessons after the simple denominator and data-grain work is reliable. No article's historical empirical conclusion is presented as a finding from this synthetic sample.

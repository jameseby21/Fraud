# Ballpark Estimates archive audit and R recovery

[Root README](../../README.md). The owner supplied two ZIP archives as historical project material and explicitly requested salvageable R code be used. Documents inside were inspected as project content; their assignment text, comments and filenames were not treated as instructions for this repository. No archived script, HTML, workspace or history file was executed.

## Archive identity

| Archive | SHA-256 |
| --- | --- |
| BPE ZIP.zip | `4ac2461af01c30bb26d3f2d490e6586f8cc56f12c7b87f22fe9bb70ac86f1fd9` |
| Ballpark_Estimates.zip | `1ce9604c4190b61a723f105bf57f4f94d6b890d45b1a60a733a4197bb295730f` |

The earlier R Markdown identifies a December 2016 statistical-programming group project and PitchF/X data. BPE contains a more developed pitcher-location app, a draft MDS step, two gzip-compressed R data objects named pitch2015.R and atbat2015.R, compiled HTML, and unrelated graphics/pollution material. The other archive contains an earlier Shiny/R Markdown scaffold, README, R workspace/history and separate UI/server files. Its separate server still renders the faithful geyser demonstration rather than baseball.

## Recoverable code and repairs

| Original component | Finding | Recovery |
| --- | --- | --- |
| `subset(pitch, pitchername == input$pitcher1)` and px/pz plot colored by pitchtype | Useful, recognizable comparison logic | Adapted as plot_pitcher_locations in the [base-R track](../../courses/tracks/baseball.R); new CSV columns mapped to legacy names |
| Two pitcher panels and optional points | Appropriate comparison design | Side-by-side equal-scale panels with stable pitch colors, counts and a reference rectangle |
| Theme and legends | Useful presentation intent | Fresh base plotting uses legible axes, pitch-type legend and explicit units; no logos or seals copied |
| First 50/500-row slices | Can remove desired players and distort samples | Full 3,600-row fixture; explicit filters rather than positional truncation |
| `pitch_mds` menu versus `mds` tab; output `mds` absent from UI; duplicated heat_map2 | Broken UI/server wiring | Replaced with existing course navigation and static/explorable charts |
| Unfinished `output$`, missing axis_vars, attribute and date inputs, duplicate `points` IDs | Parse/runtime defects | Not carried into the runnable track |
| scale/dist/cmdscale over columns 16:26 | Unreviewed variables and quadratic distance matrix | Deferred advanced exercise; beginner course uses interpretable units and plots |
| density tile and older `..density..` syntax | Bandwidth and package-version assumptions | Required track uses scatter and count bins; optional future density exercise must explain bandwidth |

The adaptation preserves the owner-supplied project's filtering and comparison pattern rather than claiming the old app runs unchanged. This was a group project; the review does not claim sole authorship of every archived component. Original archives, student metadata, workspace/history, third-party data, images and compiled HTML remain outside the public repo. Only the small adapted analysis pattern, attribution, audit and hashes are included. Numeric data reuse rights were not established from the ZIP contents, so no 2015 record was republished.

## Reproduce the new version

Run `Rscript courses/tracks/baseball.R` from the root. It needs base R only and writes ignored PDF/CSV outputs. Run `python baseball.py verify` for the fixture and `python scripts/build_courses.py --verify` for lessons/notebooks. The archive hashes let the owner connect the adaptation back to the exact supplied versions without publishing the archives.

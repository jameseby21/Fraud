"""Primary baseball walkthrough using measured CC BY data; no planted outcomes."""
import json

LESSONS=[
 ('real-brief','1. Inspect real college pitch-tracking data',
  'What is measured, what was anonymized, and what does one row represent?',
  'Start with the real pitch CSV download, Track_Combo.csv. Read data/baseball/real-v1/README.md and the source attribution. In Excel format the data as a table called RealPitches. Keep PitcherId and BatterId as text. Count rows, distinct IDs, pitch tags and PitchCall values. Do not interpret Date as the original date: the publisher altered it. Compare the retained file hash with manifest.json.',
  'The retained source contains 3,344 real pitch observations and 141 columns. It has 1,745 manually tagged Fastball pitches. The publisher describes 21 scrimmages, while the retained file has 20 distinct altered Date labels; do not silently equate distinct dates with game count. Players have persistent anonymous IDs, not invented measurements.',
  'Do not relabel Fastball as a known four-seam type or confuse operator tags with automatic tags. Missing tracking values remain missing. No archive record, fixture value or resampled observation was mixed into the source.',
  'What can this exhibition-game sample support, and which conclusions would need a representative season?', 'bar',
  'assert len(rows)==3344\nassert len(rows[0])==141\nassert summary["pitch_types"]["Fastball"]==1745\nassert summary["anonymized_date_labels"]==20\n'),
 ('real-arsenal','2. Explore an actual pitcher arsenal and speed profile',
  'Which pitches does anonymous pitcher 1000036206 throw, and how do their observed speeds differ?',
  'Filter PitcherId to 1000036206. Pivot TaggedPitchType in rows with count of PitchNo and average RelSpeed in values. Add percentage of pitcher total and a pitch-count bar chart. Make a PlateLocSide versus PlateLocHeight scatter from the same rows. Then compare pitcher 1000103199, tagged Fastball, altered Date label 11/6/2022: chart average RelSpeed by inning with counts, and inspect raw PitchNo versus RelSpeed in Excel. Preserve the source coordinate convention; do not apply a Baseball Savant sign flip.',
  'Pitcher 1000036206 contributes 193 recorded pitches across the retained sample. Pitch tags and measured release speeds can be compared directly in the filtered numeric summary. A pooled inning profile changes when player, pitch type or date filters change. There is no designed improvement or decline in this real dataset; report the observed direction and counts rather than looking for a promised planted result.',
  'Keep all pitch types in the arsenal denominator. Filter a single pitcher, pitch type and anonymized date before interpreting a within-outing speed change. A low-count pitch tag is not an estimate of a reliable arsenal feature.',
  'How much does the pattern change when you isolate one outing instead of pooling all records?', 'line',
  'from baseball_real import select\nplayer=select(rows,pitcher="1000036206")\nassert len(player)==193\nplayer_summary=summarize(player)\nassert sum(player_summary["pitch_types"].values())==193\n'),
 ('real-contact','3. Calculate real whiff rates and compare tracked contact',
  'What do the observed misses and batted-ball speeds show after choosing the correct denominator?',
  'Create a PivotTable by TaggedPitchType and PitchCall. Count StrikeSwinging as whiffs; count StrikeSwinging, FoulBall and InPlay as swings. Divide misses by swings. For contact, filter PitchCall to InPlay and retain nonblank ExitSpeed and Angle. Compare means and sample counts by anonymous BatterId. Pick a hitter with a reasonable sample, make a histogram and write a short scouting note with source, filters, denominators, observed result and limits. Try the separate synthetic baseball practice lab afterward for known-answer pattern detection.',
  'Across the full real CSV there are 381 swinging strikes in 1,432 recorded swings, a whiff rate of about 26.61%. InPlay has 549 rows, but only 505 have measured ExitSpeed: 44 records lack a speed measurement. The contact mean therefore uses 505 values, not 549 zero-filled values. Real values are not altered to make an insight appear. A small anonymous hitter sample does not establish a causal skill change.',
  'FoulBall counts as a swing and contact but not InPlay in this definition. Do not treat BallCalled, StrikeCalled or HitByPitch as swings. Empty ExitSpeed is not zero. Do not average subgroup whiff percentages; pool misses and swings.',
  'Which descriptive observation is robust to a reasonable filter change, and which new evidence would improve confidence?', 'histogram',
  'assert summary["whiffs"]==381 and summary["swings"]==1432\nassert abs(summary["whiff_rate"]-381/1432)<1e-12\nassert summary["in_play"]==549\n')]


def artifacts():
    files,entries={},[]
    setup='''from pathlib import Path
import sys
root=Path.cwd().resolve()
while not (root/"baseball_real.py").exists() and root!=root.parent:
    root=root.parent
if not (root/"baseball_real.py").exists():
    raise RuntimeError("Open the notebook inside the cloned repository.")
if str(root) not in sys.path: sys.path.insert(0,str(root))
from baseball_real import read_rows, summarize, render_chart
rows=read_rows()
summary=summarize(rows)
assert len(rows)==3344
'''
    for slug,title,question,activity,check,debug,reflection,chart,exercise in LESSONS:
        md=f'''# {title}

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters, counts and averages. Dataset: real college TrackMan observations, DOI 10.17632/xfnz6mkdzm.3. CC BY 4.0. Source CSV is unchanged; anonymous IDs and altered dates are retained.

## Question

{question}

## Try it

{activity}

Use the Excel/spreadsheet guide first, or the adjacent Python notebook, base-R or Power BI track. The real dataset is separate from the optional 3,600-row synthetic practice fixture. Attribution: Nathan David Pifer (2024), Optical Tracking Data from College Baseball Scrimmages, Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0. No endorsement implied.

## Check your work

{check}

## Debugging

{debug}

## Reflection

{reflection}

## Record your learning

Record source DOI/version, CSV SHA-256, tool, selected anonymous IDs, all filters, counts, units and one limitation. See docs/sports/research.md and courses/templates/feedback.md; keep working files in ignored output/.
'''
        files[f'courses/baseball-fieldwork/{slug}.md']=md.encode()
        cells=[]
        for cell_id,kind,body in [('guide','markdown',md),('setup','code',setup),('try','markdown','Try the spreadsheet task before executing the worked check.'),('check','code',exercise),('visual','code',f'svg=render_chart("{chart}",pitcher="1000036206")\n# Optional Jupyter: from IPython.display import SVG, display; display(SVG(svg))\n')]:
            cell=dict(cell_type=kind,id=cell_id,metadata={},source=body.splitlines(keepends=True))
            if kind=='code':cell.update(execution_count=None,outputs=[])
            cells.append(cell)
        files[f'courses/baseball-fieldwork/{slug}.ipynb']=(json.dumps(dict(cells=cells,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.12')),nbformat=4,nbformat_minor=5),indent=2)+'\n').encode()
        entries.append(dict(id=slug,title=title,chart=chart,minutes=25))
    return files,dict(id='baseball-fieldwork',title='Baseball analytics: real pitch fieldwork',topic='sports',dataset='baseball-real-v1',lessons=entries)

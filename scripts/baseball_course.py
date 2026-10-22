"""Reviewed baseball curriculum; consumed by the shared course generator."""
import json

LESSONS = [
    ('pitch-brief','1. Take the baseball analyst brief and inspect the file',
     'What does one pitch row represent, and which baseball questions can a small sample answer?',
     'Start in Excel or LibreOffice with data/baseball/v1/pitches.csv. Format it as a table called Pitches. Count pitch_id, distinct pitcher and batter names, pitch types, game IDs and missing contact fields. Compare the file hash with manifest.json. This is an independent-pitch teaching sample, not complete games or valid sequences of plate appearances. Read docs/sports/research.md and the archive review before drawing a baseball conclusion.',
     'There are 3,600 unique pitch rows, six fictional pitchers, twelve fictional batters and three pitch types: FF, SL and CH. Each pitcher has six sampled outings with 100 pitches each. Contact speed and launch angle are blank on pitches not put in play. No numeric observation comes from an MLB player.',
     'A .R filename in an old archive may contain serialized data rather than source code. Use the supplied plain CSV for this course. Do not fill missing contact speeds with zero or treat one pitch as one at-bat.',
     'Which statement belongs in a scouting memo, and which would require complete games, opponent context, or independent observation?', 'bar',
     'assert len(rows) == 3600\nassert len({r["pitch_id"] for r in rows}) == 3600\nassert len({r["batter"] for r in rows}) == 12\n'),
    ('pitch-mix','2. Compare a pitcher arsenal with a PivotTable',
     'Did Rowan Ellis change pitch selection between the early and late sample periods?',
     'Filter pitcher to Rowan Ellis. In a PivotTable put period in rows, pitch_type in columns and count of pitch_id in values. Show values as percentage of row total. Draw grouped or 100-percent-stacked bars with sample counts beside percentages. Repeat for Theo Bennett as the control. Use the pitcher and pitch-type selectors in the reference preview to explore movement and location; chart the full CSV in your spreadsheet to compare periods.',
     'Rowan Ellis throws 180 FF pitches out of 300 early pitches (60%) and 120 out of 300 late pitches (40%). That is a 20 percentage-point decrease, or a one-third relative decrease. Theo Bennett stays at 50% in both periods. The change is deliberately planted; equal sample sizes make this an easy first comparison.',
     'Percentage of grand total answers a different question from percentage of each period row. Keep all pitch types in the denominator. Filter to one pitch type after computing a full arsenal share only when your measure preserves that denominator.',
     'Does changing the pitch mix prove better performance? What would opponent handedness, count and score context add?', 'movement',
     'mix = {(r["pitcher"], r["period"], r["pitch_type"]): r for r in summary["pitch_mix"]}\nassert mix["Rowan Ellis", "early", "FF"]["share"] == .6\nassert mix["Rowan Ellis", "late", "FF"]["share"] == .4\n'),
    ('inning-velocity','3. Separate pitch mix from velocity by inning',
     'Is Mateo Brooks throwing the same pitch more slowly in later innings?',
     'Filter pitcher to Mateo Brooks and pitch_type to FF. Pivot by inning with average speed_mph and count of pitch_id. Make a line chart with markers; label the mph axis and show group sizes. Compare innings 1-2 pooled against innings 6-7 pooled using the underlying pitches. Repeat for Theo Bennett. Then remove the pitch-type filter and explain why a changing arsenal can change the overall mean even without a within-type speed change.',
     'Mateo Brooks has a programmed within-FF decline: the pooled innings 1-2 mean exceeds innings 6-7 by more than 1.5 mph. The control pitcher has no programmed inning trend, but ordinary jitter remains. Means must be weighted by pitch counts when combining groups.',
     'Do not average inning means without weights when counts differ. Pitch velocity is mph; movement is inches and location is feet. A truncated mph axis can reveal a small change, but label its limits rather than implying a zero baseline.',
     'Could selection into later innings, workload, weather, or measurement explain a real pattern? Why is this fixture insufficient for an injury diagnosis?', 'line',
     'ff = [r for r in rows if r["pitcher"] == "Mateo Brooks" and r["pitch_type"] == "FF"]\nearly = [r["speed_mph"] for r in ff if r["inning"] <= 2]\nlate = [r["speed_mph"] for r in ff if r["inning"] >= 6]\nassert sum(early)/len(early) - sum(late)/len(late) > 1.5\n'),
    ('whiff-zones','4. Map pitch locations and calculate whiffs per swing',
     'Does the observed slider whiff rate differ inside and outside the teaching zone?',
     'Filter pitch_type to SL. Plot plate_x_ft versus plate_z_ft from the catcher perspective, with equal physical scales. The fixed teaching zone is -0.83 to 0.83 feet horizontally and 1.5 to 3.5 feet vertically, inclusive. Pivot by in_zone and sum swing and whiff. Divide total whiffs by total swings in each group. For a warm-up, 12 misses in 24 swings is what percentage? Repeat with pitcher and batter-hand filters, always retaining group counts.',
     'The warm-up whiff rate is 50%, because 12 divided by 24 equals 0.5. In the fixture, SL is programmed to miss more often per swing outside the teaching zone. Exact observed counts are in the numeric summary and instructor key. Whiffs divided by pitches is a different rate. A fixed rectangle is a teaching classification, not an umpire-call model.',
     'A zero-swing group has an undefined rate, not 0%. Use SUM(whiff)/SUM(swing); do not average subgroup percentages. Keep the catcher viewpoint and equal coordinate scales when comparing pitchers. Batters have different real strike-zone heights; the fixture uses one reference rectangle.',
     'Why does a high out-of-zone whiff rate fail to prove that throwing every pitch outside is a good strategy?', 'scatter',
     'zones = [r for r in summary["whiff_by_zone"] if r["pitch_type"] == "SL"]\nassert all(abs(r["whiff_rate"] - r["whiffs"]/r["swings"]) < 1e-12 for r in zones)\nassert next(r for r in zones if not r["in_zone"])["whiff_rate"] > next(r for r in zones if r["in_zone"])["whiff_rate"]\n'),
    ('contact-report','5. Compare hitter contact and write a scouting note',
     'Did Casey Morgan recorded contact change, and what can a small batted-ball sample establish?',
     'Filter batter to Casey Morgan and in_play to 1. Pivot period with average exit_speed_mph, average launch_angle_deg and count of pitch_id. Draw an exit-speed histogram and period comparison. Repeat for another batter and keep sample sizes visible. Write a one-page note with source/version, filters, counts, units, two observations, an alternative explanation and a next-data request. Follow the Excel guide for exact formulas and the R track for a restored side-by-side pitcher plot.',
     'Casey Morgan has a deliberately planted late-period contact-speed increase greater than 3 mph in the realized sample. Contact fields are populated only for tracked balls in play. The observed shift does not measure batting average, home-run probability or a causal swing improvement. Other batters show ordinary variation without a programmed period effect.',
     'Use only nonblank contact observations. Never turn missing exit speed on a taken pitch or swing-and-miss into 0 mph. A mean of per-game means differs from the pitch-weighted mean when contact counts vary.',
     'Which finding survives a reasonable filter change, and what new sample would you collect before giving a coach advice?', 'histogram',
     'contact = {r["period"]: r for r in summary["contact"] if r["batter"] == "Casey Morgan"}\nassert contact["late"]["mean_exit_speed_mph"] - contact["early"]["mean_exit_speed_mph"] > 3\n')
]


def artifacts():
    files, entries = {}, []
    setup = '''from pathlib import Path
import sys
root = Path.cwd().resolve()
while not (root / "baseball.py").exists() and root != root.parent:
    root = root.parent
if not (root / "baseball.py").exists():
    raise RuntimeError("Open this notebook inside the cloned repository.")
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from baseball import read_rows, summarize, render_chart
rows = read_rows()
summary = summarize(rows)
assert len(rows) == 3600
'''
    for lesson_id,title,question,activity,check,debug,reflection,chart,exercise in LESSONS:
        md=f'''# {title}

Estimated time: 20-30 minutes. Prerequisite: spreadsheet filters and averages; no modeling or special library required. Dataset: data/baseball/v1/pitches.csv, version 1.0.0. All player identities and observations are fictional.

## Question

{question}

## Try it

{activity}

Use the Excel / spreadsheet track first, or the adjacent Python notebook, courses/tracks/baseball.R, or the baseball Power BI guide. All tracks use the same CSV, grain and units. Save work in ignored output/.

## Check your work

{check}

## Debugging

{debug}

## Reflection

{reflection}

## Record your learning

Record lesson ID, tool, input hash, filters, numerator/denominator, observed result and one issue in courses/templates/feedback.md copied to ignored output/. Consult docs/sports/research.md for procedural sources and docs/sports/archive-review.md for the original project adaptation.
'''
        files[f'courses/baseball-lab/{lesson_id}.md']=md.encode()
        cells=[]
        for cell_id,kind,content in [('guide','markdown',md),('setup','code',setup),('practice','markdown','Try the task before revealing the worked check.'),('worked-check','code',exercise),('visual','code',f'svg = render_chart("{chart}", pitcher="Rowan Ellis")\n# Optional Jupyter display: from IPython.display import SVG, display; display(SVG(svg))\n')]:
            cell=dict(cell_type=kind,id=cell_id,metadata={},source=content.splitlines(keepends=True))
            if kind=='code':cell.update(execution_count=None,outputs=[])
            cells.append(cell)
        notebook=dict(cells=cells,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.12')),nbformat=4,nbformat_minor=5)
        files[f'courses/baseball-lab/{lesson_id}.ipynb']=(json.dumps(notebook,indent=2)+'\n').encode()
        entries.append(dict(id=lesson_id,title=title,chart=chart,minutes=25))
    return files,dict(id='baseball-lab',title='Ballpark estimates: synthetic practice',topic='sports',dataset='baseball-v1',lessons=entries)

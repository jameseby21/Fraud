"""Real, attributed college baseball source adapter and descriptive course views."""
from collections import Counter, defaultdict
import csv
import hashlib
import html
import io
import json
import math
from pathlib import Path
import statistics

import record_library

ROOT=Path(__file__).resolve().parent
SOURCE_ID='baseball-college-trackman-v3'
SHA='7b7b8974107be6181dcf1880d609034ef9f7556f9fb13aec021a52d37cd0c190'
ATTRIBUTION='Nathan David Pifer (2024), Optical Tracking Data from College Baseball Scrimmages, Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3. CC BY 4.0.'
CHARTS={'bar':'Real pitch-type counts','scatter':'Real plate locations (source feet)',
        'line':'Real mean release speed by inning (mph)','histogram':'Real tracked in-play exit-speed distribution (mph)'}
SWINGS={'StrikeSwinging','FoulBall','InPlay'}


def number(value):
    try:
        result=float(value)
        return result if math.isfinite(result) else None
    except (ValueError,TypeError):return None


def read_rows():
    _,payload=record_library.record_download(SOURCE_ID)
    if hashlib.sha256(payload).hexdigest()!=SHA:raise ValueError('Real baseball source hash changed')
    return list(csv.DictReader(io.StringIO(payload.decode('utf-8-sig'))))


def filters():
    rows=read_rows()
    return {key:sorted({r[column] for r in rows}) for key,column in
            [('pitcher','PitcherId'),('batter','BatterId'),('pitch_type','TaggedPitchType'),('game_date','Date')]}


def select(rows, pitcher='',batter='',pitch_type='',game_date=''):
    criteria={'PitcherId':pitcher,'BatterId':batter,'TaggedPitchType':pitch_type,'Date':game_date}
    for key,value in criteria.items():
        if value and value not in {r[key] for r in read_rows()}:raise ValueError('Unknown baseball filter')
    return [r for r in rows if all(not value or r[key]==value for key,value in criteria.items())]


def summarize(rows):
    swings=sum(r['PitchCall'] in SWINGS for r in rows)
    whiffs=sum(r['PitchCall']=='StrikeSwinging' for r in rows)
    groups=defaultdict(list)
    for row in rows:groups[row['TaggedPitchType']].append(row)
    means=lambda values:statistics.mean(values) if values else None
    contact=[number(r['ExitSpeed']) for r in rows if r['PitchCall']=='InPlay' and number(r['ExitSpeed']) is not None]
    return dict(synthetic=False,source_id=SOURCE_ID,source_sha256=SHA,attribution=ATTRIBUTION,row_count=len(rows),
        anonymous_pitchers=len({r['PitcherId'] for r in rows}),anonymous_batters=len({r['BatterId'] for r in rows}),
        anonymized_date_labels=len({r['Date'] for r in rows}),pitch_types=dict(Counter(r['TaggedPitchType'] for r in rows)),
        swings=swings,whiffs=whiffs,whiff_rate=whiffs/swings if swings else None,
        in_play=sum(r['PitchCall']=='InPlay' for r in rows),measured_in_play_exit_speeds=len(contact),mean_in_play_exit_mph=means(contact),
        by_pitch_type=[dict(pitch_type=k,pitches=len(v),share=len(v)/len(rows),
            measured_speeds=sum(number(r['RelSpeed']) is not None for r in v),
            mean_release_mph=means([number(r['RelSpeed']) for r in v if number(r['RelSpeed']) is not None]),
            swings=sum(r['PitchCall'] in SWINGS for r in v),whiffs=sum(r['PitchCall']=='StrikeSwinging' for r in v)) for k,v in sorted(groups.items())],
        limits='Real anonymized college scrimmages, not MLB or representative season data. Date labels are altered; no original calendar dates or game count inferred. Rates are descriptive.')


def artifacts():
    summary=summarize(read_rows())
    manifest=dict(source_id=SOURCE_ID,doi='10.17632/xfnz6mkdzm.3',source_version=3,sha256=SHA,
        attribution=ATTRIBUTION,license='CC-BY-4.0',license_url='https://creativecommons.org/licenses/by/4.0/',
        landing_url='https://data.mendeley.com/datasets/xfnz6mkdzm/3',raw_modified=False,
        transformations=['CSV fields preserved verbatim in learner input','Summaries parse finite numerical values without imputation',
            'Swing = PitchCall in StrikeSwinging, FoulBall, InPlay; whiff = StrikeSwinging',
            'Contact summary restricts to InPlay with measured ExitSpeed; anonymous IDs and altered dates unchanged'],
        row_count=summary['row_count'])
    encode=lambda value:(json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
    return {'data/baseball/real-v1/manifest.json':encode(manifest),
            'data/baseball/real-v1/instructor/observations.json':encode(summary)}


def verify():
    if len(read_rows())!=3344:raise ValueError('Real baseball row count changed')
    for path,payload in artifacts().items():
        if not (ROOT/path).exists() or (ROOT/path).read_bytes()!=payload:raise ValueError('Real baseball derived drift: '+path)
    return dict(valid=True,rows=3344,synthetic=False)


def render_chart(name,**criteria):
    if name not in CHARTS:raise KeyError(name)
    rows=select(read_rows(),**criteria);esc=html.escape
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 500" role="img" aria-labelledby="title desc"><title id="title">{esc(CHARTS[name])}</title><desc id="desc">Real anonymized college pitches. {len(rows)} matching rows. Original source unchanged. Descriptive sample; no causal claim.</desc><rect width="850" height="500" fill="white"/><g fill="#172d38" font-family="sans-serif" font-size="12"><text x="35" y="25">{esc(CHARTS[name])}; n={len(rows)}</text>']
    def text(x,y,value):parts.append(f'<text x="{x}" y="{y}">{esc(str(value))}</text>')
    if not rows:text(40,120,'No rows match these filters.')
    elif name=='scatter':
        points=[(number(r['PlateLocSide']),number(r['PlateLocHeight']),r) for r in rows]
        points=[p for p in points if p[0] is not None and p[1] is not None]
        if points:
            xmin,xmax=min(p[0] for p in points),max(p[0] for p in points);ymin,ymax=min(p[1] for p in points),max(p[1] for p in points)
            scale=min(650/max(1,xmax-xmin),320/max(1,ymax-ymin))
            for x,y,row in points:
                parts.append(f'<circle cx="{80+(x-xmin)*scale:.2f}" cy="{390-(y-ymin)*scale:.2f}" r="2" fill="#1768ac" opacity=".4"><title>Pitcher {esc(row["PitcherId"])} {esc(row["TaggedPitchType"])}: {x}, {y} feet</title></circle>')
            text(45,420,f'Horizontal PlateLocSide: {xmin:.2f} to {xmax:.2f} ft; vertical PlateLocHeight: {ymin:.2f} to {ymax:.2f} ft')
            text(45,440,f'{len(points)} measured locations; equal units; source sign preserved, no Savant-axis conversion')
    elif name=='line':
        groups=defaultdict(list)
        for row in rows:
            value=number(row['RelSpeed'])
            if value is not None:groups[int(row['Inning'])].append(value)
        means={i:statistics.mean(v) for i,v in sorted(groups.items())}
        if means:
            low=min(means.values())-1;high=max(means.values())+1;previous=None
            for inning,value in means.items():
                x=70+inning*650/max(means);y=380-(value-low)*280/(high-low)
                if previous:parts.append(f'<line x1="{previous[0]}" y1="{previous[1]}" x2="{x}" y2="{y}" stroke="#1768ac"/>')
                parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#1768ac"><title>inning {inning}, n={len(groups[inning])}, mean {value:.3f} mph</title></circle>');text(x,410,inning);previous=x,y
            text(40,80,f'Mean mph axis: {low:.2f} to {high:.2f} (truncated); innings on x; hover for counts')
            text(40,440,'Filter one pitcher, pitch type and anonymized date before interpreting a within-outing change.')
    else:
        if name=='bar':bars=sorted(Counter(r['TaggedPitchType'] for r in rows).items())
        else:
            values=[number(r['ExitSpeed']) for r in rows if r['PitchCall']=='InPlay'];values=[v for v in values if v is not None]
            bars=[(f'{a}–<{a+10}',sum(a<=v<a+10 for v in values)) for a in range(0,150,10)]
        maximum=max((v for _,v in bars),default=1) or 1
        step=740/max(1,len(bars))
        for i,(label,value) in enumerate(bars):
            x=60+i*step;h=280*value/maximum
            parts.append(f'<rect x="{x:.1f}" y="{380-h:.1f}" width="{step*.7:.1f}" height="{h:.1f}" fill="#1768ac"/>');text(round(x),400,label);text(round(x),round(370-h),value)
        text(30,380,'0');text(30,100,maximum)
        text(40,440,'Counts; all selected pitches' if name=='bar' else 'Counts; measured InPlay contact only; equal 10 mph bins from 0 to <150')
    text(30,475,'Source: N. D. Pifer, Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0')
    parts.append('</g></svg>');return ''.join(parts)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['build','verify']);args=parser.parse_args()
    if args.command=='build':
        for path,payload in artifacts().items():(ROOT/path).parent.mkdir(parents=True,exist_ok=True);(ROOT/path).write_bytes(payload)
    print(json.dumps(verify(),indent=2))

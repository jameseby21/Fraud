"""Offline baseball teaching fixture, descriptive analysis, and accessible SVGs."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import date, timedelta
import hashlib
import html
import io
import json
from pathlib import Path
import random
import statistics

ROOT = Path(__file__).resolve().parent
VERSION = '1.0.0'
PITCHERS = ['Rowan Ellis','Mateo Brooks','Theo Bennett','Adrian Cole','Jordan Hayes','Avery Reed']
BATTERS = ['Casey Morgan','Drew Parker','Alex Sutton','Blake Quinn','Cameron Wells','Emery Lane',
           'Finley Ross','Harper Shaw','Jamie Hart','Kendall Ames','Logan Finch','Reese Taylor']
TYPES = ['FF','SL','CH']
CHARTS = {
    'bar':'Pitch mix: counts by pitch type', 'line':'Fastball velocity by inning (mph)',
    'histogram':'Pitch speed distribution (mph)', 'scatter':'Pitch locations: catcher perspective (feet)',
    'box':'Pitch velocity spread: min/max and quartiles (mph)',
    'heatmap':'Location grid: pitch counts, not density', 'pareto':'Whiff rate by pitch type (whiffs / swings)',
    'movement':'Pitch movement: catcher perspective (inches)',
}


def rate(numerator, denominator):
    return numerator / denominator if denominator else None


def build_rows():
    rng = random.Random(3152016)
    rows = []
    for p, pitcher in enumerate(PITCHERS):
        for game in range(6):
            period = 'early' if game < 3 else 'late'
            ff = (60 if game < 3 else 40) if p == 0 else 50
            pitches = ['FF']*ff + ['SL']*30 + ['CH']*(70-ff)
            rng.shuffle(pitches)
            for j, pitch_type in enumerate(pitches):
                inning = j // 15 + 1
                batter = BATTERS[(j + p*3 + game) % len(BATTERS)]
                stand = 'L' if BATTERS.index(batter) % 2 else 'R'
                # Stable grid with jitter, spanning a transparent teaching rectangle.
                col, band = j % 3, (j // 3) % 3
                px = round([-1.1,0,1.1][col] + rng.uniform(-.2,.2),3)
                pz = round([1.3,2.5,3.7][band] + rng.uniform(-.15,.15),3)
                in_zone = abs(px) <= .83 and 1.5 <= pz <= 3.5
                swing = int(rng.random() < (.7 if in_zone else .45))
                miss_chance = (.5 if not in_zone else .2) if pitch_type == 'SL' else .18
                whiff = int(swing and rng.random() < miss_chance)
                in_play = int(swing and not whiff and rng.random() < .65)
                speed = {'FF':94,'SL':84,'CH':85}[pitch_type] + p*.25 + rng.uniform(-1,1)
                if p == 1 and pitch_type == 'FF':
                    speed -= max(0, inning-2)*.55
                move_x, move_z = {'FF':(-7,15),'SL':(5,2),'CH':(-10,6)}[pitch_type]
                exit_speed = None
                launch_angle = None
                if in_play:
                    exit_speed = round(87 + rng.uniform(-12,12) + (6 if batter=='Casey Morgan' and period=='late' else 0),1)
                    launch_angle = round(rng.uniform(-15,40),1)
                rows.append(dict(pitch_id=f'P-{p+1}-{game+1}-{j+1:03}',game_id=f'G-{p+1}-{game+1}',
                    game_date=(date(2025,5,1)+timedelta(days=game*5+p)).isoformat(),period=period,
                    pitcher=pitcher,batter=batter,p_throws='R',stand=stand,inning=inning,
                    pitch_number=j+1,pitch_type=pitch_type,speed_mph=round(speed,1),
                    plate_x_ft=px,plate_z_ft=pz,movement_x_in=round(move_x+rng.uniform(-2,2),1),
                    movement_z_in=round(move_z+rng.uniform(-2,2),1),in_zone=int(in_zone),
                    swing=swing,whiff=whiff,in_play=in_play,exit_speed_mph=exit_speed,
                    launch_angle_deg=launch_angle,synthetic=True))
    return rows


def select(rows, pitcher='', batter='', pitch_type=''):
    for field, value, allowed in [('pitcher',pitcher,PITCHERS),('batter',batter,BATTERS),('pitch_type',pitch_type,TYPES)]:
        if value and value not in allowed:
            raise ValueError('Unknown '+field)
    return [r for r in rows if (not pitcher or r['pitcher']==pitcher) and
            (not batter or r['batter']==batter) and (not pitch_type or r['pitch_type']==pitch_type)]


def read_rows():
    with (ROOT/'data/baseball/v1/pitches.csv').open(encoding='utf-8',newline='') as stream:
        rows = list(csv.DictReader(stream))
    ints = ['inning','pitch_number','in_zone','swing','whiff','in_play']
    floats = ['speed_mph','plate_x_ft','plate_z_ft','movement_x_in','movement_z_in','exit_speed_mph','launch_angle_deg']
    for row in rows:
        for key in ints: row[key]=int(row[key])
        for key in floats: row[key]=float(row[key]) if row[key] else None
        row['synthetic']=row['synthetic']=='True'
    return rows


def summarize(rows):
    mix, velocity, zones, contact = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    for r in rows:
        mix[r['pitcher'],r['period'],r['pitch_type']].append(r)
        if r['pitch_type']=='FF': velocity[r['pitcher'],r['inning']].append(r['speed_mph'])
        zones[r['pitch_type'],r['in_zone']].append(r)
        if r['in_play']: contact[r['batter'],r['period']].append(r)
    totals = Counter((r['pitcher'],r['period']) for r in rows)
    return dict(row_count=len(rows),
        pitch_mix=[dict(pitcher=p,period=t,pitch_type=k,count=len(v),share=rate(len(v),totals[p,t])) for (p,t,k),v in sorted(mix.items())],
        velocity_by_inning=[dict(pitcher=p,inning=i,count=len(v),mean_mph=statistics.mean(v)) for (p,i),v in sorted(velocity.items())],
        whiff_by_zone=[dict(pitch_type=k,in_zone=z,pitches=len(v),swings=sum(r['swing'] for r in v),
            whiffs=sum(r['whiff'] for r in v),whiff_rate=rate(sum(r['whiff'] for r in v),sum(r['swing'] for r in v))) for (k,z),v in sorted(zones.items())],
        contact=[dict(batter=b,period=p,tracked_balls_in_play=len(v),mean_exit_speed_mph=statistics.mean(r['exit_speed_mph'] for r in v),
            mean_launch_angle_deg=statistics.mean(r['launch_angle_deg'] for r in v)) for (b,p),v in sorted(contact.items())])


def artifacts():
    rows=build_rows()
    stream=io.StringIO(newline=''); writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n'); writer.writeheader(); writer.writerows(rows)
    data=stream.getvalue().encode()
    summary=summarize(rows)
    answers=dict(version=VERSION,findings=[
        'Rowan Ellis FF share falls from 60% (180/300) early to 40% (120/300) late; Theo Bennett stays at 50%.',
        'Mateo Brooks loses more than 1.5 mph comparing FF innings 1-2 versus 6-7. Other pitchers have no programmed inning trend.',
        'SL whiffs per swing are higher outside the teaching zone; check denominator and counts before interpreting.',
        'Casey Morgan has a programmed late-period exit-speed increase; it is descriptive, not proof of a mechanical change.'
        ],summary=summary)
    manifest=dict(version=VERSION,rows=len(rows),sha256=hashlib.sha256(data).hexdigest(),seed=3152016,
        source='Entirely fabricated; schema and workflow informed by cited baseball research and the owner-supplied 2016 project.',
        grain='one independent recorded pitch; sample is not a complete game or legal sequence of plate appearances',
        observation_units=dict(speed='mph',location='feet, catcher perspective',movement='inches, catcher perspective',exit_speed='mph'))
    encode=lambda value:(json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
    return {'data/baseball/v1/pitches.csv':data,'data/baseball/v1/manifest.json':encode(manifest),
            'data/baseball/v1/instructor/answers.json':encode(answers)}


def render_chart(name, pitcher='', batter='', pitch_type=''):
    if name not in CHARTS: raise KeyError(name)
    rows=select(read_rows(),pitcher,batter,pitch_type)
    esc=html.escape
    title=CHARTS[name]
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 440" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">All {len(rows)} filtered fictional pitches. Counts and units shown; no causal conclusions. Catcher perspective for location and movement.</desc><rect width="800" height="440" fill="#ffffff"/><g font-family="sans-serif" font-size="12" fill="#172d38"><text x="35" y="24">{esc(title)}</text><text x="35" y="44">{esc(pitcher or "All pitchers")} / {esc(batter or "All batters")} / {esc(pitch_type or "All types")} — n={len(rows)}</text>']
    def text(x,y,s): parts.append(f'<text x="{x}" y="{y}">{esc(str(s))}</text>')
    def line(x1,y1,x2,y2,color='#64748b'): parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"/>')
    colors={'FF':'#1768ac','SL':'#b64517','CH':'#6b4e96'}
    if not rows:
        text(50,100,'No pitches match these filters.')
    elif name in ('scatter','movement'):
        movement=name=='movement'
        xkey,ykey=('movement_x_in','movement_z_in') if movement else ('plate_x_ft','plate_z_ft')
        xmin,xmax,ymin,ymax=(-15,15,-5,20) if movement else (-2.5,2.5,0,5)
        # Equal screen units in both dimensions; axes never silently crop pitches.
        scale=12 if movement else 60
        x=lambda value:400+(value-(xmin+xmax)/2)*scale
        y=lambda value:250-(value-(ymin+ymax)/2)*scale
        line(x(xmin),y(ymin),x(xmax),y(ymin)); line(x(xmin),y(ymin),x(xmin),y(ymax))
        for value in ([ -10,0,10] if movement else [-2,-1,0,1,2]): text(x(value),y(ymin)+18,value)
        for value in ([0,10,20] if movement else [0,1,2,3,4,5]): text(x(xmin)-30,y(value),value)
        if not movement:
            parts.append(f'<rect x="{x(-.83)}" y="{y(3.5)}" width="{1.66*scale}" height="{2*scale}" fill="none" stroke="#172d38"/>')
        for row in rows:
            parts.append(f'<circle cx="{x(row[xkey]):.2f}" cy="{y(row[ykey]):.2f}" r="2" fill="{colors[row["pitch_type"]]}" opacity=".35"><title>{esc(row["pitch_id"])} {row["pitch_type"]}: {row[xkey]}, {row[ykey]}</title></circle>')
        text(75,410,'FF blue; SL orange; CH purple. Axes: '+('movement inches' if movement else 'plate feet; rectangle is a fixed teaching zone'))
    elif name=='line':
        for p in sorted({r['pitcher'] for r in rows}):
            groups=defaultdict(list)
            for r in rows:
                if r['pitcher']==p and r['pitch_type']=='FF': groups[r['inning']].append(r['speed_mph'])
            previous=None
            color=['#1768ac','#b64517','#6b4e96','#167d4c','#ad3367','#756000'][PITCHERS.index(p)]
            for inning,values in sorted(groups.items()):
                xx,yy=75+inning*85,370-(statistics.mean(values)-88)*30
                if previous: line(*previous,xx,yy,color)
                parts.append(f'<circle cx="{xx}" cy="{yy}" r="4" fill="{color}"><title>{esc(p)} inning {inning}, n={len(values)}, mean={statistics.mean(values):.2f} mph</title></circle>')
                previous=(xx,yy)
            text(75,70+PITCHERS.index(p)*16,p)
        for i in range(1,8): text(75+i*85,395,i)
        for mph in (88,90,92,94,96): text(30,370-(mph-88)*30,mph)
        text(300,425,'Inning; FF only. Truncated mph axis, not zero. Hover for group counts.')
    elif name=='box':
        for i,k in enumerate(TYPES):
            values=sorted(r['speed_mph'] for r in rows if r['pitch_type']==k)
            if not values: continue
            q1,_,q3=statistics.quantiles(values,n=4,method='inclusive') if len(values)>1 else (values[0],)*3
            x=lambda v:75+(v-75)*28
            yy=120+i*85
            line(x(min(values)),yy,x(max(values)),yy)
            parts.append(f'<rect x="{x(q1)}" y="{yy-18}" width="{max(1,x(q3)-x(q1))}" height="36" fill="{colors[k]}" opacity=".5"/>')
            line(x(statistics.median(values)),yy-18,x(statistics.median(values)),yy+18)
            text(20,yy,f'{k} n={len(values)}')
        for mph in (75,80,85,90,95,100): text(75+(mph-75)*28,390,mph)
        text(100,425,'mph; inclusive quartiles, min/max whiskers. No Tukey outlier convention.')
    elif name=='heatmap':
        counts=Counter((min(2,max(0,int((r['plate_x_ft']+1.5)//1))),min(2,max(0,int((r['plate_z_ft']-.5)//1)))) for r in rows)
        maximum=max(counts.values(),default=1)
        for col in range(3):
            for band in range(3):
                count=counts[col,band]; xx,yy=220+col*100,300-band*85
                parts.append(f'<rect x="{xx}" y="{yy}" width="100" height="85" fill="#1768ac" opacity="{.15+.8*count/maximum:.2f}" stroke="white"/>')
                text(xx+30,yy+42,count)
        text(100,100,'x bins: [-1.5,-0.5), [-0.5,0.5), [0.5,1.5] ft; z: 0.5–3.5, tails clipped to edge bins')
        text(140,425,'Catcher perspective; low height at bottom. All observations included in edge bins.')
    else:
        if name=='histogram':
            bars=[(f'{a}–<{a+5}',sum(a<=r['speed_mph']<a+5 for r in rows)) for a in range(75,100,5)]
            unit='Pitch count; equal 5 mph bins'
        elif name=='pareto':
            bars=[]
            for k in TYPES:
                subset=[r for r in rows if r['pitch_type']==k]; swings=sum(r['swing'] for r in subset); misses=sum(r['whiff'] for r in subset)
                if swings: bars.append((f'{k} {misses}/{swings}',100*misses/swings))
            unit='Whiffs per 100 swings (%); not per pitch'
        else:
            counts=Counter(r['pitch_type'] for r in rows);bars=sorted(counts.items());unit='Pitch count; all selected periods combined'
        maximum=100 if name=='pareto' else max((v for _,v in bars),default=1) or 1
        for i,(label,value) in enumerate(bars):
            xx=100+i*130;hh=250*value/maximum
            parts.append(f'<rect x="{xx}" y="{360-hh}" width="85" height="{hh}" fill="#1768ac"/>');text(xx,385,label);text(xx,350-hh,f'{value:.1f}')
        text(45,360,'0');text(45,110,f'{maximum:g}');text(100,425,unit)
    parts.append('</g></svg>')
    return ''.join(parts)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['build','verify']);args=parser.parse_args()
    for relative,payload in artifacts().items():
        path=ROOT/relative
        if args.command=='build': path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
        elif not path.exists() or path.read_bytes()!=payload: raise SystemExit('Baseball artifact mismatch: '+relative)
    print('PASS: baseball v1 '+args.command+'; 3600 fictional pitches.')


if __name__=='__main__': main()

"""Standard-library CSV summaries and SVG Pareto plots; no plotting dependencies."""
import argparse,csv,json,statistics,html
from pathlib import Path
def hypervolume(points,reference):
    height=reference[1]; total=0.
    for x,y in sorted(set(map(tuple,points))):
        if x<reference[0] and y<height:
            total+=(reference[0]-x)*(height-y); height=y
    return total
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(); p.add_argument('--results',default=str(ROOT/'results')); a=p.parse_args()
root=Path(a.results); records=[json.loads(f.read_text()) for f in sorted(root.glob('*/*.json'))]
if not records: raise SystemExit('No result JSON files found')
if len({r['settings']['budget'] for r in records})>1: raise SystemExit('Mixed quick/full budgets: use a fresh output folder')
out=root/'summaries'; out.mkdir(exist_ok=True); rows=[]; refs=[]
colors={'vega':'#c0392b','nsga2':'#2471a3','spea2':'#229954'}
for instance in sorted({r['settings']['instance'] for r in records}):
    group=[r for r in records if r['settings']['instance']==instance]
    points=[s['objectives'] for r in group for s in r['front']]
    reference=tuple(max(v[k] for v in points)+max(1,.1*(max(v[k] for v in points)-min(v[k] for v in points))) for k in range(2))
    refs.append(dict(instance=instance,f1_reference=reference[0],f2_reference=reference[1]))
    for r in group:
        rows.append(dict(**{k:r['settings'][k] for k in ('algorithm','instance','config','seed','budget')},runtime_seconds=r['runtime_seconds'],nd_count=r['nd_count'],hv=hypervolume([s['objectives'] for s in r['front']],reference)))
    for config in sorted({r['settings']['config'] for r in group}):
        subset=[r for r in group if r['settings']['config']==config]
        pts=[s['objectives'] for r in subset for s in r['front']]
        lo=[min(v[k] for v in pts) for k in range(2)]; hi=[max(v[k] for v in pts) for k in range(2)]
        svg=['<svg xmlns="http://www.w3.org/2000/svg" width="850" height="550" viewBox="0 0 850 550">','<rect width="850" height="550" fill="white"/>',f'<text x="70" y="30" font-size="20">{instance} {config}: pooled run fronts</text>','<path d="M70 60 V470 H760" fill="none" stroke="black"/>','<text x="300" y="525">Opening cost f1 (lower is better)</text>','<text x="5" y="50">Allocation cost f2</text>']
        for t in range(6):
            x=70+t*138; y=470-t*82
            svg.extend([f'<text x="{x}" y="492" font-size="11">{lo[0]+t*(hi[0]-lo[0])/5:.0f}</text>',f'<text x="5" y="{y}" font-size="11">{lo[1]+t*(hi[1]-lo[1])/5:.0f}</text>'])
        for idx,algorithm in enumerate(colors):
            if not any(r['settings']['algorithm']==algorithm for r in subset): continue
            svg.append(f'<text x="{80+idx*180}" y="55" fill="{colors[algorithm]}">{algorithm}</text>')
            unique={tuple(s['objectives']) for r in subset if r['settings']['algorithm']==algorithm for s in r['front']}
            for x,y in unique:
                px=70+690*(x-lo[0])/max(1,hi[0]-lo[0]); py=470-410*(y-lo[1])/max(1,hi[1]-lo[1])
                svg.append(f'<circle cx="{px}" cy="{py}" r="4" fill="{colors[algorithm]}" fill-opacity=".55" stroke="{colors[algorithm]}"><title>{algorithm}: {x}, {y}</title></circle>')
        svg.append('</svg>'); (out/f'pareto_{instance}_{config}.svg').write_text('\n'.join(svg))
def write(name,data):
    with (out/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
write('all_runs.csv',rows); write('hypervolume_reference_points.csv',refs)
aggregate=[]
for key in sorted({(r['algorithm'],r['instance'],r['config']) for r in rows}):
    group=[r for r in rows if (r['algorithm'],r['instance'],r['config'])==key]
    result=dict(zip(('algorithm','instance','config'),key)); result['runs']=len(group)
    for metric in ('hv','nd_count','runtime_seconds'):
        values=[r[metric] for r in group]; result[metric+'_mean']=statistics.mean(values); result[metric+'_std']=statistics.stdev(values) if len(values)>1 else 0
    aggregate.append(result)
write('aggregate.csv',aggregate)
print(f'Summarized {len(rows)} runs in {out}. HV references are common per instance; do not average raw HV across instance scales.')

"""Publication-friendly PNG/JPG comparisons. Pillow only; no NumPy."""
import argparse,csv,json,math,statistics,html
from pathlib import Path
try:
 from PIL import Image,ImageDraw,ImageFont
except ImportError:
 raise SystemExit('Image plotting needs Pillow. Run: py -m pip install pillow')
ROOT=Path(__file__).resolve().parent
W,H=1600,1100
COLORS={'vega':'#D55E00','nsga2':'#0072B2','spea2':'#009E73'}
NAMES={'vega':'VEGA','nsga2':'NSGA-II','spea2':'SPEA2'}
ORDER=list(COLORS); INK='#172B4D'; MUTED='#526579'; GRID='#E3E9EF'
def font(size,bold=False):
 candidates=['arialbd.ttf' if bold else 'arial.ttf','DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
 for name in candidates:
  try: return ImageFont.truetype(name,size)
  except OSError: pass
 return ImageFont.load_default()
def canvas(title,subtitle):
 image=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(image)
 d.text((105,55),title,font=font(44,True),fill=INK)
 d.text((105,120),subtitle,font=font(24),fill=MUTED)
 return image,d
def text(d,xy,value,size=24,color=INK,anchor=None,bold=False):
 d.text(xy,str(value),font=font(size,bold),fill=color,anchor=anchor)
def nice_max(v):
 if v<=0:return 1
 power=10**math.floor(math.log10(v)); normalized=v/power
 return next((x*power for x in (1,2,2.5,5,10) if x>=normalized),10*power)
def number(v):
 if abs(v)>=1000:return f'{v:,.0f}'
 return f'{v:.2f}'.rstrip('0').rstrip('.')
def quantile(values,q):
 values=sorted(values); t=(len(values)-1)*q; low=int(t); high=min(low+1,len(values)-1)
 return values[low]+(values[high]-values[low])*(t-low)
def marker(d,x,y,algorithm,r=6):
 color=COLORS[algorithm]
 if algorithm=='vega': d.ellipse((x-r,y-r,x+r,y+r),fill=color,outline='white',width=1)
 elif algorithm=='nsga2':d.rectangle((x-r,y-r,x+r,y+r),fill=color,outline='white',width=1)
 else:d.polygon([(x,y-r-2),(x-r-2,y+r),(x+r+2,y+r)],fill=color)
def save(image,name,out):
 image.save(out/'png'/f'{name}.png',dpi=(300,300))
 image.save(out/'jpg'/f'{name}.jpg',quality=95,subsampling=0,dpi=(300,300))
def metric_chart(rows,metric,label,instance,config,out):
 group=[r for r in rows if r['instance']==instance and r['config']==config]
 algorithms=[a for a in ORDER if any(r['algorithm']==a for r in group)]
 factor=1e9 if metric=='hv' else 1
 values={a:[float(r[metric])/factor for r in group if r['algorithm']==a] for a in algorithms}
 means={a:statistics.mean(v) for a,v in values.items()}
 sds={a:statistics.stdev(v) if len(v)>1 else 0 for a,v in values.items()}
 upper=max(means[a]+sds[a] for a in algorithms)*1.25 or 1
 image,d=canvas(f'{label} | {instance} · {config}','Mean across independent runs; error bars show ±1 sample standard deviation')
 left,right,top,bottom=180,1490,245,840
 def Y(v):return bottom-(bottom-top)*v/upper
 axislabel=label+(' (billions of cost²)' if metric=='hv' else '')
 text(d,(left,190),axislabel,23,color=MUTED)
 for k in range(6):
  v=upper*k/5;y=Y(v);d.line((left,y,right,y),fill=GRID,width=2);text(d,(left-20,y),number(v),23,anchor='rm',color=MUTED)
 d.line((left,bottom,right,bottom),fill=MUTED,width=2)
 for k,a in enumerate(algorithms):
  x=left+(right-left)*(k+.5)/len(algorithms);mean=means[a];sd=sds[a]
  d.rectangle((x-105,Y(mean),x+105,bottom),fill=COLORS[a])
  low=max(0,mean-sd);high=mean+sd
  d.line((x,Y(low),x,Y(high)),fill=INK,width=4)
  for v in (low,high):d.line((x-25,Y(v),x+25,Y(v)),fill=INK,width=4)
  text(d,(x,Y(high)-22),number(mean),30,anchor='mb',bold=True)
  text(d,(x,bottom+30),NAMES[a],28,anchor='mt',bold=True)
  text(d,(x,bottom+77),f'n = {len(values[a])}   SD = {number(sd)}',22,anchor='mt',color=MUTED)
 note={'hv':'Higher is better. Shared reference per instance; compare HV within each instance.', 'runtime_seconds':'Lower is better. Runtime excludes saving and plotting; compare on the same computer.', 'nd_count':'More distinct trade-off solutions provide more choices; count alone does not establish quality.'}[metric]
 text(d,(105,980),note,22,color=MUTED)
 text(d,(105,1020),'SD describes run-to-run variability, not a confidence interval. Lower error bars are clipped at zero.',21,color=MUTED)
 save(image,f'{metric}_{instance}_{config}',out)
def pareto_chart(records,instance,config,out,only=None):
 group=[r for r in records if r['settings']['instance']==instance and r['settings']['config']==config ]
 points={a:sorted({tuple(s['objectives']) for r in group if r['settings']['algorithm']==a for s in r['front']}) for a in ORDER}
 allpoints=[p for values in points.values() for p in values]
 if not allpoints:return
 image,d=canvas(f'Pareto solutions | {instance} · {config}'+(f' · {NAMES[only]}' if only else ''),'Run-level non-dominated points pooled across runs; pooled points may dominate one another')
 left,right,top,bottom=185,1480,255,850
 mins=[min(p[k] for p in allpoints)/1000 for k in range(2)];maxs=[max(p[k] for p in allpoints)/1000 for k in range(2)]
 spans=[max(1,maxs[k]-mins[k]) for k in range(2)];lo=[mins[k]-.07*spans[k] for k in range(2)];hi=[maxs[k]+.07*spans[k] for k in range(2)]
 def X(v):return left+(v/1000-lo[0])/(hi[0]-lo[0])*(right-left)
 def Y(v):return bottom-(v/1000-lo[1])/(hi[1]-lo[1])*(bottom-top)
 text(d,(left,202),'Allocation cost f₂ (thousands)',23,color=MUTED)
 for j in range(6):
  x=left+(right-left)*j/5;y=bottom-(bottom-top)*j/5
  d.line((x,top,x,bottom),fill=GRID,width=2);d.line((left,y,right,y),fill=GRID,width=2)
  text(d,(x,bottom+20),number(lo[0]+(hi[0]-lo[0])*j/5),22,anchor='mt',color=MUTED)
  text(d,(left-18,y),number(lo[1]+(hi[1]-lo[1])*j/5),22,anchor='rm',color=MUTED)
 for a in ORDER:
  for x,y in (points[a] if only is None or a==only else []):marker(d,X(x),Y(y),a,7)
 text(d,((left+right)/2,925),'Facility opening cost f₁ (thousands)',26,anchor='mt')
 x=190
 for a in ORDER:
  if points[a] and (only is None or a==only):
   marker(d,x,990,a,9);text(d,(x+25,972),NAMES[a],24);x+=330
 text(d,(105,1040),'Lower-left is preferable. Overlapping points may hide markers; inspect individual algorithm plots.',21,color=MUTED)
 save(image,f'pareto_{instance}_{config}'+(f'_{only}' if only else ''),out)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--results',default=str(ROOT/'results'));args=parser.parse_args()
 root=Path(args.results); summary=root/'summaries'; source=summary/'all_runs.csv'
 if not source.exists():raise SystemExit(f'Missing {source}. Run py summarize_results.py in your project folder first.')
 with source.open(newline='') as f:rows=list(csv.DictReader(f))
 records=[json.loads(p.read_text()) for p in sorted(root.glob('*/*.json'))]
 out=summary/'comparison_plots'
 for fmt in ('png','jpg'):(out/fmt).mkdir(parents=True,exist_ok=True)
 for instance,config in sorted({(r['instance'],r['config']) for r in rows}):
  for metric,label in [('hv','Hypervolume'),('runtime_seconds','Runtime (seconds)'),('nd_count','Non-dominated count')]:metric_chart(rows,metric,label,instance,config,out)
  pareto_chart(records,instance,config,out)
  for algorithm in ORDER:pareto_chart(records,instance,config,out,algorithm)
 files=sorted((out/'png').glob('*.png'))
 page='<html><head><meta charset="utf-8"><title>Algorithm comparison plots</title></head><body style="font-family:Arial;max-width:1200px;margin:40px auto"><h1>Algorithm comparisons</h1><p>PNG images; Mean ± SD bars and pooled Pareto solutions.</p>'
 page+=''.join(f'<h2>{html.escape(p.stem)}</h2><a href="png/{p.name}"><img src="png/{p.name}" style="width:100%"></a>' for p in files)+'</body></html>'
 (out/'index.html').write_text(page)
 print(f'Created PNG/JPG charts in:\n{(out/"png").resolve()}\n{(out/"jpg").resolve()}\nNo algorithm rerun needed.')
if __name__=='__main__':main()

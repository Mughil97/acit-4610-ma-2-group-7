"""Record and plot one run's evolution. Pillow only; uses local standalone algorithms.
Run: py plot_evolution.py --algorithm all --instance cap121 --config C3 --seed 42
History runs are separate from benchmark timing and never overwrite benchmark results.
"""
import argparse, importlib, inspect, json, random, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent
COLORS = ['#0072B2', '#D55E00']
def font(n):
    for name in ['arial.ttf', 'DejaVuSans.ttf']:
        try: return ImageFont.truetype(name,n)
        except OSError: pass
    return ImageFont.load_default()
def label(d,xy,s,n=24,anchor=None,fill='#172B4D'):
    d.text(xy,s,font=font(n),fill=fill,anchor=anchor)
def vertical(im,xy,s):
    f=font(23); box=f.getbbox(s); layer=Image.new('RGBA',(box[2]+8,40));ImageDraw.Draw(layer).text((4,-box[1]),s,font=f,fill='#172B4D')
    layer=layer.rotate(90,expand=True); im.paste(layer,(xy[0],int(xy[1]-layer.height/2)),layer)
def capture(module,instance,config,seed,budget):
    p=module.load(ROOT/'data'/f'{instance}.txt');n,pc,pm,b=module.CONFIGS[config];budget=budget or b
    if budget<n: raise ValueError('Budget must cover the initial population')
    rng=random.Random(seed);pop=[module.decode(tuple(rng.randrange(2) for _ in p.capacity),p) for _ in range(n)]
    initial=[s.objectives for s in pop]; history=[]; final=[]
    lines,start=inspect.getsourcelines(module.run);source={start+i:l.strip() for i,l in enumerate(lines)}
    def trace(frame,event,arg):
        nonlocal final
        if frame.f_code is not module.run.__code__: return None
        if event=='line':
            line=source.get(frame.f_lineno,'')
            checkpoint=(line=='if evaluations>=budget: break') if module.__name__=='spea2' else (line=='while evaluations<budget:')
            if checkpoint:
                state=frame.f_locals.get('archive') if module.__name__=='spea2' else frame.f_locals.get('pop')
                ev=frame.f_locals['evaluations']
                if state and (not history or history[-1]['evaluations']!=ev):
                    final=[s.objectives for s in state]
                    history.append(dict(generation=len(history),evaluations=ev,best_f1=min(x[0] for x in final),best_f2=min(x[1] for x in final),distinct_f1=len({x[0] for x in final}),nd_count=len(module.nondominated(state))))
        return trace
    sys.settrace(trace)
    try: front,ev=module.run(pop,p,rng,pc,pm,budget)
    finally: sys.settrace(None)
    return dict(algorithm=module.__name__,instance=instance,config=config,seed=seed,budget=budget,initial=initial,final=final,front=[s.objectives for s in front],history=history,state='archive' if module.__name__=='spea2' else 'population')
def plot(record,out):
    im=Image.new('RGB',(2400,1050),'white');d=ImageDraw.Draw(im);h=record['history']
    label(d,(75,35),f"{record['algorithm'].upper()} | {record['instance']} · {record['config']} · seed {record['seed']}",36)
    label(d,(75,95),f"One recorded run; {record['state']} history; both objectives are minimized",24)
    titles=['Starting and final solutions','Best objective costs by generation','Trade-off variety by generation']
    for panel,title in enumerate(titles):
        left=panel*800+115;right=panel*800+750;top=230;bottom=780
        label(d,((left+right)/2,175),title,27,'mm')
        if panel==0:
            allpoints=record['initial']+record['final'];xs=[x[0]/1000 for x in allpoints];ys=[x[1]/1000 for x in allpoints]
            xmin=max(0,min(xs)-(max(xs)-min(xs))*.05);xmax=max(xs)*1.05 or 1;ymin=max(0,min(ys)*.95);ymax=max(ys)*1.05 or 1
        else:
            xmin=0;xmax=max(1,h[-1]['generation']);ymin=0
            if panel==1:
                base=[h[0]['best_f1'],h[0]['best_f2']];series=[[100*r[k]/base[i] if base[i] else 0 for r in h] for i,k in enumerate(['best_f1','best_f2'])];ymax=max(105,max(max(v) for v in series)*1.05)
            else:
                series=[[r[k] for r in h] for k in ['distinct_f1','nd_count']];ymax=max(1,max(max(v) for v in series)*1.15)
        def X(v):return left+(v-xmin)/(xmax-xmin or 1)*(right-left)
        def Y(v):return bottom-(v-ymin)/(ymax-ymin or 1)*(bottom-top)
        for j in range(5):
            xx=xmin+(xmax-xmin)*j/4;yy=ymin+(ymax-ymin)*j/4
            d.line((left,Y(yy),right,Y(yy)),fill='#E3E9EF',width=2)
            label(d,(left-12,Y(yy)),f'{yy:,.0f}',20,'rm');label(d,(X(xx),bottom+20),f'{xx:,.0f}',20,'mt')
        d.line((left,top,left,bottom,right,bottom),fill='#526579',width=2)
        if panel==0:
            for points,color,radius in [(record['initial'],'#C6CBD1',4),(record['final'],'#56A5D8',5),(record['front'],'#D55E00',7)]:
                for x,y in points:d.ellipse((X(x/1000)-radius,Y(y/1000)-radius,X(x/1000)+radius,Y(y/1000)+radius),fill=color)
            entries=[('Initial solutions','#C6CBD1'),('Final solutions','#56A5D8'),('Final non-dominated','#D55E00')]
            vertical(im,(panel*800+15,505),'f2: Allocation cost (thousands)');xlabel='f1: Facility opening cost (thousands)'
        else:
            for i,values in enumerate(series):
                pts=[(X(r['generation']),Y(v)) for r,v in zip(h,values)]
                if len(pts)>1:d.line(pts,fill=COLORS[i],width=3)
            entries=list(zip(['Best f1: opening','Best f2: allocation'] if panel==1 else ['Distinct opening costs','Non-dominated objective pairs'],COLORS))
            vertical(im,(panel*800+15,505),'% of initial minimum' if panel==1 else 'Count');xlabel='Generation'
        label(d,((left+right)/2,840),xlabel,23,'mm')
        for i,(name,color) in enumerate(entries):
            yy=890+i*36;d.line((left,yy,left+30,yy),fill=color,width=6);label(d,(left+42,yy),name,22,'lm')
    label(d,(75,1020),'Best f1 and best f2 can belong to different solutions. One seed illustrates behaviour; use all-run metrics for conclusions.',23)
    name=f"{record['algorithm']}_{record['instance']}_{record['config']}_seed{record['seed']}"
    for fmt in ['png','jpg']:
        folder=out/fmt;folder.mkdir(parents=True,exist_ok=True);im.save(folder/f'{name}.{fmt}',**({'quality':95} if fmt=='jpg' else {}))
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--algorithm',choices=['all','vega','nsga2','spea2'],default='all');ap.add_argument('--instance',default='cap121');ap.add_argument('--config',default='C3',choices=['C1','C2','C3']);ap.add_argument('--seed',type=int,default=42);ap.add_argument('--budget',type=int);ap.add_argument('--output',type=Path,default=ROOT/'results'/'evolution_plots');a=ap.parse_args()
    for algo in ['vega','nsga2','spea2'] if a.algorithm=='all' else [a.algorithm]:
        module=importlib.import_module(algo);r=capture(module,a.instance,a.config,a.seed,a.budget);a.output.mkdir(parents=True,exist_ok=True)
        (a.output/f'{algo}_{a.instance}_{a.config}_seed{a.seed}_history.json').write_text(json.dumps(r,indent=2));plot(r,a.output);print(f'Created {algo} evolution charts in {a.output.resolve()}',flush=True)
if __name__=='__main__': main()

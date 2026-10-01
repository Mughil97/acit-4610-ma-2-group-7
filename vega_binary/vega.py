"""Shared binary CFLP operators. Standard library only; tuples are immutable."""
from dataclasses import dataclass
from pathlib import Path
import random

CONFIGS = {'C1': (40,.8,.1,12000), 'C2': (60,.8,.1,12000), 'C3': (60,.8,.2,12000)}
INSTANCES = ('cap61','cap62','cap101','cap102','cap121','cap122')
SEEDS = range(42,52)
@dataclass(frozen=True)
class Problem:
    capacity: tuple
    fixed: tuple
    demand: tuple
    costs: tuple  # customer-major: costs[j][i]
@dataclass(frozen=True)
class Solution:
    bits: tuple
    assignment: tuple
    objectives: tuple

def load(path):
    values=iter(Path(path).read_text().split())
    m,n=int(next(values)),int(next(values))
    facilities=[(float(next(values)),float(next(values))) for _ in range(m)]
    demand=[]; costs=[]
    for _ in range(n):
        demand.append(float(next(values)))
        costs.append(tuple(float(next(values)) for _ in range(m)))
    if next(values,None) is not None: raise ValueError('Extra benchmark tokens')
    return Problem(tuple(x[0] for x in facilities),tuple(x[1] for x in facilities),tuple(demand),tuple(costs))

def decode(bits,p):
    if len(bits)!=len(p.capacity) or any(b not in (0,1) for b in bits): raise ValueError('Invalid bits')
    y=list(bits); remaining=list(p.capacity); assignment=[-1]*len(p.demand)
    for j in sorted(range(len(p.demand)),key=lambda j:(-p.demand[j],j)):
        choices=[i for i in range(len(y)) if y[i] and remaining[i]>=p.demand[j]]
        if not choices:
            choices=[i for i in range(len(y)) if not y[i] and remaining[i]>=p.demand[j]]
            if not choices: raise ValueError('Greedy decoder failed; no feasible facility. This does not prove global infeasibility.')
            i=min(choices,key=lambda i:(p.costs[j][i],p.fixed[i],i)); y[i]=1; choices=[i]
        i=min(choices,key=lambda i:(p.costs[j][i],i))
        assignment[j]=i; remaining[i]-=p.demand[j]
    return Solution(tuple(y),tuple(assignment),(sum(f*b for f,b in zip(p.fixed,y)),sum(p.costs[j][i] for j,i in enumerate(assignment))))

def feasible(s,p):
    loads=[0]*len(p.capacity)
    if len(s.assignment)!=len(p.demand): return False
    for j,i in enumerate(s.assignment):
        if not 0<=i<len(loads) or not s.bits[i]: return False
        loads[i]+=p.demand[j]
    return all(a<=b+1e-8 for a,b in zip(loads,p.capacity))

def dominates(a,b): return all(x<=y for x,y in zip(a,b)) and any(x<y for x,y in zip(a,b))
def fronts(pop):
    dominated=[[] for _ in pop]; counts=[0]*len(pop)
    for i in range(len(pop)):
        for j in range(i+1,len(pop)):
            a,b=pop[i].objectives,pop[j].objectives
            if dominates(a,b): dominated[i].append(j); counts[j]+=1
            elif dominates(b,a): dominated[j].append(i); counts[i]+=1
    current=[i for i,c in enumerate(counts) if c==0]; result=[]
    while current:
        result.append(current); following=[]
        for i in current:
            for j in dominated[i]:
                counts[j]-=1
                if counts[j]==0: following.append(j)
        current=following
    return result

def crowding(pop,front):
    distance={i:0. for i in front}
    for k in range(2):
        ordered=sorted(front,key=lambda i:pop[i].objectives[k])
        if not ordered: continue
        low,high=pop[ordered[0]].objectives[k],pop[ordered[-1]].objectives[k]
        if high==low: continue
        distance[ordered[0]]=distance[ordered[-1]]=float('inf')
        for t in range(1,len(ordered)-1):
            distance[ordered[t]]+=(pop[ordered[t+1]].objectives[k]-pop[ordered[t-1]].objectives[k])/(high-low)
    return distance

def nsga_survival(pop,n):
    selected=[]; ranks={}; distances={}
    for rank,front in enumerate(fronts(pop)):
        d=crowding(pop,front)
        ranks.update({i:rank for i in front}); distances.update(d)
        selected.extend(sorted(front,key=lambda i:-d[i])[:n-len(selected)])
        if len(selected)==n: break
    return [pop[i] for i in selected],[(ranks[i],-distances[i]) for i in selected]

def offspring(parents,p,rng,pc,pm,count):
    # Pair consecutive selected parents, matching the teacher's reproduction structure.
    children=[]
    for t in range(0,count,2):
        a,b=parents[t%len(parents)].bits,parents[(t+1)%len(parents)].bits
        x,y=list(a),list(b)
        if rng.random()<pc:
            for i in range(len(x)):
                if rng.random()<.5: x[i],y[i]=y[i],x[i]
        for child in (x,y):
            # pm is per chromosome: flip one bit on a mutation event.
            if rng.random()<pm:
                i=rng.randrange(len(child)); child[i]=1-child[i]
            children.append(decode(tuple(child),p))
    return children[:count]

def nondominated(pop):
    unique={s.objectives:s for s in pop}
    return [unique[f] for f in sorted(unique) if not any(dominates(g,f) for g in unique)]

def hypervolume(points,reference):
    # Exact 2D minimization HV; common reference is supplied by the summarizer.
    height=reference[1]; total=0.
    for x,y in sorted(set(map(tuple,points))):
        if x<reference[0] and y<height:
            total+=(reference[0]-x)*(height-y); height=y
    return total

"""VEGA: objective partitions, teacher-style roulette, non-elitist replacement."""

def run(pop,p,rng,pc,pm,budget):
    evaluations=len(pop)
    while evaluations<budget:
        rng.shuffle(pop); half=len(pop)//2; parents=[]
        for k,group in enumerate((pop[:half],pop[half:])):
            parents.extend(rng.choices(group,weights=[1/(1+s.objectives[k]) for s in group],k=len(group)))
        rng.shuffle(parents)
        count=min(len(pop),budget-evaluations)
        pop=offspring(parents,p,rng,pc,pm,count); evaluations+=count
    return nondominated(pop),evaluations

import argparse,importlib,json,time,random,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def execute(algorithm,instance,config,seed,output,budget=None,skip=False):
    path=ROOT/'data'/f'{instance}.txt'; p=load(path)
    n,pc,pm,default_budget=CONFIGS[config]; budget=budget or default_budget
    if budget<n: raise ValueError('Budget must cover initial population')
    destination=Path(output)/algorithm/f'{instance}_{config}_{seed}.json'
    settings=dict(algorithm=algorithm,instance=instance,config=config,seed=seed,population=n,pc=pc,pm=pm,budget=budget,version='python-binary-v1',data_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    if skip and destination.exists():
        existing=json.loads(destination.read_text())
        if existing['settings']!=settings: raise ValueError(f'Settings mismatch: {destination}')
        return
    rng=random.Random(seed); start=time.perf_counter()
    pop=[decode(tuple(rng.randrange(2) for _ in p.capacity),p) for _ in range(n)]
    front,evaluations=run(pop,p,rng,pc,pm,budget)
    elapsed=time.perf_counter()-start
    if evaluations!=budget or not all(feasible(s,p) for s in front): raise AssertionError('Invalid experiment')
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(dict(settings=settings,evaluations=evaluations,runtime_seconds=elapsed,nd_count=len(front),front=[dict(bits=s.bits,assignment=s.assignment,objectives=s.objectives) for s in front]),indent=2))
    print(f'{algorithm} {instance} {config} seed={seed}: evals={evaluations}, ND={len(front)}, {elapsed:.2f}s',flush=True)

def main(algorithm):
    parser=argparse.ArgumentParser()
    parser.add_argument('--instance',default='cap61'); parser.add_argument('--config',choices=CONFIGS,default='C1')
    parser.add_argument('--seed',type=int,default=42); parser.add_argument('--output',default=str(ROOT/'results'))
    parser.add_argument('--budget',type=int); parser.add_argument('--skip-existing',action='store_true')
    a=parser.parse_args(); execute(algorithm,a.instance,a.config,a.seed,a.output,a.budget,a.skip_existing)

if __name__=='__main__':
    main('vega')

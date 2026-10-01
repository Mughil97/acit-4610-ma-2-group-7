"""Standalone integer CFLP implementation. Standard library only."""
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

def decode(genes,p):
    """Keep feasible encoded assignments; repair largest-demand customers first.

    Each gene is a facility index for one customer. Closed facilities become
    open when assigned a customer; no customer demand is split or omitted.
    """
    if len(genes)!=len(p.demand) or any(type(i) is not int or not 0<=i<len(p.capacity) for i in genes):
        raise ValueError('Invalid integer chromosome')
    remaining=list(p.capacity); used=set(); assignment=[-1]*len(p.demand)
    for j in sorted(range(len(p.demand)),key=lambda j:(-p.demand[j],j)):
        preferred=genes[j]
        if remaining[preferred]>=p.demand[j]:
            chosen=preferred
        else:
            choices=[i for i in sorted(used) if remaining[i]>=p.demand[j]]
            if not choices:
                choices=[i for i in range(len(remaining)) if remaining[i]>=p.demand[j]]
            if not choices:
                raise ValueError('Greedy integer repair failed; global infeasibility is not established')
            chosen=min(choices,key=lambda i:(p.costs[j][i],p.fixed[i],i))
        assignment[j]=chosen; used.add(chosen); remaining[chosen]-=p.demand[j]
    return Solution(tuple(assignment),(sum(p.fixed[i] for i in sorted(used)),sum(p.costs[j][i] for j,i in enumerate(assignment))))

def random_solution(p,rng):
    # Choose a random active subset before assigning customers and repairing.
    k=rng.randrange(1,len(p.capacity)+1)
    active=rng.sample(range(len(p.capacity)),k)
    return decode(tuple(rng.choice(active) for _ in p.demand),p)

def feasible(s,p):
    loads=[0]*len(p.capacity)
    if len(s.assignment)!=len(p.demand): return False
    for j,i in enumerate(s.assignment):
        if not 0<=i<len(loads): return False
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
    """Uniform crossover and single-customer random-reset mutation.

    Parents are sampled from the selected mating pool with replacement,
    matching the previous integer implementation's reproduction structure.
    """
    children=[]
    while len(children)<count:
        a,b=rng.choice(parents).assignment,rng.choice(parents).assignment
        x,y=list(a),list(b)
        if rng.random()<pc:
            for i in range(len(x)):
                if rng.random()<.5: x[i],y[i]=y[i],x[i]
        for child in (x,y):
            if rng.random()<pm and len(p.capacity)>1:
                j=rng.randrange(len(child)); old=child[j]
                new=rng.randrange(len(p.capacity)-1)
                child[j]=new+(new>=old)
            children.append(decode(tuple(child),p))
            if len(children)==count: break
    return children

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

"""SPEA2: strength fitness, normalized density and lexicographic truncation.
Distances use raw objective units. Archive size equals population size.
"""
import math

def environmental(pop,n):
    size=len(pop); strengths=[0]*size; dominators=[[] for _ in pop]
    for i in range(size):
        for j in range(i+1,size):
            if dominates(pop[i].objectives,pop[j].objectives): strengths[i]+=1; dominators[j].append(i)
            elif dominates(pop[j].objectives,pop[i].objectives): strengths[j]+=1; dominators[i].append(j)
    raw=[sum(strengths[j] for j in d) for d in dominators]
    lows=[min(s.objectives[k] for s in pop) for k in range(2)]
    spans=[max(s.objectives[k] for s in pop)-lows[k] or 1. for k in range(2)]
    normalized=[tuple((s.objectives[k]-lows[k])/spans[k] for k in range(2)) for s in pop]
    distances=[[math.dist(a,b) for b in normalized] for a in normalized]
    k=min(max(1,int(math.sqrt(size))),size-1)
    fitness=[raw[i]+1/(sorted(distances[i][j] for j in range(size) if j!=i)[k-1]+2) if size>1 else raw[i]+.5 for i in range(size)]
    selected=[i for i in range(size) if raw[i]==0]
    if len(selected)<n:
        selected.extend(sorted((i for i in range(size) if i not in selected),key=lambda i:(fitness[i],i))[:n-len(selected)])
    truncated=len(selected)>n
    while len(selected)>n:
        lows=[min(pop[i].objectives[k] for i in selected) for k in range(2)]
        spans=[max(pop[i].objectives[k] for i in selected)-lows[k] or 1. for k in range(2)]
        for i in selected:
            for j in selected:
                distances[i][j]=math.dist(tuple((pop[i].objectives[k]-lows[k])/spans[k] for k in range(2)),tuple((pop[j].objectives[k]-lows[k])/spans[k] for k in range(2)))
        remove=min(selected,key=lambda i:(sorted(distances[i][j] for j in selected if j!=i),i))
        selected.remove(remove)
    # Recompute archive fitness after truncation, as in the previous integer version.
    archive=[pop[i] for i in selected]
    if truncated:
        # Re-evaluate fitness on the selected archive, without further truncation.
        return environmental(archive,n)
    return archive,[fitness[i] for i in selected]

def run(pop,p,rng,pc,pm,budget):
    n=len(pop); evaluations=n; archive=[]
    while True:
        archive,fitness=environmental(pop+archive,n)
        if evaluations>=budget: break
        parents=[]
        for _ in range(n):
            i,j=rng.randrange(len(archive)),rng.randrange(len(archive))
            parents.append(archive[i if fitness[i]<fitness[j] else j if fitness[j]<fitness[i] else rng.choice((i,j))])
        count=min(n,budget-evaluations)
        pop=offspring(parents,p,rng,pc,pm,count); evaluations+=count
    return nondominated(archive),evaluations

import argparse,importlib,json,time,random,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def execute(algorithm,instance,config,seed,output,budget=None,skip=False):
    path=ROOT/'data'/f'{instance}.txt'; p=load(path)
    n,pc,pm,default_budget=CONFIGS[config]; budget=default_budget if budget is None else budget
    if budget<n: raise ValueError('Budget must cover initial population')
    destination=Path(output)/algorithm/f'{instance}_{config}_{seed}.json'
    settings=dict(algorithm=algorithm,instance=instance,config=config,seed=seed,population=n,pc=pc,pm=pm,budget=budget,version='python-integer-stdlib-v1',representation='integer',data_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    if skip and destination.exists():
        existing=json.loads(destination.read_text())
        if existing['settings']!=settings: raise ValueError(f'Settings mismatch: {destination}')
        return
    rng=random.Random(seed); start=time.perf_counter()
    pop=[random_solution(p,rng) for _ in range(n)]
    front,evaluations=run(pop,p,rng,pc,pm,budget)
    elapsed=time.perf_counter()-start
    if evaluations!=budget or not all(feasible(s,p) for s in front): raise AssertionError('Invalid experiment')
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(dict(settings=settings,evaluations=evaluations,runtime_seconds=elapsed,nd_count=len(front),front=[dict(assignment=s.assignment,objectives=s.objectives) for s in front]),indent=2))
    print(f'{algorithm} {instance} {config} seed={seed}: evals={evaluations}, ND={len(front)}, {elapsed:.2f}s',flush=True)

def main(algorithm):
    parser=argparse.ArgumentParser()
    parser.add_argument('--instance',default='cap61'); parser.add_argument('--config',choices=CONFIGS,default='C1')
    parser.add_argument('--seed',type=int,default=42); parser.add_argument('--output',default=str(ROOT/'results'))
    parser.add_argument('--budget',type=int); parser.add_argument('--skip-existing',action='store_true')
    a=parser.parse_args(); execute(algorithm,a.instance,a.config,a.seed,a.output,a.budget,a.skip_existing)

if __name__=='__main__':
    main('spea2')

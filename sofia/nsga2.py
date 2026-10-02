#non-dominated sorting
"""
1. initialization: each solution has an intitial rank
2. domination: determine how many + which solutions dominate it 
3. front assignemtn: first front contains the non-dominated slutsion
4. repeat by first removing the already assinged solutsion
"""

#crodwing distance: maintain diversity within a Pareto front
"""
1. initilizatinon: crowding dist = 0
2. sorting: sort based on their objective values
3. boundary assigment: boundary solution has infitite crowding
4. distance calc: calc crowding distance based on normalized diff in obj values 
    of neighbouring solutions
"""

#non-dominated sorting algo
"""
A solution's dominance count: nr of solutions that dominate it 
1. cerate empty list for each pareto front
2. count nr of solutiions that dominates it + make a list of the ones it dominates
3. first fron, rank 1: solutions that no other solutions dominates (they are non-dominated)
4. reduce domincance count of the solution it dominates, if a solution's domincance count
becomes 0: adding it to the next front 
5. repeat until all solutsion are assinged to a front
"""

#intialize
"""
FORMAT OF FILES
first line: facilites, customers
opening cost, capcaity 
demand line
cost lines 
"""

"binary rep: need a decoder that assings customers to the open facilities"
"opening cost: sum of fixed costs where gene= 1"
"allocaiton cost: cost from the decoder's assignment"


import random 
import math
import time
import pickle
paths = [#fixed order: 16, 25, 50
    "acit-4610-ma-2-group-7/sofia/data/cap61.txt","acit-4610-ma-2-group-7/sofia/data/cap62.txt",
    "acit-4610-ma-2-group-7/sofia/data/cap101.txt", "acit-4610-ma-2-group-7/sofia/data/cap102.txt",
    "acit-4610-ma-2-group-7/sofia/data/cap121.txt","acit-4610-ma-2-group-7/sofia/data/cap122.txt" ]


PARAMETER_SETS = {
    "P1": { 
        "pop_size": 50,
        "max_evals":10000,
        "crossover_prob": 0.8,
        "mutation_mult":  1, #1/m to keep the distrubtion the same on 16,25,50 facitlites 
        #prob of flipping a bit with (1/nr of facilities) x 100 %
    },

    "P2":{ 
        "pop_size": 100,
        "max_evals": 30000,
        "crossover_prob": 0.9,
        "mutation_mult": 1,

    },
    "P3":{ 
        "pop_size": 200,
        "max_evals":100000,
        "crossover_prob": 0.95,
        "mutation_mult":2,
    },
}

SEEDS = range(10) 


def read_instance(path):
    capacity = {} #k = facility nr starting form 0-15, v = capacity
    fixed_cost = 0
    facility_cost = []

    #facility i = capacity[i] = customers[c][i] (value is a list in customers, and in the list the indexes are the facility / allocation cost )

    customers_allocation = {} #k = nr of customer (from 0), v = list of cust. allocaiton cost 
    demand = {} #key = customer-nr (from o), values are the demand

    f = open(path, "r")
    nr_facilities, nr_customers = map(int, f.readline().split()) #mapper alle verdiene i lsiten til int

    for facility in range(nr_facilities): #reading the capacity for each facility
        capacity[facility],fixed_cost = map(float, f.readline().split())
        #storing hte capcaticy of each facility and the k=facility-nr starting frm 0 bc of our chromosome rep
        
        facility_cost.append(fixed_cost) #cost of opening

    for cust in range(nr_customers):
        demand[cust] = (float(f.readline())) #first element = first customer where value is its demand

        costs = []
        while len(costs) < nr_facilities: #stops when all allocation costs are counted
            costs += [float(c) for c in f.readline().split()]

        customers_allocation[cust] = [c for c in costs] #each customer has a list fo the allocation costs, 
        #...first element is the allcoaiton cost for the first facitlity

    f.close()

    return fixed_cost, facility_cost, capacity, customers_allocation, demand


#INITIALIZE
def init_pop(pop_size, nr_facilities):
    pop = []

    for i in range(pop_size):
        chromosome = []
        for f in range(nr_facilities):
            if random.random() < 0.5: #didnt decide to increase the chance to open if low opening cost bc i wanted diversity in initial
                chromosome.append(0)
            else:
                chromosome.append(1)
        pop.append(chromosome)
    
    return pop

def open_one(chromosome, facility_cost): 
    #facility_cost is a list of opening costs , index = facilitynumber 0-based

    #prefers cost 0 or else random
    closed = [i for i in range(len(chromosome)) if chromosome[i]==0]

    if not closed: #if all are open. Not closed = True if list is empty
        return None

    free_to_open = [i for i in closed if facility_cost[i] == 0]
    idx = random.choice(free_to_open or closed) #if free_to_open is not empty it uses that, otherwise chooses from closed
    chromosome[idx] = 1
    return idx #the one opened

def repair(chromosome, capacity, demand, facility_cost):
    total_demand = sum(demand.values()) #index refers to customers, values of their respective demands

    if not any(chromosome): #if all 0: closed -> false 
        open_one(chromosome, facility_cost)

    total_cap = sum(capacity[i] for i in range(len(chromosome)) if chromosome[i]==1) #sum of total capcity of open facilities
    while total_cap < total_demand:
        idx = open_one(chromosome, facility_cost)
        if idx is None:
            break
        total_cap += capacity[idx]
    return chromosome
    



#FAULTY REPAIRS
"""
#REPAIR- makes sure that atleast one facility is open and that the total capacity >= total demand
def repair(chromosome, capacity, demand, facility_cost): #return chromosome, total_opening_cost
    #fixed chromosome w enough capacity
    
    total_demand = sum(demand.values()) #index refers to customers, values of their respective demands


    #if no facility is open:
    if (not any(x == 1 for x in chromosome)): #True or false
        
        index = 0
        for cost in facility_cost:
            if cost == 0: #opening the facility w 0 opening cost
                break
            index+=1
        
        chromosome[index] = 1
        #chromosome[random.randint(0,len(capacity))] = 1 #opening a random facility
    

    #if total capacity is less than total demand
    index = 0
    open_total_capacity = 0

    for i in range(len(chromosome)):
        if chromosome[i] == 1: #find capcaity for the open facility
            open_total_capacity += capacity[i]

 
    while open_total_capacity < total_demand: #until total capacity is => total demand
        closed = [index for index in range(len(chromosome)) if chromosome[index]==0 ]
        #list of all indexes that have closed facility

        open_f = False #in case none have 0 opening cost
        for index in closed:
            if facility_cost[index] == 0:
                chromosome[index] = 1 #open the facility
                open_total_capacity += capacity[index]
                open_f = True
                break

        if not open_f:
            #pick random to open 
            index_to_open = random.choice(closed) #picks any ranodm element (elements are indexes of closed facilities)
            chromosome[index_to_open] =1 

        open_total_capacity += capacity[index_to_open]

    return chromosome
"""

#ASSIGNING AFTER REPAIR 
def decode(chromosome, capacity, customers_allo, demand): #assign customer to facility while trying to keep acclocation cost low
    #dicitonary: customer-nr points to the facility number 
    violation = 0
    assignment = {} #k = cust_nr, v = facility

    open_f = [index for index in range(len(chromosome)) if chromosome[index] == 1 ]
    #holds the indexes for every open facility in the chromosome

    #track the demand of each open facility:
    load_facility = {index: 0 for index in open_f}

    #sort customers based on largest demand first
    sort_demand = dict(sorted(demand.items(), key = lambda item: item[1], reverse=True))
    
    #we place the ones with largest demand first as they are harder to fit; place while there is still room

    for cust_nr in sort_demand: #order is customer number (0-based)

        candidates = [] #list of facilities that can take the customer
        for facility in open_f: 
            if load_facility[facility] + demand[cust_nr] <= capacity[facility]:
                candidates.append(facility) #index

        #no facility found:
        if len(candidates) == 0:
            assignment[cust_nr] = None
            violation += demand[cust_nr]

        #choosing lowest allocation cost
        else:
            best = None #faciltiy to assign cust to

            best_cost = float("inf") #infinity
            for f in candidates:
                if customers_allo[cust_nr][f] < best_cost: #trying to find the cheapest allogcaiton cost
                    best_cost = customers_allo[cust_nr][f]
                    best = f

            assignment[cust_nr] = best
            load_facility[best] += demand[cust_nr] 

    return assignment, violation



#EVALUATE THE FITNESS
#CLAUDE 
def evaluate(chromosome, facility_cost, capacity, customers_allo, demand):
#if violation > 0 -> repeairs 
    repair(chromosome, capacity, demand, facility_cost)
    assignment, violation = decode(chromosome, capacity, customers_allo, demand)

    while violation > 0:
        if open_one(chromosome, facility_cost) is None:
            break

        assignment, violation = decode(chromosome, capacity, customers_allo, demand)

    opening_sum = sum(facility_cost[i] for i in range(len(chromosome)) if chromosome[i] == 1)
    alloc_sum = sum(customers_allo[c][f] for c, f in assignment.items() if f is not None)

    return (opening_sum, alloc_sum), violation





#FROM LAB:
def dominates(a, b, va, vb): #a,b lists of obj values for each solution, va and vb are constraint violation
    """No worse in every objective and strictly better in at least one."""
    if va == 0 and vb > 0: return True #A dominates
    if va > 0 and vb == 0: return False #B dominates
    if va > 0 and vb > 0: return va < vb 

    return all(x <= y for x, y in zip(a, b)) and any(
        x < y for x, y in zip(a, b)) #Pareto dominance 
#all: true or false basically and choses false if atleast one false 
"a is never worse than B"
#any: picks true if at elast one true 
"a is better than B at least once"

#True: A dominates B
#False: A does not dominate B (can mean that B domiantes, they are identical or neitehr dominates the other)

#LAB
def nondominated_sort(objectives, violations):
    """Starting at rank 1."""
    size = len(objectives)
    dominated = [[] for _ in range(size)]
    domination_count = [0] * size
    ranks = [0] * size

    for i in range(size):
        for j in range(i + 1, size):
            if dominates(objectives[i], objectives[j], violations[i],violations[j]):
                dominated[i].append(j)
                domination_count[j] += 1
            elif dominates(objectives[j], objectives[i], violations[j], violations[i]):
                dominated[j].append(i)
                domination_count[i] += 1

    front = [i for i in range(size) if domination_count[i] == 0]
    fronts = []
    rank = 1
    while front:
        fronts.append(front)
        next_front = []
        for i in front:
            ranks[i] = rank
            for j in dominated[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        front = next_front
        rank += 1
    return fronts, ranks

            

#LAB
def crowding_distances(objectives, fronts):
    distances = [0.0] * len(objectives)
    for front in fronts:
        if len(front) <= 2:
            for i in front:
                distances[i] = math.inf
            continue

        for k in range(2):
            ordered = sorted(front, key=lambda i: objectives[i][k])
            span = objectives[ordered[-1]][k] - objectives[ordered[0]][k]
            if span == 0:
                continue
            distances[ordered[0]] = math.inf
            distances[ordered[-1]] = math.inf
            for position in range(1, len(ordered) - 1):
                previous_value = objectives[ordered[position - 1]][k]
                next_value = objectives[ordered[position + 1]][k]
                distances[ordered[position]] += (next_value - previous_value) / span
    return distances


#LAB
def nsga2_selection(population, ranks, distances):
    """Binary tournaments: lower rank wins, then larger crowding distance."""
    mating_pool = []
    for _ in range(len(population)):
        i = random.randrange(len(population))
        j = random.randrange(len(population))
        key_i = (ranks[i], -distances[i])
        key_j = (ranks[j], -distances[j])
        if key_i < key_j:
            winner = i
        elif key_j < key_i:
            winner = j
        else:
            winner = random.choice([i, j])
        mating_pool.append(population[winner].copy())
    random.shuffle(mating_pool)
    return mating_pool


#LAB
def environmental_selection(population, objectives, violations, size):
    """Keep whole fronts; split the last front by decreasing crowding distance."""
    fronts, ranks = nondominated_sort(objectives, violations)
    distances = crowding_distances(objectives, fronts)
    selected = []
    for front in fronts:
        remaining = size - len(selected)
        if remaining == 0:
            break
        if len(front) <= remaining:
            selected.extend(front)
        else:
            ordered = sorted(front, key=lambda i: distances[i], reverse=True)
            selected.extend(ordered[:remaining])
            break

    # Retain combined-front ranks/distances for the next mating tournaments.
    return ([population[i].copy() for i in selected],
            [objectives[i] for i in selected],
            [violations[i] for i in selected],
            [ranks[i] for i in selected],
            [distances[i] for i in selected],)



#crossover
def crossover(p1,p2,crossover_prob):
    c1 = []
    c2 = []
    #uniform crossover
    if random.random() < crossover_prob:
        for a, b in zip(p1,p2):
            if random.random() < 0.5:
                c1.append(a)
                c2.append(b)
            else:
                c1.append(b)
                c2.append(a)

        return c1,c2
    return p1.copy(), p2.copy()#if crossover doesnt happen, children are parent's clones

#mutation
def mutate(chromosome, mut_prob): #bit flip
    return [1 - b if random.random() < mut_prob else b for b in chromosome]


def reproduce(pool, crossover_prob, mut_prob):
    offspring=[]
    for i in range(0, len(pool)-1,2): #goes by two each time - as in jumps index by 2 bc of the code after
        #len(pool)-1 because we need i and i+1 so we dont jump over the last element (index out of bounds)
        c1,c2 = crossover(pool[i],pool[i+1],crossover_prob)
        offspring.append(mutate(c1, mut_prob))
        offspring.append(mutate(c2, mut_prob))
    return offspring

#BOUNDS: best and words values each objective can take 
#ideal point:  bes value of each objective on its own - usually unreachable bc best for obj,1 is typically bad for obj2 - lower bound
#nadir: words value of each objective: upper bound

#every solutions objectives fall btw ideal and nadir
#CLAUDE 
def compute_bounds(facility_cost, capacity, customers_allo, demand):
    total_demand, covered_demand, k_min = sum(demand.values()), 0, 0

    for cap in sorted(capacity.values(), reverse=True):
        covered_demand += cap
        k_min += 1
        if covered_demand >= total_demand:
            break

    # ideal
    ideal_open_cost = sum(sorted(facility_cost)[:k_min])
    ideal_dist = sum(min(d) for d in customers_allo.values())
    ideal = (ideal_open_cost, ideal_dist)

    # nadir: open cost with everything open, allocation cost with only k_min
    # large facilities open (the cheapest-opening, most expensive-allocation end of the front)
    chrom = [0] * len(capacity)
    for i in sorted(capacity, key=capacity.get, reverse=True)[:k_min]:
        chrom[i] = 1
    (_, worst_alloc), _ = evaluate(chrom, facility_cost, capacity, customers_allo, demand)
    nadir = (sum(facility_cost), worst_alloc)

    return ideal, nadir

"""
def compute_bounds(facility_cost, capacity, customers_allo, demand):
    total_demand, covered_demand, k_min = sum(demand.values()), 0,0
    #k_min = fewest facilites that could possible serve everyone

    for cap in sorted(capacity.values(), reverse=True): #takes biggest capacity first and addsthem utnil they cover total demand
        covered_demand += cap
        k_min +=1
        if covered_demand >= total_demand:
            break

    #ideal
    cheapest = sorted(facility_cost)[:k_min] #sorts openings costs from smallest to largest, keeping k_min first (cheapest)
    ideal_open_cost = sum(cheapest)

    ideal_dist = 0
    for dist in customers_allo.values(): #dist are the lists of allocation cost to different facilities for each customer
        ideal_dist+=min(dist)

    ideal = (ideal_open_cost, ideal_dist)

    #nadir
    nadir_open_cost = sum(facility_cost)#open all

    nadir_dist=0
    for dist in customers_allo.values(): #dist are the lists of allocation cost to different facilities for each customer
        nadir_dist+=max(dist)
    
    nadir = (nadir_open_cost, nadir_dist)

    return ideal, nadir #tuples
"""

#bigger nr better, the set of solutions are closer to the ideal and/or more spread out 
"2 obj: we haev an area of the objc space that the solutions dominate"
"""
1. normalize: scale
2. filter: drop points falling otuside of the reference point
3. sweep: sort points by obj1 and add up rectangles to get the area
"""
#CLAUDE 
def hypervolume(points, bounds, ref=(1.1,1.1)): #ref is slightly worse than nadir 
    #so solution sitting right at nadir still contributes a small area instead of exactly 0
    ideal, nadir = bounds

    #normalize every point to roughly the 0-1 range
    range1 = nadir[0] - ideal[0]
    range2 = nadir[1] - ideal[1]

    normalized = []

    for f1, f2 in points:
        if range1 != 0:
            n1 = (f1-ideal[0])/range1
        else: 
            n1 = 0.0

        if range2 != 0:
            n2 = (f2 - ideal[1]) / range2
        else:
            n2 = 0.0

        #filter: keep points better than reference point
        if n1 < ref[0] and n2 < ref[1]:
            normalized.append((n1, n2))

    normalized.sort()

    #3: sweep left ot right, adding rectangles:
    hv = 0.0
    best_f2 = ref[1]

    for n1, n2 in normalized:
        if n2 < best_f2:
            width = ref[0] - n1
            height = best_f2 - n2
            hv += width * height
            best_f2 = n2
    return hv







#CLAUDE
def run_nsga2(inst, bounds, params, seed):
    t0 = time.time()
    random.seed(seed)
    _, facility_cost, capacity, customers, demand = inst
    nr_f, pop_size = len(capacity), params["pop_size"]
    mut_prob = params["mutation_mult"] / nr_f

    pop = init_pop(pop_size, nr_f)
    objectives, viol = [], []
    for ch in pop:
        f, v = evaluate(ch, facility_cost, capacity, customers, demand)
        objectives.append(f); viol.append(v)
    evals = pop_size
    fronts, ranks = nondominated_sort(objectives, viol)
    distances = crowding_distances(objectives, fronts)

    def front_now():
        return [objectives[i] for i in range(len(pop)) if ranks[i] == 1 and viol[i] == 0]

    history = [(evals, hypervolume(front_now(), bounds))]
    while evals + pop_size <= params["max_evals"]:
        pool = nsga2_selection(pop, ranks, distances)
        children = reproduce(pool, params["crossover_prob"], mut_prob)
        c_obj, c_viol = [], []
        for ch in children:
            f, v = evaluate(ch, facility_cost, capacity, customers, demand)
            c_obj.append(f); c_viol.append(v)
        evals += len(children)
        pop, objectives, viol, ranks, distances = environmental_selection(
            pop + children, objectives + c_obj, viol + c_viol, pop_size)
        history.append((evals, hypervolume(front_now(), bounds)))

    final = sorted(set(front_now()))          # distinct non-dominated feasible points
    return final, history, time.time() - t0




#CLAUDE 
import os
import statistics
import matplotlib.pyplot as plt


def run_experiment(paths, parameter_sets, seeds):
    results = []
    for path in paths:
        inst = read_instance(path)
        bounds = compute_bounds(*inst[1:])   # facility_cost, capacity, customers, demand
        for set_name, params in parameter_sets.items():
            for seed in seeds:
                front, history, t = run_nsga2(inst, bounds, params, seed)
                results.append({"file": path, "set": set_name, "seed": seed,
                                "hv": history[-1][1], "n_nd": len(front),
                                "time": t, "front": front, "history": history})
                print(os.path.basename(path), set_name, seed,
                      "HV", round(history[-1][1], 4), "|", round(t, 1), "s")
        with open("results.pkl", "wb") as f:      # save after each file
            pickle.dump(results, f)
    return results


def summarize(results, paths, parameter_sets):
    print(f"\n{'file':<12}{'set':<5}{'HV mean':>9}{'HV std':>9}{'#ND':>7}{'time(s)':>9}")
    for path in paths:
        for set_name in parameter_sets:
            runs = [r for r in results if r["file"] == path and r["set"] == set_name]
            hvs = [r["hv"] for r in runs]
            print(f"{os.path.basename(path):<12}{set_name:<5}"
                  f"{statistics.mean(hvs):9.4f}{statistics.pstdev(hvs):9.4f}"
                  f"{statistics.mean(r['n_nd'] for r in runs):7.1f}"
                  f"{statistics.mean(r['time'] for r in runs):9.1f}")


def plot_fronts(results, paths, parameter_sets):
    for path in paths:
        plt.figure(figsize=(7, 5))
        for set_name in parameter_sets:
            runs = [r for r in results if r["file"] == path and r["set"] == set_name]
            runs.sort(key=lambda r: r["hv"])
            median_run = runs[len(runs) // 2]            # the median-HV run
            f1 = [p[0] for p in median_run["front"]]
            f2 = [p[1] for p in median_run["front"]]
            plt.plot(f1, f2, alpha=0.4)
            plt.scatter(f1, f2, label=set_name)
        plt.xlabel("f1: opening cost")
        plt.ylabel("f2: allocation cost")
        plt.title(f"Final Pareto front, {os.path.basename(path)}")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.savefig(os.path.basename(path).replace(".txt", "_front.png"), dpi=150)
    plt.show()


if __name__ == "__main__":
    results = run_experiment(paths, PARAMETER_SETS, SEEDS)

    # print the seed-0 front for every file and parameter set
    for r in results:
        if r["seed"] == 0:
            print(os.path.basename(r["file"]), r["set"], r["front"])

    # diagnostic: are the HV values and fronts really identical?
    for path in paths:
        for set_name in PARAMETER_SETS:
            runs = [r for r in results if r["file"] == path and r["set"] == set_name]
            print(os.path.basename(path), set_name,
                  "HV values:", sorted(set(round(r["hv"], 6) for r in runs)),
                  "| fronts:", len(set(tuple(r["front"]) for r in runs)), "distinct")

    # HV history of the first run (every 10th generation)
    r = results[0]
    print(r["front"])
    print([round(h[1], 4) for h in r["history"][::10]])

    summarize(results, paths, PARAMETER_SETS)
    plot_fronts(results, paths, PARAMETER_SETS)




    







        
            
    





    









    
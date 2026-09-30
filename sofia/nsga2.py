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
paths = [#fixed order: 16, 25, 50
    "sofia/data/cap61.txt","sofia/data/cap62.txt",
    "sofia/data/cap101.txt", "sofia/data/cap122.txt" ]


PARAMETER_SETS = {
    "P1": { 
        "pop_size": 50,
        "generations":200,
        "crossover_prob": 0.8,
        "mutation_mult":  1, #1/m to keep the distrubtion the same on 16,25,50 facitlites 
        #prob of flipping a bit with (1/nr of facilities) x 100 %
    },

    "P2":{ 
        "pop_size": 100,
        "generations": 300,
        "crossover_prob": 0.9,
        "mutation_mult": 1,

    },
    "P3":{ 
        "pop_size": 200,
        "generations":500,
        "crossover_prob": 0.95,
        "mutation_mult":2,
    },
}

SEEDS = range(10) 


def read_instance(path):
    capacity = {} #k = facility nr starting form 0-15, v = capacity
    fixed_cost = 0
    facility_cost = []

    customers = {} #k = nr of customer, v = list of cust. allocaiton cost 
    demand = [] #index = customer-nr, values are the demand

    f = open(path, "r")
    nr_facilities, nr_customers = map(int, f.readline().split()) #mapper alle verdiene i lsiten til int

    for facility in range(nr_facilities): #reading the capacity for each facility
        capacity[facility],fixed_cost = map(float, f.readline().split())
        #storing hte capcaticy of each facility and the k=facility-nr starting frm 0 bc of our chromosome rep
        facility_cost.append(fixed_cost)

    for cust in range(nr_customers):
        demand.append(float(f.readline())) #first element = first customer where value is its demand

        costs = []
        while len(costs) < nr_facilities: #stops when all allocation costs are counted
            costs += [float(c) for c in f.readline().split()]

        customers[cust+1] = [c for c in costs] #each customer has a list fo the allocation costs, 
        #...first element is the allcoaiton cost for the first facitlity

    f.close()

    return fixed_cost, capacity, customers, demand


#INITIALIZE
def init_pop(pop_size, nr_facilities, range):
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


#REPAIR- makes sure that atleast one facility is open and that the total capacity >= total demand
def repair(chromosome, capacity, demand, facility_cost, range): #return chromosome, total_opening_cost
    #fixed chromosome w enough capacity
    
    
    total_demand = sum(demand) #index refers to customers, values of their respective demands


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
        if chromosome[i] == 1: #find capcaity for htat facility
            open_total_capacity += capacity[i]

 
    while open_total_capacity < total_demand: #until total capcoty is => total demand
        closed = [index for index in range(len(chromosome)) if chromosome[index]==0 ]
        #list of all indexes that have closed facility

        open = False #in case none have 0 opening cost
        for index in closed:
            if facility_cost[index] == 0:
                chromosome[index] = 1 #open the facility
                open = True
                break

        if not open:
            chromosome[random.randint(0, len(closed))] = 1 #pick random to open 

    return chromosome


#ASSIGNING AFTER REPAIR 
def decode(chromosome, capacity, customers, demand): #assign customer to facility
    #dicitonary: customer nr points to the facility number 
    violation = 0
    assingment = {}
    open = [index for index in range(len(chromosome)) if chromosome[index] == 1 ]

    #track the demand of each open facility:
    load_facility = {index: 0 for index in open}

    #sort customers 





    







        
            
    





    









    
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


paths = [#fixed order: 16, 25, 50
    "sofia/data/cap61.txt","sofia/data/cap62.txt",
    "sofia/data/cap101.txt", "sofia/data/cap122.txt" ]


PARAMETER_SETS = {
    "P1": { 
        "pop_size": 50,
        "generations":200,
        "crossover_prob": 0.8,
        "mutation_prob":  1, #1/mto keep the distrubtion the same on 16,25,50 facitlites 
        #prob of flipping a bit with 1/nr of facilities x 100%
    },

    "P2":{ 
        "pop_size": 100,
        "generations": 300,
        "crossover_prob": 0.9,
        "mutation_prob": 1, # 1/m

    },
    "P3":{ 
        "pop_size": 200,
        "generation":500,
        "crossover_prob": 0.95,
        "mutation_prob":2,
    },
}

SEEDS = range(10) 


def read_instance(path):
    
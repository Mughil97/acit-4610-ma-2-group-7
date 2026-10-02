"""Crossover and mutation for both representations, shared by both MOEAs."""


def uniform_crossover(parent1, parent2, crossover_prob, rng):
    """With probability crossover_prob, uniform crossover (a coin flip per gene); else the children are copies."""
    if rng.random() < crossover_prob:
        child1, child2 = [], []
        for gene1, gene2 in zip(parent1, parent2):
            if rng.random() < 0.5:
                child1.append(gene1)
                child2.append(gene2)
            else:
                child1.append(gene2)
                child2.append(gene1)
        return child1, child2
    return parent1.copy(), parent2.copy()


def bit_flip(individual, mutation_prob, rng):
    """Binary: each facility opens or closes with probability mutation_prob."""
    return [1 - gene if rng.random() < mutation_prob else gene for gene in individual]


def one_point_crossover(parent1, parent2, crossover_prob, rng):
    """With probability crossover_prob, cut both parents at one random place and swap the tails; else copies."""
    if rng.random() < crossover_prob:
        point = rng.randint(1, len(parent1) - 1)
        return parent1[:point] + parent2[point:], parent2[:point] + parent1[point:]
    return parent1.copy(), parent2.copy()


def move_to_open(individual, mutation_prob, rng):
    """Integer: each customer may move to another open facility; moving its last customer closes a facility."""
    mutated = individual.copy()
    for customer in range(len(mutated)):
        if rng.random() < mutation_prob:
            other_open = [f for f in sorted(set(mutated)) if f != mutated[customer]]
            if other_open:
                mutated[customer] = rng.choice(other_open)
    return mutated

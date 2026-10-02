"""Crossover and mutation, shared by both MOEAs."""


def crossover(parent1, parent2, crossover_prob, rng):
    """With probability crossover_prob, uniform crossover (a coin flip per facility); else the children are copies."""
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


def mutate(individual, mutation_prob, rng):
    """Bit flip: each facility opens or closes with probability mutation_prob."""
    return [1 - gene if rng.random() < mutation_prob else gene for gene in individual]

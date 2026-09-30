"""Crossover and mutation, shared by both MOEAs."""


def crossover(parent1, parent2, crossover_prob, rng):
    """One-point crossover; otherwise the children are copies of the parents."""
    if rng.random() < crossover_prob:
        point = rng.randint(1, len(parent1) - 1)
        return parent1[:point] + parent2[point:], parent2[:point] + parent1[point:]
    return parent1.copy(), parent2.copy()


def mutate(individual, mutation_prob, rng):
    """Each customer may move to another open facility; moving its last customer closes a facility."""
    mutated = individual.copy()
    for customer in range(len(mutated)):
        if rng.random() < mutation_prob:
            other_open = [f for f in sorted(set(mutated)) if f != mutated[customer]]
            if other_open:
                mutated[customer] = rng.choice(other_open)
    return mutated

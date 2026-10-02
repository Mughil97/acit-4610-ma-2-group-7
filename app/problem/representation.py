"""A solution is a list of 0/1, one per facility: individual[i] = 1 means facility i is open."""


def random_individual(instance, rng):
    return [rng.randrange(2) for _ in range(instance.m)]  # every facility open with probability 0.5

"""A solution is a list: individual[j] is the facility that serves customer j."""


def random_individual(instance, rng):
    return [rng.randrange(instance.m) for _ in range(instance.n)]

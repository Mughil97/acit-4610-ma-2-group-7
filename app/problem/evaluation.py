"""The two objectives, both minimised; only called on repaired individuals."""

from app.problem.repair import decode


def evaluate(individual, instance):
    f1 = 0.0
    for facility in decode(individual):  # fixed cost of every open facility
        f1 += instance.fixed_cost[facility]

    f2 = 0.0
    for customer, facility in enumerate(individual):  # not multiplied by demand
        f2 += instance.alloc_cost[facility][customer]

    return f1, f2

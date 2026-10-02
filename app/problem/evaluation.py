"""The two objectives, both minimised; only called on repaired individuals."""

from app.problem.repair import decode


def evaluate(individual, instance):
    f1 = sum(instance.fixed_cost[i] for i in range(instance.m) if individual[i])  # every open facility
    f2 = sum(instance.alloc_cost[facility][customer]  # each customer's cost, not multiplied by demand
             for customer, facility in enumerate(decode(individual, instance)))
    return f1, f2

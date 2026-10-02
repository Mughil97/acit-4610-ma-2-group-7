"""The two objectives, both minimised; only called on repaired individuals."""

from app.problem.repair import decode


def evaluate_binary(individual, instance):
    f1 = sum(instance.fixed_cost[i] for i in range(instance.m) if individual[i])  # every open facility
    f2 = sum(instance.alloc_cost[facility][customer]  # each customer's cost, not multiplied by demand
             for customer, facility in enumerate(decode(individual, instance)))
    return f1, f2


def evaluate_integer(individual, instance):
    f1 = sum(instance.fixed_cost[i] for i in set(individual))  # a facility is open when it serves a customer
    f2 = sum(instance.alloc_cost[facility][customer] for customer, facility in enumerate(individual))
    return f1, f2

"""Feasibility: the greedy decoder gives every customer a facility, and repair opens facilities until it can."""


def decode(individual, instance):
    """Greedy rule: biggest customer first, to its cheapest open facility with room (None if none has room)."""
    loads = [0.0] * instance.m
    assignment = [None] * instance.n  # assignment[j]: the facility that serves customer j
    for customer in instance.customers_by_demand:
        for facility in instance.facilities_by_cost[customer]:
            if individual[facility] and loads[facility] + instance.demand[customer] <= instance.capacity[facility]:
                assignment[customer] = facility
                loads[facility] += instance.demand[customer]
                break
    return assignment


def open_one(individual, instance, rng):
    """Open a closed facility: a free one (fixed cost 0) if there is one, otherwise a random one."""
    closed = [i for i in range(instance.m) if not individual[i]]
    if not closed:
        raise ValueError(f"{instance.name}: every facility is open and some customers still do not fit")
    free = [i for i in closed if instance.fixed_cost[i] == 0]
    facility = rng.choice(free or closed)
    individual[facility] = 1
    return facility


def repair(individual, instance, rng):
    """Open facilities until there is enough capacity and the greedy rule can place every customer."""
    biggest = max(instance.capacity)
    for customer in range(instance.n):  # e.g. cap41/cap42: this customer fits nowhere
        if instance.demand[customer] > biggest:
            raise ValueError(
                f"{instance.name}: customer {customer} needs {instance.demand[customer]:,.0f}, but no facility holds "
                f"more than {biggest:,.0f}, so no assignment with one facility per customer exists"
            )

    repaired = individual.copy()
    total_demand = sum(instance.demand)
    open_capacity = sum(instance.capacity[i] for i in range(instance.m) if repaired[i])
    while open_capacity < total_demand:
        open_capacity += instance.capacity[open_one(repaired, instance, rng)]
    while None in decode(repaired, instance):  # enough capacity in total, but a customer fits nowhere
        open_one(repaired, instance, rng)
    return repaired

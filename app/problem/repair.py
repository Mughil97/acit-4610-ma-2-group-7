"""Capacity repair and decoding."""


def facility_loads(individual, instance):
    loads = [0.0] * instance.m
    for customer, facility in enumerate(individual):
        loads[facility] += instance.demand[customer]
    return loads


def decode(individual):
    return set(individual)  # the open facilities


def is_feasible(individual, instance):
    loads = facility_loads(individual, instance)
    return len(individual) == instance.n and all(loads[i] <= instance.capacity[i] for i in range(instance.m))


def repair(individual, instance, rng):
    """Move customers off overloaded facilities, in random order, to random facilities with room."""
    capacity, demand = instance.capacity, instance.demand

    for customer in range(instance.n):  # e.g. cap41/cap42: this customer fits nowhere
        if demand[customer] > max(capacity):
            raise ValueError(
                f"{instance.name}: customer {customer} needs {demand[customer]:,.0f}, but no facility holds more "
                f"than {max(capacity):,.0f}, so no assignment with one facility per customer exists"
            )

    repaired = individual.copy()
    loads = facility_loads(repaired, instance)

    while True:
        overloaded = [i for i in range(instance.m) if loads[i] > capacity[i]]
        if not overloaded:
            return repaired

        facility = overloaded[0]
        customers = [j for j in range(instance.n) if repaired[j] == facility]
        rng.shuffle(customers)

        for customer in customers:
            if loads[facility] <= capacity[facility]:
                break
            loads[facility] -= demand[customer]
            with_room = [i for i in range(instance.m) if loads[i] + demand[customer] <= capacity[i]]
            if with_room:
                new_facility = rng.choice(with_room)
            else:  # nobody has room: take the facility with the most free space
                new_facility = max(range(instance.m), key=lambda i: capacity[i] - loads[i])
            repaired[customer] = new_facility
            loads[new_facility] += demand[customer]

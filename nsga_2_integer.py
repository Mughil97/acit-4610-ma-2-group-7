import random

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import FuncFormatter

from read_data import read_file

random.seed(1)

(
    no_facilities,
    no_customers,
    facility_capacity,
    facility_costs,
    customer_demands,
    allocation_costs,
) = read_file("61")


def initialise_chromosome():
    return [random.randint(0, (no_facilities - 1)) for _ in range(no_customers)]


def repair(chromosome):
    """
    Repairs the chromosome if its infeasible else leave it as is. The method is idempotent.
    """
    # Create a copy to avoid mutating the original chromosome unexpectedly
    repaired_chromosome = chromosome.copy()

    # Step 1: Calculate current load for each facility
    facility_load = np.zeros(no_facilities, dtype=int)
    for i in range(no_customers):
        j = repaired_chromosome[i]
        # Ignore any customers that might already be marked unassigned (e.g., -1)
        if 0 <= j < no_facilities:
            facility_load[j] += customer_demands[i]

    unassigned_customers = []

    # Step 2: Evict customers from over-capacitated facilities
    for j in range(no_facilities):
        if facility_load[j] > facility_capacity[j]:
            # Get all customers currently assigned to facility j
            assigned = [i for i in range(no_customers) if repaired_chromosome[i] == j]

            # Sort by inefficiency: allocation_costs / demand (descending)
            assigned.sort(
                key=lambda i: allocation_costs[i][j] / customer_demands[i],
                reverse=True,
            )

            # Evict customers until the facility is within capacity limits
            for i in assigned:
                if facility_load[j] <= facility_capacity[j]:
                    break

                repaired_chromosome[i] = -1  # Mark temporarily as unassigned
                facility_load[j] -= customer_demands[i]
                unassigned_customers.append(i)

    # Step 3: Identify active facilities
    open_facilities = set(j for j in repaired_chromosome if j != -1)

    # Sort unassigned customers by demand descending (hardest to fit first)
    unassigned_customers.sort(key=lambda i: customer_demands[i], reverse=True)

    # Step 4: Greedily reassign unassigned customers
    for i in unassigned_customers:
        best_facility = -1
        min_cost = float("inf")

        # Attempt A: Try to place customer in an OPEN facility with available capacity
        for j in open_facilities:
            spare_capacity = facility_capacity[j] - facility_load[j]
            if customer_demands[i] <= spare_capacity:
                if allocation_costs[i][j] < min_cost:
                    min_cost = allocation_costs[i][j]
                    best_facility = j

        # Successfully found an open facility
        if best_facility != -1:
            repaired_chromosome[i] = best_facility
            facility_load[best_facility] += customer_demands[i]
        else:
            # Attempt B (Fallback): Open a CLOSED facility
            closed_facilities = set(range(no_facilities)) - open_facilities
            best_closed = -1
            min_closed_cost = float("inf")

            for j in closed_facilities:
                if customer_demands[i] <= facility_capacity[j]:
                    # For closed facilities, factor in the facility_costs
                    total_cost = allocation_costs[i][j] + facility_costs[j]
                    if total_cost < min_closed_cost:
                        min_closed_cost = total_cost
                        best_closed = j

            if best_closed != -1:
                repaired_chromosome[i] = best_closed
                facility_load[best_closed] += customer_demands[i]
                open_facilities.add(best_closed)
            else:
                # Attempt C (Severe Fallback): Total system capacity limit reached.
                # Assign to the facility that results in the smallest capacity violation.
                best_overflow_fac = -1
                min_overflow = float("inf")

                for j in range(no_facilities):
                    overflow = (
                        facility_load[j] + customer_demands[i]
                    ) - facility_capacity[j]
                    if overflow < min_overflow:
                        min_overflow = overflow
                        best_overflow_fac = j

                repaired_chromosome[i] = best_overflow_fac
                facility_load[best_overflow_fac] += customer_demands[i]
                open_facilities.add(best_overflow_fac)

    return repaired_chromosome


def evaluate(chromosome):
    return (evaluate_opening_cost(chromosome), evaluate_allocation_cost(chromosome))


def evaluate_opening_cost(chromosome):
    opening_cost = 0
    opened_facilities = set(chromosome)
    for i in opened_facilities:
        opening_cost += facility_costs[i]
    return opening_cost  # minimisation so 1/value to get lower number


def evaluate_allocation_cost(chromosome):
    total_cost = 0
    for customer, facility in enumerate(chromosome):
        total_cost += allocation_costs[customer][int(facility)]
    return total_cost


def dominates(a, b):
    """No worse in every objective and strictly better in at least one."""
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def nondominated_sort(objectives):
    """Starting at rank 1."""
    size = len(objectives)
    dominated = [[] for _ in range(size)]
    domination_count = [0] * size
    ranks = [0] * size

    for i in range(size):
        for j in range(i + 1, size):
            if dominates(objectives[i], objectives[j]):
                dominated[i].append(j)
                domination_count[j] += 1
            elif dominates(objectives[j], objectives[i]):
                dominated[j].append(i)
                domination_count[i] += 1

    front = [i for i in range(size) if domination_count[i] == 0]
    fronts = []
    rank = 1
    while front:
        fronts.append(front)
        next_front = []
        for i in front:
            ranks[i] = rank
            for j in dominated[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        front = next_front
        rank += 1
    return fronts, ranks


def crowding_distances(objectives, fronts):
    distances = [0.0] * len(objectives)
    for front in fronts:
        if len(front) <= 2:
            for i in front:
                distances[i] = float("inf")
            continue

        for k in range(2):
            ordered = sorted(front, key=lambda i: objectives[i][k])
            span = objectives[ordered[-1]][k] - objectives[ordered[0]][k]
            if span == 0:
                continue
            distances[ordered[0]] = float("inf")
            distances[ordered[-1]] = float("inf")
            for position in range(1, len(ordered) - 1):
                previous_value = objectives[ordered[position - 1]][k]
                next_value = objectives[ordered[position + 1]][k]
                distances[ordered[position]] += (next_value - previous_value) / span
    return distances


def nsga2_selection(population, ranks, distances):
    """Binary tournaments: lower rank wins, then larger crowding distance."""
    mating_pool = []
    for _ in range(len(population)):
        i = random.randrange(len(population))
        j = random.randrange(len(population))
        key_i = (ranks[i], -distances[i])
        key_j = (ranks[j], -distances[j])
        if key_i < key_j:
            winner = i
        elif key_j < key_i:
            winner = j
        else:
            winner = random.choice([i, j])
        mating_pool.append(population[winner].copy())
    random.shuffle(mating_pool)
    return mating_pool


def uniform_crossover(parent1, parent2):
    child1 = []
    child2 = []

    for gene1, gene2 in zip(parent1, parent2):
        if random.random() < 0.5:
            # Swap or keep from respective parents
            child1.append(gene1)
            child2.append(gene2)
        else:
            child1.append(gene2)
            child2.append(gene1)

    return repair(child1), repair(child2)


def random_resetting_mutation(chromosome):
    mutated_chromosome = chromosome.copy()

    for i in range(len(mutated_chromosome)):
        if random.random() < 0.2:
            mutated_chromosome[i] = random.randint(0, (no_facilities - 1))

    return repair(mutated_chromosome)


def reproduce(mating_pool):
    offspring = []
    for i in range(0, len(mating_pool), 2):
        parent1, parent2 = mating_pool[i], mating_pool[i + 1]
        if random.random() < 0.8:
            children = uniform_crossover(parent1, parent2)
        else:
            children = parent1.copy(), parent2.copy()

        for child in children:
            if random.random() < 0.05:
                child = random_resetting_mutation(child)
            offspring.append(child)
    return offspring


def environmental_selection(population, objectives, size):
    """Keep whole fronts; split the last front by decreasing crowding distance."""
    fronts, ranks = nondominated_sort(objectives)
    distances = crowding_distances(objectives, fronts)
    selected = []
    for front in fronts:
        remaining = size - len(selected)
        if remaining == 0:
            break
        if len(front) <= remaining:
            selected.extend(front)
        else:
            ordered = sorted(front, key=lambda i: distances[i], reverse=True)
            selected.extend(ordered[:remaining])
            break

    # Retain combined-front ranks/distances for the next mating tournaments.
    return (
        [population[i].copy() for i in selected],
        [objectives[i] for i in selected],
        [ranks[i] for i in selected],
        [distances[i] for i in selected],
    )


def deduplicate(population, objectives):
    seen, pop, obj = set(), [], []
    for chrom, o in zip(population, objectives):
        key = tuple(chrom)
        if key not in seen:
            seen.add(key)
            pop.append(chrom)
            obj.append(o)
    return pop, obj


def plot_results(results):
    fig, axes = plt.subplots(
        1, len(results), figsize=(6 * len(results), 4), squeeze=False
    )

    for ax, (name, population) in zip(axes[0], results.items()):
        # Evaluate the actual integer chromosomes from our population
        objectives = [evaluate(individual) for individual in population]
        print(objectives)

        ax.scatter(
            [f[0] for f in objectives],
            [f[1] for f in objectives],
            alpha=0.7,
            label="Final population",
        )
        ax.set(title=name, xlabel="f1 (minimize)", ylabel="f2 (minimize)")
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.grid(alpha=0.25)
        ax.legend()

    fig.tight_layout()
    plt.show()


def run():
    population = [repair(initialise_chromosome()) for _ in range(10)]
    objectives = [evaluate(i) for i in population]
    fronts, ranks = nondominated_sort(objectives)
    distances = crowding_distances(objectives, fronts)
    for _ in range(99):
        print(_, len(fronts[0]), len(set(map(tuple, population))))
        mating_pool = nsga2_selection(population, ranks, distances)
        offspring = reproduce(mating_pool)
        offspring_objectives = [evaluate(i) for i in offspring]
        # combined_pop, combined_obj = deduplicate(
        #     population + offspring, objectives + offspring_objectives
        # )
        population, objectives, ranks, distances = environmental_selection(
            population + offspring, objectives + offspring_objectives, 10
        )

    results = {"NSGA-II": population}
    plot_results(results)


if __name__ == "__main__":
    run()

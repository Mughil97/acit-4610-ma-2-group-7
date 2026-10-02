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
    return opening_cost 


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


def plot_results(objectives, nd_front_indices, hv_history):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Panel 1: Objective Space ---
    ax1 = axes[0]
    
    # Plot all dominated solutions in gray
    dominated_f1 = [objectives[i][0] for i in range(len(objectives)) if i not in nd_front_indices]
    dominated_f2 = [objectives[i][1] for i in range(len(objectives)) if i not in nd_front_indices]
    if dominated_f1:
        ax1.scatter(dominated_f1, dominated_f2, alpha=0.4, color='gray', label="Dominated")

    # Plot Non-dominated (Rank 1) solutions in red with a connecting line
    nd_objectives = sorted([objectives[i] for i in nd_front_indices], key=lambda x: x[0])
    nd_f1 = [obj[0] for obj in nd_objectives]
    nd_f2 = [obj[1] for obj in nd_objectives]
    
    ax1.plot(nd_f1, nd_f2, color='red', marker='o', linestyle='-', linewidth=2, label="Pareto Front (Rank 1)")

    ax1.set(title="Final Population Objective Space", xlabel="Opening Cost (Minimize)", ylabel="Allocation Cost (Minimize)")
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax1.grid(alpha=0.25)
    ax1.legend()

    # --- Panel 2: Hypervolume Evolution ---
    ax2 = axes[1]
    ax2.plot(range(len(hv_history)), hv_history, color='blue', linewidth=2)
    ax2.set(title="Hypervolume Over Generations", xlabel="Generation", ylabel="Hypervolume")
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax2.grid(alpha=0.25)

    fig.tight_layout()
    plt.show()


def calculate_hypervolume_2d(front_objectives, ref_point):
    """
    Calculates the 2D hypervolume of a Pareto front.
    Assumes minimization for both objectives.
    """
    # Filter out any points that are strictly worse than the reference point
    valid_points = [
        obj for obj in front_objectives 
        if obj[0] <= ref_point[0] and obj[1] <= ref_point[1]
    ]
    
    if not valid_points:
        return 0.0

    # Sort the front by the first objective ascending
    sorted_front = sorted(valid_points, key=lambda x: x[0])
    
    hv = 0.0
    prev_f1 = ref_point[0]

    # Calculate area by sweeping rectangles backwards from the largest f1
    for f1, f2 in reversed(sorted_front):
        width = prev_f1 - f1
        height = ref_point[1] - f2
        hv += width * height
        prev_f1 = f1

    return hv


def run():
    pop_size = 100
    generations = 300
    
    population = [repair(initialise_chromosome()) for _ in range(pop_size)]
    objectives = [evaluate(i) for i in population]
    fronts, ranks = nondominated_sort(objectives)
    distances = crowding_distances(objectives, fronts)
    
    # Establish a reference point for hypervolume based on the worst initial solutions
    max_f1 = max(obj[0] for obj in objectives)
    max_f2 = max(obj[1] for obj in objectives)
    ref_point = (max_f1 * 1.1, max_f2 * 1.1)  # Offset by 10% to capture boundary points
    
    hv_history = []

    for gen in range(generations):
        # 1. Track Hypervolume for the current Rank 1 front
        nd_objectives = [objectives[i] for i in fronts[0]]
        current_hv = calculate_hypervolume_2d(nd_objectives, ref_point)
        hv_history.append(current_hv)
        
        print(f"Gen {gen:03d} | Front Size: {len(fronts[0]):03d} | Unique Solutions: {len(set(map(tuple, population))):03d} | HV: {current_hv:,.0f}")

        # 2. Evolve
        mating_pool = nsga2_selection(population, ranks, distances)
        offspring = reproduce(mating_pool)
        offspring_objectives = [evaluate(i) for i in offspring]
        
        # 3. Select (Fixed from size 10 to pop_size)
        population, objectives, ranks, distances = environmental_selection(
            population + offspring, objectives + offspring_objectives, pop_size
        )
        
        # Re-calculate fronts so we have the accurate Rank 1 indices for the next iteration/plotting
        fronts, ranks = nondominated_sort(objectives)

    # Plot the final results
    plot_results(objectives, fronts[0], hv_history)


if __name__ == "__main__":
    run()

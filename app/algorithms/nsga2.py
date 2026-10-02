"""NSGA-II (Deb et al. 2002): selection ported from Mughil's nsga_2_integer.py, on the shared loop used by VEGA."""

from app.algorithms.base import MOEA


def non_dominated_sort(objectives):
    """Split the points into fronts 1, 2, ...; return (fronts as lists of indices, the rank of every point)."""
    # With two objectives: go through the points by f1 and put each one in the first front that does not
    # dominate it. Within a front f2 only falls, so only the front's last point can dominate the next one.
    fronts, ranks = [], [0] * len(objectives)
    for i in sorted(range(len(objectives)), key=lambda i: objectives[i]):
        for rank, front in enumerate(fronts, start=1):
            last = objectives[front[-1]]
            if objectives[i][1] < last[1] or objectives[i] == last:  # not dominated by this front
                front.append(i)
                ranks[i] = rank
                break
        else:
            fronts.append([i])
            ranks[i] = len(fronts)
    return fronts, ranks


def crowding_distances(objectives, fronts):
    """How much room each point has in its front (bigger = more isolated); the ends of a front get infinity."""
    distances = [0.0] * len(objectives)
    for front in fronts:
        if len(front) <= 2:
            for i in front:
                distances[i] = float("inf")
            continue
        for k in range(2):
            ordered = sorted(front, key=lambda i, k=k: objectives[i][k])
            span = objectives[ordered[-1]][k] - objectives[ordered[0]][k]
            if span == 0:
                continue
            distances[ordered[0]] = distances[ordered[-1]] = float("inf")
            for position in range(1, len(ordered) - 1):
                gap = objectives[ordered[position + 1]][k] - objectives[ordered[position - 1]][k]
                distances[ordered[position]] += gap / span
    return distances


class NSGA2(MOEA):
    name = "NSGA-II"

    def select_parents(self, population, objectives):
        """Tournaments of tournament_size: the lower rank wins, a tie goes to the larger crowding distance."""
        fronts, ranks = non_dominated_sort(objectives)
        distances = crowding_distances(objectives, fronts)
        mating_pool = []
        for _ in range(len(population)):
            candidates = [self.rng.randrange(len(population)) for _ in range(self.config.tournament_size)]
            winner = min(candidates, key=lambda i: (ranks[i], -distances[i]))
            mating_pool.append(population[winner].copy())
        return mating_pool

    def environmental_selection(self, population, objectives, offspring, offspring_objectives):
        """Keep the best pop_size of parents + children: whole fronts first, the last front by crowding distance."""
        combined = population + offspring
        combined_objectives = objectives + offspring_objectives
        size = self.config.pop_size

        # leave out exact copies while there are enough different solutions, so copies can not take over
        unique, copies, seen = [], [], set()
        for i, individual in enumerate(combined):
            if tuple(individual) in seen:
                copies.append(i)
            else:
                seen.add(tuple(individual))
                unique.append(i)
        if len(unique) <= size:
            chosen = unique + copies[:size - len(unique)]
        else:
            candidate_objectives = [combined_objectives[i] for i in unique]
            fronts, _ = non_dominated_sort(candidate_objectives)
            distances = crowding_distances(candidate_objectives, fronts)
            chosen = []
            for front in fronts:
                room = size - len(chosen)
                if len(front) > room:
                    front = sorted(front, key=lambda i: distances[i], reverse=True)[:room]
                chosen.extend(unique[i] for i in front)
                if len(chosen) == size:
                    break

        return [combined[i] for i in chosen], [combined_objectives[i] for i in chosen]

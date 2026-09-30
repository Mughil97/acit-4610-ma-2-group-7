"""VEGA: Vector Evaluated Genetic Algorithm (Schaffer 1984, Lecture 3 slides 33-35)."""

from app.algorithms.base import MOEA

NUMBER_OF_OBJECTIVES = 2  # f1 and f2


def roulette_wheel_selection(costs, how_many, rng):
    """Pick how_many positions; a lower cost gets a bigger slice of the wheel."""
    worst = max(costs)
    slices = [worst - cost for cost in costs]  # best = biggest slice, worst = no slice
    total = sum(slices)

    if total == 0:  # all costs equal: pick at random
        return [rng.randrange(len(costs)) for _ in range(how_many)]

    chosen = []
    for _ in range(how_many):
        spin = rng.random() * total
        running_total = 0.0
        for position in range(len(slices)):
            running_total += slices[position]
            if spin < running_total:
                chosen.append(position)
                break
        else:  # rounding: the spin landed exactly on the end of the wheel
            chosen.append(max(p for p in range(len(slices)) if slices[p] > 0))
    return chosen


class VEGA(MOEA):
    name = "VEGA"

    def select_parents(self, population, objectives):
        """Shuffle, split into one part per objective, roulette each part on its own objective, shuffle."""
        indices = list(range(len(population)))
        self.rng.shuffle(indices)
        part_size = len(population) // NUMBER_OF_OBJECTIVES

        mating_pool = []
        for objective in range(NUMBER_OF_OBJECTIVES):
            part = indices[objective * part_size:(objective + 1) * part_size]
            costs = [objectives[i][objective] for i in part]
            for position in roulette_wheel_selection(costs, part_size, self.rng):
                mating_pool.append(population[part[position]].copy())

        self.rng.shuffle(mating_pool)
        return mating_pool

    def environmental_selection(self, population, objectives, offspring, offspring_objectives):
        return offspring, offspring_objectives  # generational replacement

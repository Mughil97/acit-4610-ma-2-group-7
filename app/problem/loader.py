"""Read an OR-Library capacitated warehouse file (cap41, cap101, cap121, ...), values unchanged.

File layout: "m n", then m lines "capacity fixed_cost", then per customer its demand and m allocation costs.
"""

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from app.config import DATA_DIR


@dataclass(frozen=True)
class CFLPInstance:
    name: str
    capacity: tuple    # capacity[i], S_i
    fixed_cost: tuple  # fixed_cost[i], F_i
    demand: tuple      # demand[j], d_j
    alloc_cost: tuple  # alloc_cost[i][j], C_ij: serving all of customer j from facility i

    @property
    def m(self):
        return len(self.capacity)

    @property
    def n(self):
        return len(self.demand)

    @cached_property  # worked out once per instance, for the greedy decoder
    def customers_by_demand(self):
        """Customers from the biggest demand to the smallest (a tie: the lower number first)."""
        return tuple(sorted(range(self.n), key=lambda j: -self.demand[j]))

    @cached_property
    def facilities_by_cost(self):
        """facilities_by_cost[j]: the facilities from the cheapest to the dearest for customer j."""
        return tuple(tuple(sorted(range(self.m), key=lambda i, j=j: self.alloc_cost[i][j])) for j in range(self.n))


def load_instance(path):
    numbers = Path(path).read_text().split()
    m, n = int(numbers[0]), int(numbers[1])

    expected = 2 + 2 * m + n * (1 + m)
    if len(numbers) != expected:
        raise ValueError(f"{Path(path).name}: expected {expected} numbers for m={m}, n={n}, found {len(numbers)}")

    position = 2
    capacity, fixed_cost = [], []
    for _ in range(m):
        capacity.append(float(numbers[position]))
        fixed_cost.append(float(numbers[position + 1]))
        position += 2

    demand = []
    alloc_cost = [[0.0] * n for _ in range(m)]  # the file is per customer, we store per facility
    for j in range(n):
        demand.append(float(numbers[position]))
        position += 1
        for i in range(m):
            alloc_cost[i][j] = float(numbers[position])
            position += 1

    return CFLPInstance(  # tuples, so the data can not be changed by accident
        name=Path(path).stem,
        capacity=tuple(capacity),
        fixed_cost=tuple(fixed_cost),
        demand=tuple(demand),
        alloc_cost=tuple(tuple(row) for row in alloc_cost),
    )


def load_by_name(name, data_dir=DATA_DIR):
    return load_instance(Path(data_dir) / f"{name}.txt")

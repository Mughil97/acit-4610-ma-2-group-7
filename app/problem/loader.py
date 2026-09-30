"""Parse OR-Library capacitated warehouse location files (cap61, cap101, ...).

File layout:
    m n
    for each facility i:  capacity S_i   fixed_cost F_i
    for each customer j:  demand d_j
                          m allocation costs C_ij (cost of serving ALL of j's demand from i)
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class CFLPInstance:
    name: str
    capacity: np.ndarray    # S_i, shape (m,)
    fixed_cost: np.ndarray  # F_i, shape (m,)
    demand: np.ndarray      # d_j, shape (n,)
    alloc_cost: np.ndarray  # C_ij, shape (m, n)

    @property
    def m(self) -> int:
        return len(self.capacity)

    @property
    def n(self) -> int:
        return len(self.demand)


def load_instance(path: Path) -> CFLPInstance:
    """
    Read one OR-Library CFLP file into a CFLPInstance.

    OR-Library format:

    m n

    For each facility i:
        capacity_i fixed_cost_i

    For each customer j:
        demand_j
        m allocation costs
    """

    values = path.read_text().split()
    values = [float(v) for v in values]

    idx = 0

    # number of facilities and customers
    m = int(values[idx])
    n = int(values[idx + 1])
    idx += 2

    # Facility information
    capacity = np.zeros(m)
    fixed_cost = np.zeros(m)

    for i in range(m):
        capacity[i] = values[idx]
        fixed_cost[i] = values[idx + 1]
        idx += 2

    # Customer information
    demand = np.zeros(n)

    # allocation cost matrix
    # shape: (customers, facilities)
    alloc_cost = np.zeros((n, m))

    for j in range(n):
        demand[j] = values[idx]
        idx += 1

        for i in range(m):
            alloc_cost[j, i] = values[idx]
            idx += 1

    return CFLPInstance(
        name=path.stem,
        capacity=capacity,
        fixed_cost=fixed_cost,
        demand=demand,
        alloc_cost=alloc_cost,
    )

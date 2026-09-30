"""Parse OR-Library capacitated warehouse location files (cap41, cap101, ...).

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
    """Read one OR-Library file into a CFLPInstance, using its values unchanged."""
    raise NotImplementedError

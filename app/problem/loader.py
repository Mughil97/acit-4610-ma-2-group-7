"""Parse OR-Library capacitated warehouse location files (cap41, cap101, ...).

Source: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/capinfo.html

File layout (whitespace separated; a customer's cost list wraps over several lines):
    m n
    for each facility i:  capacity S_i   fixed_cost F_i
    for each customer j:  demand d_j
                          m allocation costs C_ij (cost of serving ALL of j's demand from i)
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.config import DATA_DIR


@dataclass(frozen=True)
class CFLPInstance:
    name: str
    capacity: np.ndarray    # S_i, shape (m,)
    fixed_cost: np.ndarray  # F_i, shape (m,)
    demand: np.ndarray      # d_j, shape (n,)
    alloc_cost: np.ndarray  # C_ij, shape (m, n)

    def __post_init__(self):
        # OR-Library values must be used unchanged, so accidental writes should fail loudly.
        for arr in (self.capacity, self.fixed_cost, self.demand, self.alloc_cost):
            arr.setflags(write=False)

    @property
    def m(self) -> int:
        return len(self.capacity)

    @property
    def n(self) -> int:
        return len(self.demand)


def load_instance(path: Path) -> CFLPInstance:
    """Read one OR-Library file into a CFLPInstance, using its values unchanged."""
    path = Path(path)
    tokens = path.read_text().split()
    m, n = int(tokens[0]), int(tokens[1])

    expected = 2 + 2 * m + n * (1 + m)
    if len(tokens) != expected:
        raise ValueError(f"{path.name}: expected {expected} values for m={m}, n={n}, found {len(tokens)}")

    values = np.array(tokens[2:], dtype=float)
    facilities = values[: 2 * m].reshape(m, 2)
    customers = values[2 * m :].reshape(n, 1 + m)

    return CFLPInstance(
        name=path.stem,
        capacity=facilities[:, 0].copy(),
        fixed_cost=facilities[:, 1].copy(),
        demand=customers[:, 0].copy(),
        alloc_cost=customers[:, 1:].T.copy(),  # file is per customer; store per facility
    )


def load_by_name(name: str, data_dir: Path = DATA_DIR) -> CFLPInstance:
    """Load e.g. "cap41" from data/cap41.txt."""
    return load_instance(data_dir / f"{name}.txt")

"""Feasibility repair and decoding.

Turns any chromosome into a feasible solution: enough capacity is open, every
customer is assigned to exactly one open facility, and no capacity is exceeded.
"""

import numpy as np

from app.problem.loader import CFLPInstance


def repair(chromosome: np.ndarray, instance: CFLPInstance, rng: np.random.Generator) -> np.ndarray:
    """Return a chromosome whose decoded solution is feasible."""
    raise NotImplementedError


def decode(chromosome: np.ndarray, instance: CFLPInstance) -> tuple[np.ndarray, np.ndarray]:
    """Return (open_mask y of shape (m,), assignment of shape (n,) giving the facility per customer)."""
    raise NotImplementedError


def is_feasible(open_mask: np.ndarray, assignment: np.ndarray, instance: CFLPInstance) -> bool:
    """Check all three mandatory CFLP constraints."""
    raise NotImplementedError

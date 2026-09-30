"""Chromosome encoding and population initialisation.

Shared by both MOEAs so the comparison is fair.
"""

import numpy as np

from app.problem.loader import CFLPInstance


def random_individual(instance: CFLPInstance, rng: np.random.Generator) -> np.ndarray:
    """Create one random chromosome."""
    raise NotImplementedError


def init_population(instance: CFLPInstance, pop_size: int, rng: np.random.Generator) -> list[np.ndarray]:
    """Create the initial population."""
    raise NotImplementedError

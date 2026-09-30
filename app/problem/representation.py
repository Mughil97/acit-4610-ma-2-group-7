"""Binary chromosome encoding and population initialization.

Each gene represents one candidate facility:
    1 = facility is open
    0 = facility is closed

Shared by VEGA and NSGA-II so the comparison is fair.
"""

import numpy as np

from app.problem.loader import CFLPInstance


def random_individual(
    instance: CFLPInstance,
    rng: np.random.Generator
) -> np.ndarray:
    """Create one random binary chromosome."""

    return rng.integers(
        0,
        2,
        size=instance.m,
        dtype=np.int8,
    )


def init_population(
    instance: CFLPInstance,
    pop_size: int,
    rng: np.random.Generator,
) -> list[np.ndarray]:
    """Create the initial binary population."""

    return [
        random_individual(instance, rng)
        for _ in range(pop_size)
    ]

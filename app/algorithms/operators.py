"""Variation operators shared by both MOEAs."""

import numpy as np


def crossover(p1: np.ndarray, p2: np.ndarray, prob: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Recombine two parents into two children."""
    raise NotImplementedError


def mutate(chromosome: np.ndarray, prob: float, rng: np.random.Generator) -> np.ndarray:
    """Mutate a chromosome."""
    raise NotImplementedError

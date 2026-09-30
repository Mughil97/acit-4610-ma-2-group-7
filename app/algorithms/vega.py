"""VEGA (Vector Evaluated GA): the mating pool is filled in equal shares by
selecting on one objective at a time, then shuffled before variation."""

import numpy as np

from app.algorithms.base import MOEA, Population


def select_by_objective(objectives: np.ndarray, obj_index: int, n_select: int, rng: np.random.Generator) -> np.ndarray:
    """Pick n_select parent indices using only objective obj_index (minimisation)."""
    raise NotImplementedError


class VEGA(MOEA):
    name = "VEGA"

    def select_parents(self, population: Population, objectives: np.ndarray) -> np.ndarray:
        """Fill pop_size/k slots per objective, then shuffle the combined pool."""
        raise NotImplementedError

    def environmental_selection(
        self,
        population: Population,
        objectives: np.ndarray,
        offspring: Population,
        offspring_objectives: np.ndarray,
    ) -> tuple[Population, np.ndarray]:
        """Decide which individuals form the next generation."""
        raise NotImplementedError

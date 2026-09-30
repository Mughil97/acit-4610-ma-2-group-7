"""NSGA-II: fast non-dominated sorting, crowding distance, binary tournament
selection, and elitist (mu + lambda) environmental selection."""

import numpy as np

from app.algorithms.base import MOEA, Population


def non_dominated_sort(objectives: np.ndarray) -> list[list[int]]:
    """Split indices into Pareto fronts F1, F2, ..."""
    raise NotImplementedError


def crowding_distance(objectives: np.ndarray, front: list[int]) -> np.ndarray:
    """Crowding distance of each member of one front."""
    raise NotImplementedError


class NSGA2(MOEA):
    name = "NSGA-II"

    def select_parents(self, population: Population, objectives: np.ndarray) -> np.ndarray:
        """Binary tournament: lower rank wins, ties broken by larger crowding distance."""
        raise NotImplementedError

    def environmental_selection(
        self,
        population: Population,
        objectives: np.ndarray,
        offspring: Population,
        offspring_objectives: np.ndarray,
    ) -> tuple[Population, np.ndarray]:
        """Merge parents and offspring, fill by front, truncate the last front by crowding."""
        raise NotImplementedError

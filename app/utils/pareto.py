"""Pareto dominance helpers (minimisation), shared by the MOEAs and the metrics."""

import numpy as np


def dominates(a: np.ndarray, b: np.ndarray) -> bool:
    """True if objective vector a Pareto-dominates b."""
    raise NotImplementedError


def non_dominated(objectives: np.ndarray) -> np.ndarray:
    """Filter to the non-dominated objective vectors."""
    raise NotImplementedError

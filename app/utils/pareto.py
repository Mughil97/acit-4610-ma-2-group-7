"""Pareto dominance helpers (minimisation), shared by the MOEAs and metrics."""

import numpy as np


def dominates(a: np.ndarray, b: np.ndarray) -> bool:
    """True iff a is no worse than b in all objectives and better in >=1."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return bool(np.all(a <= b) and np.any(a < b))


def non_dominated(objectives: np.ndarray) -> np.ndarray:
    """Return unique non-dominated objective vectors for minimisation."""
    objectives = np.asarray(objectives, dtype=float)
    if objectives.size == 0:
        return objectives.reshape(0, objectives.shape[-1] if objectives.ndim == 2 else 0)

    keep = np.ones(len(objectives), dtype=bool)
    for i in range(len(objectives)):
        if not keep[i]:
            continue
        for j in range(len(objectives)):
            if i != j and dominates(objectives[j], objectives[i]):
                keep[i] = False
                break

    nd = objectives[keep]
    # Remove exact duplicate objective vectors without reordering the first copy.
    _, first = np.unique(nd, axis=0, return_index=True)
    return nd[np.sort(first)]

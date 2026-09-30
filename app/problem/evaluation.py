"""Objective evaluation (both minimised), computed only on feasible solutions.

f1 = sum_i F_i * y_i          facility-opening cost
f2 = sum_i sum_j C_ij * x_ij  customer-allocation cost (C_ij already includes demand)
"""

import numpy as np

from app.problem.loader import CFLPInstance


def evaluate(open_mask: np.ndarray, assignment: np.ndarray, instance: CFLPInstance) -> tuple[float, float]:
    """Return (f1, f2) for a feasible solution."""
    raise NotImplementedError

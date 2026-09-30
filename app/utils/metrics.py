"""Multi-objective performance metrics.

Both MOEAs use the same normalisation bounds and HV reference point per instance.
"""

import numpy as np


def normalise(objectives: np.ndarray, ideal: np.ndarray, nadir: np.ndarray) -> np.ndarray:
    """Min-max scale objectives using bounds shared across all compared runs."""
    raise NotImplementedError


def hypervolume_2d(objectives: np.ndarray, ref_point: np.ndarray) -> float:
    """Exact 2-D hypervolume for minimisation."""
    raise NotImplementedError

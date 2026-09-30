"""Statistical comparison of the two MOEAs over independent runs."""

import numpy as np
import pandas as pd


def summarise(values: np.ndarray) -> dict[str, float]:
    """Mean, std, best and worst of a metric over runs."""
    raise NotImplementedError


def mann_whitney_u(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Two-sided Mann-Whitney U test; returns (U, p-value)."""
    raise NotImplementedError


def results_table(df: pd.DataFrame) -> pd.DataFrame:
    """Per instance/config/algorithm table: HV mean/std/best/worst, #ND, mean time."""
    raise NotImplementedError

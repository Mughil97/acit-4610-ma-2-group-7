"""Pareto-front plots (f1 vs f2) with both MOEAs on the same axes."""

from pathlib import Path

import numpy as np


def plot_pareto_fronts(fronts: dict[str, np.ndarray], title: str, out_path: Path) -> None:
    """Scatter the final front of each algorithm on shared axes and save to out_path."""
    raise NotImplementedError

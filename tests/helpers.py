"""Shared test fixtures."""

import numpy as np

from app.config import ExperimentConfig
from app.problem.loader import CFLPInstance


def tiny_instance() -> CFLPInstance:
    """2 facilities, 3 customers."""
    return CFLPInstance(
        name="tiny",
        capacity=np.array([10.0, 10.0]),
        fixed_cost=np.array([5.0, 7.0]),
        demand=np.array([2.0, 3.0, 4.0]),
        alloc_cost=np.arange(6, dtype=float).reshape(2, 3),
    )


def tiny_config(pop_size: int = 4, max_evaluations: int = 10) -> ExperimentConfig:
    return ExperimentConfig("T", pop_size=pop_size, max_evaluations=max_evaluations, crossover_prob=0.9, mutation_prob=0.1)

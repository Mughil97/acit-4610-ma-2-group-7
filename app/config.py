"""Experiment settings shared by both MOEAs.

Within one configuration NSGA-II and VEGA must use identical values so the
comparison is fair. Values below are provisional and will be tuned.
"""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

# OR-Library instances required by the assignment, grouped by size.
INSTANCES = {
    "small": ["cap61", "cap62"],
    "medium": ["cap101", "cap102"],
    "large": ["cap121", "cap122"],
}

N_RUNS = 10
BASE_SEED = 42


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    pop_size: int
    max_evaluations: int
    crossover_prob: float
    mutation_prob: float
    tournament_size: int = 2


CONFIGS = [
    ExperimentConfig("C1", pop_size=50, max_evaluations=10_000, crossover_prob=0.9, mutation_prob=0.05),
    ExperimentConfig("C2", pop_size=100, max_evaluations=20_000, crossover_prob=0.9, mutation_prob=0.02),
    ExperimentConfig("C3", pop_size=200, max_evaluations=40_000, crossover_prob=0.8, mutation_prob=0.01),
]

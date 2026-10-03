"""Factory for building MOEAs by name, so experiment code never imports a concrete class."""

from app.algorithms.base import MOEA
from app.algorithms.nsga2 import NSGA2
from app.algorithms.vega import VEGA
from app.config import ExperimentConfig
from app.problem.loader import CFLPInstance

_REGISTRY: dict[str, type[MOEA]] = {
    "nsga2": NSGA2,
    "vega": VEGA,
}


def available_algorithms() -> list[str]:
    return list(_REGISTRY)


def create_algorithm(name: str, instance: CFLPInstance, config: ExperimentConfig, seed: int,
                     representation: str = "binary") -> MOEA:
    try:
        cls = _REGISTRY[name.lower()]
    except KeyError:
        raise ValueError(f"Unknown algorithm {name!r}; choose from {available_algorithms()}") from None
    return cls(instance, config, seed, representation)

"""Common MOEA skeleton (template method).

The generational loop, evaluation budget, variation and repair live here so
every algorithm runs under identical conditions. Subclasses only decide how
parents are chosen and how the next population is formed.
"""

from abc import ABC, abstractmethod

import numpy as np

from app.algorithms.operators import crossover, mutate
from app.config import ExperimentConfig
from app.problem.evaluation import evaluate
from app.problem.loader import CFLPInstance
from app.problem.repair import decode, repair
from app.problem.representation import init_population
from app.utils.pareto import non_dominated

Population = list[np.ndarray]


class MOEA(ABC):
    name: str

    def __init__(self, instance: CFLPInstance, config: ExperimentConfig, seed: int):
        self.instance = instance
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.evaluations = 0

    def run(self) -> np.ndarray:
        """Evolve until the evaluation budget is spent; return the final
        non-dominated objective vectors, shape (k, 2)."""
        population = [self._repair(c) for c in init_population(self.instance, self.config.pop_size, self.rng)]
        objectives = self._evaluate(population)

        while self.evaluations < self.config.max_evaluations:
            parents = self.select_parents(population, objectives)
            offspring = self._vary(population, parents)
            offspring_objectives = self._evaluate(offspring)
            population, objectives = self.environmental_selection(
                population, objectives, offspring, offspring_objectives
            )

        return non_dominated(objectives)

    @abstractmethod
    def select_parents(self, population: Population, objectives: np.ndarray) -> np.ndarray:
        """Return pop_size indices into population forming the mating pool."""

    @abstractmethod
    def environmental_selection(
        self,
        population: Population,
        objectives: np.ndarray,
        offspring: Population,
        offspring_objectives: np.ndarray,
    ) -> tuple[Population, np.ndarray]:
        """Return the next population and its objectives."""

    def _vary(self, population: Population, parents: np.ndarray) -> Population:
        """Pair consecutive parents, apply crossover and mutation, then repair."""
        offspring = []
        for a, b in zip(parents[::2], parents[1::2]):
            c1, c2 = crossover(population[a], population[b], self.config.crossover_prob, self.rng)
            offspring += [self._repair(mutate(c, self.config.mutation_prob, self.rng)) for c in (c1, c2)]
        return offspring

    def _repair(self, chromosome: np.ndarray) -> np.ndarray:
        return repair(chromosome, self.instance, self.rng)

    def _evaluate(self, population: Population) -> np.ndarray:
        """Objective matrix of shape (len(population), 2); counts toward the budget."""
        self.evaluations += len(population)
        return np.array([evaluate(*decode(c, self.instance), self.instance) for c in population])
